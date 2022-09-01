# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class Problem(models.Model):
	graph = models.TextField()
	isCalculatedPos = models.IntegerField(default=0) #deprecated, remover quanto antes possível
	isCalculatingPos = models.IntegerField(default=0)
	multipleChoiceProblem = models.IntegerField(default=1)

	class Meta:
		app_label  = 'studentGraph'

class Node(models.Model):
	problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
	title = models.TextField()
	nodePositionX = models.IntegerField(default=-1)
	nodePositionY = models.IntegerField(default=-1)
	correctness = models.FloatField(default=0)
	weigth = models.IntegerField(default=1)
	visible = models.IntegerField(default=1)
	alreadyCalculatedPos = models.IntegerField(default=0)
	customPos = models.IntegerField(default=0)

	class Meta:
		app_label  = 'studentGraph'

class Edge(models.Model):
	problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
	sourceNode = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='sourceNode')
	destNode = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='destNode')
	correctness = models.FloatField(default=0)
	visible = models.IntegerField(default=1)
	weigth = models.IntegerField(default=1)

	class Meta:
		app_label  = 'studentGraph'

class Resolution(models.Model):
	problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
	nodeIdList = models.TextField()
	studentId = models.TextField()
	correctness = models.FloatField(default=0)

	class Meta:
		app_label  = 'studentGraph'

class ErrorSpecificFeedback(models.Model):
	problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
	edge = models.ForeignKey(Edge, on_delete=models.CASCADE, related_name='errorSpecificFeedbackEdge')
	text = models.TextField()
	order = models.IntegerField(default=0)
	class Meta:
		app_label  = 'studentGraph'

class Hints(models.Model):
	problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
	edge = models.ForeignKey(Edge, on_delete=models.CASCADE, related_name='hintsEdge')
	text = models.TextField()
	order = models.IntegerField(default=0)
	class Meta:
		app_label  = 'studentGraph'

class Explanations(models.Model):
	problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
	edge = models.ForeignKey(Edge, on_delete=models.CASCADE, related_name='explanationsEdge')
	text = models.TextField()
	order = models.IntegerField(default=0)
	class Meta:
		app_label  = 'studentGraph'

class Doubt(models.Model):
	problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
	edgeType = models.IntegerField(default=0)
	edge = models.ForeignKey(Edge, on_delete=models.CASCADE, related_name='doubtEdge')
	node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='doubtNode')
	text = models.TextField()
	order = models.IntegerField(default=0)
	class Meta:
		app_label  = 'studentGraph'

class KnowledgeComponent(models.Model):
	problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
	edge = models.ForeignKey(Edge, on_delete=models.CASCADE, related_name='knowledgeComponentEdge')
	node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='knowledgeComponentNode')
	text = models.TextField()
	order = models.IntegerField(default=0)
	class Meta:
		app_label  = 'studentGraph'