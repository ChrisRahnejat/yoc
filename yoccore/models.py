import isodate

from django.db import models
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

        logger.debug("%s created"%(self.real_type.model))

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


class Session(BaseModel):

	locations = (
		('M', 'Moorgate'),
		('S', 'Shoreditch')
	)

	session_key = models.CharField(length=50)
	user_initials = models.Charfield(length=5)
	location = models.Charfield(length=1, choices=locations)
	submit_date = models.DateTimeField()

	class Meta:
		verbose_name = 'session'
		app_label = 'yoccore'

	@classmethod
	def create(cls, username, timestamp, session_key):

		submit_date = datetime.strptime(timestamp.strip(), '%d/%m/%Y %I:%M')
		location = username[0]
		user_initials = ''.join([n for n in username if not n.isdigit()])[1:]

		return cls.objects.get_or_create(submit_date=submit_date, location=location, user_initials=user_initials, session_key=session_key)


class Question(BaseModel):

	question_types = (
		('TX', 'text'),
		('NM', 'numerical'),
		('PD', 'personal details'),
		('EN', 'from enums'),
	)


