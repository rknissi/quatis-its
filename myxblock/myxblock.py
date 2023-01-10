import json
from re import I
import pkg_resources
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import Integer, Scope, String, Boolean, List, Set, Dict, Float
import ast 
from .studentGraph.models import Answer, Problem, Node, Edge, Resolution, ErrorSpecificFeedbacks, Hint, Explanation, Doubt, KnowledgeComponent
from .visualGraph import *
from django.utils.timezone import now
from datetime import datetime  
from django.http import JsonResponse
from django.core import serializers

receivedMinimalFeedbackAmount = 0.1
receivedHintUsefulnessAmount = 1

#Max amount of feedback
maxMinimumFeedback = 4
maxErrorSpecificFeedback = 2
maxExplanations = 2
maxDoubts = 2

#Step information
correctnessMinValue = -1
correctnessMaxValue = 1

#Resolution values
incorrectResolution = [-1, -0.75001]
partiallyIncorrectResolution = [-0.75, -0.00001]
partiallyCorrectResolution = [0, 0.74999]
correctResolution = [0.75, 1]
defaultResolutionValue = 0

problemGraphDefault = {'_start_': ['Option 1'], 'Option 1': ["Option 2"], "Option 2": ["_end_"]}
problemGraphNodePositionsDefault = {}  
problemGraphStatesCorrectnessDefault = {'_start_': correctState[1], 'Option 1': correctState[1], 'Option 2': correctState[1]}
problemGraphStepsCorrectnessDefault = {str(('_start_', 'Option 1')): validStep[1], str(('Option 1', 'Option 2')): validStep[1], str(('Option 2', '_end_')): validStep[1]}
allResolutionsDefault = []

#Ainda não salvando nada nessa variável
allResolutionsNew = allResolutionsDefault

def amorzinhoErrorSpecificFeedback(element):
    quantity = ast.literal_eval(ErrorSpecificFeedbacks.objects.filter(problem = element.problem, edge = element)).length()
    correctness = element.correctness
    return (1/(correctness * 10) * (1/(0.1 + quantity)))

def amorzinhoMinimalFeedback(element):
    return abs(element.correctness)

def amorzinhoHints(element):
    quantity = ast.literal_eval(Hint.objects.filter(problem = element.problem, edge = element)).length()
    correctness = element.correctness
    return (1/(correctness * 10) * (1/(0.1 + quantity)))

def amorzinhoExplanations(element):
    quantity = ast.literal_eval(Explanation.objects.filter(problem = element.problem, edge = element)).length()
    correctness = element.correctness
    return (1/(correctness * 10) * (1/(0.1 + quantity)))

def amorzinhoTempo(element):
    return element.dateAdded

def levenshteinDistance(A, B):
    if(len(A) == 0):
        return len(B)
    if(len(B) == 0):
        return len(A)
    if (A[0] == B[0]):
        return levenshteinDistance(A[1:], B[1:])
    return 1 + min(levenshteinDistance(A, B[1:]), levenshteinDistance(A[1:], B), levenshteinDistance(A[1:], B[1:])) 

#Colinha:
#Scope.user_state = Dado que varia de aluno para aluno
#Scope.user_state_summary = Dado igual para todos os alunos
#Scope.content = Dado imutável

