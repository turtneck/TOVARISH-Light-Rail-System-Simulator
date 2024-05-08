import os, sys, time, datetime, shutil
#print(f"FILE:\t\t<{__file__[-10:-3]}>")
#print(f"FILE2:\t\t<{sys.argv[0][-10:-3]}>")

from Tovarish_Belback_Jonah_Train_Controller_Testbenchv2 import *
from Tovarish_Belback_Jonah_Train_Controller_HW_UI_PyFirmata import *


#================================================================================
#testing func
def PTSD_test(file, title_str,variable,expected,perc=None,Controller=None):
    #float
    if perc:
        file.write("\n-------------\n")
        test = (expected * (1 + (perc / 100)) >= variable >= expected * (1 - (perc / 100)))
        file.write(f"{title_str}: <{'PASS' if test else 'FAIL'}>\n")
        file.write(f"REAL:\t<{variable}>\t\tGOAL:\t<{expected}> *<{perc}>% (<{expected*(1+(perc/100))}>,<{expected*(1-(perc/100))}>)\n")
        file.write(f"ERR:\t<{variable - expected}>\n")
    #other
    else:
        file.write("\n-------------\n")
        test = ( variable == expected )        
        file.write(f"{title_str}: <{'PASS' if test else 'FAIL'}>\n")
        file.write(f"REAL:\t<{variable}>\t\tGOAL:\t<{expected}>\n")
    
    if Controller:
        file.write(f"Driver TrainC #1:\t{Controller.Driver_arr}\t{'AUTO' if not Controller.Mode else 'MANUAL'}\n")
        file.write(f"TrainModel TrainC #1:\t{Controller.TrainModel_arr} {'AUTO' if not Controller.Mode else 'MANUAL'}\n")
        file.write(f"Output TrainC #1:\t{Controller.output_arr}\t{'AUTO' if not Controller.Mode else 'MANUAL'}\n")
        
    return test



#================================================================================
#get testing folder
def get_testing_folder():
    print("================================================================================")
    print("\n\n[!!!!!!!] TESTING:\t get_testing_folder")
    
    #reset log folder for todays date
    dir_path = os.path.dirname(os.path.realpath(__file__))
    print(f"DIRECTORY:\t\t{dir_path}>")
    
    if os.path.exists(dir_path+'\Testlogs'):
        #folder path and name
        print(f"TIME:\t\t<{str(datetime.datetime.now())[:10]}>")
        testing_dir = f"{dir_path}\Testlogs\{str(datetime.datetime.now())[:10]}"
        print(f"TESTING DIRECTORY:\t\t<{testing_dir}>")
        
        #deleting folder if it exists
        if os.path.exists( testing_dir ):
            print(f"ATTENTION!!!!!!!!!!!!!!!!!!!\nLOG FOLDER ALREADY EXISTS\nDELETE?: {testing_dir}........")
            inp = input("y/n: ")
            if inp.lower() in ["n","no"]:
                raise TypeError("TRAIN CONTROLLER HW TESTING:\t\tNO DELETION")
            elif inp.lower() in ["y","ye","yes"]:
                print("DELETING...")
                shutil.rmtree( testing_dir )
            else:
                raise TypeError("TRAIN CONTROLLER HW TESTING:\t\tINVALID SELECTION")
        
        #remake folder    
        os.makedirs(testing_dir)
        print("DIRECTORY MADE")
    else:
        raise TypeError("TRAIN CONTROLLER HW TESTING:\t\tNO Testlogs DIRECTORY")
    
    return testing_dir



#================================================================================
#Passenger Break enables eBrake
def pass_ebreak_enable(folder):
    #prints, prep log
    print("================================================================================")
    print("\n[!!!!!!!] TESTING:\t 00pass_ebreak_enable")
    print(f"file:\t\t{folder}/00pass_ebreak_enable.txt")
    file = open(f"{folder}/00pass_ebreak_enable.txt", 'w')
    file.write("Hi\n")
    
    #----------------------------------------------
    #making controller
    main_TrainModel_arr = [0,0,0,False,False,False,"0"*128]
    main_output_arr = []
    main_Driver_arr = []
    
    try: it = util.Iterator(board); it.start()
    except (Exception,): print("No Train Controller HW detected: util.Iterator")
    
    trainCtrl = HW_UI_JEB382_PyFirmat(main_Driver_arr, main_TrainModel_arr, main_output_arr)
    
    #----------------------------------------------
    #Testing
    Endcase = True
    
    #-----
    #init
    Endcase *= PTSD_test(file, "A: PASSENGER EBRAKE: CHANGE0", trainCtrl.TrainModel_arr[3], False)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: PASSENGER EBRAKE: INIT", trainCtrl.output_arr[3], False, Controller=trainCtrl)
    
    #-----
    #on
    trainCtrl.TrainModel_arr[3] = True #passenger brake
    Endcase *= PTSD_test(file, "A: PASSENGER EBRAKE: CHANGE1", trainCtrl.TrainModel_arr[3], True)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: PASSENGER EBRAKE: ENABLED", trainCtrl.output_arr[3], True, Controller=trainCtrl)
    
    #-----
    #off
    trainCtrl.TrainModel_arr[3] = False #passenger brake
    Endcase *= PTSD_test(file, "A: PASSENGER EBRAKE: CHANGE2", trainCtrl.TrainModel_arr[3], False)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: PASSENGER EBRAKE: REMOVED", trainCtrl.output_arr[3], False, Controller=trainCtrl)
    
    #-----
    #on, manual
    trainCtrl.TrainModel_arr[3] = True #passenger brake
    Endcase *= PTSD_test(file, "A: PASSENGER EBRAKE: CHANGE3", trainCtrl.TrainModel_arr[3], True)
    trainCtrl.Mode = True
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "M: PASSENGER EBRAKE: ENABLED", trainCtrl.output_arr[3], True, Controller=trainCtrl)
    
    
    
    
    
    #----------------------------------------------
    #Endcase
    file.write("\n-------------\n")
    file.write(f"[!!!!!] 00pass_ebreak_enable: <{'PASS' if Endcase else 'FAIL'}>\n")

    print("\n-------------")
    print(f"[!!!!!] 00pass_ebreak_enable: <{'PASS' if Endcase else 'FAIL'}>")
    return Endcase



