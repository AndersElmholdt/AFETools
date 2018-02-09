import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

kPluginNodeName = "scaleForce"
kPluginNodeId = OpenMaya.MTypeId(0x0012b810)

class vectorArrayReverse(OpenMayaMPx.MPxNode):
	inputArray = OpenMaya.MObject()
	outputArray = OpenMaya.MObject()
	scaleValue = OpenMaya.MObject()

	def __init__(self):
		OpenMayaMPx.MPxNode.__init__(self)
		
	def postConstructor(self):
		self.setExistWithoutOutConnections(True)
		
	def compute(self, plug, dataBlock):
		if plug == vectorArrayReverse.outputArray:
			stateData = 0
			state = OpenMayaMPx.cvar.MPxNode_state
			stateData = dataBlock.outputValue(state)
				
			# Check for bypass
			if stateData.asShort() == 1:
				inputArrayData = dataBlock.inputValue(vectorArrayReverse.inputArray).data()
				outputArrayValue = dataBlock.outputValue(vectorArrayReverse.outputArray)
				outputArrayValue.setMObject(inputArrayData)
				dataBlock.setClean(plug)
				return
			
			inputArrayData = dataBlock.inputValue(vectorArrayReverse.inputArray).data()
			inputArrayFn = OpenMaya.MFnVectorArrayData(inputArrayData)
			inputArrayEdit = OpenMaya.MVectorArray()
			inputArrayFn.copyTo(inputArrayEdit)
			
			inputScalePlug = OpenMaya.MPlug(self.thisMObject(), self.scaleValue)
			xScale = inputScalePlug.child(0).asDouble()
			yScale = inputScalePlug.child(1).asDouble()
			zScale = inputScalePlug.child(2).asDouble()
			
			for i in range(inputArrayEdit.length()):
				newVal = OpenMaya.MVector(inputArrayEdit[i][0] * xScale, inputArrayEdit[i][1] * yScale, inputArrayEdit[i][2] * zScale)
				inputArrayEdit.set(newVal, i)
			
			outputArrayFn = OpenMaya.MFnVectorArrayData()
			outputArrayObject = outputArrayFn.create(inputArrayEdit)
			outputArrayValue = dataBlock.outputValue(vectorArrayReverse.outputArray)
			outputArrayValue.setMObject(outputArrayObject)
			dataBlock.setClean(plug)
		else:
			return OpenMaya.kUnknownParameter
			
		
def nodeCreator():
	return OpenMayaMPx.asMPxPtr(vectorArrayReverse())
	
def nodeInitializer():
	tAttr = OpenMaya.MFnTypedAttribute()
	nAttr = OpenMaya.MFnNumericAttribute()
	
	vectorArrayReverse.scaleValue = nAttr.createPoint('scaleForce', 'sf')
	
	vectorArrayReverse.inputArray = tAttr.create('inputForce', 'if', OpenMaya.MFnData.kVectorArray)
	vectorArrayReverse.outputArray = tAttr.create('outputForce', 'of', OpenMaya.MFnData.kVectorArray)
	tAttr.storable = False
	tAttr.writeable = False
	
	vectorArrayReverse.addAttribute(vectorArrayReverse.outputArray)
	vectorArrayReverse.addAttribute(vectorArrayReverse.inputArray)
	vectorArrayReverse.addAttribute(vectorArrayReverse.scaleValue)
	
	vectorArrayReverse.attributeAffects(vectorArrayReverse.inputArray, vectorArrayReverse.outputArray)
	vectorArrayReverse.attributeAffects(vectorArrayReverse.scaleValue, vectorArrayReverse.outputArray)

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