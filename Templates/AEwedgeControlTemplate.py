import maya.cmds as cmds

from PySide2 import QtCore, QtGui, QtWidgets
import maya.OpenMayaUI as mui
import shiboken2

################################################################################
#Base Attribute Widget
################################################################################
class BaseAttrWidget(QtWidgets.QWidget):
    '''
    This is the base attribute widget from which all other attribute widgets
    will inherit. Sets up all the relevant methods + common widgets and initial
    layout.
    '''
    def __init__(self, node, attr, label='', parent=None):
        '''
        Initialize

        @type node: str
        @param node: The name of the node that this widget should start with.
        @type attr: str
        @param attr: The name of the attribute this widget is responsible for.
        @type label: str
        @param label: The text that should be displayed in the descriptive label.
        '''
        super(BaseAttrWidget, self).__init__(parent)

        self.node = node    #: Store the node name
        self.attr = attr    #: Store the attribute name

        #: This will store information about the scriptJob that we will create
        #: so that we can update this widget whenever its attribute is updated
        #: separately.
        self.sj = None

        #: Use this variable to track whether the gui is currently being updated
        #: or not.
        self.updatingGUI = False
	self.forceUpdateGUI = False

        ########################################################################
        #Widgets
        ########################################################################
        #: The QLabel widget with the name of the attribute
	if label:
	    self.label = QtWidgets.QLabel(label if label else attr, parent=self)

        ########################################################################
        #Layout
        ########################################################################
        self.layout = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.LeftToRight, self)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(5)

	if label:
	    self.layout.addWidget(self.label)
		
    def updateGUI(self):
	raise NotImplementedError
		
    def updateAttr(self):
	raise NotImplementedError
		
    def callUpdateGUI(self):
	self.updatingGUI = True
	self.updateGUI()
	self.updatingGUI = False
		
    def callUpdateAttr(self):
	if not self.updatingGUI:
	    self.updateAttr()
			
    def setNode(self, node):
	'''
	This widget should now represent the same attr on a different node.
	'''
	oldNode = self.node
	self.node = node
	self.forceUpdateGUI = True
	self.callUpdateGUI()
	self.forceUpdateGUI = False
    
	if not self.sj or not cmds.scriptJob(exists=self.sj) or not oldNode == self.node:
	    #script job
	    ct = 0
	    while self.sj:
		#Kill the old script job.
		try:
		    if cmds.scriptJob(exists=self.sj):
			cmds.scriptJob(kill=self.sj, force=True)
		    self.sj = None
		except RuntimeError:
		    #Could not kill the old script job for some reason.
		    #This happens, albeit very rarely, when that scriptJob is
		    #being executed at the same time we try to kill it. Pause
		    #for a second and then retry.
		    ct += 1
		    if ct < 10:
			cmds.warning("Got RuntimeError trying to kill scriptjob...trying again")
			time.sleep(1)
		    else:
			#We've failed to kill the scriptJob 10 consecutive times.
			#Time to give up and move on.
			cmds.warning("Killing scriptjob is taking too long...skipping")
			break

	    #Set the new scriptJob to call the callUpdateGUI method everytime the
	    #node.attr is changed.
	    self.sj = cmds.scriptJob(ac=['%s.%s' % (self.node, self.attr), self.callUpdateGUI], killWithScene=1)

class ListWidget(BaseAttrWidget):
    '''
    This widget can be used with string attributes.
    '''
    def __init__(self, node, attr, label='', parent=None):
        '''
        Initialize
        '''
        super(ListWidget, self).__init__(node, attr, label, parent)

	# create font
	font = QtGui.QFont()
	font.setPointSize(12)
	
	
        ########################################################################
        #Widgets
        ########################################################################
        #: The QLineEdit storing the value of the attribute
        self.valLE = QtWidgets.QListWidget(parent=self)
	self.valLE.setFont(font)
	self.valLE.itemDoubleClicked.connect(self.selectionEvent)

        ########################################################################
        #Layout
        ########################################################################
        self.layout.addWidget(self.valLE, 1)

        ########################################################################
        #Connections
        ########################################################################
        #We need to call the callUpdateAttr method whenever the user modifies the
        #value in valLE
        #self.connect(self.valLE, QtCore.SIGNAL("textChanged()"), self.callUpdateAttr)

        ########################################################################
        #Set the initial node
        ########################################################################
        self.setNode(node)

    def selectionEvent(self, item):
	cmds.select(item.text())

    def updateGUI(self):
        '''
        Implement this virtual method to update the value in valLE based on the
        current node.attr
        '''
	self.valLE.clear()
	connections = cmds.listConnections("%s.%s" % (self.node, self.attr))
	if connections is not None:
	    for connection in connections:
		self.valLE.addItem(connection)

    def updateAttr(self):
        '''
        Implement this virtual method to update the actual node.attr value to
        reflect what is currently in the UI.
        '''
	pass
        #cmds.setAttr("%s.%s" % (self.node, self.attr), str(self.valLE.toPlainText()), type='string') 