#----------------------------------------------
#Driver can disable Passenger Brake's effect in any mode
def driver_disable_pass(folder):
    #prints, prep log
    print("================================================================================")
    print("\n[!!!!!!!] TESTING:\t 01driver_disable_pass")
    print(f"file:\t\t{folder}/01driver_disable_pass.txt")
    file = open(f"{folder}/01driver_disable_pass.txt", 'w')
    file.write("Hi\n")
    
    #----------------------------------------------
    #making controller
    main_TrainModel_arr = [0,0,0,False,False,False,"0"*128]
    main_output_arr = []
    main_Driver_arr = []
    
    try: it = util.Iterator(board); it.start()
    except (Exception,): print("No Train Controller HW detected: util.Iterator")
    
    trainCtrl = HW_UI_JEB382_PyFirmat(main_Driver_arr, main_TrainModel_arr, main_output_arr)
    
    #----------------------------------------------
    #Testing
    Endcase = True
    
    #Auto
    #-----
    #false,false(init):true
    Endcase *= PTSD_test(file, "A: PASSENGER EBRAKE: CHANGE0", trainCtrl.TrainModel_arr[3], False)
    Endcase *= PTSD_test(file, "A: DISABLE PASSENGER: CHANGE0", trainCtrl.Driver_arr[10], False)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: DISABLE PASSENGER: false,false", trainCtrl.output_arr[3], False, Controller=trainCtrl)
    
    #-----
    #true,false:true
    trainCtrl.TrainModel_arr[3] = True #passenger brake
    Endcase *= PTSD_test(file, "A: PASSENGER EBRAKE: CHANGE1", trainCtrl.TrainModel_arr[3], True)
    Endcase *= PTSD_test(file, "A: DISABLE PASSENGER: CHANGE0", trainCtrl.Driver_arr[10], False)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: DISABLE PASSENGER: true,false", trainCtrl.output_arr[3], True, Controller=trainCtrl)
    
    #-----
    #true,true:false
    trainCtrl.Driver_arr[10] = True #disable passenger brake
    Endcase *= PTSD_test(file, "A: PASSENGER EBRAKE: CHANGE1", trainCtrl.TrainModel_arr[3], True)
    Endcase *= PTSD_test(file, "A: DISABLE PASSENGER: CHANGE1", trainCtrl.Driver_arr[10], True)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: DISABLE PASSENGER: true,true", trainCtrl.output_arr[3], False, Controller=trainCtrl)
    
    #-----
    #false,true:false
    trainCtrl.TrainModel_arr[3] = False #passenger brake
    Endcase *= PTSD_test(file, "A: PASSENGER EBRAKE: CHANGE2", trainCtrl.TrainModel_arr[3], False)
    Endcase *= PTSD_test(file, "A: DISABLE PASSENGER: CHANGE1", trainCtrl.Driver_arr[10], True)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: DISABLE PASSENGER: false,true", trainCtrl.output_arr[3], False, Controller=trainCtrl)
    
    
    #=====================
    #manual
    trainCtrl.Mode = True
    trainCtrl.TrainModel_arr[3] = False #passenger brake
    trainCtrl.Driver_arr[10] = False #disable passenger brake
    Endcase *= PTSD_test(file, "M: PASSENGER EBRAKE: CHANGE0", trainCtrl.TrainModel_arr[3], False)
    Endcase *= PTSD_test(file, "M: DISABLE PASSENGER: CHANGE0", trainCtrl.Driver_arr[10], False)
    #-----
    #false,false:true
    Endcase *= PTSD_test(file, "M: PASSENGER EBRAKE: CHANGE0", trainCtrl.TrainModel_arr[3], False)
    Endcase *= PTSD_test(file, "M: DISABLE PASSENGER: CHANGE0", trainCtrl.Driver_arr[10], False)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "M: DISABLE PASSENGER: false,false", trainCtrl.output_arr[3], False, Controller=trainCtrl)
    
    #-----
    #true,false:true
    trainCtrl.TrainModel_arr[3] = True #passenger brake
    Endcase *= PTSD_test(file, "M: PASSENGER EBRAKE: CHANGE1", trainCtrl.TrainModel_arr[3], True)
    Endcase *= PTSD_test(file, "M: DISABLE PASSENGER: CHANGE0", trainCtrl.Driver_arr[10], False)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "M: PASSENGER EBRAKE: true,false", trainCtrl.output_arr[3], True, Controller=trainCtrl)
    
    #-----
    #true,true:false
    trainCtrl.Driver_arr[10] = True #disable passenger brake
    Endcase *= PTSD_test(file, "M: PASSENGER EBRAKE: CHANGE1", trainCtrl.TrainModel_arr[3], True)
    Endcase *= PTSD_test(file, "M: DISABLE PASSENGER: CHANGE1", trainCtrl.Driver_arr[10], True)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "M: DISABLE PASSENGER: true,true", trainCtrl.output_arr[3], False, Controller=trainCtrl)
    
    #-----
    #false,true:false
    trainCtrl.TrainModel_arr[3] = False #passenger brake
    Endcase *= PTSD_test(file, "M: PASSENGER EBRAKE: CHANGE2", trainCtrl.TrainModel_arr[3], False)
    Endcase *= PTSD_test(file, "M: DISABLE PASSENGER: CHANGE1", trainCtrl.Driver_arr[10], True)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "M: PASSENGER EBRAKE: false,true", trainCtrl.output_arr[3], False, Controller=trainCtrl)
    
    
    
    
    
    #----------------------------------------------
    #Endcase
    file.write("\n-------------\n")
    file.write(f"[!!!!!] 01driver_disable_pass: <{'PASS' if Endcase else 'FAIL'}>\n")

    print("\n-------------")
    print(f"[!!!!!] 01driver_disable_pass: <{'PASS' if Endcase else 'FAIL'}>")
    return Endcase


#----------------------------------------------
#Driver can enable ebrake in any mode
def driver_ebreak_enable(folder):
    #prints, prep log
    print("================================================================================")
    print("\n[!!!!!!!] TESTING:\t 02driver_ebreak_enable")
    print(f"file:\t\t{folder}/02driver_ebreak_enable.txt")
    file = open(f"{folder}/02driver_ebreak_enable.txt", 'w')
    file.write("Hi\n")
    
    #----------------------------------------------
    #making controller
    main_TrainModel_arr = [1,1,1,False,False,False,"0"*128]#need moving
    main_output_arr = []
    main_Driver_arr = []
    
    try: it = util.Iterator(board); it.start()
    except (Exception,): print("No Train Controller HW detected: util.Iterator")
    
    trainCtrl = HW_UI_JEB382_PyFirmat(main_Driver_arr, main_TrainModel_arr, main_output_arr)
    
    #----------------------------------------------
    #Testing
    Endcase = True
    
    #-----
    #auto
    #init
    Endcase *= PTSD_test(file, "A: DRIVER EBRAKE: CHANGE0", trainCtrl.Driver_arr[8], False)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: DRIVER EBRAKE: INIT", trainCtrl.output_arr[3], False, Controller=trainCtrl)
    
    #-----
    #on
    trainCtrl.Driver_arr[8] = True #ebrake
    Endcase *= PTSD_test(file, "A: DRIVER EBRAKE: CHANGE1", trainCtrl.Driver_arr[8], True)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: DRIVER EBRAKE: ENABLE", trainCtrl.output_arr[3], True, Controller=trainCtrl)
    
    #-----
    #manual
    #off
    trainCtrl.Driver_arr[8] = False #ebrake
    Endcase *= PTSD_test(file, "A: DRIVER EBRAKE: CHANGE2", trainCtrl.Driver_arr[8], False)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: DRIVER EBRAKE: REMOVED", trainCtrl.output_arr[3], False, Controller=trainCtrl)
    
    #-----
    #on, manual
    trainCtrl.Driver_arr[8] = True #ebrake
    Endcase *= PTSD_test(file, "A: DRIVER EBRAKE: CHANGE3", trainCtrl.Driver_arr[8], True)
    trainCtrl.Mode = True
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "M: DRIVER EBRAKE: ENABLE", trainCtrl.output_arr[3], True, Controller=trainCtrl)
    
    
    
    
    
    #----------------------------------------------
    #Endcase
    file.write("\n-------------\n")
    file.write(f"[!!!!!] 02driver_ebreak_enable: <{'PASS' if Endcase else 'FAIL'}>\n")

    print("\n-------------")
    print(f"[!!!!!] 02driver_ebreak_enable: <{'PASS' if Endcase else 'FAIL'}>")
    return Endcase


#----------------------------------------------
#Driver can enable service brake in manual mode only
def driver_sbreak_enable(folder):
    #prints, prep log
    print("================================================================================")
    print("\n[!!!!!!!] TESTING:\t 03driver_sbreak_enable")
    print(f"file:\t\t{folder}/03driver_sbreak_enable.txt")
    file = open(f"{folder}/03driver_sbreak_enable.txt", 'w')
    file.write("Hi\n")
    
    #----------------------------------------------
    #making controller
    main_TrainModel_arr = [1,1,1,False,False,False,"0"*128]#need moving
    main_output_arr = []
    main_Driver_arr = []
    
    try: it = util.Iterator(board); it.start()
    except (Exception,): print("No Train Controller HW detected: util.Iterator")
    
    trainCtrl = HW_UI_JEB382_PyFirmat(main_Driver_arr, main_TrainModel_arr, main_output_arr)
    
    #----------------------------------------------
    #Testing
    Endcase = True
    
    #-----
    #auto
    #init
    Endcase *= PTSD_test(file, "A: DRIVER SBRAKE: CHANGE0", trainCtrl.Driver_arr[9], False)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: DRIVER SBRAKE: INIT", trainCtrl.output_arr[2], False, Controller=trainCtrl)
    
    #-----
    #on
    trainCtrl.Driver_arr[9] = True #sbrake
    Endcase *= PTSD_test(file, "A: DRIVER SBRAKE: CHANGE1", trainCtrl.Driver_arr[9], True)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: DRIVER SBRAKE: ENABLE IN AUTO", trainCtrl.output_arr[2], False, Controller=trainCtrl)
    
    #-----
    #manual
    #off
    trainCtrl.Driver_arr[9] = False #sbrake
    trainCtrl.Mode = True #mode
    Endcase *= PTSD_test(file, "A: DRIVER SBRAKE: CHANGE2", trainCtrl.Driver_arr[9], False)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: DRIVER SBRAKE: REMOVED", trainCtrl.output_arr[2], False, Controller=trainCtrl)
    
    #-----
    #on, manual
    trainCtrl.Driver_arr[9] = True #sbrake
    Endcase *= PTSD_test(file, "A: DRIVER SBRAKE: CHANGE3", trainCtrl.Driver_arr[9], True)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "M: DRIVER SBRAKE: ENABLE", trainCtrl.output_arr[2], True, Controller=trainCtrl)
    
    
    
    
    
    #----------------------------------------------
    #Endcase
    file.write("\n-------------\n")
    file.write(f"[!!!!!] 03driver_sbreak_enable: <{'PASS' if Endcase else 'FAIL'}>\n")

    print("\n-------------")
    print(f"[!!!!!] 03driver_sbreak_enable: <{'PASS' if Endcase else 'FAIL'}>")
    return Endcase


