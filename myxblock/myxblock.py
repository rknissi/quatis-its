from array import array
import json
from re import I
import pkg_resources
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import Integer, Scope, String, Boolean, List, Set, Dict, Float
from django.core.files.storage import default_storage
import ast 
#from .studentGraph import models
from .studentGraph.graph import StudentGraphGen
from .studentGraph.models import Question

from django.utils import timezone

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

    #Caminhos corretos do grafo
    problemGraph = Dict(
        default={'_start_': ['Option 1'], 'Option 1': ["Option 2"], "Option 2": ["_end_"]}, scope=Scope.user_state_summary,
        help="The problem graph itself",
    )

    editorProblemGraph = Dict(
        default={'_start_': ['Option 1'], 'Option 1': ["Option 2"], "Option 2": ["_end_"]}, scope=Scope.content,
        help="The problem graph itself",
    )

    editorProblemGraphNodePositions = Dict(
        scope=Scope.content,
        help="The problem graph nodes positions",
    )

    problemGraphStatesCorrectness = Dict(
        default={'_start_': correctState[1], 'Option 1': defaultStateValue, 'Option 2': defaultStateValue}, scope=Scope.user_state_summary,
        help="Shows if each node of the graph is correct with true or false",
    )

    editorProblemGraphStatesCorrectness = Dict(
        default={'_start_': correctState[1], 'Option 1': defaultStateValue, 'Option 2': defaultStateValue}, scope=Scope.content,
        help="Shows if each node of the graph is correct with true or false",
    )
    

    problemGraphStepsCorrectness = Dict(
        default={str(('_start_', 'Option 1')): defaultStepValue, str(('Option 1', 'Option 2')): defaultStepValue, str(('Option 2', '_end_')): defaultStepValue}, scope=Scope.user_state_summary,
        help="Shows if each step of the graph is correct with true or false",
    )

    editorProblemGraphStepsCorrectness = Dict(
        default={str(('_start_', 'Option 1')): defaultStepValue, str(('Option 1', 'Option 2')): defaultStepValue, str(('Option 2', '_end_')): defaultStepValue}, scope=Scope.content,
        help="Shows if each step of the graph is correct with true or false",
    )


    problemVersion = Integer(
        default=1, scope=Scope.user_state_summary,
        help="Version of the problem graph",
    )

    editorProblemVersion = Integer(
        default=1, scope=Scope.content,
        help="Version of the student graph",
    )

    #Resoluções dos alunos

    correctResolutions = List(
        default=["id1"], scope=Scope.user_state_summary,
        help="Ids of correct resolutions",
    )

    wrongResolutions = List(
        default=["id2"], scope=Scope.user_state_summary,
        help="Ids of incorrect resolutions",
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

    @XBlock.json_handler
    def get_node_info(self,data,suffix=''):
        return

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

    def updateProblemGraph(self):
        if (self.problemVersion < self.editorProblemVersion):
            self.problemVersion = self.editorProblemVersion
            self.problemGraph = self.editorProblemGraph
            self.problemGraphStatesCorrectness = self.editorProblemGraphStatesCorrectness
            self.problemGraphStepsCorrectness = self.editorProblemGraphStepsCorrectness

    def updateEditorProblemGraph(self):
        if (self.problemVersion > self.editorProblemVersion):
            self.editorProblemVersion = self.problemVersion
            self.editorProblemGraph = self.problemGraph
            self.editorProblemGraphStatesCorrectness = self.problemGraphStatesCorrectness
            self.editorProblemGraphStepsCorrectness = self.problemGraphStepsCorrectness


    @XBlock.json_handler
    def submit_graph_data(self,data,suffix=''):

        graphData = data.get('graphData')

        self.editorProblemVersion = self.editorProblemVersion + 1

        self.editorProblemGraph.clear()
        self.editorProblemGraphStatesCorrectness.clear()
        self.editorProblemGraphStepsCorrectness.clear()

        for edge in graphData['edges']:
            if edge["from"] not in self.editorProblemGraph:
                self.editorProblemGraph[edge["from"]] = [edge["to"]]
            else:
                self.editorProblemGraph[edge["from"]].append(edge["to"])
            self.editorProblemGraphStepsCorrectness[str(((edge["from"], edge["to"])))] = float(edge["correctness"])

        for node in graphData['nodes']:
            self.editorProblemGraphNodePositions[node["id"]] = {"x": node["x"], "y": node["y"]}
            self.editorProblemGraphStatesCorrectness[node["id"]] = float(node["correctness"])
            if "stroke" in node:
                if node["stroke"] == finalNodeStroke:
                    if node["id"] in self.editorProblemGraph:
                        self.editorProblemGraph[node["id"]].append("_end_")
                    else:
                        self.editorProblemGraph[node["id"]] = ["_end_"]
                else:
                    if "_start_" not in self.editorProblemGraph:
                        self.editorProblemGraph["_start_"] = []
            else:
                if node["id"] not in self.editorProblemGraph:
                    self.editorProblemGraph[node["id"]] = []


        return {'problemGraph': self.editorProblemGraph, 'problemGraphStatesCorrectness': self.editorProblemGraphStatesCorrectness, 'problemGraphStepsCorrectness': self.editorProblemGraphStepsCorrectness, 'editorProblemGraphNodePositions': self.editorProblemGraphNodePositions}


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

    
        #Ver até onde está certo
        for step in answerArray:
            if (step in self.problemCorrectStates.get(lastElement) and self.problemCorrectStates.get(step) != None):
                lastElement = step
                wrongStep = wrongStep + 1
                if  ("_end_" in self.problemCorrectStates.get(step)):
                    break
                else:
                    continue
            else:
                wrongElement = step
                break

        #Se null, então tudo certo
        if (wrongElement == None):
            return {"wrongElement": wrongElement, "lastCorrectElement": lastElement, "correctElementLine": wrongStep}

        return {"wrongElement": wrongElement, "availableCorrectSteps": self.problemCorrectStates.get(lastElement), "wrongElementLine": wrongStep, "lastCorrectElement": lastElement}
    
    def getJsonFromProblemGraph(self):
        self.updateEditorProblemGraph()
        nodeList = []
        edgeList = []
        addedNodes = []
        fixedPos = False

        for source in self.editorProblemGraph:
            for dest in self.editorProblemGraph[source]:
                if source == "_start_":
                    nodeColor = self.getNodeColor(source)

                    if source not in addedNodes:
                        node = {"id": source, "height": defaultNodeHeight, "fill": nodeColor, "shape": initialNodeShape ,"stroke": initialNodeStroke, "correctness": self.editorProblemGraphStatesCorrectness[source]}
                        if source in self.editorProblemGraphNodePositions:
                            node["x"] = self.editorProblemGraphNodePositions[source]["x"]
                            node["y"] = self.editorProblemGraphNodePositions[source]["y"]
                            fixedPos = True
                        nodeList.append(node)
                        addedNodes.append(source)

                    nodeColor = self.getNodeColor(dest)
                    if dest not in addedNodes:
                        node = {"id": dest, "height": defaultNodeHeight, "fill": nodeColor, "correctness": self.editorProblemGraphStatesCorrectness[dest]}
                        if dest in self.editorProblemGraphNodePositions:
                            node["x"] = self.editorProblemGraphNodePositions[dest]["x"]
                            node["y"] = self.editorProblemGraphNodePositions[dest]["y"]
                            fixedPos = True
                        nodeList.append(node)
                        addedNodes.append(dest)
                    else: 
                        pos = addedNodes.index(dest)
                        nodeList[pos] = {"id": dest, "height": defaultNodeHeight, "fill": nodeColor, "correctness": self.editorProblemGraphStatesCorrectness[dest]}

                    edge = {"from": source, "to": dest, "stroke": defaultArrowStroke + self.getEdgeColor(str((source, dest))), "correctness": self.editorProblemGraphStepsCorrectness[str((source, dest))]}
                    edgeList.append(edge)

                    
                elif dest == "_end_":
                    nodeColor = self.getNodeColor(source)
                    if source not in addedNodes:
                        node = {"id": source, "height": defaultNodeHeight, "shape": finalNodeShape ,"fill": nodeColor, "stroke": finalNodeStroke, "correctness": self.editorProblemGraphStatesCorrectness[source]}
                        if source in self.editorProblemGraphNodePositions:
                            node["x"] = self.editorProblemGraphNodePositions[source]["x"]
                            node["y"] = self.editorProblemGraphNodePositions[source]["y"]
                            fixedPos = True
                        nodeList.append(node)
                        addedNodes.append(source)
                    else:
                        pos = addedNodes.index(source)
                        node = {"id": source, "height": defaultNodeHeight, "shape": finalNodeShape, "fill": nodeColor, "stroke": finalNodeStroke, "correctness": self.editorProblemGraphStatesCorrectness[source]}
                        if source in self.editorProblemGraphNodePositions:
                            node["x"] = self.editorProblemGraphNodePositions[source]["x"]
                            node["y"] = self.editorProblemGraphNodePositions[source]["y"]
                            fixedPos = True
                        nodeList[pos] = node
                else:
                    if source not in addedNodes:
                        nodeColor = self.getNodeColor(source)
                        node = {"id": source, "height": defaultNodeHeight, "fill": nodeColor, "correctness": self.editorProblemGraphStatesCorrectness[source]}
                        if source in self.editorProblemGraphNodePositions:
                            node["x"] = self.editorProblemGraphNodePositions[source]["x"]
                            node["y"] = self.editorProblemGraphNodePositions[source]["y"]
                            fixedPos = True
                        nodeList.append(node)
                        addedNodes.append(source)
                    if dest not in addedNodes:
                        nodeColor = self.getNodeColor(dest)
                        node = {"id": dest, "height": defaultNodeHeight, "fill": nodeColor, "correctness": self.editorProblemGraphStatesCorrectness[dest]}
                        if dest in self.editorProblemGraphNodePositions:
                            node["x"] = self.editorProblemGraphNodePositions[dest]["x"]
                            node["y"] = self.editorProblemGraphNodePositions[dest]["y"]
                            fixedPos = True
                        nodeList.append(node)
                        addedNodes.append(dest)
                    
                    edge = {"from": source, "to": dest, "stroke": defaultArrowStroke + self.getEdgeColor(str((source, dest))), "correctness": self.editorProblemGraphStepsCorrectness[str((source, dest))]}
                    edgeList.append(edge)

        return {"nodes": nodeList, "edges": edgeList, "fixedPos": fixedPos, "teste": self.problemVersion, "teste2": self.editorProblemVersion, "teste3": self.problemGraph}
                
    def getEdgeColor(self, edge):

        edgeValue = self.editorProblemGraphStepsCorrectness[edge]
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

        nodeValue = self.editorProblemGraphStatesCorrectness[node]
        if nodeValue >= incorrectState[0] and nodeValue <= incorrectState[1]:
            return "#EE8182"
        if nodeValue >= unknownState[0] and nodeValue <= unknownState[1]:
            return "#F0E591"
        if nodeValue >= correctState[0] and nodeValue <= correctState[1]:
            return "#2AFD84"

    @XBlock.json_handler
    def generate_graph(self, data, suffix=''):
        q = Question(question_text="What's new?", pub_date=timezone.now())
        q.save()
        StudentGraphGen.test()
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
                nextElement = self.problemCorrectStates.get(possibleIncorrectAnswer.get("lastCorrectElement"))[0]
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
        self.updateProblemGraph()

        self.problemVersion = self.problemVersion + 1
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

        lastElement = None
        wrongElement = None

        self.studentResolutionsStates = answerArray
        self.studentResolutionsSteps = list()

        #Verifica se a resposta está correta
        for step in answerArray:
            #Substitui o que existe na resposta do aluno pelos estados equivalentes cadastrados
            if (step in self.problemEquivalentStates):
                step = self.problemEquivalentStates[step]
            if (currentStep == 0):
                if (step in self.problemCorrectStates['_start_']):
                    if (self.problemCorrectStates.get(step) != None):
                        lastElement = step
                        currentStep = currentStep + 1
                        continue
                else:
                    wrongElement = step
                    break
            else:
                if (step in self.problemCorrectStates.get(lastElement) and self.problemCorrectStates.get(step) != None):
                    if  ("_end_" in self.problemCorrectStates.get(step)):
                        isStepsCorrect = True
                        break
                    else:
                        lastElement = step
                        currentStep = currentStep + 1
                        continue
                else:
                    wrongElement = step
                    break

        lastElement = '_start_'
        isAnswerCorrect = isStepsCorrect and self.answerRadio == self.problemCorrectRadioAnswer

        #Vai ser booleano ou vai ser float?
        #self.studentResolutionsCorrectness[data['studentId']] = isAnswerCorrect

        #Aqui ficaria o updateCG, mas sem a parte do evaluation
        #Salva os passos, estados e também salva os passos feitos por cada aluno, de acordo com seu ID
        #COMENTADO OS PASSOS DE ATUALIZAÇÃO DE CORRETUDE, VAMOS FAZER DIREITO AGORA
        #LEMBRAR DE FAZER O IF DE ÚLTINO ELEMENTO PARA NÃO FICAR FEIO
        for step in answerArray:
            if (lastElement not in self.problemGraph):
                self.problemGraph[lastElement] = [step]
            elif (lastElement in self.problemGraph and step not in self.problemGraph[lastElement]):
                self.problemGraph[lastElement].append(step)

            #Colocar os valores certos depois
            if (isAnswerCorrect):
                self.problemGraphStatesCorrectness[step] = defaultStateValue
                self.problemGraphStepsCorrectness[str((lastElement, step))] = defaultStepValue
            else:
                if (step not in self.problemGraphStatesCorrectness):
                    self.problemGraphStatesCorrectness[step] = defaultStateValue
                if (str((lastElement, step)) not in self.problemGraphStepsCorrectness):
                    self.problemGraphStepsCorrectness[str((lastElement, step))] = defaultStepValue

            ###
            self.studentResolutionsSteps.append(str((lastElement, step)))
            lastElement = step

        #Adicionar o caso do últio elemento com o _end_
        finalElement = '_end_'
        if (lastElement not in self.problemGraph):
            self.problemGraph[lastElement] = [finalElement]
        elif (lastElement in self.problemGraph and finalElement not in self.problemGraph[lastElement]):
            self.problemGraph[lastElement].append(finalElement)

        #Colocar os valores certos depois
        if (isAnswerCorrect):
            self.problemGraphStepsCorrectness[str((lastElement, finalElement))] = defaultStepValue
        else:
            if (str((lastElement, finalElement)) not in self.problemGraphStepsCorrectness):
                self.problemGraphStepsCorrectness[str((lastElement, finalElement))] = defaultStepValue
        ###

        self.studentResolutionsSteps.append(str((lastElement, finalElement)))

        #Fim da parte do updateCG

        #self.alreadyAnswered = True
        if isAnswerCorrect:
            return {"answer": "Correto!"}
        else:
            return {"answer": "Incorreto!"}

    def getExplanationOrHintStepsFromProblemGraph(self):
        steps = {}
        for i in self.problemGraph:
            for j in self.problemGraph[i]:
                if self.problemGraphStepsCorrectness[str((i, j))] >= stronglyValidStep[0]:
                    if self.problemGraphStatesCorrectness[i] >= correctState[0] and self.problemGraphStatesCorrectness[j] >= correctState[0]:
                        if i in steps:
                            steps[i].append(j)
                        else:
                            steps[i] = [j]
        return steps    

    def getHintStepFromStudentResolution(self, studentStates):
        chosenHintStep = None
        chosenHintValue = None

        hintSteps = self.getExplanationOrHintStepsFromProblemGraph()

        for i in range(len(studentStates) - 1):
            for hintStepFromGraph in hintSteps:
                if studentStates[i] == hintStepFromGraph and self.problemGraphStatesCorrectness[studentStates[i]] >= correctState[0]:
                    for destinyHintStep in hintSteps[hintStepFromGraph]:
                        if studentStates[i+1] == destinyHintStep and self.problemGraphStatesCorrectness[studentStates[i+1]] >= correctState[0]:

                            hintStep = str((hintStepFromGraph, destinyHintStep))
                            if chosenHintStep == None:
                                chosenHintStep = hintStep
                                chosenHintValue = self.problemGraphStepsCorrectness[hintStep]
                            else:
                                if hintStep in self.hintFromSteps:
                                    newHintFeedbacks = self.hintFromSteps[hintStep]
                                else:
                                    newHintFeedbacks = 0

                                if chosenHintStep in self.explanationFromSteps:
                                    chosenHintStepFeedbacks = self.explanationFromSteps[chosenHintStep]
                                else:
                                    chosenHintstepFeedbacks = 0

                                if chosenHintValue < self.problemGraphStepsCorrectness[hintStep] or chosenHintStepFeedbacks < newHintFeedbacks:
                                    chosenHintStep = hintStep
                                    chosenHintValue = self.problemGraphStepsCorrectness[hintStep]
        return chosenHintStep

    def getExplanationStepsFromStudentResolution(self, studentStates, amount):
        chosenExplanationSteps = {}
        explanationSteps = self.getExplanationOrHintStepsFromProblemGraph()

        for i in range(len(studentStates) - 1):
            for explanationStep in explanationSteps:
                if studentStates[i] == explanationStep and self.problemGraphStatesCorrectness[studentStates[i]] >= correctState[0]:
                    for destinyExplanationStep in explanationSteps[explanationStep]:
                        if studentStates[i+1] == destinyExplanationStep and self.problemGraphStatesCorrectness[studentStates[i+1]] >= correctState[0]:

                            chosenExplanationStep = str((explanationStep, destinyExplanationStep))
                            if len(chosenExplanationSteps) < amount:
                                chosenExplanationSteps[chosenExplanationStep] = self.problemGraphStepsCorrectness[chosenExplanationStep]
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

                                        if chosenExplanationSteps[step] < self.problemGraphStepsCorrectness[chosenExplanationStep] or stepFeedbacks < chosenExplanationStepFeedbacks:
                                            stepsToBeRemoved.append(step)
                                            stepsToBeAdded[chosenExplanationStep] = self.problemGraphStepsCorrectness[chosenExplanationStep]

                                for step in stepsToBeRemoved:
                                    chosenExplanationSteps.pop(step)

                                for step in stepsToBeAdded:
                                    chosenExplanationSteps[step] = stepsToBeAdded[step]

        return chosenExplanationSteps    
    
    def getErrorSpecificFeedbackStepsFromProblemGraph(self):
        steps = {}
        for i in self.problemGraph:
            for j in self.problemGraph[i]:
                if self.problemGraphStepsCorrectness[str((i, j))] < stronglyInvalidStep[1]:
                    if self.problemGraphStatesCorrectness[i] > correctState[0] and self.problemGraphStatesCorrectness[j] < incorrectState[1]:
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
                        if studentStates[i+1] != errorSpecificFeedbackDestinyState and self.problemGraphStepsCorrectness[studentStep] >= stronglyValidStep[0] and self.problemGraphStatesCorrectness[studentStates[i+1]] >= correctState[0] :
                            if len(usefulRelatedSteps) < amount:
                                usefulRelatedSteps[errorSpecificStep] = self.problemGraphStepsCorrectness[errorSpecificStep]
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

                                        if usefulRelatedSteps[usefulRelatedStep] > self.problemGraphStepsCorrectness[errorSpecificStep] or usefulRelatedStepFeedbacks < errorSpecificStepFeedbacks:
                                            stepsToBeRemoved.append(usefulRelatedStep)
                                            stepsToBeAdded[errorSpecificStep] = self.problemGraphStepsCorrectness[errorSpecificStep]

                                for step in stepsToBeRemoved:
                                    usefulRelatedSteps.pop(step)

                                for step in stepsToBeAdded:
                                    chosenExplanationSteps[step] = stepsToBeAdded[step]

                        
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

            if studentState not in self.problemGraph:
                #Pega os estados finais no qual tem esse estado inicial
                if previousStudentState !=  '_start_' and previousStudentState in self.problemGraph:
                    for nextStepFromPreviousStudentState in self.problemGraph[previousStudentState]:
                        if nextStepFromPreviousStudentState != '_end_':
                            self.insertStepIfCorrectnessIsValid(str((previousStudentState, nextStepFromPreviousStudentState)), statesAndStepsNeededInfo, amount)

                #Pega os estados iniciais no qual tem esse estado final
                if nextStudentState != '_end_' and nextStudentState in self.problemGraph:
                    for beforeState in getSourceStatesFromDestinyState(nextStudentState):
                        if beforeState != '_start_':
                            self.insertStepIfCorrectnessIsValid(str((beforeState, nextStudentState)), statesAndStepsNeededInfo, amount)
            else:
                #Pega os estados finais no qual tem esse estado inicial
                if previousStudentState !=  '_start_' and previousStudentState in self.problemGraph:
                    #Pega os passos onde o estado final é diferente do feito pelo aluno
                    for nextStepFromPreviousStudentState in self.problemGraph[previousStudentState]:
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
                            for nextState in self.problemGraph[sourceState]:
                                if nextState != studentState and nextState != '_end_':
                                    alternativeSteps.append(str((sourceState, nextState)))

                    for step in alternativeSteps:
                        self.insertStepIfCorrectnessIsValid(step, statesAndStepsNeededInfo, amount)

                #Pega os estados iniciais no qual tem esse estado final
                if nextStudentState != '_end_' and nextStudentState in self.problemGraph:
                    #Casos onde o estado inicial é o atual, mas o final é diferente
                    for nextStepFromStudentState in self.problemGraph[studentState]:
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
                            for nextState in self.problemGraph[sourceState]:
                                if nextState != nextStudentState and nextState != '_end_':
                                    alternativeSteps.append(str((sourceState, nextState)))

                    for step in alternativeSteps:
                        self.insertStepIfCorrectnessIsValid(step, statesAndStepsNeededInfo, amount)

            previousStudentState = studentState
        return statesAndStepsNeededInfo

    def getSourceStatesFromDestinyState(self, destinyState):
        sourceStates = []
        for step in self.problemGraph:
            if destinyState in self.problemGraph[step]:
                sourceStates.append(step)
        return sourceStates


    def insertStepIfCorrectnessIsValid(self, step, statesAndStepsNeededInfo, amount):
        if step in statesAndStepsNeededInfo:
            return

        #Adiciona se achar um maior que o valor passado
        for element in statesAndStepsNeededInfo:
            if abs(self.problemGraphStepsCorrectness[step]) < abs(statesAndStepsNeededInfo[element]):
                statesAndStepsNeededInfo[step] = self.problemGraphStepsCorrectness[step]

        #Se tiver espaço na lista, adiciona
        if len(statesAndStepsNeededInfo) < amount:
            statesAndStepsNeededInfo[step] = self.problemGraphStepsCorrectness[step]


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


        
    def corretudeResolucao(resolutionId, self):
        stateNumber = len(self.studentResolutionsStates)
        stepNumber = len(self.studentResolutionsStep)
    
        stateValue = 0
        for state in self.studentResolutionsStates:
            stateValue = stateValue + self.corretudeEstado(state)
    
        stepValue = 0
        for step in self.studentResolutionsSteps:
            stepValue = stepValue + self.validadePasso(step)
    
        return (1/2*stateNumber) * (stateValue) + (1/2*stepNumber) * (stepValue)

    def possuiEstadoGrafo(state, self):
        for resolution in self.studentResolutionsStates:
            if state in resolution:
                return True
        return False
    
    def getStepsWhereStartsWith(state, self):
        stepList = []
        for step in self.problemGraphStatesSteps:
            if eval(step)[0] == state:
                stepList.append(eval(step))
        return stepList

    def getStepsWhereEndsWith(state, self):
        stepList = []
        for step in self.problemGraphStatesSteps:
            if eval(step)[1] == state:
                stepList.append(eval(step))
        return stepList
    
    def possuiEstado(state, resolutionId, self):
        return int(state in self.studentResolutionsStates)
    
    def possuiEstadoConjunto(state, resolutionIds, self):
        value = 0
        for id in resolutionIds:
            value = value +  self.possuiEstado(state, id)
        return value
    
    def corretudeEstado(state, self):
        correctValue = self.possuiEstadoConjunto(state, self.correctResolutions)
        incorrectValue = self.possuiEstadoConjunto(state, self.incorrectResolutions)
    
        return (correctValue-incorrectValue)/(correctValue + incorrectValue)
    
    def possuiPasso(step, resolutionId, self):
        return int(str((step[0], step[1])) in self.studentResolutionsSteps)
    
    def possuiPassoConjunto(step, resolutionIds, self):
        value = 0
        for id in resolutionIds:
            value = value + self.possuiPasso(step, id)
        return value
    
    def validadePasso(step, self):
        correctValue = self.possuiPassoConjunto(step, self.correctResolutions)
        incorrectValue = self.possuiPassoConjunto(step, self.incorrectResolutions)
    
        return (correctValue-incorrectValue)/(correctValue + incorrectValue)


    @XBlock.json_handler
    def initial_data(self, data, suffix=''):
        return {"title": self.problemTitle, "description": self.problemDescription, 
        "answer1": self.problemAnswer1, "answer2": self.problemAnswer2, "answer3": self.problemAnswer3, "answer4": self.problemAnswer4, "answer5": self.problemAnswer5,
        "subject": self.problemSubject, "tags": self.problemTags, "alreadyAnswered": str(self.alreadyAnswered), "teste": self.problemVersion, "teste2": self.editorProblemVersion, "teste3": self.editorProblemGraph}


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
