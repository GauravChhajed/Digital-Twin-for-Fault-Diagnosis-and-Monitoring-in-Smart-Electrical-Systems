#include <LiquidCrystal_I2C.h>
#include <DHT.h>
#include "ACS712.h"

// Pin Definitions
const int potPin = A1;       // Potentiometer wiper
const int fanRelayPin = 2;   // Fan control relay
const int primaryRelayPin = A3; // Main relay for load
const int buzzerPin = 6;     // Buzzer alarm
const int dhtPin = 7;        // DHT11 data pin

// LCD Setup
LiquidCrystal_I2C lcd(0x27, 16, 2); // Change I2C address if needed

// DHT Setup
#define DHTTYPE DHT11
DHT dht(dhtPin, DHTTYPE);

// ACS712 Setup
ACS712 sensor(A0, 5.0, 185); // ACS712-05B (185mV per A)

// Thresholds (Adjust as needed)
const float currentThresholdHigh = 0.415; // High current limit (relay off)
const float currentThresholdLow = 0.19;  // Low current limit (relay on)
const float currentThresholdCutOff = 0.05; // Power cut-off threshold
const float voltageThresholdLow = 180.0; // Minimum acceptable voltage
const float voltageThresholdHigh = 240.0; // Maximum acceptable voltage
const float tempThreshold = 42.0; // Maximum allowed temperature (°C)
const int overcurrentThreshold = 5; // Number of continuous overcurrent readings before shutdown

// Relay & Protection State Variables
bool relayState = true; // True = Relay ON, False = Relay OFF
int overcurrentCount = 0;

void setup() {
  Serial.begin(9600);
  lcd.init();
  lcd.backlight();
  
  pinMode(fanRelayPin, OUTPUT);
  digitalWrite(fanRelayPin, HIGH); // Fan off initially (active low relay)
  
  pinMode(primaryRelayPin, OUTPUT);
  digitalWrite(primaryRelayPin, LOW); // Primary relay off initially
  
  pinMode(buzzerPin, OUTPUT);
  digitalWrite(buzzerPin, LOW); // Buzzer off initially

  dht.begin();
}

void loop() {
  // Read Sensor Values
  float current = getACCurrentFiltered(); // RMS current reading with filtering
  float voltage = readVoltage(); // Read scaled voltage value
  float dhtTemp = dht.readTemperature();

  // Display Data on LCD
  displayData(current, voltage, dhtTemp);

  // Check Conditions & Control Relays
  checkThresholds(current, voltage, dhtTemp);

  // Print to Serial Monitor for Debugging
  Serial.print(current);
  Serial.print(",");
  Serial.print(voltage);
  Serial.print(",");
  Serial.println(dhtTemp);

  delay(1000); // Stabilization delay
}

// Function to measure AC current with filtering
float getACCurrentFiltered() {
  const int sampleCount = 1000; // Number of samples for averaging
  float sumSquares = 0.0;
  
  for (int i = 0; i < sampleCount; i++) {
    float sensorValue = analogRead(A0) - 512; // Center around zero
    float voltage = sensorValue * (5.0 / 1023.0); // Convert to voltage
    float current = voltage / 0.08; // Convert to current (100mV per A)
    sumSquares += current * current; // Sum of squares
    delayMicroseconds(500); // Sampling delay
  }
  
  float rmsCurrent = sqrt(sumSquares / sampleCount); // RMS Calculation
  
  // Apply moving average filter to smooth fluctuations
  static float lastCurrent = 0.0;
  rmsCurrent = (lastCurrent * 0.6) + (rmsCurrent * 0.4); // Weighted average
  lastCurrent = rmsCurrent;
  
  return rmsCurrent;
}

// Function to read voltage
float readVoltage() {
  int sensorValue = analogRead(potPin);
  float voltage = (sensorValue / 1023.0) * 5.0;
  float scaledVoltage = voltage * 65; // Adjusted scaling factor
  return scaledVoltage;
}

// Function to display data on LCD
void displayData(float current, float voltage, float dhtTemp) {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("C:");
  lcd.print(current);
  lcd.print("A");
  
  lcd.setCursor(8, 0);
  lcd.print("T:");
  lcd.print(dhtTemp);
  
  lcd.setCursor(0, 1);
  lcd.print("V:");
  lcd.print(voltage);
  lcd.print("V");
}

// Function to check thresholds and control relays
void checkThresholds(float current, float voltage, float dhtTemp) {
  bool errorState = false;

  // Check overcurrent condition
  if (current > currentThresholdHigh) {
    overcurrentCount++;
    if (overcurrentCount > overcurrentThreshold) {
      errorState = true;
    }
  } else {
    overcurrentCount = 0; // Reset overcurrent count if current is normal
  }

  // If voltage is outside acceptable range, shut down
  if (voltage < voltageThresholdLow || voltage > voltageThresholdHigh) {
    errorState = true;
  }

  // If temperature is too high, shut down
  if (dhtTemp > tempThreshold) {
    errorState = true;
  }

  // If error state is detected, turn off the relay and sound the alarm
  if (errorState) {
    digitalWrite(primaryRelayPin, HIGH); // Turn relay OFF
    digitalWrite(buzzerPin, HIGH); // Sound buzzer
    lcd.setCursor(15, 0);
    lcd.print("!");
    relayState = false;
  } 
  // Restore operation if conditions return to normal
  else if (current < currentThresholdLow && !relayState && current > currentThresholdCutOff && dhtTemp <= tempThreshold) {
    digitalWrite(primaryRelayPin, LOW); // Turn relay ON
    digitalWrite(buzzerPin, LOW); // Turn buzzer OFF
    lcd.setCursor(15, 0);
    lcd.print(" ");
    relayState = true;
  } else if (voltage >= voltageThresholdLow && voltage <= voltageThresholdHigh && dhtTemp <= tempThreshold && relayState) {
    digitalWrite(buzzerPin, LOW);
    lcd.setCursor(15, 0);
    lcd.print(" ");
  }

  // Fan control based on load and temperature
  if (current > 0.415 || voltage > 240 || dhtTemp > tempThreshold) {
    digitalWrite(fanRelayPin, LOW); // Fan ON (active low)
  } else {
    digitalWrite(fanRelayPin, HIGH); // Fan OFF (active low)
  }
}
