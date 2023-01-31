/* Javascript for MyXBlock. */
function MyXBlock(runtime, element, data) {

    var hints = [];
    var hintsIds = [];
    var actualHint = -1;

    var minimumCheckboxLLineId = 1
    var checkboxLineId = minimumCheckboxLLineId

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
    }

    function feedbackSuccess(message) {
        alert(message)
    }

    function showHint(value) {
        if (value.status == 'OK') {

            //Tratar os cassos
            //tenho nada e peço uma dica, e depois digito algo: vem de novo a primeira
            //Tenho tudo certo, e apago para ter dica do último passo (faz sentido?)

            //Mostrar que a linha está OK, por agora fazer nada
            $('#hint', element).append("\n" + value.hint);
            hints.push(value.hint);
            hintsIds.push(value.hintId);
            actualHint = hints.length - 1;
            document.getElementById('hint').innerHTML = hints[actualHint];

            //Mostrar que está tudo certo
            for (var i = minimumCheckboxLLineId; i < checkboxLineId; i++) {
                partialAnswer.style.background = "green"
            }

        } else {
            //Coloca a dica na pilha
            $('#hint', element).append("\n" + value.hint);
            hints.push(value.hint);
            hintsIds.push(value.hintId);
            actualHint = hints.length - 1;
            document.getElementById('hint').innerHTML = hints[actualHint];

            //Pega cada uma das respostas do usuário
            for (var i = minimumCheckboxLLineId; i < checkboxLineId; i++) {
                var partialAnswer = document.getElementById("idt" + i);
                if (partialAnswer.value == value.wrongElement) {
                    partialAnswer.style.background = "red"
                    break;
                } else {
                    partialAnswer.style.background = "green"
                }
            }

            //var lines = $('#userInput').val().split('\n');
            //var endPos = 0;
            //for(var i = 0;i < lines.length;i++){
            //    if(value.wrongElement == lines[i]) {
            //        //Pega as posições e imprime
            //        endPos += lines[i].length; 
            //        if  (i == 0) {
            //            startPos = 0;
            //        } else {
            //            endPos += i;
            //            startPos = endPos - lines[i].length;
            //        }

            //        tarea = document.getElementById("userInput");
            //        tarea.focus();
            //        tarea.selectionStart = startPos;
            //        tarea.selectionEnd = endPos;
            //        tarea.value.substring(tarea.selectionStart, tarea.selectionEnd); 

            //    } else {
            //        endPos += lines[i].length;
            //        continue;
            //    }
            //}

        }
    }

    function showResults(value) {
        if(value.error) {
            alert(value.error);
            return;
        }
        $("#hintButton").css("background","grey");
        $("#answerButton").css("background","grey");
        $("#prevHint").css("background","grey");
        $("#nextHint").css("background","grey");
        //document.getElementById('userInput').readOnly = true;
        document.getElementById("hintButton").disabled = true;
        document.getElementById("answerButton").disabled = true;
        document.getElementById("nextHint").disabled = true;
        document.getElementById("prevHint").disabled = true;
        $(':radio:not(:checked)').attr('disabled', true);
        alert(value.message);

        var hintsToShow = []
        var hintsIdToShow = []
        for (var i = 0; i < hints.length; i++) {
            if (hintsIds[i] != 0 && !hintsToShow.includes(hints[i])) {
                hintsToShow.push(hints[i])
                hintsIdToShow.push(hintsIds[i])
            }
        }

        if (hintsToShow.length > 0) {
            for (var i = 0; i < hintsToShow.length; i++) {
                if (hintsIdToShow[i] != 0) {
                    feedback = prompt("O seguinte feedback foi útil? " + hintsToShow[i])

                    if (feedback != null) {
                        $.ajax({
                            type: "POST",
                            url: recommend_feedback,
                            data: JSON.stringify({ message: feedback, existingHint: hintsToShow[i], existingHintId: hintsIdToShow[i] })
                        });
                    }
                }
            }
        }


        if (value.minimalStep.length > 0) {
            for(var i = 0; i < value.minimalStep.length; i++){
                feedback = prompt("O seguinte passo está correto? " + value.minimalStep[i] + " -> " + value.minimalStep[++i]);

                if (feedback != null) {
                    $.ajax({
                        type: "POST",
                        url: send_feedback,
                        data: JSON.stringify({ type: "minimalStep", message: feedback, nodeFrom: value.minimalStep[i - 1], nodeTo: value.minimalStep[i] }),
                        success: feedbackSuccess
                    });
                }
            }
        }
        if (value.minimalState.length > 0) {
            for(var i = 0; i < value.minimalState.length; i++){
                feedback = prompt("O seguinte estado parece correto em uma resolução? " + value.minimalState[i]);

                if (feedback != null) {
                    $.ajax({
                        type: "POST",
                        url: send_feedback,
                        data: JSON.stringify({ type: "minimalState", message: feedback, node: value.minimalState[i]}),
                        success: feedbackSuccess
                    });
                }
            }
        }
        if (value.errorSpecific.length > 0) {
            for(var i = 0; i < value.errorSpecific.length; i++){
                var feedback = prompt("Como você explicaria que o seguinte passo está incorreto? " + value.errorSpecific[i] + " -> " + value.errorSpecific[++i]);
                if (feedback != null) {
                    $.ajax({
                        type: "POST",
                        url: send_feedback,
                        data: JSON.stringify({ type: "errorSpecific", message: feedback, nodeFrom: value.errorSpecific[i], nodeTo: value.errorSpecific[++i] }),
                        success: feedbackSuccess
                    });
                }
            }
        }
        if (value.explanation.length > 0) {
            for(var i = 0; i < value.explanation.length; i++){
                var feedback = prompt("Como você explicaria que o seguinte passo está correto? " + value.explanation[i] + " -> " + value.explanation[++i]);
                if (feedback != null) {
                    $.ajax({
                        type: "POST",
                        url: send_feedback,
                        data: JSON.stringify({ type: "explanation", message: feedback, nodeFrom: value.errorSpecific[i], nodeTo: value.errorSpecific[++i] }),
                        success: feedbackSuccess
                    });
                }
            }
        }
        if (value.doubtsSteps.length > 0) {
            for(var i = 0; i < value.doubtsSteps.length; i++){
                var feedback = prompt("Como você responderia a seguinte dúvida? " + value.doubtsSteps[i].message + " do passo " + value.doubtsSteps[i].source + " -> " + value.doubtsSteps[i].dest);
                if (feedback != null) {
                    $.ajax({
                        type: "POST",
                        url: send_feedback,
                        data: JSON.stringify({ type: "doubtAnswer", message: feedback, doubtId: value.doubtsSteps[i].doubtId }),
                        success: feedbackSuccess
                    });
                }
            }
        }
        if (value.doubtsNodes.length > 0) {
            for(var i = 0; i < value.doubtsNodes.length; i++){
                var feedback = prompt("Como você responderia a seguinte dúvida? " + value.doubtsNodes[i].message + " do estado " + value.doubtsNodes[i].node);
                if (feedback != null) {
                    $.ajax({
                        type: "POST",
                        url: send_feedback,
                        data: JSON.stringify({ type: "doubtAnswer", message: feedback, doubtId: value.doubtsNodes[i].doubtId }),
                        success: feedbackSuccess
                    });
                }
            }
        }
    }

    async function create_initial_positions() {
        $.ajax({
          type: "POST",
          url: runtime.handlerUrl(element, 'create_initial_positions'),
          data: "{}",
          success: function (data) {
          }   
        });
    }

    var send_answer = runtime.handlerUrl(element, 'send_answer');
    var send_feedback = runtime.handlerUrl(element, 'send_feedback');
    var recommend_feedback = runtime.handlerUrl(element, 'recommend_feedback');
    var get_hint_for_last_step = runtime.handlerUrl(element, 'get_hint_for_last_step');
    var getInitialData = runtime.handlerUrl(element, 'initial_data');
    var getDoubtsAndAnswerFromStep = runtime.handlerUrl(element, 'get_doubts_and_answers_from_step');
    var getDoubtsAndAnswerFromState = runtime.handlerUrl(element, 'get_doubts_and_answers_from_state');
    var submitDoubtAnswerInfo = runtime.handlerUrl(element, 'submit_doubt_answer_info');


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
        var userAnswer = getCompleteAnswer()

        $.ajax({
            type: "POST",
            url: get_hint_for_last_step,
            data: JSON.stringify({userAnswer: userAnswer}),
            success: showHint
        });
    });

    function getCompleteAnswer() {
        var completeAnswer = "";
        for (var i = minimumCheckboxLLineId; i < checkboxLineId; i++) {
            var partialAnswer = document.getElementById("idt" + i);
            completeAnswer = completeAnswer.concat(partialAnswer.value)
            completeAnswer = completeAnswer.concat("\n")
        }
        return completeAnswer;
    }

    $('#answerButton', element).click(function(eventObject) {
        //var userAnswer = $(".userInput").val();
        var userAnswer = getCompleteAnswer()
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
        if (checkboxLineId > minimumCheckboxLLineId) { 
            checkboxLineId--;
            var checkbox = document.getElementById("id" + checkboxLineId);
            var line = document.getElementById("idt" + checkboxLineId);

            checkbox.remove();
            line.remove();
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

    }

    $('#askQuestion', element).click(function(eventObject) {
        var checkedBoxes = []
        for (var i = minimumCheckboxLLineId; i < checkboxLineId; i++) {
            var checkBox = document.getElementById("id" + i);
            if (checkBox.checked) {
                checkedBoxes.push(i)
            }
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
                $.ajax({
                    type: "POST",
                    url: getDoubtsAndAnswerFromState,
                    data: JSON.stringify({node: singleNode.value}),
                    success: getOrShowStateDoubt
                });

                function getOrShowStateDoubt(message) {
                    if (message.doubts.length == 0) {
                        var singleNode = document.getElementById("idt" + checkedBoxes[0]);
                        doubt = prompt("Qual a dúvida para o seguinte estado? " + singleNode.value);
                        if (doubt != null) {
                            $.ajax({
                                type: "POST",
                                url: send_feedback,
                                data: JSON.stringify({ type: "doubtState", message: doubt, node: singleNode.value })
                            });
                        }


                    } else {
                        for (var i = 0; i < message.doubts.length; i++) {
                            sameDoubt = prompt("Essa dúvida é a mesma que você tem? " + message.doubts[i].text)
                            if (sameDoubt && sameDoubt == "s") {
                                for (var j = 0; j < message.doubts[i].answers.length; j++) {
                                    doubtAnswer = prompt("Isso responde sua dúvida ou é útil? " + message.doubts[i].answers[j].text)
                                    if (doubtAnswer && doubtAnswer == "s") {
                                        answerUsefulness = message.doubts[i].answers[j].usefulness
                                        answerUsefulness++
                                        $.ajax({
                                            type: "POST",
                                            url: submitDoubtAnswerInfo,
                                            data: JSON.stringify({id: message.doubts[i].answers[j].id, text: message.doubts[i].answers[j].text, usefulness: answerUsefulness})
                                        });
                                    } else if (doubtAnswer && doubtAnswer == "n") {
                                        answerUsefulness = message.doubts[i].answers[j].usefulness
                                        answerUsefulness--
                                        $.ajax({
                                            type: "POST",
                                            url: submitDoubtAnswerInfo,
                                            data: JSON.stringify({id: message.doubts[i].answers[j].id, text: message.doubts[i].answers[j].text, usefulness: answerUsefulness})
                                        });
                                    }
                                }
                            }
                            i = message.doubts.length
                        }
                        newDoubt = prompt("Ainda gostaria de perguntar uma dúvida?")
                        if (newDoubt && newDoubt == "s") {
                            var singleNode = document.getElementById("idt" + checkedBoxes[0]);
                            doubt = prompt("Qual a dúvida para o seguinte estado? " + singleNode.value);

                            if (doubt != null) {
                                $.ajax({
                                    type: "POST",
                                    url: send_feedback,
                                    data: JSON.stringify({ type: "doubtState", message: doubt, node: singleNode.value })
                                });
                            }
                        }
                    }
                }

            } else {
                var sourceNode = document.getElementById("idt" + checkedBoxes[0]);
                var destNode = document.getElementById("idt" + checkedBoxes[1]);

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

                        doubt = prompt("Qual a dúvida para o seguinte passo? " + sourceNode.value + " -> " + destNode.value);

                        $.ajax({
                            type: "POST",
                            url: send_feedback,
                            data: JSON.stringify({ type: "doubtStep", message: doubt, nodeFrom: sourceNode.value, nodeTo: destNode.value }),
                            success: feedbackSuccess
                        });

                    } else {
                        for (var i = 0; i < message.doubts.length; i++) {
                            sameDoubt = prompt("Essa dúvida é a mesma que você tem? " + message.doubts[i].text)
                            if (sameDoubt && sameDoubt == "s") {
                                for (var j = 0; j < message.doubts[i].answers.length; j++) {
                                    doubtAnswer = prompt("Isso responde sua dúvida ou é útil? " + message.doubts[i].answers[j].text)
                                    if (doubtAnswer && doubtAnswer == "s") {
                                        answerUsefulness = message.doubts[i].answers[j].usefulness
                                        answerUsefulness++
                                        $.ajax({
                                            type: "POST",
                                            url: submitDoubtAnswerInfo,
                                            data: JSON.stringify({id: message.doubts[i].answers[j].id, text: message.doubts[i].answers[j].text, usefulness: answerUsefulness})
                                        });
                                    } else if (doubtAnswer && doubtAnswer == "n") {
                                        answerUsefulness = message.doubts[i].answers[j].usefulness
                                        answerUsefulness--
                                        $.ajax({
                                            type: "POST",
                                            url: submitDoubtAnswerInfo,
                                            data: JSON.stringify({id: message.doubts[i].answers[j].id, text: message.doubts[i].answers[j].text, usefulness: answerUsefulness})
                                        });
                                    }
                                }
                            }
                            i = message.doubts.length
                        }
                        newDoubt = prompt("Ainda gostaria de perguntar uma dúvida?")
                        if (newDoubt && newDoubt == "s") {
                            var sourceNode = document.getElementById("idt" + checkedBoxes[0]);
                            var destNode = document.getElementById("idt" + checkedBoxes[1]);

                            doubt = prompt("Qual a dúvida para o seguinte passo? " + sourceNode.value + " -> " + destNode.value);

                            $.ajax({
                                type: "POST",
                                url: send_feedback,
                                data: JSON.stringify({ type: "doubtStep", message: doubt, nodeFrom: sourceNode.value, nodeTo: destNode.value }),
                                success: feedbackSuccess
                            });
                        }
                    }
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
    });
    return {};
}
