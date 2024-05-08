# Train Controller Hardware, Jonah Belback

The Train Controller hardware module is used to control a simulated train on the simulated track. The train 
controller takes inputs from the train model (either through integration or through manual test bench) and the driver 
then performs control functions on those inputs in order to provide the train model with an engine power. All actions 
performed by the train controller module are done so to ensure the train system remains in a vital state.
## Installation
### Windows 10
Windows 10 can be installed here: https://www.microsoft.com/en-us/software-download/windows10%20

### Python 3.11
Python 3.11 can be installed here: https://www.python.org/downloads/release/python-3110/

### Python libraries
The following external libraries are needed for proper functionality of the Train Controller hardware module
- PyQt6

PyQt6 is used for both the UI design and for sending signals between the train controller hardware frontend and backend,
as well as for integration.
PyQt6 can be installed by using the following command in the Command Prompt:
```pip install PyQt6```




### Arduino
The Display of Train Controller Hardware requires an Arduino Mega 2560
one can be purchased here: https://store.arduino.cc/products/arduino-mega-2560-rev3

The Arduino needs to be installed with the C file 'PyFirmata.ino' under the 'Pyfrimata' directory folder under this module's.
This needs to be installed via the software 'Arduino IDE'
The software can be downloaded here:https://www.arduino.cc/en/software

Your IDE also needs to be given the library 'LiquidCrystal_I2C' v1.1.2, a zip of the library can be found under the same as the .ino



The Pins of the Arduino need to be matched up to buttons, LEDs, Potentiometers, and a LCD display as specficied by such:


### *Potentiometers*
- Analog 1    :Kp
- Analog 2    :Ki
- Analog 3    :Driver Commanded Speed
- Analog 4    :Temperature


### *LEDs*
- Digital 22  :Cabin Light
- Digital 23  :Head Light
- Digital 24  :Left Door
- Digital 25  :Right Door
- Digital 26  :Passenger Emergency Brake
- Digital 27  :Track Polarity
- Digital 28  :Station Side Door -Right Bit x_
- Digital 29  :Station Side Door -Left  Bit _x
- Digital 33  :Emergency Brake
- Digital 34  :Service Brake


### *Buttons*
- Digital 38  :Driver Cabin Light Override
- Digital 39  :Driver Head Light Override
- Digital 42  :Driver Left Door Override
- Digital 44  :Driver Right Door Override
- Digital 46  :Driver Emergency Brake
- Digital 48  :Driver Service Brake
- Digital 50  :Disable Passenger Emergency Brake
- Digital 52  :Mode

A picture of the pinout can be found at the file 'TrainC HW Arduino Pinout.jpg'




## Running Standalone Module
To run the module as a standalone component, navigate to 'Tovarish_Belback_Jonah_Train_Controller_HW_UI_PyFirmata.py'
file within an IDE or code editor of choice and run main().

You are given a selection based on what you comment out, indicating how the Train Controller is initalized:
- 0: Start beacon is all zeros, normally an error but for limitations with other modules places on the greenline
- 1: Start beacon is on the greenline
- 2: Start beacon is on the redline
- 3: Start beacon is full of nonsense information, raise error
Only uncomment one at a time.


If a choice is picked between 0 through 2, a single Hardware Traincontroller will spawn.
A testbench will then appear and the if the Hardware is setup correctly, it will light up with information.
Due to the vital architecture of the Train Controller, the module initializes with the speed and authority set to 0.
To simulate train movement and communication between modules when running standalone, the train controller test bench can 
be used.

Within the test bench, modifying the values for commanded speed and authority will trigger power control of the Train
Controller. Power will be calculated once authority is above 0 and commanded speed is set above 0.

Once power and authority is set and the train has calculated power, the actual speed of the train can be changed in the
test bench and the train controller will update values as if a signal has been received from the train model.




## Running Standalone Module - Automated Testing
To view how the Train Contoller is tested with automated regression tests, navigate to the 'Tovarish_Belback_Jonah_Train_Controller_Testing.py'
file within an IDE or code editor of choice and run main().

NOTE: Due to differences in some IDE's, minor modification may be nessecary, this module was created in VS Studio Code but use
in an IDE like PyCharm may need changes like to lines containing the 'linecache.getline()' function where files directories are interpreted differently. A new file path may be necessary. As of publication 4/25/2024 these issues are handled in Python 3.11.5 with latest PyCharm and VS Studio Code

Once ran, a folder will be created named the day's date in the folder 'Testlogs' under the module's folder.
This contains several textfiles all containing the logs of each regression test individually.
If the file is ran more then once on the same day, it will prompt you asking to delete the previously
created folder for that day before remaking it with that run's tests. Otherwise it will create the folder without asking.

The bottom printout in the terminal once a rundown of all the regressions are completed will tell you if all the tests have passed or not.
If not, please search within the console for 'fail' and navigate to the test that printed out that it has failed.
Each test's nonlog printouts and individual final results are split between 'bars' and have names labeled for your reading comprehension.




## Running Integrated Module
_To be completed when integration is complete..._