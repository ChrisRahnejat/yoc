import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yoc.settings")

from yoccore import models

class Load():

	@staticmethod
	def questions():

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

	@classmethod
	def all(cls):
		cls.questions()

		return True
