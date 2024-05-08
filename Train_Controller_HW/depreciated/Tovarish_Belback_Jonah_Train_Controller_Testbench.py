import os
import sys
import functools
import time
import threading
import numpy

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *


'''app = QApplication([])
window = QWidget()
layout = QVBoxLayout()
layout.addWidget(QPushButton('Top'))
layout.addWidget(QPushButton('Bottom'))
window.setLayout(layout)
window.show()
app.exec()'''


'''
#TrainModel_arr
ticks
0: act spd
1: com spd
2: vit auth
3: spd lim
4: acc lim
buttons
5 : pass ebrake
6 : Track Circuit State
7 : Station side(0to3)
8 : sig fail
9 : eng fail
10: brake fail
11: beacon (128chars)
'''
global glob_TB
glob_TB = None

class TestBench_JEB382(QWidget):
    def __init__(self,numtrain,in_TrainModel_arr,ToggleBtn=None):#,verbose=False):
        super(TestBench_JEB382, self).__init__()
        self.setWindowTitle('TrainControllerHW TB #'+str(numtrain))
        self.setFixedSize(874, 316)
        
        ICON = QIcon(os.getcwd()+"\icon.png")
        self.setWindowIcon(ICON)
        
        #this array inputed as an init gets updated as UI is used
        #classes that created this TB have the array they passed locally update with it as well
        if len(in_TrainModel_arr)<12:
            #if array is empty or missing values, autofills at end of missing indexes
            t_TrainModel_arr = [0.0, 0.0, 0.0, 0.0, 0.0, False, False, 0, False, False,False,"00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"]
            in_TrainModel_arr = in_TrainModel_arr + t_TrainModel_arr[len(in_TrainModel_arr):]
        #if over, snips
        elif len(in_TrainModel_arr)>12: in_TrainModel_arr = in_TrainModel_arr[0:-(len(in_TrainModel_arr)-12)]
        #ensure beacon arr indx is proper size
        if len(str(in_TrainModel_arr[-1]))<128:
            in_TrainModel_arr[-1] = "0"*(128-len(str(in_TrainModel_arr[-1])))+str(in_TrainModel_arr[-1])
        elif len(str(in_TrainModel_arr[-1]))>128:
            in_TrainModel_arr[-1] = str(in_TrainModel_arr[-1])[len(str(in_TrainModel_arr[-1]))-128:]
        #checks door side state is within range
        if in_TrainModel_arr[7] not in range(0,5):
            in_TrainModel_arr[7]=0
        self.statside=in_TrainModel_arr[7]
        #check tickboxes are within limit(0,100)
        limit1=0;limit2=100
        for i in range(0,4):
            if   in_TrainModel_arr[i] < limit1: in_TrainModel_arr[i]=limit1
            elif in_TrainModel_arr[i] > limit2: in_TrainModel_arr[i]=limit2
        
        self.TrainModel_arr = in_TrainModel_arr
        #print(TrainModel_arr)
        
        #SW UI passthrough
        self.ToggleBtn = ToggleBtn
                
        #self.resize(800, 600)
        self.layout = QGridLayout(self)

        #self.tabs = tabWidget(self)
        #self.setCentralWidget(self.tabs)
        self.ttlabel = QLabel("Inputs from Train Model #"+str(numtrain))
        #self.ttlabel.setFrameStyle(QFrame.Panel)
        self.ttlabel.setStyleSheet("font-size: 18pt; border: 0px")
        self.ttlabel.setMaximumHeight(40)
        
        self.layout.addWidget(self.ttlabel, 0, 0, 1, 4)
        
        self.genTCKs()
        self.genbuttons()
        self.gentxtbox()
        self.Thread1_active = True
        
        #pyfrimata edition
        #while True: self.update_TestBench_JEB382()
    
    #--------
    def genTCKs(self):
        
        self.ticks = []
        tickNames1 = ["Actual Speed:","Commanded Speed","Vital Authority","Speed Limit","Accel/Decel Limit"]
        tickNames2 = ["MPH"          ,"MPH"            ,"Miles"          ,"MPH"        ,"MPH/s"]
        
        # generates tickboxes and names with names from array
        for i in range(1,len(tickNames1)+1):
            label1 = better_label_ret(tickNames1[i-1])
            self.layout.addWidget(label1, i, 0, 1, 1)
            
            tickbox = QDoubleSpinBox()
            tickbox.setValue(self.TrainModel_arr[i-1])
            self.layout.addWidget(tickbox, i, 1, 1, 1)
            self.ticks.append(tickbox)
            
            label2 = QLabel(tickNames2[i-1])
            #label2.setFrameStyle(QFrame.Panel)
            label2.setStyleSheet("border: 0px")
            label2.setMaximumHeight(40)
            self.layout.addWidget(label2, i, 2, 1, 1)
    def update_TestBench_JEB382(self):
        try:
            #tickers
            for i in range(len(self.ticks)):
                self.TrainModel_arr[i] = self.ticks[i].value()
            #beacon
            for i in range(len(self.ticks),len(self.buttons)+len(self.ticks)):
                self.TrainModel_arr[i] = self.buttons[i-len(self.ticks)].isChecked()
            self.TrainModel_arr[-1] = self.textbox.text()
            
            #exception
            self.TrainModel_arr[7] = self.statside
        except:
            print("TB done; min err")
            self.Thread1_active = False
            
            
    #--------
    def genbuttons(self):
        self.buttons = []
        buttonNames1 = ["Passenger eBrake","Track Circuit State","Station Side","Signal Pickup Failure","Engine Failure","Brake Failure"]
                
        # generates buttons with names from btnNames array
        for i in range(1,len(buttonNames1)+1):
            label1 = better_label_ret(text=buttonNames1[i-1])
            self.layout.addWidget(label1, i, 4, 1, 1)
            
            button = better_button_ret()
            button.setChecked(bool(self.TrainModel_arr[i+4]))
            gen_but_tog(button)
            button.clicked.connect( functools.partial(gen_but_tog,but=button) )
            if i not in [2,3]: self.layout.addWidget(button, i, 5, 1, 1)
            self.buttons.append(button)
        
        #adjust 1,2 ; Track Circuit State,Station Side
        button = better_button_ret()
        button.clicked.connect( functools.partial(gen_but_tog,but=button,text1="Left",text2="Right",
                                                  style_on="background-color: rgb(0, 224, 34); border: 2px solid rgb(30, 143, 47); border-radius: 4px",
                                                  style_off="background-color: rgb(222, 62, 38); border: 2px solid rgb(222, 0, 0); border-radius: 4px") )
        button.setChecked(bool(self.TrainModel_arr[6]))
        gen_but_tog(but=button,text1="Left",text2="Right",
                    style_on="background-color: rgb(0, 224, 34); border: 2px solid rgb(30, 143, 47); border-radius: 4px",
                    style_off="background-color: rgb(222, 62, 38); border: 2px solid rgb(222, 0, 0); border-radius: 4px") 
        self.layout.addWidget(button, 2, 5, 1, 1)
        self.buttons[1] = button
        
        button = better_button_ret()
        self.BTNF_station(button,start=True)#change layout
        button.clicked.connect( functools.partial(self.BTNF_station,but=button))
        self.layout.addWidget(button, 3, 5, 1, 1)
        self.buttons[2] = button
        
    def BTNF_station(self,but,start=False):
        if   self.statside-start == 0: #0to1 Left
            but.setText("Left")
            but.setStyleSheet("background-color: rgb(255, 175, 255); border: 2px solid rgb(255, 150, 255); border-radius: 6px")
            if not start: self.statside = 1
            
        elif self.statside-start == 1: #1to2 Right
            but.setText("Right")
            but.setStyleSheet("background-color: rgb(255, 150, 255); border: 2px solid rgb(255, 115, 255); border-radius: 6px")
            if not start: self.statside = 2
            
        elif self.statside-start == 2: #2to3 Both
            but.setText("Both")
            but.setStyleSheet("background-color: rgb(255, 115, 255); border: 2px solid rgb(189,  72, 181); border-radius: 6px")
            if not start: self.statside = 3
            
        else:# self.statside-start == 3: #3to0 Neither
            but.setText("Neither")
            but.setStyleSheet("background-color: rgb(255, 207, 255); border: 2px solid rgb(255, 175, 255); border-radius: 6px")
            if not start: self.statside = 0
        #else: print("TestBench_JEB382 BTNF_station error")
        
     
    #code when window closes
    def closeEvent(self, *args, **kwargs):
        super(TestBench_JEB382, self).closeEvent(*args, **kwargs)
        if __name__ == "__main__": self.Thread1_active = False
        else:
            print("JEB382 TB Hidden")
            if self.ToggleBtn:
                self.ToggleBtn.setText("Toggle TestBench[off]")
                self.ToggleBtn.setStyleSheet("background-color: rgb(156, 156, 156); border: 2px solid rgb(100, 100, 100); border-radius: 6px")
            
    
    #--------
    def gentxtbox(self):
        txtlab = better_label_ret("Beacon (128chars): 0x")
        self.layout.addWidget(txtlab, 12, 0, 1, 4)
        self.textbox = QLineEdit()
        self.textbox.setFixedWidth(852)
        self.textbox.setText(self.TrainModel_arr[-1])
        self.layout.addWidget(self.textbox, 13, 0, 1, 8)
            
 #--------#--------#--------#--------#--------
