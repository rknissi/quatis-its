function MyXBlockEdit(runtime, element) {

  var submitDataUrl = runtime.handlerUrl(element, 'submit_data');
  var getGraphurl = runtime.handlerUrl(element, 'generate_graph');
  var submitGraphDataUrl = runtime.handlerUrl(element, 'submit_graph_data');
  var getEdgeInfoUrl = runtime.handlerUrl(element, 'get_edge_info');
  var submitErrorSpecificFeedbackUrl = runtime.handlerUrl(element, 'submit_error_specific_feedback');
  var submitExplanationUrl = runtime.handlerUrl(element, 'submit_explanation');
  var submitHintUrl = runtime.handlerUrl(element, 'submit_hint');

  var chart;
  var data;

  var invalidStep = [-1, -0.80001]
  var stronglyInvalidStep = [-0.8, -0.40001]
  var possiblyInvalidStep = [-0.4, -0.00001]
  var neutralStep = [0, 0]
  var possiblyValidStep = [0.00001, 0.39999]
  var stronglyValidStep = [0.4, 0.79999]
  var validStep = [0.8, 1]
  
  var incorrectState = [-1, -0.7]
  var unknownState = [-0.69999, 0.69999]
  var correctState = [0.7, 1]


  function reApplyConfig() {
    document.getElementById("graph").innerHTML = "";

    chart = anychart.graph(data);
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
      size: 15
    });

    chart.container("graph").draw();
  }

  function removeNode(nodeName){
    for (i = 0; i < data.nodes.length; ++i) {
      if (nodeName === data.nodes[i].id) {
        data.nodes.splice(i, 1);
        removeEdgeWithNode(nodeName)
        break;
      }
    }
    reApplyConfig();
  }

  function changeNodeValue(nodeName, value){
    for (i = 0; i < data.nodes.length; ++i) {
      if (nodeName === data.nodes[i].id) {
        nodeData = data.nodes[i];
        data.nodes.splice(i, 1);
        nodeData.id = value;
        addNode(nodeData);
        changeNodeNameInEdges(nodeName, value)
        break;
      }
    }
    reApplyConfig();
  }

  function changeNodeNameInEdges(oldName, newName){
    for (i = 0; i < data.edges.length; ++i) {
      if (oldName === data.edges[i].from) {
        edgeData = data.edges[i];
        data.edges.splice(i, 1);
        edgeData.from = newName;
        addEdge(edgeData);
      }
      if (oldName === data.edges[i].to) {
        edgeData = data.edges[i];
        data.edges.splice(i, 1);
        edgeData.to = newName;
        addEdge(edgeData);
      }
    }
    reApplyConfig();
  }

  function changeNodeToNormal(nodeName){
    for (i = 0; i < data.nodes.length; ++i) {
      if (nodeName === data.nodes[i].id) {
        nodeData = data.nodes[i];
        data.nodes.splice(i, 1);
        nodeData.stroke = null;
        addNode(nodeData);
        break;
      }
    }
    reApplyConfig();
  }

  function changeNodeToInitial(nodeName){
      for (i = 0; i < data.nodes.length; ++i) {
        if (nodeName === data.nodes[i].id) {
          nodeData = data.nodes[i];
          data.nodes.splice(i, 1);
          nodeData.stroke = {"color": "black", "dash": "5 5"};
          addNode(nodeData);
          break;
        }
    }
    reApplyConfig();
  }

  function changeNodeToFinal(nodeName){
      for (i = 0; i < data.nodes.length; ++i) {
        if (nodeName === data.nodes[i].id) {
          nodeData = data.nodes[i];
          data.nodes.splice(i, 1);
          nodeData.stroke = "1 black";
          addNode(nodeData);
          break;
        }
    }
    reApplyConfig();
  }
  
  function changeNodeCorrectness(nodeName, value){
      for (i = 0; i < data.nodes.length; ++i) {
        if (nodeName === data.nodes[i].id) {
          nodeData = data.nodes[i];
          data.nodes.splice(i, 1);
          nodeData.correctness = value;
          nodeData.fill = getNodeColor(value);
          addNode(nodeData);
          break;
        }
    }
    reApplyConfig();
  }

  function changeStepCorrectness(sourceName, distName, value){
      for (i = 0; i < data.edges.length; ++i) {
        if (sourceName === data.edges[i].from && distName === data.edges[i].to) {
          edgeData = data.edges[i];
          data.edges.splice(i, 1);
          edgeData.correctness = value;
          edgeData.stroke = getEdgeColor(value);
          addEdge(edgeData);
          break;
        }
    }
    reApplyConfig();
  }

  function removeEdge(sourceName, distName){
      for (i = 0; i < data.edges.length; ++i) {
        if (sourceName === data.edges[i].from && distName === data.edges[i].to) {
          data.edges.splice(i, 1);
          break;
        }
    }
    reApplyConfig();
  }

  function removeEdgeWithNode(nodeName){
      for (i = 0; i < data.edges.length; ++i) {
        if (nodeName === data.edges[i].from || nodeName === data.edges[i].to) {
          data.edges.splice(i, 1);
        }
    }
    reApplyConfig();
  }

  function addNode(node){
    data.nodes = data.nodes.concat(node)
    reApplyConfig();
  }

  function addEdge(edge){
    data.edges = data.edges.concat(edge)
    reApplyConfig();
  }

  function getEdgeColor(edgeValue) {
    if (edgeValue >= invalidStep[0] && edgeValue <= invalidStep[1]) 
        return "#FC0D1B"
    if (edgeValue >= stronglyInvalidStep[0] && edgeValue <= stronglyInvalidStep[1]) 
      return "#FC644D"
    if (edgeValue >= possiblyInvalidStep[0] && edgeValue <= possiblyInvalidStep[1])
      return "#FDA07E"
    if (edgeValue >= neutralStep[0] && edgeValue <= neutralStep[1])
      return "#FED530"
    if (edgeValue >= possiblyValidStep[0] && edgeValue <= possiblyValidStep[1])
      return  "#807F17"
    if (edgeValue >= stronglyValidStep[0] && edgeValue <= stronglyValidStep[1])
      return  "#9BCB40"
    if (edgeValue >= validStep[0] && edgeValue <= validStep[1])
      return "#81FA30"
  }

  function getNodeColor(nodeValue) {
    if (nodeValue >= incorrectState[0] && nodeValue <= incorrectState[1])
      return "#EE8182"
    if (nodeValue >= unknownState[0] && nodeValue <= unknownState[1])
      return "#F0E591"
    if (nodeValue >= correctState[0] && nodeValue <= correctState[1])
      return "#2AFD84"
  }

  $('#saveGraph', element).click(function(eventObject) {
    var el = $(element);
    var body = {
      graphData: data
    };

    $.ajax({
      type: "POST",
      url: submitGraphDataUrl,
      data: JSON.stringify(body),
      success: function (data) {
        console.log(data)
      }   
    });
  });


  $('#createStep', element).click(function(eventObject) {
    var el = $(element);
    var data = {
      from: el.find('input[id=sourceState]').val(),
      to: el.find('input[id=destState]').val(),
      stroke: getEdgeColor(el.find('input[id=stepCorrectness]').val()),
      correctness: el.find('input[id=stepCorrectness]').val()
    };
    addEdge(data)
  });


  $('#createState', element).click(function(eventObject) {
    var el = $(element);
    var data = {
      id: el.find('input[id=stateName]').val(),
      height: "50",
      fill: getNodeColor(el.find('input[id=stateCorrectness]').val()),
      correctness: el.find('input[id=stateCorrectness]').val()
    };
    addNode(data)
  });

  $('#createInitialState', element).click(function(eventObject) {
    var el = $(element);
    var data = {
      id: el.find('input[id=stateName]').val(),
      height: "50",
      fill: getNodeColor(el.find('input[id=stateCorrectness]').val()),
      stroke: {"color": "black", "dash": "5 5"},
      correctness: el.find('input[id=stateCorrectness]').val()
    };
    addNode(data)
  });

  $('#createFinalState', element).click(function(eventObject) {
    var el = $(element);
    var data = {
      id: el.find('input[id=stateName]').val(),
      height: "50",
      fill: getNodeColor(el.find('input[id=stateCorrectness]').val()),
      stroke: "1 black",
      correctness: el.find('input[id=stateCorrectness]').val()
    };
    addNode(data)
  });


  $('#removeState', element).click(function(eventObject) {
    var el = $(element);
    var id = el.find('input[id=editState]').val()
    removeNode(id)
  });

  $('#removeStep', element).click(function(eventObject) {
    var el = $(element);
    var from = el.find('input[id=editStepSource]').val()
    var to = el.find('input[id=editStepDest]').val()
    removeEdge(from, to)
  });


  $('#changeStateValue', element).click(function(eventObject) {
    var el = $(element);
    var id = el.find('input[id=editState]').val()
    var value = el.find('input[id=editStateValue]').val()
    changeNodeValue(id, value)
  });

  $('#changeStateToNormal', element).click(function(eventObject) {
    var el = $(element);
    var id = el.find('input[id=editState]').val()
    changeNodeToNormal(id)
  });

  $('#changeStateToInitial', element).click(function(eventObject) {
    var el = $(element);
    var id = el.find('input[id=editState]').val()
    changeNodeToInitial(id)
  });

  $('#changeStateToFinal', element).click(function(eventObject) {
    var el = $(element);
    var id = el.find('input[id=editState]').val()
    changeNodeToFinal(id);
  });


  $('#changeStateCorrectness', element).click(function(eventObject) {
    var el = $(element);
    var id = el.find('input[id=editState]').val()
    var value = el.find('input[id=editStateValue]').val()
    changeNodeCorrectness(id, value)
  });

  $('#changeStepCorrectness', element).click(function(eventObject) {
    var el = $(element);
    var from = el.find('input[id=editStepSource]').val()
    var to = el.find('input[id=editStepDest]').val()
    var value = el.find('input[id=editStepValue]').val()
    changeStepCorrectness(from, to, value)
  });

  $('#saveErrorSpecificFeedback', element).click(function(eventObject) {
    var el = $(element);
    var data = {
      from: el.find('input[id=editStepSource]').val(),
      to: el.find('input[id=editStepDest]').val(),
      errorSpecificFeedbacks: el.find('input[name=stepErrorSpecificFeedbacks]').val().split(",")
    };

    $.ajax({
      type: "POST",
      url: submitErrorSpecificFeedbackUrl,
      data: JSON.stringify(data),
      success: function (data) {
        console.log(data)
      }   
    });
  });

  $('#saveExplanations', element).click(function(eventObject) {
    var el = $(element);
    var data = {
      from: el.find('input[id=editStepSource]').val(),
      to: el.find('input[id=editStepDest]').val(),
      explanations: el.find('input[name=stepExplanations]').val().split(",")
    };

    $.ajax({
      type: "POST",
      url: submitExplanationUrl,
      data: JSON.stringify(data),
      success: function (data) {
        console.log(data)
      }   
    });
  });

  $('#saveHints', element).click(function(eventObject) {
    var el = $(element);
    var data = {
      from: el.find('input[id=editStepSource]').val(),
      to: el.find('input[id=editStepDest]').val(),
      hints: el.find('input[name=stepHints]').val().split(",")
    };

    $.ajax({
      type: "POST",
      url: submitHintUrl,
      data: JSON.stringify(data),
      success: function (data) {
        console.log(data)
      }   
    });
  });


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

  $('#closeGraphModal', element).click(function(eventObject) {
    var modal = document.getElementById("graphModal");
    modal.style.display = "none";
  });

  $('#createGraph', element).click(function(eventObject) {
    document.getElementById("graph").innerHTML = "";

    var modal = document.getElementById("graphModal");

    modal.style.display = "block";

    $.ajax({
      type: "POST",
      url: getGraphurl,
      data: JSON.stringify({}),
      success: function (value) {
          // create a chart from the loaded data
        chart = anychart.graph(value.teste);
        data = value.teste;

        // set the title
        chart.title("Grafo das escolhas dos estudantes");

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
            size: 15
        });

        chart.container("graph").draw();

        chart.listen("click", function(e) {
          var tag = e.domTarget.tag;
          if (tag) {
            if (tag.type === 'node') {
              menu = document.getElementById("edgeMenu");
              menu.style.display = "none";
              for (var i = 0; i < data.nodes.length; i++) {
                if (data.nodes[i].id === tag.id) {
                  var menu = document.getElementById("nodeMenu");
                  document.getElementById("editState").value = tag.id;
                  document.getElementById("editStateValue").value = data.nodes[i].correctness;
                  menu.style.display = "block";
                  break;
                }
              }
            }
            else if (tag.type === 'edge') {
              var menu = document.getElementById("nodeMenu");
              menu.style.display = "none";
              edgePos = tag.id.split("_")[1];
              var body = {
                from: data.edges[edgePos].from,
                to: data.edges[edgePos].to
              };

              $.ajax({
                type: "POST",
                url: getEdgeInfoUrl,
                data: JSON.stringify(body),
                success: function (edgeInfo) {
                  document.getElementById("stepErrorSpecificFeedbacks").value = edgeInfo.errorSpecificFeedbacks;
                  document.getElementById("stepExplanations").value = edgeInfo.explanations;
                  document.getElementById("stepHints").value = edgeInfo.hints;
                }   
              });

              document.getElementById("editStepSource").value = data.edges[edgePos].from;
              document.getElementById("editStepDest").value = data.edges[edgePos].to;
              document.getElementById("editStepValue").value = data.edges[edgePos].correctness;

              var menu = document.getElementById("edgeMenu");
              menu.style.display = "block";
            }
          } else {
            var menu = document.getElementById("nodeMenu");
            menu.style.display = "none";
            menu = document.getElementById("edgeMenu");
            menu.style.display = "none";
          }
        });
      }   
   });
  });

  $('#cancel_button', element).click(function(eventObject) {
    runtime.notify('cancel', {});
  });
}
