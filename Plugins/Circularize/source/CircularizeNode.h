#pragma once

#include <maya/MPxNode.h>
#include <maya/MPoint.h>
#include <vector>
#include <maya/MPointArray.h>
#include <maya/MNodeMessage.h>
#include <maya/MCallbackIdArray.h>

class CircularizeNode : public MPxNode
{
public:

	MStatus compute(const MPlug&, MDataBlock&) override;
	
	static MStatus initialize();
	static void *creator() { return new CircularizeNode(); }

	static const MTypeId typeId;
	static const MString typeName;
	
private:
	MStatus sortPoints(MPointArray&, MPoint &centerPoint, MIntArray&);
	void onFailure(MDataBlock&);

	static MObject inputPolymesh;
	static MObject inputComponents;
	static MObject twist;
	static MObject radius;
	static MObject autoEstimateRadius;
	static MObject flatten;
	static MObject strength;
	static MObject output;
};
