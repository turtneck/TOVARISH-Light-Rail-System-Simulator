from Tovarish_Belback_Jonah_Train_Controller_Testbench import TestBench_JEB382
from Tovarish_Belback_Jonah_Train_Controller_HW_UI_PyFirmata import HW_UI_JEB382_PyFirmat

import os
import sys
import functools

import PyQt6.QtGui as QtGui
import threading

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

import serial
import pyfirmata2

#TODO
#make so commanded speed in Driver_arr is overwritten by TrainModels cmd spd if in auto
#default labels,btns,tcks to inputted array
#add new I/Os


'''
self.Driver_arr[0] = self.TCK_Kp.value()
self.Driver_arr[1] = self.TCK_Ki.value()
self.Driver_arr[2] = self.TCK_CmdSpd.value()
self.Driver_arr[3] = self.BTN_CabnLgt.isChecked()
self.Driver_arr[4] = self.BTN_HeadLgt.isChecked()
self.Driver_arr[5] = self.TCK_Temp.value()
self.Driver_arr[6] = self.BTN_Door_L.isChecked()
self.Driver_arr[7] = self.BTN_Door_R.isChecked()
self.Driver_arr[8] = self.BTN_EBRK.isChecked()
self.Driver_arr[9] = self.BTN_SBRK.isChecked()
self.Driver_arr[10] = disabled passenger brake

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




global Arduino, board, serial_b
serial_b=False
verbose = True
w = None

#background
stylesheet = """
    SW_UI_JEB382 {
        border-image: url(JEB382_bg2);
        background-repeat: no-repeat; 
        background-position: center;
    }
"""




class SW_UI_JEB382(QMainWindow):
    def __init__(self,numtrain,in_Driver_arr,in_TrainModel_arr,in_output_arr,app=None):
        super(SW_UI_JEB382, self).__init__()
        self.setWindowTitle('TrainControllerHW SW_UI #'+str(numtrain))
        self.setFixedSize(670, 446)
        
        self.numtrain = numtrain
        
        in_output_arr = [1.0,1.0, False,False, False,False, False,False, 0.0, ""]
        self.output_arr = in_output_arr
        
        #-------adjust arrays-------
        #array inputed as an init gets updated as UI is used
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
        if in_TrainModel_arr[7] not in range(0,5): in_TrainModel_arr[7]=0
        #check tickboxes are within limit(0,100)
        limit1=0;limit2=100
        for i in range(0,4):
            if   in_TrainModel_arr[i] < limit1: in_TrainModel_arr[i]=limit1
            elif in_TrainModel_arr[i] > limit2: in_TrainModel_arr[i]=limit2
        
        print(in_TrainModel_arr); print(len(in_TrainModel_arr))#debug
        self.TrainModel_arr = in_TrainModel_arr
        
        #Driver_arr, is output, the inputted arr is just used for the variable reference
        in_Driver_arr = [1.0, 1.0, 0.0, False, False, 0.0, False, False, False, False, False]
        
        print(in_Driver_arr); print(len(in_Driver_arr))#debug
        self.SW_Driver_arr = in_Driver_arr[:]#make copy, detach from other ware
        self.HW_Driver_arr = in_Driver_arr[:]#make copy, detach from other ware
        in_Driver_arr = self.SW_Driver_arr  #the initial state is HW, reference preserved
        self.Driver_arr = in_Driver_arr #class arr is reference to input
        self.Ware = 0
            
        
        
        
        #-------Setup window-------
        
        ICON = QIcon(os.getcwd()+"\icon.png")
        self.setWindowIcon(ICON)
        
        self.WidgetSpace = QWidget()
        self.setCentralWidget(self.WidgetSpace)

        self.layout = QGridLayout(self.WidgetSpace)
        
        #---generation of sections of window
        self.genSect0(0,0) #TestBench; Mode Select
        self.genSect1_1(1,0) #TrainEnviroment
        self.genSect1_2(1,4) #Station Info
        self.genSect1_3(1,8) #FailStates
        self.genSect2_1(7,0) #EngControl
        self.genSect2_2(7,4) #DriverControl
        self.layout.addWidget(QLabel(""), 5, 0,  1, 8)#spacer; Horz 1_x/2_x
        self.layout.addWidget(QLabel(""), 1, 3, 13, 1)#spacer; Vert x_1/x_2
        self.layout.addWidget(QLabel(""), 1, 8,  6, 1)#spacer; Vert x_2/x_3
        #self.layout.addWidget(QLabel(""), 14, 0, 1, 9)#spacer; bottom
        if app: app.setStyleSheet(stylesheet)#set background
        
        #update command helpers
        self.init_comp=True
        self.aux1=self.Driver_arr[:]#copy not reference
        self.aux2=self.TrainModel_arr[:]
        self.update_SW_UI_JEB382(True)
        if self.Driver_arr[-1] == "" or self.Driver_arr[-1] == 0.0: self.LED_Announce.setText("N/A")
        
        self.prevBTNstate=[0,0,0,0]#used for mode button function
        
        if Arduino: self.HW_UI_JEB382 = HW_UI_JEB382_PyFirmat(self.HW_Driver_arr,self.TrainModel_arr)


    
    #--------
    #code when window closes
    def closeEvent(self, *args, **kwargs):
        super(SW_UI_JEB382, self).closeEvent(*args, **kwargs)
        self.TB_window.hide()
        self.TB_window.Thread1_active = False
        print("closed UI")
            
    def update_SW_UI_JEB382(self,skip=False):
        if not(self.init_comp and self.isVisible() ): return
        try:
            #----get values of all the TCKs and BTNs; put in Driver_arr
            if self.BTN_Mode.isChecked():   #update the array if its manual mode
                self.SW_Driver_arr[0] = self.TCK_Kp.value()    #2_1
                self.SW_Driver_arr[1] = self.TCK_Ki.value()
                self.SW_Driver_arr[2] = self.TCK_CmdSpd.value()
                self.SW_Driver_arr[3] = self.BTN_CabnLgt.isChecked()
                self.SW_Driver_arr[4] = self.BTN_HeadLgt.isChecked()
                self.SW_Driver_arr[5] = self.TCK_Temp.value()
                self.SW_Driver_arr[6] = self.BTN_Door_L.isChecked()
                self.SW_Driver_arr[7] = self.BTN_Door_R.isChecked()
                self.SW_Driver_arr[8] = self.BTN_EBRK.isChecked()
                self.SW_Driver_arr[9] = self.BTN_SBRK.isChecked()
                self.SW_Driver_arr[10]= self.BTN_DisPaEB.isChecked()
                
            if Arduino and self.Ware:
                #self.HW_UI_JEB382.updateOuts()
                #self.HW_UI_JEB382.updateDisplay()
                self.HW_Driver_arr = self.HW_UI_JEB382.Driver_arr
            
            
            #----get values from Test Bench
            if self.TB_window.isVisible():
                self.TB_window.update_TestBench_JEB382()
                
            #correct beacon errors
            if len(str(self.TrainModel_arr[-1]))<128:
                self.TrainModel_arr[-1] = "0"*(128-len(str(self.TrainModel_arr[-1])))+str(self.TrainModel_arr[-1])
            elif len(str(self.TrainModel_arr[-1]))>128:
                self.TrainModel_arr[-1] = str(self.TrainModel_arr[-1])[len(str(self.TrainModel_arr[-1]))-128:]
            
            #detect changes before changing LED
            #change LED values-----------------------------
            if self.aux1[ 3] != self.Driver_arr[ 3] or skip: LED_tog(self.LED_CabnLgt,       self.Driver_arr[ 3])
            if self.aux1[ 4] != self.Driver_arr[ 4] or skip: LED_tog(self.LED_HeadLgt,       self.Driver_arr[ 4])
            self.LED_Temp    .setText(str(  self.Driver_arr[ 5]))
            #unsure what beacon is right now but rn assume first 20 is station name
            self.LED_Announce.setText( str(self.TrainModel_arr[-1])[0:20].replace("0", "") + " Station")
            if self.aux1[ 6] != self.Driver_arr[ 6] or skip: LED_tog(self.LED_Door_L,        self.Driver_arr[ 6],"Left","Left")
            if self.aux1[ 7] != self.Driver_arr[ 7] or skip: LED_tog(self.LED_Door_R,        self.Driver_arr[ 7],"Right","Right")
            if (self.aux2[5] != self.TrainModel_arr[ 5] and not self.BTN_DisPaEB.isChecked()) or skip: LED_tog(self.LED_Pass_EB,  self.TrainModel_arr[5])
            if self.aux2[ 6] != self.TrainModel_arr[ 6] or skip: LED_tog(self.LED_Track_Circ,  self.TrainModel_arr[6],"Right","Left")
            if self.aux2[ 7] != self.TrainModel_arr[ 7] or skip: self.LEDT_station(self.LED_Stat_Side)
            if self.aux2[-4] != self.TrainModel_arr[-4] or skip: LED_tog(self.LED_Sig_Fail,  self.TrainModel_arr[-4])
            if self.aux2[-3] != self.TrainModel_arr[-3] or skip: LED_tog(self.LED_Eng_Fail,  self.TrainModel_arr[-3])
            if self.aux2[-2] != self.TrainModel_arr[-2] or skip: LED_tog(self.LED_Brk_Fail,  self.TrainModel_arr[-2])
            self.LED_CurSpd  .setText(str(  self.aux2[0]))
            '''if (self.aux2[-1] != self.TrainModel_arr[-1] and self.aux2[-1] != "" and self.aux2[-1] != 0.0) or skip:
                print("HEEEERRREEE1:",self.TrainModel_arr[-1])
                print("HEEEERRREEE2:",str(self.TrainModel_arr[-1]))
                print("HEEEERRREEE3:",str(self.TrainModel_arr[-1])[0:-3])
                self.LED_Announce.setText( str(self.TrainModel_arr[-1])[0:-3] )#station name is all chars expect last 3'''
            
            self.aux1=self.Driver_arr[:]
            self.aux2=self.TrainModel_arr[:]
            
            #print("DRV",self.Driver_arr)
            #print("TRM",self.TrainModel_arr)
            #print("OUT",self.output_arr)
            
            
            self.output_arr[2] = self.Driver_arr[9]
            self.output_arr[3] = self.Driver_arr[8] or (self.TrainModel_arr[5] and not self.Driver_arr[10])
            self.output_arr[4] = self.Driver_arr[3] #or \/\/\/\/ or if beacon give info that its underground (undetermined)
            self.output_arr[5] = self.Driver_arr[4] #or ^^^^ or if its night outside, in overall integration time var
            self.output_arr[6] = (self.Driver_arr[6] and self.BTN_Mode.isChecked()) or self.TrainModel_arr[7]%2==1 #at station or overwriten
            self.output_arr[7] = (self.Driver_arr[7] and self.BTN_Mode.isChecked()) or self.TrainModel_arr[7]>1 #at station or overwriten
            self.output_arr[8] = self.Driver_arr[5]
            self.output_arr[9] = str(self.TrainModel_arr[-1])[0:20].replace("0", "") + " Station"
            
            
            if self.output_arr[3] or self.TrainModel_arr[-3] or self.TrainModel_arr[-2]:
                self.output_arr[0] = 0
                self.output_arr[1] = 0
                return
            
            commandspd=0
            if self.BTN_Mode.isChecked(): commandspd = self.Driver_arr[2]
            else: commandspd = self.TrainModel_arr[1]
            
            #if commandspd >self.TrainModel_arr[3] or self.TrainModel_arr[0]> self.TrainModel_arr[3]: commandspd=self.TrainModel_arr[3]
            #if self.output_arr[0] != 0: if commandspd/self.self.output_arr[0] > self.TrainModel_arr[4]: commandspd = (commandspd*self.TrainModel_arr[4]) #correct with acceleration limit
            if commandspd >self.TrainModel_arr[3] or self.TrainModel_arr[0]> self.TrainModel_arr[3]:
                self.output_arr[0]=self.TrainModel_arr[3]
                self.output_arr[1] = 0
            else:
                self.output_arr[0] = commandspd
                self.output_arr[1] = self.Driver_arr[0]+(self.Driver_arr[1]/(commandspd-self.TrainModel_arr[0])) #pwr= Kp+(Ki/s)
            #print("CCCCC")
            #if main_ouput: print(f"OUT TrainC #{numtrain}",self.output_arr)
            
            #if not self.TB_window.isVisible(): print(f"TrainC #{1}",self.Driver_arr)
            if self.TrainModel_arr[2] == 0:
                self.output_arr[0] = 0
                self.output_arr[1] = 0
                self.output_arr[3] = True
                
        except Exception as e:
            #print("update:",e)
            return
                    


    #--------
    def genSect0(self,OriginY,OriginX):
        self.BTN_TB = better_button_ret(text="Toggle TestBench[off]",checkable=True)
        self.BTN_TB.clicked.connect(self.toggle_TB)
        self.layout.addWidget(self.BTN_TB,0,0,1,3)
        
        self.TB_window = TestBench_JEB382(self.numtrain,self.TrainModel_arr,self.BTN_TB)
        
        self.BTN_Mode = better_button_ret(text="Auto",checkable=True)
        self.BTN_Mode.clicked.connect(self.BTNF_Mode)
        self.layout.addWidget(self.BTN_Mode, OriginY, OriginX+4, 1, 3)#7)
        
        self.BTN_HW = better_button_ret(text="Engage HW",checkable=True)
        self.BTN_HW.clicked.connect(self.BTNF_HW)
        self.layout.addWidget(self.BTN_HW, OriginY, OriginX+8, 1, 3)
    
    def toggle_TB(self):
        if self.TB_window.isVisible():
            self.TB_window.hide()
            self.BTN_TB.setText("Toggle TestBench[off]")
            self.BTN_TB.setStyleSheet("background-color: rgb(156, 156, 156); border: 2px solid rgb(100, 100, 100); border-radius: 6px")
            print("JEB382 TB Hidden")
        else:
            self.BTN_TB.setText("Toggle TestBench[on]")
            self.BTN_TB.setStyleSheet("background-color: rgb(143, 186, 255); border: 2px solid rgb(42, 97, 184); border-radius: 6px")
            self.update_SW_UI_JEB382(True)
            self.TB_window.show()
    
    def BTNF_Mode(self):
        gen_but_tog(self.BTN_Mode,"Auto","Manual")
        if self.BTN_Mode.isChecked():#manual
            self.TCK_Kp.setDisabled(False)
            self.TCK_Ki.setDisabled(False)
            self.TCK_CmdSpd.setDisabled(False)
            self.TCK_Temp.setDisabled(False)
            
            self.BTN_CabnLgt.setCheckable(True)
            self.BTN_CabnLgt.setChecked(self.prevBTNstate[0])
            gen_but_tog(self.BTN_CabnLgt)
            LED_tog(self.LED_CabnLgt, self.BTN_CabnLgt.isChecked())
            
            self.BTN_HeadLgt.setCheckable(True)
            self.BTN_HeadLgt.setChecked(self.prevBTNstate[1])
            gen_but_tog(self.BTN_HeadLgt)
            LED_tog(self.LED_HeadLgt, self.BTN_HeadLgt.isChecked())
            
            self.BTN_Door_L.setCheckable(True)
            self.BTN_Door_L.setChecked(self.prevBTNstate[2])
            gen_but_tog(self.BTN_Door_L,"Left","Left")
            LED_tog(self.LED_Door_L, self.BTN_Door_L.isChecked(),"Left","Left")
            
            self.BTN_Door_R.setCheckable(True)
            self.BTN_Door_R.setChecked(self.prevBTNstate[3])
            gen_but_tog(self.BTN_Door_R,"Right","Right")
            LED_tog(self.LED_Door_R, self.BTN_Door_R.isChecked(),"Right","Right")
        else:#auto
            self.TCK_Kp.setDisabled(True)
            self.TCK_Ki.setDisabled(True)
            self.TCK_CmdSpd.setDisabled(True)
            self.TCK_Temp.setDisabled(True)
            self.prevBTNstate[0] = self.BTN_CabnLgt.isChecked()
            self.BTN_CabnLgt.setText("DISABLED")
            self.BTN_CabnLgt.setStyleSheet("background-color: rgb(156, 156, 156); border: 2px solid rgb(100, 100, 100); border-radius: 6px")
            self.BTN_CabnLgt.setCheckable(False)
            LED_tog(self.LED_CabnLgt, False)
            
            self.prevBTNstate[1] = self.BTN_HeadLgt.isChecked()
            self.BTN_HeadLgt.setText("DISABLED")
            self.BTN_HeadLgt.setStyleSheet("background-color: rgb(156, 156, 156); border: 2px solid rgb(100, 100, 100); border-radius: 6px")
            self.BTN_HeadLgt.setCheckable(False)
            LED_tog(self.LED_HeadLgt, False)
            
            self.prevBTNstate[2] = self.BTN_Door_L.isChecked()
            self.BTN_Door_L.setText("DISABLED")
            self.BTN_Door_L.setStyleSheet("background-color: rgb(156, 156, 156); border: 2px solid rgb(100, 100, 100); border-radius: 6px")
            self.BTN_Door_L.setCheckable(False)
            LED_tog(self.LED_Door_L, False,"Left","Left")
            
            self.prevBTNstate[3] = self.BTN_Door_R.isChecked()
            self.BTN_Door_R.setText("DISABLED")
            self.BTN_Door_R.setStyleSheet("background-color: rgb(156, 156, 156); border: 2px solid rgb(100, 100, 100); border-radius: 6px")
            self.BTN_Door_R.setCheckable(False)
            LED_tog(self.LED_Door_R, False,"Right","Right")
    
    def BTNF_HW(self):
        gen_but_tog(self.BTN_HW,"Engage HW","Engage HW")
        if self.BTN_HW.isChecked():
            self.Driver_arr = self.HW_UI_JEB382.Driver_arr#self.HW_UI_JEB382.Driver_arr
            self.Ware = 1
        else:
            self.Driver_arr = self.SW_Driver_arr
            self.Ware = 0
        


    #--------
    def genSect1_1(self,OriginY,OriginX):
        #5R;3C
        
        #generate labels
        label = better_label_ret("Train Enviroment",16)
        self.layout.addWidget(label, OriginY, OriginX, 1, 3)
        
        self.layout.setColumnMinimumWidth(OriginX,80)
        
        label_names = ["Cabin Lights","Headlights","Cabin Temp"]
        for i in range(1,len(label_names)+1):
            label = better_label_ret(label_names[i-1])
            self.layout.addWidget(label, OriginY+i, OriginX, 1, 1)
        
        #individually make rest of section
        #LEDs
        self.LED_CabnLgt = better_LED_ret()
        self.layout.addWidget(self.LED_CabnLgt, OriginY+1, OriginX+1, 1, 1)
        self.LED_HeadLgt = better_LED_ret()
        self.layout.addWidget(self.LED_HeadLgt, OriginY+2, OriginX+1, 1, 1)
        
        self.LED_Temp = better_LED_ret("0.00","background-color: white; border: 1px solid black")
        self.LED_Temp.setText(str(self.Driver_arr[5]))
        self.layout.addWidget(self.LED_Temp, OriginY+3, OriginX+1, 1, 1)
        label = better_label_ret("°F")
        self.layout.addWidget(label, OriginY+3, OriginX+2, 1, 3)
        
        self.layout.addWidget(better_label_ret("Door States"), OriginY+4, OriginX, 1, 2)
        self.LED_Door_L = better_LED_ret("Left")
        self.layout.addWidget(self.LED_Door_L, OriginY+4, OriginX+1, 1, 1)
        self.LED_Door_R = better_LED_ret("Right")
        self.layout.addWidget(self.LED_Door_R, OriginY+4, OriginX+2, 1, 1)
    
    
    #--------
    def genSect1_2(self,OriginY,OriginX):
        #3R;3C
        
        #generate labels
        label = better_label_ret("Station Information",16)
        self.layout.addWidget(label, OriginY, OriginX, 1, 3)
        
        self.layout.setColumnMinimumWidth(OriginX,120)
        
        #individually make rest of section
        #self.layout.addWidget(better_label_ret("Announcement"), OriginY+1, OriginX, 1, 2)
        self.LED_Announce = better_LED_ret("N/A","background-color: white; border: 1px solid black")
        self.LED_Announce.setFixedWidth(252)
        self.layout.addWidget(self.LED_Announce, OriginY+1, OriginX, 1, 3)
        
        self.layout.addWidget(better_label_ret("Passenger eBrake"), OriginY+2, OriginX, 1, 2)
        self.LED_Pass_EB = better_LED_ret()
        LED_tog(self.LED_Pass_EB, self.TrainModel_arr[5])
        self.LED_Pass_EB.setFixedWidth(126)
        self.layout.addWidget(self.LED_Pass_EB, OriginY+2, OriginX+1, 1, 2)
        
        self.layout.addWidget(better_label_ret("Track Circuit"), OriginY+3, OriginX, 1, 2)
        self.LED_Track_Circ = better_LED_ret("Left")
        LED_tog(self.LED_Track_Circ, self.TrainModel_arr[6],"Right","Left")
        self.LED_Track_Circ.setFixedWidth(126)
        self.layout.addWidget(self.LED_Track_Circ, OriginY+3, OriginX+1, 1, 2)
        
        self.layout.addWidget(better_label_ret("Station Side"), OriginY+4, OriginX, 1, 2)
        self.LED_Stat_Side = better_LED_ret()
        self.LEDT_station(self.LED_Stat_Side)
        self.LED_Stat_Side.setFixedWidth(126)
        self.layout.addWidget(self.LED_Stat_Side, OriginY+4, OriginX+1, 1, 2)
    
    def LEDT_station(self,but,start=False):#special toggle func for station state
        if   self.TrainModel_arr[7] == 1: #0to1 Left
            but.setText("Left")
            but.setStyleSheet("background-color: rgb(255, 175, 255); border: 2px solid rgb(255, 150, 255); border-radius: 6px")
            
        elif self.TrainModel_arr[7] == 2: #1to2 Right
            but.setText("Right")
            but.setStyleSheet("background-color: rgb(255, 150, 255); border: 2px solid rgb(255, 115, 255); border-radius: 6px")
            
        elif self.TrainModel_arr[7] == 3: #2to3 Both
            but.setText("Both")
            but.setStyleSheet("background-color: rgb(255, 115, 255); border: 2px solid rgb(189,  72, 181); border-radius: 6px")
            
        else:# self.statside-start == 3: #3to0 Neither
            but.setText("Neither")
            but.setStyleSheet("background-color: rgb(255, 207, 255); border: 2px solid rgb(255, 175, 255); border-radius: 6px")
    
    #--------
    def genSect1_3(self,OriginY,OriginX):
        #4R;2C
        
        #generate labels
        label = better_label_ret("Fail States",16)
        self.layout.addWidget(label, OriginY, OriginX, 1, 3)
        
        label_names = ["Signal Failure","Engine Failure","Brake Failure"]
        for i in range(1,len(label_names)+1):
            label = better_label_ret(label_names[i-1])
            self.layout.addWidget(label, OriginY+i, OriginX, 1, 1)
        
        #individually make rest of section
        #LEDs
        self.LED_Sig_Fail = better_LED_ret()
        LED_tog(self.LED_Sig_Fail, self.TrainModel_arr[8])
        self.layout.addWidget(self.LED_Sig_Fail, OriginY+1, OriginX+1, 1, 1)
        self.LED_Eng_Fail = better_LED_ret()
        LED_tog(self.LED_Eng_Fail, self.TrainModel_arr[9])
        self.layout.addWidget(self.LED_Eng_Fail, OriginY+2, OriginX+1, 1, 1)
        self.LED_Brk_Fail = better_LED_ret()
        LED_tog(self.LED_Brk_Fail, self.TrainModel_arr[10])
        self.layout.addWidget(self.LED_Brk_Fail, OriginY+3, OriginX+1, 1, 1)
    
    
    #--------
    def genSect2_1(self,OriginY,OriginX):
        #3R;2C
        
        #generate labels
        label = better_label_ret("Engineer Control",16)
        self.layout.addWidget(label, OriginY, OriginX, 1, 3)
        
        label_names = ["Kp Gain","Ki Gain"]
        for i in range(1,len(label_names)+1):
            label = better_label_ret(label_names[i-1])
            self.layout.addWidget(label, OriginY+i, OriginX, 1, 1)
        
        #individually make rest of section
        self.TCK_Kp = QDoubleSpinBox()
        self.TCK_Kp.setValue(self.Driver_arr[0])
        self.TCK_Kp.valueChanged.connect(self.TCKF_Kp)
        self.TCK_Kp.setDisabled(True)
        self.layout.addWidget(self.TCK_Kp, OriginY+1, OriginX+1, 1, 1)
        self.TCK_Ki = QDoubleSpinBox()
        self.TCK_Ki.setValue(self.Driver_arr[1])
        self.TCK_Ki.valueChanged.connect(self.TCKF_Ki)
        self.TCK_Ki.setDisabled(True)
        self.layout.addWidget(self.TCK_Ki, OriginY+2, OriginX+1, 1, 1)
        
    def TCKF_Kp(self):
        self.SW_Driver_arr[0] = self.TCK_Kp.value()
    def TCKF_Ki(self):
        self.SW_Driver_arr[1] = self.TCK_Ki.value()
    
    
    #--------
    def genSect2_2(self,OriginY,OriginX):
        #4R;3C+(2 Button spacing)
        
        #generate labels
        label = better_label_ret("Driver Control",16)
        self.layout.addWidget(label, OriginY, OriginX, 1, 3)
        
        label_names = ["Actual Speed","Commanded Speed","Cabin Lights","Headlights","Cabin Temp","Door States"]
        for i in range(1,len(label_names)+1):
            label = better_label_ret(label_names[i-1])
            self.layout.addWidget(label, OriginY+i, OriginX, 1, 2)
        
        #individually make rest of section
        self.LED_CurSpd = better_LED_ret("0.00")
        self.LED_CurSpd.setStyleSheet("background-color: rgb(207, 207, 207); border: 1px solid black")
        self.layout.addWidget(self.LED_CurSpd, OriginY+1, OriginX+1, 1, 1)
        label = better_label_ret("MPH")
        self.layout.addWidget(label, OriginY+1, OriginX+2, 1, 3)
        
        self.TCK_CmdSpd = QDoubleSpinBox()
        self.TCK_CmdSpd.valueChanged.connect(self.TCKF_CmdSpd)
        self.TCK_CmdSpd.setDisabled(True)
        self.layout.addWidget(self.TCK_CmdSpd, OriginY+2, OriginX+1, 1, 1)
        label = better_label_ret("MPH")
        self.layout.addWidget(label, OriginY+2, OriginX+2, 1, 3)
        
        
        self.BTN_CabnLgt = better_button_ret(sizeW=True)
        self.BTN_CabnLgt.clicked.connect(self.BTNF_CL)
        self.layout.addWidget(self.BTN_CabnLgt, OriginY+3, OriginX+1, 1, 1)
        
        self.BTN_HeadLgt = better_button_ret(sizeW=True)
        self.BTN_HeadLgt.clicked.connect(self.BTNF_HL)
        self.layout.addWidget(self.BTN_HeadLgt, OriginY+4, OriginX+1, 1, 1)
        
        self.TCK_Temp = QDoubleSpinBox()
        self.TCK_Temp.setValue(self.Driver_arr[5])
        self.TCK_Temp.valueChanged.connect(self.TCKF_Temp)
        self.TCK_Temp.setDisabled(True)
        self.layout.addWidget(self.TCK_Temp, OriginY+5, OriginX+1, 1, 1)
        label = better_label_ret("°F")
        self.layout.addWidget(label, OriginY+5, OriginX+2, 1, 3)
        
        
        self.BTN_Door_L = better_button_ret(sizeW=True)
        self.BTN_Door_L.clicked.connect(self.BTNF_DL)
        self.layout.addWidget(self.BTN_Door_L, OriginY+6, OriginX+1, 1, 1)
        
        self.BTN_Door_R = better_button_ret(sizeW=True)
        self.BTN_Door_R.clicked.connect(self.BTNF_DR)
        self.layout.addWidget(self.BTN_Door_R, OriginY+6, OriginX+2, 1, 1)
        
        #right side
        self.BTN_EBRK = better_button_ret(sizeH=116,
                                          checkable=True,text="EMERGENCY BRAKE",
                                          style="background-color: rgb(200,  100,  100); border: 6px solid rgb(120, 0, 0); border-radius: 6px")
        self.BTN_EBRK.clicked.connect(self.BTNF_EB)
        self.layout.addWidget(self.BTN_EBRK, OriginY, OriginX+4, 4, 3)
        
        self.BTN_SBRK = better_button_ret(sizeH=56,
                                          checkable=True,text="Service Brake")
        self.BTN_SBRK.clicked.connect(self.BTNF_SB)
        self.layout.addWidget(self.BTN_SBRK, OriginY+4, OriginX+4, 2, 3)
        
        self.BTN_DisPaEB = better_button_ret(checkable=True,text="Disable Passenger eBrake")
        self.BTN_DisPaEB.clicked.connect(self.BTNF_DPE)
        self.layout.addWidget(self.BTN_DisPaEB, OriginY+6, OriginX+4, 1, 3)
        
    def BTNF_CL(self):
        if self.BTN_Mode.isChecked():
            gen_but_tog(self.BTN_CabnLgt)
            self.SW_Driver_arr[3] = self.BTN_CabnLgt.isChecked()
            LED_tog(self.LED_CabnLgt, self.Driver_arr[3])
    def BTNF_HL(self):
        if self.BTN_Mode.isChecked():
            gen_but_tog(self.BTN_HeadLgt)
            self.SW_Driver_arr[4] = self.BTN_HeadLgt.isChecked()
            LED_tog(self.LED_HeadLgt, self.Driver_arr[4])
    def BTNF_DL(self):
        if self.BTN_Mode.isChecked():
            gen_but_tog(self.BTN_Door_L,"Left","Left")
            self.SW_Driver_arr[6] = self.BTN_Door_L.isChecked()
            LED_tog(self.LED_Door_L, self.Driver_arr[6],"Left","Left")
    def BTNF_DR(self):
        if self.BTN_Mode.isChecked():
            gen_but_tog(self.BTN_Door_R,"Right","Right")
            self.SW_Driver_arr[7] = self.BTN_Door_R.isChecked()
            LED_tog(self.LED_Door_R, self.Driver_arr[7],"Right","Right")
    def BTNF_EB(self):
        gen_but_tog(self.BTN_EBRK,"EMERGENCY BRAKE","EMERGENCY BRAKE",
                "background-color: rgb(200,  50,  50); border: 6px solid rgb(120, 0, 0); border-radius: 6px",
                "background-color: rgb(200, 100, 100); border: 6px solid rgb(120, 0, 0); border-radius: 6px")
        self.SW_Driver_arr[8] = self.BTN_EBRK.isChecked()
    def BTNF_SB(self):
        gen_but_tog(self.BTN_SBRK,"Service Brake","Service Brake")
        self.SW_Driver_arr[9] = self.BTN_SBRK.isChecked()   
    def BTNF_DPE(self):
        gen_but_tog(self.BTN_DisPaEB,"Disable Passenger eBrake","Disable Passenger eBrake")
        self.SW_Driver_arr[10] = self.BTN_DisPaEB.isChecked()
        if self.LED_Pass_EB.text() != "DISABLED":
            self.LED_Pass_EB.setText("DISABLED")
            self.LED_Pass_EB.setStyleSheet("background-color: rgb(156, 156, 156); border: 2px solid rgb(100, 100, 100); border-radius: 6px")
        else:
            LED_tog(self.LED_Pass_EB,self.TrainModel_arr[5])
    #++++++
    def TCKF_CmdSpd(self):
        self.SW_Driver_arr[2] = self.TCK_CmdSpd.value()
    def TCKF_Temp(self):
        self.SW_Driver_arr[5] = self.TCK_Temp.value()
        self.LED_Temp.setText(str(  self.Driver_arr[5] ))



