#include <Servo.h>  

// === Pin Definitions ===
#define PWMA 5      // right side motors
#define AIN1 7
#define PWMB 6      // left side motors
#define BIN1 8
#define STBY 3      // standby pin


char lastCommand = 'S';
int lastSpeed = 0;

Servo myServo;
const int servoPin = 10;

Servo ServoCam;
const int camPin = 11;

// === Setup ===
void setup() {
  
  pinMode(PWMA, OUTPUT);
  pinMode(AIN1, OUTPUT);
  pinMode(PWMB, OUTPUT);
  pinMode(BIN1, OUTPUT);
  pinMode(STBY, OUTPUT);

  digitalWrite(STBY, HIGH);
  Serial.begin(9600);
  
  myServo.attach(servoPin);
  ServoCam.attach(camPin);
  myServo.write(55);
  ServoCam.write(92);
  Serial.println("System Ready ✅");
}


// === Main Loop ===
void loop() {
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    input.trim();
   
    int firstComma = input.indexOf(',');
    int secondComma = input.indexOf(',', firstComma + 1);
    int thirdComma = input.indexOf(',', secondComma + 1);
    int fourthComma = input.indexOf(',', thirdComma + 1);
   
    char command = 'S';
    int speed = 0;
    int angle = 0;
    int cam_angle = 0;
    int turns = 0;
   
    // === Parse Command, Speed, Angle, Camera Angle, and Turns ===
    if (firstComma > 0) {
      command = input.charAt(0);
     
      if (fourthComma > 0) {
        // Five parameters: command,speed,angle,cam_angle,turns
        speed = input.substring(firstComma + 1, secondComma).toInt();
        angle = input.substring(secondComma + 1, thirdComma).toInt();
        cam_angle = input.substring(thirdComma + 1, fourthComma).toInt();
        turns = input.substring(fourthComma + 1).toInt();
      }
      else if (thirdComma > 0) {
        // Four parameters: command,speed,angle,cam_angle
        speed = input.substring(firstComma + 1, secondComma).toInt();
        angle = input.substring(secondComma + 1, thirdComma).toInt();
        cam_angle = input.substring(thirdComma + 1).toInt();
      }
      else if (secondComma > 0) {
        // Three parameters: command,speed,angle
        speed = input.substring(firstComma + 1, secondComma).toInt();
        angle = input.substring(secondComma + 1).toInt();
      }
      else {
        // Two parameters: command,speed
        speed = input.substring(firstComma + 1).toInt();
      }
    }
    else if (input.length() > 0) {
      // Only command, no commas
      command = input.charAt(0);
    }
   
    Serial.print("Command: "); Serial.println(command);
    Serial.print("Speed: "); Serial.println(speed);
    Serial.print("Angle: "); Serial.println(angle);
    Serial.print("Cam Angle: "); Serial.println(cam_angle);
    Serial.print("Turns: "); Serial.println(turns);
   
    // === Handle Camera Command ===
    if (command == 'Z') {
      moveCamera(cam_angle);
      return;
    }
   
    // === Handle Servo Command ===
    if (command == 'A') {
      moveServo(angle);
      return;
    }
   
    // === Handle Spin Command ===
    if (command == 'V') {  // SpinRIGHT
      SpinRIGHT(turns);
      return;
    }
    if (command == 'U') {  // SpinLEFT
      SpinLEFT(turns);
      return;
    }
   
    // === Handle Motor Commands ===
    if (command != lastCommand) {
      lastCommand = command;
      lastSpeed = speed;
      runImmediateCommand(command, speed);
    }
  }
}
void moveCamera(int camAngle) {
  camAngle = constrain(camAngle, 0, 180);
  ServoCam.write(camAngle);
  Serial.print("Camera moved to: ");
  Serial.println(camAngle);
  delay(500); // give servo time to reach position
}

void SpinRIGHT( int turns) {

  int speed = 200;
  Serial.print(turns);
  for (int n = 0; n < turns; n++)
   { digitalWrite(AIN1, LOW);   // Right side BACKWARD
    analogWrite(PWMA, speed);
    digitalWrite(BIN1, HIGH);  // Left side FORWARD
    analogWrite(PWMB, speed);
    delay(250);
    analogWrite(PWMA, 0);
    analogWrite(PWMB, 0);
    delay(250);}
}


void SpinLEFT(int turns) {
  int speed = 200;
  Serial.print(turns);
  for (int n = 0; n < turns; n++)
    {digitalWrite(AIN1, HIGH);   // Right side BACKWARD
    analogWrite(PWMA, speed);
    digitalWrite(BIN1, LOW);  // Left side FORWARD
    analogWrite(PWMB, speed);
    delay(300);
    analogWrite(PWMA, 0);
    analogWrite(PWMB, 0);
    delay(300);}
}


// === Move Servo Function ===
void moveServo(int angle) {
  angle = constrain(angle, 0, 180);
  myServo.write(angle);
  Serial.print("Servo moved to: ");
  Serial.println(angle);
  delay(500); // give servo time to reach position
}

// === Motor Control Function ===
void runImmediateCommand(char command, int speed) {
  if (command == 'F') { // forwards
    digitalWrite(AIN1, HIGH);
    analogWrite(PWMA, speed);
    digitalWrite(BIN1, HIGH);
    analogWrite(PWMB, speed);
  }
  else if (command == 'S') { // stop
    digitalWrite(AIN1, LOW);
    digitalWrite(BIN1, LOW);
    analogWrite(PWMA, 0);
    analogWrite(PWMB, 0);
  }
  else if (command == 'L') { // left forward
    digitalWrite(AIN1, HIGH);
    analogWrite(PWMA, speed);
    digitalWrite(BIN1, LOW);  // ADD THIS
    analogWrite(PWMB, 0);
  }
  else if (command == 'R') { // right forward
    digitalWrite(AIN1, LOW);  // ADD THIS
    analogWrite(PWMA, 0);
    digitalWrite(BIN1, HIGH);
    analogWrite(PWMB, speed);
  }
}