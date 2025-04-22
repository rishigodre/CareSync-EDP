#include <MPU9250_WE.h>
#include <Adafruit_Sensor.h>
#include <MAX30100_PulseOximeter.h>
#include <Wire.h>

#define MPU9250_ADDR 0x68
#define sampleInterval 1
MPU9250_WE myMPU9250 = MPU9250_WE(MPU9250_ADDR);
PulseOximeter pox;
uint32_t tsLastReport = 0;
uint32_t fdLastReport = 0;
const float fallThreshold = 1500; //650000;
float prevAccX = 0.0, prevAccY = 0.0, prevAccZ = 0.0;

void onBeatDetected(){
    //Serial.println("Beat!");
    return;
}

void setup() {
  // setting the commutionction rate - baud rate
  Serial.begin(115200);
  // set pins for I2C commutication 
  Wire.begin(32, 33);

  // pin setting for ECG sensor 
  pinMode(12, INPUT);
  pinMode(13, INPUT);

  while(!Serial){
    delay(10);
  }

  // checks if MPU9250 is responding 
  if(!myMPU9250.init()){
    Serial.println("MPU9250 does not respond");
  }
  else{
    Serial.println("MPU9250 is connected");
  }
  Serial.println("Position you MPU9250 flat and don't move it - calibrating...");
  delay(1000);
  myMPU9250.autoOffsets();
  Serial.println("Done!");
  
  // setup for MPU9250
  myMPU9250.enableGyrDLPF();
  myMPU9250.setGyrDLPF(MPU9250_DLPF_6);
  myMPU9250.setSampleRateDivider(5);
  myMPU9250.setGyrRange(MPU9250_GYRO_RANGE_250);
  myMPU9250.setAccRange(MPU9250_ACC_RANGE_2G);
  myMPU9250.enableAccDLPF(true);
  myMPU9250.setAccDLPF(MPU9250_DLPF_6);
  myMPU9250.setMagOpMode(AK8963_CONT_MODE_100HZ);
  delay(200);

  // checks if PulseOximeter is responding 
  if(!pox.begin()){
    Serial.println("PulseOximeter is not connected!");
    while(1){
      delay(100);
    } 
  }
  Serial.println("PulseOximeter connected");
  pox.setOnBeatDetectedCallback(onBeatDetected);
  
}

void loop() {
  // updates the Pulse Oximeter
  pox.update();

  // ECG reporting logic
  if((digitalRead(12) == 0) && (digitalRead(13) == 0)){
    Serial.println(analogRead(14));
  }
  //Wait for a bit to keep serial data from saturating
  delay(1);

  // Fall detection logic
  if(millis() - fdLastReport > sampleInterval){
    // get values of g from the sensor 
    xyzFloat gValue = myMPU9250.getGValues();
    
    // calculation of jerk, rate of change of acceleration for each direction
    float jerkX = (gValue.x - prevAccX) / (sampleInterval / 1000.0);
    float jerkY = (gValue.y - prevAccY) / (sampleInterval / 1000.0);
    float jerkZ = (gValue.z - prevAccZ) / (sampleInterval / 1000.0);

    // updating the last values
    prevAccX = gValue.x;
    prevAccY = gValue.y;
    prevAccZ = gValue.z;

    // magnitue of jerk 
    float jerkMagnitude = sqrt(jerkX * jerkX + jerkY * jerkY + jerkZ * jerkZ);
    //Serial.println(jerkMagnitude);

    if (jerkMagnitude > fallThreshold){
      Serial.println("Fall detected!");
    }
    fdLastReport = millis();
  }

  // SpO2 and heart rate logic 
  if (millis() - tsLastReport > 1000){
    // printing the data from the pulseoximeter 
    Serial.print("Heart rate:");
    Serial.print(pox.getHeartRate());
    Serial.print("bpm / SpO2:");
    Serial.print(pox.getSpO2());
    Serial.println("%");

    float temp = myMPU9250.getTemperature();
  
    Serial.print("Ambient Temperature in °C: ");
    Serial.println(temp);
  
    Serial.println("");
    tsLastReport = millis();
  }

}
