from __future__ import unicode_literals

from django.db import models

from django.db.models.signals import pre_save
from django.dispatch import receiver
from unidecode import unidecode
from datetime import datetime  

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
	customPos = models.IntegerField(default=0)
	dateAdded = models.DateTimeField()
	linkedSolution = models.TextField(default=None, blank=True, null=True)
	dateModified = models.DateTimeField(default=None, blank=True, null=True)
	counter = models.IntegerField(default=0)

	class Meta:
		app_label  = 'studentGraph'

	@staticmethod
	def pre_save(sender, instance, **kwargs):
		instance.title = transformToSimplerAnswer(instance.title)
		if instance.id is not None:
			old = Node.objects.get(id = instance.id)
			if old.title != instance.title or old.correctness != instance.correctness or old.fixedValue != instance.fixedValue or old.visible != instance.visible or old.linkedSolution != instance.linkedSolution or old.counter != instance.counter:
				newEntry = Node_history(problem=instance.problem, title = instance.title, 
					nodePositionX = instance.nodePositionX, nodePositionY = instance.nodePositionY, 
			   		correctness = instance.correctness, fixedValue = instance.fixedValue,
			   		visible = instance.visible, alreadyCalculatedPos = instance.alreadyCalculatedPos, customPos = instance.customPos, 
			   		dateAdded = instance.dateAdded, linkedSolution = instance.linkedSolution, 
			   		dateModified = instance.dateModified, counter = instance.counter, originalId = instance.id, historyDate = datetime.now(), historyAction = "save")
				newEntry.save()

	@staticmethod
	def post_save(sender, instance, created, **kwargs):
		if created:
			newEntry = Node_history(problem=instance.problem, title = instance.title, 
			   nodePositionX = instance.nodePositionX, nodePositionY = instance.nodePositionY, 
			   correctness = instance.correctness, fixedValue = instance.fixedValue,
			   visible = instance.visible, alreadyCalculatedPos = instance.alreadyCalculatedPos, customPos = instance.customPos, 
			   dateAdded = instance.dateAdded, linkedSolution = instance.linkedSolution, 
			   dateModified = instance.dateModified, counter = instance.counter, originalId = instance.id, historyDate = datetime.now(), historyAction = "created")
			newEntry.save()

	@staticmethod
	def pre_delete(sender, instance, **kwargs):
		newEntry = Node_history(problem=instance.problem, title = instance.title, 
	       nodePositionX = instance.nodePositionX, nodePositionY = instance.nodePositionY, 
		   correctness = instance.correctness, fixedValue = instance.fixedValue,
		   visible = instance.visible, alreadyCalculatedPos = instance.alreadyCalculatedPos, customPos = instance.customPos, 
		   dateAdded = instance.dateAdded, linkedSolution = instance.linkedSolution, 
		   dateModified = instance.dateModified, counter = instance.counter, originalId = instance.id, historyDate = datetime.now(), historyAction = "delete")
		newEntry.save()

	@property
	def normalizedTitle(self):
	    return self.title.replace(" ", "").lower() #Não se esquecer dos acentos
	
class Node_history(models.Model):
	problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
	title = models.TextField()
	nodePositionX = models.IntegerField(default=-1)
	nodePositionY = models.IntegerField(default=-1)
	correctness = models.FloatField(default=0)
	fixedValue = models.IntegerField(default=0)
	visible = models.IntegerField(default=1)
	alreadyCalculatedPos = models.IntegerField(default=0)
	customPos = models.IntegerField(default=0)
	dateAdded = models.DateTimeField()
	linkedSolution = models.TextField(default=None, blank=True, null=True)
	dateModified = models.DateTimeField(default=None, blank=True, null=True)
	counter = models.IntegerField(default=0)
	originalId = models.IntegerField(default=None, blank=True, null=True)
	historyDate = models.DateTimeField(default=None, blank=True, null=True)
	historyAction = models.TextField(default=None, blank=True, null=True)

	class Meta:
		app_label  = 'studentGraph'

