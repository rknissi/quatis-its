from .studentGraph.models import Answer, Problem, Node, Edge, Resolution, ErrorSpecificFeedbacks, Hint, Explanation, Doubt, KnowledgeComponent
import copy

#VisualGraphProperties
defaultArrowStroke = "3 "
initialNodeShape = "square"
finalNodeShape = "diamond"
defaultNodeHeight = 20
initialNodeStroke = {"color": "black", "dash": "5 5"}
finalNodeStroke = "1 black"


graphHeightDefaultValue = 60
graphWidthDefaultValue = 0
graphWidthExtraValue = 100
graphWidthExtraValueY = 67
graphNodeMinimumDistance = 100

#Step information
correctnessMinValue = -1
correctnessMaxValue = 1

#Resolution values
incorrectResolution = [-1, -0.75001]
partiallyIncorrectResolution = [-0.75, -0.00001]
partiallyCorrectResolution = [0, 0.74999]
correctResolution = [0.75, 1]
defaultResolutionValue = 0

#Step values
invalidStep = [-1, -0.80001]
stronglyInvalidStep = [-0.8, -0.40001]
possiblyInvalidStep = [-0.4, -0.00001]
neutralStep = [0, 0]
possiblyValidStep = [0.00001, 0.39999]
stronglyValidStep = [0.4, 0.79999]
validStep = [0.8, 1]
defaultStepValue = 0

#State values
incorrectState = [-1, -0.7]
unknownState = [-0.69999, 0.69999]
correctState = [0.7, 1]
defaultStateValue = 0

def createGraphInitialPositions(problemId):

    currentX = 0
    currentY = 500
    endNodes = []
    usedEdges = []

    loadedProblem = Problem.objects.get(id=problemId)

    needToCalculate = Node.objects.filter(problem=loadedProblem, alreadyCalculatedPos = 0).exists() 
    if not needToCalculate:
        return

    if loadedProblem.isCalculatingPos == 1:
        return

        
    loadedProblem.isCalculatingPos = 1
    loadedProblem.save()

    endEdges = Edge.objects.filter(problem=loadedProblem, destNode__title = '_end_')
    for edge in endEdges:
        endNodes.append(edge.sourceNode)

    for node in endNodes:
        if node.nodePositionX == -1 and node.nodePositionY == -1:
            pos = avoidSamePosFromAnotherNode(currentX, currentY, loadedProblem)
            node.nodePositionX = pos['x']
            node.nodePositionY = pos['y']

        node.alreadyCalculatedPos = 1
        node.save()

    currentY = currentY - graphWidthExtraValueY

    nextEdges = []
    for node in endNodes:
        nextEdges.extend(Edge.objects.filter(problem=loadedProblem, destNode = node).exclude(sourceNode = node))

    createGraphInitialPositionsNextSteps(nextEdges, usedEdges, currentY, loadedProblem)

    loadedProblem.isCalculatingPos = 0
    loadedProblem.save()


def createGraphInitialPositionsNextSteps(nextEdges, usedEdges, currentY, loadedProblem):
    for edge in nextEdges:
        changed = False
        node = edge.sourceNode
        if edge.sourceNode.title + edge.destNode.title not in usedEdges:
            copyUsedEdges = copy.deepcopy(usedEdges)
            if node.nodePositionX == -1 and node.nodePositionY == -1:
                pos = avoidSamePosFromAnotherNode(edge.destNode.nodePositionX, currentY, loadedProblem)
                node.nodePositionX = pos['x']
                node.nodePositionY = pos['y']
                node.alreadyCalculatedPos = 1
                node.save()
                if edge.sourceNode.title + edge.destNode.title not in copyUsedEdges:
                    copyUsedEdges.append(edge.sourceNode.title + edge.destNode.title)
            else:
                if node.nodePositionY > currentY:
                    node.nodePositionY = currentY
                    node.alreadyCalculatedPos = 0

                if node.alreadyCalculatedPos == 0:
                    pos = avoidEdgesAboveOthers(node, loadedProblem)
                    node.nodePositionX = pos['x']
                    node.nodePositionY = pos['y']
                    node.alreadyCalculatedPos = 1

                node.save()

                if edge.sourceNode.title + edge.destNode.title not in copyUsedEdges:
                    copyUsedEdges.append(edge.sourceNode.title + edge.destNode.title)

            nextEdgesToCalc = Edge.objects.filter(problem=loadedProblem, destNode = node, sourceNode__visible = 1, sourceNode__customPos = 0)

            createGraphInitialPositionsNextSteps(nextEdgesToCalc, copyUsedEdges, currentY - graphWidthExtraValueY, loadedProblem)

