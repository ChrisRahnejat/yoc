import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yoc.settings")

from yoccore import models

from django.contrib.auth.models import User
from django.db.models import Q

import csv
from datetime import date

class Load():

    def __init__(self):
        self.session_ids_parsed = []

    def create_users(self):

        users_to_create = (
            ('ap', 'adam'),
            ('crw', 'charlie'),
            ('kcr', 'chris'),
            ('sc', 'sarah c'),
            ('sm', 'sarah m'),
            ('mw', 'mark w'),
            ('at', 'tarver'),
            ('aa', 'ammar'),
            ('cr', '?'),
            ('ec', 'lizzie'),
            ('es', 'eleanor'),
            ('ghg', '?'),
            ('gsm', 'grace'),
            ('hg', 'haley g'),
            ('rg', 'rob geboy'),
            ('wt', 'travis'),
            ('wj', 'will j'),
            ('dj', 'darragh j'),
            ('dr', 'dazzle r'),
        )

        for u in zip(*users_to_create)[0]:
            User.objects.create_user(username=u, password='%s_yoc' % u)

        return True

    def questions(self):

        models.Question.create('What do you think about what you can see?', 'TX', 1, 1)

        models.Question.create('On a scale of 1-5 (1 being not useful at all, 5 being very useful) how useful do you think it (Manage Money) would be?', 'NM', 2, 1)
        models.Question.create('What in particular makes you think that (Manage Money comments)?', 'TX', 2, 2)
        models.Question.create('Which option (name for Manage Money) do you prefer?', 'EN', 2, 3)
        models.Question.create('Suggestion for another (Manage Money) name', 'SG', 2, 4)

        models.Question.create('On a scale of 1-5 (1 being not useful at all, 5 being very useful) how useful do you think it (House Move) would be?', 'NM', 3, 1)
        models.Question.create('What in particular makes you think that (House Move comments)?', 'TX', 3, 2)
        models.Question.create('Which option (name for House Move) do you prefer?', 'EN', 3, 3)
        models.Question.create('Suggestion for another (House Move) name', 'SG', 3, 4)

        models.Question.create('On a scale of 1-5 (1 being not useful at all, 5 being very useful) how useful do you think it (Spendorama) would be?', 'NM', 4, 1)
        models.Question.create('What in particular makes you think that (Spendorama comments)?', 'TX', 4, 2)
        models.Question.create('Which option (name for Spendorama) do you prefer?', 'EN', 4, 3)
        models.Question.create('Suggestion for another (Spendorama) name', 'SG', 4, 4)

        models.Question.create('Which life events could we help with?', 'EN', 5, 1)
        models.Question.create('What other life events (not already listed) can we help with?', 'SG', 5, 2)
        models.Question.create('On a scale of 1-5 (1 being strongly dislike and 5 being strongly like) what do you think of "Smart Life" as a name?', 'NM', 5, 3)

        models.Question.create('What would you like to sign up for?', 'EN', 6, 1)
        models.Question.create('e-mail address', 'PD', 6, 2)
        models.Question.create('Name', 'PD', 6, 3)
        models.Question.create('Gender', 'PD', 6, 4)
        models.Question.create('Age', 'PD', 6, 5)

        models.Question.create('General comments', 'TX', 7, 1)

        return True

    def load_answers_csv(self):

        with open('answers-export.csv', 'rb') as comments_file:

            comments_reader = csv.reader(comments_file)

            for row in comments_reader:

                username = row[8].strip()
                if 'test' in username.lower():
                    continue

                if 'user name' in username.lower():
                    continue

                session_id = row[-1].strip()

                if session_id not in self.session_ids_parsed:
                    timestamp = row[6].strip()

                    models.Session.create(username, timestamp, session_id)

                question_page = int(row[2])

                # backwards compatibility with old 7 page version of YOC
                if question_page == 7:
                    question_page = 6

                question_number = int(row[3])
                answer_text = row[4]

                if not answer_text:
                    continue

                # print session_id, self.session_ids_parsed[-1] if len(self.session_ids_parsed) > 0 else None

                models.Answer.create(question_page, question_number, answer_text, session_id)

        return True

    def load_comments_csv(self):

        with open('comments-export.csv', 'rb') as comments_file:

            comments_reader = csv.reader(comments_file)

            for row in comments_reader:

                session_id = row[-1].strip()

                if session_id not in self.session_ids_parsed:
                    timestamp = row[2].strip()
                    username = row[3].strip()

                    models.Session.create(username, timestamp, session_id)

                question_page = 7
                question_number = 1

                if row[4] not in ['', ' ', '  ', None]:
                    models.Answer.create(question_page, question_number, row[4].strip(), session_id)

                if row[5] not in ['', ' ', '  ', None]:
                    models.Answer.create(question_page, question_number, row[5].strip(), session_id)

                if row[6] not in ['', ' ', '  ', None]:
                    models.Answer.create(question_page, question_number, row[6].strip(), session_id)

        return True

    def clean_up_duff_ratings(self):
        feb24 = date(2015, 02, 24)
        sessions_from_before_24feb = models.Session.objects.filter(
            submit_date__lt=feb24)

        this_filter = Q()
        this_filter.add(Q(session__in=sessions_from_before_24feb), Q.AND)
        this_filter.add(Q(question__question_type='NM'), Q.AND)

        ratings_to_kill = models.Answer.objects.filter(this_filter)

        print "ratings objects to kill: %s" % ratings_to_kill.count()

        ratings_to_kill.delete()

        print "rating objects killed"

        return True


    def all(self):

        self.questions()
        self.load_answers_csv()
        self.load_comments_csv()
        # self.create_users()
        self.clean_up_duff_ratings()

        return True
