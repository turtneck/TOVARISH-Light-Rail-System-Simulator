from pyfirmata2 import ArduinoMega, util, STRING_DATA
import time#replace with shared time module when created and we do integration
if __name__ == "__main__": from Tovarish_Belback_Jonah_Train_Controller_Testbenchv2 import *#TestBench_JEB382
from PyQt6.QtWidgets import *
#import sys
import linecache
import threading
import sys,os
#print(f"FILE:\t\t<{__file__[-10:-3]}>")
#print(f"FILE2:\t\t<{sys.argv[0][-10:-3]}>")
if __name__ != "__main__" and sys.argv[0][-10:-3] != "Testing": from SystemTime import SystemTime
import math


#commanded speed: Auto/Manual: Turn into Verr, calc power with Kp Ki
#double check array.txt lines up with I/O
#if new indexes, add new LEDs???
#change test bench to new I/O
    #input text box of station name
    #label below displays the output beacon with other given info
#add txt file of look up table
    #one per line?
    #line number is index number, use '.split()'
    #look at excel file
    #python parser?

#fill out rest of updatCalc()

#doors open: cant move


#max auth of 4 (no foresight)
#auth=0: sits there (if station from beacon, open doors, else don't just sit)

#when entering driver, reset to what's the auto array set


#self.Mode 0: AUTO

#need to calc when to deaccelerate based on total distance from authority (look ahead table?????)



#authority: number of blocks until I stop, don't stop at every station


global board,Pmax,NoHW,RL_LAjump_dict,RL_switchdirs_dict,dir_path

dir_path = os.path.dirname(os.path.realpath(__file__))
dir_path=dir_path.replace('\Train_Controller_HW','')
print(f"DIRECTORY:\t\t{dir_path}>")

Pmax=120000
try:
    board = ArduinoMega('COM7')
    NoHW=False
except (Exception,):
    NoHW=True
    print("No Train Controller HW detected: Arduino COM")


#================================================================================

#[last, curr]
#IT4: 0:Downlist, 1:Uplist, 2:delete
RL_switchdirs_dict ={
    #downs
    "[1, 16]":0,
    "[16, 1]":0,
    "[32, 72]":0,
    "[43, 67]":0,
    #ups
    "[0, 9]":1,
    "[26, 76]":1,
    "[76, 26]":1,
    "[38, 71]":1,
    "[71, 38]":1,
    "[72, 32]":1,
    "[67, 43]":1,
    "[52, 66]":1,
    "[66, 52]":1,
    #back to yard, delete
    "[9, 0]":2
}


#[block, direction] (dir: 0:down, 1:up)
RL_LAjump_dict ={
    "[67, 1]":[43,42,41,40],
    "[1, 1]":[16,17,18,19],
    "[0, 0]":[9,8,7,6],
    "[0, 1]":[9,8,7,6],
    "[76, 0]":[27,26,25,24],
    "[72, 1]":[32,31,30,29],
    "[71, 0]":[38,37,36,35],
    "[66, 0]":[52,51,50,49]
}



#================================================================================
#mini classes---------------------------------------------------------
class LED_PyF:
    def __init__(self,Pin):
        self.item = board.get_pin('d:'+str(Pin)+':o')
        self.item.write(0)#start with LOW
    def write(self,writing):
        #print("O:",writing)
        self.item.write(int(writing))
    
class BTN_PyF:
    def __init__(self,Pin):
        self.item = board.get_pin('d:'+str(Pin)+':i')
        self.prev_red=False
        self.outp=False
        #self.item.enable_reporting()
    def read(self):
        #print(self.item.read())
        #if self.item.read() == None or self.item.read() <0.85: return 0
        #else: return 1
        #toggle
        red = self.item.read()
        if red == 1 and red != self.prev_red: self.outp = not self.outp
        self.prev_red = red
        return int(self.outp)
    
class POT_PyF:
    def __init__(self,Pin,start=0,end=100):
        self.start=start;self.end=end#read items
        self.item = board.analog[Pin]
        self.item.enable_reporting()
    def read(self):
        #print("I2:",self.item.read() )
        if self.item.read() is None: return 0
        else: return round( ( (self.item.read())*(self.end-self.start) )+self.start,0)

