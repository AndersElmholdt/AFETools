//
// Copyright (C) 2017 Anders Elmholdt
//

#ifndef _HISTORY_NODE
#define _HISTORY_NODE

#include <maya/MPxNode.h>
#include <maya/MCallbackIdArray.h>
#include <maya/MNodeMessage.h>

class HistoryControlNode : public MPxNode
{
public:
	friend void attributesChanged(MNodeMessage::AttributeMessage, MPlug&, MPlug&, void*);

	MStatus compute(const MPlug&, MDataBlock&) override;
	void postConstructor() override;

	static MStatus initialize();
	static void *creator() { return new HistoryControlNode(); }

	static const MTypeId typeId;
	static const MString typeName;
	static MCallbackIdArray callbackIds;

private:
	void updateActiveNode();

	static MObject inputPolymesh;
	static MObject activeNode;
	static MObject amount;
	static MObject output;
};

void attributesChanged(MNodeMessage::AttributeMessage, MPlug&, MPlug&, void*);

#endif