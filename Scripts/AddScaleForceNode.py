from pymel.core import *

selection = ls(sl=True)[0]

if (attributeQuery("outputForce", node=str(selection), ex=1)):
    outAttrName = '.outputForce'
    if (attributeQuery("outputForce", node=str(selection), m=1)):
        outAttrName += '[0]'
    connections = listConnections(selection + outAttrName, p=True)
    scaleNode = createNode('scaleForce')
    connectAttr(str(selection) + outAttrName, str(scaleNode) + '.inputForce')
    for connection in connections:
        connectAttr(str(scaleNode) + '.outputForce', connection, f=True)
else:
    print 'Cannot scale the force'