import isodate
import logging, json
logger = logging.getLogger(__name__)

from datetime import datetime
from django.db import models
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType

class BaseModel(models.Model):
    """ All models in the project should inherit from this class for data consistency and traceability """

    real_type = models.ForeignKey(ContentType, editable=False)
    created = models.DateTimeField(auto_now_add=True, null=True)
    last_updated = models.DateTimeField(auto_now=True, null=True)
    # source = models.TextField(null=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """ Save instance into the database, all non-nullable and non-blankable model fields must be satisfied """

        if not self.id:
            self.real_type = self._get_real_type()

        super(BaseModel, self).save(*args, **kwargs)

    def _get_real_type(self):
        return ContentType.objects.get_for_model(type(self))

    def get_related(self):
        return [rel.get_accessor_name() for rel in self._meta.get_all_related_objects()]

    def cast(self):
        return self.real_type.get_object_for_this_type(pk=self.pk)

    @classmethod
    def get_all(cls):
        return cls.objects.all()

    @classmethod
    def get_filtered(cls, **kwargs):
        return cls.objects.filter(**kwargs)

    @classmethod
    def clear_all(cls):
        return cls.objects.all().delete()

    @classmethod
    def clear_filtered(cls, **kwargs):
        return cls.objects.filter(**kwargs).delete()

    @classmethod
    def create(cls, **kwargs):  # overwrite as required
        return cls.objects.get_or_create(**kwargs)


class Session(BaseModel):

    locations = (
        ('M', 'Moorgate'),
        ('S', 'Shoreditch')
    )

    session_key = models.CharField(max_length=50)
    user_initials = models.CharField(max_length=5)
    location = models.CharField(max_length=1, choices=locations)
    submit_date = models.DateField()

    class Meta:
        verbose_name = 'session'
        app_label = 'yoccore'

    def __unicode__(self):
        return ' '.join([self.user_initials, self.session_key])

    @classmethod
    def create(cls, username, timestamp, session_key):

        try:
            submit_date = datetime.strptime(timestamp.strip(), '%d/%m/%Y %H:%M').date()
        except ValueError:
            print "Error: %s was not a valid time stamp, session_key was %s" % (timestamp, session_key)
            return False

        location = username[0].upper()
        user_initials = ''.join([n for n in username if not n.isdigit()])[1:].lower()

        return cls.objects.get_or_create(submit_date=submit_date,

                                         location=location,
                                         user_initials=user_initials,
                                         session_key=session_key) # tuple of object, created TRUE/FALSE


class Question(BaseModel):

    question_types = (
        ('TX', 'text'),
        ('NM', 'numerical'),
        ('PD', 'personal details'),
        ('EN', 'from enums'),
        ('SG', 'name suggestions')
    )

    question_text = models.TextField()
    question_type = models.CharField(max_length=2, choices=question_types)
    question_page = models.IntegerField()
    question_number = models.IntegerField()

    class Meta:
        verbose_name = 'question'
        app_label = 'yoccore'

    def __unicode__(self):
        return self.question_text

    @classmethod
    def create(cls, question_text, question_type, question_page, question_number):

        return cls.objects.get_or_create(question_text=question_text, question_type=question_type, question_page=question_page, question_number=question_number)

    def default_topic(self):

        topics = {
            1: ['LF'],
            2: ['FA', 'FA', 'LF', 'LF'],
            3: ['LE', 'LE', 'LF', 'LF'],
            4: ['GM', 'GM', 'LF', 'LF'],
            5: ['LE', 'LE', 'LF'],
            6: ['OT'] * 5,
            7: ['OT']
        }

        return topics[self.question_page][self.question_number - 1]

    def default_app(self):

        apps = ['Any', 'Manage Money', 'House Move', 'Spendorama', 'Any', 'Any', 'Any']

        return apps[self.question_page - 1]

