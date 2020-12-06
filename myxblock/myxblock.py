"""TO-DO: Write a description of what this XBlock is."""

import json
import pkg_resources
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import Integer, Scope, String, Boolean, List, Set
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

    problemCorrectSteps = List(
        default=[["Option 1", "Option 2"], ["Option 2", "Option 1", "Option 3"]], scope=Scope.settings,
        help="List of correct steps to the answer",
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

        for l in self.problemCorrectSteps:
            if answerArray == l:
                isStepsCorrect = True

        if isStepsCorrect and self.answerRadio == self.problemCorrectRadioAnswer:
            return {"hint": "Correto!", "answers": answerArray, "radioAnswer": data['radioAnswer']}
        else:
            bestAnswer = None
            mostTrues = 0
            for l in self.problemCorrectSteps:
                i = 0
                trues = 0
                while i < len(l) and i < len(answerArray) :
                    if l[i] == answerArray[i]:
                        trues = trues + 1
                    i = i + 1

                if bestAnswer == None or trues > mostTrues:
                    bestAnswer = l
                    mostTrues = trues

            if  mostTrues < len(answerArray):
                return {"hint": "Verifique se a resposta está correta!", "answers": answerArray, "steps": list(bestAnswer), "stepHint": answerArray[mostTrues]}
            else:
                return {"hint": "Verifique se a resposta está correta!", "answers": answerArray, "steps": list(bestAnswer), "stepHint": answerArray[-1]}


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
