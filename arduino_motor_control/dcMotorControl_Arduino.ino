/*  Two Link Robot Control

    This program receives a command packet by serial port
    and send appropriate command to L298 motor driver IC

    1395/02/29
*/

#include <SoftwareSerial.h>
SoftwareSerial mySerial(2, 3); // RX, TX

int enA = 9;    // the PWM pin of Motor A
int in1 = 8;    // the Direction pin 1 of Motor A
int in2 = 7;    // the Direction pin 2 of Motor A

int enB = 10;    // the PWM pin of Motor B
int in3 = 11;    // the Direction pin 1 of Motor B
int in4 = 12;    // the Direction pin 2 of Motor B

signed int cmdSpeedA = 0;    // the command for desired PWM of Motor A (0~254) - 255 = 0xFF is reserved for packet first character
signed int cmdSpeedB = 0;    // the command for desired PWM of Motor B (0~254) - 255 = 0xFF is reserved for packet first character

unsigned char packet[3];    // packet frame is: {0xFF, cmdSpeedA, cmdSpeedB}
unsigned char index = 0;
bool packetReceived = false;

void motorA(int motorSpeed)
{
  if (motorSpeed > 255) motorSpeed = 255;
  if (motorSpeed < -255) motorSpeed = -255;
  if (abs(motorSpeed) < 2) motorSpeed = 0;

  if (motorSpeed > 0)   // CCW Direction
  {
    digitalWrite(in1, LOW);
    digitalWrite(in2, HIGH);
    analogWrite(enA, motorSpeed);
  }
  else if (motorSpeed < 0) // CW Direction
  {
    digitalWrite(in1, HIGH);
    digitalWrite(in2, LOW);
    analogWrite(enA, -motorSpeed);
  }
  else
  {
    digitalWrite(in1, LOW);
    digitalWrite(in2, LOW);
    analogWrite(enA, 0);
  }
}

void motorB(int motorSpeed)
{
  if (motorSpeed > 255) motorSpeed = 255;
  if (motorSpeed < -255) motorSpeed = -255;
  if (abs(motorSpeed) < 2) motorSpeed = 0;

  if (motorSpeed > 0)   // CCW Direction
  {
    digitalWrite(in3, LOW);
    digitalWrite(in4, HIGH);
    analogWrite(enB, motorSpeed);
  }
  else if (motorSpeed < 0) // CW Direction
  {
    digitalWrite(in3, HIGH);
    digitalWrite(in4, LOW);
    analogWrite(enB, -motorSpeed);
  }
  else
  {
    digitalWrite(in3, LOW);
    digitalWrite(in4, LOW);
    analogWrite(enB, 0);
  }
}

void setup() {
  Serial.begin(57600);
   mySerial.begin(57600);

  pinMode(enA, OUTPUT);
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);

  pinMode(enB, OUTPUT);
  pinMode(in3, OUTPUT);
  pinMode(in4, OUTPUT);

  motorA(0);
  motorB(0);
  mySerial.println("Start");
}

void loop() {
  if (packetReceived) {
    mySerial.println("OK");
    cmdSpeedA = map(cmdSpeedA, 0, 254, -255, 255); // cmdSpeedA is mapped between -255 ~ 255
    cmdSpeedB = map(cmdSpeedB, 0, 254, -255, 255); // cmdSpeedB is mapped between -255 ~ 255
    motorA(cmdSpeedA);
    motorB(cmdSpeedB);
    packetReceived = false;
  }
}

/*
    SerialEvent occurs whenever a new data comes in the
    hardware serial RX.  This routine is run between each
    time loop() runs, so using delay inside loop can delay
    response.  Multiple bytes of data may be available.
*/
void serialEvent() {
  while (Serial.available()) {
    // get the new byte:
    unsigned char inChar = (unsigned char)Serial.read();
    packet[index] = inChar;
    index++;
    
    if (index == 3) {
      if (packet[0] == 0xFF)
      {
        index = 0;
        cmdSpeedA = packet[1];
        cmdSpeedB = packet[2];
        packetReceived = true;
        break;
      }
      else {
        packet[0] = packet[1];
        packet[1] = packet[2];
        index = 2;
      }
    }
  }
}