#----------------------------------------------
#Driver can change door state when train is stopped in manual mode
def driver_door(folder):
    #prints, prep log
    print("================================================================================")
    print("\n[!!!!!!!] TESTING:\t 04driver_door")
    print(f"file:\t\t{folder}/04driver_door.txt")
    file = open(f"{folder}/04driver_door.txt", 'w')
    file.write("Hi\n")
    
    #----------------------------------------------
    #making controller
    main_TrainModel_arr = [0,0,0,False,False,False,"0"*128]
    main_output_arr = []
    main_Driver_arr = []
    
    try: it = util.Iterator(board); it.start()
    except (Exception,): print("No Train Controller HW detected: util.Iterator")
    
    trainCtrl = HW_UI_JEB382_PyFirmat(main_Driver_arr, main_TrainModel_arr, main_output_arr)
    
    #----------------------------------------------
    #Testing
    Endcase = True
    
    #-----
    #auto
    #off
    trainCtrl.Driver_arr[6] = False
    trainCtrl.Driver_arr[7] = False
    Endcase *= PTSD_test(file, "A: DRIVER L DOOR: INIT", trainCtrl.Driver_arr[6], False)
    Endcase *= PTSD_test(file, "A: DRIVER R DOOR: INIT", trainCtrl.Driver_arr[7], False)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: DOOR OUTPUT: INIT", trainCtrl.output_arr[4], 0)
    
    #-----
    #left on
    trainCtrl.Driver_arr[6] = True
    trainCtrl.Driver_arr[7] = False
    Endcase *= PTSD_test(file, "A: DRIVER L DOOR: LEFT", trainCtrl.Driver_arr[6], True)
    Endcase *= PTSD_test(file, "A: DRIVER R DOOR: LEFT", trainCtrl.Driver_arr[7], False)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: DOOR OUTPUT: LEFT", trainCtrl.output_arr[4], 0)
    
    #-----
    #right on
    trainCtrl.Driver_arr[6] = False
    trainCtrl.Driver_arr[7] = True
    Endcase *= PTSD_test(file, "A: DRIVER L DOOR: RIGHT", trainCtrl.Driver_arr[6], False)
    Endcase *= PTSD_test(file, "A: DRIVER R DOOR: RIGHT", trainCtrl.Driver_arr[7], True)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: DOOR OUTPUT: RIGHT", trainCtrl.output_arr[4], 0)
    
    #-----
    #both True
    trainCtrl.Driver_arr[6] = True
    trainCtrl.Driver_arr[7] = True
    Endcase *= PTSD_test(file, "A: DRIVER L DOOR: BOTH", trainCtrl.Driver_arr[6], True)
    Endcase *= PTSD_test(file, "A: DRIVER R DOOR: BOTH", trainCtrl.Driver_arr[7], True)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: DOOR OUTPUT: BOTH", trainCtrl.output_arr[4], 0)
    
    
    
    
    #-----------------
    #manual
    trainCtrl.Mode = True #mode
    #off
    trainCtrl.Driver_arr[6] = False
    trainCtrl.Driver_arr[7] = False
    Endcase *= PTSD_test(file, "M: DRIVER L DOOR: INIT", trainCtrl.Driver_arr[6], False)
    Endcase *= PTSD_test(file, "M: DRIVER R DOOR: INIT", trainCtrl.Driver_arr[7], False)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "M: DOOR OUTPUT: INIT", trainCtrl.output_arr[4], 0)
    
    #-----
    #left on
    trainCtrl.Driver_arr[6] = True
    trainCtrl.Driver_arr[7] = False
    Endcase *= PTSD_test(file, "M: DRIVER L DOOR: LEFT", trainCtrl.Driver_arr[6], True)
    Endcase *= PTSD_test(file, "M: DRIVER R DOOR: LEFT", trainCtrl.Driver_arr[7], False)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "M: DOOR OUTPUT: LEFT", trainCtrl.output_arr[4], 1)
    
    #-----
    #right on
    trainCtrl.Driver_arr[6] = False
    trainCtrl.Driver_arr[7] = True
    Endcase *= PTSD_test(file, "M: DRIVER L DOOR: RIGHT", trainCtrl.Driver_arr[6], False)
    Endcase *= PTSD_test(file, "M: DRIVER R DOOR: RIGHT", trainCtrl.Driver_arr[7], True)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "M: DOOR OUTPUT: RIGHT", trainCtrl.output_arr[4], 2)
    
    #-----
    #both on
    trainCtrl.Driver_arr[6] = True
    trainCtrl.Driver_arr[7] = True
    Endcase *= PTSD_test(file, "M: DRIVER L DOOR: BOTH", trainCtrl.Driver_arr[6], True)
    Endcase *= PTSD_test(file, "M: DRIVER R DOOR: BOTH", trainCtrl.Driver_arr[7], True)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "M: DOOR OUTPUT: BOTH", trainCtrl.output_arr[4], 3)
    
    
    
    
    #-----------------
    #moving
    trainCtrl.TrainModel_arr[0] = 1 #moving
    #off
    trainCtrl.Driver_arr[6] = False
    trainCtrl.Driver_arr[7] = False
    Endcase *= PTSD_test(file, "MOVING: DRIVER L DOOR: INIT", trainCtrl.Driver_arr[6], False)
    Endcase *= PTSD_test(file, "MOVING: DRIVER R DOOR: INIT", trainCtrl.Driver_arr[7], False)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "MOVING: DOOR OUTPUT: INIT", trainCtrl.output_arr[4], 0)
    
    #-----
    #left on
    trainCtrl.Driver_arr[6] = True
    trainCtrl.Driver_arr[7] = False
    Endcase *= PTSD_test(file, "MOVING: DRIVER L DOOR: LEFT", trainCtrl.Driver_arr[6], True)
    Endcase *= PTSD_test(file, "MOVING: DRIVER R DOOR: LEFT", trainCtrl.Driver_arr[7], False)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "MOVING: DOOR OUTPUT: LEFT", trainCtrl.output_arr[4], 0)
    
    #-----
    #right on
    trainCtrl.Driver_arr[6] = False
    trainCtrl.Driver_arr[7] = True
    Endcase *= PTSD_test(file, "MOVING: DRIVER L DOOR: RIGHT", trainCtrl.Driver_arr[6], False)
    Endcase *= PTSD_test(file, "MOVING: DRIVER R DOOR: RIGHT", trainCtrl.Driver_arr[7], True)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "MOVING: DOOR OUTPUT: RIGHT", trainCtrl.output_arr[4], 0)
    
    #-----
    #both on
    trainCtrl.Driver_arr[6] = True
    trainCtrl.Driver_arr[7] = True
    Endcase *= PTSD_test(file, "MOVING: DRIVER L DOOR: BOTH", trainCtrl.Driver_arr[6], True)
    Endcase *= PTSD_test(file, "MOVING: DRIVER R DOOR: BOTH", trainCtrl.Driver_arr[7], True)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "MOVING: DOOR OUTPUT: BOTH", trainCtrl.output_arr[4], 0)
    
    
    
    
    
    #----------------------------------------------
    #Endcase
    file.write("\n-------------\n")
    file.write(f"[!!!!!] 04driver_door: <{'PASS' if Endcase else 'FAIL'}>\n")

    print("\n-------------")
    print(f"[!!!!!] 04driver_door: <{'PASS' if Endcase else 'FAIL'}>")
    return Endcase


#----------------------------------------------
#TODO: BEACON ADDITION
#Train opens stationside door when train is stopped in auto mode
def train_door(folder):
    #prints, prep log
    print("================================================================================")
    print("\n[!!!!!!!] TESTING:\t 05train_door")
    print(f"file:\t\t{folder}/05train_door.txt")
    file = open(f"{folder}/05train_door.txt", 'w')
    file.write("Hi\n")
    
    #----------------------------------------------
    #making controller
    main_TrainModel_arr = [0,0,0,False,False,False,"0"*128]
    main_output_arr = []
    main_Driver_arr = []
    
    try: it = util.Iterator(board); it.start()
    except (Exception,): print("No Train Controller HW detected: util.Iterator")
    
    trainCtrl = HW_UI_JEB382_PyFirmat(main_Driver_arr, main_TrainModel_arr, main_output_arr)
    
    #----------------------------------------------
    #Testing
    Endcase = True
    
    
    
    
    
    #----------------------------------------------
    #Endcase
    file.write("\n-------------\n")
    file.write(f"[!!!!!] 05train_door: <{'PASS' if Endcase else 'FAIL'}>\n")

    print("\n-------------")
    print(f"[!!!!!] 05train_door: <{'PASS' if Endcase else 'FAIL'}>")
    return Endcase


