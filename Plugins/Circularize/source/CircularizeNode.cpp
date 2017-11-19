#define _USE_MATH_DEFINES

#include "CircularizeNode.h"
#include <maya/MFnTypedAttribute.h>
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
#include <maya/MFnMeshData.h>
#include <maya/MFnMesh.h>
#include <maya/MFnComponentListData.h>
#include <maya/MPointArray.h>
#include <maya/MFnSingleIndexedComponent.h>
#include <maya/MGlobal.h>
#include <maya/MQuaternion.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnNumericData.h>
#include <maya/MBoundingBox.h>
#include <maya/MNodeMessage.h>
#include <map>
#include <cmath>
#include <algorithm>

const MTypeId CircularizeNode::typeId(0x0012b802);
const MString CircularizeNode::typeName("circularize");

MObject CircularizeNode::inputPolymesh;
MObject CircularizeNode::inputComponents;
MObject CircularizeNode::twist;
MObject CircularizeNode::radius;
MObject CircularizeNode::autoEstimateRadius;
MObject CircularizeNode::flatten;
MObject CircularizeNode::strength;
MObject CircularizeNode::output;

// TODO: support symmetry
MStatus CircularizeNode::compute(const MPlug &plug, MDataBlock &data)
{
	MStatus stat;
	
	if (plug == output || plug == radius)
	{	
		MDataHandle inMeshHnd = data.inputValue(inputPolymesh);
		MDataHandle inComponentsHnd = data.inputValue(inputComponents);
		MDataHandle autoRadiusHnd = data.inputValue(autoEstimateRadius);
		MDataHandle twistHnd = data.inputValue(twist);
		MDataHandle flattenHnd = data.inputValue(flatten);
		MDataHandle strengthHnd = data.inputValue(strength);
		MDataHandle outHnd = data.outputValue(output);
		MDataHandle stateHnd = data.inputValue(state);

		MObject inMeshData = inMeshHnd.asMesh();
		int iState = stateHnd.asInt();
		if (iState == 1) // Pass through
		{
			outHnd.set(inMeshData);
			data.setClean(plug);
			return MS::kSuccess;
		}

		MObject inComponentsData = inComponentsHnd.data();
		bool bFlatten = flattenHnd.asBool();
		bool bAutoRadius = autoRadiusHnd.asBool();
		double dStrength = std::min(std::max(strengthHnd.asDouble(), 0.0), 1.0);
		double dTwist = twistHnd.asDouble() / 360 * 2 * M_PI;

		MFnMeshData meshDataFn;
		MObject newMeshData = meshDataFn.create();
		MFnMesh inMeshFn(inMeshData);
		inMeshFn.copy(inMeshData, newMeshData);
		MFnMesh newMeshFn(newMeshData);

		MFnComponentListData compListFn(inComponentsData);
		MIntArray compIds;

		unsigned int nComps = 0;
		for (unsigned int i = 0; i < compListFn.length(); ++i)
		{		
			MObject comp = compListFn[i];
			MFnSingleIndexedComponent siComp(comp, &stat);
			for (int j = 0; j < siComp.elementCount(); ++j) {
				compIds.append(siComp.element(j));
				++nComps;
			}
		}
		if (nComps == 0)
		{
			MGlobal::displayError("Cannot circularize without any input components");
			onFailure(data);
			return MS::kFailure;
		}
		
		// Load vertex information
		MVector averageNormal;
		MPointArray vertexArray;
		for (unsigned int i = 0; i < nComps; ++i)
		{
			// Maybe use getRawpoints to optimize?
			MPoint point;
			newMeshFn.getPoint(compIds[i], point);
			vertexArray.append(point);

			MVector normal;
			newMeshFn.getVertexNormal(compIds[i], normal);
			averageNormal += normal;
		}
		averageNormal /= nComps;

		// Rotate points to lie on XY plane
		MBoundingBox boundingBox = MBoundingBox();
		MQuaternion rotation = averageNormal.rotateTo(MVector(0, 0, 1));
		for (unsigned int i = 0; i < nComps; ++i)
		{
			vertexArray[i] = MVector(vertexArray[i]).rotateBy(rotation);
			boundingBox.expand(vertexArray[i]);
		}

		// Auto estimate radius
		if (bAutoRadius)
		{
			MDataHandle radiusOutHnd = data.outputValue(radius);
			radiusOutHnd.setDouble(std::min(boundingBox.width(), boundingBox.height()) / 2);
			radiusOutHnd.setClean();
		}

		// Load radius amount
		MDataHandle radiusInHnd = data.inputValue(radius);
		double dRadius = radiusInHnd.asDouble();

		// Get sorted array indices by Angle
		MPoint centerPoint = boundingBox.center();
		MIntArray sortedArrayIndices = MIntArray();
		stat = sortPoints(vertexArray, centerPoint, sortedArrayIndices);

		// Error check
		if (!stat)
		{
			MGlobal::displayError("Failed to circularize vertices, some components are possibly overlapping");
			onFailure(data);
			return MS::kFailure;
		}

		// Circularize
		double radius = 0.1;
		for (unsigned int i = 0; i < nComps; ++i)
		{
			double x = std::sin(double(i) / nComps * 2 * M_PI + dTwist) * dRadius + centerPoint.x;
			double y = std::cos(double(i) / nComps * 2 * M_PI + dTwist) * dRadius + centerPoint.y;
			double z = (bFlatten) ? centerPoint.z : vertexArray[sortedArrayIndices[i]].z;
			vertexArray[sortedArrayIndices[i]] = MPoint(x, y, z) * dStrength + vertexArray[sortedArrayIndices[i]] * (1 - dStrength);
		}

		// Rotate points back to original plane
		rotation.invertIt();
		for (unsigned int i = 0; i < nComps; ++i)
		{
			vertexArray[i] = MVector(vertexArray[i]).rotateBy(rotation);
		}

		// Assign vertex information
		for (unsigned int i = 0; i < nComps; ++i)
		{
			newMeshFn.setPoint(compIds[i], vertexArray[i]);
		}
		newMeshFn.updateSurface();
		outHnd.set(newMeshData);

		data.setClean(plug);
	}
	else
		return MS::kUnknownParameter;
	
	return MS::kSuccess;
}