################################################################################
#Main AETemplate Widget
################################################################################
class AEwedgeCustomActionTemplate(QtWidgets.QWidget):
    '''
    The main class that holds all the controls for the uselessTransform node
    '''
    def __init__(self, node, parent=None):
        '''
        Initialize
        '''
        super(AEwedgeCustomActionTemplate, self).__init__(parent)
        self.node = node
		
        ########################################################################
        #Widgets
        ########################################################################
	self.strAttr = ListWidget(node, 'connectedWedgeActions', label='', parent=self)
	
	buttonHeight = 30
	
	self.upButton = QtWidgets.QPushButton('Move Up')
	self.upButton.setMinimumHeight(buttonHeight)
	self.upButton.setMaximumHeight(buttonHeight)
	self.upButton.clicked.connect(self.moveUp)
	
	self.downButton = QtWidgets.QPushButton('Move Down')
	self.downButton.setMinimumHeight(buttonHeight)
	self.downButton.setMaximumHeight(buttonHeight)
	self.downButton.clicked.connect(self.moveDown)
	
	self.deleteButton = QtWidgets.QPushButton('Delete Action')
	self.deleteButton.setMinimumHeight(buttonHeight)
	self.deleteButton.setMaximumHeight(buttonHeight)
	self.deleteButton.clicked.connect(self.deleteAction)
	
	self.createButton = QtWidgets.QPushButton('Create Action')
	self.createButton.setMinimumHeight(buttonHeight)
	self.createButton.setMaximumHeight(buttonHeight)
	self.createButton.clicked.connect(self.createAction)	

        ########################################################################
        #Layout
        ########################################################################
        self.layout = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.TopToBottom, self)
        self.layout.setContentsMargins(5,3,11,3)
        self.layout.setSpacing(5)
	self.layout.addWidget(self.strAttr)
	self.buttonLayout = QtWidgets.QHBoxLayout(self)
	self.buttonLayout.addWidget(self.upButton)
	self.buttonLayout.addWidget(self.downButton)
	self.buttonLayout.addWidget(self.deleteButton)
	self.buttonLayout.addWidget(self.createButton)
	self.layout.addLayout(self.buttonLayout)

    def setNode(self, node):
        '''
        Set the current node
        '''
        self.node = node
		
	self.strAttr.setNode(node)
	
    def moveUp(self):
	itemToMove = self.strAttr.valLE.currentItem()
	if itemToMove is None:
	    return
    
	actionToMove = itemToMove.text()
	indexToMove = self.strAttr.valLE.indexFromItem(itemToMove).row()
	actionToSwap = self.strAttr.valLE.item(max(0, indexToMove-1)).text()
    
	connection1 = cmds.listConnections('%s.message' % actionToMove, p=True)[0]
	connection2 = cmds.listConnections('%s.message' % actionToSwap, p=True)[0]
    
	cmds.connectAttr('%s.message' % actionToSwap, connection1, f=True)
	cmds.connectAttr('%s.message' % actionToMove, connection2, f=True)
	
    def moveDown(self):
	itemToMove = self.strAttr.valLE.currentItem()
	if itemToMove is None:
	    return
	
	actionToMove = itemToMove.text()
	indexToMove = self.strAttr.valLE.indexFromItem(itemToMove).row()
	actionToSwap = self.strAttr.valLE.item(min(self.strAttr.valLE.count()+1, indexToMove+1)).text()
	
	connection1 = cmds.listConnections('%s.message' % actionToMove, p=True)[0]
	connection2 = cmds.listConnections('%s.message' % actionToSwap, p=True)[0]
	
	cmds.connectAttr('%s.message' % actionToSwap, connection1, f=True)
	cmds.connectAttr('%s.message' % actionToMove, connection2, f=True)
	
    def deleteAction(self):
	actionToDelete = self.strAttr.valLE.currentItem().text()
	cmds.delete(actionToDelete)
	
    def createAction(self):
	selectedAction = cmds.confirmDialog(title='Create Action', message='Select Action Type', button=('Cache Action', 'Playblast Action', 'Custom Action'), icn='question')
	if selectedAction == 'dismiss':
	    return
	elif selectedAction == 'Cache Action':
	    selectedAction = 'wedgeCacheAction'
	elif selectedAction == 'Custom Action':
	    selectedAction = 'wedgeCustomAction'
	elif selectedAction == 'Playblast Action':
	    selectedAction = 'wedgePlayblastAction'
	
	customNode = str(cmds.createNode(selectedAction, ss=True))
	index = cmds.getAttr('%s.connectedWedgeActions' % (self.node), size=True)
	cmds.connectAttr(customNode + '.message', '%s.connectedWedgeActions[%i]' % (self.node, index))	

################################################################################
#Initialize/Update methods:
#   These are the methods that get called to Initialize & install the QT GUI
#   and to update/repoint it to a different node
################################################################################
def getLayout(lay):
    '''
    Get the layout object

    @type lay: str
    @param lay: The (full) name of the layout that we need to get

    @rtype: QtGui.QLayout (or child)
    @returns: The QLayout object
    '''
    ptr = mui.MQtUtil.findLayout(lay)
    return shiboken2.wrapInstance(long(ptr), QtWidgets.QWidget).children()[0]

def buildQT(lay, node):
    '''
    Build/Initialize/Install the QT GUI into the layout.

    @type lay: str
    @param lay: Name of the Maya layout to add the QT GUI to
    @type node: str
    @param node: Name of the node to (initially) connect to the QT GUI
    '''
    #get the layout object
    mLayout = getLayout(lay)

    #create the GUI/widget
    widg = AEwedgeCustomActionTemplate(node)

    #add the widget to the layout
    mLayout.addWidget(widg)

def updateQT(lay, node):
    '''
    Update the QT GUI to point to a different node

    @type lay: str
    @param lay: Name of the Maya layout to where the QT GUI lives
    @type node: str
    @param node: Name of the new node to connect to the QT GUI
    '''
    #get the layout
    mLayout = getLayout(lay)

    #find the widget
    for c in range(mLayout.count()):
        widg = mLayout.itemAt(c).widget()
        if isinstance(widg, AEwedgeCustomActionTemplate):
            #found the widget, update the node it's pointing to
            widg.setNode(node)
            break