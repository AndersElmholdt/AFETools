//
// Copyright (C) 2017 Anders Elmholdt
//

#include <maya/MFnPlugin.h>
#include "UtilityFunctions.h"
#include "HistoryControlNode.h"
#include "HistoryControlCmd.h"

MStatus initializePlugin(MObject obj)
{
	MStatus stat;
	MFnPlugin plugin(obj, "Anders Elmholdt", "0.2", "Any");

	stat = plugin.registerNode(HistoryControlNode::typeName, HistoryControlNode::typeId, HistoryControlNode::creator, HistoryControlNode::initialize);
	CHECK_MSTATUS_AND_PRINT_ERROR(stat, "Unable to register node: " + HistoryControlNode::typeName);

	stat = plugin.registerCommand(HistoryControlCmd::commandName, HistoryControlCmd::creator, HistoryControlCmd::newSyntax);
	CHECK_MSTATUS_AND_PRINT_ERROR(stat, "Unable to register command: " + HistoryControlCmd::commandName);

	return stat;
}

MStatus uninitializePlugin(MObject obj)
{
	MStatus stat;
	MFnPlugin plugin(obj);

	for (unsigned int i = 0; i < HistoryControlNode::callbackIds.length(); ++i)
	{
		stat = MMessage::removeCallback(HistoryControlNode::callbackIds[i]);
		CHECK_MSTATUS_AND_PRINT_ERROR(stat, "Unable to remove callback ids");
	}

	stat = plugin.deregisterNode(HistoryControlNode::typeId);
	CHECK_MSTATUS_AND_PRINT_ERROR(stat, "Unable to deregister node: " + HistoryControlNode::typeName);

	stat = plugin.deregisterCommand(HistoryControlCmd::commandName);
	CHECK_MSTATUS_AND_PRINT_ERROR(stat, "Unable to deregister command: " + HistoryControlCmd::commandName);

	return stat;
}
