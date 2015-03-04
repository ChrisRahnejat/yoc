__author__ = 'aakh'

import logging, json
from datetime import datetime
logger = logging.getLogger(__name__)

from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.http import HttpResponse
from yoccore.models import *
from yoc.grapher import TimeDependentGraph
import validations
import random

def grapher_view(request):
    """
        Should handle all numerical graph types, see do_grapher for accepable POST fields (below)
        {
            desired_series:<str>
            desired_filters:<dict>
        }
    """

    def do_grapher(desired_series, **desired_filters):
        """
           //DEPRECATED KEY: outcome: 'count' or 'average'
            desired_series: 'age', total', 'gender', 'topic' or 'branch'
            desired_filters may have the following key / value pairings:
                *   'age': list of age categories, subset of [''>55','46-55','26-35','<18','36-45','18-25']
                    'gender': list of genders, subset of ['Male', 'Female']
                    'branch': list of branches, subset of ['M', 'S']
                    'topic': list of topics, subset of zip(*models.CleanedAnswer.topics)[0]

        """

        # Module variables - can override and use inputs instead later if desired
        START_DATE = datetime.strptime('Feb 23 2015  00:00:00', '%b %d %Y %H:%M:%S')
        END_DATE = datetime.strptime('Mar 07 2015  00:00:00', '%b %d %Y %H:%M:%S')

        grapher = TimeDependentGraph(START_DATE, END_DATE)

        grapher.create_y_series(desired_series, **desired_filters)

        return grapher.get_data()

    def return_cleaned_grapher_inputs(cpost):
        """
            Acceptable keys for POST can be seen here
        """
        
        # try:
        #     outcome = cpost['outcome']
        # except KeyError:
        #     logger.info("No outcome provided for grapher")
        #     return False

        # if outcome not in ['count', 'average']:
        #     logger.info("outcome provided %s was not valid" % outcome)
        #     return False

        try:
            desired_series = cpost['desired_series']
        except KeyError:
            logger.info("No desired series specified for grapher")
            return False

        if desired_series not in ['age', 'total', 'gender', 'topic', 'branch']:
            logger.info("desired_series provided %s was no valid" % desired_series)
            return False

        try:
            desired_filters = cpost['desired_filters']
        except KeyError:
            logger.info("no desired filters were provided, which is fine, but FYI")
            desired_filters = {}

        keys_to_kill = []
        for k in desired_filters:
            if k not in ['age', 'gender', 'branch', 'topic']:
                logger.info("invalid filter %s was passed in" % k)
                keys_to_kill.append(k)

            elif k == 'age':
                supported_ages = ['>55','46-55','26-35','<18','36-45','18-25']
                if any([v not in supported_ages for v in desired_filters[k]]):
                    logger.info("at least one value for age filters was not supported")
                    keys_to_kill.append(k)

            elif k == 'gender':
                if any([v not in ['Male', 'Female', 'Would rather not disclose', 'Other'] for v in desired_filters[k]]):
                    logger.info("at least one value for gender filters was not supported")
                    keys_to_kill.append(k)

            elif k == 'branch':
                if any([v not in ['M', 'S'] for v in desired_filters[k]]):
                    logger.info("at least one value for branch filters was not supported")
                    keys_to_kill.append(k)

            elif k == 'topic':
                if any([v not in zip(*models.CleanedAnswer.topics)[0] for v in desired_filters[k]]):
                    logger.info("at least one value for topic filters was not supported")
                    keys_to_kill.append(k)

        if not keys_to_kill:
            logger.info("the following filters were dropped: %s" % keys_to_kill)

        for k in keys_to_kill:
            desired_filters.pop(k, None)

        return desired_series, desired_filters

    
    post = validations.clean_data(request)

    x = return_cleaned_grapher_inputs(post)

    if x is False:
        data = None
    else:
        desired_series, desired_filters = x
        data = do_grapher(desired_series, **desired_filters)

    return HttpResponse(json.dumps(data), content_type="application/json")


