function MyXBlockEdit(runtime, element) {

  var submitDataUrl = runtime.handlerUrl(element, 'submit_data');
  var generateProblemId = runtime.handlerUrl(element, 'generate_problem_id');
  var getGraphurl = runtime.handlerUrl(element, 'generate_graph');
  var submitGraphDataUrl = runtime.handlerUrl(element, 'submit_graph_data');
  var getEdgeInfoUrl = runtime.handlerUrl(element, 'get_edge_info');
  var getNodeInfoUrl = runtime.handlerUrl(element, 'get_doubts_and_answers_from_state');
  var submitEdgeInfoUrl = runtime.handlerUrl(element, 'submit_edge_info');
  var submitNodeInfoUrl = runtime.handlerUrl(element, 'submit_node_info');

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


  var defaultArrowStroke = "3 ";
  var defaultArrowSize = 8;
  var defaultFontSize = 10;
  var defaultNodeHeight = 20;

  var normalNodeShape = "circle";
  var initialNodeShape = "square";
  var finalNodeShape = "diamond";
  var initialNodeStroke = {"color": "black", "dash": "5 5"};
  var finalNodeStroke = "1 black";
  var normalNodeStroke = null


  function reApplyConfig() {
    createOrReloadGraph()
  }

  function removeNode(nodeName){
    for (i = 0; i < data.nodes.length; ++i) {
      if (nodeName === data.nodes[i].id) {
        data.nodes[i].visible = 0;
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
        nodeData.stroke = normalNodeStroke;
        nodeData.shape = normalNodeShape;
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
          nodeData.stroke = initialNodeStroke;
          nodeData.shape = initialNodeShape;
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
          nodeData.stroke = finalNodeStroke
          nodeData.shape = finalNodeShape;
          addNode(nodeData);
          break;
        }
    }
    reApplyConfig();
  }
  
  function changeNodeCorrectness(nodeName, value, fixedValue){
      for (i = 0; i < data.nodes.length; ++i) {
        if (nodeName === data.nodes[i].id) {
          nodeData = data.nodes[i];
          nodeData.correctness = value;
          nodeData.fixedValue = fixedValue;

          nodeData.fill = getNodeColor(value);

          nodeData.hovered = {stroke: {color: "#333333", thickness: 3}};
          nodeData.selected = {stroke: {color: "#333333", thickness: 3}};
          nodeData.modifiedCorrectness = 1;

          break;
        }
    }
    reApplyConfig();
  }

  function changeStepCorrectness(sourceName, distName, value, fixedValue){
      for (i = 0; i < data.edges.length; ++i) {
        if (sourceName === data.edges[i].from && distName === data.edges[i].to) {
          edgeData = data.edges[i];
    
          edgeData.correctness = value
          edgeData.fixedValue = fixedValue;

          edgeData.normal = {stroke: defaultArrowStroke + getEdgeColor(value)}
          edgeData.hovered = {stroke: {thickness: 5, color: getEdgeColor(value)}}
          edgeData.selected = {stroke: {color: getEdgeColor(value), dash: '10 3', thickness: '7' }}
          edgeData.modifiedCorrectness = 1;
          
          break;
        }
    }
    reApplyConfig();
  }

  function removeEdge(sourceName, distName){
      for (i = 0; i < data.edges.length; ++i) {
        if (sourceName === data.edges[i].from && distName === data.edges[i].to) {
          data.edges[i].visible = 0
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
  }

  function addNode(node){
    data.nodes = data.nodes.concat(node)
  }

  function addEdge(edge){
    data.edges = data.edges.concat(edge)
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

  function saveGraph() {
    var body = {
      graphData: data
    };

    $.ajax({
      type: "POST",
      url: submitGraphDataUrl,
      data: JSON.stringify(body),
      success: function (data) {
      }   
    });
  }


  $('#createStep', element).click(function(eventObject) {
    var el = $(element);

    var fixedValueCheckbox = el.find('input[id=stepFixedValue]').is(':checked')
    if (fixedValueCheckbox == true) {
      fixedValueCheckbox = 1
    } else {
      fixedValueCheckbox = 0
    }

    var data = {
      from: el.find('input[id=sourceState]').val(),
      to: el.find('input[id=destState]').val(),
      normal: {stroke: defaultArrowStroke + getEdgeColor(el.find('input[id=stepCorrectness]').val())},
      hovered: {stroke: {thickness: 5, color: getEdgeColor(el.find('input[id=stepCorrectness]').val())}},
      selected: {stroke: {color: getEdgeColor(el.find('input[id=stepCorrectness]').val()), dash: '10 3', thickness: '7' }},
      correctness: el.find('input[id=stepCorrectness]').val(),
      fixedValue: fixedValueCheckbox,
      visible: 1,
      modifiedCorrectness: 0
    };
    addEdge(data);
    reApplyConfig();
  });


  $('#createState', element).click(function(eventObject) {
    var el = $(element);

    var dropDown = document.getElementById("addStateType");
    var dropDownValue = dropDown.options[dropDown.selectedIndex].value;
    var strokeType;
    var shapeType;

    if (dropDownValue === 'initialState') {
        strokeType = initialNodeStroke;
        shapeType = initialNodeShape;
    } else if (dropDownValue === 'finalState') {
        strokeType = finalNodeStroke;
        shapeType = finalNodeShape;
    }

    var data;

    var fixedValueCheckbox = el.find('input[id=stateFixedValue]').is(':checked')
    if (fixedValueCheckbox == true) {
      fixedValueCheckbox = 1
    } else {
      fixedValueCheckbox = 0
    }

    if (dropDownValue === 'normalState') {
      data = {
        id: el.find('input[id=stateName]').val(),
        height: defaultNodeHeight,
        fill: getNodeColor(el.find('input[id=stateCorrectness]').val()),
        correctness: el.find('input[id=stateCorrectness]').val(),
        fixedValue: fixedValueCheckbox,
        visible: 1,
        x: 0,
        y: 0,
        type: dropDownValue,
        modifiedCorrectness: 0
      };
    } else {
      data = {
        id: el.find('input[id=stateName]').val(),
        height: defaultNodeHeight,
        fill: getNodeColor(el.find('input[id=stateCorrectness]').val()),
        correctness: el.find('input[id=stateCorrectness]').val(),
        fixedValue: fixedValueCheckbox,
        visible: 1,
        stroke: strokeType,
        shape: shapeType,
        x: 0,
        y: 0,
        type: dropDownValue,
        modifiedCorrectness: 0
      };
    }
    addNode(data)
    reApplyConfig();
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


  $('#saveStateinfo', element).click(function(eventObject) {
    var el = $(element);
    var id = el.find('input[id=editState]').val()
    var value = el.find('input[id=editStateValue]').val()
    var fixedValue = el.find('input[id=editStateFixedValue]').is(':checked')
    if (fixedValue == true) {
      fixedValue = 1
    } else {
      fixedValue = 0
    }

    var dropDown = document.getElementById("changeStateType");
    var dropDownValue = dropDown.options[dropDown.selectedIndex].value;

    changeNodeCorrectness(id, value, fixedValue)
    if (dropDownValue === 'normalState') {
      changeNodeToNormal(id)
    } else if (dropDownValue === 'initialState') {
      changeNodeToInitial(id)
    } else if (dropDownValue === 'finalState') {
      changeNodeToFinal(id);
    }

    var el = $(element);
    var data = {
      node: el.find('input[id=editState]').val(),
      doubts: el.find('input[name=stateDoubts]').val()
    };

    $.ajax({
      type: "POST",
      url: submitNodeInfoUrl,
      data: JSON.stringify(data)
    });

  });

  $('#changeStateCorrectness', element).click(function(eventObject) {
    var el = $(element);
    var id = el.find('input[id=editState]').val()
    var value = el.find('input[id=editStateValue]').val()
    changeNodeCorrectness(id, value)
  });

  $('#saveEdgeInfo', element).click(function(eventObject) {
    var el = $(element);

    var from = el.find('input[id=editStepSource]').val()
    var to = el.find('input[id=editStepDest]').val()
    var value = el.find('input[id=editStepValue]').val()
    var fixedValue = el.find('input[id=editStepFixedValue]').is(':checked')
    if (fixedValue == true) {
      fixedValue = 1
    } else {
      fixedValue = 0
    }
    changeStepCorrectness(from, to, value, fixedValue)

    var data = {
      from: el.find('input[id=editStepSource]').val(),
      to: el.find('input[id=editStepDest]').val(),
      errorSpecificFeedbacks: el.find('input[name=stepErrorSpecificFeedbacks]').val(),
      explanations: el.find('input[name=stepExplanations]').val(),
      doubts: el.find('input[name=stepDoubts]').val(),
      hints: el.find('input[name=stepHints]').val()
    };

    $.ajax({
      type: "POST",
      url: submitEdgeInfoUrl,
      data: JSON.stringify(data)
    });
  });


  $(document).ready( function () {
    $.ajax({
      type: "POST",
      url: generateProblemId,
      data: JSON.stringify(null),
      success: function (data) {
        if (data.result == 'created') {
          alert("Dados iniciais gerados com sucesso! Recarregando a página...");
          window.location.reload(false);
        }
      }   
    });
  });

  $('#save_button', element).click(function(eventObject) {
    var el = $(element);
    var data = {
      problemTitle: el.find('input[name=problemTitle]').val(),
      problemDescription: el.find('input[id=problemDescription]').val(),
      problemCorrectRadioAnswer: el.find('input[id=problemCorrectRadioAnswer]').val(),
      multipleChoiceProblem: el.find('input[id=multipleChoiceProblem]').val(),
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

    var loadingMessage = document.getElementById("loadingMessage");
    loadingMessage.style.display = "none";

    var errorMessage = document.getElementById("errorMessage");
    errorMessage.style.display = "none";

    reApplyConfig();

  });

  function createOrReloadGraph(value) {
    if (value != null) {

      chart = anychart.graph(value.teste);
      data = value.teste;

      chart.labels().anchor("center");
      chart.labels().position("center");

      var zoomController = anychart.ui.zoom();
      zoomController.target(chart);
      zoomController.render();

    } else {
      document.getElementById("graph").innerHTML = "";
      var nodeData = chart.toJson().chart.graphData.nodes

      for (i = 0; i < nodeData.length; ++i) {
        for (j = 0; j < data.nodes.length; ++j) {
          if (nodeData[i].id === data.nodes[j].id) {
            data.nodes[j].x = nodeData[i].x;
            data.nodes[j].y = nodeData[i].y;
            break
          }
        }
      }

      saveGraph();

      for (i = 0; i < data.nodes.length; ++i) {
        if (data.nodes[i].visible == 0) {
          nodeName = data.nodes[i].id
          data.nodes.splice(i, 1);
          removeEdgeWithNode(nodeName)
        }
      }

      for (i = 0; i < data.edges.length; ++i) {
        if (data.edges[i].visible == 0) {
          data.edges.splice(i, 1);
        }
      }

      chart = anychart.graph(data);

    }
      var nodes = chart.nodes();

      chart.title("Grafo de conhecimento");

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

      chart.labels().anchor("center");
      chart.labels().position("center");

      var zoomController = anychart.ui.zoom();
      zoomController.target(chart);
      zoomController.render();

      // configure the labels of nodes
      chart.nodes().labels().format("{%id}");
      chart.nodes().labels().fontSize(defaultFontSize);
      chart.nodes().labels().fontWeight(600);

      chart.edges().arrows({
        enabled: true,
        size: defaultArrowSize,
        position: '80%'
      });
    
      chart.interactivity().scrollOnMouseWheel(true);
      chart.interactivity().zoomOnMouseWheel(false);

      chart.layout().type("fixed");

      chart.container("graph").draw();

      chart.listen("click", function(e) {
        var tag = e.domTarget.tag;
        var nodeMenu = document.getElementById("nodeMenu");
        var edgeMenu = document.getElementById("edgeMenu");
        var addMenu = document.getElementById("addMenu");

        if (tag) {
          if (tag.type === 'node') {
            edgeMenu.style.display = "none";
            addMenu.style.display = "none";
            for (var i = 0; i < data.nodes.length; i++) {
              if (data.nodes[i].id === tag.id) {
                document.getElementById("editState").value = tag.id;
                document.getElementById("editStateValue").value = data.nodes[i].correctness;
                if (data.nodes[i].fixedValue == 1) {
                  document.getElementById("editStateFixedValue").checked = true;
                } else {
                  document.getElementById("editStateFixedValue").checked = false;
                }

                var body = {
                  node: data.nodes[i].id
                };

                $.ajax({
                  type: "POST",
                  url: getNodeInfoUrl,
                  data: JSON.stringify(body),
                  success: function (nodeInfo) {
                    document.getElementById("stateDoubts").value = JSON.stringify(nodeInfo.doubts);
                  }   
                });

                if (data.nodes[i].shape === 'diamond') {
                  document.getElementById('changeStateType').value = 'finalState';
                } else if (data.nodes[i].shape === 'square') {
                  document.getElementById('changeStateType').value = 'initialState';
                } else {
                  document.getElementById('changeStateType').value = 'normalState';
                }

                nodeMenu.style.display = "block";
                break;
              }
            }
          }
          else if (tag.type === 'edge') {
            nodeMenu.style.display = "none";
            addMenu.style.display = "none";
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
                document.getElementById("stepErrorSpecificFeedbacks").value = JSON.stringify(edgeInfo.errorSpecificFeedbacks);
                document.getElementById("stepExplanations").value = JSON.stringify(edgeInfo.explanations);
                document.getElementById("stepHints").value = JSON.stringify(edgeInfo.hints);
                document.getElementById("stepDoubts").value = JSON.stringify(edgeInfo.doubts);
              }   
            });

            document.getElementById("editStepSource").value = data.edges[edgePos].from;
            document.getElementById("editStepDest").value = data.edges[edgePos].to;
            document.getElementById("editStepValue").value = data.edges[edgePos].correctness;
            if (data.edges[edgePos].fixedValue == 1) {
              document.getElementById("editStepFixedValue").checked = true;
            } else {
              document.getElementById("editStepFixedValue").checked = false;
            }

            edgeMenu.style.display = "block";
          }
        } else {
          addMenu.style.display = "block";
          nodeMenu.style.display = "none";
          edgeMenu.style.display = "none";
        }
      });

  }

  $('#createGraph', element).click(function(eventObject) {
    document.getElementById("graph").innerHTML = "";

    var modal = document.getElementById("graphModal");
    modal.style.display = "block";

    var loadingMessage = document.getElementById("loadingMessage");
    loadingMessage.style.display = "block";

    var errorMessage = document.getElementById("errorMessage");
    errorMessage.style.display = "none";

    $.ajax({
      type: "POST",
      url: getGraphurl,
      data: JSON.stringify({}),
      success: function (value) {
        var loadingMessage = document.getElementById("loadingMessage");
        loadingMessage.style.display = "none"

        var errorMessage = document.getElementById("errorMessage");
        errorMessage.style.display = "none";
        creategraph(value);
      }   
   });
  });

  function creategraph (value) {
    try {
      createOrReloadGraph(value)
    } catch(error) {
      var errorMessage = document.getElementById("errorMessage");
      errorMessage.style.display = "block";
      creategraph(value);
    }
  }

  $('#cancel_button', element).click(function(eventObject) {
    runtime.notify('cancel', {});
  });
}
