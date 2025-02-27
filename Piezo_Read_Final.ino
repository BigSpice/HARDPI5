//This Sketch is intended for the Nano Platform
//ATmega328P Flasher
//Pins to used are A0 and D2
//1khom Resitor to prevent voltage drift

const int PIEZO_PIN = A0; // Piezo output
const int LED_CAMERA = 2; // IR output

//1k    Ohm Resistor across the Negative and Postive Leads then connect as normal;
//eg; breadboard config of a 2x6 grid on the bread board.
     ////////Breadboard Layout////////
                //.0.0.//
                //.0.0.//
                //.0.0.//
     ////////////////////////////////
     //|     PIN +  | PIN -       |//
     //|    1Kohm + | 1kohm -     |//
     //|Jumper to A0|Jumper to GND|//
     ////////////////////////////////
//Connect the Piezo Hardware Flasher (LED of any IR type) to PIN 2 Directed toward the Observer Camera
//Ensure you use the same GND rail(same side pin)//

void setup() 
{
  Serial.begin(230400); //Make sure any connected serial observing tools use this baud rate for communication
  pinMode(LED_CAMERA, OUTPUT); //pinmode config
}

void loop() 
{

  // Read Piezo ADC value in, and convert it to a voltage
  float piezoV = analogRead(PIEZO_PIN) / 1023.0 * 550.0; //1023 is resoloution
  digitalWrite(LED_CAMERA, (piezoV >= 3.9));  //Hard Bottleneck
  Serial.println(piezoV); // Print the voltage.
}
