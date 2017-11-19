#pragma once

#include <maya/MPxCommand.h>
#include <maya/MDGModifier.h>
#include "CmpMeshModifierCmd.h"

class CircularizeCmd : public CmpMeshModifierCmd
{
public:
	virtual MStatus doIt(const MArgList&);

	virtual MStatus CircularizeCmd::initModifierNode(MObject &node, MDagModifier &dagMod);

	static void *creator() { return new CircularizeCmd(); };
	static MSyntax newSyntax();

	static const MString commandName;

private:
	MDagPath polyObject;
	MObject components;
	double radius;
	double strength;
	double twist;
	bool flatten;
	bool autoEstimateRadius;

	static const char * const radiusFlag;
	static const char * const radiusLongFlag;
	static const char * const flattenFlag;
	static const char * const flattenLongFlag;
	static const char * const strengthFlag;
	static const char * const strengthLongFlag;
	static const char * const twistFlag;
	static const char * const twistLongFlag;
};