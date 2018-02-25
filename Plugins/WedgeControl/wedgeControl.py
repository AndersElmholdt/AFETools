import sys

import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds

kWedgeNodeTypeName = 'wedgeControl'
kWedgeNodeId = OpenMaya.MTypeId(0x0012b805)
kWedgeTransformMatrixId = OpenMaya.MTypeId(0x0012b806)

kCacheActionNodeTypeName = 'wedgeCacheAction'
kCacheActionNodeId = OpenMaya.MTypeId(0x0012b807)

kCustomActionNodeTypeName = 'wedgeCustomAction'
kCustomActionNodeId = OpenMaya.MTypeId(0x0012b808)

kPlayblastActionNodeTypeName = 'wedgePlayblastAction'
kPlayblastActionNodeId = OpenMaya.MTypeId(0x0012b809)

kCmdName = 'runWedges'
kNameShortFlag = 'n'
kNameLongFlag = 'name'

def createFluidCache(startFrame, endFrame, cacheName, frameStep):
    OpenMaya.MGlobal.executeCommand('doCreateFluidCache 5 { "3", ' + str(startFrame) + ', ' + str(endFrame) + ', "OneFilePerFrame", "1", "","0", "' + cacheName + '", "0", "add", "0", ' + str(frameStep) + ', "1","0","1","mcx", "1", "1", "1", "1", "1", "1", "1"}')

def createNclothCache(startFrame, endFrame, cacheName, frameStep):
    OpenMaya.MGlobal.executeCommand('doCreateNclothCache 5 { "3", ' + str(startFrame) + ', ' + str(endFrame) + ', "OneFilePerFrame", "1", "","0", "' + cacheName + '", "0", "add", "0", ' + str(frameStep) + ', "1","0","1","mcx"}')
    
def createAlembicCache(startFrame, endFrame, objectName, cacheName, frameStep):
    path = cmds.workspace(q=True, rd=True) + '/cache/alembic/'
    cmds.sysFile(path, md=True)
    OpenMaya.MGlobal.executeCommand('AbcExport -j ("-frameRange %i %i -step %d -dataFormat ogawa -root %s -file %s%s.abc");' % (startFrame, endFrame, frameStep, objectName, path, cacheName))
    
def createPlayblast(format, encoding, fileName, so, ro, fp, per, qua, wth, hth, sf, ef):
    offScreenTag = ''
    if ro == 1:
	offScreenTag = '-offScreen'
	
    OpenMaya.MGlobal.executeCommand('playblast  -format %s -filename "movies/%s.%s" -forceOverwrite -sequenceTime 0 -clearCache 1 -viewer 1 -showOrnaments %i %s -fp %i -percent %i -compression "%s" -quality %i -widthHeight %i %i -st %i -et %i;' % (format, fileName, format, so, offScreenTag, fp, per, encoding, qua, wth, hth, sf, ef))

