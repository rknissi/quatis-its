/* Javascript for MyXBlock. */
function MyXBlock(runtime, element, data) {

    var hints = [];
    var hintsIds = [];
    var hintsTypes = [];
    var hintsSentFeedback = [];
    var actualHint = -1;

    var doubtIds = []

    var minimumCheckboxLLineId = 1
    var checkboxLineId = minimumCheckboxLLineId

    var send_answer = runtime.handlerUrl(element, 'send_answer');
    var send_feedback = runtime.handlerUrl(element, 'send_feedback');
    var recommend_feedback = runtime.handlerUrl(element, 'recommend_feedback');
    var get_hint_for_last_step = runtime.handlerUrl(element, 'get_hint_for_last_step');
    var return_full_explanation = runtime.handlerUrl(element, 'return_full_explanation');
    var getInitialData = runtime.handlerUrl(element, 'initial_data');
    var getDoubtsAndAnswerFromStep = runtime.handlerUrl(element, 'get_doubts_and_answers_from_step');
    var getDoubtsAndAnswerFromState = runtime.handlerUrl(element, 'get_doubts_and_answers_from_state');
    var submitDoubtAnswerInfo = runtime.handlerUrl(element, 'submit_doubt_answer_info');
    var checkIfUseAiExplanation = runtime.handlerUrl(element, 'check_if_use_ai_explanation');
    var increaseFeedbackCount = runtime.handlerUrl(element, 'increase_feedback_count');
    var finishActivityTime = runtime.handlerUrl(element, 'finish_activity_time');
    var update_positions = runtime.handlerUrl(element, 'update_positions')
    var update_resolution_correctness = runtime.handlerUrl(element, 'update_resolution_correctness')

    var yesAnswer = ["sim", "s", "yes", "y", "si", "ye", "yep", "yeah", "yea"];
    var noAnswer = ["não", "n", "no", "nao", "nope", "nop"];

    var yesUniversalAnswer = "yes"
    var noUniversalAnswer = "no"

    var wrongAnswerColor = "red"
    var rightAnswerColor = "#03b803" 
    var noneAnswerColor = "none"
    var doubtAnswerColor = "yellow"

    var PT = 0
    var EN = 1

    var language = 0

    var explanationMessages = ["Como você resolveu a seguinte etapa?\n", "How would you explain to someone why the following step is correct?\n"]
    var hintMessages = ["Qual dica você daria para resolver a seguinte etapa?\nNão vale dar dar a resposta, heim!\n", "Which hint would be useful on the following step?\nGiving away the answer is not a hint!\n"]
    var errorSpecificMessages = ["Por que a ação abaixo está errada?\n", "How would you explain to someone why the following step is incorrect?\n"]
    var stepMessage = ["Esta ação está correta?\n", "Is the following action correct?\nRemember: we shouldn't skip steps\n"]
    var stateMessage1 = ["A seguinte situação está correta?\n", "Is the following situation correct?\n"]
    var stateMessage2 = ["\nPara a seguinte resolução:\n", "\nFor the solution:\n"]
    var yesOrNoMessage = ["\nEscreva 'S' para sim, ou 'N' para não", "\nAnswer with yes or no"]
    var stepDoubtMessage1 = ["Como você responderia a seguinte dúvida?\n", "How would you answer the question: \n"]
    var stepDoubtMessage2 = ["\nDa ação: ", "\nFor the action: "]
    var stateDoubtMessage1 = ["Como você responderia a seguinte dúvida?\n", "How would you answer the question: \n"]
    var stateDoubtMessage2 = ["\nPara ajudar a realizar a próxima ação a partir de: ", "\nTo help to get to the next step from: "]
    var emptyResolutionMessage = ["Sua resolução não pode ser vazia", "Your stey-by-step solution cannot be empty"]
    var doubtSentMessage = ["Dúvida enviada com sucesso", "Your question was sent successfully"]
    var alreadyCreatedDoubtMessage = ["Essa dúvida já foi realizada por um colega seu, e ninguém ainda a respondeu", "This question was made by another person, but there are still no answers"]
    var whatDoubtStateMessage = ["Qual dúvida te impede de saber como prosseguir a partir de: \n", "What's your question that is preventing you continuing from: \n"]
    var whatDoubtStepMessage = ["Qual a dúvida para a seguinte transição? \n", "What's your question about the action? \n"]
    var sameDoubtMessage = ["Essa dúvida é a mesma que você tem?\n", "Is this the same question that you have? Answer with yes or no\n"]
    var answerMessage = ["Isso responde sua dúvida ou é útil?\n", "Does this answers your question or is it useful to you?\n"]
    var newDoubtMessage1 = ["Você tem dúvidas na transição \n", "Do you have a question in the action\n"]
    var newDoubtMessage2 = ["\n\nOu você não sabe como prosseguir do passo\n", "\n\nOr you can't continue from the following step: \n"]
    var newDoubtMessage3 = ["\n\nDigite 'primeiro' se for na transição, ou 'segundo' se não sabe como prosseguir", "\n\nWrite 'first' if it's on the action, or 'second' if you don't know how to proceed"]
    var invalidDoubtChoiceMessage = ["Escolha inválida. Por favor escreva 'primeiro' ou 'segundo'", "Invalid choice. Please choose either 'first' or 'second'"]
    var stillHaveDoubts = ["Ainda lhe restam dúvidas?", "Do you still have any questions? Answer with yes or no"]
    var invalidFieldValuesMessage = ["Por favor remova os passos '_start_' e _end_ de sua resolução", "Please remove the steps '_start_' and '_end_' from your solution"]
    var selfLoopMessage = ["Não coloque 2 passos iguais um após o outro", "Please do not use 2 identical steps that are after each other"]
    var invalidSolution = ["Uma resolução precisa conter pelo menos 2 passos!", "A solution must contain at least 2 steps!"]
    var onlySpacesMessage = ["Remova os passos que tenham apenas espaços ou vazios", "Please remove any steps that only contains spaces or it's empty"]

    var doubtChoiceFirst = ["primeiro", "first"]
    var doubtChoiceSecond = ["segundo", "second"]

    function transformToSimplerAnswer(answer) {
        if (answer) {
            withoutSpaces = answer.replace(/\s/g, "")
            lowerCase = withoutSpaces.toLowerCase()
            noAccent = lowerCase.normalize("NFD").replace(/\p{Diacritic}/gu, "")
            return noAccent
        }
        return answer
    }

    function disableButton(buttonElement) {
        document.getElementById(buttonElement).disabled = true;
    }

    function enableButton(buttonElement) {
        document.getElementById(buttonElement).disabled = false;
    }


    function checkIfUserInputIsValid(input) {
        if (yesAnswer.includes(input.toLowerCase()) || noAnswer.includes(input.toLowerCase())) {
            return true
        } 
        return false
    }

    function getUserAnswer(input) {
        if (yesAnswer.includes(input.toLowerCase()) ) {
            return yesUniversalAnswer
        } else if (noAnswer.includes(input.toLowerCase())) {
            return noUniversalAnswer
        }
        return null
    }

    function defineValues(value) {
        if (value.language != 'pt') {
            language = EN
        }

        $('#question', element).text(value.title);

        $('#description', element).text(value.description);

        $('#subject', element).text(value.subject);

        var result = [];
        for(var i in value.tags)
            result.push([value.tags[i]]);
        
        $('#tags', element).text(result);

        if (value.multipleChoiceProblem == 1) {
            document.getElementById("answer1").value = value.answer1;
            var itsLabel1 = $("[for=" + $("#answer1").attr("id") + "]");
            itsLabel1.text(value.answer1);

            document.getElementById("answer2").value = value.answer2;
            var itsLabel2 = $("[for=" + $("#answer2").attr("id") + "]");
            itsLabel2.text(value.answer2);

            document.getElementById("answer3").value = value.answer3;
            var itsLabel3 = $("[for=" + $("#answer3").attr("id") + "]");
            itsLabel3.text(value.answer3);

            document.getElementById("answer4").value = value.answer4;
            var itsLabel4 = $("[for=" + $("#answer4").attr("id") + "]");
            itsLabel4.text(value.answer4);

            document.getElementById("answer5").value = value.answer5;
            var itsLabel5 = $("[for=" + $("#answer5").attr("id") + "]");
            itsLabel5.text(value.answer5);
        } else {
            document.getElementById("answer1").remove();
            document.getElementById("answer2").remove();
            document.getElementById("answer3").remove();
            document.getElementById("answer4").remove();
            document.getElementById("answer5").remove();

            document.getElementById("labelAnswer1").remove();
            document.getElementById("labelAnswer2").remove();
            document.getElementById("labelAnswer3").remove();
            document.getElementById("labelAnswer4").remove();
            document.getElementById("labelAnswer5").remove();
        }


        if (value.alreadyAnswered == "True") {
            $("#hintButton").css("background", "grey");
            $("#answerButton").css("background", "grey");
            $("#prevHint").css("background", "grey");
            $("#nextHint").css("background", "grey");
            $("#addLine").css("background", "grey");
            $("#removeLine").css("background", "grey");
            document.getElementById("hintButton").disabled = true;
            document.getElementById("answerButton").disabled = true;
            document.getElementById("nextHint").disabled = true;
            document.getElementById("prevHint").disabled = true;
            document.getElementById("addLine").disabled = true;
            document.getElementById("removeLine").disabled = true;
            $(':radio:not(:checked)').attr('disabled', true);
        }

        document.getElementById("hintThumbsDown").disabled = true;
        document.getElementById("hintThumbsUp").disabled = true;
    }

    function feedbackSuccess(message) {
        alert(message)
    }

    function showFullExplanation(value) {
        enableButton("explanationButton")
        //document.getElementById('hint').innerHTML = value.explanation;

        var askQuestionButton = document.getElementById("askQuestion");
        var hintButton = document.getElementById("hintButton");
        var explanationButton = document.getElementById("explanationButton");

        askQuestionButton.style.display = 'none';
        hintButton.style.display = 'block';
        explanationButton.style.display = 'none';

        hints.push(value.explanation);
        hintsIds.push(0);
        hintsTypes.push("explanation");
        hintsSentFeedback.push(false);
        actualHint = hints.length - 1;
        document.getElementById('hint').innerHTML = hints[actualHint];

        document.getElementById("hintThumbsDown").disabled = true;
        document.getElementById("hintThumbsUp").disabled = true;
    }

    function showHint(value) {
        enableButton("hintButton")
        var askQuestionButton = document.getElementById("askQuestion");
        var hintButton = document.getElementById("hintButton");
        var explanationButton = document.getElementById("explanationButton");

        if (value.lastHint == true) {
            askQuestionButton.style.display = 'block';
            hintButton.style.display = 'none';
            explanationButton.style.display = 'none';
        } else {
            askQuestionButton.style.display = 'none';
            explanationButton.style.display = 'none';
            hintButton.style.display = 'block';
        }

         
        if (value.status == 'OK') {

            //Tratar os cassos
            //tenho nada e peço uma dica, e depois digito algo: vem de novo a primeira
            //Tenho tudo certo, e apago para ter dica do último passo (faz sentido?)

            //Mostrar que a linha está OK, por agora fazer nada
            //$('#hint', element).append("\n" + value.hint);
            //if (hintsIds.includes(value.hintId) && value.hintId != 0) {
            if (hintsIds.includes(value.hintId) && hintsTypes[hintsIds.indexOf(value.hintId)] == value.hintType && value.hintId != 0) {
                actualHint = hintsIds.indexOf(value.hintId)
            } else if (hints.includes(value.hint) && value.hintId == 0) {
                actualHint = hints.indexOf(value.hint)
            } else {
                hints.push(value.hint);
                hintsIds.push(value.hintId);
                hintsTypes.push(value.hintType);
                hintsSentFeedback.push(false);
                actualHint = hints.length - 1;
            }
            document.getElementById('hint').innerHTML = hints[actualHint];
            
            if (value.hintId == 0 || hintsSentFeedback[actualHint]) {
                document.getElementById("hintThumbsDown").disabled = true;
                document.getElementById("hintThumbsUp").disabled = true;
            } else {
                document.getElementById("hintThumbsDown").disabled = false;
                document.getElementById("hintThumbsUp").disabled = false;
            }

            //Mostrar que está tudo certo
            for (var i = minimumCheckboxLLineId; i < checkboxLineId; i++) {
                var partialAnswer = document.getElementById("idt" + i);
                if (partialAnswer.value) {
                    partialAnswer.style.background = rightAnswerColor
                } else {
                    partialAnswer.style.background = noneAnswerColor
                }
            }

        } else {
            //Coloca a dica na pilha
            //$('#hint', element).append("\n" + value.hint);
            if (hintsIds.includes(value.hintId)) {
                actualHint = hintsIds.indexOf(value.hintId)
            } else if (hints.includes(value.hint) && value.hintId == 0) {
                actualHint = hints.indexOf(value.hint)
            } else {
                hints.push(value.hint);
                hintsIds.push(value.hintId);
                hintsTypes.push(value.hintType);
                hintsSentFeedback.push(false);
                actualHint = hints.length - 1;
            }
            document.getElementById('hint').innerHTML = hints[actualHint];

            if (value.hintId == 0 || hintsSentFeedback[actualHint]) {
                document.getElementById("hintThumbsDown").disabled = true;
                document.getElementById("hintThumbsUp").disabled = true;
            } else {
                document.getElementById("hintThumbsDown").disabled = false;
                document.getElementById("hintThumbsUp").disabled = false;
            }

            //Pega cada uma das respostas do usuário
            var removeBack = false
            for (var i = minimumCheckboxLLineId; i < checkboxLineId; i++) {
                var partialAnswer = document.getElementById("idt" + i);
                if (partialAnswer.value == value.wrongElement && !removeBack) {
                    if (value.wrongElementCorrectness < 0) {
                        partialAnswer.style.background = wrongAnswerColor
                    } else {
                        partialAnswer.style.background = doubtAnswerColor
                    }
                    removeBack = true

                } else {
                    if (removeBack) {
                        partialAnswer.style.background = noneAnswerColor
                    } else {
                        partialAnswer.style.background = rightAnswerColor
                    }
                }
            }
        }
    }

    function showResults(value) {
        enableButton("answerButton")
        if(value.error) {
            alert(value.error);
            return;
        }
        $("#hintButton").css("background","grey");
        $("#answerButton").css("background","grey");
        $("#prevHint").css("background","grey");
        $("#nextHint").css("background","grey");
        $("#askQuestion").css("background","grey");
        $("#explanationButton").css("background","grey");
        $("#addLine").css("background","grey");
        $("#removeLine").css("background","grey");
        $("#hintThumbsDown").css("background","grey");
        $("#hintThumbsUp").css("background","grey");

        document.getElementById("hintButton").disabled = true;
        document.getElementById("answerButton").disabled = true;
        document.getElementById("nextHint").disabled = true;
        document.getElementById("prevHint").disabled = true;
        document.getElementById("askQuestion").disabled = true;
        document.getElementById("explanationButton").disabled = true;
        document.getElementById("addLine").disabled = true;
        document.getElementById("removeLine").disabled = true;
        document.getElementById("hintThumbsDown").disabled = true;
        document.getElementById("hintThumbsUp").disabled = true;


        for (var i = minimumCheckboxLLineId; i < checkboxLineId; i++) {
            var checkBox = document.getElementById("id" + i);
            checkBox.style.visibility = 'hidden'
            checkBox.checked = false;
            var line = document.getElementById("idt" + i);
            line.setAttribute("readOnly", true);
        }

        $(':radio:not(:checked)').attr('disabled', true);
        alert(value.message);

        if (value.minimalStep.length > 0) {
            for(var i = 0; i < value.minimalStep.length; i++){
                feedback = prompt(stepMessage[language] + value.minimalStep[i] + " --> " + value.minimalStep[++i] + yesOrNoMessage[language]);

                if (feedback && checkIfUserInputIsValid(feedback)) {
                    $.ajax({
                        type: "POST",
                        url: send_feedback,
                        data: JSON.stringify({ type: "minimalStep", message: getUserAnswer(feedback), nodeFrom: value.minimalStep[i - 1], nodeTo: value.minimalStep[i] })
                    });
                }
            }
        }
        if (value.minimalState.length > 0) {
            for(var i = 0; i < value.minimalState.length; i++){
                promptMessage = stateMessage1[language] + value.minimalState[i] + stateMessage2[language]
                for (var j = 0; j < value.minimalStateResolutions[i].length; j++) {
                    promptMessage = promptMessage.concat(value.minimalStateResolutions[i][j])
                    if (j != value.minimalStateResolutions[i].length - 1) {
                        promptMessage = promptMessage.concat(" --> ")
                    }
                }
                promptMessage = promptMessage.concat(yesOrNoMessage[language])

                feedback = prompt(promptMessage);

                if (feedback && checkIfUserInputIsValid(feedback)) {
                    $.ajax({
                        type: "POST",
                        url: send_feedback,
                        data: JSON.stringify({ type: "minimalState", message: getUserAnswer(feedback), node: value.minimalState[i]})
                    });
                }
            }
        }

        if (value.errorSpecific.length > 0) {
            for(var i = 0; i < value.errorSpecific.length; i++){
                var feedback = prompt(errorSpecificMessages[language] + value.errorSpecific[i] + " --> " + value.errorSpecific[i + 1]);

                if (feedback != null && (feedback.replace(/\s/g, '').length)) {
                    $.ajax({
                        type: "POST",
                        url: send_feedback,
                        data: JSON.stringify({ type: "errorSpecific", message: feedback, nodeFrom: value.errorSpecific[i], nodeTo: value.errorSpecific[++i] })
                    });
                } else {
                    i++;
                }
            }
        }

        //Desabilitado por agora
        //if (value.knowledgeComponent.length > 0) {
        //    for(var i = 0; i < value.knowledgeComponent.length; i++){
        //        var feedback = prompt("Para o seguinte passo, qual elemento básico você considera necessário para resolvê-lo?\n" + value.knowledgeComponent[i] + " --> " + value.knowledgeComponent[i + 1]);

        //        if (feedback != null && (str.replace(/\s/g, '').length)) {
        //            $.ajax({
        //                type: "POST",
        //                url: send_feedback,
        //                data: JSON.stringify({ type: "knowledgeComponent", message: feedback, nodeFrom: value.knowledgeComponent[i], nodeTo: value.knowledgeComponent[++i] })
        //            });
        //        } else {
        //            i++;
        //        }
        //    }
        //}

        if (value.hints.length > 0) {
            for(var i = 0; i < value.hints.length; i++){
                var feedback = prompt(hintMessages[language] + value.hints[i] + " -> " + value.hints[i + 1]);

                if (feedback != null && (feedback.replace(/\s/g, '').length)) {
                    $.ajax({
                        type: "POST",
                        url: send_feedback,
                        data: JSON.stringify({ type: "hint", message: feedback, nodeFrom: value.hints[i], nodeTo: value.hints[++i] })
                    });
                } else {
                    i++;
                }
            }
        }
        if (value.explanation.length > 0) {
            for(var i = 0; i < value.explanation.length; i++){
                var feedback = prompt(explanationMessages[language] + value.explanation[i] + " --> " + value.explanation[i + 1]);

                if (feedback != null && (feedback.replace(/\s/g, '').length)) {
                    $.ajax({
                        type: "POST",
                        url: send_feedback,
                        data: JSON.stringify({ type: "explanation", message: feedback, nodeFrom: value.explanation[i], nodeTo: value.explanation[++i] })
                    });
                } else {
                    i++;
                }
            }
        }
        if (value.doubtsSteps.length > 0) {
            for(var i = 0; i < value.doubtsSteps.length; i++){
                if (!doubtIds.includes(value.doubtsSteps[i].doubtId)) {
                    var feedback = prompt(stepDoubtMessage1[language] + value.doubtsSteps[i].message + stepDoubtMessage2[language] + value.doubtsSteps[i].source + " --> " + value.doubtsSteps[i].dest);
                    if (feedback != null && (feedback.replace(/\s/g, '').length)) {
                        $.ajax({
                            type: "POST",
                            url: send_feedback,
                            data: JSON.stringify({ type: "doubtAnswer", message: feedback, doubtId: value.doubtsSteps[i].doubtId })
                        });
                    }
                }
            }
        }
        if (value.doubtsNodes.length > 0) {
            for(var i = 0; i < value.doubtsNodes.length; i++){
                if (!doubtIds.includes(value.doubtsNodes[i].doubtId)) {
                    var feedback = prompt(stateDoubtMessage1[language] + value.doubtsNodes[i].message + stateDoubtMessage2[language] + value.doubtsNodes[i].node);
                    if (feedback != null && (feedback.replace(/\s/g, '').length)) {
                        $.ajax({
                            type: "POST",
                            url: send_feedback,
                            data: JSON.stringify({ type: "doubtAnswer", message: feedback, doubtId: value.doubtsNodes[i].doubtId })
                        });
                    }
                }
            }
        }
        $.ajax({
          type: "POST",
          url: finishActivityTime,
          data: "{}",
          success: function (value) {
            alert("This is your confirmation code, please use it to confirm your participation on the experiment: " + value.confirmationCode)
            }
        });
    }

    async function updatePositions() {
        $.ajax({
          type: "POST",
          url: update_positions,
          data: "{}"
        });
    }

    async function updateResolutionsCorrectness() {
        $.ajax({
          type: "POST",
          url: update_resolution_correctness,
          data: "{}"
        });
    }


    $(document).ready(function(eventObject) {
        $.ajax({
            type: "POST",
            url: getInitialData,
            data: JSON.stringify({}),
            success: defineValues
        });
        newLineAndCheckbox();
    });

    $('#hintButton', element).click(function(eventObject) {
        if (checkIfContainsInvalidFields()) {
            alert(invalidFieldValuesMessage[language])
            return
        }
        if (checkIfContainsSelfLoops()) {
            alert(selfLoopMessage[language])
            return
        }
        if (checkIfContainsOnlySpacesStep()) {
            alert(onlySpacesMessage[language])
            return
        }
        
        disableButton("hintButton")
        var userAnswer = getCompleteAnswer()

        $.ajax({
            type: "POST",
            url: get_hint_for_last_step,
            data: JSON.stringify({userAnswer: userAnswer}),
            success: showHint
        });
    });

    $('#explanationButton', element).click(function(eventObject) {
        disableButton("explanationButton")
        $.ajax({
            type: "POST",
            url: return_full_explanation,
            data: "{}",
            success: showFullExplanation
        });
    });

    function checkIfContainsInvalidFields() {
        for (var i = minimumCheckboxLLineId; i < checkboxLineId; i++) {
            var partialAnswer = document.getElementById("idt" + i);
            if (partialAnswer.value == "_start_" || partialAnswer.value == "_end_") {
                return true
            }
        }
        return false
    }

    function checkIfSpecialCase() {
        foundEmpty = false
        for (var i = minimumCheckboxLLineId; i < checkboxLineId; i++) {
            if (foundEmpty) {
                return true
            }
            if (document.getElementById("idt" + i).value == '') {
                foundEmpty = true
            }
        }
        return false
    }

    function checkIfContainsOnlySpacesStep() {
        for (var i = minimumCheckboxLLineId; i < checkboxLineId; i++) {
            var partialAnswer = transformToSimplerAnswer(document.getElementById("idt" + i).value);

            if (document.getElementById("idt" + i).value == '') {
                if (checkIfSpecialCase()) {
                    return true
                }

            } else if (!(partialAnswer.replace(/\s/g, '').length)) {
                return true
            }
        }
        return false
    }

    function checkIfContainsLessThanTwoStep() {
        count = 0
        for (var i = minimumCheckboxLLineId; i < checkboxLineId; i++) {
            var partialAnswer = transformToSimplerAnswer(document.getElementById("idt" + i).value);
            if (partialAnswer && (partialAnswer.replace(/\s/g, '').length)) {
                count++
            }
        }
        if (count < 2) {
            return true
        } 
        return false
    }

    function checkIfContainsSelfLoops() {
        previousAnswer = null
        for (var i = minimumCheckboxLLineId; i < checkboxLineId; i++) {
            var partialAnswer = transformToSimplerAnswer(document.getElementById("idt" + i).value);
            if (previousAnswer && previousAnswer == partialAnswer) {
                return true
            }
            previousAnswer = partialAnswer
        }
        return false
    }

    function getCompleteAnswer() {
        var completeAnswer = "";
        for (var i = minimumCheckboxLLineId; i < checkboxLineId; i++) {
            var partialAnswer = document.getElementById("idt" + i);
            completeAnswer = completeAnswer.concat(partialAnswer.value)
            completeAnswer = completeAnswer.concat("\n")
        }

        return completeAnswer.substring(0, completeAnswer.length - 1);
    }

    $('#answerButton', element).click(function(eventObject) {
        if (checkIfContainsInvalidFields()) {
            alert(invalidFieldValuesMessage[language])
            return
        }
        if (checkIfContainsSelfLoops()) {
            alert(selfLoopMessage[language])
            return
        }
        if (checkIfContainsLessThanTwoStep()) {
            alert(invalidSolution[language])
            return
        }
        if (checkIfContainsOnlySpacesStep()) {
            alert(onlySpacesMessage[language])
            return
        }
        disableButton("answerButton")
        var userAnswer = getCompleteAnswer()
        if (userAnswer.replace(/(\r\n|\n|\r)/gm, "") == "") {
            alert(emptyResolutionMessage[language])
            return
        }
        var radioAnswer = $("input:radio[name=radioAnswer]:checked").val()

        $.ajax({
            type: "POST",
            url: send_answer,
            data: JSON.stringify({answer: userAnswer, radioAnswer: radioAnswer}),
            success: function (value) {
                updatePositions()
                updateResolutionsCorrectness()
                showResults(value)
            } 
        });

    });

    function removeLineAndCheckbox() {
        if ((checkboxLineId - 1) > minimumCheckboxLLineId) { 
            checkboxLineId--;
            var checkbox = document.getElementById("id" + checkboxLineId);
            var line = document.getElementById("idt" + checkboxLineId);

            checkbox.remove();
            line.remove();

        }
        enableHintButton()

    }

    function enableExplanationButton() {
        var askQuestionButton = document.getElementById("askQuestion");
        var hintButton = document.getElementById("hintButton");
        var explanationButton = document.getElementById("explanationButton");

        askQuestionButton.style.display = 'none';
        hintButton.style.display = 'none';
        explanationButton.style.display = 'block';

        for (var i = minimumCheckboxLLineId; i < checkboxLineId; i++) {
            var checkBox = document.getElementById("id" + i);
            checkBox.style.visibility = 'hidden'
            checkBox.checked = false;
        }
    }

    function enableHintButton() {
        var askQuestionButton = document.getElementById("askQuestion");
        var hintButton = document.getElementById("hintButton");
        var explanationButton = document.getElementById("explanationButton");

        askQuestionButton.style.display = 'none';
        hintButton.style.display = 'block';
        explanationButton.style.display = 'none';

        for (var i = minimumCheckboxLLineId; i < checkboxLineId; i++) {
            var checkBox = document.getElementById("id" + i);
            checkBox.style.visibility = 'hidden'
            checkBox.checked = false;
        }
    }

    function newLineAndCheckbox() {
        var ul = document.getElementById("checkBoxList");
        var li = document.createElement("li");

        var checkbox = document.createElement('input');
        checkbox.type = "checkbox";
        checkbox.name = "name";
        checkbox.value = "value";
        checkbox.id = "id" + checkboxLineId;
        checkbox.style.visibility = 'hidden'
        li.style.margin = 0
        li.style.padding = 0


        var ul2 = document.getElementById("lineList");
        var li2 = document.createElement("li");
        var text = document.createElement('input');
        text.type = "text";
        text.name = "name";
        text.id = "idt" + checkboxLineId;
        text.style.height= "20px";
        li2.style.margin = 0
        li2.style.padding = 0
        li2.appendChild(text);
        ul2.appendChild(li2);

        li.appendChild(checkbox);
        ul.appendChild(li);

        checkboxLineId++;

        enableHintButton()
    }

    function addDoubtIdtoList(doubtId) {
        doubtIds.push(doubtId)
    }

    $('#askQuestion', element).click(function(eventObject) {
        if (checkIfContainsInvalidFields()) {
            alert(invalidFieldValuesMessage[language])
            return
        }
        if (checkIfContainsSelfLoops()) {
            alert(selfLoopMessage[language])
            return
        }
        if (checkIfContainsOnlySpacesStep()) {
            alert(onlySpacesMessage[language])
            return
        }
        disableButton("askQuestion")
        var currentStep = null
        var checkedBoxes = []

        for (var i = checkboxLineId - 1; i >= minimumCheckboxLLineId; i--) {
            currentStep = document.getElementById("idt" + i);
            if (currentStep.value != "" && checkedBoxes.length < 2) {
                checkedBoxes.push(i)
            }
        }
        
        if (checkedBoxes.length == 2) {
            checkedBoxes = checkedBoxes.reverse()
        }

        var firstNode = document.getElementById("idt" + checkedBoxes[0]);
        var secondNode = document.getElementById("idt" + checkedBoxes[1]);

        if (secondNode) {
            choice = prompt(newDoubtMessage1[language]
                + firstNode.value + "-->" + secondNode.value
                + newDoubtMessage2[language]
                + secondNode.value
                + newDoubtMessage3[language]);

            if (choice == null) {
                enableButton("askQuestion")
                enableHintButton()
                return
            }
            if ((choice.toLowerCase() != doubtChoiceFirst[language] && choice.toLowerCase() != doubtChoiceSecond[language])) {
                alert(invalidDoubtChoiceMessage[language])
                enableButton("askQuestion")
                return
            }
        } else {
            if (language == 0) {
                choice = "segundo"

            } else {
                choice = "second"
            }
        }

        if (choice.toLowerCase() == doubtChoiceSecond[language]) {

            var sourceNode = document.getElementById("idt" + checkedBoxes[0]);
            var destNode = document.getElementById("idt" + checkedBoxes[1]);

            if (destNode && destNode.value != "") {
                var choosenNode = destNode.value
            } else {
                var choosenNode = sourceNode.value
            }

            $.ajax({
                type: "POST",
                url: getDoubtsAndAnswerFromState,
                data: JSON.stringify({ node: choosenNode }),
                success: getOrShowStateDoubt
            });

            function getOrShowStateDoubt(message) {
                enableButton("askQuestion")
                if (message.doubts.length == 0) {
                    var sourceNode = document.getElementById("idt" + checkedBoxes[0]);
                    var destNode = document.getElementById("idt" + checkedBoxes[1]);
                    if (destNode && destNode.value != "") {
                        var doubtNodeValue = destNode.value
                    } else {
                        var doubtNodeValue = sourceNode.value
                    }
                    doubt = prompt(whatDoubtStateMessage[language] + doubtNodeValue);

                    if (destNode) {
                        var sourceNodeValue = sourceNode.value
                        var destNodeValue = destNode.value
                    } else {
                        var sourceNodeValue = "_start_"
                        var destNodeValue = sourceNode.value
                    }

                    if (doubt != null && (doubt.replace(/\s/g, '').length)) {
                        $.ajax({
                            type: "POST",
                            url: send_feedback,
                            data: JSON.stringify({ type: "doubtState", message: doubt, nodeTo: destNodeValue, nodeFrom: sourceNodeValue }),
                            success: function (value) {
                                alert(doubtSentMessage[language])
                                addDoubtIdtoList(value.doubtId)
                            }
                        });
                    }
                } else {
                    for (var i = 0; i < message.doubts.length; i++) {
                        if (message.doubts[i].id) {
                            $.ajax({
                                type: "POST",
                                url: increaseFeedbackCount,
                                data: JSON.stringify({ type: "doubt", id: message.doubts[i].id })
                            });
                        }
                        sameDoubt = prompt(sameDoubtMessage[language] + message.doubts[i].text)
                        if (sameDoubt && checkIfUserInputIsValid(sameDoubt) && getUserAnswer(sameDoubt) == yesUniversalAnswer) {
                            if (message.doubts[i].answers.length == 0) {
                                alert(alreadyCreatedDoubtMessage[language])
                            } else {
                                for (var j = 0; j < message.doubts[i].answers.length; j++) {
                                    $.ajax({
                                        type: "POST",
                                        url: increaseFeedbackCount,
                                        data: JSON.stringify({ type: "answer", id: message.doubts[i].answers[j].id })
                                    });
                                    doubtAnswer = prompt(answerMessage[language] + message.doubts[i].answers[j].text)
                                    if (doubtAnswer && checkIfUserInputIsValid(doubtAnswer) && getUserAnswer(doubtAnswer) == yesUniversalAnswer) {
                                        answerUsefulness = message.doubts[i].answers[j].usefulness
                                        answerUsefulness++
                                        $.ajax({
                                            type: "POST",
                                            url: submitDoubtAnswerInfo,
                                            data: JSON.stringify({ id: message.doubts[i].answers[j].id, text: message.doubts[i].answers[j].text, usefulness: answerUsefulness })
                                        });
                                        j = message.doubts[i].answers.length
                                    } else if (doubtAnswer && checkIfUserInputIsValid(doubtAnswer) && getUserAnswer(doubtAnswer) == noUniversalAnswer) {
                                        answerUsefulness = message.doubts[i].answers[j].usefulness
                                        answerUsefulness--
                                        $.ajax({
                                            type: "POST",
                                            url: submitDoubtAnswerInfo,
                                            data: JSON.stringify({ id: message.doubts[i].answers[j].id, text: message.doubts[i].answers[j].text, usefulness: answerUsefulness })
                                        });
                                    }
                                }
                            }
                            i = message.doubts.length
                        }
                    }
                    newDoubt = prompt(stillHaveDoubts[language])
                    if (newDoubt && checkIfUserInputIsValid(newDoubt) && getUserAnswer(newDoubt) == yesUniversalAnswer) {
                        var sourceNode = document.getElementById("idt" + checkedBoxes[0]);
                        var destNode = document.getElementById("idt" + checkedBoxes[1]);

                        if (destNode && destNode.value != "") {
                            var doubtNodeValue = destNode.value
                        } else {
                            var doubtNodeValue = sourceNode.value
                        }
                        doubt = prompt(whatDoubtStateMessage[language] + doubtNodeValue);

                        if (destNode) {
                            var sourceNodeValue = sourceNode.value
                            var destNodeValue = destNode.value
                        } else {
                            var sourceNodeValue = "_start_"
                            var destNodeValue = sourceNode.value
                        }

                        if (doubt != null && (doubt.replace(/\s/g, '').length)) {
                            $.ajax({
                                type: "POST",
                                url: send_feedback,
                                data: JSON.stringify({ type: "doubtState", message: doubt, nodeTo: destNodeValue, nodeFrom: sourceNodeValue }),
                                success: function (value) {
                                    alert(doubtSentMessage[language])
                                    addDoubtIdtoList(value.doubtId)
                                }
                            });
                        }
                    }
                }
                $.ajax({
                    type: "POST",
                    url: checkIfUseAiExplanation,
                    data: "{}",
                    success: function (value) {
                        if (value.callOpenAiExplanation == "true") {
                            enableExplanationButton()
                        } else {
                            enableHintButton()
                        }
                    }
                });
            }

        } else {
            var sourceNode = document.getElementById("idt" + checkedBoxes[0]);
            var destNode = document.getElementById("idt" + checkedBoxes[1]);

            if (sourceNode.value == "" || destNode.value == "") {
                alert("Selecione apenas passos que contenham algo escrito")
                return
            }
            $.ajax({
                type: "POST",
                url: getDoubtsAndAnswerFromStep,
                data: JSON.stringify({ from: sourceNode.value, to: destNode.value }),
                success: getOrShowStepDoubt
            });

            function getOrShowStepDoubt(message) {
                enableButton("askQuestion")
                if (message.doubts.length == 0) {
                    var sourceNode = document.getElementById("idt" + checkedBoxes[0]);
                    var destNode = document.getElementById("idt" + checkedBoxes[1]);

                    doubt = prompt(whatDoubtStepMessage[language] + sourceNode.value + " -> " + destNode.value);

                    if (doubt != null && (doubt.replace(/\s/g, '').length)) {
                        $.ajax({
                            type: "POST",
                            url: send_feedback,
                            data: JSON.stringify({ type: "doubtStep", message: doubt, nodeFrom: sourceNode.value, nodeTo: destNode.value }),
                            success: function (value) {
                                alert(doubtSentMessage[language])
                                addDoubtIdtoList(value.doubtId)
                            }
                        });
                    }
                } else {
                    for (var i = 0; i < message.doubts.length; i++) {
                        $.ajax({
                            type: "POST",
                            url: increaseFeedbackCount,
                            data: JSON.stringify({ type: "doubt", id: message.doubts[i].id })
                        });
                        sameDoubt = prompt(sameDoubtMessage[language] + message.doubts[i].text)
                        if (sameDoubt && checkIfUserInputIsValid(sameDoubt) && getUserAnswer(sameDoubt) == yesUniversalAnswer) {
                            if (message.doubts[i].answers.length == 0) {
                                alert(alreadyCreatedDoubtMessage[language])
                            } else {
                                for (var j = 0; j < message.doubts[i].answers.length; j++) {
                                    $.ajax({
                                        type: "POST",
                                        url: increaseFeedbackCount,
                                        data: JSON.stringify({ type: "answer", id: message.doubts[i].answers[j].id })
                                    });
                                    doubtAnswer = prompt(answerMessage[language] + message.doubts[i].answers[j].text)
                                    if (doubtAnswer && checkIfUserInputIsValid(doubtAnswer) && getUserAnswer(doubtAnswer) == yesUniversalAnswer) {
                                        answerUsefulness = message.doubts[i].answers[j].usefulness
                                        answerUsefulness++
                                        $.ajax({
                                            type: "POST",
                                            url: submitDoubtAnswerInfo,
                                            data: JSON.stringify({ id: message.doubts[i].answers[j].id, text: message.doubts[i].answers[j].text, usefulness: answerUsefulness })
                                        });
                                        j = message.doubts[i].answers.length
                                    } else if (doubtAnswer && checkIfUserInputIsValid(sameDoubt) && getUserAnswer(sameDoubt) == noUniversalAnswer) {
                                        answerUsefulness = message.doubts[i].answers[j].usefulness
                                        answerUsefulness--
                                        $.ajax({
                                            type: "POST",
                                            url: submitDoubtAnswerInfo,
                                            data: JSON.stringify({ id: message.doubts[i].answers[j].id, text: message.doubts[i].answers[j].text, usefulness: answerUsefulness })
                                        });
                                    }
                                }
                            }
                            i = message.doubts.length
                        }
                    }
                    newDoubt = prompt(stillHaveDoubts[language])
                    if (newDoubt && checkIfUserInputIsValid(newDoubt) && getUserAnswer(newDoubt) == yesUniversalAnswer) {
                        var sourceNode = document.getElementById("idt" + checkedBoxes[0]);
                        var destNode = document.getElementById("idt" + checkedBoxes[1]);

                        doubt = prompt(whatDoubtStepMessage[language] + sourceNode.value + " -> " + destNode.value);

                        if (doubt != null && (doubt.replace(/\s/g, '').length)) {
                            $.ajax({
                                type: "POST",
                                url: send_feedback,
                                data: JSON.stringify({ type: "doubtStep", message: doubt, nodeFrom: sourceNode.value, nodeTo: destNode.value }),
                                success: function (value) {
                                    alert(doubtSentMessage[language])
                                    addDoubtIdtoList(value.doubtId)
                                }
                            });
                        }
                    }
                }
                $.ajax({
                    type: "POST",
                    url: checkIfUseAiExplanation,
                    data: "{}",
                    success: function (value) {
                        if (value.callOpenAiExplanation == "true") {
                            enableExplanationButton()
                        } else {
                            enableHintButton()
                        }
                    }
                });
            }
        }

    });

    $('#addLine', element).click(function(eventObject) {
        newLineAndCheckbox()
    });

    $('#removeLine', element).click(function(eventObject) {
        removeLineAndCheckbox()
    });

    $('#hintThumbsUp', element).click(function(eventObject) {
        if (hintsIds[actualHint] != 0) {
            var sentFeedback = false
            if (hintsTypes[actualHint] == "hint") {
                $.ajax({
                    type: "POST",
                    url: recommend_feedback,
                    data: JSON.stringify({ message: yesUniversalAnswer, existingHint: hints[actualHint], existingHintId: hintsIds[actualHint], existingType: "hint" })
                });
                sentFeedback = true
            } else if (hintsTypes[actualHint] == "explanation") {
                $.ajax({
                    type: "POST",
                    url: recommend_feedback,
                    data: JSON.stringify({ message: yesUniversalAnswer, existingHint: hints[actualHint], existingHintId: hintsIds[actualHint], existingType: "explanation" })
                });
                sentFeedback = true
            } else if (hintsTypes[actualHint] == "errorSpecificFeedback") {
                $.ajax({
                    type: "POST",
                    url: recommend_feedback,
                    data: JSON.stringify({ message: yesUniversalAnswer, existingHint: hints[actualHint], existingHintId: hintsIds[actualHint], existingType: "errorSpecificFeedback" })
                });
                sentFeedback = true
            }

            if (sentFeedback) {
                hintsSentFeedback[actualHint] = true;
                $("#hintThumbsDown").css("background","grey");
                $("#hintThumbsUp").css("background","grey");
                document.getElementById("hintThumbsDown").disabled = true;
                document.getElementById("hintThumbsUp").disabled = true;
            }
        }
    });

    $('#hintThumbsDown', element).click(function(eventObject) {
        if (hintsIds[actualHint] != 0) {
            var sentFeedback = false
            if (hintsTypes[actualHint] == "hint") {
                $.ajax({
                    type: "POST",
                    url: recommend_feedback,
                    data: JSON.stringify({ message: noUniversalAnswer, existingHint: hints[actualHint], existingHintId: hintsIds[actualHint], existingType: "hint" })
                });
                sentFeedback = true
            } else if (hintsTypes[actualHint] == "explanation") {
                $.ajax({
                    type: "POST",
                    url: recommend_feedback,
                    data: JSON.stringify({ message: noUniversalAnswer, existingHint: hints[actualHint], existingHintId: hintsIds[actualHint], existingType: "explanation" })
                });
                sentFeedback = true
            } else if (hintsTypes[actualHint] == "errorSpecificFeedback") {
                $.ajax({
                    type: "POST",
                    url: recommend_feedback,
                    data: JSON.stringify({ message: noUniversalAnswer, existingHint: hints[actualHint], existingHintId: hintsIds[actualHint], existingType: "errorSpecificFeedback" })
                });
                sentFeedback = true
            }

            if (sentFeedback) {
                hintsSentFeedback[actualHint] = true;
                $("#hintThumbsDown").css("background","grey");
                $("#hintThumbsUp").css("background","grey");
                document.getElementById("hintThumbsDown").disabled = true;
                document.getElementById("hintThumbsUp").disabled = true;
            }
        }
    });

    $('#prevHint', element).click(function(eventObject) {
        if (actualHint == -1) {
            return;
        }
        if (actualHint == 0) {
            actualHint = hints.length - 1;
        } else {
            actualHint--;
        }
        document.getElementById('hint').innerHTML = hints[actualHint];

        if (hintsSentFeedback[actualHint] || hintsIds[actualHint] == 0) {
            document.getElementById("hintThumbsDown").disabled = true;
            document.getElementById("hintThumbsUp").disabled = true;
        } else {
            document.getElementById("hintThumbsDown").disabled = false;
            document.getElementById("hintThumbsUp").disabled = false;
        }
    });

    $('#nextHint', element).click(function(eventObject) {
        if (actualHint == -1) {
            return;
        }
        if (actualHint == hints.length - 1) {
            actualHint = 0;
        } else {
            actualHint++;
        }
        document.getElementById('hint').innerHTML = hints[actualHint];

        if (hintsSentFeedback[actualHint] || hintsIds[actualHint] == 0) {
            document.getElementById("hintThumbsDown").disabled = true;
            document.getElementById("hintThumbsUp").disabled = true;
        } else {
            document.getElementById("hintThumbsDown").disabled = false;
            document.getElementById("hintThumbsUp").disabled = false;
        }
    });
    return {};
}
