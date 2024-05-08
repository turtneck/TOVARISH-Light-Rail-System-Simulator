from pyfirmata2 import ArduinoMega, util, STRING_DATA
import time#replace with shared time module when created and we do integration
if __name__ == "__main__": from Tovarish_Belback_Jonah_Train_Controller_Testbenchv2 import *#TestBench_JEB382
from PyQt6.QtWidgets import *
#import sys
import linecache
import threading
if __name__ != "__main__": from SystemTime import SystemTime
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
#auth=0: sits there (if station from beacon, open doors, else dont just sit)

#when entering driver, reset to whats the auto array set


#self.Mode 0: AUTO

#need to calc when to deaccelerate based on total distance from authority (look ahead table?????)



#authority: number of blocks until I stop, dont stop at every station


global board,Pmax,Acc_Lim,DeAcc_Lim,NoHW
Pmax=10000
Acc_Lim=0.5
DeAcc_Lim=1.2#train spec page (1.20 is service brake)
try:
    board = ArduinoMega('COM7')
    NoHW=False
except:
    NoHW=True
    print("No Train Controller HW detected: Arduino COM")

#mini classes---------------------------------------------------------
class LED_PyF():
    def __init__(self,Pin):
        self.item = board.get_pin('d:'+str(Pin)+':o')
        self.item.write(0)#start with LOW
    def write(self,writing):
        #print("O:",writing)
        self.item.write(int(writing))
    
class BTN_PyF():
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
    
class POT_PyF():
    def __init__(self,Pin,start=0,end=100):
        self.start=start;self.end=end#read items
        self.item = board.analog[Pin]
        self.item.enable_reporting()
    def read(self):
        #print("I2:",self.item.read() )
        if self.item.read() == None: return 0
        else: return round( ( (self.item.read())*(self.end-self.start) )+self.start,0)

class DISP_PyF():
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