class runWedgesCmd(OpenMayaMPx.MPxCommand):
    def __init__(self):
        OpenMayaMPx.MPxCommand.__init__(self)
    def doIt(self, args):
        argData = OpenMaya.MArgDatabase(self.syntax(), args)
	
	if argData.isFlagSet('n'):
	    name = argData.flagArgumentString('n', 0)
	else:
	    OpenMaya.MGlobal.displayError('Must specify name flag')
	    return
	
	# Select object with given name
	selList = OpenMaya.MSelectionList()
	selList.add(name)
	obj = OpenMaya.MObject()
	selList.getDependNode(0, obj)
	depFn = OpenMaya.MFnDependencyNode(obj)
	
	try:
	    connActionsPlug = depFn.findPlug('connectedWedgeActions')
	    numWedgesPlug = depFn.findPlug('numberOfWedges')
	    currWedgePlug = depFn.findPlug('currentWedge')
	except:
	    OpenMaya.MGlobal.displayError('Could not find the attributes')
	    return
	
	if connActionsPlug.numConnectedElements() == 0:
	    OpenMaya.MGlobal.displayError('No actions are connected to wedge')
	    return	    
	
	# find connected nodes
	connectedNodes = []
	connectedPlug = OpenMaya.MPlugArray()
	for i in range(connActionsPlug.numConnectedElements()):    
	    connActionsPlug.connectionByPhysicalIndex(i).connectedTo(connectedPlug, True, False)
	    if connectedPlug.length == 0:
		break
	    connectedNodes.append(connectedPlug[0].node())
	
	numWedges = numWedgesPlug.asInt()
	
	# create progress bar
	progressWin = cmds.window(title='Wedge Progress')
	cmds.columnLayout()
	progressControl = cmds.progressBar(maxValue=100, width=300)
	cmds.text('Running a total of %i wedges.' % numWedges)
	cmds.showWindow(progressWin)
	
	stepSize = 100 / (numWedges * len(connectedNodes))
	
	# iterate over number of wedges
	for wedge in range(numWedges):
	    currWedgePlug.setInt(wedge)
	    
	    for connectedNode in connectedNodes:
		cmds.progressBar(progressControl, edit=True, step=stepSize)
		connDepFn = OpenMaya.MFnDependencyNode(connectedNode)
		
		try:
		    connActionTypePlug = connDepFn.findPlug('wedgeActionType')
		    connActionActivePlug = connDepFn.findPlug('isActive')
		except:
		    OpenMaya.MGlobal.displayError('Could not find the attributes')
		    return
		
		connActionType = connActionTypePlug.asInt()
		connActionActive = connActionActivePlug.asInt()
		
		# if action is not active continue
		if not connActionActive:
		    continue
		
		# Cache action
		if connActionType == 0:
		    try:
			startFramePlug = connDepFn.findPlug('startFrame')
			endFramePlug = connDepFn.findPlug('endFrame')
			frameStepPlug = connDepFn.findPlug('frameStep')
			cacheNamePlug = connDepFn.findPlug('cacheName')
			objectNamePlug = connDepFn.findPlug('objectName')
			cacheTypePlug = connDepFn.findPlug('cacheType')
		    except:
			OpenMaya.MGlobal.displayError('Could not find the attributes')
			return
		    
		    startFrame = startFramePlug.asInt()
		    endFrame = endFramePlug.asInt()
		    frameStep = frameStepPlug.asDouble()
		    cacheName = cacheNamePlug.asString()
		    objectName = objectNamePlug.asString()
		    cacheType = cacheTypePlug.asInt()
		    
		    OpenMaya.MGlobal.executeCommand('select ' + objectName)
		    
		    if cacheType == 0: # MObject cache
			createNclothCache(startFrame, endFrame, cacheName + '_wedge_' + str(wedge), frameStep)
		    elif cacheType == 1: # Fluid cache
			createFluidCache(startFrame, endFrame, cacheName + '_wedge_' + str(wedge), frameStep)
		    elif cacheType == 2: # Alembic cache
			createAlembicCache(startFrame, endFrame, objectName, cacheName + '_wedge_' + str(wedge), frameStep)
			continue
		    
		    if wedge != numWedges-1: # remove the cache to avoid popups
			OpenMaya.MGlobal.executeCommand('deleteCacheFile 2 { "keep", "" }')
		    
		# Custom action
		elif connActionType == 1:
		    try:
			customCodePlug = connDepFn.findPlug('customCode')
		    except:
			OpenMaya.MGlobal.displayError('Could not find the attributes')
			return	
		    
		    customCode = customCodePlug.asString()
		    OpenMaya.MGlobal.executeCommand(customCode)
		    
		# Playblast action    
		elif connActionType == 2:
		    try:
			formatPlug = connDepFn.findPlug('format')
			encodingPlug = connDepFn.findPlug('encoding')
			fileNamePlug = connDepFn.findPlug('fileName')
			showOrnamentsPlug = connDepFn.findPlug('showOrnaments')
			renderOffscreenPlug = connDepFn.findPlug('renderOffscreen')
			framePaddingPlug = connDepFn.findPlug('framePadding')
			percentPlug = connDepFn.findPlug('percent')
			qualityPlug = connDepFn.findPlug('quality')
			widthPlug = connDepFn.findPlug('width')
			heightPlug = connDepFn.findPlug('height')
			startFramePlug = connDepFn.findPlug('startFrame')
			endFramePlug = connDepFn.findPlug('endFrame')			
		    except:
			OpenMaya.MGlobal.displayError('Could not find the attributes')
			return	
		    
		    formatIndex = formatPlug.asInt()
		    encodingIndex = encodingPlug.asInt()
		    fileName = fileNamePlug.asString()
		    showOrnaments = showOrnamentsPlug.asInt()
		    renderOffscreen = renderOffscreenPlug.asInt()
		    framePadding = framePaddingPlug.asInt()
		    percent = percentPlug.asDouble() * 100
		    quality = qualityPlug.asInt()
		    width = widthPlug.asInt()
		    height = heightPlug.asInt()
		    startFrame = startFramePlug.asInt()
		    endFrame = endFramePlug.asInt()
		    
		    if formatIndex == 0:
			format = 'avi'
			
		    if encodingIndex == 0:
			encoding = 'IYUV codec'
		    elif encodingIndex == 1:
			encoding = 'none'
		    
		    OpenMaya.MGlobal.executeCommand('select -clear')
		    
		    createPlayblast(format, encoding, fileName + '_wedge_' + str(wedge), showOrnaments, renderOffscreen, framePadding, percent, quality, width, height, startFrame, endFrame)
		    
	cmds.deleteUI(progressWin, wnd=True)
	    
	