class Node_votes(models.Model):
	problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
	node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='nodeVote', blank=True, null=True)
	positiveCounter = models.IntegerField(default=0)
	negativeCounter = models.IntegerField(default=0)
	dateAdded = models.DateTimeField()
	dateModified = models.DateTimeField(default=None, blank=True, null=True)

	class Meta:
		app_label  = 'studentGraph'

	@staticmethod
	def pre_save(sender, instance, **kwargs):
		if instance.id is not None:
			old = Node_votes.objects.get(id = instance.id)
			if old.positiveCounter != instance.positiveCounter or old.negativeCounter != instance.negativeCounter:
				newEntry = Node_votes_history(problem = instance.problem, node = instance.node, 
	       			positiveCounter = instance.positiveCounter, negativeCounter = instance.negativeCounter, dateAdded = instance.dateAdded, dateModified = instance.dateModified,
		   			originalId = instance.id, historyDate = datetime.now(), historyAction =  "save")
				newEntry.save()

	@staticmethod
	def post_save(sender, instance, created, **kwargs):
		if created:
			newEntry = Node_votes_history(problem = instance.problem, node = instance.node, 
	       		positiveCounter = instance.positiveCounter, negativeCounter = instance.negativeCounter, dateAdded = instance.dateAdded, dateModified = instance.dateModified,
		   		originalId = instance.id, historyDate = datetime.now(), historyAction =  "created")
			newEntry.save()

class Node_votes_history(models.Model):
	problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
	node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='nodeVoteHistory', blank=True, null=True)
	positiveCounter = models.IntegerField(default=0)
	negativeCounter = models.IntegerField(default=0)
	dateAdded = models.DateTimeField()
	dateModified = models.DateTimeField(default=None, blank=True, null=True)
	historyDate = models.DateTimeField(default=None, blank=True, null=True)
	historyAction = models.TextField(default=None, blank=True, null=True)

	class Meta:
		app_label  = 'studentGraph'


class Edge(models.Model):
	problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
	sourceNode = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='sourceNode')
	destNode = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='destNode')
	correctness = models.FloatField(default=0)
	visible = models.IntegerField(default=1)
	fixedValue = models.IntegerField(default=0)
	dateAdded = models.DateTimeField()
	dateModified = models.DateTimeField(default=None, blank=True, null=True)
	counter = models.IntegerField(default=0)

	class Meta:
		app_label  = 'studentGraph'

	@staticmethod
	def pre_save(sender, instance, **kwargs):
		if instance.id is not None:
			newEntry = Edge_history(problem = instance.problem, sourceNode = instance.sourceNode, 
	       		destNode = instance.destNode, correctness = instance.correctness, 
		   		visible = instance.visible, fixedValue = instance.fixedValue, 
		   		dateAdded = instance.dateAdded, dateModified = instance.dateModified, 
		   		counter = instance.counter, originalId = instance.id, historyDate = datetime.now(), historyAction = "save")
			newEntry.save()

	@staticmethod
	def post_save(sender, instance, created, **kwargs):
		if created:
			newEntry = Edge_history(problem = instance.problem, sourceNode = instance.sourceNode, 
	       		destNode = instance.destNode, correctness = instance.correctness, 
		   		visible = instance.visible, fixedValue = instance.fixedValue, 
		   		dateAdded = instance.dateAdded, dateModified = instance.dateModified, 
		   		counter = instance.counter, originalId = instance.id, historyDate = datetime.now(), historyAction = "created")
			newEntry.save()

	@staticmethod
	def pre_delete(sender, instance, **kwargs):
		newEntry = Edge_history(problem = instance.problem, sourceNode = instance.sourceNode, 
	       destNode = instance.destNode, correctness = instance.correctness, 
		   visible = instance.visible, fixedValue = instance.fixedValue, 
		   dateAdded = instance.dateAdded, dateModified = instance.dateModified, 
		   counter = instance.counter, originalId = instance.id, historyDate = datetime.now(), historyAction = "delete")
		newEntry.save()