def better_button_ret(sizeW=True,sizeH=24,checkable=True,text="Off",style="background-color: rgb(156, 156, 156); border: 2px solid rgb(100, 100, 100); border-radius: 6px"):
        button = QPushButton()
        if sizeW: button.setFixedWidth(120)
        button.setFixedHeight(sizeH)
        button.setCheckable(checkable)
        button.setStyleSheet(style)
        button.setText(text)
        
        return button

def better_label_ret(text,size=10,bold=False):
    label = QLabel(text)
    #label.setFixedWidth(120)
    label.setStyleSheet(f"font-size: {size}pt; border: 0px; {'font-weight: bold;' if bold else ''}")
    return label

def gen_but_tog(but, text1=None,text2=None, style_on=None,style_off=None):
    if but.isChecked():
        but.setStyleSheet(f"{style_on  if style_on  else 'background-color: rgb(143, 186, 255); border: 2px solid rgb( 42,  97, 184); border-radius: 6px'}")
        if text1: but.setText(text2)
        else: but.setText("On")
    else:
        but.setStyleSheet(f"{style_off if style_off else 'background-color: rgb(156, 156, 156); border: 2px solid rgb(100, 100, 100); border-radius: 6px'}")
        if text1: but.setText(text1)
        else: but.setText("Off")