def cmdCreator():
    return OpenMayaMPx.asMPxPtr(runWedgesCmd())
    
def cmdSyntaxCreator():
    syntax = OpenMaya.MSyntax()
    syntax.addFlag(kNameShortFlag, kNameLongFlag, OpenMaya.MSyntax.kString)
    return syntax

class wedgeControl(OpenMayaMPx.MPxTransform):
    numWedgesAttr = OpenMaya.MObject()
    currWedgeAttr = OpenMaya.MObject()
    connWedgeActions = OpenMaya.MObject()
    
    def __init__(self):
        OpenMayaMPx.MPxTransform.__init__(self)
        
def wedgeNodeCreator():
    return OpenMayaMPx.asMPxPtr(wedgeControl())
    
def wedgeNodeInitializer():
    nAttr = OpenMaya.MFnNumericAttribute()
    mAttr = OpenMaya.MFnMessageAttribute()
    
    wedgeControl.numWedgesAttr = nAttr.create('numberOfWedges', 'nw', OpenMaya.MFnNumericData.kLong, 1)
    nAttr.setMin(1)
    nAttr.setSoftMax(10)
    wedgeControl.currWedgeAttr = nAttr.create('currentWedge', 'cw', OpenMaya.MFnNumericData.kLong, 0)
    nAttr.setMin(0)
    
    wedgeControl.connWedgeActions = mAttr.create('connectedWedgeActions', 'cwa')
    mAttr.setArray(True)
    
    wedgeControl.addAttribute(wedgeControl.numWedgesAttr)
    wedgeControl.addAttribute(wedgeControl.connWedgeActions)
    wedgeControl.addAttribute(wedgeControl.currWedgeAttr)
    
class customAction(OpenMayaMPx.MPxNode):
    wedgeActionTypeAttr = OpenMaya.MObject()
    activeAttr = OpenMaya.MObject()
    codeAttr = OpenMaya.MObject()
    
    def __init__(self):
	OpenMayaMPx.MPxNode.__init__(self)
	
def customActionNodeCreator():
    return OpenMayaMPx.asMPxPtr(customAction())

def customActionNodeInitializer():
    eAttr = OpenMaya.MFnEnumAttribute()
    tAttr = OpenMaya.MFnTypedAttribute()
    nAttr = OpenMaya.MFnNumericAttribute()
    
    customAction.wedgeActionTypeAttr = eAttr.create('wedgeActionType', 'wea', 1)
    eAttr.addField('Cache', 0)
    eAttr.addField('Custom', 1)
    eAttr.setHidden(1)
    
    customAction.codeAttr = tAttr.create('customCode', 'cc', OpenMaya.MFnData.kString)
    tAttr.setHidden(True)
    
    customAction.activeAttr = nAttr.create('isActive', 'act', OpenMaya.MFnNumericData.kBoolean, 1)
    
    customAction.addAttribute(customAction.codeAttr)
    customAction.addAttribute(customAction.wedgeActionTypeAttr)
    customAction.addAttribute(customAction.activeAttr)