class Edge_history(models.Model):
	problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
	sourceNode = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='historySourceNode')
	destNode = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='historyDestNode')
	correctness = models.FloatField(default=0)
	visible = models.IntegerField(default=1)
	fixedValue = models.IntegerField(default=0)
	dateAdded = models.DateTimeField()
	dateModified = models.DateTimeField(default=None, blank=True, null=True)
	counter = models.IntegerField(default=0)
	originalId = models.IntegerField(default=None, blank=True, null=True)
	historyDate = models.DateTimeField(default=None, blank=True, null=True)
	historyAction = models.TextField(default=None, blank=True, null=True)

	class Meta:
		app_label  = 'studentGraph'

class Edge_votes(models.Model):
	problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
	edge = models.ForeignKey(Edge, on_delete=models.CASCADE, related_name='edgeVote', blank=True, null=True)
	positiveCounter = models.IntegerField(default=0)
	negativeCounter = models.IntegerField(default=0)
	dateAdded = models.DateTimeField()
	dateModified = models.DateTimeField(default=None, blank=True, null=True)

	class Meta:
		app_label  = 'studentGraph'

	@staticmethod
	def pre_save(sender, instance, **kwargs):
		if instance.id is not None:
			old = Edge_votes.objects.get(id = instance.id)
			if old.positiveCounter != instance.positiveCounter or old.negativeCounter != instance.negativeCounter:
				newEntry = Edge_votes_history(problem = instance.problem, edge = instance.edge, 
	       			positiveCounter = instance.positiveCounter, negativeCounter = instance.negativeCounter, dateAdded = instance.dateAdded, dateModified = instance.dateModified,
		   			originalId = instance.id, historyDate = datetime.now(), historyAction =  "save")
				newEntry.save()

	@staticmethod
	def post_save(sender, instance, created, **kwargs):
		if created:
			newEntry = Edge_votes_history(problem = instance.problem, edge = instance.edge, 
	       		positiveCounter = instance.positiveCounter, negativeCounter = instance.negativeCounter, dateAdded = instance.dateAdded, dateModified = instance.dateModified,
		   		originalId = instance.id, historyDate = datetime.now(), historyAction =  "created")
			newEntry.save()

class Edge_votes_history(models.Model):
	problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
	edge = models.ForeignKey(Edge, on_delete=models.CASCADE, related_name='edgeVoteHistory', blank=True, null=True)
	positiveCounter = models.IntegerField(default=0)
	negativeCounter = models.IntegerField(default=0)
	dateAdded = models.DateTimeField()
	dateModified = models.DateTimeField(default=None, blank=True, null=True)
	originalId = models.IntegerField(default=None, blank=True, null=True)
	historyDate = models.DateTimeField(default=None, blank=True, null=True)
	historyAction = models.TextField(default=None, blank=True, null=True)

	class Meta:
		app_label  = 'studentGraph'