#----------------------------------------------
#Driver can enable interior lights in manual when it is otherwise off
def driver_int_lights(folder):
    #prints, prep log
    print("================================================================================")
    print("\n[!!!!!!!] TESTING:\t 06driver_int_lights")
    print(f"file:\t\t{folder}/06driver_int_lights.txt")
    file = open(f"{folder}/06driver_int_lights.txt", 'w')
    file.write("Hi\n")
    
    #----------------------------------------------
    #making controller
    main_TrainModel_arr = [0,0,0,False,False,False,"0"*128]
    main_output_arr = []
    main_Driver_arr = []
    
    try: it = util.Iterator(board); it.start()
    except (Exception,): print("No Train Controller HW detected: util.Iterator")
    
    trainCtrl = HW_UI_JEB382_PyFirmat(main_Driver_arr, main_TrainModel_arr, main_output_arr)
    
    #----------------------------------------------
    #Testing
    Endcase = True
    
    #-----
    #auto
    #off
    trainCtrl.Driver_arr[3] = False
    Endcase *= PTSD_test(file, "A: DRIVER INT LIGHT: INIT", trainCtrl.Driver_arr[3], False)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: INT LIGHT: INIT", trainCtrl.output_arr[6], False)
    
    #-----
    #on
    trainCtrl.Driver_arr[3] = True
    Endcase *= PTSD_test(file, "A: DRIVER INT LIGHT: CHANGE1", trainCtrl.Driver_arr[3], True)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: INT LIGHT: CHANGE1", trainCtrl.output_arr[6], False)
    
    
    
    
    #-----------------
    #manual
    trainCtrl.Mode = True #mode
    #off
    trainCtrl.Driver_arr[3] = False
    Endcase *= PTSD_test(file, "M: DRIVER INT LIGHT: INIT", trainCtrl.Driver_arr[3], False)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "M: INT LIGHT: INIT", trainCtrl.output_arr[6], False)
    
    #-----
    #on
    trainCtrl.Driver_arr[3] = True
    Endcase *= PTSD_test(file, "M: DRIVER INT LIGHT: CHANGE1", trainCtrl.Driver_arr[3], True)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "M: INT LIGHT: CHANGE1", trainCtrl.output_arr[6], True)
    
    
    
    
    
    #----------------------------------------------
    #Endcase
    file.write("\n-------------\n")
    file.write(f"[!!!!!] 06driver_int_lights: <{'PASS' if Endcase else 'FAIL'}>\n")

    print("\n-------------")
    print(f"[!!!!!] 06driver_int_lights: <{'PASS' if Endcase else 'FAIL'}>")
    return Endcase


#----------------------------------------------
#Driver can enable exterior lights in manual mode when it is otherwise off.
def driver_ext_lights(folder):
    #prints, prep log
    print("================================================================================")
    print("\n[!!!!!!!] TESTING:\t 07driver_ext_lights")
    print(f"file:\t\t{folder}/07driver_ext_lights.txt")
    file = open(f"{folder}/07driver_ext_lights.txt", 'w')
    file.write("Hi\n")
    
    #----------------------------------------------
    #making controller
    main_TrainModel_arr = [0,0,0,False,False,False,"0"*128]
    main_output_arr = []
    main_Driver_arr = []
    
    try: it = util.Iterator(board); it.start()
    except (Exception,): print("No Train Controller HW detected: util.Iterator")
    
    trainCtrl = HW_UI_JEB382_PyFirmat(main_Driver_arr, main_TrainModel_arr, main_output_arr)
    
    #----------------------------------------------
    #Testing
    Endcase = True
    
    #-----
    #auto
    #off
    trainCtrl.Driver_arr[4] = False
    Endcase *= PTSD_test(file, "A: DRIVER EXT LIGHT: INIT", trainCtrl.Driver_arr[4], False)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: EXT LIGHT: INIT", trainCtrl.output_arr[7], False)
    
    #-----
    #on
    trainCtrl.Driver_arr[4] = True
    Endcase *= PTSD_test(file, "A: DRIVER EXT LIGHT: CHANGE1", trainCtrl.Driver_arr[4], True)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: EXT LIGHT: CHANGE1", trainCtrl.output_arr[7], False)
    
    
    
    
    #-----------------
    #manual
    trainCtrl.Mode = True #mode
    #off
    trainCtrl.Driver_arr[4] = False
    Endcase *= PTSD_test(file, "M: DRIVER EXT LIGHT: INIT", trainCtrl.Driver_arr[4], False)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "M: EXT LIGHT: INIT", trainCtrl.output_arr[7], False)
    
    #-----
    #on
    trainCtrl.Driver_arr[4] = True
    Endcase *= PTSD_test(file, "M: DRIVER EXT LIGHT: CHANGE1", trainCtrl.Driver_arr[4], True)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "M: EXT LIGHT: CHANGE1", trainCtrl.output_arr[7], True)
    
    
    
    
    
    #----------------------------------------------
    #Endcase
    file.write("\n-------------\n")
    file.write(f"[!!!!!] 07driver_ext_lights: <{'PASS' if Endcase else 'FAIL'}>\n")

    print("\n-------------")
    print(f"[!!!!!] 07driver_ext_lights: <{'PASS' if Endcase else 'FAIL'}>")
    return Endcase


