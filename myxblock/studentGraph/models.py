# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class Problem(models.Model):
	graph = models.TextField()
	isCalculatedPos = models.IntegerField(default=0)
	isCalculatingPos = models.IntegerField(default=0)

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