class Resolution(models.Model):
	problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
	nodeIdList = models.TextField(default="")
	edgeIdList = models.TextField(default="")
	selectedOption = models.TextField(default=None, blank=True, null=True)
	confirmationKey = models.TextField(default="")
	studentId = models.TextField()
	attempt = models.IntegerField(default=0)
	correctness = models.FloatField(default=0)
	dateStarted = models.DateTimeField()
	dateFinished = models.DateTimeField(default=None, blank=True, null=True)
	dateModified = models.DateTimeField(default=None, blank=True, null=True)

	class Meta:
		app_label  = 'studentGraph'

	@staticmethod
	def pre_save(sender, instance, **kwargs):
		if instance.id is not None:
			newEntry = Resolution_history(problem = instance.problem, nodeIdList = instance.nodeIdList, selectedOption = instance.selectedOption, 
	       		edgeIdList = instance.edgeIdList, confirmationKey = instance.confirmationKey, studentId = instance.studentId, 
		   		correctness = instance.correctness, dateStarted = instance.dateStarted, dateFinished = instance.dateFinished, attempt = instance.attempt, dateModified = instance.dateModified, 
		   		originalId = instance.id, historyDate = datetime.now(), historyAction = "save")
			newEntry.save()

	@staticmethod
	def post_save(sender, instance, created, **kwargs):
		if created:
			newEntry = Resolution_history(problem = instance.problem, nodeIdList = instance.nodeIdList, selectedOption = instance.selectedOption, 
	       		edgeIdList = instance.edgeIdList, confirmationKey = instance.confirmationKey, studentId = instance.studentId, 
		   		correctness = instance.correctness, dateStarted = instance.dateStarted, dateFinished = instance.dateFinished, attempt = instance.attempt, dateModified = instance.dateModified, 
		   		originalId = instance.id, historyDate = datetime.now(), historyAction = "created")
			newEntry.save()

	@staticmethod
	def pre_delete(sender, instance, **kwargs):
		newEntry = Resolution_history(problem = instance.problem, nodeIdList = instance.nodeIdList, selectedOption = instance.selectedOption, 
	       edgeIdList = instance.edgeIdList, confirmationKey = instance.confirmationKey, studentId = instance.studentId, 
		   correctness = instance.correctness, dateStarted = instance.dateStarted, dateFinished = instance.dateFinished, attempt = instance.attempt, dateModified = instance.dateModified, 
		   originalId = instance.id, historyDate = datetime.now(), historyAction = "delete")
		newEntry.save()

class Resolution_history(models.Model):
	problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
	nodeIdList = models.TextField(default="")
	edgeIdList = models.TextField(default="")
	selectedOption = models.TextField(default=None, blank=True, null=True)
	confirmationKey = models.TextField(default="")
	studentId = models.TextField()
	correctness = models.FloatField(default=0)
	attempt = models.IntegerField(default=0)
	dateStarted = models.DateTimeField()
	dateFinished = models.DateTimeField(default=None, blank=True, null=True)
	dateModified = models.DateTimeField(default=None, blank=True, null=True)
	originalId = models.IntegerField(default=None, blank=True, null=True)
	historyDate = models.DateTimeField(default=None, blank=True, null=True)
	historyAction = models.TextField(default=None, blank=True, null=True)

	class Meta:
		app_label  = 'studentGraph'

class Attempt(models.Model):
	problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
	nodeIdList = models.TextField(default="")
	edgeIdList = models.TextField(default="")
	studentId = models.TextField()
	attempt = models.IntegerField(default=0)
	dateCreated = models.DateTimeField()

	class Meta:
		app_label  = 'studentGraph'


class ErrorSpecificFeedbacks(models.Model):
	problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
	edge = models.ForeignKey(Edge, on_delete=models.CASCADE, related_name='errorSpecificFeedbackEdge', blank=True, null=True)
	text = models.TextField()
	studentId = models.TextField()
	dateAdded = models.DateTimeField()
	dateModified = models.DateTimeField(default=None, blank=True, null=True)
	priority = models.IntegerField(default=0)
	usefulness = models.IntegerField(default=0)
	counter = models.IntegerField(default=0)

	class Meta:
		app_label  = 'studentGraph'

	@staticmethod
	def pre_save(sender, instance, **kwargs):
		if instance.id is not None:
			old = ErrorSpecificFeedbacks.objects.get(id = instance.id)
			if old.edge != instance.edge or old.text != instance.text or old.priority != instance.priority or old.usefulness != instance.usefulness or old.counter != instance.counter:
				newEntry = ErrorSpecificFeedbacks_history(problem = instance.problem, edge = instance.edge, 
	       			text = instance.text, dateAdded = instance.dateAdded, dateModified = instance.dateModified, studentId = instance.studentId,
	       			priority = instance.priority, usefulness = instance.usefulness, counter = instance.counter, 
		   			originalId = instance.id, historyDate = datetime.now(),historyAction =  "save")
				newEntry.save()

	@staticmethod
	def post_save(sender, instance, created, **kwargs):
		if created:
			newEntry = ErrorSpecificFeedbacks_history(problem = instance.problem, edge = instance.edge, 
	       		text = instance.text, dateAdded = instance.dateAdded, dateModified = instance.dateModified, studentId = instance.studentId, 
	       		priority = instance.priority, usefulness = instance.usefulness, counter = instance.counter, 
		   		originalId = instance.id, historyDate = datetime.now(),historyAction =  "created")
			newEntry.save()

	@staticmethod
	def pre_delete(sender, instance, **kwargs):
		newEntry = ErrorSpecificFeedbacks_history(problem = instance.problem, edge = instance.edge, 
	       text = instance.text, dateAdded = instance.dateAdded, dateModified = instance.dateModified, studentId = instance.studentId, 
	       priority = instance.priority, usefulness = instance.usefulness, counter = instance.counter, 
		   originalId = instance.id, historyDate = datetime.now(),historyAction =  "delete")
		newEntry.save()

