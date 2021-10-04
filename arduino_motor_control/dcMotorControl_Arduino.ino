/*  Two Link Robot Control
 *  
 *  This program receives a command packet by serial port
 *  and send appropriate command to L298 motor driver IC
 *  
 *  1394/10/27
 */
 
//#include <SoftwareSerial.h>
//SoftwareSerial mySerial(2, 3); // RX, TX

int en = 9;     // the PWM pin
int in1 = 8;    // the Direction pin 1
int in2 = 7;    // the Direction pin 2

signed int cmdSpeed = 0;    // the desired PWM
bool cmdReceived = false;

void motor(int motorSpeed)
{
    if (motorSpeed > 255) motorSpeed = 255;
    if (motorSpeed < -255) motorSpeed = -255;
    if (abs(motorSpeed) < 2) motorSpeed = 0;
    
    if (motorSpeed > 0)   // CCW Direction
    {
      digitalWrite(in1, LOW);
      digitalWrite(in2, HIGH);
      analogWrite(en, motorSpeed);
    }
    else if (motorSpeed < 0) // CW Direction
    {
      digitalWrite(in1, HIGH);
      digitalWrite(in2, LOW);
      analogWrite(en, -motorSpeed);
    }
    else
    {
      digitalWrite(in1, LOW);
      digitalWrite(in2, LOW);
      analogWrite(en, 0);
    }
}

void setup() {
  Serial.begin(57600);
  //mySerial.begin(57600);
  
  pinMode(en, OUTPUT);
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);
  
  motor(0);
}

void loop() {
  // print the string when a newline arrives:
  if (cmdReceived) {
    cmdSpeed = 2 * (cmdSpeed - 127) - 1; // cmdSpeed is mapped between -255 ~ 255
    motor(cmdSpeed);
    cmdReceived = false;
  }
}

/*
 *  SerialEvent occurs whenever a new data comes in the
 *  hardware serial RX.  This routine is run between each
 *  time loop() runs, so using delay inside loop can delay
 *  response.  Multiple bytes of data may be available.
 */
void serialEvent() {
  while (Serial.available()) {
    // get the new byte:
    unsigned char inChar = (unsigned char)Serial.read();
    cmdSpeed = inChar;
    cmdReceived = true;
  }
}