#----------------------------------------------
#Power is zero without authority or commanded speed
#Power is also zero when matching actual speed
def zero_pow(folder):
    #prints, prep log
    print("================================================================================")
    print("\n[!!!!!!!] TESTING:\t 08zero_pow_auth")
    print(f"file:\t\t{folder}/08zero_pow_auth.txt")
    file = open(f"{folder}/08zero_pow_auth.txt", 'w')
    file.write("Hi\n")
    
    #----------------------------------------------
    #making controller
    main_TrainModel_arr = [0,0,0,False,False,False,"0"*128]
    main_output_arr = []
    main_Driver_arr = []
    
    try: it = util.Iterator(board); it.start()
    except (Exception,): print("No Train Controller HW detected: util.Iterator")
    
    trainCtrl = HW_UI_JEB382_PyFirmat(main_Driver_arr, main_TrainModel_arr, main_output_arr)
    
    #----------------------------------------------
    #Testing
    Endcase = True
    
    #-----
    #auto
    #0,0,0
    Endcase *= PTSD_test(file, "A: ACTSPD: INIT", trainCtrl.TrainModel_arr[0], 0)
    Endcase *= PTSD_test(file, "A: CMDSPD: INIT", trainCtrl.TrainModel_arr[1], 0)
    Endcase *= PTSD_test(file, "A: AUTH: INIT",   trainCtrl.TrainModel_arr[2], 0)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: POWER: 0,0,0", trainCtrl.output_arr[1], 0)
    
    #-----
    #1,0,0
    trainCtrl.TrainModel_arr[0] = 1
    Endcase *= PTSD_test(file, "A: ACTSPD: 1", trainCtrl.TrainModel_arr[0], 1)
    Endcase *= PTSD_test(file, "A: CMDSPD: 0", trainCtrl.TrainModel_arr[1], 0)
    Endcase *= PTSD_test(file, "A: AUTH: 0",   trainCtrl.TrainModel_arr[2], 0)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: POWER: 1,0,0", trainCtrl.output_arr[1], 0)
    
    #-----
    #1,1,0
    trainCtrl.TrainModel_arr[1] = 1
    Endcase *= PTSD_test(file, "A: ACTSPD: 1", trainCtrl.TrainModel_arr[0], 1)
    Endcase *= PTSD_test(file, "A: CMDSPD: 1", trainCtrl.TrainModel_arr[1], 1)
    Endcase *= PTSD_test(file, "A: AUTH: 0",   trainCtrl.TrainModel_arr[2], 0)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: POWER: 1,0,0", trainCtrl.output_arr[1], 0)
    
    #-----
    #1,0,1
    trainCtrl.TrainModel_arr[1] = 0
    trainCtrl.TrainModel_arr[2] = 1
    Endcase *= PTSD_test(file, "A: ACTSPD: 1", trainCtrl.TrainModel_arr[0], 1)
    Endcase *= PTSD_test(file, "A: CMDSPD: 0", trainCtrl.TrainModel_arr[1], 0)
    Endcase *= PTSD_test(file, "A: AUTH: 1",   trainCtrl.TrainModel_arr[2], 1)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: POWER: 1,0,1", trainCtrl.output_arr[1], 0)
    
    #-----
    print("trouble:A")
    #1,1,1: MATCH
    trainCtrl.TrainModel_arr[0] = 8
    trainCtrl.TrainModel_arr[1] = 8
    Endcase *= PTSD_test(file, "A: ACTSPD: 1", trainCtrl.TrainModel_arr[0], 8)
    Endcase *= PTSD_test(file, "A: CMDSPD: 1", trainCtrl.TrainModel_arr[1], 8)
    Endcase *= PTSD_test(file, "A: AUTH: 1",   trainCtrl.TrainModel_arr[2], 1)
    time.sleep(1)#necessary for stable testing
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: POWER: CMD SPD MATCH ACTUAL", trainCtrl.output_arr[1], 0)
    file.write("TRAIN"+str(trainCtrl.TrainModel_arr)+"\n")
    file.write("OUTPUT"+str(trainCtrl.output_arr)+"\n")
    
    #-----
    #1,2,1
    trainCtrl.TrainModel_arr[0] = 1
    trainCtrl.TrainModel_arr[1] = 2
    Endcase *= PTSD_test(file, "A: ACTSPD: 1", trainCtrl.TrainModel_arr[0], 1)
    Endcase *= PTSD_test(file, "A: CMDSPD: 2", trainCtrl.TrainModel_arr[1], 2)
    Endcase *= PTSD_test(file, "A: AUTH: 1",   trainCtrl.TrainModel_arr[2], 1)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: POWER: 1,2,1", trainCtrl.output_arr[1]>0, True)
    file.write("TRAIN"+str(trainCtrl.TrainModel_arr)+"\n")
    file.write("OUTPUT"+str(trainCtrl.output_arr)+"\n")
    
    #-----
    #0,1,1
    trainCtrl.TrainModel_arr[0] = 0
    trainCtrl.TrainModel_arr[1] = 1
    Endcase *= PTSD_test(file, "A: ACTSPD: 0", trainCtrl.TrainModel_arr[0], 0)
    Endcase *= PTSD_test(file, "A: CMDSPD: 1", trainCtrl.TrainModel_arr[1], 1)
    Endcase *= PTSD_test(file, "A: AUTH: 1",   trainCtrl.TrainModel_arr[2], 1)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: POWER: 0,1,1", trainCtrl.output_arr[1]>0, True)
    file.write("TRAIN"+str(trainCtrl.TrainModel_arr)+"\n")
    file.write("OUTPUT"+str(trainCtrl.output_arr)+"\n")
    
    #-----
    #0,1,0
    trainCtrl.TrainModel_arr[2] = 0
    Endcase *= PTSD_test(file, "A: ACTSPD: 0", trainCtrl.TrainModel_arr[0], 0)
    Endcase *= PTSD_test(file, "A: CMDSPD: 1", trainCtrl.TrainModel_arr[1], 1)
    Endcase *= PTSD_test(file, "A: AUTH: 0",   trainCtrl.TrainModel_arr[2], 0)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: POWER: 0,1,1", trainCtrl.output_arr[1]>0, 0)
    file.write("TRAIN"+str(trainCtrl.TrainModel_arr)+"\n")
    file.write("OUTPUT"+str(trainCtrl.output_arr)+"\n")
    
    #-----
    #0,0,1
    trainCtrl.TrainModel_arr[1] = 0
    trainCtrl.TrainModel_arr[2] = 1
    Endcase *= PTSD_test(file, "A: ACTSPD: 0", trainCtrl.TrainModel_arr[0], 0)
    Endcase *= PTSD_test(file, "A: CMDSPD: 0", trainCtrl.TrainModel_arr[1], 0)
    Endcase *= PTSD_test(file, "A: AUTH: 1",   trainCtrl.TrainModel_arr[2], 1)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: POWER: 0,1,1", trainCtrl.output_arr[1], 0)
    
    
    
    
    #-----------------
    #manual
    trainCtrl.Mode = True #mode
    trainCtrl.TrainModel_arr[0] = 0 #reset
    trainCtrl.TrainModel_arr[1] = 0
    trainCtrl.TrainModel_arr[2] = 0
    
    #-----
    #commanded speed switch off
    trainCtrl.Driver_arr[2] = 5
    trainCtrl.TrainModel_arr[1] = 2
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "M: CMD SPD IS MANUAL", trainCtrl.output_arr[0], 5)
    
    #-----
    #reset
    trainCtrl.TrainModel_arr[0] = 0
    trainCtrl.TrainModel_arr[1] = 0
    trainCtrl.TrainModel_arr[2] = 0
    trainCtrl.Driver_arr[2] = 0
    
    #-----
    #0,0,0
    Endcase *= PTSD_test(file, "M: ACTSPD: INIT", trainCtrl.TrainModel_arr[0], 0)
    Endcase *= PTSD_test(file, "M: CMDSPD: INIT", trainCtrl.Driver_arr[2], 0)
    Endcase *= PTSD_test(file, "M: AUTH: INIT",   trainCtrl.TrainModel_arr[2], 0)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "M: POWER: 0,0,0", trainCtrl.output_arr[1], 0)
    
    #-----
    #1,0,0
    trainCtrl.TrainModel_arr[0] = 1
    Endcase *= PTSD_test(file, "M: ACTSPD: 1", trainCtrl.TrainModel_arr[0], 1)
    Endcase *= PTSD_test(file, "M: CMDSPD: 0", trainCtrl.Driver_arr[2], 0)
    Endcase *= PTSD_test(file, "M: AUTH: 0",   trainCtrl.TrainModel_arr[2], 0)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "M: POWER: 1,0,0", trainCtrl.output_arr[1], 0)
    
    #-----
    #1,1,0
    trainCtrl.Driver_arr[2] = 1
    Endcase *= PTSD_test(file, "M: ACTSPD: 1", trainCtrl.TrainModel_arr[0], 1)
    Endcase *= PTSD_test(file, "M: CMDSPD: 1", trainCtrl.Driver_arr[2], 1)
    Endcase *= PTSD_test(file, "M: AUTH: 0",   trainCtrl.TrainModel_arr[2], 0)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "M: POWER: 1,0,0", trainCtrl.output_arr[1], 0)
    
    #-----
    #1,0,1
    trainCtrl.Driver_arr[2] = 0
    trainCtrl.TrainModel_arr[2] = 1
    Endcase *= PTSD_test(file, "M: ACTSPD: 1", trainCtrl.TrainModel_arr[0], 1)
    Endcase *= PTSD_test(file, "M: CMDSPD: 0", trainCtrl.Driver_arr[2], 0)
    Endcase *= PTSD_test(file, "M: AUTH: 1",   trainCtrl.TrainModel_arr[2], 1)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "M: POWER: 1,0,1", trainCtrl.output_arr[1], 0)
    
    #-----
    print("trouble:M")
    #1,1,1: MATCH
    trainCtrl.TrainModel_arr[0] = 8
    trainCtrl.Driver_arr[2] = 8
    Endcase *= PTSD_test(file, "M: ACTSPD: 1", trainCtrl.TrainModel_arr[0], 8)
    Endcase *= PTSD_test(file, "M: CMDSPD: 1", trainCtrl.Driver_arr[2], 8)
    Endcase *= PTSD_test(file, "M: AUTH: 1",   trainCtrl.TrainModel_arr[2], 1)
    time.sleep(1)#necessary for stable testing
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "M: POWER: CMD SPD MATCH ACTUAL", trainCtrl.output_arr[1], 0)
    file.write("TRAIN"+str(trainCtrl.Driver_arr)+"\n")
    file.write("TRAIN"+str(trainCtrl.TrainModel_arr)+"\n")
    file.write("OUTPUT"+str(trainCtrl.output_arr)+"\n")
    
    #-----
    #1,2,1
    trainCtrl.TrainModel_arr[0] = 1
    trainCtrl.Driver_arr[2] = 2
    Endcase *= PTSD_test(file, "M: ACTSPD: 1", trainCtrl.TrainModel_arr[0], 1)
    Endcase *= PTSD_test(file, "M: CMDSPD: 2", trainCtrl.Driver_arr[2], 2)
    Endcase *= PTSD_test(file, "M: AUTH: 1",   trainCtrl.TrainModel_arr[2], 1)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "M: POWER: 1,2,1", trainCtrl.output_arr[1]>0, True)
    file.write("TRAIN"+str(trainCtrl.Driver_arr)+"\n")
    file.write("TRAIN"+str(trainCtrl.TrainModel_arr)+"\n")
    file.write("OUTPUT"+str(trainCtrl.output_arr)+"\n")
    
    #-----
    #0,1,1
    trainCtrl.TrainModel_arr[0] = 0
    trainCtrl.Driver_arr[2] = 1
    Endcase *= PTSD_test(file, "M: ACTSPD: 0", trainCtrl.TrainModel_arr[0], 0)
    Endcase *= PTSD_test(file, "M: CMDSPD: 1", trainCtrl.Driver_arr[2], 1)
    Endcase *= PTSD_test(file, "M: AUTH: 1",   trainCtrl.TrainModel_arr[2], 1)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "M: POWER: 0,1,1", trainCtrl.output_arr[1]>0, True)
    file.write("TRAIN"+str(trainCtrl.Driver_arr)+"\n")
    file.write("TRAIN"+str(trainCtrl.TrainModel_arr)+"\n")
    file.write("OUTPUT"+str(trainCtrl.output_arr)+"\n")
    
    #-----
    #0,1,0
    trainCtrl.TrainModel_arr[2] = 0
    Endcase *= PTSD_test(file, "M: ACTSPD: 0", trainCtrl.TrainModel_arr[0], 0)
    Endcase *= PTSD_test(file, "M: CMDSPD: 1", trainCtrl.Driver_arr[2], 1)
    Endcase *= PTSD_test(file, "M: AUTH: 0",   trainCtrl.TrainModel_arr[2], 0)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "M: POWER: 0,1,1", trainCtrl.output_arr[1]>0, 0)
    file.write("TRAIN"+str(trainCtrl.Driver_arr)+"\n")
    file.write("TRAIN"+str(trainCtrl.TrainModel_arr)+"\n")
    file.write("OUTPUT"+str(trainCtrl.output_arr)+"\n")
    
    #-----
    #0,0,1
    trainCtrl.Driver_arr[2] = 0
    trainCtrl.TrainModel_arr[2] = 1
    Endcase *= PTSD_test(file, "M: ACTSPD: 0", trainCtrl.TrainModel_arr[0], 0)
    Endcase *= PTSD_test(file, "M: CMDSPD: 0", trainCtrl.Driver_arr[2], 0)
    Endcase *= PTSD_test(file, "M: AUTH: 1",   trainCtrl.TrainModel_arr[2], 1)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "M: POWER: 0,1,1", trainCtrl.output_arr[1], 0)
    
    
    
    
    
    #----------------------------------------------
    #Endcase
    file.write("\n-------------\n")
    file.write(f"[!!!!!] 08zero_pow_auth: <{'PASS' if Endcase else 'FAIL'}>\n")

    print("\n-------------")
    print(f"[!!!!!] 08zero_pow_auth: <{'PASS' if Endcase else 'FAIL'}>")
    return Endcase