def avoidEdgesAboveOthers(node, loadedProblem):
    pos = {"x": node.nodePositionX, "y": node.nodePositionY}
    needsTest = True
    oldPos = {"x": pos["x"], "y": pos["y"]}
    invert = False

    while needsTest:
        nodeDests = Edge.objects.filter(problem=loadedProblem, sourceNode__title = node.title, destNode__nodePositionX = pos["x"], destNode__visible = 1)
        nodeCross =  Edge.objects.filter(problem=loadedProblem, sourceNode__nodePositionX = pos["x"], destNode__nodePositionX = pos["x"], sourceNode__nodePositionY__lt = pos["y"], destNode__nodePositionY__gt = pos["y"], destNode__visible = 1, sourceNode__visible = 1).exclude(sourceNode = node, destNode = node)
        nodeSame =  Node.objects.filter(problem=loadedProblem, nodePositionX = pos["x"], nodePositionY = pos["y"], visible = 1).exclude(title=node.title)

        needsTest = False
        if  nodeDests.count() > 1 or nodeCross.count() > 0 or nodeSame.count() > 0:
            if not invert:
                pos = avoidSamePosFromAnotherNode(pos["x"] + graphWidthExtraValue, pos["y"], loadedProblem)
            else:
                pos = avoidSamePosFromAnotherNode(pos["x"] - graphWidthExtraValue, pos["y"], loadedProblem)

            if oldPos["x"] == pos["x"] and oldPos["y"] == pos["y"]:
                invert = not invert

            oldPos = pos
            needsTest = True

    return pos


def avoidSamePosFromAnotherNode(x, y, loadedProblem):
    allNodes = Node.objects.filter(problem=loadedProblem).exclude(nodePositionX = -1, nodePositionY = -1)

    for node in allNodes:
        if (abs(node.nodePositionX - x) < graphNodeMinimumDistance and abs(node.nodePositionY - y) < graphWidthExtraValueY):
            rightX = avoidSamePosFromAnotherNodeRight(x + graphWidthExtraValue, y, loadedProblem)
            leftX = avoidSamePosFromAnotherNodeLeft(x - graphWidthExtraValue, y, loadedProblem)
            if abs(x - rightX) >= abs(x - leftX):
                return {"x": leftX, "y": y}
            return {"x": rightX, "y": y}

    return {"x": x, "y": y}

def avoidSamePosFromAnotherNodeLeft(x, y, loadedProblem):
    allNodes = Node.objects.filter(problem=loadedProblem).exclude(nodePositionX = -1, nodePositionY = -1)

    for node in allNodes:
        if (abs(node.nodePositionX - x) <= graphNodeMinimumDistance and abs(node.nodePositionY - y) < graphWidthExtraValueY):
            leftX = avoidSamePosFromAnotherNodeLeft(x - graphWidthExtraValue, y, loadedProblem)
            return leftX

    return x

def avoidSamePosFromAnotherNodeRight(x, y, loadedProblem):
    allNodes = Node.objects.filter(problem=loadedProblem).exclude(nodePositionX = -1, nodePositionY = -1)

    for node in allNodes:
        if (abs(node.nodePositionX - x) <= graphNodeMinimumDistance and abs(node.nodePositionY - y) < graphWidthExtraValueY):
            rightX = avoidSamePosFromAnotherNodeRight(x + graphWidthExtraValue, y, loadedProblem)
            return rightX

    return  x


