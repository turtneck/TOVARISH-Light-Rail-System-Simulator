from Tovarish_Belback_Jonah_Train_Controller_Testbench import TestBench_JEB382,pyqtloop
#from Tovarish_Belback_Jonah_Train_Controller_SW_UI import SW_UI_JEB382
#from Tovarish_Belback_Jonah_Train_Controller_HW_UI import HW_UI_JEB382
import threading

#threading of TB window not working


verbose = True

#UI_Ware=   0:HW, 1:SW
class TrainC_HW_JEB382():
    def __init__(self,numtrain,TrainModel_arr,UI_Ware):
        self.TrainModel_arr = TrainModel_arr
        #open UI/TB if first train
        if numtrain == 1:
            #Hardware/Software UI
            #if not UI_Ware: self.UI = SW_UI_JEB382
            #else: self.UI = HW_UI_JEB382
            
            #if TrainModel inputs not present, open testbench
            if not self.TrainModel_arr or len(self.TrainModel_arr)<10:
                self.TrainModel_arr = [0]*10
                global verbose
                if verbose:
                    TestBench = TestBench_JEB382(numtrain,self.TrainModel_arr,True)
                else: 
                    t1 = threading.Thread(target=pyqtloop, args=(numtrain,self.TrainModel_arr,verbose))
                    t1.daemon = True
                    t1.start()










#================================================================
if __name__ == "__main__":
    numtrain=1
    arr = None
    w = TrainC_HW_JEB382(numtrain, arr,True)