#----------------------------------------------
#Enable of Emergency brake turns off service brake
def brake_overturn(folder):
    #prints, prep log
    print("================================================================================")
    print("\n[!!!!!!!] TESTING:\t 10brake_overturn")
    print(f"file:\t\t{folder}/10brake_overturn.txt")
    file = open(f"{folder}/10brake_overturn.txt", 'w')
    file.write("Hi\n")
    
    #----------------------------------------------
    #making controller
    main_TrainModel_arr = [1,1,1,False,False,False,"0"*128]
    main_output_arr = []
    main_Driver_arr = []
    
    try: it = util.Iterator(board); it.start()
    except (Exception,): print("No Train Controller HW detected: util.Iterator")
    
    trainCtrl = HW_UI_JEB382_PyFirmat(main_Driver_arr, main_TrainModel_arr, main_output_arr)
    
    #----------------------------------------------
    #Testing
    Endcase = True
    
    #-----
    #auto
    Endcase *= PTSD_test(file, "A: SBRAKE: INIT", trainCtrl.output_arr[2], False)
    Endcase *= PTSD_test(file, "A: EBRAKE: INIT", trainCtrl.output_arr[3], False)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: SBRAKE: CALC1", trainCtrl.output_arr[2], False)
    Endcase *= PTSD_test(file, "A: EBRAKE: CALC1", trainCtrl.output_arr[3], False)
    
    #-----
    #sbrake
    trainCtrl.TrainModel_arr[2] = 0
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: SBRAKE: CALC2", trainCtrl.output_arr[2], True)
    Endcase *= PTSD_test(file, "A: EBRAKE: CALC2", trainCtrl.output_arr[3], False)
    
    #-----
    #ebrake
    trainCtrl.Driver_arr[8] = True
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: SBRAKE: CALC3", trainCtrl.output_arr[2], False)
    Endcase *= PTSD_test(file, "A: EBRAKE: CALC3", trainCtrl.output_arr[3], True)
    
    #-----
    #ebrake force
    trainCtrl.Driver_arr[8] = False
    trainCtrl.TrainModel_arr[3] = True
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: SBRAKE: CALC4", trainCtrl.output_arr[2], False)
    Endcase *= PTSD_test(file, "A: EBRAKE: CALC4", trainCtrl.output_arr[3], True)
    
    
    
    
    
    #----------------------------------------------
    #Endcase
    file.write("\n-------------\n")
    file.write(f"[!!!!!] 10brake_overturn: <{'PASS' if Endcase else 'FAIL'}>\n")

    print("\n-------------")
    print(f"[!!!!!] 10brake_overturn: <{'PASS' if Endcase else 'FAIL'}>")
    return Endcase


#----------------------------------------------
#Turn on both lights when given lack of ambient light in both modes
def amb_light(folder):
    #prints, prep log
    print("================================================================================")
    print("\n[!!!!!!!] TESTING:\t 11amb_light_on")
    print(f"file:\t\t{folder}/11amb_light_on.txt")
    file = open(f"{folder}/11amb_light_on.txt", 'w')
    file.write("Hi\n")
    
    #----------------------------------------------
    #making controller
    main_TrainModel_arr = [0,0,0,False,False,True,"0"*128]
    main_output_arr = []
    main_Driver_arr = []
    
    try: it = util.Iterator(board); it.start()
    except (Exception,): print("No Train Controller HW detected: util.Iterator")
    
    trainCtrl = HW_UI_JEB382_PyFirmat(main_Driver_arr, main_TrainModel_arr, main_output_arr)
    
    #----------------------------------------------
    #Testing
    Endcase = True
    
    #-----
    #auto
    #off
    Endcase *= PTSD_test(file, "A: AMBIENT LIGHT: Inheritance", trainCtrl.TrainModel_arr[5], True)
    trainCtrl.TrainModel_arr[5] = False
    Endcase *= PTSD_test(file, "A: AMBIENT LIGHT: INIT", trainCtrl.TrainModel_arr[5], False)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: INT LIGHT: INIT", trainCtrl.output_arr[6], False)
    Endcase *= PTSD_test(file, "A: EXT LIGHT: INIT", trainCtrl.output_arr[7], False)
    
    #-----
    #on
    trainCtrl.TrainModel_arr[5] = True
    Endcase *= PTSD_test(file, "A: AMBIENT LIGHT: CHANGE1", trainCtrl.TrainModel_arr[5], True)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: INT LIGHT: CHANGE1", trainCtrl.output_arr[6], True)
    Endcase *= PTSD_test(file, "A: EXT LIGHT: CHANGE1", trainCtrl.output_arr[7], True)
    
    
    
    
    #-----------------
    #manual
    trainCtrl.Mode = True #mode
    #off
    trainCtrl.TrainModel_arr[5] = False
    Endcase *= PTSD_test(file, "A: AMBIENT LIGHT: INIT", trainCtrl.TrainModel_arr[5], False)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: INT LIGHT: INIT", trainCtrl.output_arr[6], False)
    Endcase *= PTSD_test(file, "A: EXT LIGHT: INIT", trainCtrl.output_arr[7], False)
    
    #-----
    #on
    trainCtrl.TrainModel_arr[5] = True
    Endcase *= PTSD_test(file, "A: AMBIENT LIGHT: CHANGE1", trainCtrl.TrainModel_arr[5], True)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: INT LIGHT: CHANGE1", trainCtrl.output_arr[6], True)
    Endcase *= PTSD_test(file, "A: EXT LIGHT: CHANGE1", trainCtrl.output_arr[7], True)
    
    #-----
    #off2
    trainCtrl.TrainModel_arr[5] = False
    Endcase *= PTSD_test(file, "A: AMBIENT LIGHT: CHANGE2", trainCtrl.TrainModel_arr[5], False)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: INT LIGHT: CHANGE2", trainCtrl.output_arr[6], False)
    Endcase *= PTSD_test(file, "A: EXT LIGHT: CHANGE2", trainCtrl.output_arr[7], False)
    
    #-----
    #this is also tested in driver_int_lights and driver_ext_lights
    #driver addition int
    trainCtrl.Driver_arr[3] = True
    Endcase *= PTSD_test(file, "A: AMBIENT LIGHT: DRIVER1", trainCtrl.TrainModel_arr[5], False)
    Endcase *= PTSD_test(file, "A: DRIVER INT LIGHT: DRIVER1", trainCtrl.Driver_arr[3], True)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: INT LIGHT: DRIVER1", trainCtrl.output_arr[6], True)
    Endcase *= PTSD_test(file, "A: EXT LIGHT: DRIVER1", trainCtrl.output_arr[7], False)
    
    #-----
    #driver addition ext
    trainCtrl.Driver_arr[4] = True
    Endcase *= PTSD_test(file, "A: AMBIENT LIGHT: DRIVER2", trainCtrl.TrainModel_arr[5], False)
    Endcase *= PTSD_test(file, "A: DRIVER INT LIGHT: DRIVER2", trainCtrl.Driver_arr[3], True)
    Endcase *= PTSD_test(file, "A: DRIVER EXT LIGHT: DRIVER2", trainCtrl.Driver_arr[4], True)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: INT LIGHT: DRIVER2", trainCtrl.output_arr[6], True)
    Endcase *= PTSD_test(file, "A: EXT LIGHT: DRIVER2", trainCtrl.output_arr[7], True)
    
    
    
    
    
    #----------------------------------------------
    #Endcase
    file.write("\n-------------\n")
    file.write(f"[!!!!!] 11amb_light_on: <{'PASS' if Endcase else 'FAIL'}>\n")

    print("\n-------------")
    print(f"[!!!!!] 11amb_light_on: <{'PASS' if Endcase else 'FAIL'}>")
    return Endcase


#----------------------------------------------
#TODO: BEACON ADDITION
#Train calculates correct stopping distance with current speed
def stop_dist(folder):
    #prints, prep log
    print("================================================================================")
    print("\n[!!!!!!!] TESTING:\t 13stop_dist")
    print(f"file:\t\t{folder}/13stop_dist.txt")
    file = open(f"{folder}/13stop_dist.txt", 'w')
    file.write("Hi\n")
    
    #----------------------------------------------
    #making controller
    main_TrainModel_arr = [0,0,0,False,False,False,"0"*128]
    main_output_arr = []
    main_Driver_arr = []
    
    try: it = util.Iterator(board); it.start()
    except (Exception,): print("No Train Controller HW detected: util.Iterator")
    
    trainCtrl = HW_UI_JEB382_PyFirmat(main_Driver_arr, main_TrainModel_arr, main_output_arr)
    
    #----------------------------------------------
    #Testing
    Endcase = True
    
    
    
    
    
    #----------------------------------------------
    #Endcase
    file.write("\n-------------\n")
    file.write(f"[!!!!!] 13stop_dist: <{'PASS' if Endcase else 'FAIL'}>\n")

    print("\n-------------")
    print(f"[!!!!!] 13stop_dist: <{'PASS' if Endcase else 'FAIL'}>")
    return Endcase


