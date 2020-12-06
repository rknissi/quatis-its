/* Javascript for MyXBlock. */
function MyXBlock(runtime, element, data) {

    var hints = [];
    var actualHint = -1;

    function defineValues(value) {
        $('#question', element).text(value.title);

        $('#description', element).text(value.description);

        $('#subject', element).text(value.subject);

        var result = [];
        for(var i in value.tags)
            result.push([value.tags[i]]);
        
        $('#tags', element).text(result);

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
    }

    function showAnswer(value) {
        $('#hint', element).append("\n" + value.hint);
        hints.push(value.hint);
        actualHint = hints.length - 1;
        document.getElementById('hint').innerHTML = hints[actualHint];

        if (value.stepHint != null) {
            var lines = $('#userInput').val().split('\n');

            endPos = 0;

            for(var i = 0;i < lines.length;i++){
                endPos += lines[i].length;
                if (lines[i] == value.stepHint) {
                    tarea = document.getElementById("userInput");
                    if  (i == 0) {
                        startPos = 0;
                    } else {
                        endPos += i;
                        startPos = endPos - lines[i].length;
                    }
                    tarea.focus();
                    tarea.selectionStart = startPos;
                    tarea.selectionEnd = endPos;
                    //$('#userInput').css('font-style', 'italic')
                    var sel = tarea.value.substring(tarea.selectionStart, tarea.selectionEnd); // Gets selection
                    console.log (sel);
                    //var e = document.createElement('p');
                    //$(e).css("z-index", 9999);
                    //$('#userInput').append(e);
                    //var e = document.createElement('span');
                    //e.innerHTML = value.stepHint + "teste UIA"; // Selected text
                    //sel.getRangeAt(0);

                        // https://developer.mozilla.org/en-US/docs/Web/API/Selection/getRangeAt
                        //var range = sel.getRangeAt(0);
                        //range.deleteContents(); // Deletes selected text…
                        //range.insertNode(e); // … and inserts the new element at its place
                }
            }


        }
    }

    var send_answer = runtime.handlerUrl(element, 'send_answer');
    var getInitialData = runtime.handlerUrl(element, 'initial_data');

    $('#userInput').attr("rows", $('#userInput').val().split("\n").length+1||2);

    $(document).ready(function(eventObject) {
        $.ajax({
            type: "POST",
            url: getInitialData,
            data: JSON.stringify({}),
            success: defineValues
        });
    });

    $('.answer', element).click(function(eventObject) {
        var stepAnswer = $(".userInput").val();
        var radioAnswer = $("input:radio[name=radioAnswer]:checked").val()

        $.ajax({
            type: "POST",
            url: send_answer,
            data: JSON.stringify({answer: stepAnswer, radioAnswer: radioAnswer}),
            success: showAnswer
        });
    });

    $('.prevHint', element).click(function(eventObject) {
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

    $('.nextHint', element).click(function(eventObject) {
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