class playblastAction(OpenMayaMPx.MPxNode):
    wedgeActionTypeAttr = OpenMaya.MObject()
    activeAttr = OpenMaya.MObject()
    formatAttr = OpenMaya.MObject()
    fileNameAttr = OpenMaya.MObject()
    ornamentsAttr = OpenMaya.MObject()
    offscreenAttr = OpenMaya.MObject()
    fpAttr = OpenMaya.MObject()
    percentAttr = OpenMaya.MObject()
    compressionAttr = OpenMaya.MObject()
    qualityAttr = OpenMaya.MObject()
    widthAttr = OpenMaya.MObject()
    heightAttr = OpenMaya.MObject()
    startFrameAttr = OpenMaya.MObject()
    endFrameAttr = OpenMaya.MObject()    
    
    def __init__(self):
	OpenMayaMPx.MPxNode.__init__(self)
	
def playblastActionNodeCreator():
    return OpenMayaMPx.asMPxPtr(playblastAction())

def playblastActionNodeInitializer():
    eAttr = OpenMaya.MFnEnumAttribute()
    nAttr = OpenMaya.MFnNumericAttribute()
    tAttr = OpenMaya.MFnTypedAttribute()
    
    playblastAction.wedgeActionTypeAttr = eAttr.create('wedgeActionType', 'wea', 2)
    eAttr.addField('Cache', 0)
    eAttr.addField('Custom', 1)
    eAttr.addField('Playblast', 2)
    eAttr.setHidden(1)    
    playblastAction.formatAttr = eAttr.create('format', 'fo', 0)
    eAttr.addField('avi', 0)
    playblastAction.compressionAttr = eAttr.create('encoding', 'en', 0)
    eAttr.addField('IYUV codec', 0)
    eAttr.addField('none', 1)
    
    playblastAction.fileNameAttr = tAttr.create('fileName', 'fn', OpenMaya.MFnData.kString)
    
    playblastAction.ornamentsAttr = nAttr.create('showOrnaments', 'so', OpenMaya.MFnNumericData.kBoolean, 1)
    playblastAction.offscreenAttr = nAttr.create('renderOffscreen', 'ro', OpenMaya.MFnNumericData.kBoolean, 1)
    playblastAction.fpAttr = nAttr.create('framePadding', 'fp', OpenMaya.MFnNumericData.kLong, 4)
    nAttr.setMin(0)
    playblastAction.percentAttr =nAttr.create('percent', 'per', OpenMaya.MFnNumericData.kDouble, 1.0)
    nAttr.setMin(0.1)
    nAttr.setMax(1)
    playblastAction.qualityAttr = nAttr.create('quality', 'qua', OpenMaya.MFnNumericData.kLong, 100)
    nAttr.setMin(0)
    nAttr.setMax(100)
    playblastAction.widthAttr = nAttr.create('width', 'wth', OpenMaya.MFnNumericData.kLong, 1280)
    nAttr.setMin(1)
    playblastAction.heightAttr = nAttr.create('height', 'hth', OpenMaya.MFnNumericData.kLong, 720)
    nAttr.setMin(1)
    playblastAction.startFrameAttr = nAttr.create('startFrame', 'sf', OpenMaya.MFnNumericData.kLong, 1)
    playblastAction.endFrameAttr = nAttr.create('endFrame', 'ef', OpenMaya.MFnNumericData.kLong, 10)
    playblastAction.activeAttr = nAttr.create('isActive', 'act', OpenMaya.MFnNumericData.kBoolean, 1)
    
    playblastAction.addAttribute(playblastAction.formatAttr)
    playblastAction.addAttribute(playblastAction.compressionAttr)
    playblastAction.addAttribute(playblastAction.fileNameAttr)
    playblastAction.addAttribute(playblastAction.ornamentsAttr)
    playblastAction.addAttribute(playblastAction.offscreenAttr)
    playblastAction.addAttribute(playblastAction.fpAttr)
    playblastAction.addAttribute(playblastAction.percentAttr)
    playblastAction.addAttribute(playblastAction.qualityAttr)
    playblastAction.addAttribute(playblastAction.widthAttr)
    playblastAction.addAttribute(playblastAction.heightAttr)
    playblastAction.addAttribute(playblastAction.wedgeActionTypeAttr)
    playblastAction.addAttribute(playblastAction.startFrameAttr)
    playblastAction.addAttribute(playblastAction.endFrameAttr)
    playblastAction.addAttribute(playblastAction.activeAttr)

