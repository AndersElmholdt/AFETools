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
#include <maya/MArgDatabase.h>
#include <maya/MFloatVector.h>
#include <maya/MPlugArray.h>

const MString HistoryControlCmd::commandName("addHistoryControl");
const char * const HistoryControlCmd::amountFlag = "-a";
const char * const HistoryControlCmd::amountLongFlag = "-amount";

MStatus HistoryControlCmd::doIt(const MArgList &args)
{
	MStatus stat;

	// Get cmd options
	amount = 1;
	MArgDatabase argData(syntax(), args, &stat);
	CHECK_MSTATUS_AND_PRINT_ERROR(stat, "Invalid input flags");

	if (argData.isFlagSet(amountFlag))
		argData.getFlagArgument(amountFlag, 0, amount);
	if (amount < 0)
		amount = 1;

	MSelectionList selection;
	MGlobal::getActiveSelectionList(selection);

	int nSelMeshes = 0;
	MDagPath dagPath;
	MItSelectionList iter(selection, MFn::kMesh);
	for (; !iter.isDone(); iter.next())
	{
		nSelMeshes++;

		iter.getDagPath(dagPath);
		dagPath.extendToShape();

		break;
	}

	if (nSelMeshes == 0)
	{
		MGlobal::displayWarning("Select one or more meshes");
		return MS::kFailure;
	}

	CmpMeshModifierCmd::doIt(dagPath, HistoryControlNode::typeId);

	return MS::kSuccess;
}

MStatus HistoryControlCmd::initModifierNode(MObject & node, MDagModifier & dagMod)
{
	MStatus stat;

	MFnDependencyNode depFn(node);
	stat = dagMod.newPlugValueInt(depFn.findPlug("amount"), amount);

	return stat;
}

MSyntax HistoryControlCmd::newSyntax()
{
	MStatus stat;
	MSyntax syntax;
	stat = syntax.addFlag(amountFlag, amountLongFlag, MSyntax::kLong);
	if (!stat)
		PRINT_ERROR("Unable to add amount flag");

	return syntax;
}