class MyXBlock(XBlock):
    #Se o aluno já fez o exercício
    alreadyAnswered = Boolean(
        default=False, scope=Scope.user_state,
        help="If the student already answered the exercise",
    )

    studentId = Boolean(
        default=0, scope=Scope.user_state,
        help="StudentId for the problem",
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

    studentResolutionsCorrectness = Float(
        default=defaultResolutionValue, scope=Scope.user_state,
        help="Resolution correctness by the student",
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

    problemCorrectRadioAnswer = String(
        default="Option 1", scope=Scope.content,
        help="Correct item of the problem",
    )

    problemCorrectStates = Dict(
        default={'_start_': ['Option 1'], 'Option 1': ["Option 2"], "Option 2": ["_end_"]}, scope=Scope.content,
        help="List of correct states to the answer",
    )

    problemEquivalentStates = Dict(
        default={'option1': 'Option 1', 'option2': "Option 2"}, scope=Scope.content,
        help="For each entry, which step is equivalent to the original state representation",
    )

    problemTipsToNextState = Dict(
        default={"Option 1": ["Dicaaaaas 1", "Dicaaaaaaa 2"], "Option 2": ["Tainted Love suaidiosadisasa bcsabcasbcascnasnc sancnsacnsn cbascbasbcsabcbascbas", "Uia"]}, scope=Scope.content,
        help="List of tips for each state of the correct answers",
    )

    errorSpecificFeedbackFromSteps = Dict(
        default={str(('Option 1', 'Option 2')): ["Error Specific feedback 1", "Error Specific Feedback 2"], str(('X=500-2', 'X=498')): ["Error Specific feedback 1", "Error Specific Feedback 2"]}, scope=Scope.content,
        help="For each wrong step that the student uses, it will show a specific feedback",
    )

    explanationFromSteps = Dict(
        default={str(('Option 1', 'Option 2')): ["Explanation feedback 1", "Explanation Feedback 2"], str(('X=500-2', 'X=498')): ["Explanation feedback 1", "Explanation Feedback 2"]}, scope=Scope.content,
        help="For each correct step that the student uses, it will show a specific feedback",
    )

    problemDefaultHint = String(
        default="Verifique se a resposta está correta", scope=Scope.content,
        help="If there is no available hint",
    )

    problemInitialHint = String(
        default="Inicialmente, coloque o mesmo que está no enunciado", scope=Scope.content,
        help="If thew student dont know how to start thew process",
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

    problemSubject = String(
        default="Subject", scope=Scope.content,
        help="Subject of the problem",
    )

    problemTags = List(
        default=["Tag1, Tag2, Tag3"], scope=Scope.content,
        help="Tags of the problem",
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
        html = self.resource_string("static/html/myxblock.html")
        loadedProblem = Problem.objects.filter(id=self.problemId)
        if loadedProblem.exists():
            loadedMultipleChoiceProblem = loadedProblem[0].multipleChoiceProblem
            frag = Fragment(str(html).format(block=self, multipleChoiceProblem=loadedMultipleChoiceProblem))
        else: 
            frag = Fragment(str(html).format(block=self))
            

        frag.add_css(self.resource_string("static/css/myxblock.css"))
        frag.add_javascript(self.resource_string("static/js/src/myxblock.js"))

        #Também precisa inicializar
        frag.initialize_js('MyXBlock')
        self.lastWrongElementCount = 0
        return frag

    problem_view = student_view

    def studio_view(self,context=None):
        html=self.resource_string("static/html/myxblockEdit.html")

        loadedProblem = Problem.objects.filter(id=self.problemId)
        if loadedProblem.exists():
            loadedMultipleChoiceProblem = loadedProblem[0].multipleChoiceProblem
        else:
            loadedMultipleChoiceProblem = "Valor ainda não carregado"

        frag = Fragment(str(html).format(problemTitle=self.problemTitle,problemDescription=self.problemDescription,problemCorrectRadioAnswer=self.problemCorrectRadioAnswer,multipleChoiceProblem=loadedMultipleChoiceProblem,problemDefaultHint=self.problemDefaultHint,problemAnswer1=self.problemAnswer1,problemAnswer2=self.problemAnswer2,problemAnswer3=self.problemAnswer3,problemAnswer4=self.problemAnswer4,problemAnswer5=self.problemAnswer5,problemSubject=self.problemSubject,problemTags=self.problemTags))
        frag.add_javascript(self.resource_string("static/js/src/myxblockEdit.js"))

        frag.initialize_js('MyXBlockEdit')
        return frag

    @XBlock.json_handler
    def submit_graph_data(self,data,suffix=''):
        graphData = data.get('graphData')

        loadedProblem = Problem.objects.get(id=self.problemId)

        for node in graphData['nodes']:
            nodeModel = Node.objects.filter(problem=loadedProblem, title=node["id"])
            if not nodeModel.exists():
                n1 = Node(title=node["id"], correctness=float(node["correctness"]), problem=loadedProblem, nodePositionX=node["x"], nodePositionY=node["y"], dateAdded=datetime.now(), fixedValue=float(node["fixedValue"]))
                n1.save()
            else:
                nodeModel = nodeModel.first()
                nodeModel.correctness = float(node["correctness"])
                nodeModel.fixedValue = float(node["fixedValue"])
                nodeModel.visible = float(node["visible"])
                nodeModel.nodePositionX = node["x"]
                nodeModel.nodePositionY = node["y"]
                nodeModel.dateModified = datetime.now()
                nodeModel.save()

            if "stroke" in node:
                if node["stroke"] == finalNodeStroke:
                    edgeModel = Edge.objects.filter(problem=loadedProblem, sourceNode__title=node["id"], destNode__title="_end_")
                    if not edgeModel.exists():
                        fromNode = Node.objects.get(problem=loadedProblem, title=node["id"])
                        toNode = Node.objects.get(problem=loadedProblem, title="_end_")
                        e1 = Edge(sourceNode=fromNode, destNode=toNode, problem=loadedProblem, dateAdded=datetime.now())
                        e1.save()
                elif node["stroke"] == initialNodeStroke:
                    edgeModel = Edge.objects.filter(problem=loadedProblem, sourceNode__title="_start_", destNode__title=node["id"])
                    if not edgeModel.exists():
                        fromNode = Node.objects.get(problem=loadedProblem, title="_start_")
                        toNode = Node.objects.get(problem=loadedProblem, title=node["id"])
                        e1 = Edge(sourceNode=fromNode, destNode=toNode, problem=loadedProblem, dateAdded=datetime.now())
                        e1.save()


        for edge in graphData['edges']:
            edgeModel = Edge.objects.filter(problem=loadedProblem, sourceNode__title=edge["from"], destNode__title=edge["to"])
            if not edgeModel.exists():
                fromNode = Node.objects.get(problem=loadedProblem, title=edge["from"])
                toNode = Node.objects.get(problem=loadedProblem, title=edge["to"])
                e1 = Edge(sourceNode=fromNode, destNode=toNode, correctness=float(edge["correctness"]), problem=loadedProblem, visible=edge["visible"], dateAdded=datetime.now(), fixedValue=float(edge["fixedValue"]))
                e1.save()
            else:
                edgeModel = Edge.objects.get(problem=loadedProblem, sourceNode__title=edge["from"], destNode__title=edge["to"])
                edgeModel.correctness = float(edge["correctness"])
                edgeModel.visible = edge["visible"]
                edgeModel.dateModified = datetime.now()
                edgeModel.fixedValue = float(edge["fixedValue"])
                edgeModel.save()

        return {}


    @XBlock.json_handler
    def get_edge_info(self,data,suffix=''):
        errorSpecificFeedbacks = None
        explanations = None
        hints = None

        loadedProblem = Problem.objects.get(id=self.problemId)
        loadedEdge = Edge.objects.get(problem=loadedProblem, sourceNode__title=data.get("from"), destNode__title=data.get("to"))
        loadedHints = Hint.objects.filter(problem=loadedProblem, edge=loadedEdge).order_by("-usefulness", "priority")
        hints = []
        if loadedHints.exists():
            for hint in loadedHints:
                hints.append({"id": hint.id, "text": hint.text, "priority": hint.priority, "usefulness": hint.usefulness})

        loadedExplanations = Explanation.objects.filter(problem=loadedProblem, edge=loadedEdge).order_by("-usefulness", "priority")
        explanations = []
        if loadedExplanations.exists():
            for explanation in loadedExplanations:
                explanations.append({"id": explanation.id, "text": explanation.text, "priority": explanation.priority, "usefulness": explanation.usefulness})

        loadedErrorSpecificFeedbacks = ErrorSpecificFeedbacks.objects.filter(problem=loadedProblem, edge=loadedEdge).order_by("-usefulness", "priority")
        errorSpecificFeedbacks = []
        if loadedErrorSpecificFeedbacks.exists():
            for errorSpecificFeedback in loadedErrorSpecificFeedbacks:
                errorSpecificFeedbacks.append({"id": errorSpecificFeedback.id, "text": errorSpecificFeedback.text, "priority": errorSpecificFeedback.priority, "usefulness": errorSpecificFeedback.usefulness})
        
        return {"errorSpecificFeedbacks": errorSpecificFeedbacks, "explanations": explanations, "hints": hints}

    @XBlock.json_handler
    def submit_edge_info(self,data,suffix=''):

        loadedProblem = Problem.objects.get(id=self.problemId)
        loadedEdge = Edge.objects.get(problem=loadedProblem, sourceNode__title=data.get("from"), destNode__title=data.get("to"))
        
        allHints = ast.literal_eval(data.get("hints"))
        for hint in allHints:
            if "id" in hint:
                loadedHint = Hint.objects.get(problem=loadedProblem, edge=loadedEdge, id=hint["id"])
                loadedHint.dateModified = datetime.now()
            else:
                loadedHint = Hint(problem=loadedProblem, edge=loadedEdge, dateAdded=datetime.now())

            loadedHint.text = hint["text"]
            loadedHint.usefulness = hint["usefulness"]
            loadedHint.priority = hint["priority"]
            loadedHint.save()


        allErrorSpecificFeedbacks = ast.literal_eval(data.get("errorSpecificFeedbacks"))
        for errorSpecificFeedback in allErrorSpecificFeedbacks:
            if "id" in errorSpecificFeedback:
                loadedError = ErrorSpecificFeedbacks.objects.get(problem=loadedProblem, edge=loadedEdge, id=errorSpecificFeedback["id"])
                loadedError.dateModified = datetime.now()
            else:
                loadedError = ErrorSpecificFeedbacks(problem=loadedProblem, edge=loadedEdge, dateAdded=datetime.now())

            loadedError.text = errorSpecificFeedback["text"]
            loadedError.usefulness = errorSpecificFeedback["usefulness"]
            loadedError.priority = errorSpecificFeedback["priority"]
            loadedError.save()


        allExplanations = ast.literal_eval(data.get("explanations"))
        for explanation in allExplanations:
            if "id" in explanation:
                loadedExplanation = Explanation.objects.get(problem=loadedProblem, edge=loadedEdge, id=explanation["id"])
                loadedExplanation.dateModified = datetime.now()
            else:
                loadedExplanation = Explanation(problem=loadedProblem, edge=loadedEdge, dateAdded=datetime.now())

            loadedExplanation.text = explanation["text"]
            loadedExplanation.usefulness = explanation["usefulness"]
            loadedExplanation.priority = explanation["priority"]
            loadedExplanation.save()

        return {"status": "Done!"}

    @XBlock.json_handler
    def create_initial_positions(self,data,suffix=''):
        createGraphInitialPositions(self.problemId)

        return {"Status": "Ok"}


    def createInitialEdgeData(self, nodeList, problemFK):
        e1 = Edge(sourceNode=nodeList[0], destNode=nodeList[1], correctness=1, fixedValue=1, problem=problemFK, dateAdded=datetime.now())
        e2 = Edge(sourceNode=nodeList[1], destNode=nodeList[2], correctness=1, fixedValue=1, problem=problemFK, dateAdded=datetime.now())
        e3 = Edge(sourceNode=nodeList[2], destNode=nodeList[3], correctness=1, fixedValue=1, problem=problemFK, dateAdded=datetime.now())

        e1.save()
        e2.save()
        e3.save()

        #hint11 = Hint(problem=problemFK, edge=e1)
        #hint11.text="hahaha"
        #hint11.dateAdded = datetime.now()
        #hint11.priority = 1
        #hint11.usefulness = 1000

        #hint12 = Hint(problem=problemFK, edge=e1)
        #hint12.text="Uiaaa"
        #hint12.dateAdded = datetime.now()
        #hint12.priority = 2
        #hint12.usefulness = 1000


        hint21 = Hint(problem=problemFK, edge=e2)
        hint21.text="hint 1"
        hint21.dateAdded = datetime.now()
        hint21.priority = 1
        hint21.usefulness = 1000

        hint22 = Hint(problem=problemFK, edge=e2)
        hint22.text="Hint 2"
        hint22.dateAdded = datetime.now()
        hint22.priority = 2
        hint22.usefulness = 1000


        #hint31 = Hint(problem=problemFK, edge=e3)
        #hint31.text="Hint feedback 1"
        #hint31.dateAdded = datetime.now()
        #hint31.priority = 1
        #hint31.usefulness = 1000

        #hint32 = Hint(problem=problemFK, edge=e3)
        #hint32.text="Hint Feedback 2"
        #hint32.dateAdded = datetime.now()
        #hint32.priority = 2
        #hint32.usefulness = 1000

        #hint11.save()
        #hint12.save()
        hint21.save()
        hint22.save()
        #hint31.save()
        #hint32.save()

        errorSpecificFeedback1 = ErrorSpecificFeedbacks(problem=problemFK, edge=e2)
        errorSpecificFeedback1.text="Error Specific feedback 1"
        errorSpecificFeedback1.dateAdded = datetime.now()
        errorSpecificFeedback1.priority = 1
        errorSpecificFeedback1.usefulness = 1000
        errorSpecificFeedback1.save()

        errorSpecificFeedback2 = ErrorSpecificFeedbacks(problem=problemFK, edge=e2)
        errorSpecificFeedback2.text="Error Specific Feedback 2"
        errorSpecificFeedback2.dateAdded = datetime.now()
        errorSpecificFeedback2.priority = 2
        errorSpecificFeedback2.usefulness = 1000
        errorSpecificFeedback2.save()

        explanations1 = Explanation(problem=problemFK, edge=e2)
        explanations1.text="Explanation feedback 1"
        explanations1.dateAdded = datetime.now()
        explanations1.priority = 1
        explanations1.usefulness = 1000
        explanations1.save()

        explanations2 = Explanation(problem=problemFK, edge=e2)
        explanations2.text="Explanation Feedback 2"
        explanations2.dateAdded = datetime.now()
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
        n2 = Node(title="Option 1", correctness=1, fixedValue=1, problem=problemFK, dateAdded=datetime.now())
        n3 = Node(title="Option 2", correctness=1, fixedValue=1, problem=problemFK, dateAdded=datetime.now())
        n4 = Node(title="_end_", correctness=1, fixedValue=1, alreadyCalculatedPos = 1, problem=problemFK, dateAdded=datetime.now())

        n1.save()
        n2.save()
        n3.save()
        n4.save()
        
        nodeList = [n1, n2, n3, n4]

        edgeList = self.createInitialEdgeData(nodeList, problemFK)
        self.createInitialResolutionData(nodeList, edgeList, problemFK)
        

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
    def submit_data(self,data,suffix=''):
        loadedProblem = Problem.objects.get(id=self.problemId)

        self.problemTitle = data.get('problemTitle')
        self.problemDescription = data.get('problemDescription')
        self.problemCorrectRadioAnswer = data.get('problemCorrectRadioAnswer')
        loadedProblem.multipleChoiceProblem = data.get('multipleChoiceProblem')
        self.problemAnswer1 = data.get('problemAnswer1')
        self.problemAnswer2 = data.get('problemAnswer2')
        self.problemAnswer3 = data.get('problemAnswer3')
        self.problemAnswer4 = data.get('problemAnswer4')
        self.problemAnswer5 = data.get('problemAnswer5')
        self.problemSubject = data.get('problemSubject')
        self.problemTags = ast.literal_eval(data.get('problemTags'))
        loadedProblem.dateModified=datetime.now()

        loadedProblem.save()

        return {'result':'success'}

    @XBlock.json_handler
    def recommend_feedback(self,data,suffix=''):
        loadedProblem = Problem.objects.get(id=self.problemId)
        loadedHint = Hint.objects.get(problem = loadedProblem, id=data.get("existingHintId"))

        if data.get("message") == "s":
            loadedHint.usefulness += receivedHintUsefulnessAmount
        else:
            loadedHint.usefulness -= receivedHintUsefulnessAmount
        
        loadedHint.save()

        return {'result':'success'}

    @XBlock.json_handler
    def send_feedback(self,data,suffix=''):
        loadedProblem = Problem.objects.get(id=self.problemId)
        
        feedbackType = data.get("type")
        if feedbackType == "minimalState" or feedbackType == "doubtNode":
            loadedNode = Node.objects.get(problem=loadedProblem, title=data.get("node"))
        else:
            loadedEdge = Edge.objects.get(problem=loadedProblem, sourceNode__title=data.get("nodeFrom"), destNode__title=data.get("nodeTo"))

        if feedbackType == 'minimalStep':
            if data.get("message") == "s":
                loadedEdge.correctness += receivedMinimalFeedbackAmount
            else:
                loadedEdge.correctness -= receivedMinimalFeedbackAmount
            loadedEdge.save()
        elif feedbackType == 'minimalState':
            if data.get("message") == "s":
                loadedNode.correctness += receivedMinimalFeedbackAmount
            else:
                loadedNode.correctness -= receivedMinimalFeedbackAmount
            loadedNode.save()
        elif feedbackType == 'errorSpecific':
            errorSpecificFeedback = ErrorSpecificFeedbacks(problem=loadedProblem, edge=loadedEdge)
            errorSpecificFeedback.text=data.get("message")
            errorSpecificFeedback.dateAdded = datetime.now()
            errorSpecificFeedback.priority = 1
            errorSpecificFeedback.usefulness = 0
            errorSpecificFeedback.save()
        elif feedbackType == 'explanation':
            explanation = Explanation(problem=loadedProblem, edge=loadedEdge)
            explanation.text=data.get("message")
            explanation.dateAdded = datetime.now()
            explanation.priority = 1
            explanation.usefulness = 0
            explanation.save()
        elif feedbackType == 'doubtStep':
            print("doubtStep")
        elif feedbackType == 'doubtNode':
            loadedDoubt = Doubt.objects.get(problem=loadedProblem, id=data.get("doubtId"))
            answer = Answer(problem=loadedProblem, edge=loadedEdge, doubt=loadedDoubt)
            answer.dateAdded = datetime.now()
            answer.text = data.get("message")
            answer.usefulness = 0
            answer.save()

        return {'result':'success'}

    #Sistema que mostra quais dicas até o primeiro passo errado
    #Aqui ele pega a primeira resposta errada, e coloca a dica da que mais se assemelha
    #Feedback mínimo, sem dicas
    def getFirstIncorrectAnswer (self, answerArray):

        lastElement = "_start_"
        wrongElement = None
        wrongStep = 0

        loadedProblem = Problem.objects.get(id=self.problemId)
        endNode = Node.objects.get(problem=loadedProblem, title="_end_")
        #Ver até onde está certo
        for step in answerArray:
            lastNode = Node.objects.get(problem=loadedProblem, title=lastElement)
            currentNode = Node.objects.filter(problem=loadedProblem, title=step)

            if  currentNode.exists() and Edge.objects.filter(problem=loadedProblem, sourceNode = currentNode.first(), destNode=endNode).exists():
                break

            if currentNode.exists() and Edge.objects.filter(problem=loadedProblem, sourceNode = lastNode, destNode=currentNode.first()).exists() and currentNode.first().correctness >= correctState[0]:
                lastElement = step
                wrongStep = wrongStep + 1
            else:
                wrongElement = step
                break

        #Se null, então tudo certo
        if (wrongElement == None):
            return {"wrongElement": wrongElement, "lastCorrectElement": lastElement, "correctElementLine": wrongStep}

        availableCorrectSteps = []
        lastNode = Node.objects.get(problem=loadedProblem, title=lastElement)
        nextElements = Edge.objects.filter(problem=loadedProblem, sourceNode = lastNode)
        for element in nextElements:
            if element.destNode.correctness >= correctState[0]:
                availableCorrectSteps.append(element.destNode.title)
        return {"wrongElement": wrongElement, "availableCorrectSteps": availableCorrectSteps, "wrongElementLine": wrongStep, "lastCorrectElement": lastElement}



    @XBlock.json_handler
    def generate_graph(self, data, suffix=''):
        return {"teste": getJsonFromProblemGraph(self.problemId)}

    #COMO MOSTRAR SE UMA REPSOSTAS ESTÁ CORRETA?
    #TALVEZ COLOCAR ALGUMA COISA NOA TELA QUE MOSTRE QUE A LINHA ESTÁ CORRETA
    #Sistema que mostra a dica até o primeiro passo que estiver errado
    #Mostra um next-Step hint, mas desse passo que está errado (como colocar ele certo)
    #Rodar após cada enter? Faria sentido
    @XBlock.json_handler
    def get_hint_for_last_step(self, data, suffix=''):


        answerArray = data['userAnswer'].split('\n')

        if '' in answerArray:
            answerArray =  list(filter(lambda value: value != '', answerArray))

        possibleIncorrectAnswer = self.getFirstIncorrectAnswer(answerArray)
        
        wrongElement = possibleIncorrectAnswer.get("wrongElement")

        hintText = self.problemDefaultHint
        hintId = 0
        hintList = None

        loadedProblem = Problem.objects.get(id=self.problemId)

        #Precisa dessa parte mesmo? Parece ser igual abaixo
        minValue = float('inf')
        nextCorrectStep = None
        if  (wrongElement != None):
            possibleSteps = possibleIncorrectAnswer.get("availableCorrectSteps")
            for step in possibleSteps:
                actualValue = levenshteinDistance(wrongElement, step)
                if(actualValue < minValue):
                    minValue = actualValue
                    nextCorrectStep = step

            edgeForStep = Edge.objects.filter(problem=loadedProblem, sourceNode__title=possibleIncorrectAnswer.get("lastCorrectElement"), destNode__title=nextCorrectStep)
            if edgeForStep.exists():
                hintForStep = Hint.objects.filter(problem=loadedProblem, edge=edgeForStep.first()).order_by("-usefulness", "priority")
                if hintForStep.exists():
                    hintList = []
                    hintIdList = []
                    for hint in hintForStep:
                        hintList.append(hint.text)
                        hintIdList.append(hint.id)
                else:
                    if possibleIncorrectAnswer.get("lastCorrectElement") == "_start_":
                        hintList = [self.problemInitialHint]
                        hintIdList = [0]
                    else:
                        hintList = [self.problemDefaultHint]
                        hintIdList = [0]
            else:
                if possibleIncorrectAnswer.get("lastCorrectElement") == "_start_":
                    hintList = [self.problemInitialHint]
                    hintIdList = [0]
                else:
                    hintList = [self.problemDefaultHint]
                    hintIdList = [0]


        try:
            #Então está tudo certo, pode dar um OK e seguir em frente
            #MO passo está correto, mas agora é momento de mostrar a dica para o próximo passo.
            if (wrongElement == None):
                loadedProblem = Problem.objects.get(id=self.problemId)
                nextPossibleElementsEdges = Edge.objects.filter(problem=loadedProblem, sourceNode__title=possibleIncorrectAnswer.get("lastCorrectElement"))

                nextElement = None
                for edge in nextPossibleElementsEdges:
                    element = edge.destNode.title
                    loadedProblem = Problem.objects.get(id=self.problemId)
                    nodeElement = Node.objects.get(problem=loadedProblem, title=element)
                    if nodeElement.correctness >= correctState[0]:
                        nextElement = element
                #Verificar se é o último passo, se for, sempre dar a dica padrão?
                if (nextElement == "_end_"):
                    hintText = self.problemDefaultHint
                    hintId = 0
                else:

                    edgeForStep = Edge.objects.filter(problem=loadedProblem, sourceNode__title=possibleIncorrectAnswer.get("lastCorrectElement"), destNode__title=nextCorrectStep)
                    if edgeForStep.exists():
                        hintForStep = Hint.objects.filter(problem=loadedProblem, edge=edgeForStep.first()).order_by("-usefulness", "priority")
                        if hintForStep.exists():
                            hintList = []
                            hintIdList = []
                            for hint in hintForStep:
                                hintList.append(hint.text)
                                hintIdList.append(hint.id)
                        else:
                            hintList = [self.problemDefaultHint]
                            hintIdList = [0]
                    else:
                        hintList = [self.problemDefaultHint]
                        hintIdList = [0]

                    if (self.lastWrongElement != str((possibleIncorrectAnswer.get("lastCorrectElement"), nextElement))):
                        self.lastWrongElement = str((possibleIncorrectAnswer.get("lastCorrectElement"), nextElement))
                        self.lastWrongElementCount = 1
                        hintText = hintList[0]
                        hintId = hintIdList[0]
                    elif (self.lastWrongElementCount < len(hintList)):
                        hintText = hintList[self.lastWrongElementCount]
                        hintId = hintIdList[self.lastWrongElementCount]
                        self.lastWrongElementCount = self.lastWrongElementCount + 1
                    else:
                        hintText = hintList[-1]
                        hintId = hintIdList[-1]
                
                return {"status": "OK", "hint": hintText, "hintId": hintId, "lastCorrectElement": possibleIncorrectAnswer.get("lastCorrectElement")}
            else:
                wrongStepCount = possibleIncorrectAnswer.get("correctElementLine")
                if (wrongStepCount == 0):
                    hintText = self.problemInitialHint
                    hintId = 0
                elif (str((possibleIncorrectAnswer.get("lastCorrectElement"), nextCorrectStep)) != self.lastWrongElement):
                    self.lastWrongElement = str((possibleIncorrectAnswer.get("lastCorrectElement"), nextCorrectStep))
                    self.lastWrongElementCount = 1
                    hintText = hintList[0]
                    hintId = hintIdList[0]
                elif (self.lastWrongElementCount < len(hintList)):
                    hintText = hintList[self.lastWrongElementCount]
                    hintId = hintIdList[self.lastWrongElementCount]
                    self.lastWrongElementCount = self.lastWrongElementCount + 1
                else:
                    hintText = hintList[-1]
                    hintId = hintIdList[-1]
        except IndexError:
            hintText = self.problemDefaultHint
            hintId = 0

        return {"status": "NOK", "hint": hintText, "wrongElement": wrongElement, "hintId": hintId, "wrongStepCount": wrongStepCount}

    #Envia a resposta final
    @XBlock.json_handler
    def send_answer(self, data, suffix=''):

        loadedProblem = Problem.objects.get(id=self.problemId)
        #Inicialização e coleta dos dados inicial
        answerArray = data['answer'].split('\n')

        if '' in answerArray:
            answerArray =  list(filter(lambda value: value != '', answerArray))

        self.answerSteps = answerArray

        if loadedProblem.multipleChoiceProblem == 1 and 'radioAnswer' not in data :
            return {"error": "Nenhuma opções de resposta foi selecionada!"}

        if loadedProblem.multipleChoiceProblem == 1:
            self.answerRadio = data['radioAnswer']

        isStepsCorrect = False

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

            lastNode = Node.objects.filter(problem=loadedProblem, title=lastElement)
            currentNode = Node.objects.filter(problem=loadedProblem, title=step)

            if not lastNode.exists():
                n1 = Node(title=lastElement, problem=loadedProblem, dateAdded=datetime.now())
                n1.save()
            else:
                n1 = lastNode.first()

            if lastNode.exists() and not currentNode.exists():
                n2 = Node(title=step, problem=loadedProblem, dateAdded=datetime.now())
                n2.save()
            else:
                n2 = currentNode.first()

            
            currentEdge = Edge.objects.filter(problem=loadedProblem, sourceNode = n1, destNode = n2)
            if not currentEdge.exists():
                e1 = Edge(sourceNode = n1, destNode = n2, problem=loadedProblem, dateAdded=datetime.now())
                e1.save()


            self.studentResolutionsSteps.append(str((lastElement, step)))
            lastElement = step

        #Adicionar o caso do últio elemento com o _end_
        finalElement = '_end_'

        currentNode = Node.objects.get(problem=loadedProblem, title=lastElement)
        edgeList = Edge.objects.filter(problem=loadedProblem, sourceNode=currentNode, destNode=endNode)

        if not edgeList.exists():
            e1 = Edge(sourceNode = currentNode, destNode = endNode, problem=loadedProblem, dateAdded=datetime.now())
            e1.save()

        self.studentResolutionsSteps.append(str((lastElement, finalElement)))


        lastElement = '_start_'
        #Verifica se a resposta está correta
        for step in answerArray:
            #Substitui o que existe na resposta do aluno pelos estados equivalentes cadastrados
            if (step in self.problemEquivalentStates):
                step = self.problemEquivalentStates[step]

            lastNode = Node.objects.get(problem=loadedProblem, title=lastElement)
            currentNode = Node.objects.get(problem=loadedProblem, title=step)
            edgeList = Edge.objects.filter(problem=loadedProblem, sourceNode=lastNode, destNode=currentNode)

            if (edgeList.exists() and edgeList[0].correctness >= validStep[0] and lastNode.correctness >= correctState[0] and currentNode.correctness >= correctState[0]):
                endNodes = Edge.objects.filter(problem=loadedProblem, sourceNode=currentNode, destNode=endNode)
                if  (endNodes.exists()):
                    isStepsCorrect = True
                    break
                else:
                    lastElement = step
                    currentStep = currentStep + 1
                    continue
            else:
                wrongElement = step
                break

        if loadedProblem.multipleChoiceProblem == 1:
            isAnswerCorrect = isStepsCorrect and self.answerRadio == self.problemCorrectRadioAnswer
        else:
            isAnswerCorrect = isStepsCorrect

        minimal = self.getMinimalFeedbackFromStudentResolution(answerArray)
        minimalSteps = []
        minimalStates = []
        for model in minimal:
            if isinstance(model, Edge):
                minimalSteps.append(model.sourceNode.title)
                minimalSteps.append(model.destNode.title)
            else:
                minimalStates.append(model.title)

        errorSpecific = self.getErrorSpecificFeedbackFromProblemGraph(answerArray)
        errorSpecificSteps = []
        for errorSpecificStep in errorSpecific:
            errorSpecificSteps.append(errorSpecificStep.sourceNode.title)
            errorSpecificSteps.append(errorSpecificStep.destNode.title)

        explanation = self.getExplanationsAndHintsFromProblemGraph(answerArray)
        explanationSteps = []
        for explanationStep in explanation:
            explanationSteps.append(explanationStep.sourceNode.title)
            explanationSteps.append(explanationStep.destNode.title)

        doubts = self.getDoubtsFromProblemGraph()
        doubtsStepReturn = []
        doubtsNodeReturn = []
        for model in doubts:
            if isinstance(model, Edge):
                edgeDoubt = {"message": model.text, "source": model.edge.sourceNode.title, "dest": model.edge.destNode.title, "doubtId": model.id}
                doubtsStepReturn.append(edgeDoubt)
            else:
                nodeDoubt = {"message": model.text, "node": model.node.title, "doubtId": model.id}
                doubtsNodeReturn.append(nodeDoubt)

        #Fim da parte do updateCG

        #self.alreadyAnswered = True

        self.calculateValidityAndCorrectness(answerArray)

        return {"message": "Resposta enviada com sucesso!", "minimalStep": minimalSteps, "minimalState": minimalStates, "errorSpecific": errorSpecificSteps, "explanation": explanationSteps, "doubtsSteps": doubtsStepReturn, "doubtsNodes": doubtsNodeReturn, "answerArray": answerArray}

    def getMinimalFeedbackFromStudentResolution(self, resolution):
        askInfoSteps = []
        askInfoStates = []
        loadedProblem = Problem.objects.get(id=self.problemId)
        previousStateName = "_start_"
        nextStateName = None
        for index, stateName in enumerate(resolution):
            if index + 1 < len(resolution):
                nextStateName = resolution[index + 1]
            else:
                nextStateName = "_end_"

            if previousStateName != "_start_":
                inforSteps1 = Edge.objects.filter(problem=loadedProblem, sourceNode__title = previousStateName).exclude(destNode__title=stateName).exclude(destNode__title = "_end_").exclude(sourceNode__title = "_start_")
                for step in inforSteps1:
                    if step not in askInfoSteps:
                        askInfoSteps.append(step)
                    if step.sourceNode.title not in resolution and step.sourceNode not in askInfoStates:
                        askInfoSteps.append(step.sourceNode)
                    if step.destNode.title not in resolution and step.sourceNode not in askInfoStates:
                        askInfoSteps.append(step.destNode)
                inforSteps2 = Edge.objects.filter(problem=loadedProblem, destNode__title=stateName).exclude(sourceNode__title = previousStateName).exclude(destNode__title = "_end_").exclude(sourceNode__title = "_start_")
                for step in inforSteps2:
                    if step not in askInfoSteps:
                        askInfoSteps.append(step)
                    if step.sourceNode.title not in resolution and step.sourceNode not in askInfoStates:
                        askInfoSteps.append(step.sourceNode)
                    if step.destNode.title not in resolution and step.sourceNode not in askInfoStates:
                        askInfoSteps.append(step.destNode)

                #Como obter outros estados no mesmo nivel? Podemos fazer buscando por resolutions, mas ficaria pesado
                #inforSteps3 = Edge.objects.filter(problem=loadedProblem).exclude(sourceNode__title = previousStateName, destNode__title=stateName).exclude(destNode__title = "_end_").exclude(sourceNode__title = "_start_")
                #for step in inforSteps3:
                #    if step not in askInfoSteps:
                #        askInfoSteps.append(step)
            
            if nextStateName != "_end_":
                inforSteps4 = Edge.objects.filter(problem=loadedProblem, destNode__title = nextStateName).exclude(sourceNode__title = stateName).exclude(destNode__title = "_end_").exclude(sourceNode__title = "_start_")
                for step in inforSteps4:
                    if step not in askInfoSteps:
                        askInfoSteps.append(step)
                    if step.sourceNode.title not in resolution and step.sourceNode not in askInfoSteps:
                        askInfoSteps.append(step.sourceNode)
                    if step.destNode.title not in resolution and step.destNode not in askInfoSteps:
                        askInfoSteps.append(step.destNode)
                inforSteps5 = Edge.objects.filter(problem=loadedProblem, sourceNode__title = stateName).exclude(destNode__title = nextStateName).exclude(destNode__title = "_end_").exclude(sourceNode__title = "_start_")
                for step in inforSteps5:
                    if step not in askInfoSteps:
                        askInfoSteps.append(step)
                    if step.sourceNode.title not in resolution and step.sourceNode not in askInfoSteps:
                        askInfoSteps.append(step.sourceNode)
                    if step.destNode.title not in resolution and step.destNode not in askInfoSteps:
                        askInfoSteps.append(step.destNode)
 
                #Como obter outros estados no mesmo nivel? Podemos fazer buscando por resolutions, mas ficaria pesado
                #inforSteps6 = Edge.objects.filter(problem=loadedProblem).exclude(destNode__title = nextStateName, sourceNode__title = stateName).exclude(destNode__title = "_end_").exclude(sourceNode__title = "_start_")
                #for step in inforSteps6:
                #    if step not in askInfoSteps:
                #        askInfoSteps.append(step)

            previousStateName = stateName

        askInfoSteps.sort(key=amorzinhoMinimalFeedback)
        if askInfoSteps is not None and len(askInfoSteps) >= maxMinimumFeedback:
            return askInfoSteps[0:maxMinimumFeedback]
        else:
            return askInfoSteps


    def getErrorSpecificFeedbackFromProblemGraph(self, resolution):
        CFEE = []
        returnList = []
        loadedProblem = Problem.objects.get(id=self.problemId)
        CFEE = Edge.objects.filter(problem=loadedProblem, correctness__lt = possiblyInvalidStep[0], sourceNode__correctness__gte = correctState[0], destNode__correctness__lte = incorrectState[0])
        for stepEE in CFEE:
            sourceNodeTitleEE = stepEE.sourceNode.title 
            if sourceNodeTitleEE in resolution:
                sourceNodeIndexEE = resolution.index(sourceNodeTitleEE)
                if sourceNodeIndexEE < len(resolution) - 1:
                    if resolution[sourceNodeIndexEE + 1] != stepEE.destNode.title:
                        possibleEdge = Edge.objects.filter(problem=loadedProblem, correctness__gte = stronglyValidStep[0], sourceNode__title = sourceNodeTitleEE, destNode__title = resolution[sourceNodeIndexEE + 1], destNode__correctness__gte = correctState[0])
                        if possibleEdge.exists():
                            returnList.append(possibleEdge[0])
        if len(returnList) >= maxErrorSpecificFeedback:
            returnList.sort(key=amorzinhoErrorSpecificFeedback)
            return returnList[0:maxErrorSpecificFeedback]
        else:
            return returnList

    def getExplanationsAndHintsFromProblemGraph(self, resolution):
        CEX = []
        returnList = []
        loadedProblem = Problem.objects.get(id=self.problemId)
        CEX = Edge.objects.filter(problem=loadedProblem, correctness__gt = stronglyValidStep[0], sourceNode__correctness__gte = correctState[0], destNode__correctness__gte = correctState[0])
        for stepEX in CEX:
            sourceNodeTitleEX = stepEX.sourceNode.title 
            if sourceNodeTitleEX in resolution:
                sourceNodeIndexEX = resolution.index(sourceNodeTitleEX)
                if sourceNodeIndexEX < len(resolution) - 1:
                    if resolution[sourceNodeIndexEX + 1] == stepEX.destNode.title:
                        possibleEdge = Edge.objects.filter(problem=loadedProblem, sourceNode__correctness__gte = correctState[0], sourceNode__title = sourceNodeTitleEX, destNode__title = resolution[sourceNodeIndexEX + 1], destNode__correctness__gte = correctState[0])
                        if possibleEdge.exists():
                            returnList.append(possibleEdge[0])
        if len(returnList) >= maxExplanations:
            returnList.sort(key=amorzinhoErrorSpecificFeedback)
            return returnList[0:maxExplanations]
        else:
            return returnList


    def getDoubtsFromProblemGraph(self):
        CDU = []
        allDoubtsWithAnswers = []
        loadedProblem = Problem.objects.get(id=self.problemId)
        allDoubts = Doubt.objects.filter(problem=loadedProblem)
        allAnswers = Answer.objects.filter(problem=loadedProblem)
        for answer in allAnswers:
            if answer.doubt not in allDoubtsWithAnswers:
                allDoubtsWithAnswers.append(answer)
        if len(allDoubts) > 0 and len(allDoubtsWithAnswers) > 0:
            CDU = allDoubts.difference(allDoubtsWithAnswers)

        if len(CDU) > 0:
            CDU.sort(key=amorzinhoTempo)
            return CDU[0:maxDoubts]
        else:
            return CDU

    def corretudeResolucao(self, resolution):
        loadedProblem = Problem.objects.get(id=self.problemId)
        stateIdList = ast.literal_eval(resolution.nodeIdList)
        stateIdAmount = len(stateIdList) - 2
        stepIdList = ast.literal_eval(resolution.edgeIdList)
        stepIdAmount = len(stepIdList) - 2

        stateCorrectness = 0
        stepCorrectness = 0

        for stateId in stateIdList:
            if stateId != stateIdList[0] and stateId != stateIdList[-1]:
                state = Node.objects.get(problem=loadedProblem, id = stateId)
                stateCorrectness = stateCorrectness + self.corretudeEstado(state)

        for stepId in stepIdList:
            if stepId != stepIdList[0] and stepId != stepIdList[-1]:
                step = Edge.objects.get(problem=loadedProblem, id = stepId)
                stepCorrectness = stepCorrectness + self.validadePasso(step)
                
        return (1/(2*stateIdAmount)) * (stateCorrectness) + (1/(2*stepIdAmount)) * (stepCorrectness)
    
    def possuiEstado(self, state, resolution):
        return state.id in ast.literal_eval(resolution.nodeIdList)
    
    def possuiEstadoConjunto(self, state, resolutions):
        sum = 0
        for resolution in resolutions:
            sum = sum + self.possuiEstado(state, resolution)
        
        return sum
    
    def corretudeEstado(self, state):
        loadedProblem = Problem.objects.get(id=self.problemId)
        allResolutions = Resolution.objects.filter(problem=loadedProblem)
        correctResolutions = []
        wrongResolutions = []

        for resolution in allResolutions:
            lastStateId = ast.literal_eval(resolution.nodeIdList)[-2]
            lastState = Node.objects.get(problem=loadedProblem, id=lastStateId)

            if self.problemCorrectRadioAnswer == lastState.title:
                correctResolutions.append(resolution)
            else:
                wrongResolutions.append(resolution)


        correctValue = self.possuiEstadoConjunto(state, correctResolutions)
        incorrectValue = self.possuiEstadoConjunto(state, wrongResolutions)
    
        if correctValue + incorrectValue != 0:
            return (correctValue-incorrectValue)/(correctValue + incorrectValue)
        return 0
    
    def possuiPassoConjunto(self, step, resolutions):
        sum = 0
        for resolution in resolutions:
            sum = sum + self.possuiPasso(step, resolution)
        
        return sum

    def possuiPasso(self, step, resolution):
        return step.id in ast.literal_eval(resolution.edgeIdList)
    
    def validadePasso(self, step):
        loadedProblem = Problem.objects.get(id=self.problemId)
        allResolutions = Resolution.objects.filter(problem=loadedProblem)
        correctResolutions = []
        wrongResolutions = []

        for resolution in allResolutions:
            lastEdgeId = ast.literal_eval(resolution.edgeIdList)[-1]
            lastEdge = Edge.objects.get(problem=loadedProblem, id=lastEdgeId)

            if self.problemCorrectRadioAnswer == lastEdge.sourceNode.title:
                correctResolutions.append(resolution)
            else:
                wrongResolutions.append(resolution)


        correctValue = self.possuiPassoConjunto(step, correctResolutions)
        incorrectValue = self.possuiPassoConjunto(step, wrongResolutions)
    
        if correctValue + incorrectValue != 0:
            return (correctValue-incorrectValue)/(correctValue + incorrectValue)
        return 0

    def calculateValidityAndCorrectness(self, resolution):

        loadedProblem = Problem.objects.get(id=self.problemId)

        nodeArray = []
        edgeArray = []
        lastNodeName = "_start_"
        lastNode = Node.objects.get(problem=loadedProblem, title=lastNodeName)
        nodeArray.append(lastNode.id)
        for node in resolution:
            currentNode = Node.objects.get(problem=loadedProblem, title=node)
            if currentNode.fixedValue == 0:
                currentNode.correctness = self.corretudeEstado(currentNode)
                currentNode.dateAdded = datetime.now()
                currentNode.save()
            nodeArray.append(currentNode.id)
            currentEdge = Edge.objects.get(problem=loadedProblem, sourceNode=lastNode, destNode=currentNode)
            if currentEdge.fixedValue == 0:
                currentEdge.correctness = self.validadePasso(currentEdge)
                currentEdge.dateAdded = datetime.now()
                currentEdge.save()
            edgeArray.append(currentEdge.id)
            lastNode = currentNode

        currentNode = Node.objects.get(problem=loadedProblem, title="_end_")
        nodeArray.append(currentNode.id)
        currentEdge = Edge.objects.get(problem=loadedProblem, sourceNode=lastNode, destNode=currentNode)
        edgeArray.append(currentEdge.id)
        lastNode = currentNode

        r1 = Resolution(nodeIdList = nodeArray, edgeIdList = edgeArray, problem=loadedProblem, correctness=0, dateAdded=datetime.now())
        r1.save()
        r1 = Resolution.objects.get(id = r1.id)
        r1.correctness = self.corretudeResolucao(r1)
        r1.save()



    @XBlock.json_handler
    def initial_data(self, data, suffix=''):
        loadedProblem = Problem.objects.filter(id=self.problemId)
        if not loadedProblem.exists():
            return {"title": self.problemTitle, "description": self.problemDescription, 
            "answer1": self.problemAnswer1, "answer2": self.problemAnswer2, "answer3": self.problemAnswer3, "answer4": self.problemAnswer4, "answer5": self.problemAnswer5,
            "subject": self.problemSubject, "tags": self.problemTags, "alreadyAnswered": str(self.alreadyAnswered)}

        return {"title": self.problemTitle, "description": self.problemDescription, 
        "answer1": self.problemAnswer1, "answer2": self.problemAnswer2, "answer3": self.problemAnswer3, "answer4": self.problemAnswer4, "answer5": self.problemAnswer5,
        "subject": self.problemSubject, "tags": self.problemTags, "alreadyAnswered": str(self.alreadyAnswered), "multipleChoiceProblem": loadedProblem[0].multipleChoiceProblem}


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
