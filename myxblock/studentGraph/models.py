# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class Problem(models.Model):
	graph = models.TextField()
	nodePosition = models.TextField()
	stateCorrectness = models.TextField()
	stepCorrectness = models.TextField()
	allStudentResolutions = models.TextField()
	allCorrectStudentResolutions = models.TextField()
	allIncorrectStudentResolutions = models.TextField()

	class Meta:
		app_label  = 'studentGraph'

#class ProblemResolutions(models.Model):
#	studentResolution = models.TextField()
#	problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
#
#
#	class Meta:
#		app_label  = 'studentGraphResolutions'