def get_some_quotes(request):
    """
        POST - no inputs (because age and gender are not DB fields we can do a WHERE against)

        [{'quote': 'blah', 'age': age or None, 'gender': gender or None},..]

        Returns 5 random negative and 5 random positive.

        In future (if desired) can make the number and negative/positive adjustable.

    """

    Qpositive = Q(rating__gte=4)
    Qnegative = Q(rating__lte=2)
    Qquotable = Q(quotable=True)

    # Get 5 positive quotes

    this_filter = Q()
    this_filter.add(Qpositive, Q.AND)
    this_filter.add(Qquotable, Q.AND)

    lazy_list = CleanedAnswer.objects.filter(this_filter)

    number = lazy_list.count()

    if number <1:
        positive_quotes = []
    else:
        random_number_list = random.sample(range(number), 5)
        positive_quotes = [lazy_list[i] for i in random_number_list]

    # Get 5 negative quotes

    this_filter = Q()
    this_filter.add(Qnegative, Q.AND)
    this_filter.add(Qquotable, Q.AND)

    lazy_list = CleanedAnswer.objects.filter(this_filter)

    number = lazy_list.count()

    if number <1:
        negative_quotes = []
    else:
        random_number_list = random.sample(range(number), 5)
        negative_quotes = [lazy_list[i] for i in random_number_list]

    def enhance_list(quote_list):
        output = []

        for q in quote_list:
            quote = q.answer.answer_text
            gender = q.answer.what_gender()
            age = q.answer.what_age()

            output.append({'quote': quote, 'gender': gender, 'age': age})

        return output

    data = {
        'positive_quotes': enhance_list(positive_quotes),
        'negative_quotes': enhance_list(negative_quotes)
    }

    return HttpResponse(json.dumps(data), content_type="application/json")


def get_name_rankings(request):

    def font_size_formula(ratio):
        return 0.5 + ratio * 1.75

    apps = { #page numbers
        'Manage Money': 2, 
        'House Move': 3, 
        'Spendorama': 4
    }

    # question numbers per page
    enums_q = 3 #which of the following names do you like?
    suggestion_q = 4 #do you have suggestions for other name?

    data = {
        'Manage Money': {},
        'House Move': {},
        'Spendorama': {}
    }

    for app in apps:
        enum_question = Question.objects.get(Q(question_page=apps[app]) & Q(question_number=enums_q))
        suggestion_question = Question.objects.get(Q(question_page=apps[app]) & Q(question_number=suggestion_q))

        all_names = Answer.objects.filter(Q(question=enum_question) | Q(question=suggestion_question)).values_list('answer_text', flat=True)

        different_names = list(set(all_names))
        number_of_answers = len(all_names)

        for name in different_names:
            instances = all_names.count(name)
            ratio = float(instances) / number_of_answers
            font_size = font_size_formula(ratio)

            data[app].setdefault(name, font_size)

    return HttpResponse(json.dumps(data), content_type="application/json")


def feedback_quotes_for_app(request):
    """
        POST

        Returns structure:
        {
            'Manage Money': quotes...,
            'House Move': quotes...,
            'Spendorama': quotes...,
            'Any': quotes (about multiple, any or non-app specific)...
        }

    """

    apps = {
        'Manage Money': 2, 
        'House Move': 3, 
        'Spendorama': 4,
        'Any': None
    }

    data = {}

    for app in apps:
        page_number = apps[app]

        this_filter = Q()
        this_filter.add(Q(quotable=True), Q.AND)

        if page_number != None:
            this_filter.add(Q(answer__question__question_page=page_number), Q.AND)
        else:
            this_filter.add(~Q(answer__question__question_page__in=[2,3,4]), Q.AND)

        quotes = CleanedAnswer.objects.filter(this_filter).values_list('answer__answer_text', flat=True)

        data.setdefault(app, quotes)

    return HttpResponse(json.dumps(data), content_type="application/json")

