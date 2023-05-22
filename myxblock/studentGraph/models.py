from __future__ import unicode_literals

from django.db import models

from django.db.models.signals import pre_save
from django.dispatch import receiver
from unidecode import unidecode

def transformToSimplerAnswer(answer):
    withoutSpaces = answer.replace(" ", "")
    lowerCase = withoutSpaces.lower()
    noAccent = unidecode(lowerCase)

    return noAccent

class Problem(models.Model):
	graph = models.TextField()
	isCalculatedPos = models.IntegerField(default=0) #deprecated, remover quanto antes possível
	isCalculatingPos = models.IntegerField(default=0)
	multipleChoiceProblem = models.IntegerField(default=1)
	dateAdded = models.DateTimeField()
	dateModified = models.DateTimeField(default=None, blank=True, null=True)

	class Meta:
		app_label  = 'studentGraph'

class Node(models.Model):
	problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
	title = models.TextField()
	nodePositionX = models.IntegerField(default=-1)
	nodePositionY = models.IntegerField(default=-1)
	correctness = models.FloatField(default=0)
	fixedValue = models.IntegerField(default=0)
	visible = models.IntegerField(default=1)
	alreadyCalculatedPos = models.IntegerField(default=0)
	usageCount = models.IntegerField(default=0)
	customPos = models.IntegerField(default=0)
	dateAdded = models.DateTimeField()
	linkedSolution = models.TextField(default=None, blank=True, null=True)
	dateModified = models.DateTimeField(default=None, blank=True, null=True)

	class Meta:
		app_label  = 'studentGraph'

	@staticmethod
	def pre_save(sender, instance, **kwargs):
		instance.title = transformToSimplerAnswer(instance.title)

	@property
	def normalizedTitle(self):
	    return self.title.replace(" ", "").lower() #Não se esquecer dos acentos
	

class Edge(models.Model):
	problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
	sourceNode = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='sourceNode')
	destNode = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='destNode')
	correctness = models.FloatField(default=0)
	visible = models.IntegerField(default=1)
	fixedValue = models.IntegerField(default=0)
	usageCount = models.IntegerField(default=0)
	dateAdded = models.DateTimeField()
	dateModified = models.DateTimeField(default=None, blank=True, null=True)

	class Meta:
		app_label  = 'studentGraph'

class Resolution(models.Model):
	problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
	nodeIdList = models.TextField(default="")
	edgeIdList = models.TextField(default="")
	studentId = models.TextField()
	correctness = models.FloatField(default=0)
	dateAdded = models.DateTimeField()
	dateModified = models.DateTimeField(default=None, blank=True, null=True)

	class Meta:
		app_label  = 'studentGraph'

class ErrorSpecificFeedbacks(models.Model):
	problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
	edge = models.ForeignKey(Edge, on_delete=models.CASCADE, related_name='errorSpecificFeedbackEdge', blank=True, null=True)
	text = models.TextField()
	dateAdded = models.DateTimeField()
	dateModified = models.DateTimeField(default=None, blank=True, null=True)
	priority = models.IntegerField(default=0)
	usefulness = models.IntegerField(default=0)

	class Meta:
		app_label  = 'studentGraph'

class Hint(models.Model):
	problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
	edge = models.ForeignKey(Edge, on_delete=models.CASCADE, related_name='hintsEdge', blank=True, null=True)
	text = models.TextField()
	dateAdded = models.DateTimeField()
	dateModified = models.DateTimeField(default=None, blank=True, null=True)
	priority = models.IntegerField(default=0)
	usefulness = models.IntegerField(default=0)

	class Meta:
		app_label  = 'studentGraph'

class Explanation(models.Model):
	problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
	edge = models.ForeignKey(Edge, on_delete=models.CASCADE, related_name='explanationsEdge', blank=True, null=True)
	text = models.TextField()
	dateAdded = models.DateTimeField()
	dateModified = models.DateTimeField(default=None, blank=True, null=True)
	priority = models.IntegerField(default=0)
	usefulness = models.IntegerField(default=0)

	class Meta:
		app_label  = 'studentGraph'

class Doubt(models.Model):
	problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
	type = models.IntegerField(default=0) #0 = node, 1 = edge
	edge = models.ForeignKey(Edge, on_delete=models.CASCADE, related_name='doubtEdge', blank=True, null=True)
	node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='doubtNode', blank=True, null=True)
	text = models.TextField()
	dateAdded = models.DateTimeField()
	dateModified = models.DateTimeField(default=None, blank=True, null=True)

	class Meta:
		app_label  = 'studentGraph'

class Answer(models.Model):
	problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
	doubt = models.ForeignKey(Doubt, on_delete=models.CASCADE, related_name='AnswerDoubt', blank=True, null=True)
	text = models.TextField()
	dateAdded = models.DateTimeField()
	dateModified = models.DateTimeField(default=None, blank=True, null=True)
	usefulness = models.IntegerField(default=0)

	class Meta:
		app_label  = 'studentGraph'

class KnowledgeComponent(models.Model):
	problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
	edge = models.ForeignKey(Edge, on_delete=models.CASCADE, related_name='knowledgeComponentEdge', blank=True, null=True)
	node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='knowledgeComponentNode', blank=True, null=True)
	text = models.TextField()
	dateAdded = models.DateTimeField()
	dateModified = models.DateTimeField(default=None, blank=True, null=True)

	class Meta:
		app_label  = 'studentGraph'