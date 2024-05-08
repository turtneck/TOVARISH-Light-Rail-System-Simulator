int incomingByte = 0; // for incoming serial data
String TrainModel_arr[12];
int Driver_arr[11];
int StringCount = 0;

//analog-----------------------
int TCK_Kp  = 0;
int TCK_Ki      = 1;
int TCK_CmdSpd  = 2;
int TCK_Temp    = 3;

//digital----------------------

//BUTTONS
int BTN_CabnLgt = 38;
int BTN_HeadLgt = 40;

int BTN_Door_L  = 42;
int BTN_Door_R  = 44;

int BTN_EBRK    = 46;
int BTN_SBRK    = 48;

int BTN_DisPaEB = 50;

int BTN_Mode = 52;
int Mode = 0;
int curr_Mode_state = 0;
int last_Mode_state = 0;    // previous state of the button

//LEDS-------------------------
int LED_CabnLgt    = 22;
int LED_HeadLgt    = 23;
int LED_Door_L     = 24;
int LED_Door_R     = 25;
int LED_Pass_EB    = 26;
int LED_Track_Circ = 27;
int LED_Stat_Side2 = 28;
int LED_Stat_Side1 = 29;
int LED_Sig_Fail   = 30;
int LED_Eng_Fail   = 31;
int LED_Brk_Fail   = 32;
int LED_EBRK_Fail  = 33;
int LED_SBRK_Fail  = 34;




//runtime----------------------
void setup() {
  Serial.begin(9600); // opens serial port, sets data rate to 9600 bps

  pinMode(BTN_CabnLgt, INPUT);
  pinMode(BTN_HeadLgt, INPUT);   
  pinMode(BTN_Door_L, INPUT);
  pinMode(BTN_Door_R, INPUT);   
  pinMode(BTN_EBRK, INPUT);
  pinMode(BTN_SBRK, INPUT);
  pinMode(BTN_DisPaEB, INPUT);
  pinMode(BTN_Mode, INPUT);
}

void loop() {
  // send data only when you receive data:
  if (Serial.available() > 0) {
    // read the incoming byte:
    String incomingString = Serial.readString();

    // prints the received data
    //Serial.print("I received: ");
    //Serial.println(incomingString);

    while (incomingString.length() > 0)
    {
      int index = incomingString.indexOf(", ");
      if (index == -1) // No space found
        {
          TrainModel_arr[StringCount++] = incomingString;
          break;
        }
      else
        {
          TrainModel_arr[StringCount++] = incomingString.substring(0, index);
          incomingString = incomingString.substring(index+1);
        }
    }
  /*
  for (int i = 0; i < StringCount; i++)
  {
    Serial.print(i);
    Serial.print(": ");
    Serial.println(TrainModel_arr[i]);
  }*/
  }
  
  //prepare return array
  Driver_arr[0] = analogRead(TCK_Kp);
  Driver_arr[1] = analogRead(TCK_Ki);
  Driver_arr[2] = analogRead(TCK_CmdSpd);
  Driver_arr[5] = analogRead(TCK_Temp);
  

  //make all toggle,array
  if(digitalRead(BTN_CabnLgt) == HIGH ){Driver_arr[3] = 1;}
  else{Driver_arr[3] = 0;}
  if(digitalRead(BTN_HeadLgt) == HIGH ){Driver_arr[4] = 1;}
  else{Driver_arr[4] = 0;}
  if(digitalRead(BTN_Door_L) == HIGH ){Driver_arr[6] = 1;}
  else{Driver_arr[6] = 0;}
  if(digitalRead(BTN_Door_R) == HIGH ){Driver_arr[7] = 1;}
  else{Driver_arr[7] = 0;}
  if(digitalRead(BTN_EBRK) == HIGH ){Driver_arr[8] = 1;}
  else{Driver_arr[8] = 0;}
  if(digitalRead(BTN_SBRK) == HIGH ){Driver_arr[9] = 1;}
  else{Driver_arr[9] = 0;}
  if(digitalRead(BTN_DisPaEB) == HIGH ){Driver_arr[10] = 1;}
  else{Driver_arr[10] = 0;}

  Serial.print("W ");
  for (int i = 0; i < 12; i++)
  {
    Serial.print(Driver_arr[i]);
    Serial.print(", ");
  }
  
  curr_Mode_state = digitalRead(BTN_Mode);
  if(curr_Mode_state != last_Mode_state && curr_Mode_state == HIGH){Mode ^= 1;}
  if( Mode == 0 ){Serial.print("\tAUTO");}
  else{Serial.print("\tMANUAL");}
  last_Mode_state = curr_Mode_state;

  Serial.println("");

  //set leds
  digitalWrite(LED_CabnLgt,Driver_arr[3]);
  digitalWrite(LED_HeadLgt,Driver_arr[4]);
  digitalWrite(LED_Door_L, Driver_arr[6]);
  digitalWrite(LED_Door_R, Driver_arr[7]);
  //digitalWrite(LED_Pass_EB,Driver_arr[3]);//TrainModel_arr[5]
  //digitalWrite(LED_Track_Circ,Driver_arr[3]);//TrainModel_arr[6]
  //digitalWrite(LED_Stat_Side2,Driver_arr[3]);//TrainModel_arr[7]%2
  //digitalWrite(LED_Stat_Side1,Driver_arr[3]);//TrainModel_arr[7]>1
  //digitalWrite(LED_Sig_Fail,Driver_arr[3]);//TrainModel_arr[8]
  //digitalWrite(LED_Eng_Fail,Driver_arr[3]);//TrainModel_arr[9]
  //digitalWrite(LED_Brk_Fail,Driver_arr[3]);//TrainModel_arr[10]
  //write //TrainModel_arr[11] to LCD
  digitalWrite(LED_EBRK_Fail,Driver_arr[8]);//TrainModel_arr[9]
  digitalWrite(LED_SBRK_Fail,Driver_arr[9]);//TrainModel_arr[10]




}