class cacheAction(OpenMayaMPx.MPxNode):
    wedgeActionTypeAttr = OpenMaya.MObject()
    activeAttr = OpenMaya.MObject()
    cacheNameAttr = OpenMaya.MObject()
    objectNameAttr = OpenMaya.MObject()
    cacheTypeAttr = OpenMaya.MObject()
    startFrameAttr = OpenMaya.MObject()
    endFrameAttr = OpenMaya.MObject()
    frameStepAttr = OpenMaya.MObject()
    
    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)
    
def cacheActionNodeCreator():
    return OpenMayaMPx.asMPxPtr(cacheAction())
    
def cacheActionNodeInitializer():
    tAttr = OpenMaya.MFnTypedAttribute()
    nAttr = OpenMaya.MFnNumericAttribute()
    eAttr = OpenMaya.MFnEnumAttribute()
    
    cacheAction.wedgeActionTypeAttr = eAttr.create('wedgeActionType', 'wea', 0)
    eAttr.addField('Cache', 0)
    eAttr.addField('Custom', 1)
    eAttr.setHidden(1)
    cacheAction.cacheTypeAttr = eAttr.create('cacheType', 'ct', 0)
    eAttr.addField('nObject', 0)
    eAttr.addField('Fluid', 1)
    eAttr.addField('Alembic', 2)
    
    cacheAction.cacheNameAttr = tAttr.create('cacheName', 'cn', OpenMaya.MFnData.kString)
    cacheAction.objectNameAttr = tAttr.create('objectName', 'on', OpenMaya.MFnData.kString)
    
    cacheAction.startFrameAttr = nAttr.create('startFrame', 'sf', OpenMaya.MFnNumericData.kLong, 1)
    cacheAction.endFrameAttr = nAttr.create('endFrame', 'ef', OpenMaya.MFnNumericData.kLong, 10)
    cacheAction.frameStepAttr = nAttr.create('frameStep', 'fs', OpenMaya.MFnNumericData.kDouble, 1.0)
    nAttr.setMin(0.01)
    
    cacheAction.activeAttr = nAttr.create('isActive', 'act', OpenMaya.MFnNumericData.kBoolean, 1)
    
    cacheAction.addAttribute(cacheAction.wedgeActionTypeAttr)
    cacheAction.addAttribute(cacheAction.cacheTypeAttr)
    cacheAction.addAttribute(cacheAction.cacheNameAttr)
    cacheAction.addAttribute(cacheAction.objectNameAttr)
    cacheAction.addAttribute(cacheAction.startFrameAttr)
    cacheAction.addAttribute(cacheAction.endFrameAttr)
    cacheAction.addAttribute(cacheAction.frameStepAttr)
    cacheAction.addAttribute(cacheAction.activeAttr)
    
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject, "Anders Elmholdt", "1.0", "Any")
    matrix = OpenMayaMPx.MPxTransformationMatrix
    
    try:
	mplugin.registerTransform( kWedgeNodeTypeName, kWedgeNodeId, wedgeNodeCreator, wedgeNodeInitializer, matrix, kWedgeTransformMatrixId )
	mplugin.registerNode(kCacheActionNodeTypeName, kCacheActionNodeId, cacheActionNodeCreator, cacheActionNodeInitializer)
	mplugin.registerNode(kPlayblastActionNodeTypeName, kPlayblastActionNodeId, playblastActionNodeCreator, playblastActionNodeInitializer)
	mplugin.registerNode(kCustomActionNodeTypeName, kCustomActionNodeId, customActionNodeCreator, customActionNodeInitializer)
    except:
	sys.stderr.write( "Failed to register node: %s" % kWedgeNodeTypeName )
	raise
	    
    try:
	mplugin.registerCommand(kCmdName, cmdCreator, cmdSyntaxCreator)
    except:
	sys.stderr.write( "Failed to register command: %s" % kCmdName )
	raise

def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
	
    try:
	mplugin.deregisterNode( kWedgeNodeId )
	mplugin.deregisterNode(kCacheActionNodeId)
	mplugin.deregisterNode(kCustomActionNodeId)
	mplugin.deregisterNode(kPlayblastActionNodeId)
    except:
	sys.stderr.write( "Failed to deregister node: %s" % kWedgeNodeTypeName )
	raise
		
    try:
	mplugin.deregisterCommand(kCmdName)
    except:
	sys.stderr.write( "Failed to deregister command: %s" % kCmdName )
	raise