import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

kPluginNodeName = "normalizeForce"
kPluginNodeId = OpenMaya.MTypeId(0x0012b813)

class normalizeForce(OpenMayaMPx.MPxNode):
	inputArray = OpenMaya.MObject()
	outputArray = OpenMaya.MObject()

	def __init__(self):
		OpenMayaMPx.MPxNode.__init__(self)
		
	def postConstructor(self):
		self.setExistWithoutOutConnections(True)
		
	def compute(self, plug, dataBlock):
		if plug == normalizeForce.outputArray:
			stateData = 0
			state = OpenMayaMPx.cvar.MPxNode_state
			stateData = dataBlock.outputValue(state)
				
			# Check for bypass
			if stateData.asShort() == 1:
				inputArrayData = dataBlock.inputValue(normalizeForce.inputArray).data()
				outputArrayValue = dataBlock.outputValue(normalizeForce.outputArray)
				outputArrayValue.setMObject(inputArrayData)
				dataBlock.setClean(plug)
				return
			
			inputArrayData = dataBlock.inputValue(normalizeForce.inputArray).data()
			inputArrayFn = OpenMaya.MFnVectorArrayData(inputArrayData)
			inputArrayEdit = OpenMaya.MVectorArray()
			inputArrayFn.copyTo(inputArrayEdit)
			
			for i in range(inputArrayEdit.length()):
				inputArrayEdit.set(inputArrayEdit[i].normal(), i)
			
			outputArrayFn = OpenMaya.MFnVectorArrayData()
			outputArrayObject = outputArrayFn.create(inputArrayEdit)
			outputArrayValue = dataBlock.outputValue(normalizeForce.outputArray)
			outputArrayValue.setMObject(outputArrayObject)
			dataBlock.setClean(plug)
		else:
			return OpenMaya.kUnknownParameter
			
		
def nodeCreator():
	return OpenMayaMPx.asMPxPtr(normalizeForce())
	
def nodeInitializer():
	tAttr = OpenMaya.MFnTypedAttribute()
	nAttr = OpenMaya.MFnNumericAttribute()
	eAttr = OpenMaya.MFnEnumAttribute()
	
	normalizeForce.inputArray = tAttr.create('inputForce', 'if', OpenMaya.MFnData.kVectorArray)
	normalizeForce.outputArray = tAttr.create('outputForce', 'of', OpenMaya.MFnData.kVectorArray)
	tAttr.storable = False
	tAttr.writeable = False
	
	normalizeForce.addAttribute(normalizeForce.outputArray)
	normalizeForce.addAttribute(normalizeForce.inputArray)
	
	normalizeForce.attributeAffects(normalizeForce.inputArray, normalizeForce.outputArray)

def initializePlugin(obj):
	mplugin = OpenMayaMPx.MFnPlugin(obj, "", "", "Any")
	
	try:
		mplugin.registerNode( kPluginNodeName, kPluginNodeId, nodeCreator, nodeInitializer)
	except:
		raise RuntimeError, "Failed to register node"

def uninitializePlugin(obj):
	mplugin = OpenMayaMPx.MFnPlugin(obj)
	try:
		mplugin.deregisterNode( kPluginNodeId )
	except:
		raise RuntimeError, "Failed to deregister node"