class DISP_PyF:
    def __init__(self):
        self.laststring = ""
        board.send_sysex(STRING_DATA, util.str_to_two_byte_iter(""))
    def send(self,writing):
        #autobreaks line if over 16 characters, max length is 31 characters
        #autofills with spaces to elimate bug with it not clearing 2nd line
        temp = writing+" "*(31-len(writing))
        if writing != self.laststring:
            board.send_sysex(STRING_DATA, util.str_to_two_byte_iter(temp))
            #print("."+f"{writing:<31}"[:32]+".")
            #print("."+str(temp)+".")
            self.laststring = writing



#================================================================================
#arduino verison of HW UI----------------------------------------------
class HW_UI_JEB382_PyFirmat:
    def __init__(self,in_Driver_arr,in_TrainModel_arr,in_output_arr,TestBench=False):
        
        #TODO: ADJUST LENGTH AND INDEX BASED ON I/O dictionary
        
        #it = util.Iterator(board)
        #it.start()
        
        in_output_arr = [0.0,0.0, False, False, 0, "", False, False, 68.0]
        self.output_arr = in_output_arr
        self.TrainModel_arr = in_TrainModel_arr

        if self.TrainModel_arr[-1] is None or str(self.TrainModel_arr[-1]) == "nan":
            self.TrainModel_arr[-1] = "0"*128

        print(self.TrainModel_arr)
        
        #Driver_arr, is output, the inputted arr is just used for the variable reference
        in_Driver_arr = [50.0, 50.0, 0.0, False, False, 0.0, False, False, False, False, False]
        self.Driver_arr = in_Driver_arr
        
        #+-+-+-+-
        
        #input sets
        try:
            self.TCK_Kp     = POT_PyF(0)
            self.TCK_Ki     = POT_PyF(1)
            self.TCK_CmdSpd = POT_PyF(2)
            self.TCK_Temp   = POT_PyF(3,-20,20)
            
            self.BTN_CabnLgt = BTN_PyF(38)
            self.BTN_HeadLgt = BTN_PyF(39)#
            self.BTN_Door_L  = BTN_PyF(42)
            self.BTN_Door_R  = BTN_PyF(44)#
            self.BTN_EBRK    = BTN_PyF(46)
            self.BTN_SBRK    = BTN_PyF(48)#
            self.BTN_DisPaEB = BTN_PyF(50)#
            self.BTN_Mode    = BTN_PyF(52)#
            
            #LEDs
            self.LED_CabnLgt    = LED_PyF(22)
            self.LED_HeadLgt    = LED_PyF(23)
            self.LED_Door_L     = LED_PyF(24)
            self.LED_Door_R     = LED_PyF(25)
            self.LED_Pass_EB    = LED_PyF(26)
            self.LED_Track_Circ = LED_PyF(27)
            self.LED_Stat_Side2 = LED_PyF(28)
            self.LED_Stat_Side1 = LED_PyF(29)
            self.LED_Sig_Fail   = LED_PyF(30)
            self.LED_Eng_Fail   = LED_PyF(31)
            self.LED_Brk_Fail   = LED_PyF(32)
            self.LED_EBRK       = LED_PyF(33)
            self.LED_SBRK       = LED_PyF(34)
                        
            self.DISP = DISP_PyF()
        
        except (Exception,):
            global NoHW
            NoHW = True
            print("No Train Controller HW detected")
        
        self.Announcements=""
        self.Mode = False
        self.stat_Dside=0
        
        #PowerCalc Inits
        self.uk1=0
        self.ek1=0
        if __name__ != "__main__" and sys.argv[0][-10:-3] != "Testing":
            self.timeL = SystemTime.time()
        else:
            print(f"TRAINC HW: sys.argv[0]: <{sys.argv[0][-10:-3]}>")
            self.timeL = time.time()
        self.Pcmd=0
        
        #Block traversal
        self.line=None #False:Greenline, True:Redline
        self.polarity = bool(self.TrainModel_arr[4])
        #which line, train spawn has beacon
        print(f"TRAINC HW INIT BEACON SPAWN: <{self.TrainModel_arr[-1][-4:]}>")
        if self.TrainModel_arr[-1] == "0"*128:
            #NOTE: should raise error but due to state of system, nessecary
            #raise Exception("TRAINC HW INIT: NOT SPAWNED ON SPECIFIED BLOCK")
            
            print("TRAINC HW INIT: NOT SPAWNED ON SPECIFIED BLOCK, ASSUMPTION GREENLINE")
            self.line=False
            self.speedlimit=30#[IT3 application]
            self.blockNum = 1
        elif self.TrainModel_arr[-1][-4] == "G":
            #greenline
            self.line=False
            print("TRAINC HW INIT: SPAWNED ON GREENLINE: PROPER")
            self.speedlimit=30#[IT3 application]
            self.blockNum = 1
        elif self.TrainModel_arr[-1][-4] == "R":
            #redline
            self.line=True
            print("TRAINC HW INIT: SPAWNED ON REDLINE: PROPER")
            self.speedlimit=40
            self.lastbeacon=0 #IT4: Redline start is block 0, will be overwritten
            self.blockNum = 0
            #may need edge case of stopping
        else: raise Exception(f"TRAINC HW INIT: SPAWN BLOCK IS NONSENSE:\n<{self.TrainModel_arr[-1]}>")
        
        self.polarity = bool(self.TrainModel_arr[4])
        self.direction = 0 #IT4: 0:Downlist, 1:Uplist
        
        #distance traveled
        self.passover=False
        self.traveled=0 #over block
        self.distleft=0 #dist left in block
        self.lastspd=0
    
    
    
    
    #================================================================================
    def updateRead(self):
        self.Driver_arr[3] = self.BTN_CabnLgt.read()
        self.Driver_arr[4] = self.BTN_HeadLgt.read()
        self.Driver_arr[6] = self.BTN_Door_L.read()
        self.Driver_arr[7] = self.BTN_Door_R.read()
        self.Driver_arr[8] = self.BTN_EBRK.read()
        self.Driver_arr[9] = self.BTN_SBRK.read()
        self.Driver_arr[10]= self.BTN_DisPaEB.read()
        
        self.Driver_arr[0] = self.TCK_Kp.read()
        self.Driver_arr[1] = self.TCK_Ki.read()
        self.Driver_arr[2] = self.TCK_CmdSpd.read()
        self.Driver_arr[5] = self.TCK_Temp.read()
        self.Mode = self.BTN_Mode.read()
    
    
    
    
    #================================================================================
    def updateDisplay(self):
        self.LED_CabnLgt   .write( bool(self.output_arr[6])      )
        self.LED_HeadLgt   .write( bool(self.output_arr[7])      )
        self.LED_Door_L    .write( bool(self.output_arr[4]%2)    )
        self.LED_Door_R    .write( bool(self.output_arr[4]>1)    )
        self.LED_Pass_EB   .write( bool(self.TrainModel_arr[3])  )
        self.LED_Track_Circ.write( bool(self.TrainModel_arr[4])  )
        self.LED_Stat_Side2.write( bool(self.stat_Dside%2) ) #_x 2,3
        self.LED_Stat_Side1.write( bool(self.stat_Dside>1) ) #x_ 1,3
        self.LED_EBRK  .write( bool(self.output_arr[3]) )
        self.LED_SBRK  .write( bool(self.output_arr[2]) )
        
        if len(self.Announcements) < 16: self.Announcements = self.Announcements+(" "*16)
        self.Announcements = self.Announcements[:16]
        #print(f"<{self.Announcements}> {len(self.Announcements)}")
        
        #m/s to mph
        #actual, COMspd, speedlimit
        self.DISP.send(f"{self.Announcements}{int(self.TrainModel_arr[0]*2.237)}  {int(self.output_arr[0]*2.237)}  {self.speedlimit*2.237}")
        
        
        
        
    #================================================================================
    def updateCalc(self,file=None):
        #on polarity edge case:
            #greenline:
                #curr++, read txt
            #redline:
                #if beacon: curr_override
                #else: calc block number from traveled since beacon

        #return:
            #speed limit
            #distance alloted from authority
        
        
        #every block flips in polarity, +/- on edge
        if self.polarity != self.TrainModel_arr[4]:
            print("TRAINC HW: NEW BLOCK")
            #greenline
            #because of discussion in class where we decided it just goes back to yard
            #train goes on set path: preset list
            #possibly change when redline is figured out
            if not self.line:
                self.blockNum+=1
            
            #redline
            else:
                #figure out self.direction, distance_to_station
                
                #if beacon: curr_override
                #else: calc block number from traveled since beacon
                if self.TrainModel_arr[-1] != "0"*128:# and not self.passover: #???? passover
                    # new beacon,read: curr_override
                    block = int(self.TrainModel_arr[-1][-3:])
                    self.blockNum = block
                    
                    #TODO?: depending on last beacon, adjust direction
                    
                    temp_arr= [self.lastbeacon, block]
                    #print(f"<{str(temp_arr)}>")
                    if str(temp_arr) in RL_switchdirs_dict:
                        # change in direction
                        #print( switchdirs_dict[ str(temp_arr) ] )
                        self.direction = RL_switchdirs_dict[ str(temp_arr) ]
                        print(f"<{str(temp_arr)}>: <{RL_switchdirs_dict[ str(temp_arr) ]}>")
                        #input("wait")
                        
                        if self.direction == 2:
                            #going back to yard
                            #TODO SIGNAL
                            self.__del__()
                            
                        
                    else:
                        # unless trackmodel really screwed up:
                        # this is a case between beacons where direction doesn't change
                        print(f"TRAINC HW CALC: BEACON DIRECTIONAL SWITCH EDGECASE NOT FOUND: <{str(temp_arr)}>")
                    
                    #update last beacon
                    self.lastbeacon = block
                else:
                    #in new block but unbeaconed
                    self.blockNum+= (self.direction*-2) + 1 #-1 if up(1), +1 if down(0)
            
            
            
            self.traveled=0
            self.passover=True#just changed block
        else:
            self.passover=False
        self.polarity = self.TrainModel_arr[4]
        
        
        
        #-----------------------------
        #TODO: REDUCE LOGIC, REDUNDENT LINES
        
        
        #distance
        distance_to_station=0
        self.stat_Dside=0
        app_stat=None
                
                
        #================================================
        
        if not self.line:
            temp=range(int(self.TrainModel_arr[2])+1)
        else:
            # get 5size array of future blocks
            curr=self.blockNum
            temp=[]
            for i in range(6):
                temp.append(curr)
                # if edgecase of block+dir: adjust, add, break
                if str([curr,self.direction]) in RL_LAjump_dict:
                        for x in RL_LAjump_dict[ str([curr,self.direction]) ]: temp.append(x)
                        break

                #else adjust curr by direction
                curr += (self.direction*-2) + 1
        
        #TODO: DEBUG???
        #cut back to 5 incase#NOTE:don't have to due to next line
        #add up distance of array according to authority+1
        for i in range(int(self.TrainModel_arr[2])+1):
            if not self.line:
                infra = linecache.getline(dir_path+'\Resources\IT3_GreenLine.txt', self.blockNum).split('\t')[5]
                particular_line = linecache.getline(dir_path+'\Resources\IT3_GreenLine.txt', self.blockNum+i).split("\t")
            else:
                #print(f"<{i}>: {temp}")
                #print(dir_path+'\Resources\IT4_RedLine.txt')
                infra = linecache.getline(dir_path+'\Resources\IT4_RedLine.txt', self.blockNum+1).split('\t')[5]
                particular_line = linecache.getline(dir_path+'\Resources\IT4_RedLine.txt', temp[i]+1).split("\t")
            #print(f"LINE: <{self.blockNum}<,\t{particular_line}")
            #print(f"LINE: <{temp[i+1]+1}>,\t{particular_line}")
            distance_to_station += int(float(particular_line[3]))

            if particular_line[5][:7] == "STATION" or infra[:7] == "STATION":
                if "Left" in particular_line[6]: self.stat_Dside+=1
                if "Right" in particular_line[6]: self.stat_Dside+=2
                if i<2: app_stat=particular_line[5][9:]
            else:
                app_stat=None
        
        self.Announcements= ""
        self.output_arr[5] = ""
        if app_stat:
            if not self.line:
                infra = linecache.getline(dir_path+'\Resources\IT3_GreenLine.txt', self.blockNum  ).split('\t')[5]
            else:
                infra = linecache.getline(dir_path+'\Resources\IT4_RedLine.txt',   self.blockNum+1).split('\t')[5]
            self.output_arr[5] = app_stat[:12]
            self.Announcements = f"{'NOW' if infra[:7] == 'STATION' else 'APP'}:{app_stat[:12]}"
        #================================================  
            
            
            
            
        
        #print(f"BlockNum: {self.blockNum}")
        #print(f"ANNOUNCE: <{self.blockNum}>,\t<{i}>,\t<{app_stat}>,\t<{self.Announcements}>,\t<{self.output_arr[5]}>")
        #print(f"ANNOUNCE: <{self.blockNum}>,\t<{self.stat_Dside}>,\t<{self.Announcements}>,\t<{self.output_arr[5]}>")
        #print(f"DIST: {distance_to_station},\tANNOUNCE: <{self.Announcements}>")
        
        
         #2   On/Off Service Brake	        Boolean	    Slow down vital control from train controller
        if not self.Mode:#auto
            if int(self.TrainModel_arr[2]) == 0:
                self.output_arr[2]=True
            else:
                #reset from previous non auth, if it needs to brake will be caught later
                self.output_arr[2]=False
        else:#manual
            self.output_arr[2] = self.Driver_arr[9]
                    
                        
        #3   On/Off Emergency Brake	        Boolean	    Emergency Slow down vital control from train controller
        self.output_arr[3] = (self.TrainModel_arr[3] and not (self.Driver_arr[10]) ) or self.Driver_arr[8]
        if self.output_arr[3]: self.output_arr[2] = False
        
        
        #distance traveled-----------
        displace_buffer=10
        #service
        t1=( (0-float(self.TrainModel_arr[0]))/(-1.2 ) )#*(5/18)
        s1=0.5*(0+float(self.TrainModel_arr[0]))*t1#*(5/18)#1/2 * u * t * conversion of km/hr to m/s
        
        t2=( (0-float(self.TrainModel_arr[0]))/(-2.73 ) )#*(5/18)
        s2=0.5*(0+float(self.TrainModel_arr[0]))*t2#*(5/18)#1/2 * u * t * conversion of km/hr to m/s
        
        if __name__ != "__main__" and sys.argv[0][-10:-3] != "Testing": currtime = SystemTime.time()
        else: currtime = time.time()
        T = currtime-self.timeL #sec-sec
        
        if not self.passover: self.traveled += 0.5*(float(self.TrainModel_arr[0])+self.lastspd)*T#*(5/18)
        distance_to_station -= self.traveled
        
        
        #PRESENT
        #print(f"DIST: {distance_to_station},\tTRVL:{self.traveled},\tGRP:<{temp}>,\t<{self.output_arr[5]}>")
        
            
        
        #if authority<4 and distance to station <= s1 + buffer: serivce brake, power=0, commanded speed=0
        if distance_to_station <= s1+displace_buffer:
            #print("TrainC HW: service brake")
            self.output_arr[0] = 0
            self.output_arr[1] = 0
            self.output_arr[2] = True
            print("SBRAKE")
            input("wait")
        #elif authority<4 and distance to station <= s1: emergency brake, power=0, commanded speed=0
        elif distance_to_station < s2+displace_buffer:
            #print("TrainC HW: emergency brake")
            self.output_arr[0] = 0
            self.output_arr[1] = 0
            self.output_arr[3] = True
            print("EBRAKE")
            input("wait")
        else:
            #print("TrainC HW: moving")
            #fill out self.output_arr and self.Announcements
            #0   Commanded Speed	                m/s	        How fast the driver has commanded the train to go
            if self.Mode: #Manual
                self.output_arr[0] = self.Driver_arr[2]
            else:
                self.output_arr[0] = self.TrainModel_arr[1]
            #-----
            if not self.line:
                self.speedlimit = int(linecache.getline(dir_path+'\Resources\IT3_GreenLine.txt', self.blockNum).split("\t")[4])
            else:
                self.speedlimit = int(linecache.getline(dir_path+'\Resources\IT4_RedLine.txt', self.blockNum+1).split("\t")[4])
            #-----
            if self.output_arr[0] > (self.speedlimit/3.6):
                self.output_arr[0] = float((self.speedlimit/3.6))#TODO: SPDLMT is KM/HR, CONVERT
                #print("TrainC HW: over speed limit")
            
            
            #-----------------------------------------------------------------------------------------------------------------------
            #1   Power                           Watts	    Engine power (Lec2 Slide61-65 pdf54-58)
            if self.output_arr[2] or self.output_arr[3]: #Brake overrides
                #print("TrainC HW: moving: cancel: brake")
                self.output_arr[1] = 0
            elif (not self.Mode and self.TrainModel_arr[1] == 0) or (self.Mode and self.Driver_arr[2] == 0) or self.TrainModel_arr[2] == 0:
                #print("TrainC HW: moving: cancel: no auth and/or cmd spd")
                self.output_arr[1] = 0
            else:                    
                #print("TrainC HW: moving: moving confirm")
                
                V_err = self.output_arr[0] - self.TrainModel_arr[0] #Verr=Vcmd-Vactual ; m/s-m/s
                #T = currtime-self.timeL #sec-sec
                if self.Pcmd < Pmax:
                    uk = self.uk1+( (T/2)*(V_err-self.ek1) )  # m + ( s*(m/s-m/s) )
                else:
                    uk = self.uk1
                self.Pcmd = (self.Driver_arr[0]*V_err) + (self.Driver_arr[1]*uk) #(m/s*m/s)+(Ki*m) ; m2/s2 + m
                
                if file:
                    file.write(f"curr:{currtime},\t last:{self.timeL}\n")
                    file.write(f"T: {T}\n")
                    file.write(f"Verr: {V_err}\n")
                    file.write(f"ek1: {self.ek1}\n")
                    file.write(f"uk: {uk}")
                    file.write(f"uk1: {self.uk1}\n")
                    file.write(f"Pcmd: {self.Pcmd}\n")
                
                if self.Pcmd > Pmax: self.Pcmd=Pmax
                elif self.Pcmd < 0: self.Pcmd=0
                #print(f"Pcmd: {self.Pcmd}\t{V_err}\t{uk}\n{T}\t{currtime}\t{self.timeL}")
                self.uk1 = uk
                self.ek1 = V_err
            
                self.output_arr[1] = self.Pcmd
                
                
        self.timeL = currtime
            #-----------------------------------------------------------------------------------------------------------------------
            #Look ahead algo (returns arr of total distance)
        
        
        #-----------------------------------------------------------------------------------------------------------------------
        #4   Open/Close Left/Right Doors	    integer	    Which Doors to open; 0:none, 1:left, 2:right, 3:both
        if not self.Mode and (self.TrainModel_arr[0]==0):
            self.output_arr[4] = self.stat_Dside
            
        elif self.Mode and (self.TrainModel_arr[0]==0):#not moving manual
            self.output_arr[4] = self.Driver_arr[6] + self.Driver_arr[7]*2
        
        else:
            self.output_arr[4] = 0
            
        #-----------------------------------------------------------------------------------------------------------------------
        #5   Announce Stations	            String	    not "" make announcement of String; "" don't make announcement
        #earlier
        
        
        #6   Cabin lights (interior)	        Boolean	    lights inside cabin; Automatically turned on from enviroment or toggled by driver; 1 on, 0 off
        self.output_arr[6] = self.TrainModel_arr[5] or (self.Driver_arr[3] and self.Mode)
        #7   headlights (exterior)	        Boolean	    Automatically turned on from enviroment or toggled by driver; 1 on, 0 off
        self.output_arr[7] = self.TrainModel_arr[5] or (self.Driver_arr[4] and self.Mode)
        
        #-----------------------------------------------------------------------------------------------------------------------
        #8   Cabin Temperature	            Fahrenheit  What temperature to make cabin
        self.output_arr[8] = 68 + self.Driver_arr[5]
        
        
        #-----------------------------------------------------------------------------------------------------------------------
        #x   Act On Faults/Failures	        N/A	        No specific unit, but a change in behavior represented in one of these other outputs
        
        #print(f"Output TrainC HW:\t{self.output_arr}\t{'AUTO' if not self.Mode else 'MANUAL'}")
        self.lastspd = self.TrainModel_arr[0]
        
    
    
    
    #================================================================================
    def updateTot(self):
        if self.TrainModel_arr[-1] is None or str(self.TrainModel_arr[-1]) == "nan": self.TrainModel_arr[-1] = "0"*128

        with open('TrainC_HW_bugfix.txt', 'w') as f: f.write('Hi')
        
        global NoHW
        if not NoHW:
            print("updateRead")
            self.updateRead()
            print("updateCalc")
            self.updateCalc()
            print("updateDisplay")
            self.updateDisplay()
        else:
            print("updateCalc")
            self.updateCalc()
        
        if __name__ != "__main__":
            print(f"\nDriver TrainC HW:\t{self.Driver_arr}\t{'AUTO' if not self.Mode else 'MANUAL'}")
            print(f"TrainModel TrainC HW:\t{self.TrainModel_arr} {'AUTO' if not self.Mode else 'MANUAL'}")
            print(f"Output TrainC HW:\t{self.output_arr}\t{'AUTO' if not self.Mode else 'MANUAL'}")

        
    def __del__(self):
        try:
            super().__del__()
        except (Exception,):
            print("Hi PyCharm :////")
        print('HW_UI_JEB382_PyFirmat: Destructor called')







    #================================================================================
    #[{!!!!!!!!!!!!!!!!!!!!!!!!}]
    #can call this just as its class, this implies it's not getting information from a testbench which requires threading
    def HW_UI_mainloop_fast(self):
        time.sleep(2)
        ptime = time.time()
        
        #global printout
        global NoHW
        prin=True
        while True:
            with open('TrainC_HW_bugfix.txt', 'w') as f: f.write('Hi')
            
            if not NoHW: self.updateRead()
            self.updateCalc()
            if (int(time.time())-int(ptime))%2==0 and prin:                
                prin=False
                if not NoHW: self.updateDisplay()
                #if self.printout == 1 and not NoHW: print(f"Driver TrainC HW:\t{self.Driver_arr}\t{'AUTO' if not self.Mode else 'MANUAL'}")
                #elif self.printout == 2 and not NoHW: print(f"TrainModel TrainC HW:\t{self.TrainModel_arr} {'AUTO' if not self.Mode else 'MANUAL'}")
                #elif self.printout == 3 and not NoHW: print(f"Output TrainC HW:\t{self.output_arr}\t{'AUTO' if not self.Mode else 'MANUAL'}")
                
                #if not NoHW:
                #print("\nHW_UI_mainloop_fast")
                #PRESENT
                print("===================================")
                print(f"Driver TrainC HW:\t{self.Driver_arr} {'AUTO' if not self.Mode else 'MANUAL'}")
                print(f"TrainModel TrainC HW:\t{self.TrainModel_arr} {'AUTO' if not self.Mode else 'MANUAL'}")
                print(f"Output TrainC HW:\t{self.output_arr} {'AUTO' if not self.Mode else 'MANUAL'}")
            elif (int(time.time())-int(ptime))%2!=0:
                prin=True
            #print(self.Mode)
            #if self.Mode or not self.Mode: sys.stdout.write("")
            
    def HW_UI_fin(self, TestBench=False):
        print(f"HW_UI_fin: {TestBench}")#,\t{self.printout}")
        
        t1 = threading.Thread(target=self.HW_UI_mainloop_fast, args=())
        t1.start()
        
        if TestBench:
            t2 = threading.Thread(target=TB_pyqtloop, args=(1,self.TrainModel_arr))
            t2.start()
            t2.join()
        t1.join()
    
    


