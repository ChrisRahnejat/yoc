import isodate
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
		return self.session_key

	@classmethod
	def create(cls, username, timestamp, session_key):

		try:
			submit_date = datetime.strptime(timestamp.strip(), '%d/%m/%Y %H:%M').date()
		except ValueError:
			print "Error: %s was not a valid time stamp, session_key was %s" % (timestamp, session_key)
			return False

		location = username[0].upper()
		user_initials = ''.join([n for n in username if not n.isdigit()])[1:].lower()

		return cls.objects.get_or_create(submit_date=submit_date, location=location, user_initials=user_initials, session_key=session_key) # tuple of object, created TRUE/FALSE


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


class Answer(BaseModel):

	question = models.ForeignKey(Question)
	session = models.ForeignKey(Session)
	answer_text = models.TextField()
	done = models.BooleanField(default=False)

	class Meta:
		verbose_name = 'answer'
		app_label = 'yoccore'

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

		return cls.objects.get_or_create(question=question_object, session=session_object, answer_text=answer_text, done=done)


class CleanedAnswer(BaseModel):

	topics = (
		('GM', 'Gamification'),
		('FA', 'Financial analysis'),
		('LE', 'Life events'),
		('LF', 'Look and feel'),
		('OT', 'Other')
	)

	answer = models.ForeignKey(Answer)
	rating = models.IntegerField()
	topic = models.CharField(max_length=2, choices=topics)
	quotable = models.BooleanField()
	not_feedback = models.BooleanField(default=False)

	class Meta:
		verbose_name = 'session'
		app_label = 'yoccore'

	@classmethod
	def create(cls, answer_id, rating, topic, quotable, not_feedback=False):
		answer = Answer.objects.get(pk=answer_id)

		item, success = cls.objects.get_or_create(answer=answer, rating=rating, topic=topic, quotable=quotable, not_feedback=not_feedback)

		answer.done = success
		answer.save()

		return item