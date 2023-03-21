function MyXBlockEdit(runtime, element) {

  var submitDataUrl = runtime.handlerUrl(element, 'submit_data');
  var importDataUrl = runtime.handlerUrl(element, 'import_data');
  var exportDataUrl = runtime.handlerUrl(element, 'export_data');
  var generateReportUrl = runtime.handlerUrl(element, 'generate_report');
  var generateProblemId = runtime.handlerUrl(element, 'generate_problem_id');
  var getGraphurl = runtime.handlerUrl(element, 'generate_graph');
  var submitGraphDataUrl = runtime.handlerUrl(element, 'submit_graph_data');
  var getEdgeInfoUrl = runtime.handlerUrl(element, 'get_edge_info');
  var getNodeInfoUrl = runtime.handlerUrl(element, 'get_doubts_and_answers_from_state');
  var submitEdgeInfoUrl = runtime.handlerUrl(element, 'submit_edge_info');
  var submitNodeInfoUrl = runtime.handlerUrl(element, 'submit_node_info');
  var deleteDoubtsUrl = runtime.handlerUrl(element, 'delete_doubts');
  var deleteAnswersUrl = runtime.handlerUrl(element, 'delete_answers');
  var deleteFeedbacksUrl = runtime.handlerUrl(element, 'delete_feedbacks');
  
  var lastWindowBeforeDoubts = null
  var editingFeedbackType = null

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


  var currentDoubtAnswers = new Map()
  var currentHints = new Map()
  var currentExplanations = new Map()
  var currentErrorSpecificFeedback = new Map()
  var currentAnswers = new Map()


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
  
  function changeNodeCorrectness(nodeName, value, fixedValue, linkedSolution){
      for (i = 0; i < data.nodes.length; ++i) {
        if (nodeName === data.nodes[i].id) {
          nodeData = data.nodes[i];
          nodeData.correctness = value;
          nodeData.fixedValue = fixedValue;
          nodeData.linkedSolution = linkedSolution;

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
    var linkedSolution = el.find('input[id=editStateLinkedSolution]').val()
    if (fixedValue == true) {
      fixedValue = 1
    } else {
      fixedValue = 0
    }

    var dropDown = document.getElementById("changeStateType");
    var dropDownValue = dropDown.options[dropDown.selectedIndex].value;

    changeNodeCorrectness(id, value, fixedValue, linkedSolution)
    if (dropDownValue === 'normalState') {
      changeNodeToNormal(id)
    } else if (dropDownValue === 'initialState') {
      changeNodeToInitial(id)
    } else if (dropDownValue === 'finalState') {
      changeNodeToFinal(id);
    }
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

  $('#import_graph', element).click(function(eventObject) {
    var el = $(element);
    var data = {
      problemData: el.find('input[name=importProblemData]').val()
    };

    $.ajax({
      type: "POST",
      url: importDataUrl,
      data: JSON.stringify(data),
      success: function (data) {
        window.alert("Dados importados com sucesso")
        window.location.reload(false);
      }   
    });
  });

  $('#generate_report', element).click(function(eventObject) {
    var el = $(element);
    var data = {
    };

    $.ajax({
      type: "POST",
      url: generateReportUrl,
      data: JSON.stringify(data)
    });
  });

  $('#export_graph', element).click(function(eventObject) {
    var el = $(element);
    var data = {};

    $.ajax({
      type: "POST",
      url: exportDataUrl,
      data: JSON.stringify(data)
    });
  });

  $('#save_button', element).click(function(eventObject) {
    multipleChoiceElement = document.getElementById("multipleChoiceProblem");
    multipleChoice = multipleChoiceElement.options[multipleChoiceElement.selectedIndex].value;
 
    var el = $(element);
    var data = {
      problemTitle: el.find('input[name=problemTitle]').val(),
      problemDescription: el.find('input[id=problemDescription]').val(),
      multipleChoiceProblem: multipleChoice,
      problemDefaultHint: el.find('input[id=problemDefaultHint]').val(),
      problemInitialHint: el.find('input[id=problemInitialHint]').val(),
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
        var doubtMenu = document.getElementById("doubtMenu");
        var feedbackMenu = document.getElementById("feedbackMenu");

        if (tag) {
          if (tag.type === 'node') {
            edgeMenu.style.display = "none";
            addMenu.style.display = "none";
            doubtMenu.style.display = "none";
            feedbackMenu.style.display = "none";

            for (var i = 0; i < data.nodes.length; i++) {
              if (data.nodes[i].id === tag.id) {
                document.getElementById("editState").value = tag.id;
                document.getElementById("editStateValue").value = data.nodes[i].correctness;
                document.getElementById("editStateLinkedSolution").value = data.nodes[i].linkedSolution;
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

                    currentDoubtAnswers.clear()
                    var select = document.getElementById("stateDoubts");
                    var i, L = select.options.length - 1;
                    for(i = L; i >= 0; i--) {
                       select.remove(i);
                    }

                    doubts = nodeInfo.doubts

                    for (var i = 0; i < doubts.length; i++) {

                      var id = doubts[i].id;
                      var text = doubts[i].text;
                      var el = document.createElement("option");
                      el.textContent = text;
                      el.value = id;
                      select.appendChild(el);

                      currentDoubtAnswers.set(id, doubts[i].answers)
                    }
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
            doubtMenu.style.display = "none";
            feedbackMenu.style.display = "none";

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

                currentDoubtAnswers.clear()
                currentExplanations.clear()
                currentErrorSpecificFeedback.clear()
                currentHints.clear()

                var errorSpecificSelect = document.getElementById("stepErrorSpecificFeedbacks");
                var i, L = errorSpecificSelect.options.length - 1;
                for (i = L; i >= 0; i--) {
                  errorSpecificSelect.remove(i);
                }

                var explanationSelect = document.getElementById("stepExplanations");
                var i, L = explanationSelect.options.length - 1;
                for (i = L; i >= 0; i--) {
                  explanationSelect.remove(i);
                }

                var hintSelect = document.getElementById("stepHints");
                var i, L = hintSelect.options.length - 1;
                for (i = L; i >= 0; i--) {
                  hintSelect.remove(i);
                }

                var doubtSelect = document.getElementById("stepDoubts");
                var i, L = doubtSelect.options.length - 1;
                for (i = L; i >= 0; i--) {
                  doubtSelect.remove(i);
                }


                var doubts = edgeInfo.doubts
                for (var i = 0; i < doubts.length; i++) {

                  var id = doubts[i].id;
                  var text = doubts[i].text;
                  var el = document.createElement("option");
                  el.textContent = text;
                  el.value = id;
                  doubtSelect.appendChild(el);

                  currentDoubtAnswers.set(id, doubts[i].answers)
                }

                var errorSpecificFeedbacks = edgeInfo.errorSpecificFeedbacks
                for (var i = 0; i < errorSpecificFeedbacks.length; i++) {

                  var id = errorSpecificFeedbacks[i].id;
                  var text = errorSpecificFeedbacks[i].text;
                  var el = document.createElement("option");
                  el.textContent = text;
                  el.value = id;
                  errorSpecificSelect.appendChild(el);

                  currentErrorSpecificFeedback.set(id, errorSpecificFeedbacks[i])
                }

                var el = document.createElement("option");
                el.textContent = "<Adicionar um novo feedback>";
                el.value = 0;
                errorSpecificSelect.appendChild(el);
                currentErrorSpecificFeedback.set(0, { "id": "", "text": "", "usefulness": 0, "priority": 0 })

                var explanations = edgeInfo.explanations
                for (var i = 0; i < explanations.length; i++) {

                  var id = explanations[i].id;
                  var text = explanations[i].text;
                  var el = document.createElement("option");
                  el.textContent = text;
                  el.value = id;
                  explanationSelect.appendChild(el);

                  currentExplanations.set(id, explanations[i])
                }
                var el = document.createElement("option");
                el.textContent = "<Adicionar uma nova explicação>";
                el.value = 0;
                explanationSelect.appendChild(el);
                currentExplanations.set(0, { "id": "", "text": "", "usefulness": 0, "priority": 0 })

                var hints = edgeInfo.hints
                for (var i = 0; i < hints.length; i++) {

                  var id = hints[i].id;
                  var text = hints[i].text;
                  var el = document.createElement("option");
                  el.textContent = text;
                  el.value = id;
                  hintSelect.appendChild(el);

                  currentHints.set(id, hints[i])
                }
                var el = document.createElement("option");
                el.textContent = "<Adicionar uma nova dica>";
                el.value = 0;
                hintSelect.appendChild(el);
                currentHints.set(0, { "id": "", "text": "", "usefulness": 0, "priority": 0 })


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
          doubtMenu.style.display = "none";
          feedbackMenu.style.display = "none";
        }
      });

  }

  $('#saveDoubt', element).click(function(eventObject) {
    var el = $(element);
    if (lastWindowBeforeDoubts == "node") {
      var data = {
        node: el.find('input[id=editState]').val(),
        doubts: [{
          id: el.find('input[id=editDoubtId]').val(),
          text: el.find('input[id=editDoubtText]').val(),
          answers: []
        }]
      };

      $.ajax({
        type: "POST",
        url: submitNodeInfoUrl,
        data: JSON.stringify(data)
      });
    } else if (lastWindowBeforeDoubts == "edge") {
      var data = {
        from: el.find('input[id=editStepSource]').val(),
        to: el.find('input[id=editStepDest]').val(),
        doubts: [{
          id: el.find('input[id=editDoubtId]').val(),
          text: el.find('input[id=editDoubtText]').val(),
          answers: []
        }]
      };

      $.ajax({
        type: "POST",
        url: submitEdgeInfoUrl,
        data: JSON.stringify(data)
      });
    }

  });

  $('#removeDoubt', element).click(function(eventObject) {
    var el = $(element);
    var data = {
      doubts: [{
        id: el.find('input[id=editDoubtId]').val()
      }]
    };

    $.ajax({
      type: "POST",
      url: deleteDoubtsUrl,
      data: JSON.stringify(data),
      success: function (value) {
        var addMenu = document.getElementById("addMenu");
        var doubtMenu = document.getElementById("doubtMenu");
        addMenu.style.display = "block";
        doubtMenu.style.display = "none";
      }   
    });
  });

  $('#removeDoubtAnswer', element).click(function(eventObject) {
    var el = $(element);
    if (!el.find('input[id=editAnswerId]').val()) {
      alert("Não é possível remover essa resposta")
      return
    }
    var data = {
      answers: [{
        id: el.find('input[id=editAnswerId]').val()
      }]
    };

    $.ajax({
      type: "POST",
      url: deleteAnswersUrl,
      data: JSON.stringify(data),
      success: function (value) {
        var id = el.find('input[id=editAnswerId]').val()
        $("#doubtAnswers option[value=" + id + "]").remove();

        var doubtAnswers = document.getElementById("doubtAnswers");
        var answerId = doubtAnswers.options[doubtAnswers.selectedIndex].value;

        var answer = currentAnswers.get(Number(answerId))

        var answerIdElement = document.getElementById("editAnswerId");
        var answerTextElement = document.getElementById("editAnswerText");
        var answerUsefulnessElement = document.getElementById("editAnswerUsefulness");

        answerIdElement.value = answer.id
        answerTextElement.value = answer.text
        answerUsefulnessElement.value = answer.usefulness
      }   
    });
  });

  $('#saveDoubtAnswer', element).click(function(eventObject) {
    var el = $(element);

    if (lastWindowBeforeDoubts == "node") {
      var data = {
        node: el.find('input[id=editState]').val(),
        doubts: [{
          id: el.find('input[id=editDoubtId]').val(),
          text: el.find('input[id=editDoubtText]').val(),
          answers: [{
            id: el.find('input[id=editAnswerId]').val(),
            text: el.find('input[id=editAnswerText]').val(),
            usefulness: el.find('input[id=editAnswerUsefulness]').val()
          }]
        }]
      };

      $.ajax({
        type: "POST",
        url: submitNodeInfoUrl,
        data: JSON.stringify(data),
        success: updateDoubtSavedData
      });

    } else if (lastWindowBeforeDoubts == "edge") {
      var data = {
        from: el.find('input[id=editStepSource]').val(),
        to: el.find('input[id=editStepDest]').val(),
        doubts: [{
          id: el.find('input[id=editDoubtId]').val(),
          text: el.find('input[id=editDoubtText]').val(),
          answers: [{
            id: el.find('input[id=editAnswerId]').val(),
            text: el.find('input[id=editAnswerText]').val(),
            usefulness: el.find('input[id=editAnswerUsefulness]').val()
          }]
        }]
      };

      $.ajax({
        type: "POST",
        url: submitEdgeInfoUrl,
        data: JSON.stringify(data),
        success: updateDoubtSavedData
      });
    }
  });

  function updateDoubtSavedData (value) {
    if (value.newAnswers) {
      for (var i = 0; i < value.newAnswers.length; i++) {

        var answerIdElement = document.getElementById("editAnswerId");
        var answerTextElement = document.getElementById("editAnswerText");

        currentAnswers.set(value.newAnswers[i].id, value.newAnswers[i])

        var el = document.createElement("option");
        el.textContent = answerTextElement.value;
        el.value = value.newAnswers[i].id;

        $('#doubtAnswers').prepend($(el));

        var doubtAnswers = document.getElementById("doubtAnswers");
        doubtAnswers.selectedIndex = 0
        answerIdElement.value = value.newAnswers[i].id
      }
    }
  }

  $('#editDoubt', element).click(function(eventObject) {
    var nodeMenu = document.getElementById("nodeMenu");
    var edgeMenu = document.getElementById("edgeMenu");
    var addMenu = document.getElementById("addMenu");
    var doubtMenu = document.getElementById("doubtMenu");
    var feedbackMenu = document.getElementById("feedbackMenu");

    if (nodeMenu.style.display == "block") {
      lastWindowBeforeDoubts = "node"
    } else if (edgeMenu.style.display == "block") {
      lastWindowBeforeDoubts = "edge"
    }

    edgeMenu.style.display = "none";
    addMenu.style.display = "none";
    nodeMenu.style.display = "none";
    doubtMenu.style.display = "block";
    feedbackMenu.style.display = "none";

    currentAnswers.clear()

    var answersSelect = document.getElementById("doubtAnswers");
    var i, L = answersSelect.options.length - 1;
    for (i = L; i >= 0; i--) {
      answersSelect.remove(i);
    }


    var doubtDropDown = document.getElementById("stateDoubts");
    if (!doubtDropDown.options[doubtDropDown.selectedIndex]) {
      alert("Não há dúvidas para se editar")
      return;
    }

    var doubtDropDownId = doubtDropDown.options[doubtDropDown.selectedIndex].value;
    var doubtDropDownText = doubtDropDown.options[doubtDropDown.selectedIndex].textContent;
    

    var doubtId = document.getElementById("editDoubtId");
    doubtId.value = doubtDropDownId

    var doubtText = document.getElementById("editDoubtText");
    doubtText.value = doubtDropDownText

    var answers = currentDoubtAnswers.get(Number(doubtDropDownId))
    var answersSelect = document.getElementById("doubtAnswers");

    if (answers) {

      for (var i = 0; i < answers.length; i++) {

        var id = answers[i].id;
        var text = answers[i].text;

        var el = document.createElement("option");
        el.textContent = text;
        el.value = id;
        answersSelect.appendChild(el);

        currentAnswers.set(id, answers[i])
        
      }   
    }
    var el = document.createElement("option");
    el.textContent = "<Adicionar uma nova resposta>";
    el.value = 0;
    answersSelect.appendChild(el);
    currentAnswers.set(0, {"id": "", "text": "", "usefulness": 0})

    var answerIdElement = document.getElementById("editAnswerId");
    var answerTextElement = document.getElementById("editAnswerText");
    var answerUsefulnessElement = document.getElementById("editAnswerUsefulness");

    if (answers.length > 0) {
      answerIdElement.value = answers[0].id
      answerTextElement.value = answers[0].text
      answerUsefulnessElement.value = answers[0].usefulness
    } else {
      answerIdElement.value = ""
      answerTextElement.value = ""
      answerUsefulnessElement.value = 0
    }


  });

  $('#editDoubtStep', element).click(function(eventObject) {
    var nodeMenu = document.getElementById("nodeMenu");
    var edgeMenu = document.getElementById("edgeMenu");
    var addMenu = document.getElementById("addMenu");
    var doubtMenu = document.getElementById("doubtMenu");
    var feedbackMenu = document.getElementById("feedbackMenu");

    if (nodeMenu.style.display == "block") {
      lastWindowBeforeDoubts = "node"
    } else if (edgeMenu.style.display == "block") {
      lastWindowBeforeDoubts = "edge"
    }


    edgeMenu.style.display = "none";
    addMenu.style.display = "none";
    nodeMenu.style.display = "none";
    doubtMenu.style.display = "block";
    feedbackMenu.style.display = "none";

    currentAnswers.clear()

    var answersSelect = document.getElementById("doubtAnswers");
    var i, L = answersSelect.options.length - 1;
    for (i = L; i >= 0; i--) {
      answersSelect.remove(i);
    }


    var doubtDropDown = document.getElementById("stepDoubts");
    if (!doubtDropDown.options[doubtDropDown.selectedIndex]) {
      alert("Não há dúvidas para se editar")
      return;
    }

    var doubtDropDownId = doubtDropDown.options[doubtDropDown.selectedIndex].value;
    var doubtDropDownText = doubtDropDown.options[doubtDropDown.selectedIndex].textContent;
    

    var doubtId = document.getElementById("editDoubtId");
    doubtId.value = doubtDropDownId

    var doubtText = document.getElementById("editDoubtText");
    doubtText.value = doubtDropDownText

    var answers = currentDoubtAnswers.get(Number(doubtDropDownId))
    var answersSelect = document.getElementById("doubtAnswers");

    if (answers) {

      for (var i = 0; i < answers.length; i++) {

        var id = answers[i].id;
        var text = answers[i].text;

        var el = document.createElement("option");
        el.textContent = text;
        el.value = id;
        answersSelect.appendChild(el);

        currentAnswers.set(id, answers[i])
        
      }   
    }
    var el = document.createElement("option");
    el.textContent = "<Adicionar uma nova resposta>";
    el.value = 0;
    answersSelect.appendChild(el);
    currentAnswers.set(0, {"id": "", "text": "", "usefulness": 0})

    var answerIdElement = document.getElementById("editAnswerId");
    var answerTextElement = document.getElementById("editAnswerText");
    var answerUsefulnessElement = document.getElementById("editAnswerUsefulness");

    if (answers.length > 0) {
      answerIdElement.value = answers[0].id
      answerTextElement.value = answers[0].text
      answerUsefulnessElement.value = answers[0].usefulness
    } else {
      answerIdElement.value = ""
      answerTextElement.value = ""
      answerUsefulnessElement.value = 0
    }


  });

  $('#editStepErrorSpecificFeedbacks', element).click(function(eventObject) {
    var nodeMenu = document.getElementById("nodeMenu");
    var edgeMenu = document.getElementById("edgeMenu");
    var addMenu = document.getElementById("addMenu");
    var doubtMenu = document.getElementById("doubtMenu");
    var feedbackMenu = document.getElementById("feedbackMenu");

    edgeMenu.style.display = "none";
    addMenu.style.display = "none";
    nodeMenu.style.display = "none";
    doubtMenu.style.display = "none";
    feedbackMenu.style.display = "block";

    editingFeedbackType = "errorSpecificFeedback"

    var errorSpecificDropDown = document.getElementById("stepErrorSpecificFeedbacks");
    if (!errorSpecificDropDown.options[errorSpecificDropDown.selectedIndex]) {
      alert("Não há feedbacks específicos para se editar")
      return;
    }

    var errorSpecificDropDownId = errorSpecificDropDown.options[errorSpecificDropDown.selectedIndex].value;
    
    var errorSpecificDetails = currentErrorSpecificFeedback.get(Number(errorSpecificDropDownId))

    var errorSpecificId = document.getElementById("editFeedbackId");
    errorSpecificId.value = errorSpecificDetails.id

    var errorSpecificText = document.getElementById("editFeedbackText");
    errorSpecificText.value = errorSpecificDetails.text

    var errorSpecificPriority = document.getElementById("editFeedbackPriority");
    errorSpecificPriority.value = errorSpecificDetails.priority

    var errorSpecificUsefulness = document.getElementById("editFeedbackUsefulness");
    errorSpecificUsefulness.value = errorSpecificDetails.usefulness

  });

  $('#editStepHints', element).click(function(eventObject) {
    var nodeMenu = document.getElementById("nodeMenu");
    var edgeMenu = document.getElementById("edgeMenu");
    var addMenu = document.getElementById("addMenu");
    var doubtMenu = document.getElementById("doubtMenu");
    var feedbackMenu = document.getElementById("feedbackMenu");

    edgeMenu.style.display = "none";
    addMenu.style.display = "none";
    nodeMenu.style.display = "none";
    doubtMenu.style.display = "none";
    feedbackMenu.style.display = "block";

    editingFeedbackType = "hint"

    var hintDropDown = document.getElementById("stepHints");
    if (!hintDropDown.options[hintDropDown.selectedIndex]) {
      alert("Não há dicas para se editar")
      return;
    }

    var hintDropDownId = hintDropDown.options[hintDropDown.selectedIndex].value;
    
    var hintDetails = currentHints.get(Number(hintDropDownId))

    var hintId = document.getElementById("editFeedbackId");
    hintId.value = hintDetails.id

    var hintText = document.getElementById("editFeedbackText");
    hintText.value = hintDetails.text

    var hintPriority = document.getElementById("editFeedbackPriority");
    hintPriority.value = hintDetails.priority

    var hintUsefulness = document.getElementById("editFeedbackUsefulness");
    hintUsefulness.value = hintDetails.usefulness

  });

  $('#editStepExplanations', element).click(function(eventObject) {
    var nodeMenu = document.getElementById("nodeMenu");
    var edgeMenu = document.getElementById("edgeMenu");
    var addMenu = document.getElementById("addMenu");
    var doubtMenu = document.getElementById("doubtMenu");
    var feedbackMenu = document.getElementById("feedbackMenu");

    edgeMenu.style.display = "none";
    addMenu.style.display = "none";
    nodeMenu.style.display = "none";
    doubtMenu.style.display = "none";
    feedbackMenu.style.display = "block";

    editingFeedbackType = "explanation"

    var explanationDropDown = document.getElementById("stepExplanations");
    if (!explanationDropDown.options[explanationDropDown.selectedIndex]) {
      alert("Não há explicações para se editar")
      return;
    }

    var explanationDropDownId = explanationDropDown.options[explanationDropDown.selectedIndex].value;
    
    var explanationDetails = currentExplanations.get(Number(explanationDropDownId))

    var explanationId = document.getElementById("editFeedbackId");
    explanationId.value = explanationDetails.id

    var explanationText = document.getElementById("editFeedbackText");
    explanationText.value = explanationDetails.text

    var explanationPriority = document.getElementById("editFeedbackPriority");
    explanationPriority.value = explanationDetails.priority

    var explanationUsefulness = document.getElementById("editFeedbackUsefulness");
    explanationUsefulness.value = explanationDetails.usefulness

  });

  $('#saveFeedback', element).click(function(eventObject) {
    var el = $(element);

    if (editingFeedbackType == "errorSpecificFeedback") {
      var data = {
        from: el.find('input[id=editStepSource]').val(),
        to: el.find('input[id=editStepDest]').val(),
        errorSpecificFeedbacks: [{
          id: el.find('input[id=editFeedbackId]').val(),
          text: el.find('input[id=editFeedbackText]').val(),
          usefulness: el.find('input[id=editFeedbackUsefulness]').val(),
          priority: el.find('input[id=editFeedbackPriority]').val()
        }]
      };
    } else if (editingFeedbackType == "explanation") {
      var data = {
        from: el.find('input[id=editStepSource]').val(),
        to: el.find('input[id=editStepDest]').val(),
        explanations: [{
          id: el.find('input[id=editFeedbackId]').val(),
          text: el.find('input[id=editFeedbackText]').val(),
          usefulness: el.find('input[id=editFeedbackUsefulness]').val(),
          priority: el.find('input[id=editFeedbackPriority]').val()
        }]
      };
    } else if (editingFeedbackType == "hint") {
      var data = {
        from: el.find('input[id=editStepSource]').val(),
        to: el.find('input[id=editStepDest]').val(),
        hints: [{
          id: el.find('input[id=editFeedbackId]').val(),
          text: el.find('input[id=editFeedbackText]').val(),
          usefulness: el.find('input[id=editFeedbackUsefulness]').val(),
          priority: el.find('input[id=editFeedbackPriority]').val()
        }]
      };
    }

    $.ajax({
      type: "POST",
      url: submitEdgeInfoUrl,
      data: JSON.stringify(data),
      success: updateFeedbackSavedData
    });

  });

  function updateFeedbackSavedData (value) {
    if (value.newErrorSpecificFeedbacks) {
      for (var i = 0; i < value.newErrorSpecificFeedbacks.length; i++) {

        var feedbackIdElement = document.getElementById("editFeedbackId");

        currentErrorSpecificFeedback.set(value.newErrorSpecificFeedbacks[i].id, value.newErrorSpecificFeedbacks[i])

        var el = document.createElement("option");
        el.textContent = value.newErrorSpecificFeedbacks[i].text;
        el.value = value.newErrorSpecificFeedbacks[i].id;

        $('#stepErrorSpecificFeedbacks').prepend($(el));

        var errorSpecificFeedbacksList = document.getElementById("stepErrorSpecificFeedbacks");
        errorSpecificFeedbacksList.selectedIndex = 0
        feedbackIdElement.value = value.newErrorSpecificFeedbacks[i].id
      }
    }

    if (value.newExplanations) {
      for (var i = 0; i < value.newExplanations.length; i++) {

        var feedbackIdElement = document.getElementById("editFeedbackId");

        currentExplanations.set(value.newExplanations[i].id, value.newExplanations[i])

        var el = document.createElement("option");
        el.textContent = value.newExplanations[i].text;
        el.value = value.newExplanations[i].id;

        $('#stepExplanations').prepend($(el));

        var explanationList = document.getElementById("stepExplanations");
        explanationList.selectedIndex = 0
        feedbackIdElement.value = value.newExplanations[i].id
      }
    }

    if (value.newHints) {
      for (var i = 0; i < value.newHints.length; i++) {

        var feedbackIdElement = document.getElementById("editFeedbackId");

        currentExplanations.set(value.newHints[i].id, value.newHints[i])

        var el = document.createElement("option");
        el.textContent = value.newHints[i].text;
        el.value = value.newHints[i].id;

        $('#stepHints').prepend($(el));

        var hintList = document.getElementById("stepHints");
        hintList.selectedIndex = 0
        feedbackIdElement.value = value.newHints[i].id
      }
    }
  }

  $('#removeFeedback', element).click(function(eventObject) {
    var el = $(element);

    if (editingFeedbackType == "errorSpecificFeedback") {
      var data = {
        errorSpecificFeedbacks: [{
          id: el.find('input[id=editFeedbackId]').val()
        }]
      };
    } else if (editingFeedbackType == "explanation") {
      var data = {
        explanations: [{
          id: el.find('input[id=editFeedbackId]').val()
        }]
      };
    } else if (editingFeedbackType == "hint") {
      var data = {
        hints: [{
          id: el.find('input[id=editFeedbackId]').val()
        }]
      };
    }

    $.ajax({
      type: "POST",
      url: deleteFeedbacksUrl,
      data: JSON.stringify(data),
      success: function (value) {
        var addMenu = document.getElementById("addMenu");
        var feedbackMenu = document.getElementById("feedbackMenu");
        addMenu.style.display = "block";
        feedbackMenu.style.display = "none";
        //Voltar para a parte de passo e atualizar os dados corretamente (edgeMenu)
      }   
    });

  });

  document.getElementById('doubtAnswers').onchange = function () {
    var doubtAnswers = document.getElementById("doubtAnswers");
    var answerId = doubtAnswers.options[doubtAnswers.selectedIndex].value;

    var answer = currentAnswers.get(Number(answerId))

    var answerIdElement = document.getElementById("editAnswerId");
    var answerTextElement = document.getElementById("editAnswerText");
    var answerUsefulnessElement = document.getElementById("editAnswerUsefulness");

    answerIdElement.value = answer.id
    answerTextElement.value = answer.text
    answerUsefulnessElement.value = answer.usefulness
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
