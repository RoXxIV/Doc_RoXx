#include <Arduino.h>

extern volatile uint32_t g_blinkDelayMs;
extern SemaphoreHandle_t g_sharedMutex;

static const uint8_t LED_PIN = 2;

// #LED_INIT#BEGIN
void initLed()
{
    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, LOW);
}
// #LED_INIT#END

// #LED_GET_DELAY#BEGIN
uint32_t getBlinkDelay()
{
    uint32_t value = 500;

    if (g_sharedMutex != nullptr)
    {
        if (xSemaphoreTake(g_sharedMutex, pdMS_TO_TICKS(50)) == pdTRUE)
        {
            value = g_blinkDelayMs;
            xSemaphoreGive(g_sharedMutex);
        }
    }

    return value;
}
// #LED_GET_DELAY#END

// #LED_TASK#BEGIN
void ledTask(void *parameter)
{
    (void)parameter;

    bool ledState = false;

    for (;;)
    {
        uint32_t delayMs = getBlinkDelay();

        ledState = !ledState;
        digitalWrite(LED_PIN, ledState);

        Serial.print("[LED] Toggle, delay = ");
        Serial.println(delayMs);

        vTaskDelay(pdMS_TO_TICKS(delayMs));
    }
}
// #LED_TASK#END