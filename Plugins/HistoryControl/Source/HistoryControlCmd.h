//
// Copyright (C) 2017 Anders Elmholdt
//

#ifndef _HISTORY_CONTROL_CMD
#define _HISTORY_CONTROL_CMD

#include <maya/MPxCommand.h>
#include <maya/MDagModifier.h>
#include "CmpMeshModifierCmd.h"

class HistoryControlCmd : public CmpMeshModifierCmd
{
public:
	virtual MStatus doIt(const MArgList&);

	virtual MStatus HistoryControlCmd::initModifierNode(MObject &node, MDagModifier &dagMod);

	static void *creator() { return new HistoryControlCmd; }
	static MSyntax newSyntax();

	static const MString commandName;

private:
	int amount;
	static const char * const amountFlag;
	static const char * const amountLongFlag;
};

#endif