#=============================
#abstract generation funcs

def better_button_ret(sizeW=None,sizeH=24,checkable=True,text="DISABLED",style="background-color: rgb(156, 156, 156); border: 2px solid rgb(100, 100, 100); border-radius: 6px"):
        button = QPushButton()
        if sizeW: button.setFixedWidth(60)
        button.setFixedHeight(sizeH)
        button.setCheckable(checkable)
        button.setStyleSheet(style)
        button.setText(text)
        
        return button

def better_label_ret(text,size=10,bold=True):
    label = QLabel(text)
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

def better_LED_ret(text=None,style=None):
    if text: label = QLabel(text)
    else: label = QLabel("Off")
    label.setFixedHeight(24)
    label.setFixedWidth(60)
    if style: label.setStyleSheet(style)
    else: label.setStyleSheet("background-color: rgb(222, 62, 38); border: 2px solid rgb(222, 0, 0); border-radius: 4px")
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    return label

def LED_tog(but,checked, overwrite1="On", overwrite2="Off"):
    #on
    if checked:
        but.setText(overwrite1)
        but.setStyleSheet("background-color: rgb(0, 224, 34); border: 2px solid rgb(30, 143, 47); border-radius: 4px")
    else:
        but.setText(overwrite2)
        but.setStyleSheet("background-color: rgb(222, 62, 38); border: 2px solid rgb(222, 0, 0); border-radius: 4px")
        

