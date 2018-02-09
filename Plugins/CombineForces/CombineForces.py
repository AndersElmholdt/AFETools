import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

kPluginNodeName = "combineForces"
kPluginNodeId = OpenMaya.MTypeId(0x0012b811)

class combineForces(OpenMayaMPx.MPxNode):
	inputArray = OpenMaya.MObject()
	inputBArray = OpenMaya.MObject()
	outputArray = OpenMaya.MObject()
	operationAttr = OpenMaya.MObject()

	def __init__(self):
		OpenMayaMPx.MPxNode.__init__(self)
		
	def postConstructor(self):
		self.setExistWithoutOutConnections(True)
		
	def compute(self, plug, dataBlock):
		if plug == combineForces.outputArray:
			stateData = 0
			state = OpenMayaMPx.cvar.MPxNode_state
			stateData = dataBlock.outputValue(state)
				
			# Check for bypass
			if stateData.asShort() == 1:
				inputArrayData = dataBlock.inputValue(combineForces.inputArray).data()
				outputArrayValue = dataBlock.outputValue(combineForces.outputArray)
				outputArrayValue.setMObject(inputArrayData)
				dataBlock.setClean(plug)
				return
				
			operation = dataBlock.inputValue(combineForces.operationAttr).asInt()
			
			inputArrayData = dataBlock.inputValue(combineForces.inputArray).data()
			inputArrayFn = OpenMaya.MFnVectorArrayData(inputArrayData)
			inputArrayEdit = OpenMaya.MVectorArray()
			inputArrayFn.copyTo(inputArrayEdit)
			
			inputBArrayData = dataBlock.inputValue(combineForces.inputBArray).data()
			inputBArrayFn = OpenMaya.MFnVectorArrayData(inputBArrayData)
			inputBArrayEdit = OpenMaya.MVectorArray()
			inputBArrayFn.copyTo(inputBArrayEdit)
			
			for i in range(inputArrayEdit.length()):
				if operation == 0: # add
					newVal = OpenMaya.MVector(inputArrayEdit[i][0] + inputBArrayEdit[i][0], inputArrayEdit[i][1] + inputBArrayEdit[i][1], inputArrayEdit[i][2] + inputBArrayEdit[i][2])
				elif operation == 1: # subtract
					newVal = OpenMaya.MVector(inputArrayEdit[i][0] - inputBArrayEdit[i][0], inputArrayEdit[i][1] - inputBArrayEdit[i][1], inputArrayEdit[i][2] - inputBArrayEdit[i][2])
				elif operation == 2: # multiply
					newVal = OpenMaya.MVector(inputArrayEdit[i][0] * inputBArrayEdit[i][0], inputArrayEdit[i][1] * inputBArrayEdit[i][1], inputArrayEdit[i][2] * inputBArrayEdit[i][2])
				inputArrayEdit.set(newVal, i)
			
			outputArrayFn = OpenMaya.MFnVectorArrayData()
			outputArrayObject = outputArrayFn.create(inputArrayEdit)
			outputArrayValue = dataBlock.outputValue(combineForces.outputArray)
			outputArrayValue.setMObject(outputArrayObject)
			dataBlock.setClean(plug)
		else:
			return OpenMaya.kUnknownParameter
			
		
def nodeCreator():
	return OpenMayaMPx.asMPxPtr(combineForces())
	
def nodeInitializer():
	tAttr = OpenMaya.MFnTypedAttribute()
	nAttr = OpenMaya.MFnNumericAttribute()
	eAttr = OpenMaya.MFnEnumAttribute()
	
	combineForces.operationAttr = eAttr.create('operationType', 'ot')
	eAttr.addField('+', 0)
	eAttr.addField('-', 1)
	eAttr.addField('*', 2)
	
	combineForces.inputArray = tAttr.create('inputAForce', 'iaf', OpenMaya.MFnData.kVectorArray)
	combineForces.inputBArray = tAttr.create('inputBForce', 'ibf', OpenMaya.MFnData.kVectorArray)
	combineForces.outputArray = tAttr.create('outputForce', 'of', OpenMaya.MFnData.kVectorArray)
	tAttr.storable = False
	tAttr.writeable = False
	
	combineForces.addAttribute(combineForces.outputArray)
	combineForces.addAttribute(combineForces.inputArray)
	combineForces.addAttribute(combineForces.inputBArray)
	combineForces.addAttribute(combineForces.operationAttr)
	
	combineForces.attributeAffects(combineForces.inputArray, combineForces.outputArray)
	combineForces.attributeAffects(combineForces.inputBArray, combineForces.outputArray)
	combineForces.attributeAffects(combineForces.operationAttr, combineForces.outputArray)

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