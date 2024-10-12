import json
import string
import random
from re import I
import pkg_resources
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import Integer, Scope, String, Boolean, List, Set, Dict, Float
import ast 
from myxblock.studentGraph.models import Answer, Problem, Node, Edge, Resolution, ErrorSpecificFeedbacks, Hint, Explanation, Doubt, KnowledgeComponent, Attempt, Edge_votes, Node_votes, AskedFeedback
from myxblock.visualGraph import *
from myxblock.openaiExplanation import *
from django.utils.timezone import now
from datetime import datetime  
from django.http import JsonResponse
from django.core import serializers
from unidecode import unidecode
from django.db.models.signals import pre_save, pre_init, post_save, pre_delete
from django.db.models import Q
from django.db import transaction
from xblock.runtime import Runtime
from django.core.management import call_command
from Levenshtein import distance

receivedMinimalFeedbackAmount = 0.1
receivedHintUsefulnessAmount = 1

#Max amount of feedback
maxMinimumFeedback = 4
maxErrorSpecificFeedback = 2
maxExplanations = 2
maxHints = 2
maxDoubts = 2
maxKnowledgeComponent = 2

maxVotesToFixCorrectness = 5

#Max amount of feedbacks to ask for more
maxToAsk = 2

problemGraphDefault = {'_start_': ['Option 1'], 'Option 1': ["Option 2"], "Option 2": ["_end_"]}
problemGraphNodePositionsDefault = {}  
problemGraphStatesCorrectnessDefault = {'_start_': correctState[1], 'Option 1': correctState[1], 'Option 2': correctState[1]}
problemGraphStepsCorrectnessDefault = {str(('_start_', 'Option 1')): validStep[1], str(('Option 1', 'Option 2')): validStep[1], str(('Option 2', '_end_')): validStep[1]}
allResolutionsDefault = []

yesAnswer = ["sim", "s", "yes", "y", "si", "ye"]
noAnswer = ["não", "n", "no", "nao"]

yesUniversalAnswer = "yes"
noUniversalAnswer = "no"

incorrectStates = [175,179,186,187,195,196,222,262,263,264,265,274,287,288,289,290,295,296,394,395,397,477,495,496,500,554,612,660,145,146,159,168,171,199,237,238,270,330,382,383,384,459,605,606,607,608,609,610,611,682,683,684,160,192,194,198,271,272,297,349,350,449,450]
incorrectSteps = [228,229,242,243,287,288,289,290,291,295,361,383,402,403,404,405,406,544,545,546,653,654,679,680,681,687,688,689,690,759,760,820,846,847,914,192,194,198,251,367,370,457,458,525,526,527,528,529,628,629,839,841,842,843,844,945,946,181,231,240,249,267,268,273,376,377,415,416,481,482,616,617,618,661]
stepsWithOneHints = [381,235,234]
stepsWithTwoHints = [223,382]
stepsWithExplanations = [849,850]

#Ainda não salvando nada nessa variável
allResolutionsNew = allResolutionsDefault

def orderErrorSpecificFeedback(element):
    quantity = ErrorSpecificFeedbacks.objects.filter(problem = element.problem, edge = element).count()
    correctness = element.correctness
    return (1/(correctness * 10) * (1/(0.1 + quantity)))

def orderMinimalFeedback(element):
    return abs(element.correctness)

def orderKnowledgeComponent(element):
    return 1 - (abs(element.correctness))

def orderExplanations(element):
    quantity = Explanation.objects.filter(problem = element.problem, edge = element).count()
    correctness = element.correctness
    return (1/(correctness * 10) * (1/(0.1 + quantity)))

def orderHints(element):
    quantity = Hint.objects.filter(problem = element.problem, edge = element).count()
    correctness = element.correctness
    return (1/(correctness * 10) * (1/(0.1 + quantity)))

def orderByTime(element):
    if element.dateModified:
        return element.dateModified
    return element.dateAdded

def transformToSimplerAnswer(answer):
    if answer is not None:
        lowerCase = answer.lower()
        noAccent = unidecode(lowerCase)
        withoutSpaces = noAccent.replace(" ", "")

        return withoutSpaces
    return answer


#Colinha:
#Scope.user_state = Dado que varia de aluno para aluno
#Scope.user_state_summary = Dado igual para todos os alunos
#Scope.content = Dado imutável

