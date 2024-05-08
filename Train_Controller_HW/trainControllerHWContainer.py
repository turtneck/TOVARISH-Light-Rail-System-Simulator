# container class for calling everything from train
import sys
import numpy

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication


if __name__ == "__main__":
    from Tovarish_Belback_Jonah_Train_Controller_Testbenchv2 import *
    from Tovarish_Belback_Jonah_Train_Controller_HW_UI_PyFirmata import *
else:
    from .Tovarish_Belback_Jonah_Train_Controller_Testbenchv2 import *
    from .Tovarish_Belback_Jonah_Train_Controller_HW_UI_PyFirmata import *


#================================================================================
class TrainControler_HW_Container(QObject):

    # Signals
    new_train_values_signal = pyqtSignal(list, int)
    new_train_temp_signal = pyqtSignal(float, int)
    
    def __init__(self, Testbench=False):
        self.main_Driver_arr = []
        self.main_TrainModel_arr = [0,0,0,False,False,False,"00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"]
        self.outputs = []
        self.TB= Testbench
        self.cabin_temp=68
    
        self.trainCtrl = TC_HW_init(self.main_Driver_arr, self.main_TrainModel_arr, self.outputs, Testbench)
        #HW_UI_JEB382_PyFirmat(self.main_Driver_arr, self.main_TrainModel_arr, self.main_output_arr, Testbench)

    #================================================================================

    def show_ui(self):
        self.trainCtrl.updateTot()      
        
        
    #--------------------------------
    def update_train_controller_from_train_model(self, authority_safe_speed, track_info, train_info):
        print("Train Controller HW Container")
        #print(f"TrainC HW Container update1: {authority_safe_speed}")
        #print(f"TrainC HW Container update2: {track_info}")
        #print(f"TrainC HW Container update3: {train_info}")

        #authority_safe_speed_update
        self.trainCtrl.TrainModel_arr[2] = authority_safe_speed[0]#Auth
        self.trainCtrl.TrainModel_arr[1] = authority_safe_speed[1]#Cmd_Spd
        #track_info_update
        self.trainCtrl.TrainModel_arr[4] = track_info[0]#Track_Cicuit
        self.trainCtrl.TrainModel_arr[5] = track_info[1]#Aboveground
        self.trainCtrl.TrainModel_arr[6] = track_info[2]#beacon
        #train_info_update
        self.trainCtrl.TrainModel_arr[0] = train_info[0]#Actual_Spd
        self.trainCtrl.TrainModel_arr[3] = train_info[1]#Pass_ebrake

        self.trainCtrl.updateTot()
        return self.trainCtrl.output_arr








#================================================================================
# due to SystemTimeContainer library positioning, must test through total container
'''def TrainC_HW_main():
    system_time = SystemTimeContainer()
    trainctrlcntr = TrainControler_HW_Container(system_time)
    trainctrlcntr.show_ui()


if __name__ == "__main__":
    TrainC_HW_main()'''
