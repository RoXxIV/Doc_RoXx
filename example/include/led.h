#pragma once

#include <Arduino.h>

// #LED_DECLARATIONS#BEGIN
void initLed();
uint32_t getBlinkDelay();
void ledTask(void *parameter);
// #LED_DECLARATIONS#END