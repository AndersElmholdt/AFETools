//
// Copyright (C) 2017 Anders Elmholdt
//

#include "HistoryControlCmd.h"
#include "HistoryControlNode.h"
#include "UtilityFunctions.h"
#include <maya/MSelectionList.h>
#include <maya/MGlobal.h>
#include <maya/MItSelectionList.h>
#include <maya/MDagPath.h>
#include <maya/MFnTransform.h>
#include <maya/MSyntax.h>

const MString HistoryControlCmd::commandName("addHistoryControl");

MStatus HistoryControlCmd::doIt(const MArgList &)
{
	MStatus stat;

	MSelectionList selection;
	stat = MGlobal::getActiveSelectionList(selection);
	CHECK_MSTATUS_AND_PRINT_ERROR(stat, "Unable to get selection list");

	MItSelectionList iter(selection, MFn::kTransform, &stat);
	CHECK_MSTATUS_AND_PRINT_ERROR(stat, "Unable to create selection iteration list");
	MDagPath tDagPath;

	if (iter.isDone())
		MGlobal::displayWarning("You must have a poly object selected to add a history control node");

	for (; !iter.isDone(); iter.next())
	{
		stat = iter.getDagPath(tDagPath);
		if (!stat)
			continue;

		unsigned int numShapes;
		stat = tDagPath.numberOfShapesDirectlyBelow(numShapes);
		if (!stat)
			continue;

		for (int i = 0; i < numShapes; ++i)
		{
			MDagPath sDagPath = tDagPath;
			sDagPath.extendToShapeDirectlyBelow(i);
			MFnDagNode sDagPathFn(sDagPath);
			MPlug inMeshPlug = sDagPathFn.findPlug("inMesh");
			MObject inNode = utility::getDestinationNode(inMeshPlug, &stat);

			if (inNode.isNull())
			{
				MGlobal::displayWarning("HistoryControl node not added for " + sDagPathFn.name() + " as it does not have any poly history");
				continue;
			}

			MFnDependencyNode inNodeFn(inNode, &stat);
			MPlug inNodeOutPlug = inNodeFn.findPlug("output", &stat);

			if (inNodeOutPlug.isNull())
			{
				MGlobal::displayWarning("Unable to add HistoryControl node for " + sDagPathFn.name());
				continue;
			}

			MObject historyNode = dgMod.createNode(HistoryControlNode::typeId, &stat);
			CHECK_MSTATUS_AND_PRINT_ERROR(stat, "Unable to create history control node");

			MFnDependencyNode historyFn(historyNode, &stat);

			stat = dgMod.disconnect(inNodeOutPlug, inMeshPlug);
			CHECK_MSTATUS_AND_PRINT_ERROR(stat, "Unable to disconnect connection between " + inNodeFn.name() + " and " + sDagPathFn.name());
			stat = dgMod.connect(historyFn.findPlug("output"), inMeshPlug);
			CHECK_MSTATUS_AND_PRINT_ERROR(stat, "Unable to establish connection between " + historyFn.name() + " and " + sDagPathFn.name());
			stat = dgMod.connect(inNodeOutPlug, historyFn.findPlug("inputPolymesh"));
			CHECK_MSTATUS_AND_PRINT_ERROR(stat, "Unable to establish connection between " + inNodeFn.name() + " and " + historyFn.name());
		}
	}

	return redoIt();
}

MStatus HistoryControlCmd::redoIt()
{
	return dgMod.doIt();
}

MStatus HistoryControlCmd::undoIt()
{
	return dgMod.undoIt();
}

MSyntax HistoryControlCmd::newSyntax()
{
	return MSyntax();
}