class ErrorSpecificFeedbacks_history(models.Model):
	problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
	edge = models.ForeignKey(Edge, on_delete=models.CASCADE, related_name='historyErrorSpecificFeedbackEdge', blank=True, null=True)
	text = models.TextField()
	studentId = models.TextField()
	dateAdded = models.DateTimeField()
	dateModified = models.DateTimeField(default=None, blank=True, null=True)
	priority = models.IntegerField(default=0)
	usefulness = models.IntegerField(default=0)
	counter = models.IntegerField(default=0)
	originalId = models.IntegerField(default=None, blank=True, null=True)
	historyDate = models.DateTimeField(default=None, blank=True, null=True)
	historyAction = models.TextField(default=None, blank=True, null=True)

	class Meta:
		app_label  = 'studentGraph'

class Hint(models.Model):
	problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
	edge = models.ForeignKey(Edge, on_delete=models.CASCADE, related_name='hintsEdge', blank=True, null=True)
	text = models.TextField()
	studentId = models.TextField()
	dateAdded = models.DateTimeField()
	dateModified = models.DateTimeField(default=None, blank=True, null=True)
	priority = models.IntegerField(default=0)
	usefulness = models.IntegerField(default=0)
	counter = models.IntegerField(default=0)

	class Meta:
		app_label  = 'studentGraph'

	@staticmethod
	def pre_save(sender, instance, **kwargs):
		if instance.id is not None:
			old = Hint.objects.get(id = instance.id)
			if old.edge != instance.edge or old.text != instance.text or old.priority != instance.priority or old.usefulness != instance.usefulness or old.counter != instance.counter:
				newEntry = Hint_history(problem = instance.problem, edge = instance.edge, studentId = instance.studentId, 
	       			text = instance.text, dateAdded = instance.dateAdded, dateModified = instance.dateModified, 
	       			priority = instance.priority, usefulness = instance.usefulness, counter = instance.counter, 
		   			originalId = instance.id, historyDate = datetime.now(),historyAction =  "save")
				newEntry.save()

	@staticmethod
	def post_save(sender, instance, created, **kwargs):
		if created:
			newEntry = Hint_history(problem = instance.problem, edge = instance.edge, studentId = instance.studentId, 
	       		text = instance.text, dateAdded = instance.dateAdded, dateModified = instance.dateModified, 
	       		priority = instance.priority, usefulness = instance.usefulness, counter = instance.counter, 
		   		originalId = instance.id, historyDate = datetime.now(),historyAction =  "created")
			newEntry.save()

	@staticmethod
	def pre_delete(sender, instance, **kwargs):
		newEntry = Hint_history(problem = instance.problem, edge = instance.edge, studentId = instance.studentId, 
	       text = instance.text, dateAdded = instance.dateAdded, dateModified = instance.dateModified, 
	       priority = instance.priority, usefulness = instance.usefulness, counter = instance.counter, 
		   originalId = instance.id, historyDate = datetime.now(),historyAction =  "delete")
		newEntry.save()

