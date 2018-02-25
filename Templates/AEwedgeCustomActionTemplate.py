import maya.cmds as cmds

from PySide2 import QtCore, QtGui, QtWidgets
import maya.OpenMayaUI as mui
import shiboken2

class LineNumberArea(QtWidgets.QWidget):
    def __init__(self, editor):
	super(LineNumberArea, self).__init__(editor)
	self.editor = editor
	
    def sizeHint(self):
	return QtCore.Qsize(self.editor.lineNumberAreaWidth(), 0)
    
    def paintEvent(self, event):
	self.editor.lineNumberAreaPaintEvent(event)
	
class CodeEditor(QtWidgets.QPlainTextEdit):
    def __init__(self, parent):
	super(CodeEditor, self).__init__(parent)
	self.lineNumberArea = LineNumberArea(self)
	
	self.connect(self, QtCore.SIGNAL('blockCountChanged(int)'), self.updateLineNumberAreaWidth)
	self.connect(self, QtCore.SIGNAL('updateRequest(QRect, int)'), self.updateLineNumberArea)
	
	self.updateLineNumberAreaWidth(0)
	
    def lineNumberAreaWidth(self):
	digits = 1
	count = max(1, self.blockCount())
	while count >= 10:
	    count /= 10
	    digits += 1
	space = 3 + self.fontMetrics().width('9') * digits
	return space
    
    def updateLineNumberAreaWidth(self, _):
	self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)
	
    def updateLineNumberArea(self, rect, dy):
	
	if dy:
	    self.lineNumberArea.scroll(0, dy)
	else:
	    self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(),
	                                   rect.height())
	if rect.contains(self.viewport().rect()):
	    self.updateLineNumberAreaWidth(0)
	    
    def resizeEvent(self, event):
	super(CodeEditor, self).resizeEvent(event)
    
	cr = self.contentsRect();
	self.lineNumberArea.setGeometry(QtCore.QRect(cr.left(), cr.top(),
                                                  self.lineNumberAreaWidth(), cr.height()))
    
    def lineNumberAreaPaintEvent(self, event):
	painter = QtGui.QPainter(self.lineNumberArea)
	
	painter.fillRect(event.rect(), QtCore.Qt.darkGray)

	block = self.firstVisibleBlock()
	blockNumber = block.blockNumber()
	top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
	bottom = top + self.blockBoundingRect(block).height()

	# Just to make sure I use the right font
	height = self.fontMetrics().height()
	while block.isValid() and (top <= event.rect().bottom()):
	    if block.isVisible() and (bottom >= event.rect().top()):
		number = str(blockNumber + 1)
		painter.setPen(QtCore.Qt.black)
		painter.drawText(0, top, self.lineNumberArea.width(), height,
	                         QtCore.Qt.AlignRight, number)

	    block = block.next()
	    top = bottom
	    bottom = top + self.blockBoundingRect(block).height()
	    blockNumber += 1	
	    

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

class StrWidget(BaseAttrWidget):
    '''
    This widget can be used with string attributes.
    '''
    def __init__(self, node, attr, label='', parent=None):
        '''
        Initialize
        '''
        super(StrWidget, self).__init__(node, attr, label, parent)

	# create font
	font = QtGui.QFont()
	font.setFamily('Courier New')
	font.setPointSize(10)
	
	
        ########################################################################
        #Widgets
        ########################################################################
        #: The QLineEdit storing the value of the attribute
        self.valLE = CodeEditor(parent=self)
	self.valLE.setFont(font)

        ########################################################################
        #Layout
        ########################################################################
        self.layout.addWidget(self.valLE, 1)

        ########################################################################
        #Connections
        ########################################################################
        #We need to call the callUpdateAttr method whenever the user modifies the
        #value in valLE
        self.connect(self.valLE, QtCore.SIGNAL("textChanged()"), self.callUpdateAttr)

        ########################################################################
        #Set the initial node
        ########################################################################
        self.setNode(node)

    def updateGUI(self):
        '''
        Implement this virtual method to update the value in valLE based on the
        current node.attr
        '''
	if not self.valLE.hasFocus() or self.forceUpdateGUI:
	    self.valLE.setPlainText(str(cmds.getAttr("%s.%s" % (self.node, self.attr))))

    def updateAttr(self):
        '''
        Implement this virtual method to update the actual node.attr value to
        reflect what is currently in the UI.
        '''
        cmds.setAttr("%s.%s" % (self.node, self.attr), str(self.valLE.toPlainText()), type='string') 

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
	self.strAttr = StrWidget(node, 'customCode', label='', parent=self)

        ########################################################################
        #Layout
        ########################################################################
        self.layout = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.TopToBottom, self)
        self.layout.setContentsMargins(5,3,11,3)
        self.layout.setSpacing(5)
	self.layout.addWidget(self.strAttr)

    def setNode(self, node):
        '''
        Set the current node
        '''
        self.node = node
		
	self.strAttr.setNode(node)

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