#----------------------------------------------
#Train enables service brake within correct stopping distance
def sbrake_dist(folder):
    #prints, prep log
    print("================================================================================")
    print("\n[!!!!!!!] TESTING:\t 14sbrake_dist")
    print(f"file:\t\t{folder}/14sbrake_dist.txt")
    file = open(f"{folder}/14sbrake_dist.txt", 'w')
    file.write("Hi\n")
    
    #----------------------------------------------
    #making controller
    main_TrainModel_arr = [0,0,0,False,False,False,"0"*128]
    main_output_arr = []
    main_Driver_arr = []
    
    try: it = util.Iterator(board); it.start()
    except (Exception,): print("No Train Controller HW detected: util.Iterator")
    
    trainCtrl = HW_UI_JEB382_PyFirmat(main_Driver_arr, main_TrainModel_arr, main_output_arr)
    
    #----------------------------------------------
    #Testing
    Endcase = True
    
    
    
    
    
    #----------------------------------------------
    #Endcase
    file.write("\n-------------\n")
    file.write(f"[!!!!!] 14sbrake_dist: <{'PASS' if Endcase else 'FAIL'}>\n")

    print("\n-------------")
    print(f"[!!!!!] 14sbrake_dist: <{'PASS' if Endcase else 'FAIL'}>")
    return Endcase


#----------------------------------------------
#Train enables emergency brake if it cant stop in time
def ebrake_dist(folder):
    #prints, prep log
    print("================================================================================")
    print("\n[!!!!!!!] TESTING:\t 15ebrake_dist")
    print(f"file:\t\t{folder}/15ebrake_dist.txt")
    file = open(f"{folder}/15ebrake_dist.txt", 'w')
    file.write("Hi\n")
    
    #----------------------------------------------
    #making controller
    main_TrainModel_arr = [0,0,0,False,False,False,"0"*128]
    main_output_arr = []
    main_Driver_arr = []
    
    try: it = util.Iterator(board); it.start()
    except (Exception,): print("No Train Controller HW detected: util.Iterator")
    
    trainCtrl = HW_UI_JEB382_PyFirmat(main_Driver_arr, main_TrainModel_arr, main_output_arr)
    
    #----------------------------------------------
    #Testing
    Endcase = True
    
    
    
    
    
    #----------------------------------------------
    #Endcase
    file.write("\n-------------\n")
    file.write(f"[!!!!!] 15ebrake_dist: <{'PASS' if Endcase else 'FAIL'}>\n")

    print("\n-------------")
    print(f"[!!!!!] 15ebrake_dist: <{'PASS' if Endcase else 'FAIL'}>")
    return Endcase


#----------------------------------------------
#Train gives station when in the block
def announce_stat_block(folder):
    #prints, prep log
    print("================================================================================")
    print("\n[!!!!!!!] TESTING:\t 16announce_stat_block")
    print(f"file:\t\t{folder}/16announce_stat_block.txt")
    file = open(f"{folder}/16announce_stat_block.txt", 'w')
    file.write("Hi\n")
    
    #----------------------------------------------
    #making controller
    main_TrainModel_arr = [0,0,0,False,False,False,"0"*128]
    main_output_arr = []
    main_Driver_arr = []
    
    try: it = util.Iterator(board); it.start()
    except (Exception,): print("No Train Controller HW detected: util.Iterator")
    
    trainCtrl = HW_UI_JEB382_PyFirmat(main_Driver_arr, main_TrainModel_arr, main_output_arr)
    
    #----------------------------------------------
    #Testing
    Endcase = True
    
    
    
    
    
    #----------------------------------------------
    #Endcase
    file.write("\n-------------\n")
    file.write(f"[!!!!!] 16announce_stat_block: <{'PASS' if Endcase else 'FAIL'}>\n")

    print("\n-------------")
    print(f"[!!!!!] 16announce_stat_block: <{'PASS' if Endcase else 'FAIL'}>")
    return Endcase


#----------------------------------------------
#Driver can adjust Temperature in any mode within limit
def driver_temp(folder):
    #prints, prep log
    print("================================================================================")
    print("\n[!!!!!!!] TESTING:\t 17driver_temp")
    print(f"file:\t\t{folder}/17driver_temp.txt")
    file = open(f"{folder}/17driver_temp.txt", 'w')
    file.write("Hi\n")
    
    #----------------------------------------------
    #making controller
    main_TrainModel_arr = [0,0,0,False,False,False,"0"*128]
    main_output_arr = []
    main_Driver_arr = []
    
    try: it = util.Iterator(board); it.start()
    except (Exception,): print("No Train Controller HW detected: util.Iterator")
    
    trainCtrl = HW_UI_JEB382_PyFirmat(main_Driver_arr, main_TrainModel_arr, main_output_arr)
    
    #----------------------------------------------
    #Testing
    Endcase = True
    
    #-----
    #auto
    #init
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: OUTPUT TEMP: INIT", trainCtrl.output_arr[8], 68)
    
    #-----
    #+10
    trainCtrl.Driver_arr[5] = 10
    Endcase *= PTSD_test(file, "A: DRIVER TEMP: +10", trainCtrl.Driver_arr[5], 10)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: OUTPUT TEMP: CHANGE1", trainCtrl.output_arr[8], 78)
    
    #-----
    #-10
    trainCtrl.Driver_arr[5] = -10
    Endcase *= PTSD_test(file, "A: DRIVER TEMP: +10", trainCtrl.Driver_arr[5], -10)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: OUTPUT TEMP: CHANGE1", trainCtrl.output_arr[8], 58)
    
    #-----
    #+20 pos max
    trainCtrl.Driver_arr[5] = 20
    Endcase *= PTSD_test(file, "A: DRIVER TEMP: +10", trainCtrl.Driver_arr[5], 20)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: OUTPUT TEMP: CHANGE1", trainCtrl.output_arr[8], 88)
    
    #-----
    #-20 neg max
    trainCtrl.Driver_arr[5] = -20
    Endcase *= PTSD_test(file, "A: DRIVER TEMP: +10", trainCtrl.Driver_arr[5], -20)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: OUTPUT TEMP: CHANGE1", trainCtrl.output_arr[8], 48)
    #cant test past max as that's within pyfirmata library, manual testing required
    
    
    
    
    #-----------------
    #manual
    trainCtrl.Mode = True #mode
    #init
    trainCtrl.Driver_arr[5] = 0
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: OUTPUT TEMP: INIT", trainCtrl.output_arr[8], 68)
    
    #-----
    #+10
    trainCtrl.Driver_arr[5] = 10
    Endcase *= PTSD_test(file, "A: DRIVER TEMP: +10", trainCtrl.Driver_arr[5], 10)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: OUTPUT TEMP: CHANGE1", trainCtrl.output_arr[8], 78)
    
    #-----
    #-10
    trainCtrl.Driver_arr[5] = -10
    Endcase *= PTSD_test(file, "A: DRIVER TEMP: +10", trainCtrl.Driver_arr[5], -10)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: OUTPUT TEMP: CHANGE1", trainCtrl.output_arr[8], 58)
    
    #-----
    #+20 pos max
    trainCtrl.Driver_arr[5] = 20
    Endcase *= PTSD_test(file, "A: DRIVER TEMP: +10", trainCtrl.Driver_arr[5], 20)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: OUTPUT TEMP: CHANGE1", trainCtrl.output_arr[8], 88)
    
    #-----
    #-20 neg max
    trainCtrl.Driver_arr[5] = -20
    Endcase *= PTSD_test(file, "A: DRIVER TEMP: +10", trainCtrl.Driver_arr[5], -20)
    trainCtrl.updateCalc()
    Endcase *= PTSD_test(file, "A: OUTPUT TEMP: CHANGE1", trainCtrl.output_arr[8], 48)
    #cant test past max as that's within pyfirmata library, manual testing required
    
    
    
    
    
    #----------------------------------------------
    #Endcase
    file.write("\n-------------\n")
    file.write(f"[!!!!!] 17driver_temp: <{'PASS' if Endcase else 'FAIL'}>\n")

    print("\n-------------")
    print(f"[!!!!!] 17driver_temp: <{'PASS' if Endcase else 'FAIL'}>")
    return Endcase


#----------------------------------------------
#test beacon reading from redline
def redline_rundown(folder):
    #prints, prep log
    print("================================================================================")
    print("\n[!!!!!!!] TESTING:\t 18redline_rundown")
    print(f"file:\t\t{folder}/18redline_rundown.txt")
    file = open(f"{folder}/18redline_rundown.txt", 'w')
    file.write("Hi\n")
    
    #----------------------------------------------
    #making controller
    main_TrainModel_arr = [0,0,0,False,False,False,"0"*128]
    main_output_arr = []
    main_Driver_arr = []
    
    try: it = util.Iterator(board); it.start()
    except (Exception,): print("No Train Controller HW detected: util.Iterator")
    
    trainCtrl = HW_UI_JEB382_PyFirmat(main_Driver_arr, main_TrainModel_arr, main_output_arr)
    
    #----------------------------------------------
    #Testing
    Endcase = True
    
    
    
    
    
    #----------------------------------------------
    #Endcase
    file.write("\n-------------\n")
    file.write(f"[!!!!!] 16announce_stat_block: <{'PASS' if Endcase else 'FAIL'}>\n")

    print("\n-------------")
    print(f"[!!!!!] 16announce_stat_block: <{'PASS' if Endcase else 'FAIL'}>")
    return Endcase