class Hint_history(models.Model):
	problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
	edge = models.ForeignKey(Edge, on_delete=models.CASCADE, related_name='historyHintsEdge', blank=True, null=True)
	text = models.TextField()
	studentId = models.TextField()
	dateAdded = models.DateTimeField()
	dateModified = models.DateTimeField(default=None, blank=True, null=True)
	priority = models.IntegerField(default=0)
	usefulness = models.IntegerField(default=0)
	counter = models.IntegerField(default=0)
	originalId = models.IntegerField(default=None, blank=True, null=True)
	historyDate = models.DateTimeField(default=None, blank=True, null=True)
	historyAction = models.TextField(default=None, blank=True, null=True)

	class Meta:
		app_label  = 'studentGraph'

class Explanation(models.Model):
	problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
	edge = models.ForeignKey(Edge, on_delete=models.CASCADE, related_name='explanationsEdge', blank=True, null=True)
	text = models.TextField()
	studentId = models.TextField()
	dateAdded = models.DateTimeField()
	dateModified = models.DateTimeField(default=None, blank=True, null=True)
	priority = models.IntegerField(default=0)
	usefulness = models.IntegerField(default=0)
	counter = models.IntegerField(default=0)

	class Meta:
		app_label  = 'studentGraph'
	@staticmethod

	def pre_save(sender, instance, **kwargs):
		if instance.id is not None:
			old = Explanation.objects.get(id = instance.id)
			if old.edge != instance.edge or old.text != instance.text or old.priority != instance.priority or old.usefulness != instance.usefulness or old.counter != instance.counter:
				newEntry = Explanation_history(problem = instance.problem, edge = instance.edge, studentId = instance.studentId, 
	       				text = instance.text, dateAdded = instance.dateAdded, dateModified = instance.dateModified, 
	       				priority = instance.priority, usefulness = instance.usefulness, counter = instance.counter, 
		   				originalId = instance.id, historyDate = datetime.now(),historyAction =  "save")
				newEntry.save()

	@staticmethod
	def post_save(sender, instance, created, **kwargs):
		if created:
			newEntry = Explanation_history(problem = instance.problem, edge = instance.edge, studentId = instance.studentId, 
	       			text = instance.text, dateAdded = instance.dateAdded, dateModified = instance.dateModified, 
	       			priority = instance.priority, usefulness = instance.usefulness, counter = instance.counter, 
		   			originalId = instance.id, historyDate = datetime.now(),historyAction =  "created")
			newEntry.save()

	@staticmethod
	def pre_delete(sender, instance, **kwargs):
		newEntry = Explanation_history(problem = instance.problem, edge = instance.edge, studentId = instance.studentId, 
	       text = instance.text, dateAdded = instance.dateAdded, dateModified = instance.dateModified, 
	       priority = instance.priority, usefulness = instance.usefulness, counter = instance.counter, 
		   originalId = instance.id, historyDate = datetime.now(),historyAction =  "delete")
		newEntry.save()

class Explanation_history(models.Model):
	problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
	edge = models.ForeignKey(Edge, on_delete=models.CASCADE, related_name='historyExplanationsEdge', blank=True, null=True)
	text = models.TextField()
	studentId = models.TextField()
	dateAdded = models.DateTimeField()
	dateModified = models.DateTimeField(default=None, blank=True, null=True)
	priority = models.IntegerField(default=0)
	usefulness = models.IntegerField(default=0)
	counter = models.IntegerField(default=0)
	originalId = models.IntegerField(default=None, blank=True, null=True)
	historyDate = models.DateTimeField(default=None, blank=True, null=True)
	historyAction = models.TextField(default=None, blank=True, null=True)

	class Meta:
		app_label  = 'studentGraph'