class Quatis_main(XBlock):
    pre_save.connect(Node.pre_save, Node, dispatch_uid=".studentGraph.models.Node") 
    post_save.connect(Node.post_save, Node, dispatch_uid=".studentGraph.models.Node") 
    pre_save.connect(Node_votes.pre_save, Node_votes, dispatch_uid=".studentGraph.models.Node_votes") 
    post_save.connect(Node_votes.post_save, Node_votes, dispatch_uid=".studentGraph.models.Node_votes") 
    pre_save.connect(Edge.pre_save, Edge, dispatch_uid=".studentGraph.models.Edge") 
    post_save.connect(Edge.post_save, Edge, dispatch_uid=".studentGraph.models.Edge") 
    pre_delete.connect(Edge.pre_delete, Edge, dispatch_uid=".studentGraph.models.Edge") 
    pre_save.connect(Edge_votes.pre_save, Edge_votes, dispatch_uid=".studentGraph.models.Edge_votes") 
    post_save.connect(Edge_votes.post_save, Edge_votes, dispatch_uid=".studentGraph.models.Edge_votes") 
    pre_save.connect(Resolution.pre_save, Resolution, dispatch_uid=".studentGraph.models.Resolution") 
    post_save.connect(Resolution.post_save, Resolution, dispatch_uid=".studentGraph.models.Resolution") 
    pre_save.connect(ErrorSpecificFeedbacks.pre_save, ErrorSpecificFeedbacks, dispatch_uid=".studentGraph.models.ErrorSpecificFeedbacks") 
    post_save.connect(ErrorSpecificFeedbacks.post_save, ErrorSpecificFeedbacks, dispatch_uid=".studentGraph.models.ErrorSpecificFeedbacks") 
    pre_save.connect(Hint.pre_save, Hint, dispatch_uid=".studentGraph.models.Hint") 
    post_save.connect(Hint.post_save, Hint, dispatch_uid=".studentGraph.models.Hint") 
    pre_save.connect(Explanation.pre_save, Explanation, dispatch_uid=".studentGraph.models.Explanation") 
    post_save.connect(Explanation.post_save, Explanation, dispatch_uid=".studentGraph.models.Explanation") 
    pre_save.connect(Doubt.pre_save, Doubt, dispatch_uid=".studentGraph.models.Doubt") 
    post_save.connect(Doubt.post_save, Doubt, dispatch_uid=".studentGraph.models.Doubt") 
    pre_save.connect(Answer.pre_save, Answer, dispatch_uid=".studentGraph.models.Answer") 
    post_save.connect(Answer.post_save, Answer, dispatch_uid=".studentGraph.models.Answer") 
    pre_save.connect(KnowledgeComponent.pre_save, KnowledgeComponent, dispatch_uid=".studentGraph.models.KnowledgeComponent") 
    post_save.connect(KnowledgeComponent.post_save, KnowledgeComponent, dispatch_uid=".studentGraph.models.KnowledgeComponent") 

    #Se o aluno já fez o exercício
    alreadyAnswered = Boolean(
        default=False, scope=Scope.user_state,
        help="If the student already answered the exercise",
    )

    studentId = Integer(
        default=0, scope=Scope.user_state,
        help="StudentId for the problem",
    )

    studentRetries = Integer(
        default=0, scope=Scope.user_state,
        help="How many attempts",
    )

    #ùltimo erro cometido pelo aluno
    lastWrongElement = String(
        default="", scope=Scope.user_state,
        help="Last wrong element from the student",
    )

    #Quantidade de erros
    lastWrongElementCount = Integer(
        default=0, scope=Scope.user_state,
        help="Last wrong element count from the student",
    )

    currentHints = List(
        default=[], scope=Scope.user_state,
        help="Current hints to be shown to the student",
    )

    #Qual tipo de reedback que foi mostrado
    lastWrongElementType = String(
        default="", scope=Scope.user_state,
        help="Last wrong type type from the student",
    )

    viewedHints = List(
        default=[], scope=Scope.user_state,
        help="Current hints to be shown to the student",
    )
    viewedExplanations = List(
        default=[], scope=Scope.user_state,
        help="Current hints to be shown to the student",
    )
    viewedErrorSpecific = List(
        default=[], scope=Scope.user_state,
        help="Current hints to be shown to the student",
    )
    viewedDoubts = List(
        default=[], scope=Scope.user_state,
        help="Current hints to be shown to the student",
    )
    viewedAnswers = List(
        default=[], scope=Scope.user_state,
        help="Current hints to be shown to the student",
    )



    problemId = Integer(
        default=-1, scope=Scope.content,
        help="Version",
    )

    #Posso até separar em 2, um só para os estados e outro só para os passos
    studentResolutionsStates = List(
        default=["Option 1", "Option 2"], scope=Scope.user_state,
        help="States used by this student",
    )

    studentResolutionsSteps = List(
        default=[str(('_start_', 'Option 1')), str(('Option 1', 'Option 2')), str(('Option 2', '_end_'))], scope=Scope.user_state,
        help="States used by this student",
    )

    #Dados fixos
    problemTitle = String(
        default="Title", scope=Scope.content,
        help="Title of the problem",
    )

    problemDescription = String(
        default="Description test of the problem", scope=Scope.content,
        help="Description of the problem",
    )

    problemDefaultHint = String(
        default="Verifique se a resposta está correta", scope=Scope.content,
        help="If there is no available hint",
    )

    problemDefaultHintEnglish = String(
        default="Please check if your resolution and answer are correct. Check for hints or write a question if necessary", scope=Scope.content,
        help="If there is no available hint",
    )

    problemInitialHint = String(
        default="Inicialmente, coloque o mesmo que está no enunciado", scope=Scope.content,
        help="If thew student dont know how to start the process",
    )

    problemInitialHintEnglish = String(
        default="First, put what's on the question", scope=Scope.content,
        help="If thew student dont know how to start the process",
    )

    problemAnswer1 = String(
        default="Option 1", scope=Scope.content,
        help="Item 1 of the problem",
    )

    problemAnswer2 = String(
        default="Option 2", scope=Scope.content,
        help="Item 2 of the problem",
    )

    problemAnswer3 = String(
        default="Option 3", scope=Scope.content,
        help="Item 3 of the problem",
    )

    problemAnswer4 = String(
        default="Option 4", scope=Scope.content,
        help="Item 4 of the problem",
    )

    problemAnswer5 = String(
        default="Option 5", scope=Scope.content,
        help="Item 5 of the problem",
    )

    problemCorrectAnswer = String(
        default="Option 2", scope=Scope.content,
        help="Correct value",
    )

    problemSubject = String(
        default="Subject", scope=Scope.content,
        help="Subject of the problem",
    )

    problemTags = List(
        default=["Tag1, Tag2, Tag3"], scope=Scope.content,
        help="Tags of the problem",
    )

    callOpenAiExplanation = String(
        default="false", scope=Scope.content,
        help="If the student has access to ask the question to OpenAI",
    )

    questionToAsk = String(
        default="Como resolver uma equação?", scope=Scope.content,
        help="Which question to ask to OpenAI",
    )

    openApiToken = String(
        default="c2stdTZwR3BRVWc4SHQ1MXZuWVNQUmFUM0JsYmtGSmlsTW40bEI1bEdlRW5JQ3NQVGJPCg==", scope=Scope.content,
        help="OpenAI token in Base64",
    )

    language = String(
        default="en", scope=Scope.content,
        help="Language",
    )

    #Resposta desse bloco
    answerSteps = List(
        default=None, scope=Scope.user_state,
        help="Student's steps until the final answer",
    )

    answerRadio = String(
        default=None, scope=Scope.user_state,
        help="Student's answer from the radio button",
    )

    usedStates = List(
        default=[], scope=Scope.user_state,
        help="Student's used states on exercise",
    )

    usedSteps = List(
        default=[], scope=Scope.user_state,
        help="Student's used steps on exercise",
    )

    hasScore = Boolean(
        default=False, scope=Scope.user_state,
        help="If it is going to be graded",
    )

    icon_class = String(
        default="problem", scope=Scope.user_state_summary,
        help="Type of problem",
    )

    answerClick = Integer(
        default=0, scope=Scope.user_state,
        help="Student's final answer",
    )

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    # TO-DO: change this view to display your data your own way.
    def student_view(self, context=None):
        #Adiciona qual arquivo HTML será usado
        self.studentId = self.runtime.user_id
        self.studentRetries += 1

        if self.language == "pt":
            html = self.resource_string("static/html/quatis.html")
        else:
            html = self.resource_string("static/html/quatisEn.html")
        loadedProblem = Problem.objects.filter(id=self.problemId)
        if loadedProblem.exists():
            r1 = Resolution(problem=loadedProblem[0], studentId = self.studentId, dateStarted = datetime.now(), attempt = self.studentRetries)
            r1.save()
            loadedMultipleChoiceProblem = loadedProblem[0].multipleChoiceProblem
            frag = Fragment(str(html).format(block=self, multipleChoiceProblem=loadedMultipleChoiceProblem,useai=self.callOpenAiExplanation))
        else: 
            frag = Fragment(str(html).format(block=self))
            

        frag.add_css(self.resource_string("static/css/quatis.css"))
        frag.add_javascript(self.resource_string("static/js/src/quatis.js"))

        #Também precisa inicializar
        frag.initialize_js('Quatis')
        self.lastWrongElementCount = 0
        self.usedStates = []
        self.usedSteps = []
        self.viewedHints = []
        self.viewedExplanations = []
        self.viewedErrorSpecific = []
        self.viewedDoubts = []
        self.viewedAnswers = []

        return frag

    problem_view = student_view

    def studio_view(self,context=None):
        if self.language == "pt":
            html=self.resource_string("static/html/quatisEditHidden.html")
        else:
            html = self.resource_string("static/html/quatisEditEn.html")

        loadedProblem = Problem.objects.filter(id=self.problemId)
        if loadedProblem.exists():
            loadedMultipleChoiceProblem = loadedProblem[0].multipleChoiceProblem
        else:
            loadedMultipleChoiceProblem = "Valor ainda não carregado"

        frag = Fragment(str(html).format(problemTitle=self.problemTitle,
                                         problemDescription=self.problemDescription,
                                         multipleChoiceProblem=loadedMultipleChoiceProblem,
                                         problemDefaultHint=self.problemDefaultHint,
                                         problemDefaultHintEnglish=self.problemDefaultHintEnglish,
                                         problemInitialHint=self.problemInitialHint,
                                         problemInitialHintEnglish=self.problemInitialHintEnglish,
                                         problemAnswer1=self.problemAnswer1,
                                         problemAnswer2=self.problemAnswer2,
                                         problemAnswer3=self.problemAnswer3,
                                         problemAnswer4=self.problemAnswer4,
                                         problemAnswer5=self.problemAnswer5,
                                         problemCorrectAnswer=self.problemCorrectAnswer,
                                         problemSubject=self.problemSubject,
                                         problemTags=self.problemTags,
                                         callOpenAiExplanation=self.callOpenAiExplanation,
                                         questionToAsk=self.questionToAsk,
                                         openApiToken=self.openApiToken,
                                         language=self.language
                                         ))
        frag.add_javascript(self.resource_string("static/js/src/quatisEdit.js"))

        frag.initialize_js('QuatisEdit')
        return frag

    def calculateCompletness(self, loadedProblem, currentNode, currentNodeIds, currentEdgeIds):
        allSolutions = []
        allSolutions2 = []
        allSums = []
        #reallyIncorrectSteps = [218,219,224,228,229,242,243,292,361,364,383,402,403,404,405,544,545,546,653,654,679,680,681,759,760,820,846,847,914,192,194,198,251,252,259,370,457,458,525,526,527,528,529,628,629,839,841,842,843,844,945,946,181,231,240,249,266,272,274,275,326,376,377,415,416,481,482,616,617,618,661]
        reallyIncorrectStates = [5749,5753,5761,5762,5764,5765,5773,5774,5776,5778,5779,5783,5784,5785,5786,5787,5788,5789,5795,5801,5802,5803,5807,5809,6422,6424,6437,6438,6439,6440,6441,6443,6446,6447,6448,6450,6452,6453,6454,6455,6456,6457,6458,6972,6974,6975,6976,6979,6988,6989,6992,6993,6994,6995,6996]

        steps = Edge.objects.select_for_update().filter(problem=loadedProblem, sourceNode=currentNode)
        for step in steps:
            if (step.destNode.title == '_end_'):
                newList = currentNodeIds.copy()
                newList.append(step.destNode.id)

                newList2 = currentEdgeIds.copy()
                newList2.append(step.id)
                
                allSolutions.append(tuple(newList))
                allSolutions2.append(tuple(newList2))

                allSum = 0
                for node in newList:
                    allSum += 1

                for edge in newList2:
                    allSum += 1
                    if edge not in reallyIncorrectSteps and newList2.index(edge) != 0 and newList2.index(edge) != (len(newList2) - 1):
                        allSum += 2
                    
                allSum+=1
                
                allSums.append(allSum)
                

            else:
                if step.destNode.id not in currentNodeIds:
                    newList = currentNodeIds.copy()
                    newList.append(step.destNode.id)

                    newList2 = currentEdgeIds.copy()
                    newList2.append(step.id)

                    result = self.calculateCompletness(loadedProblem, step.destNode, newList, newList2)

                    allSolutions = allSolutions + result["nodes"]
                    allSolutions2 = allSolutions2 + result["edges"]
                    allSums = allSums + result["allSums"]

        
        return {"nodes": allSolutions, "edges": allSolutions2, "allSums": allSums}

    def calculateCompletness2(self, loadedProblem, currentNode, currentNodeIds, currentEdgeIds):
        allSolutions = []
        allSolutions2 = []
        allSumsOnlyCorrect = []
        allSums = []
        incorrectStates = [5749,5753,5761,5762,5764,5765,5773,5774,5776,5778,5779,5783,5784,5785,5786,5787,5788,5789,5795,5801,5802,5803,5807,5809,6422,6424,6437,6438,6439,6440,6441,6443,6446,6447,6448,6450,6452,6453,6454,6455,6456,6457,6458,6972,6974,6975,6976,6979,6988,6989,6992,6993,6994,6995,6996]
        incorrectSteps = [9057,9069,9070,9072,9073,9074,9075,9076,9077,9078,9081,9085,9091,9092,9093,9095,9096,9104,9105,9106,9117,9119,9120,9121,9123,9124,9125,9126,9127,9128,9131,9132,9133,10111,10112,10136,10140,10141,10146,10147,10148,10149,10150,10151,10152,10156,10158,10159,10160,10161,10979,10984,10990,10992,10993,10995,10997,11000,11001,11008,11009,11010,11011,11012,11013,11015]
        #reallyIncorrectSteps = [218,219,224,228,229,242,243,292,361,364,383,402,403,404,405,544,545,546,653,654,679,680,681,759,760,820,846,847,914,192,194,198,251,252,259,370,457,458,525,526,527,528,529,628,629,839,841,842,843,844,945,946,181,231,240,249,266,272,274,275,326,376,377,415,416,481,482,616,617,618,661]
        #stepsWithOneHints = [381,235,234]
        #stepsWithTwoHints = [223,382,112,113,114,115,116,117,118,119,120,134,135,136,137,138,139,140,141,147,148,149,150,151,152,153,154]
        #stepsWithExplanations = [849,850,112,134,147]
        #stepsStartAndEnd = [108,110,111,121,179,207,214,220,225,226,244,286,293,349,357,359,360,362,363,365,374,412,414,543,549,683,686,819,821,915,130,132,133,142,159,168,173,180,193,195,199,253,258,279,280,302,316,366,368,369,391,395,530,707,816,818,836,845,947,143,145,146,155,163,172,182,232,237,241,246,250,257,269,276,325,327,348,378,483]

        steps = Edge.objects.select_for_update().filter(problem=loadedProblem, sourceNode=currentNode)
        for step in steps:
            if (step.destNode.title == '_end_'):
                newList = currentNodeIds.copy()
                newList.append(step.destNode.id)

                newList2 = currentEdgeIds.copy()
                newList2.append(step.id)
                
                allSolutions.append(tuple(newList))
                allSolutions2.append(tuple(newList2))

                allSumOnlyCorrect = 0
                allSum = 0
                for node in newList:
                    allSum += 2
                    if node in incorrectStates:
                        #Change correctness of nodes
                        allSumOnlyCorrect += 1

                for edge in newList2:
                    allSum += 2
                    if edge in incorrectSteps:
                        #Change correctness of edge
                        allSumOnlyCorrect += 1

                allSumsOnlyCorrect.append(allSumOnlyCorrect)
                allSum -= 8
                allSums.append(allSum)

            else:
                if step.destNode.id not in currentNodeIds:
                    newList = currentNodeIds.copy()
                    newList.append(step.destNode.id)

                    newList2 = currentEdgeIds.copy()
                    newList2.append(step.id)

                    result = self.calculateCompletness2(loadedProblem, step.destNode, newList, newList2)

                    allSolutions = allSolutions + result["nodes"]
                    allSolutions2 = allSolutions2 + result["edges"]
                    allSumsOnlyCorrect = allSumsOnlyCorrect + result["allSumsOnlyCorrect"]
                    allSums = allSums + result["allSums"]

        
        return {"nodes": allSolutions, "edges": allSolutions2, "allSumsOnlyCorrect": allSumsOnlyCorrect, "allSums": allSums}


    @transaction.atomic
    def saveStatesAndSteps(self, elements):

        loadedProblem = Problem.objects.get(id=self.problemId)

        lastElement = None
        for element in elements:
            if transformToSimplerAnswer(element) not in self.usedStates:
                node = Node.objects.select_for_update().filter(problem=loadedProblem, title=transformToSimplerAnswer(element))
                if node.exists():
                    exitingNode = node.first()
                    exitingNode.counter += 1
                    exitingNode.dateModified = datetime.now()
                    exitingNode.save()
                    self.usedStates.append(transformToSimplerAnswer(element))

            if lastElement is not None:
                alreadyInserted = False
                for usedStep in self.usedSteps:
                    if usedStep[0] == transformToSimplerAnswer(lastElement) and usedStep[1] == transformToSimplerAnswer(element):
                        alreadyInserted = True
                        break
                if not alreadyInserted:
                    step = Edge.objects.select_for_update().filter(problem=loadedProblem, sourceNode__title=transformToSimplerAnswer(lastElement), destNode__title = transformToSimplerAnswer(element))
                    if step.exists():
                        existingStep = step.first()
                        existingStep.counter += 1
                        existingStep.dateModified = datetime.now()
                        existingStep.save()
                        self.usedSteps.append((transformToSimplerAnswer(lastElement), transformToSimplerAnswer(element)))
            lastElement = element

    @transaction.atomic
    @XBlock.json_handler
    def finish_activity_time(self,data,suffix=''):
        loadedProblem = Problem.objects.get(id=self.problemId)
        r1 = Resolution.objects.select_for_update().filter(problem=loadedProblem, studentId = self.studentId, attempt = self.studentRetries)

        if r1.exists():
            confirmation = self.generateConfirmationKey(10)
            existingRes = r1.first()
            existingRes.dateFinished = datetime.now()
            existingRes.confirmationKey = confirmation
            existingRes.save()
            return {"status": "Success", "confirmationCode": confirmation}

        return {"status": "Success"}

    def generateConfirmationKey(self, randonLength):
        return str(self.studentId) + ''.join(random.choices(string.ascii_uppercase, k=randonLength))

    @transaction.atomic
    def remove_edge_feedbacks(self, edgeModel, loadedProblem):
        doubts = Doubt.objects.select_for_update().filter(problem=loadedProblem, edge=edgeModel)
        for doubt in doubts:
            answers = Answer.objects.select_for_update().filter(problem=loadedProblem, doubt=doubt)
            for answer in answers:
                answer.doubt = None
                answer.save()
            doubt.edge = None
            doubt.save()

        explanations = Explanation.objects.select_for_update().filter(problem=loadedProblem, edge=edgeModel)
        for explanation in explanations:
            explanation.edge = None
            explanation.save()

        hints = Hint.objects.select_for_update().filter(problem=loadedProblem, edge=edgeModel)
        for hint in hints:
            hint.edge = None
            hint.save()

        errorSpecifics = ErrorSpecificFeedbacks.objects.select_for_update().filter(problem=loadedProblem, edge=edgeModel)
        for errorSpecific in errorSpecifics:
            errorSpecific.edge = None
            errorSpecific.save()

    @transaction.atomic
    def remove_node_feedbacks(self, nodeModel, loadedProblem):
        doubts = Doubt.objects.select_for_update().filter(problem=loadedProblem, node=nodeModel)
        for doubt in doubts:
            answers = Answer.objects.select_for_update().filter(problem=loadedProblem, doubt=doubt)
            for answer in answers:
                answer.doubt = None
                answer.save()
            doubt.node = None
            doubt.save()


    @transaction.atomic
    @XBlock.json_handler
    def submit_graph_data(self,data,suffix=''):
        graphData = data.get('graphData')

        loadedProblem = Problem.objects.get(id=self.problemId)

        for node in graphData['nodes']:
            nodeModel = Node.objects.select_for_update().filter(problem=loadedProblem, title=transformToSimplerAnswer(node["id"]))
            if not nodeModel.exists():
                n1 = Node(title=node["id"], linkedSolution=node["linkedSolution"], correctness=float(node["correctness"]), problem=loadedProblem, nodePositionX=node["x"], nodePositionY=node["y"], dateAdded=datetime.now(), fixedValue=float(node["fixedValue"]))
                n1.save()
            else:
                nodeModel = nodeModel.first()

                if ("x" in node and nodeModel.nodePositionX != node["x"]) or ("y" in node and nodeModel.nodePositionY != node["y"]) or nodeModel.linkedSolution != node["linkedSolution"] or nodeModel.correctness != float(node["correctness"]) or nodeModel.fixedValue != float(node["fixedValue"]) or nodeModel.visible != float(node["visible"]):
                    nodeModel.correctness = float(node["correctness"])
                    nodeModel.fixedValue = float(node["fixedValue"])
                    nodeModel.visible = float(node["visible"])
                    if float(node["visible"]) == 0:
                        self.remove_node_feedbacks(nodeModel, loadedProblem)
                        nodeModel.correctness = 0
                        
                        sourceEdges = Edge.objects.select_for_update().filter(problem=loadedProblem, sourceNode = nodeModel, visible = 1)
                        if sourceEdges.exists():
                            for sourceEdge in sourceEdges:
                                self.remove_edge_feedbacks(sourceEdge, loadedProblem)
                                sourceEdge.visible = 0
                                if sourceEdge.destNode.title != '_end_':
                                    sourceEdge.correctness = 0
                                sourceEdge.save()

                        destEdges = Edge.objects.select_for_update().filter(problem=loadedProblem, destNode = nodeModel, visible = 1)
                        if destEdges.exists():
                            for destEdge in destEdges:
                                self.remove_edge_feedbacks(destEdge, loadedProblem)
                                destEdge.visible = 0
                                if destEdge.sourceNode.title != '_start_':
                                    destEdge.correctness = 0
                                destEdge.save()

                    nodeModel.nodePositionX = node["x"]
                    nodeModel.nodePositionY = node["y"]

                    emptyLinkedSOlution = True
                    if nodeModel.linkedSolution and not nodeModel.linkedSolution.isspace():
                        emptyLinkedSOlution = False

                    newEmptyLinkedSOlution = True
                    if node["linkedSolution"] and not node["linkedSolution"].isspace():
                        newEmptyLinkedSOlution = False
                    
                    if not (emptyLinkedSOlution == True and newEmptyLinkedSOlution == True):
                        nodeModel.linkedSolution = node["linkedSolution"]

                    nodeModel.dateModified = datetime.now()
                    nodeModel.save()
                    if node["modifiedCorrectness"] == 1:
                        self.recalculateResolutionCorrectnessFromNode(nodeModel)

            if "stroke" in node:
                if node["stroke"] in [finalNodeStroke, finalNodeStrokeFixed] and "shape" in node and node["shape"] == finalNodeShape:
                    edgeModel = Edge.objects.filter(problem=loadedProblem, sourceNode__title=transformToSimplerAnswer(node["id"]), destNode__title="_end_")
                    if not edgeModel.exists():
                        fromNode = Node.objects.get(problem=loadedProblem, title=transformToSimplerAnswer(node["id"]))
                        toNode = Node.objects.get(problem=loadedProblem, title="_end_")
                        e1 = Edge(sourceNode=fromNode, destNode=toNode, problem=loadedProblem, dateAdded=datetime.now(), correctness = 1, fixedValue = 1)
                        e1.save()
                    startEdge = Edge.objects.select_for_update().filter(problem=loadedProblem, sourceNode__title="_start_", destNode__title=transformToSimplerAnswer(node["id"]))
                    if startEdge.exists():
                        startEdge.first().delete()
                elif node["stroke"] in [initialNodeStroke, initialNodeStrokeFixed]:
                    edgeModel = Edge.objects.filter(problem=loadedProblem, sourceNode__title="_start_", destNode__title=transformToSimplerAnswer(node["id"]))
                    if not edgeModel.exists():
                        fromNode = Node.objects.get(problem=loadedProblem, title="_start_")
                        toNode = Node.objects.get(problem=loadedProblem, title=transformToSimplerAnswer(node["id"]))
                        e1 = Edge(sourceNode=fromNode, destNode=toNode, problem=loadedProblem, dateAdded=datetime.now(), correctness = 1, fixedValue = 1)
                        e1.save()
                    endEdge = Edge.objects.select_for_update().filter(problem=loadedProblem, sourceNode__title=transformToSimplerAnswer(node["id"]), destNode__title="_end_")
                    if endEdge.exists():
                        endEdge.first().delete()
                elif node["stroke"] in [multipleNodeStroke, multipleNodeStrokeFixed] and "shape" in node and node["shape"] == multipleNodeShape:
                    edgeModel = Edge.objects.filter(problem=loadedProblem, sourceNode__title="_start_", destNode__title=transformToSimplerAnswer(node["id"]))
                    if not edgeModel.exists():
                        fromNode = Node.objects.get(problem=loadedProblem, title="_start_")
                        toNode = Node.objects.get(problem=loadedProblem, title=transformToSimplerAnswer(node["id"]))
                        e1 = Edge(sourceNode=fromNode, destNode=toNode, problem=loadedProblem, dateAdded=datetime.now(), correctness = 1, fixedValue = 1)
                        e1.save()

                    edgeModel = Edge.objects.filter(problem=loadedProblem, sourceNode__title=transformToSimplerAnswer(node["id"]), destNode__title="_end_")
                    if not edgeModel.exists():
                        fromNode = Node.objects.get(problem=loadedProblem, title=transformToSimplerAnswer(node["id"]))
                        toNode = Node.objects.get(problem=loadedProblem, title="_end_")
                        e1 = Edge(sourceNode=fromNode, destNode=toNode, problem=loadedProblem, dateAdded=datetime.now(), correctness = 1, fixedValue = 1)
                        e1.save()
                else:
                    endEdge = Edge.objects.select_for_update().filter(problem=loadedProblem, sourceNode__title=transformToSimplerAnswer(node["id"]), destNode__title="_end_")
                    if endEdge.exists():
                        endEdge.first().delete()
                    startEdge = Edge.objects.select_for_update().filter(problem=loadedProblem, sourceNode__title="_start_", destNode__title=transformToSimplerAnswer(node["id"]))
                    if startEdge.exists():
                        startEdge.first().delete()
            else:
                endEdge = Edge.objects.select_for_update().filter(problem=loadedProblem, sourceNode__title=transformToSimplerAnswer(node["id"]), destNode__title="_end_")
                if endEdge.exists():
                    endEdge.first().delete()
                startEdge = Edge.objects.select_for_update().filter(problem=loadedProblem, sourceNode__title="_start_", destNode__title=transformToSimplerAnswer(node["id"]))
                if startEdge.exists():
                    startEdge.first().delete()



        for edge in graphData['edges']:
            edgeModel = Edge.objects.filter(problem=loadedProblem, sourceNode__title=transformToSimplerAnswer(edge["from"]), destNode__title=transformToSimplerAnswer(edge["to"]))
            if not edgeModel.exists():
                fromNode = Node.objects.get(problem=loadedProblem, title=transformToSimplerAnswer(edge["from"]))
                toNode = Node.objects.get(problem=loadedProblem, title=transformToSimplerAnswer(edge["to"]))
                e1 = Edge(sourceNode=fromNode, destNode=toNode, correctness=float(edge["correctness"]), problem=loadedProblem, dateAdded=datetime.now(), fixedValue=float(edge["fixedValue"]))
                e1.save()
            else:
                edgeModel = Edge.objects.select_for_update().get(problem=loadedProblem, sourceNode__title=transformToSimplerAnswer(edge["from"]), destNode__title=transformToSimplerAnswer(edge["to"]))
                if edgeModel.correctness != float(edge["correctness"]) or edgeModel.visible != edge["visible"] or edgeModel.fixedValue != float(edge["fixedValue"]):
                    edgeModel.correctness = float(edge["correctness"])
                    edgeModel.visible = edge["visible"]
                    if edge["visible"] == 0:
                        self.remove_edge_feedbacks(edgeModel, loadedProblem)
                        edgeModel.correctness = 0
                    edgeModel.dateModified = datetime.now()
                    edgeModel.fixedValue = float(edge["fixedValue"])
                    edgeModel.save()
                    if edge["modifiedCorrectness"] == 1:
                        self.recalculateResolutionCorrectnessFromEdge(edgeModel)

        return {}
    
    def setDataOrUseDefault(self, data, key, defaultValue):
        return data[key] if key in data else defaultValue

    @XBlock.json_handler
    @transaction.atomic
    def import_data(self,data,suffix=''):
        problemData = json.loads(data.get('problemData'))
        loadedProblem = Problem.objects.select_for_update().get(id=self.problemId)
        startNode = Node.objects.get(problem=loadedProblem, title="_start_")
        endNode = Node.objects.get(problem=loadedProblem, title="_end_")

        self.problemTitle = self.setDataOrUseDefault(problemData, "problemTitle", self.problemTitle)
        self.problemDescription = self.setDataOrUseDefault(problemData, "problemDescription", self.problemDescription)
        loadedProblem.multipleChoiceProblem = self.setDataOrUseDefault(problemData, "multipleChoiceProblem", loadedProblem.multipleChoiceProblem)
        self.problemDefaultHint = self.setDataOrUseDefault(problemData, "problemDefaultHint", self.problemDefaultHint)
        self.problemDefaultHintEnglish = self.setDataOrUseDefault(problemData, "problemDefaultHintEnglish", self.problemDefaultHint)
        self.problemInitialHint = self.setDataOrUseDefault(problemData, "problemInitialHint", self.problemInitialHint)
        self.problemInitialHintEnglish = self.setDataOrUseDefault(problemData, "problemInitialHintEnglish", self.problemInitialHint)
        self.problemAnswer1 = self.setDataOrUseDefault(problemData, "problemAnswer1", self.problemAnswer1)
        self.problemAnswer2 = self.setDataOrUseDefault(problemData, "problemAnswer2", self.problemAnswer2)
        self.problemAnswer3 = self.setDataOrUseDefault(problemData, "problemAnswer3", self.problemAnswer3)
        self.problemAnswer4 = self.setDataOrUseDefault(problemData, "problemAnswer4", self.problemAnswer4)
        self.problemAnswer5 = self.setDataOrUseDefault(problemData, "problemAnswer5", self.problemAnswer5)
        self.problemCorrectAnswer = self.setDataOrUseDefault(problemData, "problemCorrectAnswer", self.problemCorrectAnswer)
        self.problemSubject = self.setDataOrUseDefault(problemData, "problemSubject", self.problemSubject)
        self.problemTags = ast.literal_eval(self.setDataOrUseDefault(problemData, "problemTags", self.problemTags))
        self.callOpenAiExplanation = self.setDataOrUseDefault(problemData, "callOpenAiExplanation", self.callOpenAiExplanation)
        self.questionToAsk = self.setDataOrUseDefault(problemData, "questionToAsk", self.questionToAsk)
        self.openApiToken = self.setDataOrUseDefault(problemData, "openApiToken", self.openApiToken)
        self.language = self.setDataOrUseDefault(problemData, "language", self.language)

        for node in problemData['nodes']:
            nodeModel = Node.objects.select_for_update().filter(problem=loadedProblem, title=transformToSimplerAnswer(node["title"]))
            if not nodeModel.exists():
                n1 = Node(title=node["title"], linkedSolution=self.setDataOrUseDefault(node, "linkedSolution", None), correctness=float(self.setDataOrUseDefault(node,"correctness", 0)), problem=loadedProblem, nodePositionX=self.setDataOrUseDefault(node, "nodePositionX", -1), nodePositionY=self.setDataOrUseDefault(node, "nodePositionY", -1), dateAdded=datetime.now(), fixedValue=self.setDataOrUseDefault(node, "fixedValue", 0), counter=self.setDataOrUseDefault(node, "counter", 0),alreadyCalculatedPos=self.setDataOrUseDefault(node, "alreadyCalculatedPos", 0), customPos=self.setDataOrUseDefault(node, "customPos", 0))
                n1.save()
            else:
                n1 = nodeModel.first()
                n1.correctness = float(self.setDataOrUseDefault(nodeModel, "correctness", n1.correctness))
                n1.fixedValue = self.setDataOrUseDefault(nodeModel, "fixedValue", n1.fixedValue)
                n1.counter = self.setDataOrUseDefault(nodeModel, "counter", n1.fixedValue)
                n1.nodePositionX = self.setDataOrUseDefault(nodeModel, "nodePositionX", n1.nodePositionX)
                n1.nodePositionY = self.setDataOrUseDefault(nodeModel, "nodePositionY", n1.nodePositionY)
                n1.linkedSolution = self.setDataOrUseDefault(nodeModel, "linkedSolution", n1.linkedSolution)
                n1.alreadyCalculatedPos = self.setDataOrUseDefault(nodeModel, "alreadyCalculatedPos", n1.alreadyCalculatedPos)
                n1.customPos = self.setDataOrUseDefault(nodeModel, "customPos", n1.customPos)
                n1.dateModified = datetime.now()
                n1.visible = 1
                n1.save()

            if "type" in node:
                if node["type"] == "multiple":
                    possibleInitialEdge = Edge.objects.select_for_update().filter(sourceNode=startNode, destNode=n1, problem=loadedProblem)
                    if not possibleInitialEdge.exists():
                        e1 = Edge(sourceNode=startNode, destNode=n1, problem=loadedProblem, dateAdded=datetime.now(), correctness=1, fixedValue=1)
                        e1.save()

                    possibleFinalEdge = Edge.objects.select_for_update().filter(sourceNode=n1, destNode=endNode, problem=loadedProblem)
                    if not possibleFinalEdge.exists():
                        e1 = Edge(sourceNode=n1, destNode=endNode, problem=loadedProblem, dateAdded=datetime.now(), correctness=1, fixedValue=1)
                        e1.save()
                elif node["type"] == "initial":
                    possibleFinalEdge = Edge.objects.select_for_update().filter(sourceNode=n1, destNode=endNode, problem=loadedProblem)
                    if possibleFinalEdge.exists():
                        possibleFinalEdge.first().delete()
                    possibleInitialEdge = Edge.objects.select_for_update().filter(sourceNode=startNode, destNode=n1, problem=loadedProblem)
                    if not possibleInitialEdge.exists():
                        e1 = Edge(sourceNode=startNode, destNode=n1, problem=loadedProblem, dateAdded=datetime.now(), correctness=1, fixedValue=1)
                        e1.save()
                elif node["type"] == "final":
                    possibleInitialEdge = Edge.objects.select_for_update().filter(sourceNode=startNode, destNode=n1, problem=loadedProblem)
                    if possibleInitialEdge.exists():
                        possibleInitialEdge.first().delete()
                    possibleFinalEdge = Edge.objects.select_for_update().filter(sourceNode=n1, destNode=endNode, problem=loadedProblem)
                    if not possibleFinalEdge.exists():
                        e1 = Edge(sourceNode=n1, destNode=endNode, problem=loadedProblem, dateAdded=datetime.now(), correctness=1, fixedValue=1)
                        e1.save()

            if "doubts" in node:
                for doubt in node["doubts"]:
                    d1 = Doubt(node=n1, studentId = self.studentId, type=0, text=doubt["text"], problem=loadedProblem, dateAdded=datetime.now())
                    d1.save()

                    if "answers" in doubt:
                        for answer in doubt["answers"]:
                            a1 = Answer(doubt=d1, text=answer["text"], studentId = self.studentId, usefulness=self.setDataOrUseDefault(answer, "usefulness", 0), problem=loadedProblem, dateAdded=datetime.now())
                            a1.save()

        for edge in problemData['edges']:
            edgeModel = Edge.objects.filter(problem=loadedProblem, sourceNode__title=transformToSimplerAnswer(edge["from"]), destNode__title=transformToSimplerAnswer(edge["to"]))
            if not edgeModel.exists():
                fromNode = Node.objects.get(problem=loadedProblem, title=transformToSimplerAnswer(edge["from"]))
                toNode = Node.objects.get(problem=loadedProblem, title=transformToSimplerAnswer(edge["to"]))
                e1 = Edge(sourceNode=fromNode, destNode=toNode, correctness=float(self.setDataOrUseDefault(edge, "correctness", 0)), problem=loadedProblem, dateAdded=datetime.now(), fixedValue=self.setDataOrUseDefault(edge, "fixedValue", 0), counter=self.setDataOrUseDefault(edge, "counter", 0))
                e1.save()
            else:
                e1 = edgeModel.first()
                e1.correctness = float(self.setDataOrUseDefault(edge, "correctness", e1.correctness))
                e1.dateModified = datetime.now()
                e1.fixedValue = self.setDataOrUseDefault(edge, "fixedValue", e1.fixedValue)
                e1.counter = self.setDataOrUseDefault(edge, "counter", e1.fixedValue)
                e1.visible = 1
                e1.save()

            if "hints" in edge:
                for hint in edge["hints"]:
                    h1 = Hint(edge=e1, text=hint["text"], studentId = self.studentId, priority=self.setDataOrUseDefault(hint, "priority", 0), usefulness=self.setDataOrUseDefault(hint, "usefulness", 0), problem=loadedProblem, dateAdded=datetime.now())
                    h1.save()

            if "explanations" in edge:
                for explanation in edge["explanations"]:
                    ex1 = Explanation(edge=e1, studentId = self.studentId, text=explanation["text"], priority=self.setDataOrUseDefault(explanation, "priority", 0), usefulness=self.setDataOrUseDefault(explanation, "usefulness", 0), problem=loadedProblem, dateAdded=datetime.now())
                    ex1.save()

            if "errorSpecificFeedbacks" in edge:
                for errorSpecificFeedback in edge["errorSpecificFeedbacks"]:
                    esf1 = ErrorSpecificFeedbacks(edge=e1, studentId = self.studentId, text=errorSpecificFeedback["text"], priority=self.setDataOrUseDefault(errorSpecificFeedback, "priority", 0), usefulness=self.setDataOrUseDefault(errorSpecificFeedback, "usefulness", 0), problem=loadedProblem, dateAdded=datetime.now())
                    esf1.save()

            if "doubts" in edge:
                for doubt in edge["doubts"]:
                    d1 = Doubt(edge=e1, type=1, studentId = self.studentId, text=doubt["text"], problem=loadedProblem, dateAdded=datetime.now())
                    d1.save()

                    if "answers" in doubt:
                        for answer in doubt["answers"]:
                            a1 = Answer(doubt=d1, text=answer["text"], studentId = self.studentId, usefulness=self.setDataOrUseDefault(answer, "usefulness", 0), problem=loadedProblem, dateAdded=datetime.now())
                            a1.save()

        createGraphInitialPositions(self.problemId)


        loadedProblem.dateModified=datetime.now()
        loadedProblem.save()

        return {}

    @XBlock.json_handler
    def get_doubts_and_answers_from_step(self,data,suffix=''):
        edgeDoubts = self.getDoubtsAndAnswersFromStep(data)
        return {"doubts": edgeDoubts}

    def getDoubtsAndAnswersFromStep(self,data):
        loadedProblem = Problem.objects.get(id=self.problemId)
        loadedEdge = Edge.objects.filter(problem=loadedProblem, sourceNode__title=transformToSimplerAnswer(data.get("from")), destNode__title=transformToSimplerAnswer(data.get("to")))
        edgeDoubts = []

        if loadedEdge.exists():

            loadedDoubts = Doubt.objects.filter(problem=loadedProblem, edge=loadedEdge.first())
            if loadedDoubts.exists():
                for loadedDoubt in loadedDoubts:
                    loadedAnswers = Answer.objects.filter(problem=loadedProblem, doubt=loadedDoubt).order_by('-usefulness')
                    edgeDoubtAnswers = []
                    for loadedAnswer in loadedAnswers:
                        edgeDoubtAnswers.append({"id": loadedAnswer.id, "counter": loadedAnswer.counter, "text": loadedAnswer.text, "usefulness": loadedAnswer.usefulness})
                    edgeDoubts.append({"id": loadedDoubt.id, "counter": loadedDoubt.counter, "text": loadedDoubt.text, "answers": edgeDoubtAnswers})

        return edgeDoubts

    @XBlock.json_handler
    @transaction.atomic
    def reset_counters(self,data,suffix=''):
        loadedProblem = Problem.objects.get(id=self.problemId)
        allNodes = Node.objects.filter(problem=loadedProblem).exclude(visible = 0)
        allEdges = Edge.objects.filter(problem=loadedProblem).exclude(visible = 0)
        allHints = Hint.objects.filter(problem=loadedProblem).exclude(edge__isnull = True)
        allExplanations = Explanation.objects.filter(problem=loadedProblem).exclude(edge__isnull = True)
        allErrorSpecificFeedbacks = ErrorSpecificFeedbacks.objects.filter(problem=loadedProblem).exclude(edge__isnull = True)
        allDoubts = Doubt.objects.filter(problem=loadedProblem).exclude(edge__isnull = True, type = 1).exclude(node__isnull = True, type = 0)
        allAnswers = Answer.objects.filter(problem=loadedProblem).exclude(doubt__isnull = True)

        for node in allNodes:
            node.counter = 0
            node.save()

        for edge in allEdges:
            edge.counter = 0
            edge.save()

        for hint in allHints:
            hint.counter = 0
            hint.save()

        for explanation in allExplanations:
            explanation.counter = 0
            explanation.save()

        for errorSpecific in allErrorSpecificFeedbacks:
            errorSpecific.counter = 0
            errorSpecific.save()

        for doubt in allDoubts:
            doubt.counter = 0
            doubt.save()

        for answer in allAnswers:
            answer.counter = 0
            answer.save()

        return {"status": "Success"}


    @XBlock.json_handler
    def get_doubts_and_answers_from_state(self,data,suffix=''):

        loadedProblem = Problem.objects.get(id=self.problemId)
        loadedNode = Node.objects.filter(problem=loadedProblem, title=transformToSimplerAnswer(data.get("node")))
        nodeDoubts = []
        if loadedNode.exists():

            loadedDoubts = Doubt.objects.filter(problem=loadedProblem, node=loadedNode.first())
            if loadedDoubts.exists():
                for loadedDoubt in loadedDoubts:
                    loadedAnswers = Answer.objects.filter(problem=loadedProblem, doubt=loadedDoubt).order_by('-usefulness')
                    nodeDoubtAnswers = []
                    for loadedAnswer in loadedAnswers:
                        nodeDoubtAnswers.append({"id": loadedAnswer.id, "counter": loadedAnswer.counter, "text": loadedAnswer.text, "usefulness": loadedAnswer.usefulness})

                    nodeDoubts.append({"id": loadedDoubt.id, "counter": loadedDoubt.counter, "text": loadedDoubt.text, "answers": nodeDoubtAnswers})

        
        return {"doubts": nodeDoubts}

    @XBlock.json_handler
    @transaction.atomic
    def delete_doubts(self,data,suffix=''):
        loadedProblem = Problem.objects.get(id=self.problemId)
        for doubt in data.get("doubts"):
            loadedDoubt = Doubt.objects.select_for_update().filter(problem=loadedProblem, id=doubt.get("id"))
            if loadedDoubt.exists():
                existingDoubt = loadedDoubt.first()
                existingDoubt.edge = None
                existingDoubt.node = None
                existingDoubt.save();

        return {"result": "success"}

    @XBlock.json_handler
    @transaction.atomic
    def delete_answers(self,data,suffix=''):
        loadedProblem = Problem.objects.get(id=self.problemId)
        for answer in data.get("answers"):
            loadedAnswer = Answer.objects.select_for_update().filter(problem=loadedProblem, id=answer.get("id"))
            if loadedAnswer.exists():
                existingAnswer = loadedAnswer.first()
                existingAnswer.doubt = None
                existingAnswer.save();

        return {"result": "success"}

    @XBlock.json_handler
    @transaction.atomic
    def delete_feedbacks(self,data,suffix=''):
        loadedProblem = Problem.objects.get(id=self.problemId)

        if data.get("hints") is not None:
            allHints = data.get("hints")
            for hint in allHints:
                loadedHint = Hint.objects.select_for_update().filter(problem=loadedProblem, id=hint.get("id"))
                if loadedHint.exists():
                    existingHint = loadedHint.first()
                    existingHint.edge = None
                    existingHint.save();
        if data.get("explanations") is not None:
            allExplanations = data.get("explanations")
            for explanation in allExplanations:
                loadedExplanation = Explanation.objects.select_for_update().filter(problem=loadedProblem, id=explanation.get("id"))
                if loadedExplanation.exists():
                    existingExplanation = loadedExplanation.first()
                    existingExplanation.edge = None
                    existingExplanation.save();
        if data.get("errorSpecificFeedbacks") is not None:
            allFeedbacks = data.get("errorSpecificFeedbacks")
            for feedback in allFeedbacks:
                loadedFeedback = ErrorSpecificFeedbacks.objects.select_for_update().filter(problem=loadedProblem, id=feedback.get("id"))
                if loadedFeedback.exists():
                    existingFeedback = loadedFeedback.first()
                    existingFeedback.edge = None
                    existingFeedback.save();

        return {"result": "success"}


    @XBlock.json_handler
    def get_edge_info(self,data,suffix=''):
        errorSpecificFeedbacks = None
        explanations = None
        hints = None

        loadedProblem = Problem.objects.get(id=self.problemId)
        loadedEdge = Edge.objects.get(problem=loadedProblem, sourceNode__title=transformToSimplerAnswer(data.get("from")), destNode__title=transformToSimplerAnswer(data.get("to")))
        loadedHints = Hint.objects.filter(problem=loadedProblem, edge=loadedEdge).order_by("-usefulness", "priority")
        hints = []
        if loadedHints.exists():
            for hint in loadedHints:
                hints.append({"id": hint.id, "counter": hint.counter, "text": hint.text, "priority": hint.priority, "usefulness": hint.usefulness})

        loadedExplanations = Explanation.objects.filter(problem=loadedProblem, edge=loadedEdge).order_by("-usefulness", "priority")
        explanations = []
        if loadedExplanations.exists():
            for explanation in loadedExplanations:
                explanations.append({"id": explanation.id, "counter": explanation.counter, "text": explanation.text, "priority": explanation.priority, "usefulness": explanation.usefulness})

        loadedErrorSpecificFeedbacks = ErrorSpecificFeedbacks.objects.filter(problem=loadedProblem, edge=loadedEdge).order_by("-usefulness", "priority")
        errorSpecificFeedbacks = []
        if loadedErrorSpecificFeedbacks.exists():
            for errorSpecificFeedback in loadedErrorSpecificFeedbacks:
                errorSpecificFeedbacks.append({"id": errorSpecificFeedback.id, "counter": errorSpecificFeedback.counter, "text": errorSpecificFeedback.text, "priority": errorSpecificFeedback.priority, "usefulness": errorSpecificFeedback.usefulness})

        edgeDoubts = self.getDoubtsAndAnswersFromStep(data)
        
        return {"errorSpecificFeedbacks": errorSpecificFeedbacks, "explanations": explanations, "hints": hints, "doubts": edgeDoubts}

    @XBlock.json_handler
    @transaction.atomic
    def submit_doubt_answer_info(self,data,suffix=''):
        loadedProblem = Problem.objects.get(id=self.problemId)

        answerId = data.get("id")
        loadedAnswer = Answer.objects.select_for_update().get(problem=loadedProblem, id=answerId)
        loadedAnswer.dateModified = datetime.now()
        loadedAnswer.usefulness = data.get("usefulness")
        loadedAnswer.text = data.get("text")
        loadedAnswer.save()

        return {"status": "Done!"}


    @XBlock.json_handler
    @transaction.atomic
    def submit_node_info(self,data,suffix=''):
        loadedProblem = Problem.objects.get(id=self.problemId)
        loadedNode = Node.objects.get(problem=loadedProblem, title=transformToSimplerAnswer(data.get("node")))

        newAnswers = []

        allDoubts = data.get("doubts")
        for doubt in allDoubts:
            if "id" in doubt:
                loadedDoubt = Doubt.objects.select_for_update().get(problem=loadedProblem, node=loadedNode, id=doubt["id"])
                loadedDoubt.dateModified = datetime.now()
            else:
                loadedDoubt = Doubt(problem=loadedProblem, node=loadedNode, dateAdded=datetime.now(), studentId = self.studentId)

            loadedDoubt.text = doubt["text"]
            loadedDoubt.save()

            allAnswers = doubt["answers"]
            for answer in allAnswers:
                newElement = False
                if "id" in answer and answer['id'] != "":
                    loadedAnswer = Answer.objects.select_for_update().get(problem=loadedProblem, id=answer["id"])
                    loadedAnswer.dateModified = datetime.now()
                else:
                    loadedAnswer = Answer(problem=loadedProblem, doubt=loadedDoubt, dateAdded=datetime.now(), studentId = self.studentId)
                    newElement = True

                if "usefulness" in answer:
                    loadedAnswer.usefulness = answer["usefulness"]

                loadedAnswer.text = answer["text"]
                loadedAnswer.save()
                if newElement:
                    newAnswers.append({"id": loadedAnswer.id, "text": loadedAnswer.text, "usefulness": loadedAnswer.usefulness})

        return {"status": "Done!", "newAnswers": newAnswers}


    @XBlock.json_handler
    @transaction.atomic
    def submit_edge_info(self,data,suffix=''):

        loadedProblem = Problem.objects.get(id=self.problemId)
        loadedEdge = Edge.objects.get(problem=loadedProblem, sourceNode__title=transformToSimplerAnswer(data.get("from")), destNode__title=transformToSimplerAnswer(data.get("to")))
        newAnswers = []
        newHints = []
        newExplanations = []
        newErrorSpecificFeedbacks = []
        
        if data.get("hints") is not None:
            allHints = data.get("hints")
            for hint in allHints:
                newHint = False
                if "id" in hint and hint['id'] != "":
                    loadedHint = Hint.objects.select_for_update().get(problem=loadedProblem, edge=loadedEdge, id=hint["id"])
                    loadedHint.dateModified = datetime.now()
                else:
                    loadedHint = Hint(problem=loadedProblem, edge=loadedEdge, dateAdded=datetime.now(), studentId = self.studentId)
                    newHint = True

                loadedHint.text = hint["text"]
                loadedHint.usefulness = int(hint["usefulness"])
                loadedHint.priority = int(hint["priority"])
                loadedHint.save()
                if newHint:
                    newHints.append({"id": loadedHint.id, "text": loadedHint.text, "usefulness": loadedHint.usefulness, "priority": loadedHint.priority})


        if data.get("errorSpecificFeedbacks") is not None:
            allErrorSpecificFeedbacks = data.get("errorSpecificFeedbacks")
            for errorSpecificFeedback in allErrorSpecificFeedbacks:
                newErrorSpecificFeedback = False
                if "id" in errorSpecificFeedback and errorSpecificFeedback['id'] != "":
                    loadedError = ErrorSpecificFeedbacks.objects.select_for_update().get(problem=loadedProblem, edge=loadedEdge, id=errorSpecificFeedback["id"])
                    loadedError.dateModified = datetime.now()
                else:
                    loadedError = ErrorSpecificFeedbacks(problem=loadedProblem, edge=loadedEdge, dateAdded=datetime.now(), studentId = self.studentId)
                    newErrorSpecificFeedback = True

                loadedError.text = errorSpecificFeedback["text"]
                loadedError.usefulness = int(errorSpecificFeedback["usefulness"])
                loadedError.priority = int(errorSpecificFeedback["priority"])
                loadedError.save()
                if newErrorSpecificFeedback:
                    newErrorSpecificFeedbacks.append({"id": loadedError.id, "text": loadedError.text, "usefulness": loadedError.usefulness, "priority": loadedError.priority})


        if data.get("explanations") is not None:
            allExplanations = data.get("explanations")
            for explanation in allExplanations:
                newExplanation = False
                if "id" in explanation and explanation['id'] != "":
                    loadedExplanation = Explanation.objects.select_for_update().get(problem=loadedProblem, edge=loadedEdge, id=explanation["id"])
                    loadedExplanation.dateModified = datetime.now()
                else:
                    loadedExplanation = Explanation(problem=loadedProblem, edge=loadedEdge, dateAdded=datetime.now(), studentId = self.studentId)
                    newExplanation = True

                loadedExplanation.text = explanation["text"]
                loadedExplanation.usefulness = int(explanation["usefulness"])
                loadedExplanation.priority = int(explanation["priority"])
                loadedExplanation.save()
                if newExplanation:
                    newExplanations.append({"id": loadedExplanation.id, "text": loadedExplanation.text, "usefulness": loadedExplanation.usefulness, "priority": loadedExplanation.priority})

        if data.get("doubts") is not None:
            allDoubts = data.get("doubts")
            for doubt in allDoubts:
                if "id" in doubt:
                    loadedDoubt = Doubt.objects.select_for_update().get(problem=loadedProblem, edge=loadedEdge, id=doubt["id"])
                    loadedDoubt.dateModified = datetime.now()
                else:
                    loadedDoubt = Doubt(problem=loadedProblem, edge=loadedEdge, dateAdded=datetime.now(), studentId = self.studentId)

                loadedDoubt.text = doubt["text"]
                loadedDoubt.save()

                allAnswers = doubt["answers"]
                for answer in allAnswers:
                    newElement = False
                    if "id" in answer and answer['id'] != "":
                        loadedAnswer = Answer.objects.select_for_update().get(problem=loadedProblem, id=answer["id"])
                        loadedAnswer.dateModified = datetime.now()
                    else:
                        loadedAnswer = Answer(problem=loadedProblem, doubt=loadedDoubt, dateAdded=datetime.now(), studentId = self.studentId)
                        newElement = True

                    if "usefulness" in answer:
                        loadedAnswer.usefulness = int(answer["usefulness"])
                
                    loadedAnswer.text = answer["text"]
                    loadedAnswer.save()
                    if newElement:
                        newAnswers.append({"id": loadedAnswer.id, "text": loadedAnswer.text, "usefulness": loadedAnswer.usefulness})

        return {"status": "Done!", "newAnswers": newAnswers, "newHints": newHints, "newExplanations": newExplanations, "newErrorSpecificFeedbacks": newErrorSpecificFeedbacks}

    @XBlock.json_handler
    def update_positions(self,data,suffix=''):
        createGraphInitialPositions(self.problemId)

        return {"Status": "Ok"}


    def createInitialEdgeData(self, nodeList, problemFK):
        e1 = Edge(sourceNode=nodeList[0], destNode=nodeList[1], correctness=1, fixedValue=1, problem=problemFK, dateAdded=datetime.now())
        e2 = Edge(sourceNode=nodeList[1], destNode=nodeList[2], correctness=1, fixedValue=1, problem=problemFK, dateAdded=datetime.now())
        e3 = Edge(sourceNode=nodeList[2], destNode=nodeList[3], correctness=1, fixedValue=1, problem=problemFK, dateAdded=datetime.now())

        e1.save()
        e2.save()
        e3.save()

        hint21 = Hint(problem=problemFK, edge=e2)
        hint21.text="hint 1"
        hint21.dateAdded = datetime.now()
        hint21.studentId = self.studentId
        hint21.priority = 1
        hint21.usefulness = 1000

        hint22 = Hint(problem=problemFK, edge=e2)
        hint22.text="Hint 2"
        hint22.dateAdded = datetime.now()
        hint22.studentId = self.studentId
        hint22.priority = 2
        hint22.usefulness = 1000

        hint21.save()
        hint22.save()

        errorSpecificFeedback1 = ErrorSpecificFeedbacks(problem=problemFK, edge=e2)
        errorSpecificFeedback1.text="Error Specific feedback 1"
        errorSpecificFeedback1.dateAdded = datetime.now()
        errorSpecificFeedback1.studentId = self.studentId
        errorSpecificFeedback1.priority = 1
        errorSpecificFeedback1.usefulness = 1000
        errorSpecificFeedback1.save()

        errorSpecificFeedback2 = ErrorSpecificFeedbacks(problem=problemFK, edge=e2)
        errorSpecificFeedback2.text="Error Specific Feedback 2"
        errorSpecificFeedback2.dateAdded = datetime.now()
        errorSpecificFeedback2.studentId = self.studentId
        errorSpecificFeedback2.priority = 2
        errorSpecificFeedback2.usefulness = 1000
        errorSpecificFeedback2.save()

        explanations1 = Explanation(problem=problemFK, edge=e2)
        explanations1.text="Explanation feedback 1"
        explanations1.dateAdded = datetime.now()
        explanations1.studentId = self.studentId
        explanations1.priority = 1
        explanations1.usefulness = 1000
        explanations1.save()

        explanations2 = Explanation(problem=problemFK, edge=e2)
        explanations2.text="Explanation Feedback 2"
        explanations2.dateAdded = datetime.now()
        explanations2.studentId = self.studentId
        explanations2.priority = 2
        explanations2.usefulness = 1000
        explanations2.save()

        return [e1, e2, e3]        

    def createInitialResolutionData(self, nodeList, edgeList, problemFK):
        nodeArray = []
        edgeArray = []
        for node in nodeList:
            nodeArray.append(node.id)

        for edge in edgeList:
            edgeArray.append(edge.id)

        r1 = Resolution(nodeIdList=json.dumps(nodeArray), edgeIdList=json.dumps(edgeArray), correctness=1, problem=problemFK, dateAdded=datetime.now())

        r1.save()


    def createInitialNodeData(self, problemFK):
        n1 = Node(title="_start_", correctness=1, fixedValue=1, alreadyCalculatedPos = 1, problem=problemFK, dateAdded=datetime.now())
        #n2 = Node(title="Option 1", correctness=1, fixedValue=1, problem=problemFK, dateAdded=datetime.now())
        #n3 = Node(title="Option 2", correctness=1, fixedValue=1, problem=problemFK, dateAdded=datetime.now(), linkedSolution="Option 2")
        n4 = Node(title="_end_", correctness=1, fixedValue=1, alreadyCalculatedPos = 1, problem=problemFK, dateAdded=datetime.now())

        n1.save()
        #n2.save()
        #n3.save()
        n4.save()
        
        #nodeList = [n1, n2, n3, n4]

        #edgeList = self.createInitialEdgeData(nodeList, problemFK)
        

    def createInitialData(self):
        if self.problemId == -1:
            p = Problem(graph=json.dumps(problemGraphDefault), dateAdded=datetime.now())
            p.save()
            self.problemId = p.id
            self.createInitialNodeData(p)

    @XBlock.json_handler
    def generate_problem_id(self,data,suffix=''):
        if self.problemId == -1:
            created = True
        else:
            created = False
        self.createInitialData()
        if created:
            return {'result':'created'}
        else:
            return {'result':'exists'}

    @XBlock.json_handler
    @transaction.atomic
    def submit_data(self,data,suffix=''):
        loadedProblem = Problem.objects.select_for_update().get(id=self.problemId)

        self.problemTitle = data.get('problemTitle')
        self.problemDescription = data.get('problemDescription')
        loadedProblem.multipleChoiceProblem = data.get('multipleChoiceProblem')
        self.problemDefaultHint = data.get('problemDefaultHint')
        self.problemDefaultHintEnglish = data.get('problemDefaultHintEnglish')
        self.problemInitialHint = data.get('problemInitialHint')
        self.problemInitialHintEnglish = data.get('problemInitialHintEnglish')
        self.problemAnswer1 = data.get('problemAnswer1')
        self.problemAnswer2 = data.get('problemAnswer2')
        self.problemAnswer3 = data.get('problemAnswer3')
        self.problemAnswer4 = data.get('problemAnswer4')
        self.problemAnswer5 = data.get('problemAnswer5')
        self.problemCorrectAnswer = data.get('problemCorrectAnswer')
        self.problemSubject = data.get('problemSubject')
        self.callOpenAiExplanation = data.get('callOpenAiExplanation')
        self.questionToAsk = data.get('questionToAsk')
        self.openApiToken = data.get('openApiToken')
        self.language = data.get('language')
        self.problemTags = ast.literal_eval(data.get('problemTags'))
        loadedProblem.dateModified=datetime.now()

        loadedProblem.save()

        return {'result':'success'}

    @XBlock.json_handler
    @transaction.atomic
    def recommend_feedback(self,data,suffix=''):
        loadedProblem = Problem.objects.get(id=self.problemId)
        if data.get("existingType") == "hint":
            loadedHint = Hint.objects.select_for_update().get(problem = loadedProblem, id=data.get("existingHintId"))

            if data.get("message") == yesUniversalAnswer:
                loadedHint.usefulness += receivedHintUsefulnessAmount
            elif data.get("message") == noUniversalAnswer:
                loadedHint.usefulness -= receivedHintUsefulnessAmount
        
            loadedHint.save()
        elif data.get("existingType") == "explanation":
            loadedExplanation = Explanation.objects.select_for_update().get(problem = loadedProblem, id=data.get("existingHintId"))

            if data.get("message") == yesUniversalAnswer:
                loadedExplanation.usefulness += receivedHintUsefulnessAmount
            elif data.get("message") == noUniversalAnswer:
                loadedExplanation.usefulness -= receivedHintUsefulnessAmount
        
            loadedExplanation.save()
        elif data.get("existingType") == "errorSpecificFeedback":
            loadedSpecificFeedback = ErrorSpecificFeedbacks.objects.select_for_update().get(problem = loadedProblem, id=data.get("existingHintId"))

            if data.get("message") == yesUniversalAnswer:
                loadedSpecificFeedback.usefulness += receivedHintUsefulnessAmount
            elif data.get("message") == noUniversalAnswer:
                loadedSpecificFeedback.usefulness -= receivedHintUsefulnessAmount
        
            loadedSpecificFeedback.save()

        return {'result':'success'}

    @XBlock.json_handler
    @transaction.atomic
    def send_feedback(self,data,suffix=''):
        loadedProblem = Problem.objects.get(id=self.problemId)
        
        feedbackType = data.get("type")
        if feedbackType == "minimalState":
            loadedNode = Node.objects.select_for_update().get(problem=loadedProblem, title=transformToSimplerAnswer(data.get("node")))
        elif feedbackType == 'errorSpecific' or feedbackType == 'explanation' or feedbackType == 'hint' or feedbackType == 'knowledgeComponent':
            loadedEdge = Edge.objects.get(problem=loadedProblem, sourceNode__title=transformToSimplerAnswer(data.get("nodeFrom")), destNode__title=transformToSimplerAnswer(data.get("nodeTo")))
        elif feedbackType == 'minimalStep':
            loadedEdge = Edge.objects.select_for_update().get(problem=loadedProblem, sourceNode__title=transformToSimplerAnswer(data.get("nodeFrom")), destNode__title=transformToSimplerAnswer(data.get("nodeTo")))
        elif feedbackType == 'knowledgeComponent':
            loadedNode = Node.objects.select_for_update().get(problem=loadedProblem, title=transformToSimplerAnswer(data.get("nodeFrom")))

        if feedbackType == 'minimalStep':

            possibleEdgeVotes = Edge_votes.objects.select_for_update().filter(problem=loadedProblem, edge=loadedEdge)
            if possibleEdgeVotes.exists():
                loadedEdgeVotes = possibleEdgeVotes.first()
                loadedEdgeVotes.dateModified = datetime.now()
                loadedEdgeVotes.lastStudentId = self.studentId
            else:
                loadedEdgeVotes = Edge_votes(problem=loadedProblem, edge=loadedEdge, dateAdded = datetime.now(), lastStudentId=self.studentId)

            if data.get("message") == yesUniversalAnswer:
                loadedEdgeVotes.positiveCounter += 1
            elif data.get("message") == noUniversalAnswer:
                loadedEdgeVotes.negativeCounter += 1

            loadedEdgeVotes.save()

            if loadedEdgeVotes.positiveCounter >= maxVotesToFixCorrectness:
                loadedEdge.correctness = 1
                loadedEdge.fixedValue = 1
                loadedEdge.save()
            elif loadedEdgeVotes.negativeCounter >= maxVotesToFixCorrectness:
                loadedEdge.correctness = -1
                loadedEdge.fixedValue = 1
                loadedEdge.save()

        elif feedbackType == 'minimalState':
            possibleNodeVotes = Node_votes.objects.select_for_update().filter(problem=loadedProblem, node=loadedNode)
            if possibleNodeVotes.exists():
                loadedNodeVotes = possibleNodeVotes.first()
                loadedNodeVotes.dateModified = datetime.now()
                loadedNodeVotes.lastStudentId = self.studentId
            else:
                loadedNodeVotes = Node_votes(problem=loadedProblem, node=loadedNode, dateAdded = datetime.now(), lastStudentId=self.studentId)

            if data.get("message") == yesUniversalAnswer:
                loadedNodeVotes.positiveCounter += 1
            elif data.get("message") == noUniversalAnswer:
                loadedNodeVotes.negativeCounter += 1

            loadedNodeVotes.save()

            if loadedNodeVotes.positiveCounter >= maxVotesToFixCorrectness:
                loadedNode.correctness = 1
                loadedNode.fixedValue = 1
                possibleEdge = Edge.objects.filter(problem = loadedProblem, sourceNode = loadedNode, destNode__title = "_end_")
                if possibleEdge.exists():
                    loadedNode.linkedSolution = self.problemCorrectAnswer
                loadedNode.save()
            elif loadedNodeVotes.negativeCounter >= maxVotesToFixCorrectness:
                loadedNode.correctness = -1
                loadedNode.fixedValue = 1
                loadedNode.save()

        elif feedbackType == 'errorSpecific':
            errorSpecificFeedback = ErrorSpecificFeedbacks(problem=loadedProblem, edge=loadedEdge)
            errorSpecificFeedback.text=data.get("message")
            errorSpecificFeedback.dateAdded = datetime.now()
            errorSpecificFeedback.studentId = self.studentId
            errorSpecificFeedback.priority = 100
            errorSpecificFeedback.usefulness = 0
            errorSpecificFeedback.save()
        elif feedbackType == 'knowledgeComponent':
            knowledgeComponent = KnowledgeComponent(problem=loadedProblem, edge=loadedEdge, node=loadedNode)
            knowledgeComponent.text=data.get("message")
            knowledgeComponent.dateAdded = datetime.now()
            knowledgeComponent.studentId = self.studentId
            knowledgeComponent.priority = 100
            knowledgeComponent.usefulness = 0
            knowledgeComponent.save()
        elif feedbackType == 'explanation':
            explanation = Explanation(problem=loadedProblem, edge=loadedEdge)
            explanation.text=data.get("message")
            explanation.dateAdded = datetime.now()
            explanation.studentId = self.studentId
            explanation.priority = 100
            explanation.usefulness = 0
            explanation.save()
        elif feedbackType == 'hint':
            hint = Hint(problem=loadedProblem, edge=loadedEdge)
            hint.text=data.get("message")
            hint.dateAdded = datetime.now()
            hint.studentId = self.studentId
            hint.priority = 100
            hint.usefulness = 0
            hint.save()
        elif feedbackType == 'doubtAnswer':
            loadedDoubt = Doubt.objects.get(problem=loadedProblem, id=data.get("doubtId"))
            answer = Answer(problem=loadedProblem, doubt=loadedDoubt)
            answer.dateAdded = datetime.now()
            answer.studentId = self.studentId
            answer.text = data.get("message")
            answer.usefulness = 0
            answer.save()
            loadedDoubt.dateModified = datetime.now()
            loadedDoubt.save()
        elif feedbackType == 'doubtStep' or feedbackType == 'doubtState':
            doubt = Doubt(problem=loadedProblem)
            step = Edge.objects.filter(problem=loadedProblem, sourceNode__title = transformToSimplerAnswer(data.get("nodeFrom")), destNode__title = transformToSimplerAnswer(data.get("nodeTo")))
            if step.exists():
                doubt.edge = step[0]
                doubt.node = step[0].destNode
            else:
                fromState = Node.objects.select_for_update().filter(problem=loadedProblem, title = transformToSimplerAnswer(data.get("nodeFrom")))
                if fromState.exists():
                    newSourceNode = fromState[0]    
                else:
                    newSourceNode = Node(problem=loadedProblem, title = data.get("nodeFrom"), dateAdded = datetime.now())
                    newSourceNode.save()
                    newSourceNode = Node.objects.get(problem=loadedProblem, title = transformToSimplerAnswer(data.get("nodeFrom")))
                
                toState = Node.objects.select_for_update().filter(problem=loadedProblem, title = transformToSimplerAnswer(data.get("nodeTo")))
                if toState.exists():
                    newDestNode = toState[0]    
                    doubt.node = newDestNode
                else:
                    newDestNode = Node(problem=loadedProblem, title = data.get("nodeTo"), dateAdded = datetime.now())
                    newDestNode.save()
                    newDestNode = Node.objects.get(problem=loadedProblem, title = transformToSimplerAnswer(data.get("nodeTo")))
                    doubt.node = newDestNode

                newStep = Edge(problem=loadedProblem, sourceNode = newSourceNode, destNode = newDestNode, dateAdded = datetime.now())
                newStep.save()
                doubt.edge = newStep
            
            if feedbackType == 'doubtStep':
                doubt.type = 1
                doubt.node = None
            else:
                doubt.type = 0
                doubt.edge = None

            doubt.text=data.get("message")
            doubt.dateAdded = datetime.now()
            doubt.studentId = self.studentId

            doubt.save()

            return {'result':'success', 'doubtId': doubt.id}

        return {'result':'success'}

    #Sistema que mostra quais dicas até o primeiro passo errado
    #Aqui ele pega a primeira resposta errada, e coloca a dica da que mais se assemelha
    #Feedback mínimo, sem dicas
    def getFirstIncorrectAnswer (self, answerArray):

        beforeLast = None
        lastElement = "_start_"
        wrongElement = None
        wrongStep = 0

        loadedProblem = Problem.objects.get(id=self.problemId)
        #Ver até onde está certo
        for step in answerArray:
            lastNode = Node.objects.get(problem=loadedProblem, title=transformToSimplerAnswer(lastElement))
            currentNode = Node.objects.filter(problem=loadedProblem, title=transformToSimplerAnswer(step), visible = 1)

            edge = Edge.objects.filter(problem=loadedProblem, sourceNode = lastNode, destNode=currentNode.first(), visible = 1)
            if currentNode.exists() and edge.exists() and edge.first().correctness >= stronglyValidStep[0]  and currentNode.first().correctness >= correctState[0]:
                beforeLast = lastElement
                lastElement = step
                wrongStep = wrongStep + 1
            else:
                wrongElement = step
                break

        #Se null, então tudo certo
        if (wrongElement == None):
            return {"wrongElement": wrongElement, "lastCorrectElement": lastElement, "correctElementLine": wrongStep, "beforeLast": beforeLast}

        availableCorrectSteps = []
        lastNode = Node.objects.get(problem=loadedProblem, title=transformToSimplerAnswer(lastElement))
        nextElements = Edge.objects.filter(problem=loadedProblem, sourceNode = lastNode)
        for element in nextElements:
            if element.destNode.correctness >= correctState[0]:
                availableCorrectSteps.append(element.destNode.title)
        return {"wrongElement": wrongElement, "availableCorrectSteps": availableCorrectSteps, "wrongElementLine": wrongStep, "lastCorrectElement": lastElement}



    @XBlock.json_handler
    def generate_graph(self, data, suffix=''):
        return {"teste": getJsonFromProblemGraph(self.problemId, self.problemDescription), "lang": self.language}

    #COMO MOSTRAR SE UMA REPSOSTAS ESTÁ CORRETA?
    #TALVEZ COLOCAR ALGUMA COISA NOA TELA QUE MOSTRE QUE A LINHA ESTÁ CORRETA
    #Sistema que mostra a dica até o primeiro passo que estiver errado
    #Mostra um next-Step hint, mas desse passo que está errado (como colocar ele certo)
    #Rodar após cada enter? Faria sentido

    @XBlock.json_handler
    def check_if_use_ai_explanation(self, data, suffix=''):
        return {"callOpenAiExplanation": self.callOpenAiExplanation}

    @XBlock.json_handler
    def return_full_explanation(self, data, suffix=''):
        return {"explanation": generate_full_explanation(self.openApiToken, self.questionToAsk)}

    @XBlock.json_handler
    def generate_answers(self, data, suffix=''):
        if "node" in data:
            element = data.get("node")
        else:
            element = data.get("from") + " - " + data.get("to")

        return {"answer": answer_doubt(self.openApiToken, data.get("text"), element)}

    @XBlock.json_handler
    def generate_error_specific_feedback(self, data, suffix=''):
        return {"feedback": generate_error_specific_feedback(self.openApiToken, data.get("from"), data.get("to"))}

    @XBlock.json_handler
    def generate_explanation(self, data, suffix=''):
        return {"feedback": generate_explanation(self.openApiToken, data.get("from"), data.get("to"))}

    @XBlock.json_handler
    def generate_hint(self, data, suffix=''):
        return {"feedback": generate_hint(self.openApiToken, data.get("from"), data.get("to"))}

    @XBlock.json_handler
    @transaction.atomic
    def get_hint_for_last_step(self, data, suffix=''):

        answerArray = data['userAnswer'].split('\n')

        if '' in answerArray:
            answerArray =  list(filter(lambda value: value != '', answerArray))
        

        possibleIncorrectAnswer = self.getFirstIncorrectAnswer(answerArray)
        
        wrongElement = possibleIncorrectAnswer.get("wrongElement")
        lastCorrectElement = possibleIncorrectAnswer.get("lastCorrectElement")

        if self.language == "pt":
            hintText = self.problemDefaultHint
        else:
            hintText = self.problemDefaultHintEnglish

        hintId = 0
        hintList = None

        loadedProblem = Problem.objects.get(id=self.problemId)

        minValue = float('inf')
        nextCorrectStep = None
        nextPossibleCorrectSteps = []
        if  (wrongElement != None):
            possibleSteps = possibleIncorrectAnswer.get("availableCorrectSteps")
            for step in possibleSteps:
                actualValue = distance(wrongElement, step)
                nextPossibleCorrectSteps.append(step)
                if(actualValue < minValue):
                    minValue = actualValue
                    nextCorrectStep = step

            hintList = []
            hintIdList = []
            hintIdType = []


            possibleState = Node.objects.select_for_update().filter(problem=loadedProblem, title=transformToSimplerAnswer(wrongElement))
            if not possibleState.exists():
                newNode = Node(title=transformToSimplerAnswer(wrongElement), problem=loadedProblem, dateAdded=datetime.now())
                newNode.save()
            else:
                newNode = possibleState.first()
                if newNode.visible == 0:
                    newNode.visible = 1
                    newNode.save()

            possibleStep = Edge.objects.select_for_update().filter(problem=loadedProblem, sourceNode__title = transformToSimplerAnswer(lastCorrectElement), destNode=newNode)
            if not possibleStep.exists():
                possibleLastState = Node.objects.select_for_update().filter(problem=loadedProblem, title=transformToSimplerAnswer(lastCorrectElement))
                if not possibleLastState.exists():
                    lastState = Node(problem=loadedProblem, title=transformToSimplerAnswer(lastCorrectElement), dateAdded=datetime.now())
                    lastState.save()
                else:
                    lastState = possibleLastState.first()
                    if lastState.visible == 0:
                        lastState.visible = 1
                        lastState.save()

                if lastState.title == '_start_' or newNode.title == '_end_':
                    newEdge = Edge(problem=loadedProblem, sourceNode=lastState, destNode=newNode, dateAdded=datetime.now(), correctness = 1, fixedValue = 1)
                else:
                    newEdge = Edge(problem=loadedProblem, sourceNode=lastState, destNode=newNode, dateAdded=datetime.now())
                newEdge.save()
            else:
                newEdge = possibleStep.first()
                if newEdge.visible == 0:
                    newEdge.visible = 1
                    newEdge.save()

            edgeForSpecificFeedback = Edge.objects.filter(problem=loadedProblem, sourceNode__title=transformToSimplerAnswer(possibleIncorrectAnswer.get("lastCorrectElement")), destNode__title=transformToSimplerAnswer(wrongElement))
            if edgeForSpecificFeedback.exists():
                specificFeedbackForStep = ErrorSpecificFeedbacks.objects.filter(problem=loadedProblem, edge=edgeForSpecificFeedback.first()).order_by("-usefulness", "priority")

                if specificFeedbackForStep.exists():
                    for specificFeedback in specificFeedbackForStep:
                        hintList.append(specificFeedback.text)
                        hintIdList.append(specificFeedback.id)
                        hintIdType.append("errorSpecificFeedback")


            hintFound = False
            if nextCorrectStep is not None and possibleIncorrectAnswer.get("lastCorrectElement") is not None:
                edgeForStep = Edge.objects.filter(problem=loadedProblem, sourceNode__title=transformToSimplerAnswer(possibleIncorrectAnswer.get("lastCorrectElement")), destNode__title=transformToSimplerAnswer(nextCorrectStep))
                if edgeForStep.exists():
                    hintForStep = Hint.objects.filter(problem=loadedProblem, edge=edgeForStep.first()).order_by("-usefulness", "priority")
                    if hintForStep.exists():
                        hintFound = True
                        for hint in hintForStep:
                            hintList.append(hint.text)
                            hintIdList.append(hint.id)
                            hintIdType.append("hint")
            if not hintFound:
                for hintPossibleStep in nextPossibleCorrectSteps:
                    edgeForStep = Edge.objects.filter(problem=loadedProblem, sourceNode__title=transformToSimplerAnswer(possibleIncorrectAnswer.get("lastCorrectElement")), destNode__title=transformToSimplerAnswer(hintPossibleStep))
                    if edgeForStep.exists() and not hintFound:
                        hintForStep = Hint.objects.filter(problem=loadedProblem, edge=edgeForStep.first()).order_by("-usefulness", "priority")
                        if hintForStep.exists():
                            hintFound = True
                            nextCorrectStep = hintPossibleStep
                            for hint in hintForStep:
                                hintList.append(hint.text)
                                hintIdList.append(hint.id)
                                hintIdType.append("hint")

                if not hintFound:
                    if possibleIncorrectAnswer.get("lastCorrectElement") == "_start_":
                        if self.language == "pt":
                            hintList.append(self.problemInitialHint)
                        else:
                            hintList.append(self.problemInitialHintEnglish)
                        hintIdList.append(0)
                        hintIdType.append("hint")
                    else:
                        if self.language == "pt":
                            hintList.append(self.problemDefaultHint)
                        else:
                            hintList.append(self.problemDefaultHintEnglish)
                        hintIdList.append(0)
                        hintIdType.append("hint")

        try:
            #Então está tudo certo, pode dar um OK e seguir em frente
            #MO passo está correto, mas agora é momento de mostrar a dica para o próximo passo.

            self.generateAttempt(answerArray)
            
            lastHint = False
            if (wrongElement == None):
                loadedProblem = Problem.objects.get(id=self.problemId)
                nextPossibleElementsEdges = Edge.objects.filter(problem=loadedProblem, sourceNode__title=transformToSimplerAnswer(possibleIncorrectAnswer.get("lastCorrectElement")))

                nextElement = None
                nextPossibleCorrectElementsEdges = []
                for edge in nextPossibleElementsEdges:
                    element = edge.destNode.title
                    loadedProblem = Problem.objects.get(id=self.problemId)
                    nodeElement = Node.objects.get(problem=loadedProblem, title=transformToSimplerAnswer(element))
                    if nodeElement.correctness >= correctState[0] and edge.correctness >= stronglyValidStep[0]:
                        nextElement = element
                        nextPossibleCorrectElementsEdges.append(element)

                hintList = []
                hintIdList = []
                hintIdType = []

                if possibleIncorrectAnswer.get("beforeLast") is not None:
                    beforeEdgeForStep = Edge.objects.filter(problem=loadedProblem, sourceNode__title=transformToSimplerAnswer(possibleIncorrectAnswer.get("beforeLast")), destNode__title=transformToSimplerAnswer(possibleIncorrectAnswer.get("lastCorrectElement")))

                    if beforeEdgeForStep is not None and beforeEdgeForStep.exists():
                        explanationForStep = Explanation.objects.filter(problem=loadedProblem, edge=beforeEdgeForStep.first()).order_by("-usefulness", "priority")

                        if explanationForStep.exists():
                            for explanation in explanationForStep:
                                hintList.append(explanation.text)
                                hintIdList.append(explanation.id)
                                hintIdType.append("explanation")


                if (nextElement != "_end_"):
                    hintFound = False

                    edgeForStep = Edge.objects.filter(problem=loadedProblem, sourceNode__title=transformToSimplerAnswer(possibleIncorrectAnswer.get("lastCorrectElement")), destNode__title=transformToSimplerAnswer(nextElement))
                    if edgeForStep.exists():
                        hintForStep = Hint.objects.filter(problem=loadedProblem, edge=edgeForStep.first()).order_by("-usefulness", "priority")
                        if hintForStep.exists():
                            hintFound = True
                            for hint in hintForStep:
                                hintList.append(hint.text)
                                hintIdList.append(hint.id)
                                hintIdType.append("hint")
                    
                    if not hintFound:
                        for nextPossibleNode in nextPossibleCorrectElementsEdges:
                            edgeForStep = Edge.objects.filter(problem=loadedProblem, sourceNode__title=transformToSimplerAnswer(possibleIncorrectAnswer.get("lastCorrectElement")), destNode__title=transformToSimplerAnswer(nextPossibleNode))
                            if edgeForStep.exists() and not hintFound:
                                hintForStep = Hint.objects.filter(problem=loadedProblem, edge=edgeForStep.first()).order_by("-usefulness", "priority")
                                if hintForStep.exists():
                                    nextElement = nextPossibleNode
                                    hintFound = True
                                    for hint in hintForStep:
                                        hintList.append(hint.text)
                                        hintIdList.append(hint.id)
                                        hintIdType.append("hint")
                    
                        if not hintFound:
                            if self.language == "pt":
                                hintList.append(self.problemDefaultHint)
                            else:
                                hintList.append(self.problemDefaultHintEnglish)
                            hintIdList.append(0)
                            hintIdType.append("hint")

                else:
                    if self.language == "pt":
                        hintList.append(self.problemDefaultHint)
                    else:
                        hintList.append(self.problemDefaultHintEnglish)
                    hintIdList.append(0)
                    hintIdType.append("hint")

                wrongStepCount = possibleIncorrectAnswer.get("correctElementLine")

                newHints = self.checkIfCurrentHintsAreSame(hintList)

                #Para casos é a primeira dica
            
                if (wrongStepCount == 0):
                    if self.language == "pt":
                        hintText = self.problemInitialHint
                        self.currentHints = [self.problemInitialHint]
                    else:
                        hintText = self.problemInitialHintEnglish
                        self.currentHints = [self.problemInitialHintEnglish]
                    hintId = 0
                    hintType = "hint"
                    typeChose = 1
                #Para casos onde está tudo correto, então ele verifica se o último elemento são os corretos
                elif (newHints):
                    self.lastWrongElement = str((possibleIncorrectAnswer.get("beforeLast"), possibleIncorrectAnswer.get("lastCorrectElement")))
                    self.lastWrongElementCount = 1
                    hintText = hintList[0]
                    hintId = hintIdList[0]
                    hintType = hintIdType[0]
                    self.currentHints = hintList
                    typeChose = 2
                #Caso básico, vai passando para o próximo
                elif (self.lastWrongElementCount < len(hintList)):
                    hintText = hintList[self.lastWrongElementCount]
                    hintId = hintIdList[self.lastWrongElementCount]
                    hintType = hintIdType[self.lastWrongElementCount]
                    self.lastWrongElementCount = self.lastWrongElementCount + 1
                    self.currentHints = hintList
                    if (self.lastWrongElementCount == len(hintList)):
                        lastHint = True
                    typeChose = 4
                #Caso onde ele pega a última dica da lista
                else:
                    lastHint = True
                    hintText = hintList[-1]
                    hintId = hintIdList[-1]
                    hintType = hintIdType[-1]
                    self.currentHints = hintList
                    typeChose = 5

                if hintId != 0:
                    self.increaseFeedbackCount(loadedProblem, hintType, hintId)

                self.saveStatesAndSteps(answerArray)
                return {"status": "OK", "hint": hintText, "hintId": hintId, "hintType": hintType, "lastCorrectElement": possibleIncorrectAnswer.get("lastCorrectElement"), "lastHint": lastHint, "debug1": possibleIncorrectAnswer, "debug2": self.lastWrongElement, "debug3": typeChose}
            else:
                newHints = self.checkIfCurrentHintsAreSame(hintList)

                if (newHints):
                    self.lastWrongElement = str((possibleIncorrectAnswer.get("lastCorrectElement"), nextCorrectStep))
                    self.lastWrongElementCount = 1
                    hintText = hintList[0]
                    hintId = hintIdList[0]
                    hintType = hintIdType[0]
                    self.currentHints = hintList
                elif (self.lastWrongElementCount < len(hintList)):
                    hintText = hintList[self.lastWrongElementCount]
                    hintId = hintIdList[self.lastWrongElementCount]
                    hintType = hintIdType[self.lastWrongElementCount]
                    self.lastWrongElementCount = self.lastWrongElementCount + 1
                    self.currentHints = hintList
                    if (self.lastWrongElementCount == len(hintList)):
                        lastHint = True
                else:
                    lastHint = True
                    hintText = hintList[-1]
                    hintId = hintIdList[-1]
                    hintType = hintIdType[-1]
                    self.currentHints = hintList

                if hintId != 0:
                    self.increaseFeedbackCount(loadedProblem, hintType, hintId)

        except IndexError as error:
            if self.language == "pt":
                hintText = self.problemDefaultHint
            else:
                hintText = self.problemDefaultHintEnglish
            hintId = 0
            hintType = "hint"
            raise

        self.saveStatesAndSteps(answerArray)
        return {"status": "NOK", "hint": hintText, "wrongElement": wrongElement, "hintId": hintId, "hintType": hintType, "lastHint": lastHint, "wrongElementCorrectness": newNode.correctness}

    @XBlock.json_handler
    def increase_feedback_count(self, data, suffix=''):
        loadedProblem = Problem.objects.get(id=self.problemId)
        self.increaseFeedbackCount(loadedProblem, data.get("type"), data.get("id"))
        return {"status": "OK"}

    @transaction.atomic
    def increaseFeedbackCount(self, loadedProblem, type, id):
        if type == "hint":
            hint = Hint.objects.select_for_update().get(problem = loadedProblem, id = id)
            if hint.id not in self.viewedHints:
                hint.counter += 1
                hint.dateModified = datetime.now()
                hint.save()
                self.viewedHints.append(hint.id)
        elif type == "explanation":
            explanation = Explanation.objects.select_for_update().get(problem = loadedProblem, id = id)
            if explanation.id not in self.viewedExplanations:
                explanation.counter += 1
                explanation.dateModified = datetime.now()
                explanation.save()
                self.viewedExplanations.append(explanation.id)
        elif type == "errorSpecificFeedback":
            errorSpecific = ErrorSpecificFeedbacks.objects.select_for_update().get(problem = loadedProblem, id = id)
            if errorSpecific.id not in self.viewedErrorSpecific:
                errorSpecific.counter += 1
                errorSpecific.dateModified = datetime.now()
                errorSpecific.save()
                self.viewedErrorSpecific.append(errorSpecific.id)
        elif type == "doubt":
            doubt = Doubt.objects.select_for_update().get(problem = loadedProblem, id = id)
            if doubt.id not in self.viewedDoubts:
                doubt.counter += 1
                doubt.dateModified = datetime.now()
                doubt.save()
                self.viewedDoubts.append(doubt.id)
        elif type == "answer":
            answer = Answer.objects.select_for_update().get(problem = loadedProblem, id = id)
            if answer.id not in self.viewedAnswers:
                answer.counter += 1
                answer.dateModified = datetime.now()
                answer.save()
                self.viewedAnswers.append(answer.id)

    
    def saveCurrentHints (self, data):
        self.currentHints = []
        for hint in data:
            self.currentHints.append(hint)

    def checkIfCurrentHintsAreSame (self, hintList):
        newHints = False
        if len(self.currentHints) != len(hintList):
            newHints = True
        else:
            for i in range(0, len(hintList)):
                if self.currentHints[i] != hintList[i]:
                  newHints = True
        return newHints

    @XBlock.json_handler
    def generate_report(self, data, suffix=''):
        loadedProblem = Problem.objects.get(id=self.problemId)
        incorrectSortedNodes = Node.objects.filter(problem=loadedProblem, correctness__lte = incorrectState[1]).exclude(title = "_start_").exclude(title = "_end_").order_by("-usageCount")[:5]
        incorrectSortedEdges = Edge.objects.filter(problem=loadedProblem, correctness__lt = possiblyInvalidStep[0]).exclude(sourceNode__title = "_start_").exclude(destNode__title = "_end_").order_by("-usageCount")[:5]

        correctSortedNodes = Node.objects.filter(problem=loadedProblem, correctness__gte = correctState[0]).exclude(title = "_start_").exclude(title = "_end_").order_by("-usageCount")[:5]
        correctSortedEdges = Edge.objects.filter(problem=loadedProblem, correctness__gte = validStep[0]).exclude(sourceNode__title = "_start_").exclude(destNode__title = "_end_").order_by("-usageCount")[:5]

        errorSpecificFeedbacks = ErrorSpecificFeedbacks.objects.filter(problem=loadedProblem).order_by("-usefulness", "priority")[:5]
        hints = Hint.objects.filter(problem=loadedProblem).order_by("-usefulness", "priority")[:5]
        explanations = Explanation.objects.filter(problem=loadedProblem).order_by("-usefulness", "priority")[:5]

        doubts = Doubt.objects.filter(problem=loadedProblem).order_by("dateAdded")[:5]


        incorrectSortedNodesJson = []
        incorrectSortedEdgesJson = []

        correctSortedNodesJson = []
        correctSortedEdgesJson = []

        errorSpecificFeedbacksJson = []
        hintJsons = []
        explanationsJson = []

        doubtsJson = []


        for node in incorrectSortedNodes:
            incorrectSortedNodesJson.append({"title": node.title, "counter": node.counter})

        for edge in incorrectSortedEdges:
            incorrectSortedEdgesJson.append({"source": edge.sourceNode.title, "dest": edge.destNode.title, "counter": edge.counter})

        for node in correctSortedNodes:
            correctSortedNodesJson.append({"title": node.title, "counter": node.counter})

        for edge in correctSortedEdges:
            correctSortedEdgesJson.append({"source": edge.sourceNode.title, "dest": edge.destNode.title, "counter": edge.counter})

        for errorSpecificFeedback in errorSpecificFeedbacks:
            if errorSpecificFeedback.edge is not None:
                errorSpecificFeedbacksJson.append({"source": errorSpecificFeedback.edge.sourceNode.title, "dest": errorSpecificFeedback.edge.destNode.title, "text": errorSpecificFeedback.text, "priority": errorSpecificFeedback.priority, "usefulness": errorSpecificFeedback.usefulness})
            
        for hint in hints:
            if hint.edge is not None:
                hintJsons.append({"source": hint.edge.sourceNode.title, "dest": hint.edge.destNode.title, "text": hint.text, "priority": hint.priority, "usefulness": hint.usefulness})

        for explanation in explanations:
            if explanation.edge is not None:
                explanationsJson.append({"source": explanation.edge.sourceNode.title, "dest": explanation.edge.destNode.title, "text": explanation.text, "priority": explanation.priority, "usefulness": explanation.usefulness})

        for doubt in doubts:
            answersJson = []
            if (doubt.type == 1 and doubt.edge is not None):
                answers = Answer.objects.filter(problem=loadedProblem, doubt=doubt).order_by("-usefulness")[:5]
                if answers.exists():
                    for answer in answers:
                        answersJson.append({"text": answer.text, "usefulness": answer.usefulness})
                doubtsJson.append({"source": doubt.edge.sourceNode.title, "dest": doubt.edge.destNode.title, "text": doubt.text, "answers": answersJson})
            elif (doubt.type == 0 and doubt.node is not None):
                answers = Answer.objects.filter(problem=loadedProblem, doubt=doubt).order_by("-usefulness")[:5]
                if answers.exists():
                    for answer in answers:
                        answersJson.append({"text": answer.text, "usefulness": answer.usefulness})
                doubtsJson.append({"node": doubt.node.title, "text": doubt.text})


        return {"incorrectNodes": incorrectSortedNodesJson, "incorrectEdges": incorrectSortedEdgesJson, "correctNodes": correctSortedNodesJson, "correctEdges": correctSortedEdgesJson, "errorSpecificFeedbacks": errorSpecificFeedbacksJson, "hints": hintJsons, "explanations": explanationsJson, "doubts": doubtsJson}

    @XBlock.json_handler
    def generate_report2(self, data, suffix=''):
        loadedProblem = Problem.objects.get(id=self.problemId)
        startNode = Node.objects.filter(problem=loadedProblem, title = '_start_')
        allSolutions = self.calculateCompletness2(loadedProblem, startNode.first(), [startNode.first().id], [])
        return {"nodes": json.dumps(list(allSolutions["nodes"])), "edges": json.dumps(list(allSolutions["edges"])), "allSums": json.dumps(list(allSolutions["allSums"])), "count": len(allSolutions["allSums"]), "allSumsOnlyCorrect": json.dumps(list(allSolutions["allSumsOnlyCorrect"]))}



    @XBlock.json_handler
    def export_data(self, data, suffix=''):
        loadedProblem = Problem.objects.get(id=self.problemId)
        startNode = Node.objects.get(problem=loadedProblem, title="_start_")
        endNode = Node.objects.get(problem=loadedProblem, title="_end_")

        allNodes = Node.objects.filter(problem=loadedProblem).exclude(title = "_start_").exclude(title = "_end_").exclude(visible = 0)
        allEdges = Edge.objects.filter(problem=loadedProblem).exclude(sourceNode__title = "_start_").exclude(destNode__title = "_end_").exclude(visible = 0)

        returnjson = {}
        allNodesJson = []
        allEdgesJson = []

        returnjson["problemTitle"] = self.problemTitle
        returnjson["problemDescription"] = self.problemDescription
        returnjson["multipleChoiceProblem"] = loadedProblem.multipleChoiceProblem
        returnjson["problemDefaultHint"] = self.problemDefaultHint
        returnjson["problemDefaultHintEnglish"] = self.problemDefaultHintEnglish
        returnjson["problemInitialHint"] = self.problemInitialHint
        returnjson["problemInitialHintEnglish"] = self.problemInitialHintEnglish
        returnjson["problemAnswer1"] = self.problemAnswer1
        returnjson["problemAnswer2"] = self.problemAnswer2
        returnjson["problemAnswer3"] = self.problemAnswer3
        returnjson["problemAnswer4"] = self.problemAnswer4
        returnjson["problemAnswer5"] = self.problemAnswer5
        returnjson["problemCorrectAnswer"] = self.problemCorrectAnswer
        returnjson["problemSubject"] = self.problemSubject
        returnjson["callOpenAiExplanation"] = self.callOpenAiExplanation
        returnjson["questionToAsk"] = self.questionToAsk
        returnjson["openApiToken"] = self.openApiToken
        returnjson["problemTags"] = str(self.problemTags)

        for node in allNodes:
            nodeJson = {}
            nodeDoubtJson = []

            possibleInitial = Edge.objects.filter(problem=loadedProblem, sourceNode = startNode, destNode = node)
            possibleEnd = Edge.objects.filter(problem=loadedProblem, sourceNode = node, destNode = endNode)
            
            nodeJson["title"] = node.title
            nodeJson["counter"] = node.counter
            nodeJson["correctness"] = node.correctness
            nodeJson["fixedValue"] = node.fixedValue
            nodeJson["nodePositionX"] = node.nodePositionX
            nodeJson["nodePositionY"] = node.nodePositionY
            nodeJson["alreadyCalculatedPos"] = node.alreadyCalculatedPos
            nodeJson["customPos"] = node.customPos
            nodeJson["linkedSolution"] = node.linkedSolution

            if possibleInitial.exists() and possibleEnd.exists():
                nodeJson["type"] = "multiple"
            elif possibleInitial.exists():
                nodeJson["type"] = "initial"
            elif possibleEnd.exists():
                nodeJson["type"] = "final"
            else:
                nodeJson["type"] = "normal"

            if node.linkedSolution is not None:
                nodeJson["linkedSolution"] = node.linkedSolution

            nodeDoubts = Doubt.objects.filter(problem=loadedProblem, node = node)
            if nodeDoubts.exists():
                for nodeDoubt in nodeDoubts:
                    doubtJson = {}
                    answersJson = []

                    doubtJson["text"] = nodeDoubt.text
                    nodeDoubtAnswers = Answer.objects.filter(problem=loadedProblem, doubt = nodeDoubt)
                    if nodeDoubtAnswers.exists():
                        for nodeDoubtAnswer in nodeDoubtAnswers:
                            answerJsonInner = {}
                            answerJsonInner["text"] = nodeDoubtAnswer.text
                            answerJsonInner["usefulness"] = nodeDoubtAnswer.usefulness
                            answersJson.append(answerJsonInner)
                    
                    if answersJson:
                        doubtJson["answers"] = answersJson

                    nodeDoubtJson.append(doubtJson)
                    
            if nodeDoubtJson:
                nodeJson["doubts"] = nodeDoubtJson
            
            allNodesJson.append(nodeJson)

        returnjson["nodes"] = allNodesJson
        
        for edge in allEdges:
            edgeJson = {}
            edgeHintJson = []
            edgeExplanationJson = []
            edgeDoubtJson = []
            edgeErrorSpecificFeedbackJson = []

            edgeJson["from"] = edge.sourceNode.title
            edgeJson["to"] = edge.destNode.title
            edgeJson["counter"] = edge.counter
            edgeJson["correctness"] = edge.correctness
            edgeJson["fixedValue"] = edge.fixedValue

            edgeHints = Hint.objects.filter(problem=loadedProblem, edge = edge)
            if edgeHints.exists():
                for edgeHint in edgeHints:
                    hintJson = {}
                    hintJson["text"] = edgeHint.text
                    hintJson["priority"] = edgeHint.priority
                    hintJson["usefulness"] = edgeHint.usefulness
                    edgeHintJson.append(hintJson)
            if edgeHintJson:
                edgeJson["hints"] = edgeHintJson


            edgeExplanations = Explanation.objects.filter(problem=loadedProblem, edge = edge)
            if edgeExplanations.exists():
                for edgeExplanation in edgeExplanations:
                    explanationJson = {}
                    explanationJson["text"] = edgeExplanation.text
                    explanationJson["priority"] = edgeExplanation.priority
                    explanationJson["usefulness"] = edgeExplanation.usefulness
                    edgeExplanationJson.append(explanationJson)
            if edgeExplanationJson:
                edgeJson["explanations"] = edgeExplanationJson

            edgeErrorSpecifiFeedbacks = ErrorSpecificFeedbacks.objects.filter(problem=loadedProblem, edge = edge)
            if edgeErrorSpecifiFeedbacks.exists():
                for edgeErrorSpecifiFeedback in edgeErrorSpecifiFeedbacks:
                    errorSpecificFeedbackJson = {}
                    errorSpecificFeedbackJson["text"] = edgeErrorSpecifiFeedback.text
                    errorSpecificFeedbackJson["priority"] = edgeErrorSpecifiFeedback.priority
                    errorSpecificFeedbackJson["usefulness"] = edgeErrorSpecifiFeedback.usefulness
                    edgeErrorSpecificFeedbackJson.append(errorSpecificFeedbackJson)
            if edgeErrorSpecificFeedbackJson:
                edgeJson["errorSpecificFeedbacks"] = edgeErrorSpecificFeedbackJson

            edgeDoubts = Doubt.objects.filter(problem=loadedProblem, edge = edge)
            if edgeDoubts.exists():
                for edgeDoubt in edgeDoubts:
                    doubtJson = {}
                    answersJson = []

                    doubtJson["text"] = edgeDoubt.text
                    edgeDoubtAnswers = Answer.objects.filter(problem=loadedProblem, doubt = edgeDoubt)
                    answerJson = None
                    if edgeDoubtAnswers.exists():
                        for edgeDoubtAnswer in edgeDoubtAnswers:
                            answerJson = {}
                            answerJson["text"] = edgeDoubtAnswer.text
                            answerJson["usefulness"] = edgeDoubtAnswer.usefulness
                            answersJson.append(answerJson)
                    
                    if answerJson:
                        doubtJson["answers"] = answersJson

                    edgeDoubtJson.append(doubtJson)
                    
            if edgeDoubtJson:
                edgeJson["doubts"] = edgeDoubtJson
            
            allEdgesJson.append(edgeJson)


        returnjson["edges"] = allEdgesJson

        return returnjson

    #Envia a resposta final
    @transaction.atomic
    @XBlock.json_handler
    def send_answer(self, data, suffix=''):

        loadedProblem = Problem.objects.get(id=self.problemId)
        #Inicialização e coleta dos dados inicial
        answerArray = data['answer'].split('\n')

        if '' in answerArray:
            answerArray =  list(filter(lambda value: value != '', answerArray))

        self.answerSteps = answerArray
        #self.saveStatesAndSteps(answerArray)

        if loadedProblem.multipleChoiceProblem == 1 and 'radioAnswer' not in data :
            if self.language == 'pt':
                return {"error": "Nenhuma opções de resposta foi selecionada!"}
            else:
                return {"error": "Please select one of the answers!"}

        if len(answerArray) < 2 :
                if self.language == 'pt':
                    return {"error": "A sua resolução precisa conter pelo menos 2 passos"}
                else:
                    return {"error": "Your solution must have at least 2 steps"}

        if loadedProblem.multipleChoiceProblem == 1:
            self.answerRadio = data['radioAnswer']

        isStepsCorrect = None

        currentStep = 0

        wrongElement = None

        self.studentResolutionsStates = answerArray
        self.studentResolutionsSteps = list()

        endNode = Node.objects.get(problem=loadedProblem, title = "_end_")

        lastElement = '_start_'
        #Aqui ficaria o updateCG, mas sem a parte do evaluation
        #Salva os passos, estados e também salva os passos feitos por cada aluno, de acordo com seu ID
        #COMENTADO OS PASSOS DE ATUALIZAÇÃO DE CORRETUDE, VAMOS FAZER DIREITO AGORA
        #LEMBRAR DE FAZER O IF DE ÚLTINO ELEMENTO PARA NÃO FICAR FEIO
        for step in answerArray:

            lastNode = Node.objects.select_for_update().filter(problem=loadedProblem, title=transformToSimplerAnswer(lastElement))
            currentNode = Node.objects.select_for_update().filter(problem=loadedProblem, title=transformToSimplerAnswer(step))

            if not lastNode.exists():
                n1 = Node(title=lastElement, problem=loadedProblem, dateAdded=datetime.now())
                n1.save()
            else:
                n1 = lastNode.first()
                if n1.visible == 0:
                    n1.visible = 1
                    n1.save()

            if lastNode.exists() and not currentNode.exists():
                n2 = Node(title=step, problem=loadedProblem, dateAdded=datetime.now())
                n2.save()
            else:
                n2 = currentNode.first()
                if n2.visible == 0:
                    n2.visible = 1
                    n2.save()
            
            currentEdge = Edge.objects.select_for_update().filter(problem=loadedProblem, sourceNode = n1, destNode = n2)
            if not currentEdge.exists():
                if lastElement == '_start_':
                    e1 = Edge(sourceNode = n1, destNode = n2, problem=loadedProblem, dateAdded=datetime.now(), correctness = 1, fixedValue=1)
                else:
                    e1 = Edge(sourceNode = n1, destNode = n2, problem=loadedProblem, dateAdded=datetime.now())

                e1.save()
            else:
                e1 = currentEdge.first()
                if e1.visible == 0:
                    e1.visible = 1
                    e1.save()


            self.studentResolutionsSteps.append(str((lastElement, step)))
            lastElement = step

        #Adicionar o caso do últio elemento com o _end_
        finalElement = '_end_'

        currentNode = Node.objects.get(problem=loadedProblem, title=transformToSimplerAnswer(lastElement))
        edgeList = Edge.objects.select_for_update().filter(problem=loadedProblem, sourceNode=currentNode, destNode=endNode)

        if not edgeList.exists():
            e1 = Edge(sourceNode = currentNode, destNode = endNode, problem=loadedProblem, dateAdded=datetime.now(), correctness = 1, fixedValue=1)
            e1.save()
        else:
            e1 = edgeList.first()
            if e1.visible == 0:
                e1.visible = 1
                e1.save()
            

        self.studentResolutionsSteps.append(str((lastElement, finalElement)))


        lastElement = '_start_'
        #Verifica se a resposta está correta
        for step in answerArray:

            lastNode = Node.objects.get(problem=loadedProblem, title=transformToSimplerAnswer(lastElement), visible = 1)
            currentNode = Node.objects.get(problem=loadedProblem, title=transformToSimplerAnswer(step), visible = 1)
            edgeList = Edge.objects.filter(problem=loadedProblem, sourceNode=lastNode, destNode=currentNode, visible = 1)

            if lastElement == '_start_':
                lastElement = step
                currentStep = currentStep + 1
                continue

            if (edgeList.exists() and edgeList[0].correctness >= stronglyValidStep[0] and lastNode.correctness >= correctState[0] and currentNode.correctness >= correctState[0]):
                endNodes = Edge.objects.filter(problem=loadedProblem, sourceNode=currentNode, destNode=endNode)
                if  (endNodes.exists()):
                    isStepsCorrect = True
                    break
                else:
                    lastElement = step
                    currentStep = currentStep + 1
                    continue
            else:
                if ((edgeList.exists() and edgeList[0].correctness > possiblyInvalidStep[0] and edgeList[0].correctness <= possiblyValidStep[0]) or (lastNode.correctness >= unknownState[0] and lastNode.correctness <= unknownState[1]) or (currentNode.correctness >= unknownState[0] and currentNode.correctness <= unknownState[1])):
                    break
                else:
                    isStepsCorrect = False
        
        if isStepsCorrect is None:
            isAnswerCorrect = None
        else:
            lastNodes = Node.objects.get(problem = loadedProblem, title = transformToSimplerAnswer(answerArray[-1]))
            if isStepsCorrect and (loadedProblem.multipleChoiceProblem == 0 or (lastNodes.linkedSolution != None and lastNodes.linkedSolution != "")):
                isAnswerCorrect = isStepsCorrect and (loadedProblem.multipleChoiceProblem == 0 or (transformToSimplerAnswer(data['radioAnswer']) == transformToSimplerAnswer(lastNodes.linkedSolution) and self.problemCorrectAnswer == data['radioAnswer']))
            else:
                isAnswerCorrect = None

        if loadedProblem.multipleChoiceProblem == 1:
            generatedResolution = self.generateResolution(answerArray, data['radioAnswer'])
        else:
            generatedResolution = self.generateResolution(answerArray, None)


        minimal = self.getMinimalFeedbackFromStudentResolution(answerArray, generatedResolution["nodeIdList"])
        minimalSteps = []
        minimalStates = []
        resolutionForStates = []
        for model in minimal["askInfoSteps"]:
            if isinstance(model, Edge):
                minimalSteps.append(model.sourceNode.title)
                minimalSteps.append(model.destNode.title)
            else:
                minimalStates.append(model.title)
                resolutionNames = []
                for resStateId in ast.literal_eval(minimal["askInfoResolutions"][model.id].nodeIdList):
                    nodeToBeAdded = Node.objects.get(id = resStateId)
                    if nodeToBeAdded.title != "_start_" and nodeToBeAdded.title != "_end_":
                        resolutionNames.append(nodeToBeAdded.title)
                        if (nodeToBeAdded.id == model.id):
                            break
                resolutionForStates.append(resolutionNames)

        errorSpecific = self.getErrorSpecificFeedbackFromProblemGraph(answerArray)
        errorSpecificSteps = []
        for errorSpecificStep in errorSpecific:
            errorSpecificSteps.append(errorSpecificStep.sourceNode.title)
            errorSpecificSteps.append(errorSpecificStep.destNode.title)

        explanation = self.getExplanationsFromProblemGraph(answerArray)
        explanationSteps = []
        for explanationStep in explanation:
            explanationSteps.append(explanationStep.sourceNode.title)
            explanationSteps.append(explanationStep.destNode.title)

        hints = self.getHintsFromProblemGraph(answerArray)
        hintsSteps = []
        for hintsStep in hints:
            hintsSteps.append(hintsStep.sourceNode.title)
            hintsSteps.append(hintsStep.destNode.title)

        doubts = self.getDoubtsFromProblemGraph()
        doubtsStepReturn = []
        doubtsNodeReturn = []
        for model in doubts:
            if model.type == 1:
                edgeDoubt = {"message": model.text, "source": model.edge.sourceNode.title, "dest": model.edge.destNode.title, "doubtId": model.id}
                doubtsStepReturn.append(edgeDoubt)
            else:
                nodeDoubt = {"message": model.text, "node": model.node.title, "doubtId": model.id}
                doubtsNodeReturn.append(nodeDoubt)

        #Não ativado por enquanto por não ter uso
        #KnowledgeComponents = self.getKnowledgeComponentFromProblemGraph(answerArray)
        #KnowledgeComponentSteps= []
        #for KnowledgeComponent in KnowledgeComponents:
        #    KnowledgeComponentSteps.append(KnowledgeComponent.sourceNode.title)
        #    KnowledgeComponentSteps.append(KnowledgeComponent.destNode.title)
        #Fim da parte do updateCG

        self.alreadyAnswered = True

        if isAnswerCorrect == None:
            if loadedProblem.multipleChoiceProblem == 0:
                if self.language == 'pt':
                    message = "Sua resolução está em análise"
                else:
                    message = "Your resolution is being analyzed"
            else:
                if self.language == 'pt':
                    message = "Sua resposta e resolução estão em análise"
                else:
                    message = "Both your answer and solution are being analyzed"

        elif isAnswerCorrect:
            if loadedProblem.multipleChoiceProblem == 0:
                if self.language == 'pt':
                    message = "Sua resolução está correta! Parabéns!"
                else:
                    message = "Congratulations! Your resolution is correct!"
            else:
                if self.language == 'pt':
                    message = "Sua resposta e resolução estão ambas corretas! Parabéns!"
                else:
                    message = "Both your answer and solution are correct! Congratulations!"
        elif not isAnswerCorrect:
            if loadedProblem.multipleChoiceProblem == 0:
                if self.language == 'pt':
                    message = "Sua resolução está incorreta"
                else:
                    message = "Your resolution is incorrect"
            else:
                if self.language == 'pt':
                    message = "Sua resolução e/ou resposta final estão incorretas"
                else:
                    message = "Your solution and/or your answer are incorrect"

        self.saveStatesAndSteps(answerArray)
        self.saveAskedFeedbacks(loadedProblem, minimalStates, minimalSteps, explanationSteps, hintsSteps, errorSpecificSteps, doubtsNodeReturn, doubtsStepReturn)
        return {"message": message, "minimalStep": minimalSteps, "minimalState": minimalStates, "errorSpecific": errorSpecificSteps, "explanation": explanationSteps, "doubtsSteps": doubtsStepReturn, "doubtsNodes": doubtsNodeReturn, "answerArray": answerArray, "hints": hintsSteps, "minimalStateResolutions": resolutionForStates}

    def saveAskedFeedbacks(self, loadedProblem, minimalStates, minimalSteps, explanations, hints, errorSpecifics, doubtStates, doubtSteps):
        for state in minimalStates:
            state = Node.objects.get(problem = loadedProblem, title = state)
            feedback = AskedFeedback(problem=loadedProblem, type=0,feedbackType="minimalState", dateAdded = datetime.now(), studentId=self.studentId, node=state)
            feedback.save()
        for i in range(0, len(minimalSteps), 2):
            step = Edge.objects.get(problem = loadedProblem, sourceNode__title = minimalSteps[i], destNode__title=minimalSteps[i+1])
            feedback = AskedFeedback(problem=loadedProblem, type=1,feedbackType="minimalStep", dateAdded = datetime.now(), studentId=self.studentId, edge=step)
            feedback.save()
        for i in range(0, len(explanations), 2):
            step = Edge.objects.get(problem = loadedProblem, sourceNode__title = explanations[i], destNode__title=explanations[i+1])
            feedback = AskedFeedback(problem=loadedProblem, type=1,feedbackType="explanation", dateAdded = datetime.now(), studentId=self.studentId, edge=step)
            feedback.save()
        for i in range(0, len(hints), 2):
            step = Edge.objects.get(problem = loadedProblem, sourceNode__title = hints[i], destNode__title=hints[i+1])
            feedback = AskedFeedback(problem=loadedProblem, type=1,feedbackType="hint", dateAdded = datetime.now(), studentId=self.studentId, edge=step)
            feedback.save()
        for i in range(0, len(errorSpecifics), 2):
            step = Edge.objects.get(problem = loadedProblem, sourceNode__title = errorSpecifics[i], destNode__title=errorSpecifics[i+1])
            feedback = AskedFeedback(problem=loadedProblem, type=1,feedbackType="errorSpecific", dateAdded = datetime.now(), studentId=self.studentId, edge=step)
            feedback.save()
        for doubtObj in doubtStates:
            doubt = Doubt.objects.get(problem = loadedProblem, id=doubtObj["doubtId"])
            feedback = AskedFeedback(problem=loadedProblem, type=0,feedbackType="doubtState", dateAdded = datetime.now(), studentId=self.studentId, doubt=doubt)
            feedback.save()
        for doubtObj in doubtSteps:
            doubt = Doubt.objects.get(problem = loadedProblem, id=doubtObj["doubtId"])
            feedback = AskedFeedback(problem=loadedProblem, type=1,feedbackType="doubtStep", dateAdded = datetime.now(), studentId=self.studentId, doubt=doubt)
            feedback.save()
        return

    def getMinimalFeedbackFromStudentResolution(self, resolution, nodeIdList):
        askInfoSteps = []
        askInfoResolutions = {}
        loadedProblem = Problem.objects.get(id=self.problemId)
        previousStateName = "_start_"
        nextStateName = None
        transformedResolution = []
        for item in resolution:
            transformedResolution.append(transformToSimplerAnswer(item))

        for index, stateName in enumerate(resolution):
            if index + 1 < len(resolution):
                nextStateName = resolution[index + 1]
            else:
                nextStateName = "_end_"

            if previousStateName != "_start_":
                inforSteps1 = Edge.objects.filter(problem=loadedProblem, sourceNode__title = transformToSimplerAnswer(previousStateName)).exclude(destNode__title=transformToSimplerAnswer(stateName)).exclude(destNode__title = "_end_").exclude(sourceNode__title = "_start_").exclude(fixedValue = 1).exclude(destNode__visible=0).exclude(sourceNode__visible=0)#.exclude(correctness = 1).exclude(correctness = -1)
                for step in inforSteps1:
                    if step not in askInfoSteps:
                        askInfoSteps.append(step)

                inforSteps2 = Edge.objects.filter(problem=loadedProblem, destNode__title=transformToSimplerAnswer(stateName)).exclude(sourceNode__title = transformToSimplerAnswer(previousStateName)).exclude(destNode__title = "_end_").exclude(sourceNode__title = "_start_").exclude(fixedValue = 1).exclude(destNode__visible=0).exclude(sourceNode__visible=0)#.exclude(correctness = 1).exclude(correctness = -1)
                for step in inforSteps2:
                    if step not in askInfoSteps:
                        askInfoSteps.append(step)

                #Experimental
                commonIds = nodeIdList[:len(nodeIdList)-(len(nodeIdList) - (index))]
                commonIdsStr = str(commonIds)[:-1]

                differentIds = nodeIdList[:len(nodeIdList)-(len(nodeIdList) - (index + 2))]
                differentIdsStr = str(differentIds)[:-1]

                inforSteps3 = Resolution.objects.filter(problem=loadedProblem, nodeIdList__startswith=commonIdsStr).exclude(nodeIdList__startswith = differentIdsStr)
                for infoStep in inforSteps3:
                    nodeIdlistLiteral = ast.literal_eval(infoStep.nodeIdList)
                    possibleEdge = Edge.objects.filter(problem=loadedProblem, sourceNode__id = nodeIdlistLiteral[index], destNode__id = nodeIdlistLiteral[index + 1]).exclude(visible = 0).exclude(destNode__visible=0).exclude(sourceNode__visible=0).exclude(sourceNode__fixedValue=1)
                    if possibleEdge.exists(): 
                        if possibleEdge.first() not in askInfoSteps and possibleEdge.first().fixedValue == 0: #and possibleEdge.first().correctness != 1 and possibleEdge.first().correctness != -1:
                            askInfoSteps.append(possibleEdge.first())
                        if possibleEdge.first().sourceNode not in askInfoSteps: #and possibleEdge.first().sourceNode.correctness != 1 and possibleEdge.first().sourceNode.correctness != -1:
                            askInfoSteps.append(possibleEdge.first().sourceNode)
                            askInfoResolutions[possibleEdge.first().sourceNode.id] = infoStep

            
            if nextStateName != "_end_":
                inforSteps4 = Edge.objects.filter(problem=loadedProblem, destNode__title = transformToSimplerAnswer(nextStateName)).exclude(sourceNode__title = transformToSimplerAnswer(stateName)).exclude(destNode__title = "_end_").exclude(sourceNode__title = "_start_").exclude(fixedValue = 1).exclude(destNode__visible=0).exclude(sourceNode__visible=0)#.exclude(correctness = 1).exclude(correctness = -1)
                for step in inforSteps4:
                    if step not in askInfoSteps:
                        askInfoSteps.append(step)
                inforSteps5 = Edge.objects.filter(problem=loadedProblem, sourceNode__title = transformToSimplerAnswer(stateName)).exclude(destNode__title = transformToSimplerAnswer(nextStateName)).exclude(destNode__title = "_end_").exclude(sourceNode__title = "_start_").exclude(fixedValue = 1).exclude(destNode__visible=0).exclude(sourceNode__visible=0)#.exclude(correctness = 1).exclude(correctness = -1)
                for step in inforSteps5:
                    if step not in askInfoSteps:
                        askInfoSteps.append(step)
 
                #Experimental
                commonIds = nodeIdList[:len(nodeIdList)-(len(nodeIdList) - (index + 1))]
                commonIdsStr = str(commonIds)[:-1]

                differentIds = nodeIdList[:len(nodeIdList)-(len(nodeIdList) - (index + 3))]
                differentIdsStr = str(differentIds)[:-1]

                inforSteps6 = Resolution.objects.filter(problem=loadedProblem, nodeIdList__startswith=commonIdsStr).exclude(nodeIdList__startswith = differentIdsStr)
                for infoStep in inforSteps6:
                    nodeIdlistLiteral = ast.literal_eval(infoStep.nodeIdList)
                    possibleEdge = Edge.objects.filter(problem=loadedProblem, sourceNode__id = nodeIdlistLiteral[index + 1], destNode__id = nodeIdlistLiteral[index + 2]).exclude(visible = 0).exclude(destNode__visible=0).exclude(sourceNode__visible=0).exclude(destNode__fixedValue=1)
                    if possibleEdge.exists():
                        if possibleEdge.first() not in askInfoSteps and possibleEdge.first().fixedValue == 0: #and possibleEdge.first().correctness != 1 and possibleEdge.first().correctness != -1:
                            askInfoSteps.append(possibleEdge.first())
                        if possibleEdge.first().destNode not in askInfoSteps: #and possibleEdge.first().destNode.correctness != 1 and possibleEdge.first().destNode.correctness != -1:
                            askInfoSteps.append(possibleEdge.first().destNode)
                            askInfoResolutions[possibleEdge.first().destNode.id] = infoStep

            previousStateName = stateName

        askInfoSteps.sort(key=orderMinimalFeedback)
        if askInfoSteps is not None and len(askInfoSteps) >= maxMinimumFeedback:
            return {"askInfoSteps": askInfoSteps[0:maxMinimumFeedback], "askInfoResolutions": askInfoResolutions}
        else:
            return {"askInfoSteps": askInfoSteps, "askInfoResolutions": askInfoResolutions}


    def getErrorSpecificFeedbackFromProblemGraph(self, resolution):
        CFEE = []
        returnList = []
        transformedResolution = []
        for item in resolution:
            transformedResolution.append(transformToSimplerAnswer(item))

        loadedProblem = Problem.objects.get(id=self.problemId)
        CFEE = Edge.objects.filter(problem=loadedProblem, correctness__lt = possiblyInvalidStep[0], sourceNode__correctness__gte = correctState[0], destNode__correctness__lte = incorrectState[1], visible = 1)
        for stepEE in CFEE:
            sourceNodeTitleEE = stepEE.sourceNode.title 
            if sourceNodeTitleEE in transformedResolution:
                sourceNodeIndexEE = transformedResolution.index(sourceNodeTitleEE)
                if sourceNodeIndexEE < len(transformedResolution) - 1:
                    if transformedResolution[sourceNodeIndexEE + 1] != stepEE.destNode.title:
                        possibleEdge = Edge.objects.filter(problem=loadedProblem, correctness__gte = stronglyValidStep[0], sourceNode__title = sourceNodeTitleEE, destNode__title = transformedResolution[sourceNodeIndexEE + 1], destNode__correctness__gte = correctState[0])
                        if possibleEdge.exists() and ErrorSpecificFeedbacks.objects.filter(problem=loadedProblem, edge=stepEE).count() < maxToAsk:
                            returnList.append(stepEE)
        if len(returnList) >= maxErrorSpecificFeedback:
            returnList.sort(key=orderErrorSpecificFeedback)
            return returnList[0:maxErrorSpecificFeedback]
        else:
            return returnList

    def getHintsFromProblemGraph(self, resolution):
        CDI = []
        returnList = []
        transformedResolution = []
        for item in resolution:
            transformedResolution.append(transformToSimplerAnswer(item))

        loadedProblem = Problem.objects.get(id=self.problemId)
        CDI = Edge.objects.filter(problem=loadedProblem, correctness__gte = stronglyValidStep[0], sourceNode__correctness__gte = correctState[0], destNode__correctness__gte = correctState[0], visible = 1)
        for stepHint in CDI:
            sourceNodeTitleEX = stepHint.sourceNode.title 
            if sourceNodeTitleEX in transformedResolution:
                sourceNodeIndexEX = transformedResolution.index(sourceNodeTitleEX)
                if sourceNodeIndexEX < len(transformedResolution) - 1:
                    if transformedResolution[sourceNodeIndexEX + 1] == stepHint.destNode.title and Hint.objects.filter(problem=loadedProblem, edge=stepHint).count() < maxToAsk:
                        returnList.append(stepHint)
        if len(returnList) >= maxHints:
            returnList.sort(key=orderHints)
            return returnList[0:maxHints]
        else:
            return returnList

    def getExplanationsFromProblemGraph(self, resolution):
        CEX = []
        returnList = []
        transformedResolution = []
        for item in resolution:
            transformedResolution.append(transformToSimplerAnswer(item))

        loadedProblem = Problem.objects.get(id=self.problemId)
        CEX = Edge.objects.filter(problem=loadedProblem, correctness__gte = stronglyValidStep[0], sourceNode__correctness__gte = correctState[0], destNode__correctness__gte = correctState[0], visible = 1)
        for stepEX in CEX:
            sourceNodeTitleEX = stepEX.sourceNode.title 
            if sourceNodeTitleEX in transformedResolution:
                sourceNodeIndexEX = transformedResolution.index(sourceNodeTitleEX)
                if sourceNodeIndexEX < len(transformedResolution) - 1:
                    if transformedResolution[sourceNodeIndexEX + 1] == stepEX.destNode.title and Explanation.objects.filter(problem=loadedProblem, edge=stepEX).count() < maxToAsk:
                        returnList.append(stepEX)
        if len(returnList) >= maxExplanations:
            returnList.sort(key=orderExplanations)
            return returnList[0:maxExplanations]
        else:
            return returnList


    def getDoubtsFromProblemGraph(self):
        CDU = []
        filteredCDU = []
        loadedProblem = Problem.objects.get(id=self.problemId)
        CDU = Doubt.objects.filter(problem=loadedProblem).exclude(node__isnull = True, type = 0).exclude(edge__isnull = True, type = 1).order_by("dateModified")

        for doubt in CDU:
            if Answer.objects.filter(problem=loadedProblem, doubt=doubt).count() < 3:
                filteredCDU.append(doubt)

        if len(filteredCDU) > maxDoubts:
            return filteredCDU[0:maxDoubts]
        else:
            return filteredCDU

    def getKnowledgeComponentFromProblemGraph(self, resolution):
        relatedSteps = []
        usefulRelatedSteps = []
        transformedResolution = []
        for item in resolution:
            transformedResolution.append(transformToSimplerAnswer(item))

        loadedProblem = Problem.objects.get(id=self.problemId)

        CCC1 = Edge.objects.filter(problem=loadedProblem, correctness__lt = possiblyInvalidStep[0], sourceNode__correctness__gte = correctState[0], destNode__correctness__lte = incorrectState[1], visible = 1)
        CCC2 = Edge.objects.filter(problem=loadedProblem, correctness__gte = stronglyValidStep[0], sourceNode__correctness__gte = correctState[0], destNode__correctness__gte = correctState[0], visible = 1)

        for stepCC in CCC2:
            sourceNodeTitleEX = stepCC.sourceNode.title 
            if sourceNodeTitleEX in transformedResolution:
                sourceNodeIndexEX = transformedResolution.index(sourceNodeTitleEX)
                if sourceNodeIndexEX < len(transformedResolution) - 1:
                    if transformedResolution[sourceNodeIndexEX + 1] == stepCC.destNode.title:
                        relatedSteps.append(stepCC)

        for stepCC in CCC1:
            sourceNodeTitleEE = stepCC.sourceNode.title 
            if sourceNodeTitleEE in transformedResolution:
                sourceNodeIndexEE = transformedResolution.index(sourceNodeTitleEE)
                if sourceNodeIndexEE < len(transformedResolution) - 1:
                    if transformedResolution[sourceNodeIndexEE + 1] != stepCC.destNode.title:
                        possibleEdge = Edge.objects.filter(problem=loadedProblem, correctness__gte = stronglyValidStep[0], sourceNode__title = sourceNodeTitleEE, destNode__title = transformedResolution[sourceNodeIndexEE + 1], destNode__correctness__gte = correctState[0])
                        if possibleEdge.exists():
                            usefulRelatedSteps.append(stepCC)


        relatedSteps.append(usefulRelatedSteps)


        if len(relatedSteps) >= maxKnowledgeComponent:
            relatedSteps.sort(key=orderKnowledgeComponent)
            return relatedSteps[0:maxKnowledgeComponent]
        else:
            return relatedSteps
    
    @transaction.atomic
    def recalculateResolutionCorrectnessFromNode(self, node):
        loadedProblem = Problem.objects.get(id=self.problemId)
        allResolutions = Resolution.objects.select_for_update().select_for_update().filter(problem=loadedProblem, nodeIdList__isnull = False, edgeIdList__isnull= False).exclude(nodeIdList__exact='', edgeIdList__exact='')
        resolutionsToBeModified = []
        for resolution in allResolutions:
            usedNodes = ast.literal_eval(resolution.nodeIdList)
            if node.id in usedNodes:
                resolution.correctness = 0
                resolution.save()
                resolutionsToBeModified.append(resolution)
        for resolution in resolutionsToBeModified:
            resolution.correctness = self.corretudeResolucao(resolution, False)
            resolution.save()

    @transaction.atomic
    def recalculateResolutionCorrectnessFromEdge(self, edge):
        loadedProblem = Problem.objects.get(id=self.problemId)
        allResolutions = Resolution.objects.select_for_update().filter(problem=loadedProblem, nodeIdList__isnull = False, edgeIdList__isnull= False).exclude(nodeIdList__exact='', edgeIdList__exact='')
        resolutionsToBeModified = []
        for resolution in allResolutions:
            usedNodes = ast.literal_eval(resolution.edgeIdList)
            if edge.id in usedNodes:
                resolution.correctness = 0
                resolution.save()
                resolutionsToBeModified.append(resolution)
        for resolution in resolutionsToBeModified:
            resolution.correctness = self.corretudeResolucao(resolution, False)
            resolution.save()


    def corretudeResolucao(self, resolution, innerUpdate):
        loadedProblem = Problem.objects.get(id=self.problemId)
        stateIdList = ast.literal_eval(resolution.nodeIdList)
        stateIdAmount = len(stateIdList) - 2
        stepIdList = ast.literal_eval(resolution.edgeIdList)
        stepIdAmount = len(stepIdList) - 2

        #Para casos com apenas um estado na resolução
        if stepIdAmount == 0:
            stepIdAmount = 2

        stateCorrectness = 0
        stepCorrectness = 0

        try:
            for stateId in stateIdList:
                if stateId != stateIdList[0] and stateId != stateIdList[-1]:
                    if innerUpdate:
                        state = Node.objects.select_for_update().get(problem=loadedProblem, id = stateId)
                        stateCorrectness = stateCorrectness + self.corretudeEstado(state, innerUpdate)
                    else:
                        state = Node.objects.get(problem=loadedProblem, id = stateId)
                        stateCorrectness = stateCorrectness + state.correctness


            for stepId in stepIdList:
                if stepId != stepIdList[0] and stepId != stepIdList[-1]:
                    if innerUpdate:
                        step = Edge.objects.select_for_update().get(problem=loadedProblem, id = stepId)
                        stepCorrectness = stepCorrectness + self.validadePasso(step, innerUpdate)
                    else:
                        step = Edge.objects.get(problem=loadedProblem, id = stepId)
                        stepCorrectness = stepCorrectness + step.correctness
                
            return (1/(2*stateIdAmount)) * (stateCorrectness) + (1/(2*stepIdAmount)) * (stepCorrectness)
        except:
            return 0
    
    def possuiEstado(self, state, resolution):
        return state.id in ast.literal_eval(resolution.nodeIdList)
    
    def possuiEstadoConjunto(self, state, resolutions):
        sum = 0
        if resolutions.exists():
            for resolution in resolutions:
                sum = sum + self.possuiEstado(state, resolution)
        
        return sum
    
    def corretudeEstado(self, state, innerUpdate):
        if state.fixedValue == 1:
            return state.correctness

        loadedProblem = Problem.objects.get(id=self.problemId)
        if loadedProblem.multipleChoiceProblem == 0:
            correctResolutions = Resolution.objects.filter(problem=loadedProblem, correctness__gte=partiallyCorrectResolution[0])
            incorrectResolutions = Resolution.objects.filter(problem=loadedProblem, correctness__lte=partiallyIncorrectResolution[1])
        else:
            correctResolutions = Resolution.objects.filter(problem=loadedProblem, selectedOption=self.problemCorrectAnswer)
            incorrectResolutions = Resolution.objects.filter(problem=loadedProblem, selectedOption__isnull=False).exclude(selectedOption=self.problemCorrectAnswer)

        correctValue = self.possuiEstadoConjunto(state, correctResolutions)
        incorrectValue = self.possuiEstadoConjunto(state, incorrectResolutions)
    
        if correctValue + incorrectValue != 0:
            correctness =  (correctValue-incorrectValue)/(correctValue + incorrectValue)
        else:
            correctness = 0

        if innerUpdate:
            state.correctness = correctness
            state.save()

        return correctness
    
    def possuiPassoConjunto(self, step, resolutions):
        sum = 0
        for resolution in resolutions:
            sum = sum + self.possuiPasso(step, resolution)
        
        return sum

    def possuiPasso(self, step, resolution):
        return step.id in ast.literal_eval(resolution.edgeIdList)
    
    def validadePasso(self, step, innerUpdate):
        if step.fixedValue == 1:
            return step.correctness
        loadedProblem = Problem.objects.get(id=self.problemId)
        if loadedProblem.multipleChoiceProblem == 0:
            correctResolutions = Resolution.objects.filter(problem=loadedProblem, correctness__gte=partiallyCorrectResolution[0])
            incorrectResolutions = Resolution.objects.filter(problem=loadedProblem, correctness__lte=partiallyIncorrectResolution[1])
        else:
            correctResolutions = Resolution.objects.filter(problem=loadedProblem, selectedOption=self.problemCorrectAnswer)
            incorrectResolutions = Resolution.objects.filter(problem=loadedProblem, selectedOption__isnull=False).exclude(selectedOption=self.problemCorrectAnswer)

        correctValue = self.possuiPassoConjunto(step, correctResolutions)
        incorrectValue = self.possuiPassoConjunto(step, incorrectResolutions)

    
        if correctValue + incorrectValue != 0:
            correctness =  (correctValue-incorrectValue)/(correctValue + incorrectValue)
        else:
            correctness =  0

        if innerUpdate:
            step.correctness = correctness
            step.save()
        return correctness

    def generateAttempt(self, resolution):

        loadedProblem = Problem.objects.get(id=self.problemId)

        nodeArray = []
        edgeArray = []
        lastNodeName = "_start_"
        lastNode = Node.objects.get(problem=loadedProblem, title=transformToSimplerAnswer(lastNodeName))
        nodeArray.append(lastNode.id)
        earlyBreak = False
        for node in resolution:
            currentNode = Node.objects.filter(problem=loadedProblem, title=transformToSimplerAnswer(node))
            if currentNode.exists():
                nodeArray.append(currentNode.first().id)
            else:
                earlyBreak = True
                break
            currentEdge = Edge.objects.filter(problem=loadedProblem, sourceNode=lastNode, destNode=currentNode.first())
            if currentEdge.exists():
                edgeArray.append(currentEdge.first().id)
            else:
                earlyBreak = True
                break
            lastNode = currentNode.first()

        if not earlyBreak:
            currentNode = Node.objects.filter(problem=loadedProblem, title="_end_")
            currentEdge = Edge.objects.filter(problem=loadedProblem, sourceNode=lastNode, destNode=currentNode.first())
            if currentEdge.exists():
                nodeArray.append(currentNode.first().id)
                edgeArray.append(currentEdge.first().id)

        a1 = Attempt(problem=loadedProblem, studentId = self.studentId, attempt = self.studentRetries, nodeIdList = nodeArray, edgeIdList = edgeArray, dateCreated = datetime.now())
        a1.save()

        return {"nodeIdList": nodeArray, "edgeIdList": edgeArray}

    def generateResolution(self, resolution, selectedOption):

        loadedProblem = Problem.objects.get(id=self.problemId)

        nodeArray = []
        edgeArray = []
        lastNodeName = "_start_"
        lastNode = Node.objects.get(problem=loadedProblem, title=transformToSimplerAnswer(lastNodeName))
        nodeArray.append(lastNode.id)
        for node in resolution:
            currentNode = Node.objects.get(problem=loadedProblem, title=transformToSimplerAnswer(node))
            nodeArray.append(currentNode.id)
            currentEdge = Edge.objects.get(problem=loadedProblem, sourceNode=lastNode, destNode=currentNode)
            edgeArray.append(currentEdge.id)
            lastNode = currentNode

        currentNode = Node.objects.get(problem=loadedProblem, title="_end_")
        nodeArray.append(currentNode.id)
        currentEdge = Edge.objects.get(problem=loadedProblem, sourceNode=lastNode, destNode=currentNode)
        edgeArray.append(currentEdge.id)
        lastNode = currentNode

        r1 = Resolution.objects.select_for_update().filter(problem=loadedProblem, studentId = self.studentId, attempt = self.studentRetries)
        if r1.exists():
            existingRes = r1.first()
            existingRes.nodeIdList = nodeArray
            existingRes.edgeIdList = edgeArray

            if (selectedOption != None):
                existingRes.selectedOption = selectedOption
            existingRes.save()
            existingRes.refresh_from_db()
            existingRes.correctness = self.corretudeResolucao(existingRes, True)
            existingRes.save()

            return {"resolutionId": existingRes.id, "nodeIdList": nodeArray, "edgeIdList": edgeArray}

        return {"nodeIdList": nodeArray, "edgeIdList": edgeArray}

    @XBlock.json_handler
    @transaction.atomic
    def update_resolution_correctness(self,data,suffix=''):
        loadedProblem = Problem.objects.get(id=self.problemId)
        calculatedNodeRes = {}
        allRes = Resolution.objects.select_for_update().filter(problem=loadedProblem, nodeIdList__isnull = False, edgeIdList__isnull= False).exclude(nodeIdList__exact='', edgeIdList__exact='')
        for res in allRes:
            if res.nodeIdList not in calculatedNodeRes:
                res.correctness = self.corretudeResolucao(res, False)
                res.save()
            else:
                res.correctness = calculatedNodeRes[res.nodeIdList]
                res.save()

            #if res.correctness == 1 and res.nodeIdList not in calculatedNodeRes:
            #    lastNodeFromRes = Node.objects.select_for_update().get(id =  ast.literal_eval(res.nodeIdList)[-2])
            #    if lastNodeFromRes.fixedValue == 0:
            #        possibleOptions = {}
            #        allSameRes = Resolution.objects.filter(problem=loadedProblem, nodeIdList = res.nodeIdList, edgeIdList = res.edgeIdList)
            #        for sameRes in allSameRes:
            #            if sameRes.selectedOption not in possibleOptions:
            #                possibleOptions[sameRes.selectedOption] = 1
            #            else:
            #                possibleOptions[sameRes.selectedOption] += 1
            #        finalOption = None
            #        finalOptionCount = None

            #        for key in possibleOptions.keys():
            #            if finalOption == None:
            #                finalOption = key
            #                finalOptionCount = possibleOptions[key]
            #            else:
            #                if finalOptionCount < possibleOptions[key]:
            #                    finalOption = key
            #                    finalOptionCount = possibleOptions[key]

            #        lastNodeFromRes.linkedSolution = finalOption
            #        lastNodeFromRes.save()

            calculatedNodeRes[res.nodeIdList] = res.correctness
        return {}


    @XBlock.json_handler
    def initial_data(self, data, suffix=''):
        loadedProblem = Problem.objects.filter(id=self.problemId)
        if not loadedProblem.exists():
            return {"title": self.problemTitle, "description": self.problemDescription, 
            "answer1": self.problemAnswer1, "answer2": self.problemAnswer2, "answer3": self.problemAnswer3, "answer4": self.problemAnswer4, "answer5": self.problemAnswer5,
            "subject": self.problemSubject, "tags": self.problemTags, "alreadyAnswered": str(self.alreadyAnswered), "language": self.language}

        return {"title": self.problemTitle, "description": self.problemDescription, 
        "answer1": self.problemAnswer1, "answer2": self.problemAnswer2, "answer3": self.problemAnswer3, "answer4": self.problemAnswer4, "answer5": self.problemAnswer5,
        "subject": self.problemSubject, "tags": self.problemTags, "alreadyAnswered": str(self.alreadyAnswered), "multipleChoiceProblem": loadedProblem[0].multipleChoiceProblem, "language": self.language}


    # TO-DO: change this to create the scenarios you'd like to see in the
    # workbench while developing your XBlock.
    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("MyXBlock",
             """<myxblock/>
             """),
            ("Problema 1",
             """<myxblock/>
             """),
            ("Problema 2",
             """<myxblock/>
             """),
            ("Multiple MyXBlock",
             """<vertical_demo>
                <myxblock/>
                <myxblock/>
                <myxblock/>
                </vertical_demo>
             """),
        ]
