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

    #ùltimo erro cometido pelo aluno
    lastWrongElement = String(
        default="", scope=Scope.user_state,
        help="Last wrong element from the student",
    )

    #ùltimo erro cometido pelo aluno (linha)
    lastWrongElementLine = Integer(
        default=0, scope=Scope.user_state,
        help="Last wrong element from the student (line)",
    )

    #Caminhos corretos do grafo
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

    #Faz sentido isso?
    errorSpecificFeedback = Dict(
        default={"Option 3": ["Error Specific feedback 1", "Error Specific Feedback 2"]}, scope=Scope.content,
        help="For each wrong step that the student uses, it will show a specific feedback",
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

        frag = Fragment(str(html).format(problemTitle=self.problemTitle,problemDescription=self.problemDescription,problemCorrectRadioAnswer=self.problemCorrectRadioAnswer,problemCorrectSteps=self.problemCorrectStates,problemTipsToNextStep=self.problemTipsToNextState,problemDefaultHint=self.problemDefaultHint,problemAnswer1=self.problemAnswer1,problemAnswer2=self.problemAnswer2,problemAnswer3=self.problemAnswer3,problemAnswer4=self.problemAnswer4,problemAnswer5=self.problemAnswer5,problemSubject=self.problemSubject,problemTags=self.problemTags))
        frag.add_javascript(self.resource_string("static/js/src/myxblockEdit.js"))

        frag.initialize_js('MyXBlockEdit')
        return frag


    @XBlock.json_handler
    def submit_data(self,data,suffix=''):
        self.problemTitle = data.get('problemTitle')
        self.problemDescription = data.get('problemDescription')
        self.problemCorrectRadioAnswer = data.get('problemCorrectRadioAnswer')
        self.problemCorrectStates = ast.literal_eval(data.get('problemCorrectSteps'))
        self.problemTipsToNextState = ast.literal_eval(data.get('problemTipsToNextStep'))
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

        return {"wrongElement": wrongElement, "availableCorrectSteps": self.problemCorrectStates.get(lastElement), "wrongElementLine": wrongStep}


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
        nextStep = None
        if  (wrongElement != None):
            possibleSteps = possibleIncorrectAnswer.get("availableCorrectSteps")
            for step in possibleSteps:
                actualValue = levenshteinDistance(wrongElement, step)
                if(actualValue < minValue):
                    minValue = actualValue
                    nextStep = step

            hintList = self.problemTipsToNextState.get(nextStep)

        try:
            #Então está tudo certo, pode dar um OK e seguir em frente
            #MO passo está correto, mas agora é momento de mostrar a dica para o próximo passo.
            if (wrongElement == None):
                lastCorrectElement = possibleIncorrectAnswer.get("lastCorrectElement")
                lastCorrectElementLine = possibleIncorrectAnswer.get("correctElementLine")
                nextElement = self.problemCorrectStates.get(lastCorrectElement)[0]
                #Verificar se é o último passo, se for, sempre dar a dica padrão?
                if (nextElement == "_end_"):
                    hintText = self.problemDefaultHint
                else:
                    hintList = self.problemTipsToNextState.get(nextElement)

                    if (lastCorrectElementLine != self.lastWrongElementLine):
                        hintText = hintList[0]
                    elif (data['currentWrongElementHintCounter'] < len(hintList)):
                        hintText = hintList[data['currentWrongElementHintCounter']]
                    else:
                        hintText = hintList[-1]
                
                    self.lastWrongElement = lastCorrectElement
                    self.lastWrongElementLine = lastCorrectElementLine

                return {"status": "OK", "hint": hintText, "lastCorrectElement": lastCorrectElement}
            else:
                wrongElementLine = possibleIncorrectAnswer.get("wrongElementLine")
                if (wrongElementLine != self.lastWrongElementLine):
                    hintText = hintList[0]
                elif (data['currentWrongElementHintCounter'] < len(hintList)):
                    hintText = hintList[data['currentWrongElementHintCounter']]
                else:
                    hintText = hintList[-1]
        except IndexError:
            hintText = self.problemDefaultHint

        self.lastWrongElement = wrongElement
        self.lastWrongElementLine = wrongElementLine
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

        lastElement = None
        wrongElement = None

        self.studentResolutionsStates[data['studentId']] = answerArray
        self.studentResolutionsSteps[data['studentId']] = list()

        #Verifica se a resposta está correta
        for step in answerArray:
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

        #Aqui ficaria o updateCG, mas sem a parte do evaluation
        #Salva os passos, estados e também salva os passos feitos por cada aluno, de acordo com seu ID
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
            return {"answer": "Incorreto!"}

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

    def possuiEstadoGrafo(state):
        for resolution in studentResolutionsStates:
            if state in resolution:
                return True
        return False
    
    def getStepsWhereStartsWith(state):
        stepList = []
        for step in self.problemGraphStatesSteps:
            if eval(step)[0] == state:
                stepList.append(eval(step))
        return stepList

    def getStepsWhereEndsWith(state):
        stepList = []
        for step in self.problemGraphStatesSteps:
            if eval(step)[1] == state:
                stepList.append(eval(step))
        return stepList
    
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

    #def minimumFeedback(states):
    #    previousState = None
    #    nextState = None
    #    for i in range(len(states) - 1):
    #        if (i != len(states) - 1):
    #            nextState = states[i+1]
    #        else:
    #            nextState = None

    #        if possuiEstadoGrafo(states[i]):
    #            for step in getStepsWhereEndsWith(states[i]):
    #                if step[0] == previousState:
    #                    #Atualizar a corretude do previousState
    #                    corretudeEstado(step[0])
    #                else:
    #                    for step2 in getStepsWhereStartsWith(step[0]):
    #                        if step2[1] != states[i]:
    #                            #Solicitar informações da validade dos passos:
    #                    
    #        else:
    #            if previousState == None and nextState == None:
    #                continue
    #            if (previousState != None):
    #                #Atualizar a corretude do previousState

    #                for step in getStepsWhereStartsWith(previousState):
    #                    if step[1] != states[i]:
    #                        #Solicitar informações da validade desses passos
    #                        #Solicitar corretude dos estados destinos desses passos
    #                        corretudeEstado(step[1])
    #            if (nextState != None):
    #                #Atualizar a corretude do nextState

    #                for step in getStepsWhereStartsWith(previousState):
    #                    if step[0] != states[i]:
    #                        #Solicitar informações da validade desses passos
    #                        #Solicitar corretudo dos estados origem desses passos
    #                        corretudeEstado(step[0])


    #        previousState = states[i]



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
