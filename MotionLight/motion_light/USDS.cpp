/*
  HCSR04 - Library for arduino, for HC-SR04 ultrasonic distance sensor.
  Created by Martin Sosic, June 11, 2016.
  Modified by AN
*/

#include "Arduino.h"
#include "USDS.h"

USDS::USDS(int triggerPin, int echoPin) {
  this->triggerPin = triggerPin;
  this->echoPin = echoPin;
  pinMode(triggerPin, OUTPUT);
  pinMode(echoPin, INPUT);
}

double USDS::getDist() {
    //Using the approximate formula 19.307°C results in roughly 343m/s which is the commonly used value for air.
    return getDist(19.307);
}

double USDS::getDist(float temperature) {
  // Make sure that trigger pin is LOW.
  digitalWrite(triggerPin, LOW);
  delayMicroseconds(2);
   
  // Hold trigger for 10 microseconds, which is signal for sensor to measure distance.
  digitalWrite(triggerPin, HIGH);
  delayMicroseconds(10);
  // Measure the length of echo signal, which is equal to the time needed for sound to go there and back.
  digitalWrite(triggerPin, LOW);
  double durationMicroSec = (double)(pulseIn(echoPin, HIGH, 200000));
  
  double speedOfSoundInCmPerMs = 0.03313 + 0.0000606 * temperature; // Cair ≈ (331.3 + 0.606 ⋅ ϑ) m/s
  
  double distanceCm = ((durationMicroSec / 2.0 * speedOfSoundInCmPerMs)*1.0);
  return distanceCm;
}
