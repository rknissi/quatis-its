"""TO-DO: Write a description of what this XBlock is."""

import json
import pkg_resources
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import Integer, Scope, String, Boolean, List
from xblock.reference.plugins import Filesystem

@XBlock.needs('fs')
class MyXBlock(XBlock):
    """
    TO-DO: document what your XBlock does.
    """

    fs = Filesystem(help="File system", scope=Scope.user_state_summary)  # pylint: disable=invalid-name

    # Fields are defined on the class.  You can access them in your code as
    # self.<fieldname>.

    #Sistema recursivo de contas
    #Cada um deles vai conter uma resposta, e um vetor de argumentos que seriam os valores que o aluno colocará
    #Pode ter um sistema dentro de outro, assim sendo recursivo
    #

    problemTitle = String(
        default="Title", scope=Scope.settings,
        help="Title of the problem",
    )

    problemDescription = String(
        default="Description", scope=Scope.settings,
        help="Description of the problem",
    )

    problemCorrectRadioAnswer = String(
        default="Option A", scope=Scope.settings,
        help="Correct item of the problem",
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

    #problemRadioAnswers = String(
    #    default=["Option A", "Option B", "Option C"], scope=Scope.user_state_summary,
    #    help="Items of the problem",
    #)


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

    #Operação desse bloco
    #0 = Soma
    #1 = Subtração
    #2 = Multiplicação
    #3 = Divisão
    #operation = Integer(
    #    default=0, scope=Scope.user_state_summary,
    #    help="Qual operação que será realizada",
    #)

    ##Um dos valores já presente desse bloco
    #value1 = Integer(
    #    default=0, scope=Scope.user_state_summary,
    #    help="Valor 1 já introduzido",
    #)

    ##Um dos valores já presente desse bloco
    #value2 = Integer(
    #    default=0, scope=Scope.user_state_summary,
    #    help="Valor 2 já introduzido",
    #)

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
        #if self.fs.exists(u"problem.json"):
        #    problem = json.load(self.fs.open(u"problem.json"))
        #    title = problem['title']
        #    description = problem['description']
        #    radioAnswers = problem['radioAnswers']
        #    correcRadioAnswer = problem['correcRadioAnswer']
        #else:
        #    with self.fs.open(u'problem.json', 'wb') as file_output:
        #        file_output.write(json.dumps({'title': 'Teste', 'description': 'Teste', 'radioAnswers': ['Option A', 'Option B', 'Option C'], 'correcRadioAnswer': 'Option A'}).encode())
        #        file_output.close()

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
            #for value in answerArray:
            #    if value == 'a:
            #        answerArray.remove('')

        #if data['answer'] == '1':
        #   return {"answer": self.answerClick}
        #else:
        #   return {"answer": 0}

        #if data['answer'] == '1':
        self.answerSteps = answerArray
        self.answerRadio = data['radioAnswer']
        if answerArray[-1] == self.problemCorrectRadioAnswer and self.answerRadio == self.problemCorrectRadioAnswer:
            return {"hint": "Correto!", "answers": answerArray, "radioAnswer": data['radioAnswer']}
        else:
            return {"hint": "Verifique se a resposta está correta!", "answers": answerArray}

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
