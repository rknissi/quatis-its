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

    var yesAnswer = ["sim", "s", "yes", "y", "si", "ye"];
    var noAnswer = ["não", "n", "no", "nao"];

    var yesUniversalAnswer = "yes"
    var noUniversalAnswer = "no"

    var wrongAnswerColor = "red"
    var rightAnswerColor = "#03b803" 
    var noneAnswerColor = "none"
    var doubtAnswerColor = "yellow"

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
            //document.getElementById('userInput').readOnly = true;
            document.getElementById("hintButton").disabled = true;
            document.getElementById("answerButton").disabled = true;
            document.getElementById("nextHint").disabled = true;
            document.getElementById("prevHint").disabled = true;
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
            if (hintsIds.includes(value.hintId) && value.hintId != 0) {
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
                if (partialAnswer.value == value.wrongElement) {
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
                feedback = prompt("O seguinte passo está correto?\n" + value.minimalStep[i] + " -> " + value.minimalStep[++i]);

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
                feedback = prompt("O seguinte estado parece correto em uma resolução?\n" + value.minimalState[i]);

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
                var feedback = prompt("Como você explicaria que o seguinte passo está incorreto?\n" + value.errorSpecific[i] + " -> " + value.errorSpecific[i + 1]);

                if (feedback != null) {
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
        //        var feedback = prompt("Para o seguinte passo, qual elemento básico você considera necessário para resolvê-lo?\n" + value.knowledgeComponent[i] + " -> " + value.knowledgeComponent[i + 1]);

        //        if (feedback != null) {
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
                var feedback = prompt("Qual dica você daria para o seguinte passo?\n" + value.explanation[i] + " -> " + value.explanation[i + 1]);

                if (feedback != null) {
                    $.ajax({
                        type: "POST",
                        url: send_feedback,
                        data: JSON.stringify({ type: "hint", message: feedback, nodeFrom: value.explanation[i], nodeTo: value.explanation[++i] })
                    });
                } else {
                    i++;
                }
            }
        }
        if (value.explanation.length > 0) {
            for(var i = 0; i < value.explanation.length; i++){
                var feedback = prompt("Como você explicaria que o seguinte passo está correto?\n" + value.explanation[i] + " -> " + value.explanation[i + 1]);

                if (feedback != null) {
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
                    var feedback = prompt("Como você responderia a seguinte dúvida?\n" + value.doubtsSteps[i].message + "\nDo passo " + value.doubtsSteps[i].source + " -> " + value.doubtsSteps[i].dest);
                    if (feedback != null) {
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
                    var feedback = prompt("Como você responderia a seguinte dúvida?\n" + value.doubtsNodes[i].message + "\nDo estado " + value.doubtsNodes[i].node);
                    if (feedback != null) {
                        $.ajax({
                            type: "POST",
                            url: send_feedback,
                            data: JSON.stringify({ type: "doubtAnswer", message: feedback, doubtId: value.doubtsNodes[i].doubtId })
                        });
                    }
                }
            }
        }
    }

    async function create_initial_positions() {
        $.ajax({
          type: "POST",
          url: runtime.handlerUrl(element, 'create_initial_positions'),
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
        disableButton("answerButton")
        var userAnswer = getCompleteAnswer()
        if (userAnswer.replace(/(\r\n|\n|\r)/gm, "") == "") {
            alert("Sua resolução não pode ser vazia")
            return
        }
        var radioAnswer = $("input:radio[name=radioAnswer]:checked").val()

        $.ajax({
            type: "POST",
            url: send_answer,
            data: JSON.stringify({answer: userAnswer, radioAnswer: radioAnswer}),
            success: function (value) {
                create_initial_positions()
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
        disableButton("askQuestion")
        var currentStep = null
        var lastStep = null
        var checkedBoxes = []

        //Não se esquecer de trocar isso para pegar os dois ultimos estados apenas
        //for (var i = minimumCheckboxLLineId; i < checkboxLineId; i++) {
        //    currentStep = document.getElementById("idt" + i);
        //    if (currentStep.style.background == wrongAnswerColor || currentStep.style.background == doubtAnswerColor) {
        //        if (i > minimumCheckboxLLineId) {
        //            checkedBoxes.push(lastStep)
        //        }
        //        checkedBoxes.push(i)
        //        i = checkboxLineId
        //    } else if (currentStep.value != "") {
        //        lastStep = i
        //    }
        //}

        //if (checkedBoxes.length == 0) {
        //    checkedBoxes.push(lastStep)
        //}

        for (var i = checkboxLineId - 1; i >= minimumCheckboxLLineId; i--) {
            currentStep = document.getElementById("idt" + i);
            if (currentStep.value != "" && checkedBoxes.length < 2) {
                checkedBoxes.push(i)
            }
        }
        
        if (checkedBoxes.length == 2) {
            checkedBoxes = checkedBoxes.reverse()
        }

        if (checkedBoxes.length == 0) {
            alert("Selecione as linhas no qual você tem dúvida!")
        } else if (checkedBoxes.length > 2) {
            alert("Selecione apenas uma ou duas linhas para pedir dúvidas!")
        }else if (checkedBoxes.length == 2 && checkedBoxes[1] - checkedBoxes[0] != 1) {
            alert("Selecione apenas passos consectuivos na resolução")
        } else {
            if (checkedBoxes.length == 1) {

                var singleNode = document.getElementById("idt" + checkedBoxes[0]);
                if (singleNode.value == "") {
                    alert("Selecione apenas passos que contenham algo escrito")
                    return
                }
                $.ajax({
                    type: "POST",
                    url: getDoubtsAndAnswerFromState,
                    data: JSON.stringify({node: singleNode.value}),
                    success: getOrShowStateDoubt
                });

                function getOrShowStateDoubt(message) {
                    enableButton("askQuestion")
                    if (message.doubts.length == 0) {
                        var singleNode = document.getElementById("idt" + checkedBoxes[0]);
                        doubt = prompt("Qual a dúvida para o seguinte estado?\n" + singleNode.value);
                        if (doubt != null) {
                            $.ajax({
                                type: "POST",
                                url: send_feedback,
                                data: JSON.stringify({ type: "doubtState", message: doubt, node: singleNode.value }),
                                success: function (value) {
                                    addDoubtIdtoList(value.doubtId)
                                }
                            });
                        }


                    } else {
                        for (var i = 0; i < message.doubts.length; i++) {
                            sameDoubt = prompt("Essa dúvida é a mesma que você tem?\n" + message.doubts[i].text)
                            if (sameDoubt && checkIfUserInputIsValid(sameDoubt) && getUserAnswer(sameDoubt) == yesUniversalAnswer) {
                                if (message.doubts[i].answers.length == 0) {
                                    alert("Essa dúvida já foi realizada por um colega seu. Estamos esperando alguém responder essa dúvida")
                                } else {
                                    for (var j = 0; j < message.doubts[i].answers.length; j++) {
                                        doubtAnswer = prompt("Isso responde sua dúvida ou é útil?\n" + message.doubts[i].answers[j].text)
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
                        newDoubt = prompt("Ainda lhe restam dúvidas?")
                        if (newDoubt && checkIfUserInputIsValid(newDoubt) && getUserAnswer(newDoubt) == yesUniversalAnswer) {
                            var singleNode = document.getElementById("idt" + checkedBoxes[0]);
                            doubt = prompt("Qual a dúvida para o seguinte estado?\n" + singleNode.value);

                            if (doubt != null) {
                                $.ajax({
                                    type: "POST",
                                    url: send_feedback,
                                    data: JSON.stringify({ type: "doubtState", message: doubt, node: singleNode.value })
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
                    data: JSON.stringify({from: sourceNode.value, to: destNode.value}),
                    success: getOrShowStepDoubt
                });

                function getOrShowStepDoubt(message) {
                    if (message.doubts.length == 0) {
                        var sourceNode = document.getElementById("idt" + checkedBoxes[0]);
                        var destNode = document.getElementById("idt" + checkedBoxes[1]);

                        doubt = prompt("Qual a dúvida para o seguinte passo?\n" + sourceNode.value + " -> " + destNode.value);

                        if (doubt != null) {
                            $.ajax({
                                type: "POST",
                                url: send_feedback,
                                data: JSON.stringify({ type: "doubtStep", message: doubt, nodeFrom: sourceNode.value, nodeTo: destNode.value }),
                                success: function (value) {
                                    addDoubtIdtoList(value.doubtId)
                                }
                            });
                        }
                    } else {
                        for (var i = 0; i < message.doubts.length; i++) {
                            sameDoubt = prompt("Essa dúvida é a mesma que você tem?\n" + message.doubts[i].text)
                            if (sameDoubt && checkIfUserInputIsValid(sameDoubt) && getUserAnswer(sameDoubt) == yesUniversalAnswer) {
                                if (message.doubts[i].answers.length == 0) {
                                    alert("Essa dúvida já foi realizada por um colega seu. Estamos esperando alguém responder essa dúvida")
                                } else {
                                    for (var j = 0; j < message.doubts[i].answers.length; j++) {
                                        doubtAnswer = prompt("Isso responde sua dúvida ou é útil?\n" + message.doubts[i].answers[j].text)
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
                        newDoubt = prompt("Ainda lhe restam dúvidas?")
                        if (newDoubt && checkIfUserInputIsValid(newDoubt) && getUserAnswer(newDoubt) == yesUniversalAnswer) {
                            var sourceNode = document.getElementById("idt" + checkedBoxes[0]);
                            var destNode = document.getElementById("idt" + checkedBoxes[1]);

                            doubt = prompt("Qual a dúvida para o seguinte passo?\n" + sourceNode.value + " -> " + destNode.value);

                            $.ajax({
                                type: "POST",
                                url: send_feedback,
                                data: JSON.stringify({ type: "doubtStep", message: doubt, nodeFrom: sourceNode.value, nodeTo: destNode.value })
                            });
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
                    data: JSON.stringify({ message: yesUniversalAnswer, existingHint: hints[actualHint], existingHintId: hintsIds[actualHint], existingType: "explanation" })
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
                    data: JSON.stringify({ message: noUniversalAnswer, existingHint: hints[actualHint], existingHintId: hintsIds[actualHint], existingType: "explanation" })
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
