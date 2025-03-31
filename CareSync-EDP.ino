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
bool fallState = false;


void onBeatDetected()
{
    //Serial.println("Beat!");
    return;
}
void setup() {
  Serial.begin(115200);
  Wire.begin(32, 33);
  while(!Serial){
    delay(10);
  }

  if(!myMPU9250.init()){
    Serial.println("MPU9250 does not respond");
  }
  else{
    Serial.println("MPU9250 is connected");
  }
  if(!myMPU9250.initMagnetometer()){
    Serial.println("Magnetometer does not respond");
  }
  else{
    Serial.println("Magnetometer is connected");
  }

  
  Serial.println("Position you MPU9250 flat and don't move it - calibrating...");
  delay(1000);
  myMPU9250.autoOffsets();
  Serial.println("Done!");

  myMPU9250.enableGyrDLPF();
  myMPU9250.setGyrDLPF(MPU9250_DLPF_6);
  myMPU9250.setSampleRateDivider(5);
  myMPU9250.setGyrRange(MPU9250_GYRO_RANGE_250);
  myMPU9250.setAccRange(MPU9250_ACC_RANGE_2G);
  myMPU9250.enableAccDLPF(true);
  myMPU9250.setAccDLPF(MPU9250_DLPF_6);
  myMPU9250.setMagOpMode(AK8963_CONT_MODE_100HZ);
  delay(200);


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
  pox.update();

  if(millis() - fdLastReport > sampleInterval){
    xyzFloat gValue = myMPU9250.getGValues();

    float jerkX = (gValue.x - prevAccX) / (sampleInterval / 1000.0);
    float jerkY = (gValue.y - prevAccY) / (sampleInterval / 1000.0);
    float jerkZ = (gValue.z - prevAccZ) / (sampleInterval / 1000.0);

    prevAccX = gValue.x;
    prevAccY = gValue.y;
    prevAccZ = gValue.z;

    float jerkMagnitude = sqrt(jerkX * jerkX + jerkY * jerkY + jerkZ * jerkZ);
    //Serial.println(jerkMagnitude);

    if (jerkMagnitude > fallThreshold){
      Serial.println("Fall detected!");
    }
    fdLastReport = millis();
  }

  if (millis() - tsLastReport > 1000){
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