#=============================
#threading debug funcs
import time
def SW_mainloop_fast(numtrain,Driver_arr,TrainModel_arr,output_arr):
    time.sleep(2)
    #try:
    while True:
        if w:
            if w.TB_window.isVisible():
                if not main_ouput: print(f"TB TrainC #{numtrain}",w.TrainModel_arr)
                w.TB_window.update_TestBench_JEB382()
                if not w.TB_window.Thread1_active: break
            w.update_SW_UI_JEB382()
            if not w.TB_window.isVisible() and not main_ouput: print(f"SW TrainC #{numtrain}",w.Driver_arr)
            if main_ouput: print(f"OUT TrainC #{numtrain}",w.output_arr)
    '''except Exception as e:
        print("MAINLOOP:",e)
        #print("TB done; minor err")'''

def SW_pyqtloop(numtrain,main_Driver_arr,main_TrainModel_arr,main_output_arr):
    app = QApplication(sys.argv)
    #app.setStyleSheet(stylesheet)
    global w
    w = SW_UI_JEB382(numtrain, main_Driver_arr, main_TrainModel_arr, main_output_arr,app)
    w.show()
    sys.exit(app.exec())
    
def SW_fin(numtrain,main_Driver_arr,main_TrainModel_arr,main_output_arr):
    t1 = threading.Thread(target=SW_pyqtloop, args=(numtrain,main_Driver_arr,main_TrainModel_arr,main_output_arr))
    t2 = threading.Thread(target=SW_mainloop_fast, args=(numtrain,main_Driver_arr,main_TrainModel_arr,main_output_arr))
 
    t1.start()
    t2.start()
 
    t1.join()
    t2.join()


global main_ouput
if __name__ == "__main__":
    Arduino = True
    
    numtrain=1
    main_Driver_arr = [12.00]*90    #gets copied, is meant to get u
    main_TrainModel_arr = [5.0, 12.0, 10.0, 9.0, 9.0, True, True, 0, True, True, True,
                           '000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000007.0']#[7.00]*90
    main_output_arr = [7.00]*90
    
    main_ouput=True
    SW_fin(numtrain,main_Driver_arr,main_TrainModel_arr,main_output_arr)
    #SW_pyqtloop(numtrain,main_Driver_arr,main_TrainModel_arr,main_output_arr)