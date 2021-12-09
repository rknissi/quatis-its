from array import array
import json
from re import I
from django.db.models.fields import NOT_PROVIDED
import pkg_resources
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import Integer, Scope, String, Boolean, List, Set, Dict, Float
from django.core.files.storage import default_storage
import ast 
from .studentGraph.models import Problem, Node, Edge, Resolution
from django.utils import timezone
import uuid

#Step information
correctnessMinValue = -1
correctnessMaxValue = 1

#Resolution values
incorrectResolution = [-1, -0.75001]
partiallyIncorrectResolution = [-0.75, -0.00001]
partiallyCorrectResolution = [0, 0.74999]
correctResolution = [0.75, 1]
defaultResolutionValue = 0

#Step values
invalidStep = [-1, -0.80001]
stronglyInvalidStep = [-0.8, -0.40001]
possiblyInvalidStep = [-0.4, -0.00001]
neutralStep = [0, 0]
possiblyValidStep = [0.00001, 0.39999]
stronglyValidStep = [0.4, 0.79999]
validStep = [0.8, 1]
defaultStepValue = 0

#State values
incorrectState = [-1, -0.7]
unknownState = [-0.69999, 0.69999]
correctState = [0.7, 1]
defaultStateValue = 0

#VisualGraphProperties
defaultArrowStroke = "3 "
initialNodeShape = "square"
finalNodeShape = "diamond"
defaultNodeHeight = 20
initialNodeStroke = {"color": "black", "dash": "5 5"}
finalNodeStroke = "1 black"
graphHeightDefaultValue = 60
graphWidthDefaultValue = 0
graphWidthExtraValue = 30
graphNodeMinimumDistance = 30

problemGraphDefault = {'_start_': ['Option 1'], 'Option 1': ["Option 2"], "Option 2": ["_end_"]}
problemGraphNodePositionsDefault = {}  
problemGraphStatesCorrectnessDefault = {'_start_': correctState[1], 'Option 1': correctState[1], 'Option 2': correctState[1]}
problemGraphStepsCorrectnessDefault = {str(('_start_', 'Option 1')): validStep[1], str(('Option 1', 'Option 2')): validStep[1], str(('Option 2', '_end_')): validStep[1]}
allResolutionsDefault = []

problemGraphStates = []
problemGraphSteps = []
problemGraphResolutions = []

