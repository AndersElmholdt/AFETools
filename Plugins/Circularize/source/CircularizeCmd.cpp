#include "CircularizeCmd.h"
#include <maya/MSyntax.h>
#include <maya/MGlobal.h>
#include <maya/MSelectionList.h>
#include <maya/MItSelectionList.h>
#include <maya/MDagPath.h>
#include <maya/MItMeshVertex.h>
#include <maya/MPoint.h>
#include <maya/MVector.h>
#include <maya/MVectorArray.h>
#include <maya/MPointArray.h>
#include <maya/MFnComponentListData.h>
#include "CircularizeNode.h"
#include <cmath>
#include <algorithm>

const MString CircularizeCmd::commandName("addCircularizeNode");
const char * const CircularizeCmd::radiusFlag = "-r";
const char * const CircularizeCmd::radiusLongFlag = "-radius";
const char * const CircularizeCmd::strengthFlag = "-s";
const char * const CircularizeCmd::strengthLongFlag = "-strength";
const char * const CircularizeCmd::twistFlag = "-t";
const char * const CircularizeCmd::twistLongFlag = "-twist";
const char * const CircularizeCmd::flattenFlag = "-f";
const char * const CircularizeCmd::flattenLongFlag = "-flatten";

MStatus CircularizeCmd::doIt(const MArgList &args)
{
	MStatus stat;
	
	// Load cmd args
	MArgDatabase argData(syntax(), args, &stat);
	radius = 1;
	strength = 1;
	twist = 0;
	flatten = false;
	autoEstimateRadius = true;
	if (argData.isFlagSet(radiusFlag))
	{
		argData.getFlagArgument(radiusFlag, 0, radius);
		autoEstimateRadius = false;
	}
	radius = std::max(0.0, radius);
	if (argData.isFlagSet(strengthFlag))
		argData.getFlagArgument(strengthFlag, 0, strength);
	if (argData.isFlagSet(flattenFlag))
		flatten = true;
	if (argData.isFlagSet(twistFlag))
		argData.getFlagArgument(twistFlag, 0, twist);

	// Load selection
	MSelectionList selection;
	MGlobal::getActiveSelectionList(selection);

	// Convert face/edge selection into verts
	MItSelectionList polyIter(selection, MFn::kMeshPolygonComponent);
	MItSelectionList edgeIter(selection, MFn::kMeshEdgeComponent);
	if (!polyIter.isDone())
	{
		MGlobal::executeCommand("ConvertSelectionToVertexPerimeter");
	}
	else if (!edgeIter.isDone())
	{
		MGlobal::executeCommand("ConvertSelectionToVertices");
	}

	// reload selection and get vert components
	MGlobal::getActiveSelectionList(selection);
	MItSelectionList vertIter(selection, MFn::kMeshVertComponent);
	int nMeshes = 0;
	if (!vertIter.isDone())
	{
		++nMeshes;
		vertIter.getDagPath(polyObject, components);
	}

	// Error check
	if (nMeshes == 0)
	{
		MGlobal::displayError("Select at least one poly object");
		return MS::kFailure;
	}

	CmpMeshModifierCmd::doIt(polyObject, CircularizeNode::typeId);

	return stat;
}

MStatus CircularizeCmd::initModifierNode(MObject & node, MDagModifier & dagMod)
{
	MFnDependencyNode depFn(node);
	MString name = depFn.name();

	// Get component IDs
	int nVerts = 0;
	MString vertList = "";
	MItMeshVertex vertIter(polyObject, components);
	for (; !vertIter.isDone(); vertIter.next())
	{
		vertList += MString("vtx[") + vertIter.index() + "] ";
		++nVerts;
	}

	// Set attributes
	dagMod.commandToExecute("setAttr -type componentList " + name + ".inputComponents " + nVerts + " " + vertList);
	if (!autoEstimateRadius) {
		dagMod.commandToExecute("setAttr " + name + ".autoEstimateRadius 0");
		dagMod.commandToExecute("setAttr " + name + ".radius " + radius);
	}
	dagMod.commandToExecute("setAttr " + name + ".twist " + twist);
	dagMod.commandToExecute("setAttr " + name + ".strength " + strength);
	if (!flatten)
		dagMod.commandToExecute("setAttr " + name + ".flatten 0");
	
	return MS::kSuccess;
}

MSyntax CircularizeCmd::newSyntax()
{
	MStatus stat;
	MSyntax syntax;
	stat = syntax.addFlag(radiusFlag, radiusLongFlag, MSyntax::kDouble);
	stat = syntax.addFlag(twistFlag, twistLongFlag, MSyntax::kDouble);
	stat = syntax.addFlag(flattenFlag, flattenLongFlag, MSyntax::kNoArg);
	stat = syntax.addFlag(strengthFlag, strengthLongFlag, MSyntax::kDouble);
	
	return syntax;
}
