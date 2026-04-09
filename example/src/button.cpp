#include <Arduino.h>

extern volatile uint32_t g_blinkDelayMs;
extern SemaphoreHandle_t g_sharedMutex;

static const uint8_t BUTTON_PIN = 18;

// #BUTTON_INIT#BEGIN
void initButton()
{
    // #BUTTON_BODY#BEGIN
    pinMode(BUTTON_PIN, INPUT_PULLUP);
    // #BUTTON_BODY#END
}
// #BUTTON_INIT#END

// #BUTTON_UPDATE_DELAY#BEGIN
void updateBlinkDelay()
{
    if (g_sharedMutex == nullptr)
        return;

    if (xSemaphoreTake(g_sharedMutex, pdMS_TO_TICKS(50)) == pdTRUE)
    {
        if (g_blinkDelayMs == 500)
            g_blinkDelayMs = 200;
        else if (g_blinkDelayMs == 200)
            g_blinkDelayMs = 1000;
        else
            g_blinkDelayMs = 500;

        Serial.print("[BUTTON] New blink delay = ");
        Serial.println(g_blinkDelayMs);

        xSemaphoreGive(g_sharedMutex);
    }
}
// #BUTTON_UPDATE_DELAY#END

// #BUTTON_TASK#BEGIN
void buttonTask(void *parameter)
{
    (void)parameter;

    bool lastState = HIGH;

    for (;;)
    {
        bool currentState = digitalRead(BUTTON_PIN);

        if (lastState == HIGH && currentState == LOW)
        {
            updateBlinkDelay();
            vTaskDelay(pdMS_TO_TICKS(200));
        }

        lastState = currentState;
        vTaskDelay(pdMS_TO_TICKS(20));
    }
}
// #BUTTON_TASK#END