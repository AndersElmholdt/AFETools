//
// Copyright (C) 2017 Anders Elmholdt
//

#include "HistoryControlNode.h"
#include "UtilityFunctions.h"
#include <maya/MFnTypedAttribute.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MCallbackIdArray.h>
#include <maya/MPlugArray.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MDGModifier.h>
#include <algorithm>

const MTypeId HistoryControlNode::typeId(0x0012b801);
const MString HistoryControlNode::typeName("historyControl");
MCallbackIdArray HistoryControlNode::callbackIds;

MObject HistoryControlNode::inputPolymesh;
MObject HistoryControlNode::activeNode;
MObject HistoryControlNode::amount;
MObject HistoryControlNode::output;

MStatus HistoryControlNode::compute(const MPlug &plug, MDataBlock &data)
{
	MStatus stat;

	if (plug == output)
	{
		MDataHandle inHnd;
		MDataHandle outHnd = data.outputValue(output, &stat);
		MDataHandle stateHnd = data.inputValue(state);
		int state = stateHnd.asInt();
		if (state == 1)	// Pass through
			inHnd = data.inputValue(inputPolymesh, &stat);
		else			// Normal
			inHnd = data.inputValue(activeNode, &stat);

		stat = outHnd.set(inHnd.asMesh());
		stat = data.setClean(plug);
	}
	else
		return MS::kUnknownParameter;

	return stat;
}

void HistoryControlNode::postConstructor()
{
	MStatus stat;
	MCallbackId id;
	id = MNodeMessage::addAttributeChangedCallback(thisMObject(), attributesChanged, this, &stat);

	if (stat)
		callbackIds.append(id);
	else
		PRINT_ERROR("Unable to setup attribute changed callback");
}

MStatus HistoryControlNode::initialize()
{
	MFnTypedAttribute tAttr;
	MFnNumericAttribute numAttr;

	inputPolymesh = tAttr.create("inputPolymesh", "im", MFnData::kMesh);
	tAttr.setHidden(true);
	activeNode = tAttr.create("activeNode", "an", MFnData::kMesh);
	tAttr.setHidden(true);
	amount = numAttr.create("amount", "am", MFnNumericData::kInt, 1);
	numAttr.setChannelBox(true);
	numAttr.setMin(0);
	output = tAttr.create("output", "out", MFnData::kMesh);
	tAttr.setHidden(true);

	addAttribute(inputPolymesh);
	addAttribute(activeNode);
	addAttribute(amount);
	addAttribute(output);

	attributeAffects(inputPolymesh, output);
	attributeAffects(activeNode, output);
	
	return MS::kSuccess;
}

void HistoryControlNode::updateActiveNode()
{
	MStatus stat;

	MPlug activeNodePlug(thisMObject(), activeNode);
	MObject oldActiveNode = utility::getDestinationNode(activeNodePlug, &stat);
	MFnDependencyNode oldActiveNodeFn(oldActiveNode, &stat);
	MPlug oldActiveNodeOutPlug = oldActiveNodeFn.findPlug(MString("output"), false, &stat);
	if (oldActiveNodeOutPlug.isNull())
	{
		oldActiveNodeOutPlug = oldActiveNodeFn.findPlug(MString("outMesh"), false, &stat);
		if (oldActiveNodeOutPlug.isNull())
			oldActiveNodeOutPlug = oldActiveNodeFn.findPlug(MString("outputGeometry"), false, &stat);
	}

	MPlug inPlug(thisMObject(), inputPolymesh);

	MPlug amountPlug(thisMObject(), amount);
	if (amountPlug.isNull())
		PRINT_ERROR("Amount plug is null");
	int amountNum = amountPlug.asInt() + 1;

	MObject newActiveNode;
	for (int i = 0; i < amountNum; ++i)
	{
		newActiveNode = utility::getDestinationNode(inPlug, &stat);
		if (newActiveNode.isNull())
		{
			if (i != 0)
				amountPlug.setInt(i-1);
			return;
		}

		MFnDependencyNode newActiveNodeFn(newActiveNode, &stat);
		inPlug = newActiveNodeFn.findPlug(MString("inputPolymesh"), true);
		if (inPlug.isNull())
			inPlug = newActiveNodeFn.findPlug(MString("inputGeometry"), true);
	}

	MFnDependencyNode newActiveNodeFn(newActiveNode, &stat);

	MPlug outPlug = newActiveNodeFn.findPlug(MString("output"), false);
	if (outPlug.isNull())
	{
			outPlug = newActiveNodeFn.findPlug(MString("outMesh"), false);
			if (outPlug.isNull())
				outPlug = newActiveNodeFn.findPlug(MString("outputGeometry"), false);
	}
	
	MDGModifier mdg;
	mdg.disconnect(oldActiveNodeOutPlug, activeNodePlug);
	mdg.connect(outPlug, activeNodePlug);
	mdg.doIt();
}

void attributesChanged(MNodeMessage::AttributeMessage msg, MPlug &plug, MPlug &otherPlug, void *clientData)
{
	if (plug == HistoryControlNode::amount || plug == HistoryControlNode::inputPolymesh)
	{
		HistoryControlNode* currentNode = static_cast<HistoryControlNode*>(clientData);
		currentNode->updateActiveNode();
	}
}
