    `/*
Title: HASRA 2024 TETST Script
Author: Irina Morozov (imorozov@uottawa.ca)
Affiliation: University of Ottawa 
9 December 2024

To use this script: open Serial window from Arduino, then enter a character as a command. Commands listed below.
a = moves motor #1 to HOME dir LOW
b = moves motor #1 to other dir 

c = moves motor #2 to HOME dir LOW 
d = moves motor #2 other dir
default (any character other than the ones listed above) = moves both motors to HOME position; motor #1 first, then motor #2
*/

// PIEZO PINS AND VALUE
#include <Time.h>
int count = 0; // number of readings
unsigned long startTime; // Store the start time
const int PIEZO_PIN = A5; // Piezo output

// PELLET ARM MOTOR PINS AND VALUE
//byte Speed = 255; // Intialize Varaible for the speed of the motor (0-255);
//int RPWM = 11; 
//int LPWM = 12;
const int relay1 = 11;   //Arduino pin that triggers relay #1
const int relay2 = 12;   //Arduino pin that triggers relay #2
int directionValue = 1; // extention-down

//BEAM BREAKER PINS AND VALUE
const int IRBreakerPin = A2;
volatile byte IRState = digitalRead(IRBreakerPin);

//STEPPER PINS AND VALUE
const int STEPS_PER_REV = 200;
const int enablePin = 9; //9 white, 11 black
const int enable2 = 10;//10 white, 9 black

const int dirPin = 2;
const int stepPin = 3;

const int dir2 = 4;
const int step2 = 5;

int home_switch1 = 7;
int home_switch2 = 6;

// ************
void setup() {
  pinMode(stepPin, OUTPUT);
  pinMode(dirPin, OUTPUT);
  
  pinMode(step2, OUTPUT);
  pinMode(dir2, OUTPUT);
  
  pinMode(enablePin, OUTPUT); // PIN for enable pin on EzDriver
  pinMode(enable2, OUTPUT);
  
  digitalWrite(enablePin, HIGH);
  digitalWrite(enable2, HIGH);
  
  pinMode(home_switch1, INPUT_PULLUP);
  pinMode(home_switch2, INPUT_PULLUP);
  
  delay(3);
  
  Serial.begin(2000000);

  //Set pinMode to OUTPUT for the two relay pins
  pinMode(relay1, OUTPUT);
  pinMode(relay2, OUTPUT);

  //***** IR BREAKER PIN SET UP ************
  pinMode(IRBreakerPin, INPUT_PULLUP);
  // ********************************
  if(directionValue==1){
    Serial.println("EXTEND");
    extendActuator();
  }
}

void loop() {
  
  Serial.print("home_switch1 --> "); 
  Serial.println(digitalRead(home_switch1));
  
  Serial.print("home_switch2 --> ");
  Serial.println(digitalRead(home_switch2));
  
  if (digitalRead(IRBreakerPin)==1){
    Serial.println("MOUSE LEFT");
  } else {
    Serial.println("MOUSE IN");
    };
  
  if (Serial.available() > 0) {
    int inByte = Serial.read();
    
    switch (inByte) {
    ////////// motor #1 - Y direction - J1 & J6 /////////////
      case 'b':
        digitalWrite(enablePin, LOW);
        Serial.println("moving RIGHT");
        Serial.print("home_switch1 --> ");
        Serial.println(digitalRead(home_switch1));
        digitalWrite(dirPin,  HIGH);
        for (int x = 0; x < 100 ; x++) {
          //Serial.println(x);
          digitalWrite(stepPin, HIGH);
          delayMicroseconds(1000);
          digitalWrite(stepPin, LOW);
          delayMicroseconds(1000); 
        }
        Serial.println("Finished b");
        Serial.print("home_switch1 --> "); 
        Serial.println(digitalRead(home_switch1));
        digitalWrite(enablePin, HIGH);      
        break;
      case 'a':
        digitalWrite(enablePin, LOW);
        digitalWrite(dirPin, LOW);
        Serial.println("moving LEFT");
        Serial.print("home_switch1 --> ");
        Serial.println(digitalRead(home_switch1));
        for (int x = 0; x < 100; x++) { //total steps = 860
          digitalWrite(stepPin, HIGH);
          delayMicroseconds(1000);
          digitalWrite(stepPin, LOW);
          delayMicroseconds(1000);
        }
        Serial.println("Finished a=left");
        Serial.print("home_switch1 --> ");
        Serial.println(digitalRead(home_switch1));
        digitalWrite(enablePin, HIGH);
        break;
      ////////// motor #2  - X direction - J2 & J 7 /////////////
      case 'd':
        Serial.println("moving back");
        Serial.print("home_switch2 --> ");
        Serial.println(digitalRead(home_switch2));
        digitalWrite(enable2, LOW);
        digitalWrite(dir2, HIGH);
        for (int x = 0; x < 100; x++) { //total steps = 940
          digitalWrite(step2, HIGH);
          delayMicroseconds(1000);
          digitalWrite(step2, LOW);
          delayMicroseconds(1000);
        }
        Serial.println("Finished back c");
        Serial.print("home_switch2 --> ");
        Serial.println(digitalRead(home_switch2));
        digitalWrite(enable2, HIGH);
        break;

      case 'c':
        Serial.println("moving forward");
        Serial.print("home_switch2 --> ");
        Serial.println(digitalRead(home_switch2));
        digitalWrite(enable2, LOW);
        digitalWrite(dir2, LOW);
        for (int x = 0; x < 100; x++) {
          digitalWrite(step2, HIGH);
          delayMicroseconds(1000);
          digitalWrite(step2, LOW);
          delayMicroseconds(1000);
        }
        Serial.println("Finished front d");
        Serial.print("home_switch2 --> ");
        Serial.println(digitalRead(home_switch2));
        digitalWrite(enable2, HIGH);
        break;
     //*********************************************************
     // HASRA 2024 - PELLET PRESENTATION TEST
     //********************************************************
      case 'i': 
        Serial.println("HASRA 2024 STEPPER TEST");
        
        for (int y = 0; y <= 7; y++){
          Serial.println("moving X direction");
          Serial.println(y);
          Serial.print("home_switch2 --> ");
          Serial.println(digitalRead(home_switch2));
        
          digitalWrite(enable2, LOW);
          digitalWrite(dir2, HIGH);
          for (int x = 0; x < 100; x++) {
            digitalWrite(step2, HIGH);
            delayMicroseconds(1000);
            digitalWrite(step2, LOW);
            delayMicroseconds(1000);
          }
          digitalWrite(enable2, HIGH);
        }

        for (int y = 0; y <= 7; y++){
          Serial.println("moving Y direction");
          Serial.println(y);
          Serial.print("home_switch1 --> ");
          Serial.println(digitalRead(home_switch1));
          
          digitalWrite(enablePin, LOW);
          digitalWrite(dirPin,  HIGH);
          for (int x = 0; x < 100 ; x++) {
            digitalWrite(stepPin, HIGH);
            delayMicroseconds(1000);
            digitalWrite(stepPin, LOW);
            delayMicroseconds(1000); 
          }
          digitalWrite(enablePin, HIGH);     
        }
        presentPellet();    
        break;
      //****************************************************************
      default:
        //homing motor #1
        digitalWrite(enablePin, LOW);
        digitalWrite(dirPin, LOW);
        Serial.println("Entered default.");
        Serial.print("home_switch1 --> ");
        Serial.println(digitalRead(home_switch1));
        for (int x = 0; x < 100000; x++) {
         //  digitalWrite(led_PIN, HIGH);
          if (digitalRead(home_switch2) == 0) {
            Serial.println("home_switch2 --> Button pressed.********");
            break;
          }
          else {
            digitalWrite(stepPin, HIGH);
            delayMicroseconds(1000);
            digitalWrite(stepPin, LOW);
            delayMicroseconds(1000);
          }
        }

        digitalWrite(enablePin, HIGH);
        delay(1000);
        //homing motor #2
        digitalWrite(enable2, LOW);
        digitalWrite(dir2, LOW);
        for (int x = 0; x < 100000; x++) {
          if (digitalRead(home_switch1) == 0) {
            Serial.println("home_switch1 --> Button pressed.********");
            break;
          }
          else {
            digitalWrite(step2, HIGH);
            delayMicroseconds(1000);
            digitalWrite(step2, LOW);
            delayMicroseconds(1000); //1000
          }
        }
      //  digitalWrite(led_PIN, LOW);
        // enable pin activated back so we can avoid heating up of motors during down time
        digitalWrite(enable2, HIGH);
    }
  }
}

// PELLET PRESENTATION FUNCTION
void presentPellet(){
  while(digitalRead(IRBreakerPin)==0){ //while mouse IN
        
    Serial.println("EXTEND");
    extendActuator();
    delay(5000);

    Serial.println("RETRACT");
    retractActuator();
    delay(1300);
    
    Serial.println("STOP");
    stopActuator();  
  }
  //if mouse left, bring motor back to home position = EXTENSION = 1
  Serial.println("MOUSE LEFT");
  extendActuator();
}

void extendActuator() {
    digitalWrite(relay1, HIGH);
    digitalWrite(relay2, LOW);
}

void retractActuator() {
    digitalWrite(relay1, LOW);
    digitalWrite(relay2, HIGH);
}

void stopActuator() {
    digitalWrite(relay1, HIGH);
    digitalWrite(relay2, HIGH);
    AnalogAsync(5000);// 5000 milliseconds = 5 seconds ~ 10000 readings    
}

// PIEZO VALUE READER 
void AnalogAsync(unsigned long duration){
  count = 0; // number of readings
  startTime = millis(); // Store the start time
  float threshold = 1.00;
  while(true){
      count = count + 1;
      if (millis() - startTime >= duration) { 
        // Check if the specified time has passed
        break; // Exit the loop after the specified time
      }
    // Read Piezo ADC value in, and convert it to a voltage
    int piezoADC = analogRead(PIEZO_PIN);
    float piezoV = piezoADC / 1023.0 * 550.0;
    Serial.println("piezoV=;" + String(count) + ";" +  String(piezoV));// Print the voltage.
    //if(piezoV >=threshold){Serial.println("HIT-VAL=;" + String(count) + ";" + String(piezoV));
   // }
  }
 }



