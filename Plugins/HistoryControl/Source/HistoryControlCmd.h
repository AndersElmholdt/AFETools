//
// Copyright (C) 2017 Anders Elmholdt
//

#ifndef _HISTORY_CONTROL_CMD
#define _HISTORY_CONTROL_CMD

#include <maya/MPxCommand.h>
#include <maya/MDagModifier.h>

class HistoryControlCmd : public MPxCommand
{
public:
	MStatus doIt(const MArgList&) override;
	MStatus undoIt() override;
	MStatus redoIt() override;
	bool isUndoable() const override { return true; }

	static void *creator() { return new HistoryControlCmd; }
	static MSyntax newSyntax();

	static const MString commandName;

private:
	MDGModifier dgMod;

	static const char * const amountFlag;
	static const char * const amountLongFlag;
};

#endif