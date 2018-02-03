import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

kPluginNodeName = "wedgeControl"
kPluginNodeId = OpenMaya.MTypeId(0x0012b805)
kTransformMatrixID = OpenMaya.MTypeId(0x0012b806)
kCmdName = "runWedges"

def createFluidCache(startFrame, endFrame, cacheName, stepFrame):
	OpenMaya.MGlobal.executeCommand('doCreateFluidCache 5 { "3", ' + str(startFrame) + ', ' + str(endFrame) + ', "OneFilePerFrame", "1", "","0", "' + cacheName + '", "0", "add", "0", ' + str(stepFrame) + ', "1","0","1","mcx", "1", "1", "1", "1", "1", "1", "1"}')

def createNclothCache(startFrame, endFrame, cacheName, stepFrame):
    OpenMaya.MGlobal.executeCommand('doCreateNclothCache 5 { "3", ' + str(startFrame) + ', ' + str(endFrame) + ', "OneFilePerFrame", "1", "","0", "' + cacheName + '", "0", "add", "0", ' + str(stepFrame) + ', "1","0","1","mcx"}')

class RunWedgesCommand(OpenMayaMPx.MPxCommand):
	def __init__(self):
		OpenMayaMPx.MPxCommand.__init__(self)
	def doIt(self, args):
		arg_data = OpenMaya.MArgDatabase(self.syntax(), args)
	
		name = ''
		if arg_data.isFlagSet('n'):
			name = arg_data.flagArgumentString('n', 0)
		else:
			OpenMaya.MGlobal.displayError('Must specify name attribute')
			raise
		
		selList = OpenMaya.MSelectionList()
		selList.add(name)
		obj = OpenMaya.MObject()
		selList.getDependNode(0, obj)
		
		depFn = OpenMaya.MFnDependencyNode(obj)
		try:
			num_plug = depFn.findPlug('numberOfWedges')
			curWedge_plug = depFn.findPlug('currentWedge')
			startFrame_plug = depFn.findPlug('startFrame') 
			endFrame_plug = depFn.findPlug('endFrame') 
			stepFrame_plug = depFn.findPlug('stepFrame') 
			name_plug = depFn.findPlug('cacheName') 
			object_plug = depFn.findPlug('objectName')
			type_plug = depFn.findPlug('cacheType')
		except:
			OpenMaya.MGlobal.displayError('Could not find the attribute.')
			raise
		
		numWedges = num_plug.asInt()
		startFrame = startFrame_plug.asInt()
		endFrame = endFrame_plug.asInt()
		stepFrame = stepFrame_plug.asDouble()
		cacheName = name_plug.asString()
		objectName = object_plug.asString()
		cacheType = type_plug.asInt()
		
		OpenMaya.MGlobal.executeCommand('select ' + objectName)
	
		for i in range(numWedges):
			curWedge_plug.setInt(i)
			
			if cacheType == 0:
				createNclothCache(startFrame, endFrame, cacheName + '_wedge_' + str(i), stepFrame)
			else:
				createFluidCache(startFrame, endFrame, cacheName + '_wedge_' + str(i), stepFrame)
				
			if i != numWedges-1:
				OpenMaya.MGlobal.executeCommand('deleteCacheFile 2 { "keep", "" }')

class wedgeControl(OpenMayaMPx.MPxTransform):
	numberOfWedges = OpenMaya.MObject()
	wedgeNumber = OpenMaya.MObject()
	startFrame = OpenMaya.MObject()
	endFrame = OpenMaya.MObject()
	stepFrame = OpenMaya.MObject()
	cacheName = OpenMaya.MObject()
	cacheType = OpenMaya.MObject()

	def __init__(self):
		OpenMayaMPx.MPxTransform.__init__(self)

def cmdCreator():
	return OpenMayaMPx.asMPxPtr(RunWedgesCommand())
	
def cmdSyntaxCreator():
	syntax = OpenMaya.MSyntax()
	syntax.addFlag('n', 'name', OpenMaya.MSyntax.kString)
	return syntax
		
def nodeCreator():
	return OpenMayaMPx.asMPxPtr(wedgeControl())

def nodeInitializer():
	nAttr = OpenMaya.MFnNumericAttribute()
	tAttr = OpenMaya.MFnTypedAttribute()
	eAttr = OpenMaya.MFnEnumAttribute()
	
	wedgeControl.numberOfWedges = nAttr.create('numberOfWedges', 'nw', OpenMaya.MFnNumericData.kLong, 1)
	nAttr.setMin(1)
	nAttr.setKeyable(True)
	wedgeControl.wedgeNumber = nAttr.create('currentWedge', 'cw', OpenMaya.MFnNumericData.kLong)
	nAttr.setMin(0)
	nAttr.setKeyable(True)
	wedgeControl.startFrame = nAttr.create('startFrame', 'sf', OpenMaya.MFnNumericData.kLong)
	nAttr.setKeyable(True)
	wedgeControl.endFrame = nAttr.create('endFrame', 'ef', OpenMaya.MFnNumericData.kLong)
	nAttr.setKeyable(True)
	nAttr.setDefault(1)
	wedgeControl.stepFrame = nAttr.create('stepFrame', 'st', OpenMaya.MFnNumericData.kDouble, 1.0)
	nAttr.setKeyable(True)
	nAttr.setMin(0.01)
	wedgeControl.cacheName = tAttr.create('cacheName', 'cn', OpenMaya.MFnData.kString)
	tAttr.setKeyable(True)
	wedgeControl.objectName = tAttr.create('objectName', 'on', OpenMaya.MFnData.kString)
	tAttr.setKeyable(True)
	wedgeControl.cacheType = eAttr.create('cacheType', 'ct')
	eAttr.addField('MObject', 0)
	eAttr.addField('Fluid', 1)
	
	wedgeControl.addAttribute(wedgeControl.numberOfWedges)
	wedgeControl.addAttribute(wedgeControl.wedgeNumber)
	wedgeControl.addAttribute(wedgeControl.startFrame)
	wedgeControl.addAttribute(wedgeControl.endFrame)
	wedgeControl.addAttribute(wedgeControl.stepFrame)
	wedgeControl.addAttribute(wedgeControl.cacheName)
	wedgeControl.addAttribute(wedgeControl.objectName)
	wedgeControl.addAttribute(wedgeControl.cacheType)

def initializePlugin(obj):
	mplugin = OpenMayaMPx.MFnPlugin(obj, "", "", "Any")
	matrix  = OpenMayaMPx.MPxTransformationMatrix
	
	try:
		mplugin.registerTransform( kPluginNodeName, kPluginNodeId, nodeCreator, nodeInitializer, matrix, kTransformMatrixID)
	except:
		raise RuntimeError, "Failed to register node"
		
	try:
		mplugin.registerCommand(kCmdName, cmdCreator, cmdSyntaxCreator)
	except:
		raise RuntimeError, "Failed to register command"

def uninitializePlugin(obj):
	mplugin = OpenMayaMPx.MFnPlugin(obj)
	try:
		mplugin.deregisterNode( kPluginNodeId )
	except:
		raise RuntimeError, "Failed to deregister node"
	try:
		mplugin.deregisterCommand(kCmdName)
	except:
		raise RuntimeError, "Failed to deregister command"