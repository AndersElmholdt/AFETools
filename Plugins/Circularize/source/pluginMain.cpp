//
// Copyright (C) 2017 Anders Elmholdt
//

#include <maya/MFnPlugin.h>
#include "CircularizeCmd.h"
#include "CircularizeNode.h"

MStatus initializePlugin(MObject obj)
{
	MStatus stat;
	MFnPlugin plugin(obj, "Anders Elmholdt", "0.1", "Any");
	
	stat = plugin.registerCommand(CircularizeCmd::commandName, CircularizeCmd::creator, CircularizeCmd::newSyntax);
	CHECK_MSTATUS_AND_RETURN_IT(stat);

	stat = plugin.registerNode(CircularizeNode::typeName, CircularizeNode::typeId, CircularizeNode::creator, CircularizeNode::initialize);
	CHECK_MSTATUS_AND_RETURN_IT(stat);

	return stat;
}

MStatus uninitializePlugin(MObject obj)
{
	MStatus stat;
	MFnPlugin plugin(obj);

	stat = plugin.deregisterCommand(CircularizeCmd::commandName);
	CHECK_MSTATUS_AND_RETURN_IT(stat);

	stat = plugin.deregisterNode(CircularizeNode::typeId);
	CHECK_MSTATUS_AND_RETURN_IT(stat);

	return stat;
}
