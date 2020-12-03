/* Javascript for MyXBlock. */
function MyXBlock(runtime, element, data) {

    function defineValues(value) {
        $('#question', element).text(value.title);

        $('#description', element).text(value.description);

        $('#subject', element).text(value.subject);

        //$('#tags', element).text(JSON.parse(value.tags));

        //for (var c in value.tags.{
        //    var newElement = document.createElement('div');
        //    newElement.id = value.tags[c]; 
        //    newElement.className = "car";
        //    newElement.innerHTML = value.tags[c];
        //    document.body.appendChild(newElement);
        //}



        //$('#tags', element).text(value.tags);

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
        //var btn = document.createElement("BUTTON");   // Create a <button> element
        //btn.innerHTML = "CLICK ME";                   // Insert text
        //document.body.appendChild(btn);               // Append <button> to <body>

        //$('.answer', element).text(value.answer);
        $('#hint', element).text(value.hint);
    }

    //showAnswer(data)
    
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

    return {};
}
