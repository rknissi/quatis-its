"""TO-DO: Write a description of what this XBlock is."""

import json
import pkg_resources
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import Integer, Scope, String, Boolean, List, Set, Dict
import ast


#Step information
minValue = -1
maxValue = 1

#Resolution values
incorrectResolution = [-1, -0.75001]
partiallyIncorrectResolution = [-0.75, -0.00001]
partiallyCorrectResolution = [0, 0.74999]
CorrectResolution = [0.75, 1]

#Step values
invalidStep = [-1, -0.80001]
stronglyInvalidStep = [-0.8, -0.40001]
possiblyInvalidStep = [-0.4, -0.00001]
neutralStep = [0, 0]
possiblyValidStep = [0.00001, 0.39999]
stronglyValidStep = [0.4, 0.79999]
validStep = [0.8, 1]

#State values
incorrectState = [-1, -0.7]
stronglyInvalidStep = [-0.69999, 0.69999]
possiblyInvalidStep = [0.7, 1]

def levenshteinDistance(A, B):
    if(len(A) == 0):
        return len(B)
    if(len(B) == 0):
        return len(A)
    if (A[0] == B[0]):
        return levenshteinDistance(A[1:], B[1:])
    return 1 + min(levenshteinDistance(A, B[1:]), levenshteinDistance(A[1:], B), levenshteinDistance(A[1:], B[1:])) 