#arduino verison of HW UI----------------------------------------------
class HW_UI_JEB382_PyFirmat():
    def __init__(self,in_Driver_arr,in_TrainModel_arr,in_output_arr,system_time=None,TestBench=False):
        
        #TODO: ADJUST LENGTH AND INDEX BASED ON I/O dictionary
        
        #it = util.Iterator(board)
        #it.start()
        self.system_time = system_time
        
        in_output_arr = [0.0,0.0, False, False, 0, "", False, False, 68.0]
        self.output_arr = in_output_arr
        
        #-------adjust arrays-------
        #array inputed as an init gets updated as UI is used
        #classes that created this TB have the array they passed locally update with it as well
        '''if len(in_TrainModel_arr)<10:
            #if array is empty or missing values, autofills at end of missing indexes
            t_TrainModel_arr = [0.0, 0.0, 0.0, False, False, False, False, False, False,"00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"]
            in_TrainModel_arr = in_TrainModel_arr + t_TrainModel_arr[len(in_TrainModel_arr):]
        #if over, snips
        elif len(in_TrainModel_arr)>10: in_TrainModel_arr = in_TrainModel_arr[0:-(len(in_TrainModel_arr)-12)]
        #ensure beacon arr indx is proper size
        print("PYF")
        print(in_TrainModel_arr)
        if len(str(in_TrainModel_arr[-1]))<128:
            in_TrainModel_arr[-1] = "0"*(128-len(str(in_TrainModel_arr[-1])))+str(in_TrainModel_arr[-1])
        elif len(str(in_TrainModel_arr[-1]))>128:
            in_TrainModel_arr[-1] = str(in_TrainModel_arr[-1])[len(str(in_TrainModel_arr[-1]))-128:]
        #check tickboxes are within limit(0,100)
        limit1=0;limit2=100
        for i in range(0,4):
            if   in_TrainModel_arr[i] < limit1: in_TrainModel_arr[i]=limit1
            elif in_TrainModel_arr[i] > limit2: in_TrainModel_arr[i]=limit2'''

        self.TrainModel_arr = in_TrainModel_arr

        if self.TrainModel_arr[-1] == None or str(self.TrainModel_arr[-1]) == "nan":
            self.TrainModel_arr[-1] = "00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"

        print(self.TrainModel_arr)
        
        #Driver_arr, is output, the inputted arr is just used for the variable reference
        in_Driver_arr = [50.0, 50.0, 0.0, False, False, 0.0, False, False, False, False, False]
        self.Driver_arr = in_Driver_arr
        
        
        
        
        #+-+-+-+-
        #self.init_clk = time.time()#replace with shared time module when created and we do integration
        
        if __name__ == "__main__": self.init_clk = time.time()
        else: self.init_clk = self.system_time.time()
        
        self.Announcements=""
        self.Mode = False
        
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
            
            #self.Announcements=""
            
            self.DISP = DISP_PyF()
        
        except:
            global NoHW
            NoHW = True
            print("No Train Controller HW detected")
        
        #PowerCalc Inits
        self.uk1=0
        self.ek1=0
        self.timeL=0
        self.Pcmd=0
        self.polarity = bool(self.TrainModel_arr[4])
        self.blockNum = 1#62 [IT3 application]
        self.speedlimit=30
        
        #TestBench
        #self.printout = 3
        '''if __name__ == "__main__":# and TestBench:
            #self.printout = 3
            self.HW_UI_fin(TestBench)
            #self.updateTot()'''
    
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
            
    def updateDisplay(self):
        '''
        self.LED_CabnLgt   .write(self.BTN_CabnLgt.read())
        self.LED_HeadLgt   .write(self.BTN_HeadLgt.read())
        self.LED_Door_L    .write(self.BTN_Door_L .read())
        self.LED_Door_R    .write(self.BTN_Door_R .read())
        self.LED_Pass_EB   .write( bool(self.TrainModel_arr[5]) )
        self.LED_Track_Circ.write( bool(self.TrainModel_arr[6]) )
        self.LED_Stat_Side2.write( self.TrainModel_arr[7]>1 ) #_x 2,3
        self.LED_Stat_Side1.write( self.TrainModel_arr[7]%2 ) #x_ 1,3
        self.LED_Sig_Fail  .write( bool(self.TrainModel_arr[-4]) )
        self.LED_Eng_Fail  .write( bool(self.TrainModel_arr[-3]) )
        self.LED_Brk_Fail  .write( bool(self.TrainModel_arr[-2]) )
        self.LED_EBRK  .write( (bool(self.TrainModel_arr[5]) and not bool(self.Driver_arr[10])) or bool(self.Driver_arr[8]) )
        self.LED_SBRK  .write( bool(self.Driver_arr[9]) )
        
        self.DISP.send(self.TrainModel_arr[-1][1:32])'''
        
        #change outputs to out arr
        '''self.LED_CabnLgt   .write( bool(self.output_arr[6])      )
        self.LED_HeadLgt   .write( bool(self.output_arr[7])      )
        self.LED_Door_L    .write( bool(self.output_arr[4]>1)    )
        self.LED_Door_R    .write( bool(self.output_arr[4]%2)    )
        self.LED_Pass_EB   .write( bool(self.TrainModel_arr[5])  )
        self.LED_Track_Circ.write( bool(self.TrainModel_arr[6])  )
        self.LED_Stat_Side2.write( bool(self.TrainModel_arr[7]>1) ) #_x 2,3
        self.LED_Stat_Side1.write( bool(self.TrainModel_arr[7]%2) ) #x_ 1,3
        self.LED_Sig_Fail  .write( bool(self.TrainModel_arr[-4]) )
        self.LED_Eng_Fail  .write( bool(self.TrainModel_arr[-3]) )
        self.LED_Brk_Fail  .write( bool(self.TrainModel_arr[-2]) )
        self.LED_EBRK  .write( bool(self.output_arr[3]) )
        self.LED_SBRK  .write( bool(self.output_arr[2]) )'''
        self.LED_CabnLgt   .write( bool(self.output_arr[6])      )
        self.LED_HeadLgt   .write( bool(self.output_arr[7])      )
        self.LED_Door_L    .write( bool(self.output_arr[4]%2)    )
        self.LED_Door_R    .write( bool(self.output_arr[4]>1)    )
        self.LED_Pass_EB   .write( bool(self.TrainModel_arr[3])  )
        self.LED_Track_Circ.write( bool(self.TrainModel_arr[4])  )
        self.LED_Stat_Side2.write( bool(self.stat_Dside%2) ) #_x 2,3
        self.LED_Stat_Side1.write( bool(self.stat_Dside>1) ) #x_ 1,3
        #self.LED_Sig_Fail  .write( bool(self.TrainModel_arr[-4]) )
        #self.LED_Eng_Fail  .write( bool(self.TrainModel_arr[-3]) )
        #self.LED_Brk_Fail  .write( bool(self.TrainModel_arr[-2]) )
        self.LED_EBRK  .write( bool(self.output_arr[3]) )
        self.LED_SBRK  .write( bool(self.output_arr[2]) )
        
        #decode message from beacon "(self.TrainModel_arr[-1]" in Update Calc into self.Announcements and display it
        #TODO:diff funct to send to line 1 and 2
        
        if len(self.Announcements) < 16: self.Announcements = self.Announcements+(" "*16)
        self.Announcements = self.Announcements[:16]
        #print(f"<{self.Announcements}> {len(self.Announcements)}")
        self.DISP.send(f"{self.Announcements}{int(self.TrainModel_arr[0])}  {int(self.output_arr[0])}  {self.speedlimit}")
        
        
        
    def updateCalc(self):
        #self.output_arr=[1.0,1.0, False,False, False,False, False,False, 0.0, ""]
        #SB_temp = False
        #EB_temp = False
        
        
        #[NOT IT3] get beacon if possible, overwrite current variable keeping track of what block train is on
        #[NOT IT3] use beacon pickup order to decide which direction its going
        #[NOT IT3] use beacon before station to decide if stoping at current block or next
        #every block flips in polarity, +/- on edge
        if self.polarity != self.TrainModel_arr[4]:
            self.blockNum+=1
        self.polarity = self.TrainModel_arr[4]
        
        self.stat_Dside=0

        distance_to_station=0
        #add up all block's length allowed by authority (num of blocks)
        #Line0, Section1, Block Num2, Block Len3, SpeedLimit4, Infrastructure5, Station Side6
        app_stat=""
        
        #print(f"<{self.TrainModel_arr[2]}>")
            
        
        for i in range(int(self.TrainModel_arr[2])):
            particular_line = linecache.getline('Resources/IT3_GreenLine.txt', self.blockNum+i).split("\t")
            #print(f"LINE: {particular_line}")
            distance_to_station += int(particular_line[3])

            if particular_line[5][:7] == "STATION":
                app_stat=particular_line[5][9:]
                #print(f"PART: {particular_line[5][9:]}")
                if "Left" in particular_line[6]: self.stat_Dside+=1
                if "Right" in particular_line[6]: self.stat_Dside+=2
        
        infra = linecache.getline('Resources/IT3_GreenLine.txt', self.blockNum).split('\t')[5]
        #print(f".txt infra: <{infra[:7]}>, app_stat: <{app_stat}>")
        self.output_arr[5] = ""
        if linecache.getline('Resources/IT3_GreenLine.txt', self.blockNum).split("\t")[5][:7] != "STATION":
            self.Announcements = "APP:"+app_stat[:12]
        elif linecache.getline('Resources/IT3_GreenLine.txt', self.blockNum).split("\t")[5][:7] == "STATION":
            self.Announcements = "NOW:"+infra[9:]#app_stat[:12]
            #if app_stat != "": self.output_arr[5] = app_stat
            #else:  self.output_arr[5] = infra[5][9:]
            self.output_arr[5] = infra[9:]
            
        
        #print(f"BlockNum: {self.blockNum}")
        #print(f"ANNOUNCE: <{self.Announcements}>")
        #print(f"DIST: {distance_to_station}")
        
        #beacon information from file
        '''#Line       Section Block#      BlockLength     Speed Limit     Infrastructure
        if self.TrainModel_arr[-1] != "":
            particular_line = linecache.getline('Beacon_info.txt', int(self.TrainModel_arr[-1], 16))
            #print(int(self.TrainModel_arr[-1], 16))
        else: particular_line=""
        #print("<"+particular_line+">")
        particular_line =particular_line.split("\t")
        #print(particular_line)'''
        
        displace_buffer=10
        #service
        t1=( (0-float(self.TrainModel_arr[0]))/(-1.2 ) )*(5/18)
        s1=0.5*(0+float(self.TrainModel_arr[0]))*t1*(5/18)#1/2 * u * t * conversion of km/hr to m/s
        #emergency
        #t2=( (0-float(self.TrainModel_arr[0]))/(-2.73) )*(5/18)
        #s2=0.5*(0+float(self.TrainModel_arr[0]))*t2*(5/18)#1/2 * u * t * conversion of km/hr to m/s
        
        #if authority<4 and distance to station <= s1 + buffer: serivce brake, power=0, commanded speed=0
        if distance_to_station <= s1+displace_buffer:
            self.output_arr[0] = 0
            self.output_arr[1] = 0
            self.output_arr[2] = True
            self.output_arr[2] = True
        #elif authority<4 and distance to station <= s1: emergency brake, power=0, commanded speed=0
        elif distance_to_station <= s1:
            self.output_arr[0] = 0
            self.output_arr[1] = 0
            self.output_arr[3] = True
        else:
            
            #2   On/Off Service Brake	        Boolean	    Slow down vital control from train controller
            if not self.Mode:#auto
                if int(self.TrainModel_arr[2]) == 0: self.output_arr[2]=True
                #edge case for Station Green Line Block 16
            else:#manual
                self.output_arr[2] = self.Driver_arr[9]
                    
                        
            #3   On/Off Emergency Brake	        Boolean	    Emergency Slow down vital control from train controller
            self.output_arr[3] = (self.TrainModel_arr[3] and not (self.Driver_arr[10]) ) or self.Driver_arr[8]
            
            if self.output_arr[3]: self.output_arr[2] = False
            
            
            
            #fill out self.output_arr and self.Announcements
            #0   Commanded Speed	                m/s	        How fast the driver has commanded the train to go
            if self.Mode: #Manual
                self.output_arr[0] = self.Driver_arr[2]
            else:
                self.output_arr[0] = self.TrainModel_arr[1]
            
            self.speedlimit = int(linecache.getline('Resources/IT3_GreenLine.txt', self.blockNum).split("\t")[4])
            if self.output_arr[0] > self.speedlimit: self.output_arr[0] = float(self.speedlimit)
            
            
            #-----------------------------------------------------------------------------------------------------------------------
            #1   Power                           Watts	    Engine power (Lec2 Slide61-65 pdf54-58)
            if (self.output_arr[2] or self.output_arr[3]): #Brake overrides
                self.output_arr[1] = 0
            elif self.TrainModel_arr[0] == 0 or self.TrainModel_arr[1] == 0:
                self.output_arr[1] = 0
            else:
                if __name__ == "__main__": currtime = time.time()
                else: currtime = self.system_time.time()
                
                
                V_err = self.output_arr[0] - self.TrainModel_arr[4] #Verr=Vcmd-Vactual
                T = currtime-self.timeL
                global Pmax
                if self.Pcmd < Pmax:
                    uk = self.uk1+( (T/2)*(V_err-self.ek1) )
                else:
                    uk = self.uk1
                self.Pcmd = (self.Driver_arr[0]*V_err) + (self.Driver_arr[1]*uk)
                
                if self.Pcmd > Pmax: self.Pcmd=Pmax
                elif self.Pcmd < 0: self.Pcmd=0
            
                #print(f"Pcmd: {self.Pcmd}\t{V_err}\t{uk}\n{T}\t{currtime}\t{self.timeL}")
            
                self.timeL = currtime
                self.uk1 = uk
                self.ek1 = V_err
            
                self.output_arr[1] = self.Pcmd
                
                
            
            #-----------------------------------------------------------------------------------------------------------------------
            #Look ahead algo (returns arr of total distance)
            
            
        '''#2   On/Off Service Brake	        Boolean	    Slow down vital control from train controller
        if not self.Mode:#auto
            if self.TrainModel_arr[2] == 0: self.output_arr[2]=True
            #edge case for Station Green Line Block 16
        else:#manual
            self.output_arr[2] = SB_temp or self.Driver_arr[9]
                
                    
        #3   On/Off Emergency Brake	        Boolean	    Emergency Slow down vital control from train controller
        self.output_arr[3] = EB_temp or (self.TrainModel_arr[3] and not (self.Driver_arr[10]) ) or self.Driver_arr[8]
        
        if self.output_arr[3]: self.output_arr[2] = False'''
        
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
        self.output_arr[6] = not self.TrainModel_arr[5] or (self.Driver_arr[3] and self.Mode)
        #7   headlights (exterior)	        Boolean	    Automatically turned on from enviroment or toggled by driver; 1 on, 0 off
        self.output_arr[7] = not self.TrainModel_arr[5] or (self.Driver_arr[4] and self.Mode)
        
        #-----------------------------------------------------------------------------------------------------------------------
        #8   Cabin Temperature	            Fahrenheit  What temperature to make cabin
        self.output_arr[8] = 68 + self.Driver_arr[5]
        
        
        #-----------------------------------------------------------------------------------------------------------------------
        #x   Act On Faults/Failures	        N/A	        No specific unit, but a change in behavior represented in one of these other outputs
        
    
    #def Lookahead(self):
    
        
    def updateTot(self):
        #print(f'Train Controller HW: NAN check {self.TrainModel_arr[-1]} <{str(self.TrainModel_arr[-1])}> {str(self.TrainModel_arr[-1]) == "nan"}')
        if self.TrainModel_arr[-1] == None or str(self.TrainModel_arr[-1]) == "nan":
            #print('Train Controller HW: caught nan')
            self.TrainModel_arr[-1] = "00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
            #print(f'Train Controller HW: nan check1 {self.TrainModel_arr[-1]}')
            #print(f'Train Controller HW: nan check2 {self.TrainModel_arr}')

        global NoHW
        #if not NoHW:
        print("update")
        #sys.stdout.write("p")
        #bugfix: cant get updates without a printout????? i hate pyfrimata
        with open('TrainC_HW_bugfix.txt', 'w') as f:
            f.write('Hi')
        
        if not NoHW:
            print("updateRead")
            self.updateRead()
        
        print("updateCalc")
        self.updateCalc()
        
        if not NoHW:
            print("updateDisplay")
            self.updateDisplay()
        
        if __name__ != "__main__":
            print(f"\nDriver TrainC #1:\t{self.Driver_arr}\t{'AUTO' if not self.Mode else 'MANUAL'}")
            print(f"TrainModel TrainC #1:\t{self.TrainModel_arr} {'AUTO' if not self.Mode else 'MANUAL'}")
            print(f"Output TrainC #1:\t{self.output_arr}\t{'AUTO' if not self.Mode else 'MANUAL'}")

        
    def __del__(self):
        print('HW_UI_JEB382_PyFirmat: Destructor called')
        #if self.TB_window: sys.exit(self.app.exec())



    #[{!!!!!!!!!!!!!!!!!!!!!!!!}]
    #can call this just as its class, this implies its not getting information from a testbench which requires threading
    def HW_UI_mainloop_fast(self):
        time.sleep(2)
        ptime = time.time()
        
        #global printout
        global NoHW
        prin=True
        while True and not NoHW:
            
            with open('TrainC_HW_bugfix.txt', 'w') as f: f.write('Hi')
            
            self.updateRead()
            self.updateCalc()
            if (int(time.time())-int(ptime))%2==0 and prin:                
                prin=False
                self.updateDisplay()
                #if self.printout == 1 and not NoHW: print(f"Driver TrainC #1:\t{self.Driver_arr}\t{'AUTO' if not self.Mode else 'MANUAL'}")
                #elif self.printout == 2 and not NoHW: print(f"TrainModel TrainC #1:\t{self.TrainModel_arr} {'AUTO' if not self.Mode else 'MANUAL'}")
                #elif self.printout == 3 and not NoHW: print(f"Output TrainC #1:\t{self.output_arr}\t{'AUTO' if not self.Mode else 'MANUAL'}")
                
                if not NoHW:
                    print("\nHW_UI_mainloop_fast")
                    print(f"Driver TrainC #1:\t{self.Driver_arr}\t{'AUTO' if not self.Mode else 'MANUAL'}")
                    print(f"TrainModel TrainC #1:\t{self.TrainModel_arr} {'AUTO' if not self.Mode else 'MANUAL'}")
                    print(f"Output TrainC #1:\t{self.output_arr}\t{'AUTO' if not self.Mode else 'MANUAL'}")
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
        
