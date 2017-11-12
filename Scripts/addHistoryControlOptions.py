from pymel.core import *
import maya.cmds as cmds

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

class HistoryControlWindow(object):
    def __init__(self):
        self.amount = 1
        if optionVar(exists='addHistoryControlAmount'):
            self.amount = optionVar(q='addHistoryControlAmount')
        
        self.hWin, cLayout, createButton, applyButton, closeButton = standardWindow('HistoryControlWin', 'Add History Control Options', ('Add History Control', 'Apply', 'Close'))
        
        menu(label='Edit')
        menuItem(label='Reset Settings', c='win.reset()')
        
        menu(label='Help', hm=True)
        menuItem(label='View plugin documentation')
        
        setParent(cLayout)
        
        frameLayout(label='Settings')
        columnLayout(adj=1)
        
        self.amountSlider = intSliderGrp(f=True, label='Amount', min=0, fieldMinValue=0, max=20, fieldMaxValue=1000, v=self.amount)
        
        button(createButton, e=1, c='win.createAction()')
        button(applyButton, e=1, c='win.applyAction()')
        button(closeButton, e=1, c='win.closeAction()')
        
    def reset(self):
        intSliderGrp(self.amountSlider, e=1, v=1, max=20)
        
    def createAction(self):
        self.applyAction()
        self.closeAction()
    
    def applyAction(self):
        self.updateAmount()
        optionVar(iv = ("addHistoryControlAmount", self.amount))
        cmds.addHistoryControl(a=self.amount)
        
    def closeAction(self):
        deleteUI(self.hWin)
    
    def updateAmount(self):
        self.amount = intSliderGrp(self.amountSlider, q=True, v=True)
        
if not window('HistoryControlWin', exists=1):
    global win
    win = HistoryControlWindow()

showWindow('HistoryControlWin')