def getJsonFromProblemGraph(problemId):
    nodeList = []
    edgeList = []
    addedNodes = []
    fixedPos = False

    loadedProblem = Problem.objects.get(id=problemId)
    allNodes = Node.objects.filter(problem=loadedProblem)

    while loadedProblem.isCalculatingPos == 1:
        loadedProblem.refresh_from_db()

    createGraphInitialPositions(problemId)

    for source in allNodes:
        edgeObjList = Edge.objects.filter(problem=loadedProblem, sourceNode = source)
        for edgeObj in edgeObjList:
            dest = edgeObj.destNode
            if source.title == "_start_":
                nodeColor = getNodeColor(dest)
                if dest not in addedNodes:
                    if dest.visible == 1:
                        node = {"id": dest.title, "height": defaultNodeHeight, "fill": nodeColor, "shape": initialNodeShape ,"normal": {"stroke": initialNodeStroke}, "correctness": dest.correctness, "equivalentTo": dest.equivalentTo.title if dest.equivalentTo is not None else None, "fixedValue": dest.fixedValue, "visible": dest.visible, "modifiedCorrectness": 0}
                        if dest.nodePositionX != -1 and dest.nodePositionY != -1:
                            node["x"] = dest.nodePositionX
                            node["y"] = dest.nodePositionY
                            fixedPos = True
                        nodeList.append(node)
                        addedNodes.append(dest)
                else: 
                    if dest.visible == 1:
                        pos = addedNodes.index(dest)
                        nodeList[pos] = {"id": dest.title, "height": defaultNodeHeight, "fill": nodeColor, "shape": initialNodeShape , "normal": {"stroke": initialNodeStroke}, "correctness": dest.correctness, "equivalentTo": dest.equivalentTo.title if dest.equivalentTo is not None else None, "fixedValue": dest.fixedValue, "visible": dest.visible, "modifiedCorrectness": 0}
                
            elif dest.title == "_end_":
                nodeColor = getNodeColor(source)
                if source not in addedNodes:
                    if source.visible == 1:
                        node = {"id": source.title, "height": defaultNodeHeight, "shape": finalNodeShape ,"fill": nodeColor, "normal": {"stroke": finalNodeStroke}, "correctness": source.correctness, "equivalentTo": source.equivalentTo.title if source.equivalentTo is not None else None, "fixedValue": source.fixedValue, "visible": source.visible, "modifiedCorrectness": 0}
                        if source.nodePositionX != -1 and source.nodePositionY != -1:
                            node["x"] = source.nodePositionX
                            node["y"] = source.nodePositionY
                            fixedPos = True
                        nodeList.append(node)
                        addedNodes.append(source)
                else:
                    if source.visible == 1:
                        pos = addedNodes.index(source)
                        node = {"id": source.title, "height": defaultNodeHeight, "shape": finalNodeShape, "fill": nodeColor, "normal": {"stroke": finalNodeStroke}, "correctness": source.correctness, "equivalentTo": source.equivalentTo.title if source.equivalentTo is not None else None, "fixedValue": source.fixedValue, "visible": source.visible, "modifiedCorrectness": 0}
                        if source.nodePositionX != -1 and source.nodePositionY != -1:
                            node["x"] = source.nodePositionX
                            node["y"] = source.nodePositionY
                            fixedPos = True
                        nodeList[pos] = node
            else:
                if source not in addedNodes:
                    if  source.visible == 1:
                        nodeColor = getNodeColor(source)
                        node = {"id": source.title, "height": defaultNodeHeight, "fill": nodeColor, "correctness": source.correctness, "equivalentTo": source.equivalentTo.title if source.equivalentTo is not None else None, "fixedValue": source.fixedValue, "visible": source.visible, "modifiedCorrectness": 0}
                        if source.nodePositionX != -1 and source.nodePositionY != -1:
                            node["x"] = source.nodePositionX
                            node["y"] = source.nodePositionY
                            fixedPos = True
                        nodeList.append(node)
                        addedNodes.append(source)
                if dest not in addedNodes:
                    if dest.visible == 1:
                        nodeColor = getNodeColor(dest)
                        node = {"id": dest.title, "height": defaultNodeHeight, "fill": nodeColor, "correctness": dest.correctness, "equivalentTo": dest.equivalentTo.title if dest.equivalentTo is not None else None, "fixedValue": dest.fixedValue, "visible": dest.visible, "modifiedCorrectness": 0}
                        if dest.nodePositionX != -1 and dest.nodePositionY != -1:
                            node["x"] = dest.nodePositionX
                            node["y"] = dest.nodePositionY
                            fixedPos = True
                        nodeList.append(node)
                        addedNodes.append(dest)
                
                if source.visible == 1 and dest.visible == 1 and edgeObj.visible == 1:
                    edge = {"from": source.title, "to": dest.title, "normal": {"stroke": defaultArrowStroke + getEdgeColor(edgeObj)}, "hovered": {"stroke": {"thickness": 5, "color": getEdgeColor(edgeObj)}}, "selected": {"stroke": {"color": getEdgeColor(edgeObj), "dash": '10 3', "thickness": '7' }}, "correctness": edgeObj.correctness, "visible": 1, "fixedValue": edgeObj.fixedValue, "modifiedCorrectness": 0}
                    edgeList.append(edge)

    return {"nodes": nodeList, "edges": edgeList, "fixedPos": fixedPos}
            
def getEdgeColor(edge):

    edgeValue = edge.correctness
    if edgeValue >= invalidStep[0] and edgeValue <= invalidStep[1]:
        return "#FC0D1B"
    if edgeValue >= stronglyInvalidStep[0] and edgeValue <= stronglyInvalidStep[1]:
        return "#FC644D"
    if edgeValue >= possiblyInvalidStep[0] and edgeValue <= possiblyInvalidStep[1]:
        return "#FDA07E"
    if edgeValue >= neutralStep[0] and edgeValue <= neutralStep[1]:
        return "#FED530"
    if edgeValue >= possiblyValidStep[0] and edgeValue <= possiblyValidStep[1]:
        return  "#807F17"
    if edgeValue >= stronglyValidStep[0] and edgeValue <= stronglyValidStep[1]:
        return  "#9BCB40"
    if edgeValue >= validStep[0] and edgeValue <= validStep[1]:
        return "#81FA30"

def getNodeColor(node):

    nodeValue = node.correctness
    if nodeValue >= incorrectState[0] and nodeValue <= incorrectState[1]:
        return "#EE8182"
    if nodeValue >= unknownState[0] and nodeValue <= unknownState[1]:
        return "#F0E591"
    if nodeValue >= correctState[0] and nodeValue <= correctState[1]:
        return "#2AFD84"
