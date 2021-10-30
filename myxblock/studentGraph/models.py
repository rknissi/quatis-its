# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class Question(models.Model):
	question_text = models.CharField(max_length=200)
	pub_date = models.DateTimeField('date published')

	class Meta:
		app_label  = 'studentGraph'

class Problem(models.Model):
	graph = models.CharField(max_length=21843)
	nodePosition = models.CharField(max_length=21843)
	stateCorrectness = models.CharField(max_length=21843)
	stepCorrectness = models.CharField(max_length=21843)

	class Meta:
		app_label  = 'studentGraph'

class Choice(models.Model):
	choice_text = models.CharField(max_length=200)
	votes = models.IntegerField(default=0)

	class Meta:
		app_label  = 'studentGraph'