class Doubt(models.Model):
	problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
	type = models.IntegerField(default=0) #0 = node, 1 = edge
	edge = models.ForeignKey(Edge, on_delete=models.CASCADE, related_name='doubtEdge', blank=True, null=True)
	node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='doubtNode', blank=True, null=True)
	text = models.TextField()
	studentId = models.TextField()
	dateAdded = models.DateTimeField()
	dateModified = models.DateTimeField(default=None, blank=True, null=True)
	counter = models.IntegerField(default=0)

	class Meta:
		app_label  = 'studentGraph'

	def pre_save(sender, instance, **kwargs):
		if instance.id is not None:
			old = Doubt.objects.get(id = instance.id)
			if old.edge != instance.edge or old.text != instance.text or old.node != instance.node or old.counter != instance.counter:
				newEntry = Doubt_history(problem = instance.problem, type = instance.type, 
	       			edge = instance.edge, node = instance.node, text = instance.text, studentId = instance.studentId,
		   			dateAdded = instance.dateAdded, dateModified = instance.dateModified, counter = instance.counter, 
		   			originalId = instance.id, historyDate = datetime.now(),historyAction =  "save")
				newEntry.save()

	@staticmethod
	def post_save(sender, instance, created, **kwargs):
		if created:
			newEntry = Doubt_history(problem = instance.problem, type = instance.type, 
	       		edge = instance.edge, node = instance.node, text = instance.text, studentId = instance.studentId,
		   		dateAdded = instance.dateAdded, dateModified = instance.dateModified, counter = instance.counter, 
		   		originalId = instance.id, historyDate = datetime.now(),historyAction =  "created")
			newEntry.save()

	@staticmethod
	def pre_delete(sender, instance, **kwargs):
		newEntry = Doubt_history(problem = instance.problem, type = instance.type, 
	       edge = instance.edge, node = instance.node, text = instance.text, studentId = instance.studentId,
		   dateAdded = instance.dateAdded, dateModified = instance.dateModified, counter = instance.counter, 
		   originalId = instance.id, historyDate = datetime.now(),historyAction =  "delete")
		newEntry.save()

class Doubt_history(models.Model):
	problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
	type = models.IntegerField(default=0) #0 = node, 1 = edge
	edge = models.ForeignKey(Edge, on_delete=models.CASCADE, related_name='historyDoubtEdge', blank=True, null=True)
	node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='historyDoubtNode', blank=True, null=True)
	text = models.TextField()
	studentId = models.TextField()
	dateAdded = models.DateTimeField()
	dateModified = models.DateTimeField(default=None, blank=True, null=True)
	counter = models.IntegerField(default=0)
	originalId = models.IntegerField(default=None, blank=True, null=True)
	historyDate = models.DateTimeField(default=None, blank=True, null=True)
	historyAction = models.TextField(default=None, blank=True, null=True)

	class Meta:
		app_label  = 'studentGraph'

class Answer(models.Model):
	problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
	doubt = models.ForeignKey(Doubt, on_delete=models.CASCADE, related_name='AnswerDoubt', blank=True, null=True)
	text = models.TextField()
	studentId = models.TextField()
	dateAdded = models.DateTimeField()
	dateModified = models.DateTimeField(default=None, blank=True, null=True)
	usefulness = models.IntegerField(default=0)
	counter = models.IntegerField(default=0)

	class Meta:
		app_label  = 'studentGraph'

	def pre_save(sender, instance, **kwargs):
		if instance.id is not None:
			old = Answer.objects.get(id = instance.id)
			if old.doubt != instance.doubt or old.text != instance.text or old.usefulness != instance.usefulness or old.counter != instance.counter:
				newEntry = Answer_history(problem = instance.problem, doubt = instance.doubt, studentId = instance.studentId, 
	       			text = instance.text, dateAdded = instance.dateAdded, dateModified = instance.dateModified, 
		   			usefulness = instance.usefulness, counter = instance.counter, 
		   			originalId = instance.id, historyDate = datetime.now(),historyAction =  "save")
				newEntry.save()

	@staticmethod
	def post_save(sender, instance, created, **kwargs):
		if created:
			newEntry = Answer_history(problem = instance.problem, doubt = instance.doubt, studentId = instance.studentId, 
	       		text = instance.text, dateAdded = instance.dateAdded, dateModified = instance.dateModified, 
		   		usefulness = instance.usefulness, counter = instance.counter, 
		   		originalId = instance.id, historyDate = datetime.now(),historyAction =  "created")
			newEntry.save()

	@staticmethod
	def pre_delete(sender, instance, **kwargs):
		newEntry = Answer_history(problem = instance.problem, doubt = instance.doubt, studentId = instance.studentId, 
	       text = instance.text, dateAdded = instance.dateAdded, dateModified = instance.dateModified, 
		   usefulness = instance.usefulness, counter = instance.counter, 
		   originalId = instance.id, historyDate = datetime.now(),historyAction =  "delete")
		newEntry.save()

