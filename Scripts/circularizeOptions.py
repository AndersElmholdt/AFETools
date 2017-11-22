from pymel.core import *
import maya.cmds as cmds
import webbrowser

def standardWindow(windowName, title, buttons):
    if len(buttons) == 0:
        error('This window should have at least one button!')
    
    if windowName == '': windowName = window(w=300, h=150, title=title)
    elif window(windowName, exists=1):
        showWindow(windowName)
        return(windowName)
    else: window(windowName, w=300, h=150, title=title, menuBar=True)
    
    result = []
    result.append(windowName)
    
    form = formLayout(nd=100)
    tab = tabLayout(tv=0, scr=0, cr=1)
    result.append(columnLayout(adj=1))
    
    setParent(form)
    sep = separator(h=10)
    
    for b in buttons: result.append(button(label=b))
    
    formLayout(form, edit=1, 
                    attachForm = [(tab, 'top', 10),
                                 (tab, 'left', 5),
                                 (tab, 'right', 5),
                                 (sep, 'left', 5),
                                 (sep, 'right', 5)],
                    attachControl = [(tab, 'bottom', 5, sep),
                                    (sep, 'bottom', 5, result[2])],
                    attachNone = [(sep, 'top')])
                    
    formLayout(form, edit=1, 
                    attachForm = [(result[2], 'left', 5),
                                 (result[2], 'bottom', 5),
                                 (result[-1], 'right', 5),
                                 (result[-1], 'bottom', 5)],
                    attachNone = [(result[2], 'top'),
                                  (result[-1], 'top')])
                                  
    gapStep = 100 / len(buttons)
    for i in range(3, len(result)):
        formLayout(form, edit=1,
                attachPosition = [(result[i-1], 'right', 2, gapStep*(i-2)),
                                  (result[i], 'left', 2, gapStep*(i-2))],
                attachForm = [(result[i], 'bottom', 5)])
    
    return result

class CircularizeWindow(object):
    def __init__(self):
        self.flatten = False
        self.autoEstimateRadius = True
        self.radius = 1.0
        self.twist = 0.0
        self.strength = 1.0
        
        # Load default values
        if optionVar(exists='addCircularizeNodeFlatten'):
            self.flatten = optionVar(q='addCircularizeNodeFlatten')
        if optionVar(exists='addCircularizeNodeAuto'):
            self.autoEstimateRadius = optionVar(q='addCircularizeNodeAuto')
        if optionVar(exists='addCircularizeNodeRadius'):
            self.radius = optionVar(q='addCircularizeNodeRadius')
        if optionVar(exists='addCircularizeNodeTwist'):
            self.twist = optionVar(q='addCircularizeNodeTwist')
        if optionVar(exists='addCircularizeNodeStrength'):
            self.strength = optionVar(q='addCircularizeNodeStrength')
        
        self.hWin, cLayout, createButton, applyButton, closeButton = standardWindow('CircularizeWin', 'Circularize Options', ('Circularize', 'Apply', 'Close'))
        
        menu(label='Edit')
        menuItem(label='Reset Settings', c='win.reset()')
        
        menu(label='Help', hm=True)
        menuItem(label='View plugin documentation', c='webbrowser.open_new_tab("https://github.com/AndersElmholdt/AFETools")')
        
        setParent(cLayout)
        
        frameLayout(label='Settings')
        columnLayout(adj=1)
        
        self.flattenRadioGrp = radioButtonGrp(label='Depth control', nrb=2, labelArray2=('Flatten', 'Maintain depth'), sl=1 if self.flatten==True else 2)
        self.strengthSlider = floatSliderGrp(f=True, label='Strength', min=0, fieldMinValue=0, max=1, fieldMaxValue=1, v=self.strength)
        self.twistSlider = floatSliderGrp(f=True, label='Twist', min=-360, fieldMinValue=-360, max=360, fieldMaxValue=360, v=self.twist)
        self.radiusSlider = floatSliderGrp(f=True, label='Radius', min=-0, fieldMinValue=0, max=5, fieldMaxValue=10000, v=self.radius, en=not self.autoEstimateRadius)
        self.autoCheckbox = checkBoxGrp(label='Auto Estimate Radius', l1='', ncb=1, v1=self.autoEstimateRadius, onc='floatSliderGrp(win.radiusSlider, e=True, en=False)', ofc='floatSliderGrp(win.radiusSlider, e=True, en=True)')
        
        button(createButton, e=1, c='win.createAction()')
        button(applyButton, e=1, c='win.applyAction()')
        button(closeButton, e=1, c='win.closeAction()')
        
    def reset(self):
        floatSliderGrp(self.strengthSlider, e=1, v=1)
        floatSliderGrp(self.twistSlider, e=1, v=0)
        floatSliderGrp(self.radiusSlider, e=1, v=1, max=5, fieldMaxValue=10000, en=False)
        checkBoxGrp(self.autoCheckbox, e=1, v1=True)
        radioButtonGrp(self.flattenRadioGrp, e=1, sl=2)
        
    def createAction(self):
        self.applyAction()
        self.closeAction()
    
    def applyAction(self):
        self.updateValues()
        optionVar(iv = ('addCircularizeNodeFlatten', 0 if self.flatten == False else 1))
        optionVar(iv = ('addCircularizeNodeAuto', 0 if self.autoEstimateRadius == False else 1))
        optionVar(fv = ('addCircularizeNodeRadius', self.radius))
        optionVar(fv = ('addCircularizeNodeTwist', self.twist))
        optionVar(fv = ('addCircularizeNodeStrength', self.strength))
        if self.autoEstimateRadius == True:
            cmds.addCircularizeNode(f=self.flatten, t=self.twist, s=self.strength)
        else:
            cmds.addCircularizeNode(f=self.flatten, t=self.twist, s=self.strength, r=self.radius)
        
    def closeAction(self):
        deleteUI(self.hWin)
        
    def updateValues(self):
        self.twist = floatSliderGrp(self.twistSlider, q=True, v=True)
        self.radius = floatSliderGrp(self.radiusSlider, q=True, v=True)
        self.strength = floatSliderGrp(self.strengthSlider, q=True, v=True)
        self.autoEstimateRadius = checkBoxGrp(self.autoCheckbox, q=True, v1=True)
        self.flatten = True if radioButtonGrp(self.flattenRadioGrp, q=True, sl=True) == 1 else False
        
if not window('CircularizeWin', exists=1):
    global win
    win = CircularizeWindow()

showWindow('CircularizeWin')