#----------------------------------------------
#must be done by a person manually
'''#HW: correct buttons correspond to correct changes in driver array
def pass_break_enable(folder):
    #prints, prep log
    print("================================================================================")
    print("\n[!!!!!!!] TESTING:\t pass_break_enable")
    print(f"file:\t\t{folder}/pass_break_enable.txt")
    file = open(f"{folder}/pass_break_enable.txt", 'w')
    file.write("Hi\n")
    
    #----------------------------------------------
    #making controller
    main_TrainModel_arr = [0,0,0,False,False,False,"0"*128]
    main_output_arr = []
    main_Driver_arr = []
    
    try: it = util.Iterator(board); it.start()
    except (Exception,): print("No Train Controller HW detected: util.Iterator")
    
    trainCtrl = HW_UI_JEB382_PyFirmat(main_Driver_arr, main_TrainModel_arr, main_output_arr)
    
    #----------------------------------------------
    #Testing
    Endcase = True
    
    
    
    
    
    #----------------------------------------------
    #Endcase
    file.write("\n-------------\n")
    file.write(f"[!!!!!] 00pass_ebreak_enable: <{'PASS' if Endcase else 'FAIL'}>\n")

    print("\n-------------")
    print(f"[!!!!!] 00pass_ebreak_enable: <{'PASS' if Endcase else 'FAIL'}>")
    return Endcase



#HW: display corresponds to store information
def pass_break_enable(folder):
    #prints, prep log
    print("================================================================================")
    print("\n[!!!!!!!] TESTING:\t pass_break_enable")
    print(f"file:\t\t{folder}/pass_break_enable.txt")
    file = open(f"{folder}/pass_break_enable.txt", 'w')
    file.write("Hi\n")
    
    #----------------------------------------------
    #making controller
    main_TrainModel_arr = [0,0,0,False,False,False,"0"*128]
    main_output_arr = []
    main_Driver_arr = []
    
    try: it = util.Iterator(board); it.start()
    except (Exception,): print("No Train Controller HW detected: util.Iterator")
    
    trainCtrl = HW_UI_JEB382_PyFirmat(main_Driver_arr, main_TrainModel_arr, main_output_arr)
    
    #----------------------------------------------
    #Testing
    Endcase = True
    
    
    
    
    
    #----------------------------------------------
    #Endcase
    file.write("\n-------------\n")
    file.write(f"[!!!!!] 00pass_ebreak_enable: <{'PASS' if Endcase else 'FAIL'}>\n")

    print("\n-------------")
    print(f"[!!!!!] 00pass_ebreak_enable: <{'PASS' if Endcase else 'FAIL'}>")
    return Endcase



#HW: displayes "APP" when within authority of a station
def pass_break_enable(folder):
    #prints, prep log
    print("================================================================================")
    print("\n[!!!!!!!] TESTING:\t pass_break_enable")
    print(f"file:\t\t{folder}/pass_break_enable.txt")
    file = open(f"{folder}/pass_break_enable.txt", 'w')
    file.write("Hi\n")
    
    #----------------------------------------------
    #making controller
    main_TrainModel_arr = [0,0,0,False,False,False,"0"*128]
    main_output_arr = []
    main_Driver_arr = []
    
    try: it = util.Iterator(board); it.start()
    except (Exception,): print("No Train Controller HW detected: util.Iterator")
    
    trainCtrl = HW_UI_JEB382_PyFirmat(main_Driver_arr, main_TrainModel_arr, main_output_arr)
    
    #----------------------------------------------
    #Testing
    Endcase = True
    
    
    
    
    
    #----------------------------------------------
    #Endcase
    file.write("\n-------------\n")
    file.write(f"[!!!!!] 00pass_ebreak_enable: <{'PASS' if Endcase else 'FAIL'}>\n")

    print("\n-------------")
    print(f"[!!!!!] 00pass_ebreak_enable: <{'PASS' if Endcase else 'FAIL'}>")
    return Endcase



#HW: displayers "NOW:" when in a station
def pass_break_enable(folder):
    #prints, prep log
    print("================================================================================")
    print("\n[!!!!!!!] TESTING:\t pass_break_enable")
    print(f"file:\t\t{folder}/pass_break_enable.txt")
    file = open(f"{folder}/pass_break_enable.txt", 'w')
    file.write("Hi\n")
    
    #----------------------------------------------
    #making controller
    main_TrainModel_arr = [0,0,0,False,False,False,"0"*128]
    main_output_arr = []
    main_Driver_arr = []
    
    try: it = util.Iterator(board); it.start()
    except (Exception,): print("No Train Controller HW detected: util.Iterator")
    
    trainCtrl = HW_UI_JEB382_PyFirmat(main_Driver_arr, main_TrainModel_arr, main_output_arr)
    
    #----------------------------------------------
    #Testing
    Endcase = True
    
    
    
    
    
    #----------------------------------------------
    #Endcase
    file.write("\n-------------\n")
    file.write(f"[!!!!!] 00pass_ebreak_enable: <{'PASS' if Endcase else 'FAIL'}>\n")

    print("\n-------------")
    print(f"[!!!!!] 00pass_ebreak_enable: <{'PASS' if Endcase else 'FAIL'}>")
    return Endcase

'''









#================================================================================
#================================================================================
if __name__ == "__main__":
    #folder: test_dir
    test_dir = get_testing_folder()
    tot_Endcase = True#total Endcase that all tests work
    
    # NOTE: Passenger Break enables eBrake
    tot_Endcase *= pass_ebreak_enable(test_dir)
    
    # NOTE: Driver can disable Passenger Brake's effect in any mode
    tot_Endcase *= driver_disable_pass(test_dir)
    
    # NOTE: Driver can enable ebrake in any mode
    tot_Endcase *= driver_ebreak_enable(test_dir)
    
    # NOTE: Driver can enable service brake in manual mode only
    tot_Endcase *= driver_sbreak_enable(test_dir)
    
    # NOTE: Driver can change door state when train is stopped in manual mode
    tot_Endcase *= driver_door(test_dir)
    
    # NOTE: Train opens stationside door when train is stopped in auto mode
    #!!!!!!!!!!TODO: ADD BEACON TRACING
    #tot_Endcase *= train_door(test_dir)
    # NOTE: Driver can enable interior lights in manual when it is otherwise off
    tot_Endcase *= driver_int_lights(test_dir)
    
    # NOTE: Driver can enable exterior lights in manual mode when it is otherwise off.
    tot_Endcase *= driver_ext_lights(test_dir)
    
    # NOTE: Power is zero without authority and/or commanded speed, or matching actual
    tot_Endcase *= zero_pow(test_dir)
    
    # NOTE: Enable of Emergency brake turns off service brake
    tot_Endcase *= brake_overturn(test_dir)
    
    # NOTE: Turn on both lights when given lack of ambient light in both modes
    # NOTE: Turn off both lights when given ambient light in both modes
    tot_Endcase *= amb_light(test_dir)
    
    # NOTE: Train calculates correct stopping distance with current speed
    #!!!!!!!!!!TODO: BEACON ADDITION
    # NOTE: Better off manual with the TB
    #tot_Endcase *= stop_dist(test_dir)
    
    # NOTE: Train enables service brake within correct stopping distance
    #!!!!!!!!!!TODO: BEACON ADDITION
    # NOTE: Better off manual with the TB
    #tot_Endcase *= sbrake_dist(test_dir)
    
    # NOTE: Train enables emergency brake if it cant stop in time
    #!!!!!!!!!!TODO: BEACON ADDITION
    # NOTE: Better off manual with the TB
    #tot_Endcase *= ebrake_dist(test_dir)
    
    # NOTE: Train gives station when in the block
    #!!!!!!!!!!TODO: BEACON ADDITION
    # NOTE: Better off manual with the TB
    #tot_Endcase *= announce_stat_block(test_dir)
    
    # NOTE: Driver can adjust Temperature in any mode within limit
    tot_Endcase *= driver_temp(test_dir)
    
    #NOTE: [!!!!!!!!!!] Must be done manually
    #HW: correct buttons correspond to correct changes in driver array
    #HW: display corresponds to store information
    #HW: displayes "APP" when within authority of a station
    #HW: displayers "NOW:" when in a station


    #----------------------------------------------
    #Endcase
    print("================================================================================")
    print("\n\n\n=============-------------=============-------------=============")
    print(f"[!!!ATTENTION!!!]\nTOTAL TESTING OF TRAIN CONTROLLER HW:\n<{'PASS' if tot_Endcase else 'FAIL'}>")