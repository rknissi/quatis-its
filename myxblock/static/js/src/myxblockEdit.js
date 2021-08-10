function MyXBlockEdit(runtime, element) {

  var submitDataUrl = runtime.handlerUrl(element, 'submit_data');
  var getGraphurl = runtime.handlerUrl(element, 'generate_graph');

  $('#save_button', element).click(function(eventObject) {
    var el = $(element);
    var data = {
      problemTitle: el.find('input[name=problemTitle]').val(),
      problemDescription: el.find('input[id=problemDescription]').val(),
      problemCorrectRadioAnswer: el.find('input[id=problemCorrectRadioAnswer]').val(),
      problemCorrectSteps: el.find('input[id=problemCorrectSteps]').val(),
      problemTipsToNextStep: el.find('input[id=problemTipsToNextStep]').val(),
      problemDefaultHint: el.find('input[id=problemDefaultHint]').val(),
      problemAnswer1: el.find('input[id=problemAnswer1]').val(),
      problemAnswer2: el.find('input[id=problemAnswer2]').val(),
      problemAnswer3: el.find('input[id=problemAnswer3]').val(),
      problemAnswer4: el.find('input[id=problemAnswer4]').val(),
      problemAnswer5: el.find('input[id=problemAnswer5]').val(),
      problemSubject: el.find('input[id=problemSubject]').val(),
      problemTags: el.find('input[id=problemTags]').val()
    };

    $.ajax({
      type: "POST",
      url: submitDataUrl,
      data: JSON.stringify(data),
      success: function (data) {
          window.location.reload(false);
      }   
  });

  });

  $('#createGraph', element).click(function(eventObject) {
    $.ajax({
      type: "POST",
      url: getGraphurl,
      data: JSON.stringify({}),
      success: function (data) {
        anychart.data.loadJsonFile("https://static.anychart.com/git-storage/word-press/data/network-graph-tutorial/data_images.json", function (data) {

          // create a chart from the loaded data
          var chart = anychart.graph(value.teste);

          // set the title
          chart.title("Network Graph showing the battles in Game of Thrones");

          // access nodes
          var nodes = chart.nodes();

          // set the size of nodes
          nodes.normal().height(30);
          nodes.hovered().height(45);
          nodes.selected().height(45);

          // set the stroke of nodes
          nodes.normal().stroke(null);
          nodes.hovered().stroke("#333333", 3);
          nodes.selected().stroke("#333333", 3);

          // enable the labels of nodes
          chart.nodes().labels().enabled(true);

          // configure the labels of nodes
          chart.nodes().labels().format("{%id}");
          chart.nodes().labels().fontSize(12);
          chart.nodes().labels().fontWeight(600);

          chart.edges().arrows({
            enabled: true,
            size: 15,
            position: '50%'
          });

          // draw the chart
          chart.container("graph").draw();
    })
            //let base64Img = new Image();
            //base64Img.src = "data:image/png;base64," + data.img;
            //document.querySelector(".graph").appendChild(base64Img);
      }   
  });
  });

  $('#cancel_button', element).click(function(eventObject) {
    runtime.notify('cancel', {});
  });
}
