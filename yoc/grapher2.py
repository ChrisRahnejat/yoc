__author__ = 'Chris Rahnejat'

import logging

from django.db import connection


logger = logging.getLogger(__name__)


class Grapher(object):

    _ratings_query = """
      SELECT fbdate, fbrating, _location as branch, gender, _age, topic, CASE WHEN question_page=2 THEN 'MM' WHEN question_page=3 THEN 'HM' WHEN question_page=4 THEN 'SP' ELSE 'Any' END AS app
        FROM
          (SELECT COALESCE(sess.session_id, demographics.session_id) as session_id, sess.submit_date as submit_date, sess.location as _location, demographics.gender, demographics._age
          FROM (
            SELECT COALESCE(genders.session_id, ages.session_id) as session_id, genders.gender, ages._age
            FROM
              (SELECT answer_text as gender, session_id
                FROM yoccore_answer
                INNER JOIN (
                  SELECT *
                  FROM yoccore_question
                  WHERE question_page = 6
                  AND question_number = 4
                  ) as qn
                ON qn.id = yoccore_answer.question_id) as genders
            FULL JOIN
              (SELECT answer_text as _age, session_id
                FROM yoccore_answer
                INNER JOIN (
                  SELECT *
                  FROM yoccore_question
                  WHERE question_page = 6
                  AND question_number = 5
                  ) as qn
                ON qn.id = yoccore_answer.question_id) AS ages
            ON ages.session_id = genders.session_id) AS demographics
          FULL JOIN (
            SELECT id as session_id, location, submit_date
            FROM yoccore_session ) as sess
          ON sess.session_id = demographics.session_id) as demosess
        INNER JOIN
          (SELECT x.fbdate, x.fbrating, x.session_id, x.topic, x.question_page FROM
            (SELECT ses.submit_date::timestamp::date as fbdate, cast(ans.answer_text AS INT) as fbrating, ses.id as session_id, NULL as topic, que.question_page
            FROM (SELECT * FROM yoccore_answer WHERE answer_text in ('1','2','3','4','5') ) as ans
            INNER JOIN yoccore_session as ses
            ON ans.session_id = ses.id
            INNER JOIN (SELECT * FROM yoccore_question WHERE question_page != 5) as que
            ON que.id = ans.question_id
            UNION
            SELECT ses.submit_date::timestamp::date as fbdate, rating as fbrating, ses.id as session_id, topic, que.question_page
            FROM (SELECT * FROM yoccore_cleanedanswer WHERE rating IS NOT NULL) as ca
            INNER JOIN yoccore_answer as ans
            ON ca.answer_id = ans.id
            INNER JOIN yoccore_session as ses
            ON ses.id = ans.session_id
            INNER JOIN yoccore_question as que
            ON que.id = ans.question_id) as x) as foo
          ON foo.session_id = demosess.session_id
          ORDER BY fbdate, app, topic, branch, gender, _age
    """

    _feedback_query = """
    SELECT question_text, answer_text, CASE WHEN question_page=2 THEN 'MM' WHEN question_page=3 THEN 'HM' WHEN question_page=4 THEN 'SP' ELSE 'Any' END AS app, CASE WHEN rating > 3 THEN 'Positive' WHEN rating < 3 THEN 'Negative' ELSE 'Neutral' END AS sentiment
    FROM yoccore_answer
    INNER JOIN yoccore_cleanedanswer
    ON yoccore_answer.id = yoccore_cleanedanswer.answer_id
    INNER JOIN yoccore_question
    ON yoccore_answer.question_id = yoccore_question.id
    WHERE question_type = 'TX' AND quotable=True
    ORDER BY app, question_text, sentiment
    """

    def __init__(self):
        """
        :return: None

        """

        super(Grapher, self).__init__()

        self.__feedback_table = []
        self.__ratings_table = []

        self.__execute_sql()

        self.__x_series = []
        self.__y_series = []

        self.__build_x_series()

        self.filter = lambda x: True
        # self.__filter = {
        #     'Total': lambda x: True,
        # }


    def __execute_sql(self):
        """
        :return: None

        """

        def _dict_fetch_all(crs):
            """
            :param crs: database cursor (executed)
            :returns: list of dictionaries

            """

            desc = crs.description
            return [
                dict(zip([col[0] for col in desc], row))
                for row in crs.fetchall()]

        cursor = connection.cursor()

        cursor.execute(self._feedback_query)
        self.__feedback_table = _dict_fetch_all(cursor)

        cursor.execute(self._ratings_query)
        self.__ratings_table = _dict_fetch_all(cursor)

    def __build_x_series(self):
        """
        :return: None

        """

        all_dates = map(lambda x: x['fbdate'], self.__ratings_table)
        all_dates = set(all_dates)
        all_dates = sorted(all_dates)

        self.__x_series = [d.isoformat() for d in all_dates]

    def get_ratings_data(self, desired_series, **desired_filters):
        """
        :param desired_series: 'age', 'topic', 'branch', 'gender', 'app',
        'rating'
        :param desired_filters: may have the following key / value pairings:
                    'age': list of age categories, subset of [''>55','46-55',
                    '26-35','<18','36-45','18-25']
                    'gender': list of genders, subset of ['Male', 'Female']
                    'branch': list of branches, subset of ['M', 'S']
                    'topic': list of topics, subset of zip(
                    *models.CleanedAnswer.topics)[0]
                    'app': ['HM', 'MM', 'SP']
        :return: NVD3 format

        """

        self.__build_filters(**desired_filters)

        filtered_table = filter(self.__filter, self.__ratings_table)

        self.__build_series_from_filtered_table(filtered_table, desired_series)

        return self.__y_series

    def __build_filters(self, **desired_filters):

        all_filters = [lambda x: True]

        if 'age' in desired_filters:
            all_filters.append(lambda x: x['_age'] in desired_filters['age'])

        if 'topic' in desired_filters:
            all_filters.append(lambda x: x['topic'] in desired_filters['topic'])

        if 'branch' in desired_filters:
            all_filters.append(lambda x: x['branch'] in desired_filters[
                'branch'])

        if 'gender' in desired_filters:
            all_filters.append(lambda x: x['gender'] in desired_filters[
                'gender'])

        if 'app' in desired_filters:
            all_filters.append(lambda x: x['app'] in desired_filters['app'])

        self.__filter = lambda x: all([f(x) for f in all_filters])

    def __build_series_from_filtered_table(self, filtered_table,
                                           desired_series):

        self.__y_series = []

        if desired_series == 'age':
            desired_series = '_age'

        if desired_series == 'rating':
            desired_series = 'fbrating'

        series_set = set([r[desired_series] for r in filtered_table])

        for serial in series_set:

            if desired_series == 'fbrating':
                points = []
                series_name = 'Rating %i' % serial

                sub_filtered_table = filter(lambda x: x['fbrating'] ==
                                                        serial, filtered_table)

                for x in self.__x_series:
                    y = len([i for i in sub_filtered_table if
                             i['fbdate'].isoformat() == x])

                    points.append({'x': x, 'y': y})

                self.__y_series.append({
                    'key': series_name,
                    'values': points
                    })

            else:
                points = []
                series_name = serial

                sub_filtered_table = filter(lambda x: x[desired_series] ==
                                                      serial, filtered_table)

                for x in self.__x_series:
                    sub_sub_filtered_table = filter(lambda n:
                                n['fbdate'].isoformat() == x, sub_filtered_table)

                    print "table", sub_sub_filtered_table
                    print "x", x

                    if len(sub_sub_filtered_table) < 1:
                        y = 0

                    else:
                        y = sum([i['fbrating'] for i in
                                 sub_sub_filtered_table]) / \
                            float(len(sub_sub_filtered_table))

                    points.append({'x': x, 'y': y})

                self.__y_series.append({
                    'key': series_name,
                    'values': points
                })


    # def __build_filters(self, **desired_filters):
    #
    #     self.__filter = {
    #         'Total': lambda x: True,
    #     }
    #
    #     print desired_filters
    #
    #     if 'age' in desired_filters:  # accepts Null
    #         for value in desired_filters['age']:
    #             if value:
    #                 self.__filter.update({
    #                     value: lambda x: x['_age'] == value
    #                 })
    #
    #             else:
    #                 self.__filter.update({
    #                     'Age not specified': lambda x: x['_age'] == None
    #                 })
    #
    #     if 'gender' in desired_filters:  # accepts Null
    #         for value in desired_filters['gender']:
    #             if value:
    #                 self.__filter.update({
    #                     value: lambda x: x['gender'] == value
    #                 })
    #             else:
    #                 self.__filter.update({
    #                     'Gender not specified': lambda x: x['gender'] == None
    #                 })
    #
    #     if 'branch' in desired_filters:  # doesn't accept Null
    #         for value in desired_filters['branch']:
    #             if value:
    #                 self.__filter.update({
    #                     value: lambda x: x['branch'] == value
    #                 })
    #
    #     if 'topic' in desired_filters:  # accepts Null
    #         topics = zip(*models.CleanedAnswer.topics)
    #         for value in desired_filters['topic']:
    #             if value:
    #                 self.__filter.update({
    #                     topics[1][topics[0].index(value)]: lambda x: x['topic']
    #                                                                == value
    #                 })
    #             else:
    #                 self.__filter.update({
    #                     'Topic unknown': lambda x: x['topic'] == None
    #                 })
    #
    #     if 'app' in desired_filters:  # doesn't accept Null
    #         appss = {
    #             'MM': 'Manage Money',
    #             'HM': 'House Move',
    #             'SP': 'Spendorama'
    #         }
    #         for value in desired_filters['app']:
    #             if value != 'Any':
    #                 self.__filter.update({
    #                     value: lambda x: x['app'] == value
    #                 })
    #             else:
    #                 self.__filter.update({
    #                     'Not app-specific': lambda x: x['app'] in [value, None]
    #                 })
