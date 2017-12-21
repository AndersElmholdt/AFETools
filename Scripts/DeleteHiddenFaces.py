from pymel.core import *
import pymel.core.datatypes as dt

selection = ls(selection=True)

insidePoints = {}
for objectID, object in enumerate(selection):
    points = object.getPoints('world')
    
    for collisionObject in selection:
        if collisionObject == object:
            continue
        for pointID, point in enumerate(points):
            hit, intersections, ids = collisionObject.intersect(point, (1.0, 0.1, 0.001), space='world')
            if len(intersections) % 2 == 1:
                if (objectID not in insidePoints):
                    insidePoints[objectID] = []
                insidePoints[objectID].append(pointID)

for objectID, pointIDs in insidePoints.items():
    object = selection[objectID]
  
    commandString = []
    for pointID in pointIDs:
        commandString.append(str(object) + '.vtx[' + str(pointID) + ']')
    commandString = polyListComponentConversion(commandString, internal=True, fv=True, tf=True)
    
    select(commandString, r=True)
    delete()