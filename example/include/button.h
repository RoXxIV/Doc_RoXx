#pragma once

#include <Arduino.h>

// #BUTTON_DECLARATIONS#BEGIN
void initButton();
void updateBlinkDelay();
void buttonTask(void *parameter);
// #BUTTON_DECLARATIONS#END