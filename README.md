AFE Shaders
=====================
This is a small but expanding collection of some shaders that I have developed for use in Autodesk Maya with Solidangle's Arnold renderer. However, since the shaders are developed using [Open Shading Language](https://github.com/imageworks/OpenShadingLanguage/) they should also work in all supporting renderers such as Pixar's Renderman or Blender's Cycles, even though the shaders have not been tested in any renderer other than Arnold.

Installation
=====================
To utilize the shaders, you must point the Arnold environment variable to the folder where the .osl and .mtl (From the <i>Shaders</i> folder) files are located, i.e. ARNOLD_PLUGIN_PATH=C:\solidangle\mtoadeploy\osl.

Furthermore, the .mel files (From the <i>Templates</i> folder) must be placed in the maya scripts folder, i.e. C:\Users\Username\Documents\maya\scripts.

For more information on installing OSL shaders refer to the [Arnold User Guide](https://support.solidangle.com/display/A5AFMUG/OSL+Shaders) aswell as the [Maya User Guide](https://knowledge.autodesk.com/support/maya/learn-explore/caas/CloudHelp/cloudhelp/2016/ENU/Maya/files/GUID-592870D2-92E6-44CC-AE54-2F79EC43076A-htm.html) for information on template installation.
