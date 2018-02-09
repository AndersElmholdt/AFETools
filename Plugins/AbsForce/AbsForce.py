import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

kPluginNodeName = "absForce"
kPluginNodeId = OpenMaya.MTypeId(0x0012b812)

class absForce(OpenMayaMPx.MPxNode):
	inputArray = OpenMaya.MObject()
	outputArray = OpenMaya.MObject()
	computeX = OpenMaya.MObject()
	computeY = OpenMaya.MObject()
	computeZ = OpenMaya.MObject()

	def __init__(self):
		OpenMayaMPx.MPxNode.__init__(self)
		
	def postConstructor(self):
		self.setExistWithoutOutConnections(True)
		
	def compute(self, plug, dataBlock):
		if plug == absForce.outputArray:
			stateData = 0
			state = OpenMayaMPx.cvar.MPxNode_state
			stateData = dataBlock.outputValue(state)
				
			# Check for bypass
			if stateData.asShort() == 1:
				inputArrayData = dataBlock.inputValue(absForce.inputArray).data()
				outputArrayValue = dataBlock.outputValue(absForce.outputArray)
				outputArrayValue.setMObject(inputArrayData)
				dataBlock.setClean(plug)
				return
			
			inputArrayData = dataBlock.inputValue(absForce.inputArray).data()
			inputArrayFn = OpenMaya.MFnVectorArrayData(inputArrayData)
			inputArrayEdit = OpenMaya.MVectorArray()
			inputArrayFn.copyTo(inputArrayEdit)
			
			computeXVal = dataBlock.inputValue(absForce.computeX).asBool()
			computeYVal = dataBlock.inputValue(absForce.computeY).asBool()
			computeZVal = dataBlock.inputValue(absForce.computeZ).asBool()
			
			for i in range(inputArrayEdit.length()):
				xVal = inputArrayEdit[i][0]
				yVal = inputArrayEdit[i][1]
				zVal = inputArrayEdit[i][2]
				if computeXVal == True:
					xVal = abs(xVal)
				if computeYVal == True:
					yVal = abs(yVal)
				if computeZVal == True:
					zVal = abs(zVal)
				inputArrayEdit.set(OpenMaya.MVector(xVal, yVal, zVal), i)
			
			outputArrayFn = OpenMaya.MFnVectorArrayData()
			outputArrayObject = outputArrayFn.create(inputArrayEdit)
			outputArrayValue = dataBlock.outputValue(absForce.outputArray)
			outputArrayValue.setMObject(outputArrayObject)
			dataBlock.setClean(plug)
		else:
			return OpenMaya.kUnknownParameter
			
		
def nodeCreator():
	return OpenMayaMPx.asMPxPtr(absForce())
	
def nodeInitializer():
	tAttr = OpenMaya.MFnTypedAttribute()
	nAttr = OpenMaya.MFnNumericAttribute()
	eAttr = OpenMaya.MFnEnumAttribute()
	
	absForce.computeX = nAttr.create('computeX', 'cx', OpenMaya.MFnNumericData.kBoolean, 1)
	absForce.computeY = nAttr.create('computeY', 'cy', OpenMaya.MFnNumericData.kBoolean, 1)
	absForce.computeZ = nAttr.create('computeZ', 'cz', OpenMaya.MFnNumericData.kBoolean, 1)
	
	absForce.inputArray = tAttr.create('inputForce', 'if', OpenMaya.MFnData.kVectorArray)
	absForce.outputArray = tAttr.create('outputForce', 'of', OpenMaya.MFnData.kVectorArray)
	tAttr.storable = False
	tAttr.writeable = False
	
	absForce.addAttribute(absForce.outputArray)
	absForce.addAttribute(absForce.inputArray)
	absForce.addAttribute(absForce.computeX)
	absForce.addAttribute(absForce.computeY)
	absForce.addAttribute(absForce.computeZ)
	
	absForce.attributeAffects(absForce.inputArray, absForce.outputArray)
	absForce.attributeAffects(absForce.computeX, absForce.outputArray)
	absForce.attributeAffects(absForce.computeY, absForce.outputArray)
	absForce.attributeAffects(absForce.computeZ, absForce.outputArray)

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