def TC_HW_init(driver,trainmodel,output,system_time,TestB=False):
    print("TC_HW_init")
    Arduino = True
    
    if not NoHW:
        it = util.Iterator(board)  
        it.start()
    
    return  HW_UI_JEB382_PyFirmat(driver, trainmodel, output,
                                  system_time,
                                  TestB)


if __name__ == "__main__":
    Arduino = True
    
    main_Driver_arr = []#[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    #main_TrainModel_arr = [0.0, 0.0, 0.0, 0.0, False, False, False , False, False, False,
    #                       "00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"]
    main_TrainModel_arr = [0,0,4,False,True,False,
                           "00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"]
    #[]
    main_output_arr = [] #[7.00]*90
    #w = HW_UI_JEB382_PyFirmat(main_Driver_arr,main_TrainModel_arr,True)
    
    try:
        it = util.Iterator(board)  
        it.start()
    except:
        print("No Train Controller HW detected: util.Iterator")
    
    #global glob_UI
    #global printout
    #printout=2
    #print("-1234567890abcdefghijklmnopqrstuvvvvv")
    glob_UI = HW_UI_JEB382_PyFirmat(main_Driver_arr,
                                    main_TrainModel_arr,
                                    main_output_arr,
                                    True)
    glob_UI.HW_UI_fin(True)
    
        