class MyXBlock(XBlock):

    #Se o aluno já fez o exercício
    alreadyAnswered = Boolean(
        default=False, scope=Scope.user_state,
        help="If the student already answered the exercise",
    )

    #Dados dos alunos
    problemGraph = Dict(
        default={'_start_': ['Option 1'], 'Option 1': ["Option 2"], "Option 2": ["_end_"]}, scope=Scope.user_state_summary,
        help="The problem graph itself",
    )

    problemGraphStates = Dict(
        default={'Option 1': True, 'Option 2': True}, scope=Scope.user_state_summary,
        help="Shows if each node of the graph is correct with true or false",
    )
    

    problemGraphStatesSteps = Dict(
        default={str(('_start_', 'Option 1')): True, str(('Option 1', 'Option 2')): True, str(('Option 2', '_end_')): True}, scope=Scope.user_state_summary,
        help="Shows if each step of the graph is correct with true or false",
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
    studentResolutionsStates = Dict(
        default={'id1':["Tag1", "Tag2", "Tag3"]}, scope=Scope.user_state_summary,
        help="Ids for each student states",
    )

    studentResolutionsSteps = Dict(
        default={'id1':[str(('_start_', 'Option 1')), str(('Option 1', 'Option 2')), str(('Option 2', '_end_'))]}, scope=Scope.user_state_summary,
        help="Id for each student steps",
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

    problemCorrectSteps = Dict(
        default={'_start_': ['Option 1'], 'Option 1': ["Option 2"], "Option 2": ["_end_"]}, scope=Scope.content,
        help="List of correct steps to the answer",
    )

    problemTipsToNextStep = Dict(
        default={"Option 1": ["Dicaaaaas 1", "Dicaaaaaaa 2"], "Option 2": ["Tainted Love suaidiosadisasa bcsabcasbcascnasnc sancnsacnsn cbascbasbcsabcbascbas", "Uia"]}, scope=Scope.content,
        help="List of tips for each step of the correct answers",
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

        frag = Fragment(str(html).format(problemTitle=self.problemTitle,problemDescription=self.problemDescription,problemCorrectRadioAnswer=self.problemCorrectRadioAnswer,problemCorrectSteps=self.problemCorrectSteps,problemTipsToNextStep=self.problemTipsToNextStep,problemDefaultHint=self.problemDefaultHint,problemAnswer1=self.problemAnswer1,problemAnswer2=self.problemAnswer2,problemAnswer3=self.problemAnswer3,problemAnswer4=self.problemAnswer4,problemAnswer5=self.problemAnswer5,problemSubject=self.problemSubject,problemTags=self.problemTags))
        frag.add_javascript(self.resource_string("static/js/src/myxblockEdit.js"))

        frag.initialize_js('MyXBlockEdit')
        return frag


    @XBlock.json_handler
    def submit_data(self,data,suffix=''):
        self.problemTitle = data.get('problemTitle')
        self.problemDescription = data.get('problemDescription')
        self.problemCorrectRadioAnswer = data.get('problemCorrectRadioAnswer')
        self.problemCorrectSteps = ast.literal_eval(data.get('problemCorrectSteps'))
        self.problemTipsToNextStep = ast.literal_eval(data.get('problemTipsToNextStep'))
        self.problemAnswer1 = data.get('problemAnswer1')
        self.problemAnswer2 = data.get('problemAnswer2')
        self.problemAnswer3 = data.get('problemAnswer3')
        self.problemAnswer4 = data.get('problemAnswer4')
        self.problemAnswer5 = data.get('problemAnswer5')
        self.problemSubject = data.get('problemSubject')
        self.problemTags = ast.literal_eval(data.get('problemTags'))

        return {'result':'success'}

    #Sistema que mostra quais dicas até o primeiro passo errado
    #Qual das dicas isso aqui é?
    @XBlock.json_handler
    def get_hint(self, data, suffix=''):
        answerArray = data['answer'].split('\n')

        if '' in answerArray:
            answerArray =  list(filter(lambda value: value != '', answerArray))

        hintList = None

        currentStep = 0

        lastElement = None
        actualElement = None

        hintText = self.problemDefaultHint
        stepText = ""
    

        #Ver até onde está certo
        for step in answerArray:
            if (currentStep == 0):
                if (step in self.problemCorrectSteps['_start_']):
                    if (self.problemCorrectSteps.get(step) != None):
                        lastElement = step
                        currentStep = currentStep + 1
                        continue
                else:
                    actualElement = step
                    break
            else:
                if (step in self.problemCorrectSteps.get(lastElement) and self.problemCorrectSteps.get(step) != None):
                    lastElement = step
                    currentStep = currentStep + 1
                    if  ("_end_" in self.problemCorrectSteps.get(step)):
                        break
                    else:
                        continue
                else:
                    actualElement = step
                    break
        
        if (lastElement == None):
            possibleSteps = self.problemCorrectSteps.get("_start_")
        else:
            possibleSteps = self.problemCorrectSteps.get(lastElement)

        #Pegar a dica do próximo passo
        minValue = float('inf')
        choosenStep = None
        if  (actualElement != None):
            for step in possibleSteps:
                actualValue = levenshteinDistance(actualElement, step)
                if(actualValue < minValue):
                    minValue = actualValue
                    choosenStep = step
        else:
            choosenStep = lastElement
            currentStep = currentStep - 1

        if (self.problemTipsToNextStep.get(choosenStep) != None):
            hintList = self.problemTipsToNextStep.get(choosenStep)
        else:
            hintList = self.problemTipsToNextStep.get(self.problemCorrectSteps.get("_start_")[0])

        try:
            if (data['hintLine'] != currentStep):
                hintText = hintList[0]
            else:
                if (data['repeatHint'] < len(hintList)):
                    hintText = hintList[data['repeatHint']]
                else:
                    hintText = hintList[-1]
            if  (currentStep != -1):
                stepText = answerArray[currentStep]
        except IndexError:
            hintText = self.problemDefaultHint
            stepText = ""
                
        return {"hint": hintText, "stepHint": stepText, "hintList": hintList, "currentStep": currentStep, "hintLine": data['hintLine']}


    #Envia a resposta final
    @XBlock.json_handler
    def send_answer(self, data, suffix=''):
        """
        An example handler, which increments the data.
        """

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
        actualElement = None

        self.studentResolutionsStates[data['studentId']] = answerArray
        self.studentResolutionsSteps[data['studentId']] = list()

        #Verifica se a resposta está correta
        for step in answerArray:
            if (currentStep == 0):
                if (step in self.problemCorrectSteps['_start_']):
                    if (self.problemCorrectSteps.get(step) != None):
                        lastElement = step
                        currentStep = currentStep + 1
                        continue
                else:
                    actualElement = step
                    break
            else:
                if (step in self.problemCorrectSteps.get(lastElement) and self.problemCorrectSteps.get(step) != None):
                    if  ("_end_" in self.problemCorrectSteps.get(step)):
                        isStepsCorrect = True
                        break
                    else:
                        lastElement = step
                        currentStep = currentStep + 1
                        continue
                else:
                    actualElement = step
                    break

        lastElement = '_start_'
        isAnswerCorrect = isStepsCorrect and self.answerRadio == self.problemCorrectRadioAnswer

        #Aqui ficaria o updateCG, mas sem a parte do evaluation
        #Salva os estados e os passos do cadastro
        for step in answerArray:
            if (lastElement not in self.problemGraph):
                self.problemGraph[lastElement] = [step]
            elif (lastElement in self.problemGraph and step not in self.problemGraph[lastElement]):
                self.problemGraph[lastElement].append(step)
            if (isAnswerCorrect):
                self.problemGraphStates[step] = True                
                self.problemGraphStatesSteps[str((lastElement, step))] = True                
            else:
                if (step not in self.problemGraphStates):
                    self.problemGraphStates[step] = False                
                if (str((lastElement, step)) not in self.problemGraphStatesSteps):
                    self.problemGraphStatesSteps[str((lastElement, step))] = False
            self.studentResolutionsSteps[data['studentId']].append(str((lastElement, step)))
            lastElement = step

        finalElement = '_end_'
        if (lastElement not in self.problemGraph):
            self.problemGraph[lastElement] = [finalElement]
        elif (lastElement in self.problemGraph and finalElement not in self.problemGraph[lastElement]):
            self.problemGraph[lastElement].append(finalElement)
        if (isAnswerCorrect):
            self.problemGraphStatesSteps[str((lastElement, finalElement))] = True                
        else:
            if (str((lastElement, finalElement)) not in self.problemGraphStatesSteps):
                self.problemGraphStatesSteps[str((lastElement, finalElement))] = False
        self.studentResolutionsSteps[data['studentId']].append(str((lastElement, finalElement)))

        #Fim da parte do updateCG

        self.alreadyAnswered = True
        if isAnswerCorrect:
            return {"answer": "Correto!"}
        else:
            return {"answer": "Incorreto!", "teste1": self.studentResolutionsSteps, "reste2": self.studentResolutionsStates}

    def corretudeResolucao(resolutionId):
        stateNumber = len(studentResolutionsStates[resolutionId])
        stepNumber = len(studentResolutionsStep[resolutionId])
    
        stateValue = 0
        for state in studentResolutionsStates[resolutionId]:
            stateValue = stateValue + corretudeEstado(state)
    
        stepValue = 0
        for step in studentResolutionsSteps[resolutionId]:
            stepValue = stepValue + validadePasso(step)
    
        return (1/2*stateNumber) * (stateValue) + (1/2*stepNumber) * (stepValue)
    
    def possuiEstado(state, resolutionId):
        return int(state in studentResolutionsStates[resolutionId])
    
    def possuiEstadoConjunto(state, resolutionIds):
        value = 0
        for id in resolutionIds:
            value = value +  possuiEstado(state, id)
        return value
    
    def corretudeEstado(state):
        correctValue = possuiEstadoConjunto(state, correctResolutions)
        incorrectValue = possuiEstadoConjunto(state, incorrectResolutions)
    
        return (correctValue-incorrectValue)/(correctValue + incorrectValue)
    
    def possuiPasso(step, resolutionId):
        return int(str((step[0], step[1])) in studentResolutionsSteps[resolutionId])
    
    def possuiPassoConjunto(step, resolutionIds):
        value = 0
        for id in resolutionIds:
            value = value +  possuiPasso(step, id)
        return value
    
    def validadePasso(step):
        correctValue = possuiPassoConjunto(step, correctResolutions)
        incorrectValue = possuiPassoConjunto(step, incorrectResolutions)
    
        return (correctValue-incorrectValue)/(correctValue + incorrectValue)

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