#Ainda não salvando nada nessa variável
allResolutionsNew = allResolutionsDefault

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

    hintFromSteps = Dict(
        default={str(('_start_', 'Option 1')): ["Uiaaa", "hahaha"], str(('Option 1', 'Option 2')): ["hint 1", "Hint 2"], str(('X=500-2', 'X=498')): ["Hint feedback 1", "Hint Feedback 2"]}, scope=Scope.content,
        help="For each correct step that the student uses, it will show a specific hint",
    )

    problemDefaultHint = String(
        default="Verifique se a resposta está correta", scope=Scope.content,
        help="If there is no available hint",
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
        frag = Fragment(str(html).format(block=self))
        frag.add_css(self.resource_string("static/css/myxblock.css"))
        frag.add_javascript(self.resource_string("static/js/src/myxblock.js"))

        #Também precisa inicializar
        frag.initialize_js('MyXBlock')
        return frag

    problem_view = student_view

    def studio_view(self,context=None):

        html=self.resource_string("static/html/myxblockEdit.html")

        frag = Fragment(str(html).format(problemTitle=self.problemTitle,problemDescription=self.problemDescription,problemCorrectRadioAnswer=self.problemCorrectRadioAnswer,problemCorrectSteps=self.problemCorrectStates,problemDefaultHint=self.problemDefaultHint,problemAnswer1=self.problemAnswer1,problemAnswer2=self.problemAnswer2,problemAnswer3=self.problemAnswer3,problemAnswer4=self.problemAnswer4,problemAnswer5=self.problemAnswer5,problemSubject=self.problemSubject,problemTags=self.problemTags))
        frag.add_javascript(self.resource_string("static/js/src/myxblockEdit.js"))

        frag.initialize_js('MyXBlockEdit')
        return frag


    def createGraphInitialPositions(self):

        loadedProblem = Problem.objects.get(id=self.problemId)
        createPos = Node.objects.filter(problem=loadedProblem, nodePositionX = -1, nodePositionY = -1)
        
        if createPos:

            nodePosition = 0
            for node in createPos:
                level = 0
                x = 0
                y = 0

                sourceNodesEdges = Edge.objects.filter(problem=loadedProblem, destNode = node)
                initialSourceNodes = sourceNodesEdges

                while sourceNodesEdges.exists():
                    level = level + 1
                    sourceNodesEdges = Edge.objects.filter(problem=loadedProblem, destNode = sourceNodesEdges[0].sourceNode)

                y = (graphHeightDefaultValue + nodePosition) * level
                if initialSourceNodes.exists():
                    x = initialSourceNodes[0].sourceNode.nodePositionX
                else:
                    x = graphWidthDefaultValue

                positions = self.avoidSamePosFromAnotherNode(x, y)
                
                node.nodePositionX = positions.get("x")
                node.nodePositionY = positions.get("y")
                node.save()

                nodePosition = nodePosition + 1

    def avoidSamePosFromAnotherNode(self, x, y):
        loadedProblem = Problem.objects.get(id=self.problemId)
        allNodes = Node.objects.filter(problem=loadedProblem)

        for node in allNodes:
            if (abs(node.nodePositionX - x) <= graphNodeMinimumDistance and abs(node.nodePositionY - y) <= graphNodeMinimumDistance):
                x = x + graphWidthExtraValue
                return self.avoidSamePosFromAnotherNode(x, y)

        return {"x": x, "y": y}


    @XBlock.json_handler
    def get_edge_info(self,data,suffix=''):
        step = str((data.get("from"), data.get("to")))
        errorSpecificFeedbacks = None
        explanations = None
        hints = None

        if step in self.errorSpecificFeedbackFromSteps:
            errorSpecificFeedbacks = self.errorSpecificFeedbackFromSteps[step]
        if step in self.explanationFromSteps:
            explanations = self.explanationFromSteps[step]
        if step in self.hintFromSteps:
            hints = self.hintFromSteps[step]
        
        return {"errorSpecificFeedbacks": errorSpecificFeedbacks, "explanations": explanations, "hints": hints}

    @XBlock.json_handler
    def submit_edge_info(self,data,suffix=''):
        step = str((data.get("from"), data.get("to")))
        self.errorSpecificFeedbackFromSteps[step] = data.get("errorSpecificFeedbacks")
        self.hintFromSteps[step] = data.get("hints")
        self.explanationFromSteps[step] = data.get("explanations")
        
        return {"errorSpecificFeedbacks": self.errorSpecificFeedbackFromSteps, "explanations": self.explanationFromSteps, "hints": self.hintFromSteps}


    @XBlock.json_handler
    def submit_graph_data(self,data,suffix=''):
        #Não está 100%, como que iremos trartar os casos das resoluções já existentes?

        graphData = data.get('graphData')

        loadedProblem = Problem.objects.get(id=self.problemId)

        for node in graphData['nodes']:
            nodeModel = Node.objects.filter(problem=loadedProblem, title=node["id"])
            if not nodeModel.exists():
                n1 = Node(title=node["id"], correctness=float(node["correctness"]), problem=loadedProblem, nodePositionX=node["x"], nodePositionY=node["y"])
                n1.save()
            else:
                nodeModel = Node.objects.get(problem=loadedProblem, title=node["id"])
                nodeModel.correctness = float(node["correctness"])
                nodeModel.nodePositionX = node["x"]
                nodeModel.nodePositionY = node["y"]
                nodeModel.save()
            
            if "stroke" in node:
                if node["stroke"] == finalNodeStroke:
                    edgeModel = Edge.objects.filter(problem=loadedProblem, sourceNode__title=node["id"], destNode__title="_end_")
                    if not edgeModel.exists():
                        fromNode = Node.objects.get(problem=loadedProblem, title=node["id"])
                        toNode = Node.objects.get(problem=loadedProblem, title="_end_")
                        e1 = Edge(sourceNode=fromNode, destNode=toNode, problem=loadedProblem)
                        e1.save()
                elif node["stroke"] == initialNodeStroke and node["id"] != "_start_":
                    edgeModel = Edge.objects.filter(problem=loadedProblem, sourceNode__title="_start_", destNode__title=node["id"])
                    if not edgeModel.exists():
                        fromNode = Node.objects.get(problem=loadedProblem, title="_start_")
                        toNode = Node.objects.get(problem=loadedProblem, title=node["id"])
                        e1 = Edge(sourceNode=fromNode, destNode=toNode, problem=loadedProblem)
                        e1.save()


        for edge in graphData['edges']:
            edgeModel = Edge.objects.filter(problem=loadedProblem, sourceNode__title=edge["from"], destNode__title=edge["to"])
            if not edgeModel.exists():
                fromNode = Node.objects.get(problem=loadedProblem, title=edge["from"])
                toNode = Node.objects.get(problem=loadedProblem, title=edge["to"])
                e1 = Edge(sourceNode=fromNode, destNode=toNode, correctness=float(edge["correctness"]), problem=loadedProblem)
                e1.save()
            else:
                edgeModel = Edge.objects.get(problem=loadedProblem, sourceNode__title=edge["from"], destNode__title=edge["to"])
                edgeModel.correctness = float(edge["correctness"])
                edgeModel.save()

        return {}

    def createInitialEdgeData(self, nodeList, problemFK):
        e1 = Edge(sourceNode=nodeList[0], destNode=nodeList[1], correctness=1, problem=problemFK)
        e2 = Edge(sourceNode=nodeList[1], destNode=nodeList[2], correctness=1, problem=problemFK)
        e3 = Edge(sourceNode=nodeList[2], destNode=nodeList[3], correctness=1, problem=problemFK)

        e1.save()
        e2.save()
        e3.save()

    def createInitialResolutionData(self, nodeList, problemFK):
        idArray = []
        for node in nodeList:
            if node.title != "_start_" and node.title != "_end_":
                idArray.append(node.id)

        r1 = Resolution(nodeIdList=json.dumps(idArray), correctness=1, problem=problemFK)

        r1.save()


    def createInitialNodeData(self, problemFK):
        n1 = Node(title="_start_", correctness=1, problem=problemFK)
        n2 = Node(title="Option 1", correctness=1, problem=problemFK)
        n3 = Node(title="Option 2", correctness=1, problem=problemFK)
        n4 = Node(title="_end_", correctness=1, problem=problemFK)

        n1.save()
        n2.save()
        n3.save()
        n4.save()
        
        nodeList = [n1, n2, n3, n4]

        self.createInitialEdgeData(nodeList, problemFK)
        self.createInitialResolutionData(nodeList, problemFK)
        

    def createInitialData(self):
        if self.problemId == -1:
            p = Problem(graph=json.dumps(problemGraphDefault))
            p.save()
            self.problemId = p.id

            self.createInitialNodeData(p)


    @XBlock.json_handler
    def submit_data(self,data,suffix=''):
        self.problemTitle = data.get('problemTitle')
        self.problemDescription = data.get('problemDescription')
        self.problemCorrectRadioAnswer = data.get('problemCorrectRadioAnswer')
        self.problemCorrectStates = ast.literal_eval(data.get('problemCorrectSteps'))
        self.problemAnswer1 = data.get('problemAnswer1')
        self.problemAnswer2 = data.get('problemAnswer2')
        self.problemAnswer3 = data.get('problemAnswer3')
        self.problemAnswer4 = data.get('problemAnswer4')
        self.problemAnswer5 = data.get('problemAnswer5')
        self.problemSubject = data.get('problemSubject')
        self.problemTags = ast.literal_eval(data.get('problemTags'))

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


    def getJsonFromProblemGraph(self):
        nodeList = []
        edgeList = []
        addedNodes = []
        fixedPos = False

        self.createGraphInitialPositions()

        loadedProblem = Problem.objects.get(id=self.problemId)
        allNodes = Node.objects.filter(problem=loadedProblem)

        for source in allNodes:
            edgeObjList = Edge.objects.filter(problem=loadedProblem, sourceNode = source)
            for edgeObj in edgeObjList:
                dest = edgeObj.destNode
                if source.title == "_start_":
                    nodeColor = self.getNodeColor(source)

                    if source not in addedNodes:
                        node = {"id": source.title, "height": defaultNodeHeight, "fill": nodeColor, "shape": initialNodeShape ,"stroke": initialNodeStroke, "correctness": source.correctness}
                        if source.nodePositionX != -1 and source.nodePositionY != -1:
                            node["x"] = source.nodePositionX
                            node["y"] = source.nodePositionY
                            fixedPos = True
                        nodeList.append(node)
                        addedNodes.append(source)

                    nodeColor = self.getNodeColor(dest)
                    if dest not in addedNodes:
                        node = {"id": dest.title, "height": defaultNodeHeight, "fill": nodeColor, "correctness": dest.correctness}
                        if dest.nodePositionX != -1 and dest.nodePositionY != -1:
                            node["x"] = dest.nodePositionX
                            node["y"] = dest.nodePositionY
                            fixedPos = True
                        nodeList.append(node)
                        addedNodes.append(dest)
                    else: 
                        pos = addedNodes.index(dest)
                        nodeList[pos] = {"id": dest.title, "height": defaultNodeHeight, "fill": nodeColor, "correctness": dest.correctness}

                    edge = {"from": source.title, "to": dest.title, "stroke": defaultArrowStroke + self.getEdgeColor(edgeObj), "correctness": edgeObj.correctness}
                    edgeList.append(edge)

                    
                elif dest.title == "_end_":
                    nodeColor = self.getNodeColor(source)
                    if source not in addedNodes:
                        node = {"id": source.title, "height": defaultNodeHeight, "shape": finalNodeShape ,"fill": nodeColor, "stroke": finalNodeStroke, "correctness": source.correctness}
                        if source.nodePositionX != -1 and source.nodePositionY != -1:
                            node["x"] = source.nodePositionX
                            node["y"] = source.nodePositionY
                            fixedPos = True
                        nodeList.append(node)
                        addedNodes.append(source)
                    else:
                        pos = addedNodes.index(source)
                        node = {"id": source.title, "height": defaultNodeHeight, "shape": finalNodeShape, "fill": nodeColor, "stroke": finalNodeStroke, "correctness": source.correctness}
                        if source.nodePositionX != -1 and source.nodePositionY != -1:
                            node["x"] = source.nodePositionX
                            node["y"] = source.nodePositionY
                            fixedPos = True
                        nodeList[pos] = node
                else:
                    if source not in addedNodes:
                        nodeColor = self.getNodeColor(source)
                        node = {"id": source.title, "height": defaultNodeHeight, "fill": nodeColor, "correctness": source.correctness}
                        if source.nodePositionX != -1 and source.nodePositionY != -1:
                            node["x"] = source.nodePositionX
                            node["y"] = source.nodePositionY
                            fixedPos = True
                        nodeList.append(node)
                        addedNodes.append(source)
                    if dest not in addedNodes:
                        nodeColor = self.getNodeColor(dest)
                        node = {"id": dest.title, "height": defaultNodeHeight, "fill": nodeColor, "correctness": dest.correctness}
                        if dest.nodePositionX != -1 and dest.nodePositionY != -1:
                            node["x"] = dest.nodePositionX
                            node["y"] = dest.nodePositionY
                            fixedPos = True
                        nodeList.append(node)
                        addedNodes.append(dest)
                    
                    edge = {"from": source.title, "to": dest.title, "stroke": defaultArrowStroke + self.getEdgeColor(edgeObj), "correctness": edgeObj.correctness}
                    edgeList.append(edge)

        return {"nodes": nodeList, "edges": edgeList, "fixedPos": fixedPos}
                
    def getEdgeColor(self, edge):

        edgeValue = edge.correctness
        if edgeValue >= invalidStep[0] and edgeValue <= invalidStep[1]:
            return "#FC0D1B"
        if edgeValue >= stronglyInvalidStep[0] and edgeValue <= stronglyInvalidStep[1]:
            return "#FC644D"
        if edgeValue >= possiblyInvalidStep[0] and edgeValue <= possiblyInvalidStep[1]:
            return "#FDA07E"
        if edgeValue >= neutralStep[0] and edgeValue <= neutralStep[1]:
            return "#FED530"
        if edgeValue >= possiblyValidStep[0] and edgeValue <= possiblyValidStep[1]:
            return  "#807F17"
        if edgeValue >= stronglyValidStep[0] and edgeValue <= stronglyValidStep[1]:
            return  "#9BCB40"
        if edgeValue >= validStep[0] and edgeValue <= validStep[1]:
            return "#81FA30"

    def getNodeColor(self, node):

        nodeValue = node.correctness
        if nodeValue >= incorrectState[0] and nodeValue <= incorrectState[1]:
            return "#EE8182"
        if nodeValue >= unknownState[0] and nodeValue <= unknownState[1]:
            return "#F0E591"
        if nodeValue >= correctState[0] and nodeValue <= correctState[1]:
            return "#2AFD84"

    @XBlock.json_handler
    def generate_graph(self, data, suffix=''):
        self.createInitialData()
        return {"teste": self.getJsonFromProblemGraph()}

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
        hintList = None

        minValue = float('inf')
        nextCorrectStep = None
        if  (wrongElement != None):
            possibleSteps = possibleIncorrectAnswer.get("availableCorrectSteps")
            for step in possibleSteps:
                actualValue = levenshteinDistance(wrongElement, step)
                if(actualValue < minValue):
                    minValue = actualValue
                    nextCorrectStep = step

            if (str((possibleIncorrectAnswer.get("lastCorrectElement"), nextCorrectStep)) in self.hintFromSteps):
                hintList = self.hintFromSteps[str((possibleIncorrectAnswer.get("lastCorrectElement"), nextCorrectStep))]
            else:
                hintList = [self.problemDefaultHint]

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
                else:
                    if (str((possibleIncorrectAnswer.get("lastCorrectElement"), nextElement)) in self.hintFromSteps):
                        hintList = self.hintFromSteps[str((possibleIncorrectAnswer.get("lastCorrectElement"), nextElement))]
                    else:
                        hintList = [self.problemDefaultHint]

                    if (self.lastWrongElement != str((possibleIncorrectAnswer.get("lastCorrectElement"), nextElement))):
                        self.lastWrongElement = str((possibleIncorrectAnswer.get("lastCorrectElement"), nextElement))
                        self.lastWrongElementCount = 1
                        hintText = hintList[0]
                    elif (self.lastWrongElementCount < len(hintList)):
                        hintText = hintList[self.lastWrongElementCount]
                        self.lastWrongElementCount = self.lastWrongElementCount + 1
                    else:
                        hintText = hintList[-1]
                
                return {"status": "OK", "hint": hintText, "lastCorrectElement": possibleIncorrectAnswer.get("lastCorrectElement")}
            else:
                if (str((possibleIncorrectAnswer.get("lastCorrectElement"), nextCorrectStep)) != self.lastWrongElement):
                    self.lastWrongElement = str((possibleIncorrectAnswer.get("lastCorrectElement"), nextCorrectStep))
                    self.lastWrongElementCount = 1
                    hintText = hintList[0]
                elif (self.lastWrongElementCount < len(hintList)):
                    hintText = hintList[self.lastWrongElementCount]
                    self.lastWrongElementCount = self.lastWrongElementCount + 1
                else:
                    hintText = hintList[-1]
        except IndexError:
            hintText = self.problemDefaultHint

        return {"status": "NOK", "hint": hintText, "wrongElement": wrongElement}

    #Envia a resposta final
    @XBlock.json_handler
    def send_answer(self, data, suffix=''):

        #Inicialização e coleta dos dados inicial
        answerArray = data['answer'].split('\n')

        if '' in answerArray:
            answerArray =  list(filter(lambda value: value != '', answerArray))

        self.answerSteps = answerArray

        if('radioAnswer' not in data) :
            return {"error": "Nenhuma opções de resposta foi selecionada!"}

        self.answerRadio = data['radioAnswer']
        isStepsCorrect = False

        currentStep = 0

        wrongElement = None

        self.studentResolutionsStates = answerArray
        self.studentResolutionsSteps = list()

        loadedProblem = Problem.objects.get(id=self.problemId)
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
                n1 = Node(title=lastElement, problem=loadedProblem)
                n1.save()

            if lastNode.exists() and not currentNode.exists():
                n2 = Node(title=step, problem=loadedProblem)
                n2.save()

                e1 = Edge(sourceNode = lastNode.first(), destNode = n2, problem=loadedProblem)
                e1.save()


            self.studentResolutionsSteps.append(str((lastElement, step)))
            lastElement = step

        #Adicionar o caso do últio elemento com o _end_
        finalElement = '_end_'

        currentNode = Node.objects.get(problem=loadedProblem, title=lastElement)
        edgeList = Edge.objects.filter(problem=loadedProblem, sourceNode=currentNode, destNode=endNode)

        if not edgeList.exists():
            e1 = Edge(sourceNode = currentNode, destNode = endNode, problem=loadedProblem)
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

            if (edgeList.exists() and currentNode.correctness >= correctState[0]):
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

        isAnswerCorrect = isStepsCorrect and self.answerRadio == self.problemCorrectRadioAnswer


        #Fim da parte do updateCG

        #self.alreadyAnswered = True

        self.calculateValidityAndCorrectness(answerArray)

        if isAnswerCorrect:
            return {"answer": "Correto!"}
        else:
            return {"answer": "Incorreto!"}

    def getExplanationOrHintStepsFromProblemGraph(self):

        loadedProblem = Problem.objects.get(id=self.problemId)
        allNodes = Node.objects.filter(problem=loadedProblem)

        steps = {}
        for sourceNode in allNodes:
            nodeEdges = Edge.objects.filter(problem=loadedProblem, sourceNode=sourceNode)
            for destNode in nodeEdges:
                step = Edge.objects.get(problem=loadedProblem, sourceNode=sourceNode, destNode=destNode)
                if step.correctness >= stronglyValidStep[0]:
                    if sourceNode.correctness >= correctState[0] and endNode.correctness >= correctState[0]:
                        if sourceNode.title in steps:
                            steps[sourceNode.title].append(destNode.title)
                        else:
                            steps[sourceNode.title] = [destNode.title]
        return steps    

    def getHintStepFromStudentResolution(self, studentStates):
        chosenHintStep = None
        chosenHintValue = None

        hintSteps = self.getExplanationOrHintStepsFromProblemGraph()

        for i in range(len(studentStates) - 1):
            for hintStepFromGraph in hintSteps:
                if studentStates[i] == hintStepFromGraph and problemGraphStatesCorrectness[studentStates[i]] >= correctState[0]:
                    for destinyHintStep in hintSteps[hintStepFromGraph]:
                        if studentStates[i+1] == destinyHintStep and problemGraphStatesCorrectness[studentStates[i+1]] >= correctState[0]:

                            hintStep = str((hintStepFromGraph, destinyHintStep))
                            if chosenHintStep == None:
                                chosenHintStep = hintStep
                                chosenHintValue = problemGraphStepsCorrectness[hintStep]
                            else:
                                if hintStep in self.hintFromSteps:
                                    newHintFeedbacks = self.hintFromSteps[hintStep]
                                else:
                                    newHintFeedbacks = 0

                                if chosenHintStep in self.explanationFromSteps:
                                    chosenHintStepFeedbacks = self.explanationFromSteps[chosenHintStep]
                                else:
                                    chosenHintstepFeedbacks = 0

                                if chosenHintValue < problemGraphStepsCorrectness[hintStep] or chosenHintStepFeedbacks < newHintFeedbacks:
                                    chosenHintStep = hintStep
                                    chosenHintValue = problemGraphStepsCorrectness[hintStep]
        return chosenHintStep

    def getExplanationStepsFromStudentResolution(self, studentStates, amount):
        chosenExplanationSteps = {}
        explanationSteps = self.getExplanationOrHintStepsFromProblemGraph()

        for i in range(len(studentStates) - 1):
            for explanationStep in explanationSteps:
                if studentStates[i] == explanationStep and problemGraphStatesCorrectness[studentStates[i]] >= correctState[0]:
                    for destinyExplanationStep in explanationSteps[explanationStep]:
                        if studentStates[i+1] == destinyExplanationStep and problemGraphStatesCorrectness[studentStates[i+1]] >= correctState[0]:

                            chosenExplanationStep = str((explanationStep, destinyExplanationStep))
                            if len(chosenExplanationSteps) < amount:
                                chosenExplanationSteps[chosenExplanationStep] = problemGraphStepsCorrectness[chosenExplanationStep]
                            else:
                                stepsToBeRemoved = []
                                stepsToBeAdded = {}
                                for step in chosenExplanationSteps:
                                    if len(chosenExplanationSteps) - len(stepsToBeRemoved) >= amount:
                                        if step in self.explanationFromSteps:
                                            stepFeedbacks = self.explanationFromSteps[step]
                                        else:
                                            stepFeedbacks = 0

                                        if chosenExplanationStep in self.explanationFromSteps:
                                            chosenExplanationStepFeedbacks = self.explanationFromSteps[chosenExplanationStep]
                                        else:
                                            chosenExplanationStepFeedbacks = 0

                                        if chosenExplanationSteps[step] < problemGraphStepsCorrectness[chosenExplanationStep] or stepFeedbacks < chosenExplanationStepFeedbacks:
                                            stepsToBeRemoved.append(step)
                                            stepsToBeAdded[chosenExplanationStep] = problemGraphStepsCorrectness[chosenExplanationStep]

                                for step in stepsToBeRemoved:
                                    chosenExplanationSteps.pop(step)

                                for step in stepsToBeAdded:
                                    chosenExplanationSteps[step] = stepsToBeAdded[step]

        return chosenExplanationSteps    
    
    def getErrorSpecificFeedbackStepsFromProblemGraph(self):
        steps = {}
        for i in problemGraph:
            for j in problemGraph[i]:
                if problemGraphStepsCorrectness[str((i, j))] < stronglyInvalidStep[1]:
                    if problemGraphStatesCorrectness[i] > correctState[0] and problemGraphStatesCorrectness[j] < incorrectState[1]:
                        if i in steps:
                            steps[i].append(j)
                        else:
                            steps[i] = [j]
        return steps    

    #Inicio igual, mas o fim não
    def getErrorSpecificFeedbackStepsFromStudentResolution(self, studentStates, amount):
        usefulRelatedSteps = {}
        errorSpecificFeedbackSteps = self.getErrorSpecificFeedbackStepsFromGraph()

        for i in range(len(studentStates) - 1):
            for errorSpecificFeedbackSourceState in errorSpecificFeedbackSteps:
                if studentStates[i] == errorSpecificFeedbackSourceState:
                    for errorSpecificFeedbackDestinyState in errorSpecificFeedbackSteps[errorSpecificFeedbackSourceState]:
                        errorSpecificStep = str((errorSpecificFeedbackSourceState, errorSpecificFeedbackDestinyState))
                        studentStep = str((studentStates[i], studentStates[i+1]))
                        if studentStates[i+1] != errorSpecificFeedbackDestinyState and problemGraphStepsCorrectness[studentStep] >= stronglyValidStep[0] and problemGraphStatesCorrectness[studentStates[i+1]] >= correctState[0] :
                            if len(usefulRelatedSteps) < amount:
                                usefulRelatedSteps[errorSpecificStep] = problemGraphStepsCorrectness[errorSpecificStep]
                            else:
                                stepsToBeRemoved = []
                                stepsToBeAdded = {}
                                for usefulRelatedStep in usefulRelatedSteps:
                                    if len(usefulRelatedSteps) - len(stepsToBeRemoved) >= amount:
                                        if usefulRelatedStep in self.errorSpecificFeedbackFromSteps:
                                            usefulRelatedStepFeedbacks = self.errorSpecificFeedbackFromSteps[usefulRelatedStep]
                                        else:
                                            usefulRelatedStepFeedbacks = 0

                                        if errorSpecificStep in self.errorSpecificFeedbackFromSteps:
                                            errorSpecificStepFeedbacks = self.errorSpecificFeedbackFromSteps[errorSpecificStep]
                                        else:
                                            errorSpecificStepFeedbacks = 0

                                        if usefulRelatedSteps[usefulRelatedStep] > problemGraphStepsCorrectness[errorSpecificStep] or usefulRelatedStepFeedbacks < errorSpecificStepFeedbacks:
                                            stepsToBeRemoved.append(usefulRelatedStep)
                                            stepsToBeAdded[errorSpecificStep] = problemGraphStepsCorrectness[errorSpecificStep]

                                for step in stepsToBeRemoved:
                                    usefulRelatedSteps.pop(step)

                                for step in stepsToBeAdded:
                                    self.chosenExplanationSteps[step] = stepsToBeAdded[step]

                        
        return usefulRelatedSteps    




    def getWhichStatesAndStepsToGetMinimumFeedback(self, studentStates, amount) :

        previousStudentState = '_start_'
        nextStudentState = None

        statesAndStepsNeededInfo = {}

        #for studentState in studentStates:
        for i in range(len(studentStates)):

            studentState = studentStates[i]
            if i < len(studentStates) - 1:
                nextStudentState = studentStates[i+1]
            else:
                nextStudentState = '_end_'

            if studentState not in problemGraph:
                #Pega os estados finais no qual tem esse estado inicial
                if previousStudentState !=  '_start_' and previousStudentState in problemGraph:
                    for nextStepFromPreviousStudentState in problemGraph[previousStudentState]:
                        if nextStepFromPreviousStudentState != '_end_':
                            self.insertStepIfCorrectnessIsValid(str((previousStudentState, nextStepFromPreviousStudentState)), statesAndStepsNeededInfo, amount)

                #Pega os estados iniciais no qual tem esse estado final
                if nextStudentState != '_end_' and nextStudentState in problemGraph:
                    for beforeState in self.getSourceStatesFromDestinyState(nextStudentState):
                        if beforeState != '_start_':
                            self.insertStepIfCorrectnessIsValid(str((beforeState, nextStudentState)), statesAndStepsNeededInfo, amount)
            else:
                #Pega os estados finais no qual tem esse estado inicial
                if previousStudentState !=  '_start_' and previousStudentState in problemGraph:
                    #Pega os passos onde o estado final é diferente do feito pelo aluno
                    for nextStepFromPreviousStudentState in problemGraph[previousStudentState]:
                        if nextStepFromPreviousStudentState != studentState and nextStepFromPreviousStudentState != '_end_':
                            self.insertStepIfCorrectnessIsValid(str((previousStudentState, nextStepFromPreviousStudentState)), statesAndStepsNeededInfo, amount)

                    #Pega os passos onde o estado inicial é diferente do usado
                    for beforeState in self.getSourceStatesFromDestinyState(studentState):
                        if beforeState != previousStudentState and beforeState != '_start_':
                            self.insertStepIfCorrectnessIsValid(str((beforeState, studentState)), statesAndStepsNeededInfo, amount)

                    #Pega os passos alternativos, onde estado anterior e estado atual são diferentes dos usados
                    alternativeSteps = []
                    sourceStates = self.getSourceStatesFromDestinyState(studentState)
                    for sourceState in sourceStates:
                        if sourceState != previousStudentState and sourceState != '_start_':
                            for nextState in problemGraph[sourceState]:
                                if nextState != studentState and nextState != '_end_':
                                    alternativeSteps.append(str((sourceState, nextState)))

                    for step in alternativeSteps:
                        self.insertStepIfCorrectnessIsValid(step, statesAndStepsNeededInfo, amount)

                #Pega os estados iniciais no qual tem esse estado final
                if nextStudentState != '_end_' and nextStudentState in problemGraph:
                    #Casos onde o estado inicial é o atual, mas o final é diferente
                    for nextStepFromStudentState in problemGraph[studentState]:
                        if nextStepFromStudentState != nextStudentState and nextStepFromStudentState != '_end_':
                            self.insertStepIfCorrectnessIsValid(str((studentState, nextStepFromStudentState)), statesAndStepsNeededInfo, amount)
                    
                    #Casos onde os estados iniciais são diferentes do estado atual, mas o estado final é o próximo estado
                    for beforeState in self.getSourceStatesFromDestinyState(nextStudentState):
                        if beforeState != studentState and beforeState != '_start_':
                            self.insertStepIfCorrectnessIsValid(str((beforeState, nextStudentState)), statesAndStepsNeededInfo, amount)
            
                    #Pega os passos alternativos, onde os passo atual e o próximo são diferentes
                    alternativeSteps = []
                    sourceStates = self.getSourceStatesFromDestinyState(nextStudentState)
                    for sourceState in sourceStates:
                        if sourceState != studentState and sourceState != '_start_':
                            for nextState in problemGraph[sourceState]:
                                if nextState != nextStudentState and nextState != '_end_':
                                    alternativeSteps.append(str((sourceState, nextState)))

                    for step in alternativeSteps:
                        self.insertStepIfCorrectnessIsValid(step, statesAndStepsNeededInfo, amount)

            previousStudentState = studentState
        return statesAndStepsNeededInfo

    #def getSourceStatesFromDestinyState(self, destinyState):
    #    sourceStates = []
    #    for step in problemGraph:
    #        if destinyState in problemGraph[step]:
    #            sourceStates.append(step)
    #    return sourceStates


    def insertStepIfCorrectnessIsValid(self, step, statesAndStepsNeededInfo, amount):
        if step in statesAndStepsNeededInfo:
            return

        #Adiciona se achar um maior que o valor passado
        for element in statesAndStepsNeededInfo:
            if abs(problemGraphStepsCorrectness[step]) < abs(statesAndStepsNeededInfo[element]):
                statesAndStepsNeededInfo[step] = problemGraphStepsCorrectness[step]

        #Se tiver espaço na lista, adiciona
        if len(statesAndStepsNeededInfo) < amount:
            statesAndStepsNeededInfo[step] = problemGraphStepsCorrectness[step]


        #Deixa o vetor com o número certo de elementos
        if len(statesAndStepsNeededInfo) > amount:
            highestValue = 0
            highestElement = None
            for element in statesAndStepsNeededInfo:
                if abs(statesAndStepsNeededInfo[element]) > highestValue:
                    highestValue = abs(statesAndStepsNeededInfo[element])
                    highestElement = element

            if highestElement != None:
                statesAndStepsNeededInfo.pop(highestElement)


    def corretudeResolucao(self, resolution):
        loadedProblem = Problem.objects.get(id=self.problemId)
        stateNumber = len(resolution)
        stepNumber = stateNumber - 1
    
        stateValue = 0
        stepValue = 0
        previousNode = None
        for state in resolution:
            node = Node.objects.get(problem=loadedProblem, title = state)
            stateValue = stateValue + node.correctness
            if previousNode != None:
                edge = Edge.objects.get(problem=loadedProblem, sourceNode=previousNode, destNode=node)
                stepValue = stepValue + edge.correctness
            previousNode = node
    
        return (1/(2*stateNumber)) * (stateValue) + (1/(2*stepNumber)) * (stepValue)
    
    def possuiEstado(self, state, resolution):
        return int(state.id in ast.literal_eval(resolution.nodeIdList))
    
    def possuiEstadoConjunto(self, state, resolutions):
        value = 0
        for resolution in resolutions:
            value = value + self.possuiEstado(state, resolution)
        return value
    
    def corretudeEstado(self, state):
        loadedProblem = Problem.objects.get(id=self.problemId)
        correctResolutions = Resolution.objects.filter(problem=loadedProblem, correctness__gt = defaultResolutionValue)
        wrongResolutions = Resolution.objects.filter(problem=loadedProblem, correctness__lte = defaultResolutionValue)

        correctValue = self.possuiEstadoConjunto(state, correctResolutions)
        incorrectValue = self.possuiEstadoConjunto(state, wrongResolutions)
    
        if correctValue + incorrectValue != 0:
            return (correctValue-incorrectValue)/(correctValue + incorrectValue)
        return 0
    
    def possuiPassoConjunto(self, initialState, finalState, resolutions):
        value = 0
        for resolution in resolutions:
            previousState = None
            for state in ast.literal_eval(resolution.nodeIdList):
                if state == finalState.id and previousState == initialState.id:
                    value = value + 1
                previousState = state
        return value
    
    def validadePasso(self, initialState, finalState):
        loadedProblem = Problem.objects.get(id=self.problemId)
        correctResolutions = Resolution.objects.filter(problem=loadedProblem, correctness__gt = defaultResolutionValue)
        wrongResolutions = Resolution.objects.filter(problem=loadedProblem, correctness__lte = defaultResolutionValue)

        correctValue = self.possuiPassoConjunto(initialState, finalState, correctResolutions)
        incorrectValue = self.possuiPassoConjunto(initialState, finalState, wrongResolutions)
    
        if correctValue + incorrectValue != 0:
            return (correctValue-incorrectValue)/(correctValue + incorrectValue)
        return 0

    def calculateValidityAndCorrectness(self, resolution):

        loadedProblem = Problem.objects.get(id=self.problemId)
        previousNode = None
        for state in resolution:
            selectedNode = Node.objects.get(problem=loadedProblem, title=state)
            selectedNode.correctness = self.corretudeEstado(selectedNode)
            if previousNode != None:
                selectedEdge = Edge.objects.get(problem=loadedProblem, sourceNode=previousNode, destNode=selectedNode)
                selectedEdge.correctness = self.validadePasso(previousNode, selectedNode)
                selectedEdge.save()
            selectedNode.save()
            previousNode = selectedNode

        idArray = []
        for node in resolution:
            currentNode = Node.objects.get(problem=loadedProblem, title=node)
            idArray.append(currentNode.id)

        r1 = Resolution(nodeIdList = idArray, problem=loadedProblem, correctness=self.corretudeResolucao(resolution))
        r1.save()



    @XBlock.json_handler
    def initial_data(self, data, suffix=''):
        return {"title": self.problemTitle, "description": self.problemDescription, 
        "answer1": self.problemAnswer1, "answer2": self.problemAnswer2, "answer3": self.problemAnswer3, "answer4": self.problemAnswer4, "answer5": self.problemAnswer5,
        "subject": self.problemSubject, "tags": self.problemTags, "alreadyAnswered": str(self.alreadyAnswered)}


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