class Answer_history(models.Model):
	problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
	doubt = models.ForeignKey(Doubt, on_delete=models.CASCADE, related_name='historyAnswerDoubt', blank=True, null=True)
	text = models.TextField()
	studentId = models.TextField()
	dateAdded = models.DateTimeField()
	dateModified = models.DateTimeField(default=None, blank=True, null=True)
	usefulness = models.IntegerField(default=0)
	counter = models.IntegerField(default=0)
	originalId = models.IntegerField(default=None, blank=True, null=True)
	historyDate = models.DateTimeField(default=None, blank=True, null=True)
	historyAction = models.TextField(default=None, blank=True, null=True)

	class Meta:
		app_label  = 'studentGraph'


class KnowledgeComponent(models.Model):
	problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
	edge = models.ForeignKey(Edge, on_delete=models.CASCADE, related_name='knowledgeComponentEdge', blank=True, null=True)
	node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='knowledgeComponentNode', blank=True, null=True)
	text = models.TextField()
	dateAdded = models.DateTimeField()
	dateModified = models.DateTimeField(default=None, blank=True, null=True)
	counter = models.IntegerField(default=0)

	class Meta:
		app_label  = 'studentGraph'

	def pre_save(sender, instance, **kwargs):
		if instance.id is not None:
			newEntry = KnowledgeComponent_history(problem = instance.problem, edge = instance.edge, 
				node = instance.node, text = instance.text, dateAdded = instance.dateAdded, dateModified = instance.dateModified, 
				counter = instance.counter, 
		   		originalId = instance.id, historyDate = datetime.now(),historyAction =  "save")
			newEntry.save()

	@staticmethod
	def post_save(sender, instance, created, **kwargs):
		if created:
			newEntry = KnowledgeComponent_history(problem = instance.problem, edge = instance.edge, 
				node = instance.node, text = instance.text, dateAdded = instance.dateAdded, dateModified = instance.dateModified, 
				counter = instance.counter, 
		   		originalId = instance.id, historyDate = datetime.now(),historyAction =  "created")
			newEntry.save()

	@staticmethod
	def pre_delete(sender, instance, **kwargs):
		newEntry = KnowledgeComponent_history(problem = instance.problem, edge = instance.edge, 
			node = instance.node, text = instance.text, dateAdded = instance.dateAdded, dateModified = instance.dateModified, 
			counter = instance.counter, 
			originalId = instance.id, historyDate = datetime.now(),historyAction =  "delete")
		newEntry.save()

class KnowledgeComponent_history(models.Model):
	problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
	edge = models.ForeignKey(Edge, on_delete=models.CASCADE, related_name='historyKnowledgeComponentEdge', blank=True, null=True)
	node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='historyKnowledgeComponentNode', blank=True, null=True)
	text = models.TextField()
	dateAdded = models.DateTimeField()
	dateModified = models.DateTimeField(default=None, blank=True, null=True)
	counter = models.IntegerField(default=0)
	originalId = models.IntegerField(default=None, blank=True, null=True)
	historyDate = models.DateTimeField(default=None, blank=True, null=True)
	historyAction = models.TextField(default=None, blank=True, null=True)

	class Meta:
		app_label  = 'studentGraph'