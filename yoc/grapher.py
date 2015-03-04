__author__ = 'aakh'

import logging, json
import calendar
from operator import __or__ as OR
from dateutil.relativedelta import relativedelta
from datetime import datetime
logger = logging.getLogger(__name__)

from django.db.models import Q
from yoccore import models
import validations


class TimeDependentGraph(object):
    """
        Class which holds static methods and data for generating
        NVD3-compatible data for feedback against time.

        Parameters for x axis are set at point of instantiation, you can then
        run methods to generate y series. All data is stored against the class.

    """

    __acceptable_step_sizes = ['D', 'M'] # Daily, Monthly

    def __init__(self, start_date, end_date=datetime.now(), step_size='D'):
        """
        Pick the date-times you want the x axis to start and end with and the
        size of bins desired. If you wish to redefine the x axis then
        instantiate a new object.

        Once instantiated the y series can be
        generated by running any other methods on this class. All data is
        stored against the class is self.x_series and self.y_series.

        :param start_date: a datetime object
        :param end_date: a datetime object
        :param step_size: a string, must be supported in
        self.acceptable_step_sizes
        :return:
        """

        assert(step_size in self.__acceptable_step_sizes)

        # store
        self.__start_date = start_date
        self.__end_date = end_date
        self.__step_size = step_size

        # initialise
        self.x_series = []  # just a list of datetime objects
        self.x_series_utc = []  # just a list of ints for utc timestamp in ms
        self.y_series = []
        self.y_series_c = []
        # Template for y_series:
        # [{
        #     'cumulative': bool,
        #     'data': [numbers],
        #     'name': string
        # },..]

        # build x series to output
        self.__create_x_series()

        # just pull from the DB once and then use the result for further queries
        self.answer_source = models.Answer.objects.all
        self.cleaned_source = models.CleanedAnswer.objects.all
        self.session_source = models.Session.objects.all

    def __create_x_series(self):
        """
        Generates the x axis data and writes to self.x_series, based on
        self.start_date, self.end_date and step_size.

        :return:
        """

        # initial values
        current_step = self.__start_date

        # continue up until (and including) the end_date
        while current_step.date() < self.__end_date.date():
            # date accuracy is enough
            # data points are stored as datetime, edit here if this changes
            self.x_series.append(current_step)
            self.x_series_utc.append(calendar.timegm( current_step.utctimetuple() * 1000 ))

            # if days
            if self.__step_size == 'D':
                current_step = current_step + relativedelta(days=1)

            # if months
            elif self.__step_size == 'M':
                current_step = current_step + relativedelta(months=1)

    def filtered_datum(self, desired_series, seriesQ):

        if desired_series in ['age', 'gender']:
            yoc_sessions = [a.session for a in list(models.Answer.objects.filter(reduce(OR, seriesQ['series'])))]
            answers = list(models.Answer.objects.filter(session__in=yoc_sessions)) #.exclude(question__question_type__iexact='PD'))
            cleaned_answers = models.CleanedAnswer.objects.filter(answer__in=answers, not_feedback=False)

        elif desired_series == 'topic':
            cleaned_answers = list(models.CleanedAnswer.objects.filter(not_feedback=False).filter(reduce(OR, seriesQ['series'])))

            answers1 = models.Answer.objects.filter(id__in=[cleaned_answer.answer for cleaned_answer in cleaned_answers])

            # and get Answer objects where get_topic evaluates to the desired criteria
            answers2 = filter(lambda x: x.get_topic(*cleaned_answers) in zip(*seriesQ['series'].children)[1],
                              models.Answer.objects.exclude(
                                  id__in=[cleaned_answer.answer for cleaned_answer in cleaned_answers]))

            answers = list(set(list(answers1)+list(answers2)))
            yoc_sessions = [a.session_id for a in answers]


        elif desired_series == 'branch':
            yoc_sessions = models.Session.objects.filter(reduce(OR, seriesQ['series']))
            answers = models.Answer.objects.filter(session__in=yoc_sessions)
            cleaned_answers = models.CleanedAnswer.objects.filter(answer__in=answers, not_feedback=False)

        else:
            yoc_sessions = models.Session.objects.all()
            answers = models.Answer.objects.all()
            cleaned_answers = models.CleanedAnswer.objects.all()

        return {'yoc_sessions':list(yoc_sessions), 'answers':list(answers), 'cleaned_answers':list(cleaned_answers)}

    def __create_new_y_series(self, desired_series, name, **seriesQ):
        """
        Creates two y_series (a cumulative and non_cumulative) count of
        feedback over time for the given set of filters.

        Outputs to self.y_series.

        :param name: name of the series
        :param seriesQ: args of django Q filters to apply to Feedback count
        :return:
        """

        # initialise
        # Non-cumulative
        count_series_nc = [0]
        avg_series_nc = [0]
        tot_series_nc = [0]


        # Cumulative
        count_series_c = [0]
        avg_series_c = [0]
        tot_series_c = [0]

        # get answers, cleaned_answers and session data for the desired series eg gender = Male
        datum = self.filtered_datum(desired_series, seriesQ)

        #apply series level filters
        try:
            temp = zip(*[x.children[0] for x in seriesQ['sessionQ']])[1]
            datum['yoc_sessions'] = filter(lambda x: x.location in temp, datum['yoc_sessions'])
        except:
            logger.debug("seriesQ['sessionQ'] is empty")

        try:
            temp = zip(*[x.children[0] for x in seriesQ['cleanedQ']])[1]
            datum['cleaned_answers'] = filter(lambda x: x.topic() in temp, datum['cleaned_answers'])
        except:
            logger.debug("seriesQ['cleanedQ'] is empty")

        try:
            temp = zip(*[z.children[0] for z in seriesQ['answersQ']])[1]
            temp2 = [x.session for x in datum['answers'] if x.answer_text in temp]
            datum['answers'] = [y for y in datum['answers'] if y.session in temp2]

        except:
            logger.debug("seriesQ['answersQ'] is empty")


        try:
            temp = zip(*[x.children[0] for x in seriesQ['cleanedQ']])[1]
            datum['answers'] = filter(lambda x: x.get_topic(*datum['cleaned_answers']) in temp, datum['answers'])
        except:
            logger.debug("seriesQ['cleanedQ'] is empty (topic filter)")

        # get rid of personal questions
        datum['answers'] = filter(lambda x: x.question.question_type != 'PD', datum['answers'])

        # start at 0, could start with all feedback before start but this could
        #  give very erroneous looking data if trying to crop into a data-set
        for i, upper in enumerate(self.x_series[1:]):
            # upper will be the top of the bin (exclusive)
            # lower will be the bottom of the bin (inclusive)
            lower = self.x_series[i]

            datum_bounded = filter(lambda x: upper.date() > x.session.submit_date >= lower.date(), datum['answers'])
            cleaned_datum_bounded = filter(lambda x: upper.date() > x.answer.session.submit_date >= lower.date(), datum['cleaned_answers'])

            # datum_bounded = filter(lambda x: x.session.submit_date >= lower.date(), datum_capped)
            # cleaned_datum_bounded = filter(lambda x: x.answer.session.submit_date >= lower.date(), cleaned_datum_capped)

            data_to_average = [x.get_rating(*cleaned_datum_bounded) for x in datum_bounded]

            logger.info('passing count')
            # Just count the feedback that this applies to
            count_series_nc.append(len([x for x in data_to_average if x is not None]))
            # count_series_nc.append(len(datum_bounded))


            logger.info('passing average')
            avg_series_nc.append(validations.Numbers.average_list(data_to_average))

            logger.info('passing total')
            tot_series_nc.append(validations.Numbers.sum_list(data_to_average))

            count_series_c.append(sum(count_series_nc))
            avg_series_c.append(sum(avg_series_nc))
            tot_series_c.append(sum(tot_series_nc))

        # Once we reach this point our series is complete

        y_series_c = {
            'cumulative': True,
            'count': count_series_c,
            'average': avg_series_c,
            'sum': tot_series_c,
            'name': "%s (cumulative)" % name
        }

        y_series_nc = {
            'cumulative': False,
            'count': count_series_nc,
            'average': avg_series_nc,
            'sum': tot_series_nc,
            'name': "%s (non-cumulative)" % name
        }

        # append to output
        self.y_series_c.append({y_series_c['name']:{
            'count':y_series_c['count'],
            'average':y_series_c['average'],
            'sum':y_series_c['sum']
            }
        })

        self.y_series.append({y_series_nc['name']:{
            'count':y_series_nc['count'],
            'average':y_series_nc['average'],
            'sum':y_series_nc['sum']
            }
        })
        # self.y_series.append({y_series_nc['name']:y_series_nc['data']})

    def get_series_list(self):
        return {
            'age': ('>55','46-55','26-35','<18','36-45','18-25',),
            'gender':('Male', 'Female', 'Would rather not disclose'),
            'topic':zip(*models.CleanedAnswer.topics)[0],
            'branch':zip(*models.Session.locations)[0],
            'total':('total',)
        }

    def create_y_series(self, desired_series='total', **desired_filters):
        """

        :param count, average,

        :param desired_series: age, gender, topic, branch. If missing, then ignored

        :param fixed_filters: dictionary of filters to apply to this chart If missing, take TOTAL
            KEYS: age, gender, branch, topic
        :return:
        """

        answersQ = []
        cleanedQ = []
        sessionQ = []
        self.y_series = []
        self.y_series_c = []

        valid_outcomes = ['count', 'average',]

        valid_filters = {
            'age':answersQ,
            'gender':answersQ,
            'branch':sessionQ,
            'topic':cleanedQ
        }

        series_lists = self.get_series_list()


        if desired_series not in series_lists.keys():
            desired_series = 'total'

        for f in desired_filters.keys():
            if f not in valid_filters.keys():
                desired_filters.pop(f)
                logger.info('removing filter %s'%f)

        #build filters
        for f,v in desired_filters.iteritems():

            if isinstance(v, basestring): v = v.split(',')
            elif not isinstance(v, (list,tuple)): v = list(v)
            v = list(set(v))

            if f in ['age', 'gender']:
                for vi in v: valid_filters[f].append(Q(answer_text=str(vi)))#, Q.OR)

            elif f == 'topic':
                for vi in v: valid_filters[f].append(Q(topic=str(vi)))#, Q.OR)

            elif f == 'branch':
                for vi in v: valid_filters[f].append(Q(location=str(vi)))#, Q.OR)

        filters = {'answersQ':answersQ,
                   'cleanedQ': cleanedQ,
                   'sessionQ': sessionQ}

        for ser in series_lists[desired_series]:
            if desired_series in ['age', 'gender']:
                q = Q(answer_text=str(ser))

            elif desired_series == 'topic':
                q = Q(topic=str(ser))

            elif desired_series == 'branch':
                q = Q(location=str(ser))

            else:
                q = Q()

            filters.update({'series': [q]})
            self.__create_new_y_series(desired_series=desired_series, name=ser, **filters)
            filters.pop('series')


    def get_data(self, x_utc=True, include_cumulatives=False):
        """

        :param outcome: <string> must be count, average or sum
        :param x_utc: boolean
        :param include_cumulatives: boolean
        :return:
        """

        return {
            'x': self.x_series_utc if x_utc else self.x_series,
            'y': self.y_series,
            'y_c': self.y_series_c if include_cumulatives else None
        }