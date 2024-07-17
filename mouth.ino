#include <Servo.h>

Servo mouthServo;
int servoPin = 12;

void setup() {
  Serial.begin(9600);
  mouthServo.attach(servoPin);
}

void loop() {
  if (Serial.available() > 0) {
    int servoPosition = Serial.parseInt();
    mouthServo.write(servoPosition);
  }
}
