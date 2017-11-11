//
// Copyright (C) 2017 Anders Elmholdt
//

#include "UtilityFunctions.h"
#include <maya/MPlugArray.h>

namespace utility
{	
	MObject getDestinationNode(MPlug & plug, MStatus * stat)
	{
		MPlugArray inputPlugs;
		plug.connectedTo(inputPlugs, true, false);
		if (inputPlugs.length() > 0)
		{
			if (stat) *stat = MS::kSuccess;
			return inputPlugs[0].node();
		}

		if (stat) *stat = MS::kFailure;
		return MObject();
	}
}