#=============================

def TB_mainloop_fast(numtrain,arr):
    while True:
        if glob_TB:
            glob_TB.update_TestBench_JEB382()
            #arr = glob_TB.TrainModel_arr
            print(f"TB TrainC #{numtrain}",glob_TB.TrainModel_arr)
            if not glob_TB.Thread1_active: break
        
        
def TB_pyqtloop(numtrain,arr):
    app = QApplication(sys.argv)
    glob_TB = TestBench_JEB382(numtrain, arr)
    glob_TB.show()
    sys.exit(app.exec())
    
def TB_fin(numtrain,arr):
    t1 = threading.Thread(target=TB_pyqtloop, args=(numtrain,arr))
    t2 = threading.Thread(target=TB_mainloop_fast, args=(numtrain,arr))
 
    t1.start()
    t2.start()
 
    t1.join()
    t2.join()
    
def test_TB():
    app = QApplication(sys.argv)
    #---------------------------
    
    arr =[9]*12
    w1 = TestBench_JEB382(1, arr)
    w1.show()
    w1.update_TestBench_JEB382()
    print(f"TB TrainC #{1}",w1.TrainModel_arr)
    
    arr =[8.0, 9.0, 10.0, 11.0, 12.0, True, False, 1, True, False, True,"hiyaaaaa"]
    w2 = TestBench_JEB382(2, arr)
    w2.show()
    w2.update_TestBench_JEB382()
    print(f"TB TrainC #{2}",w2.TrainModel_arr)
    
    arr =[1.0, 2.0, 3.0, 4.0, 5.0, True, False, 2, True, False, True,"byyeeee"]
    w3 = TestBench_JEB382(3, arr)
    w3.show()
    w3.update_TestBench_JEB382()
    print(f"TB TrainC #{3}",w3.TrainModel_arr)
    
    arr =[2.0, 2.0, 3.0, 4.0, 5.0, True, True, 3, True, True, True,"00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"]
    w4 = TestBench_JEB382(4, arr)
    w4.show()
    w4.update_TestBench_JEB382()
    print(f"TB TrainC #{4}",w4.TrainModel_arr)
    
    arr =[3.0, 2.0, 3.0, 4.0, 5.0, False, False, 0, False, False, False,"overflow00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"]
    w5 = TestBench_JEB382(5, arr)
    w5.show()
    w5.update_TestBench_JEB382()
    print(f"TB TrainC #{5}",w5.TrainModel_arr)
    
    arr =[4.0, 2.0, 3.0, 4.0, 5.0, False, False, 0, False, False, False,"overflow000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000overflow"]
    w6 = TestBench_JEB382(6, arr)
    w6.show()
    w6.update_TestBench_JEB382()
    print(f"TB TrainC #{6}",w6.TrainModel_arr)
    
    #---------------------------
    sys.exit(app.exec())
    
        
if __name__ == "__main__":
    numtrain=1
    arr =[9]*30
    TB_fin(numtrain,arr)
    
    
    #test_TB()