#include <Arduino.h>
#include "led.h"
#include "button.h"

volatile uint32_t g_blinkDelayMs = 500;
SemaphoreHandle_t g_sharedMutex = nullptr;

// #MAIN_SETUP#BEGIN
void setup()
{
    Serial.begin(115200);
    delay(500);

    g_sharedMutex = xSemaphoreCreateMutex();

    initLed();
    initButton();

    xTaskCreatePinnedToCore(
        ledTask,
        "LED_TASK",
        2048,
        nullptr,
        1,
        nullptr,
        1);

    xTaskCreatePinnedToCore(
        buttonTask,
        "BUTTON_TASK",
        2048,
        nullptr,
        1,
        nullptr,
        1);

    Serial.println("System started");
}
// #MAIN_SETUP#END

// #MAIN_LOOP#BEGIN
void loop()
{
    vTaskDelay(pdMS_TO_TICKS(1000));
}
// #MAIN_LOOP#END