MStatus CircularizeNode::initialize()
{
	MFnTypedAttribute tAttr;
	MFnNumericAttribute nAttr;

	inputPolymesh = tAttr.create("inputPolymesh", "im", MFnData::kMesh);
	tAttr.setHidden(true);
	inputComponents = tAttr.create("inputComponents", "ic", MFnData::kComponentList);
	tAttr.setHidden(true);
	autoEstimateRadius = nAttr.create("autoEstimateRadius", "ar", MFnNumericData::kBoolean);
	nAttr.setChannelBox(true);
	nAttr.setDefault(true);
	radius = nAttr.create("radius", "rad", MFnNumericData::kDouble);
	nAttr.setKeyable(true);
	nAttr.setMin(0);
	nAttr.setSoftMax(5);
	twist = nAttr.create("twist", "tw", MFnNumericData::kDouble);
	nAttr.setKeyable(true);
	nAttr.setSoftMin(-360);
	nAttr.setSoftMax(360);
	flatten = nAttr.create("flatten", "fl", MFnNumericData::kBoolean);
	nAttr.setChannelBox(true);
	nAttr.setDefault(true);
	strength = nAttr.create("strength", "st", MFnNumericData::kDouble);
	nAttr.setKeyable(true);
	nAttr.setDefault(1.0);
	nAttr.setMin(0);
	nAttr.setMax(1);
	output = tAttr.create("output", "out", MFnData::kMesh);
	tAttr.setHidden(true);

	addAttribute(inputPolymesh);
	addAttribute(inputComponents);
	addAttribute(flatten);
	addAttribute(autoEstimateRadius);
	addAttribute(radius);
	addAttribute(twist);
	addAttribute(strength);
	addAttribute(output);

	attributeAffects(inputPolymesh, output);
	attributeAffects(inputComponents, output);
	attributeAffects(twist, output);
	attributeAffects(radius, output);
	attributeAffects(autoEstimateRadius, output);
	attributeAffects(flatten, output);
	attributeAffects(strength, output);
	
	return MS::kSuccess;
}

// TODO: Alternative enhanced algorithm based on pathfinding algorithms + angle
MStatus CircularizeNode::sortPoints(MPointArray &pointArray, MPoint &centerPoint, MIntArray &intArray)
{
	std::map<double, int> sortedIndices;
	MVector upVec(0, 1, 0);
	unsigned int nPoints = pointArray.length();
	for (unsigned int i = 0; i < nPoints; ++i)
	{
		MVector posVec = (pointArray[i] - centerPoint).normal();
		double angle = upVec.angle(posVec) / (2 * M_PI) * 360;
		if (posVec[0] < centerPoint[0])
			angle = 360 - angle;

		// If 2 or more verts have same angle, return failure
		if (!sortedIndices.insert(std::make_pair(angle, i)).second)
		{
			return MS::kFailure;
		}
	}

	intArray.clear();
	for (auto map_it = sortedIndices.cbegin(); map_it != sortedIndices.cend(); ++map_it)
	{
		intArray.append(map_it->second);
	}
	
	return MS::kSuccess;
}

void CircularizeNode::onFailure(MDataBlock &data)
{
	MDataHandle stateOutHnd = data.outputValue(state);
	stateOutHnd.setInt(1); // Change node behaviour to passthrough
	stateOutHnd.setClean();
}