#================================================================================
#help funcs------------------------------------------------------------
def TC_HW_init(driver,trainmodel,output,TestB=False):
    print("TC_HW_init")
    #Arduino = True
    
    if not NoHW:
        it = util.Iterator(board)  
        it.start()
    
    return  HW_UI_JEB382_PyFirmat(driver, trainmodel, output, TestB)

def def_main(line=4):
    #Arduino = True
    
    main_Driver_arr = []#[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    if line == 0: main_TrainModel_arr = [0,0,3,False,True,False, "0"*128]#nonspecified
    elif line == 1: main_TrainModel_arr = [0,0,3,False,True,False, "0"*124+"G062"]#greenline
    elif line == 2: main_TrainModel_arr = [0,0,3,False,True,False, "0"*124+"R000"]#redline
    else: main_TrainModel_arr = [0,0,3,False,True,False, "5"*128]#nonsense
    main_output_arr = []
    
    try:
        it = util.Iterator(board)  
        it.start()
    except (Exception,):
        print("No Train Controller HW detected: util.Iterator")
    
    glob_UI = HW_UI_JEB382_PyFirmat(main_Driver_arr, main_TrainModel_arr, main_output_arr, TestBench=True)
    glob_UI.HW_UI_fin(True)

    


#================================================================================
if __name__ == "__main__":
    #def_main(0)     #nonspec
    #def_main(1)    #green
    def_main(2)    #red
    #def_main( )     #nonsense
        