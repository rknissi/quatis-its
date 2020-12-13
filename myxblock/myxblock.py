"""TO-DO: Write a description of what this XBlock is."""

import json
import pkg_resources
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import Integer, Scope, String, Boolean, List, Set, Dict
from xblock.reference.plugins import Filesystem

@XBlock.needs('fs')
class MyXBlock(XBlock):
    """
    TO-DO: document what your XBlock does.
    """

    fs = Filesystem(help="File system", scope=Scope.user_state_summary)  # pylint: disable=invalid-name

    problemTitle = String(
        default="Title", scope=Scope.settings,
        help="Title of the problem",
    )

    problemDescription = String(
        default="Description", scope=Scope.settings,
        help="Description of the problem",
    )

    problemCorrectRadioAnswer = String(
        default="Option 1", scope=Scope.settings,
        help="Correct item of the problem",
    )

    problemCorrectSteps = Dict(
        default={'_start_': ['Option 1'], 'Option 1': ["Option 2"], "Option 2": ["_end_"]}, scope=Scope.settings,
        help="List of correct steps to the answer",
    )

    problemTipsToNextStep = Dict(
        default={'_start_': ["Dicaaaaas 1"], "Option 1": ["Dicaaaaas 2", "Dicaaaaaaa 3"]}, scope=Scope.settings,
        help="List of tips for each step of the correct answers",
    )

    problemDefaultHint = String(
        default="Verifique se a resposta está correta", scope=Scope.settings,
        help="If there is no available hint",
    )

    problemAnswer1 = String(
        default="Option 1", scope=Scope.settings,
        help="Item 1 of the problem",
    )

    problemAnswer2 = String(
        default="Option 2", scope=Scope.settings,
        help="Item 2 of the problem",
    )

    problemAnswer3 = String(
        default="Option 3", scope=Scope.settings,
        help="Item 3 of the problem",
    )

    problemAnswer4 = String(
        default="Option 4", scope=Scope.settings,
        help="Item 4 of the problem",
    )

    problemAnswer5 = String(
        default="Option 5", scope=Scope.settings,
        help="Item 5 of the problem",
    )

    problemSubject = String(
        default="Subject", scope=Scope.settings,
        help="Subject of the problem",
    )

    problemTags = List(
        default=["Tag"], scope=Scope.settings,
        help="Tags of the problem",
    )


    #Resposta desse bloco
    answerSteps = String(
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

    # TO-DO: change this handler to perform your own actions.  You may need more
    # than one handler, or you may not need any handlers at all.
    @XBlock.json_handler
    def send_answer(self, data, suffix=''):
        """
        An example handler, which increments the data.
        """

        answerArray = data['answer'].split('\n')

        if '' in answerArray:
            answerArray =  list(filter(lambda value: value != '', answerArray))

        self.answerSteps = answerArray
        self.answerRadio = data['radioAnswer']


        isStepsCorrect = False

        hintList = None

        currentStep = 0
        lastElement = None

        isWrong = False

        for step in answerArray:
            if (currentStep == 0):
                if (step in self.problemCorrectSteps['_start_']):
                    if (self.problemCorrectSteps.get(step) != None):
                        lastElement = step
                        currentStep = currentStep + 1
                        continue
                else:
                    isWrong = True
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
                    isWrong = True
                    break
        
        if  (isWrong == True):
            if (lastElement == None):
                hintList = self.problemTipsToNextStep.get("_start_")
            else:
                hintList = self.problemTipsToNextStep.get(lastElement)
            try:
                if (data['hintLine'] != currentStep):
                    hintText = hintList[0]
                else:
                    if (data['repeatHint'] < len(hintList)):
                        hintText = hintList[data['repeatHint']]
                    else:
                        hintText = hintList[-1]
                stepText = answerArray[currentStep]
            except IndexError:
                hintText = self.problemDefaultHint
                stepText = ""
                
        if isStepsCorrect and self.answerRadio == self.problemCorrectRadioAnswer:
            return {"hint": "Correto!", "answers": answerArray, "radioAnswer": data['radioAnswer']}
        else:
            return {"hint": hintText, "stepHint": stepText, "hintList": hintList[currentStep], "answerArray": answerArray[currentStep]}




    @XBlock.json_handler
    def initial_data(self, data, suffix=''):
        return {"title": self.problemTitle, "description": self.problemDescription, 
        "answer1": self.problemAnswer1, "answer2": self.problemAnswer2, "answer3": self.problemAnswer3, "answer4": self.problemAnswer4, "answer5": self.problemAnswer5,
        "subject": self.problemSubject, "tags": self.problemTags}


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
