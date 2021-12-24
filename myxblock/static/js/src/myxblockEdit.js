function MyXBlockEdit(runtime, element) {

  var submitDataUrl = runtime.handlerUrl(element, 'submit_data');
  var getGraphurl = runtime.handlerUrl(element, 'generate_graph');
  var submitGraphDataUrl = runtime.handlerUrl(element, 'submit_graph_data');
  var getEdgeInfoUrl = runtime.handlerUrl(element, 'get_edge_info');
  var submitEdgeInfoUrl = runtime.handlerUrl(element, 'submit_edge_info');

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
  var defaultArrowSize = 3;
  var defaultFontSize = 10;
  var defaultNodeHeight = 20;

  var normalNodeShape = "circle";
  var initialNodeShape = "square";
  var finalNodeShape = "diamond";
  var initialNodeStroke = {"color": "black", "dash": "5 5"};
  var finalNodeStroke = "1 black";
  var normalNodeStroke = null


  function reApplyConfig() {
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

    chart = anychart.graph(data);
    var nodes = chart.nodes();

    chart.title("Grafo das escolhas dos estudantes");

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
    chart.nodes().labels().fontSize(defaultFontSize);
    chart.nodes().labels().fontWeight(600);

    chart.edges().arrows({
      enabled: true,
      size: defaultArrowSize
    });
    chart.interactivity().scrollOnMouseWheel(false);
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
              document.getElementById("editStateWeigth").value = data.nodes[i].weigth;
              if (data.nodes[i].stroke) {
                if (data.nodes[i].stroke === finalNodeStroke) {
                  document.getElementById('changeStateType').value = 'finalState';
                } else {
                  document.getElementById('changeStateType').value = 'initialState';
                }

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
              document.getElementById("stepErrorSpecificFeedbacks").value = edgeInfo.errorSpecificFeedbacks;
              document.getElementById("stepExplanations").value = edgeInfo.explanations;
              document.getElementById("stepHints").value = edgeInfo.hints;
            }   
          });

          document.getElementById("editStepSource").value = data.edges[edgePos].from;
          document.getElementById("editStepDest").value = data.edges[edgePos].to;
          document.getElementById("editStepValue").value = data.edges[edgePos].correctness;

          edgeMenu.style.display = "block";
        }
      } else {
        addMenu.style.display = "block";
        nodeMenu.style.display = "none";
        edgeMenu.style.display = "none";
      }
    });

  }

  function removeNode(nodeName){
    for (i = 0; i < data.nodes.length; ++i) {
      if (nodeName === data.nodes[i].id) {
        data.nodes[i].visible = 0;
        //data.nodes.splice(i, 1);
        //removeEdgeWithNode(nodeName)
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
  
  function changeNodeCorrectness(nodeName, value, weigth){
      for (i = 0; i < data.nodes.length; ++i) {
        if (nodeName === data.nodes[i].id) {
          nodeData = data.nodes[i];
          data.nodes.splice(i, 1);
          nodeData.correctness = value;
          nodeData.weigth = weigth;
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
          edgeData.stroke = defaultArrowSize + " " + getEdgeColor(value);
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
    var data = {
      from: el.find('input[id=sourceState]').val(),
      to: el.find('input[id=destState]').val(),
      stroke: defaultArrowStroke + getEdgeColor(el.find('input[id=stepCorrectness]').val()),
      correctness: el.find('input[id=stepCorrectness]').val()
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

    if (dropDownValue === 'normalState') {
      data = {
        id: el.find('input[id=stateName]').val(),
        height: defaultNodeHeight,
        fill: getNodeColor(el.find('input[id=stateCorrectness]').val()),
        correctness: el.find('input[id=stateCorrectness]').val(),
        weigth: el.find('input[id=stateWeigth]').val(),
        visible: 1,
        x: 0,
        y: 0,
        type: dropDownValue
      };
    } else {
      data = {
        id: el.find('input[id=stateName]').val(),
        height: defaultNodeHeight,
        fill: getNodeColor(el.find('input[id=stateCorrectness]').val()),
        correctness: el.find('input[id=stateCorrectness]').val(),
        weigth: el.find('input[id=stateWeigth]').val(),
        visible: 1,
        stroke: strokeType,
        shape: shapeType,
        x: 0,
        y: 0,
        type: dropDownValue
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

  $('#changeStateToNormal', element).click(function(eventObject) {
    var el = $(element);
    var id = el.find('input[id=editState]').val()
    var value = el.find('input[id=editStateValue]').val()
    var weigth = el.find('input[id=editStateWeigth]').val()

    var dropDown = document.getElementById("changeStateType");
    var dropDownValue = dropDown.options[dropDown.selectedIndex].value;

    changeNodeCorrectness(id, value, weigth)
    if (dropDownValue === 'normalState') {
      changeNodeToNormal(id)
    } else if (dropDownValue === 'initialState') {
      changeNodeToInitial(id)
    } else if (dropDownValue === 'finalState') {
      changeNodeToFinal(id);
    }

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


  $('#saveEdgeInfo', element).click(function(eventObject) {
    var el = $(element);
    var data = {
      from: el.find('input[id=editStepSource]').val(),
      to: el.find('input[id=editStepDest]').val(),
      errorSpecificFeedbacks: el.find('input[name=stepErrorSpecificFeedbacks]').val().split(","),
      explanations: el.find('input[name=stepExplanations]').val().split(","),
      hints: el.find('input[name=stepHints]').val().split(",")
    };

    $.ajax({
      type: "POST",
      url: submitEdgeInfoUrl,
      data: JSON.stringify(data),
      success: function (data) {
        alert("Dados salvos com sucesso!");
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
    reApplyConfig();
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
        chart.nodes().labels().fontSize(defaultFontSize);
        chart.nodes().labels().fontWeight(600);

        chart.edges().arrows({
            enabled: true,
            size: defaultArrowSize
        });

        chart.interactivity().scrollOnMouseWheel(false);
        chart.interactivity().zoomOnMouseWheel(false);

        chart.container("graph").draw();
        if(value.teste.fixedPos) {
          chart.layout().type("fixed");
        }

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
                  document.getElementById("editStateWeigth").value = data.nodes[i].weigth;
                  if (data.nodes[i].stroke) {
                    if (data.nodes[i].stroke === "1 black") {
                      document.getElementById('changeStateType').value = 'finalState';
                    } else {
                      document.getElementById('changeStateType').value = 'initialState';
                    }

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
                  document.getElementById("stepErrorSpecificFeedbacks").value = edgeInfo.errorSpecificFeedbacks;
                  document.getElementById("stepExplanations").value = edgeInfo.explanations;
                  document.getElementById("stepHints").value = edgeInfo.hints;
                }   
              });

              document.getElementById("editStepSource").value = data.edges[edgePos].from;
              document.getElementById("editStepDest").value = data.edges[edgePos].to;
              document.getElementById("editStepValue").value = data.edges[edgePos].correctness;

              edgeMenu.style.display = "block";
            }
          } else {
            addMenu.style.display = "block";
            nodeMenu.style.display = "none";
            edgeMenu.style.display = "none";
          }
        });

      }   
   });
  });

  $('#cancel_button', element).click(function(eventObject) {
    runtime.notify('cancel', {});
  });
}