class Answer(BaseModel):

    question = models.ForeignKey(Question)
    session = models.ForeignKey(Session)
    answer_text = models.TextField()
    done = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'answer'
        app_label = 'yoccore'

    def __unicode__(self):
        return ' '.join([self.session.__unicode__(), self.question.__unicode__()])


    # ANALYSIS SHORTCUTS FOR MAKING IT EASIER TO DEAL WITH DIFFERENT QUESTION TYPES
    def get_topic(self, *cleaned_answers):
        """ If Text then return CleanedAnswer topic else return Question topic """
        if cleaned_answers:
            x = filter(lambda y: y.answer_id == self.id, cleaned_answers)
        else:
            x = list(self.cleanedanswer_set.all())

        if len(x) > 0:
            return x[0].topic # todo: take topic w max count
        else:
            return self.question.default_topic()

    def get_app(self):
        """ Return the app it probably refers to (by page) or just "Any" """
        return self.question.default_app()

    def get_rating(self, *cleaned_answers):
        """ Return the 1-5 rating (either user input or from CleanedAnswer) """
        if self.question.question_type == 'NM':
            # It was a rating to begin with
            try:
                return int(self.answer_text)
            except:
                return None

        else:
            if cleaned_answers:
                x = filter(lambda y: y.answer_id == self.id, cleaned_answers)
            else:
                x = list(self.cleanedanswer_set.all())

            if len(x) > 0:
                return x[0].rating # It was text and we'll return the interpreted rating
            else:
                return None # It's not text or a rating

    def what_gender(self):
        try:
            # Find answer where question is about gender and belongs to this session
            Qfilter = Q()
            Qfilter.add(Q(session=self.session), Q.AND)
            Qfilter.add(Q(question__question_page=6), Q.AND)
            Qfilter.add(Q(question__question_page=4), Q.AND)
            
            ans = Answer.objects.get(Qfilter)
        except Answer.DoesNotExist:
            return None # Unknown!!!

        return ans.answer_text # Known - this is the answer

    def what_age(self):
        try:
            # Find answer where question is about age and belongs to this session
            Qfilter = Q()
            Qfilter.add(Q(session=self.session), Q.AND)
            Qfilter.add(Q(question__question_page=6), Q.AND)
            Qfilter.add(Q(question__question_page=5), Q.AND)
            
            ans = Answer.objects.get(Qfilter)
        except Answer.DoesNotExist:
            return None # Unknown!!!

        return ans.answer_text # Known - this is the answer

    # /END OF ANALYSIS SHORTCUTS

    @classmethod
    def create(cls, question_page, question_number, answer_text, session_key):
        session_object = Session.objects.get(session_key=session_key)

        try:
            question_object = Question.objects.get(Q(question_number=question_number) & Q(question_page=question_page))
        except Question.DoesNotExist:
            print "Error: page %s, question %s not found!" % (question_page, question_number)
            return False

        if question_object.question_type == 'TX':
            done = False
        else:
            done = True

        try:
            existing_object = cls.objects.get(Q(question=question_object) & Q(answer_text=answer_text) & Q(session=session_object))
            return (existing_object, False)
        except cls.DoesNotExist:
            return cls.objects.get_or_create(question=question_object, session=session_object, answer_text=answer_text, done=done)


class CleanedAnswer(BaseModel):

    topics = (
        ('GM', 'Gamification'),
        ('FA', 'Financial analysis'),
        ('LE', 'Life events'),
        ('LF', 'Look and feel'),
        ('BR', 'Branch setup'),
        ('OT', 'Other')
    )

    answer = models.ForeignKey(Answer)
    rating = models.IntegerField(null=True, blank=True)
    topic = models.CharField(max_length=2, choices=topics, null=True, blank=True)
    quotable = models.BooleanField(default=False)
    not_feedback = models.BooleanField(default=False)

    def __unicode__(self):
        return "CleanedAnswer-%s"%self.id

    class Meta:
        verbose_name = 'cleaned answer'
        app_label = 'yoccore'

    @classmethod
    def create(cls, answer, rating=None, topic=None, quotable=False, not_feedback=False):

        # answer = Answer.objects.get(pk=answer)
        item, success = cls.objects.get_or_create(answer=answer, rating=rating,
                                                  topic=topic, quotable=quotable,
                                                  not_feedback=not_feedback)

        answer.done = success
        answer.save()

        return item

    @classmethod
    def get_quotes(cls, specific_topic=None, specific_app=None, app_exclusive=False):
        """
            specific_topic None means don't filter for this, otherwise must be from cls.topics
            specific_app None means don't filter for this, otherwise must be from:
            ['Any', 'Manage Money', 'House Move', 'Spendorama']
            app_exclusive means "this specific answer only" if True, and "this answer plus 'Any'" if False

            Returns a list of quotes
        """

        Qfilter = Q()
        Qfilter = Q(quotable=True)

        if specific_topic:
            Qfilter.add(Q(topic=specific_topic))

        topic_filtered = cls.objects.filter(Qfilter)

        if specific_app:
            if app_exclusive:
                final_list = filter(lambda x: x.answer.get_app() == specific_app, topic_filtered)
            else:
                final_list = filter(lambda x: x.answer.get_app() in [specific_app, 'Any'], topic_filtered)
        else:
            final_list = topic_filtered

        return [f.answer.answer_text for f in final_list]

