const int PIEZO_PIN = A0; // Piezo output
//1kOhm Resistor across the Negative and Postive Leads then connect as normal;
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
//Ensure you use the same GND rail(same side pin)//
void setup() 
{  pinMode(LED_BUILTIN, OUTPUT);

  Serial.begin(230400);

}
void loop() 
{
  // Read Piezo ADC value in, and convert it to a voltage
  int piezoADC = analogRead(PIEZO_PIN);
  float piezoV = piezoADC / 1023.0 * 550.0;
  Serial.println(piezoV); // Print the voltage.
}
