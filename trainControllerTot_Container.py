# container class for calling everything from train
import sys
import numpy

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import pyqtSlot, pyqtSignal, QObject

from Train_Controller_SW.trainControllerSWContainer import TrainControllerSWContainer
from Train_Controller_HW.trainControllerHWContainer import TrainControler_HW_Container
from Train_Controller_SW.trainControllerSWUI import UI
from SystemTime import SystemTime


# ================================================================================
class TrainController_Tot_Container(QObject):

    # Signals
    # new_train_values_signal = pyqtSignal(list, int)
    # new_train_temp_signal = pyqtSignal(float, int)
    # sam connect these signals to your respective update train model values command

    def __init__(self):
        super().__init__()

        self.ctrl_list = []
        self.HW_index = None  # index for future utility in case of handling recovery of deleted HW Controller
        self.SWuiExists = False

        if len(self.ctrl_list) > 1:
            self.swUI = UI(self.ctrl_list)
            print("train controller tot container.py: made sw ui")

    # ================================================================================
    # return HW/SW Container
    def new_train_controller(self):
        #print("AHHHHHHHHHHHHHHHH",self.HW_index)
        
        if self.HW_index or self.HW_index == 0:
            trainCtrl = TrainControllerSWContainer()
            #self.new_train_controller_signal.emit(trainCtrl)
            print("train controller tot container.py: software train controller made")
        else:
            self.HW_index = len(self.ctrl_list)
            trainCtrl = TrainControler_HW_Container(True)
            print("train controller tot container.py: hardware train controller made")
        self.ctrl_list.append(trainCtrl)
        self.add_to_list()
        return trainCtrl

    # gonna need a show ui method for the list of sw controllers
    # not sure how we will want to handle the hw ui though...

    # like this maybe ? vvv
    def show_hwui(self):
        print(self.HW_index)
        if self.HW_index or self.HW_index==0:
            self.ctrl_list[self.HW_index].show_ui()
        else:
            print("train controller tot container.py: WARNING: TrainController_Tot_Container: show_hwui without HW Controller")

    def show_swui(self):
        app = QApplication.instance()

        if app is None:
            app = QApplication([])

        self.swUI = UI(self.ctrl_list)
        self.swUI.closed.connect(self.sw_ui_state)

        self.swUI.show()
        self.SWuiExists = True
        # self.ui.refreshengine()

        app.exec()

    def add_to_list(self):
        if self.SWuiExists:
            self.swUI.addtrain(self.ctrl_list)
        pass

    @pyqtSlot(bool)
    def sw_ui_state(self, value):
        self.SWuiExists = value
        print(f'train controller tot container.py: software ui state: {self.SWuiExists}')


# ================================================================================
def TrainC_main():
    trainctrlcntr = TrainController_Tot_Container()
    cntrl = trainctrlcntr.new_train_controller()  # removed (type) as parameter
    trainctrlcntr.show_hwui()
    # cntrl = trainctrlcntr.new_train_controller()  # removed (type) as parameter
    # cntrl = trainctrlcntr.new_train_controller()  # removed (type) as parameter
    # cntrl = trainctrlcntr.new_train_controller()  # removed (type) as parameter
    # trainctrlcntr.show_swui()
    '''while True:
        cntrl.show_ui()'''


if __name__ == "__main__":
    # system_time = SystemTimeContainer()
    TrainC_main()
