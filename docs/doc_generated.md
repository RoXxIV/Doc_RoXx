# Démo de documentation ancrée — FreeRTOS ESP32

Ce document sert à tester un système simple de génération de documentation à partir de blocs de code annotés dans plusieurs fichiers source.

Le projet repose sur trois fichiers :

- `main.cpp` : point d’entrée du programme
- `led.cpp` : gestion de la LED et de la task associée
- `button.cpp` : gestion du bouton et de la task associée

L’objectif fonctionnel est simple :

- une task pilote une LED
- une autre task surveille un bouton
- un appui sur le bouton change la vitesse de clignotement

---

## Vue d’ensemble

Le programme démarre sur ESP32, initialise les entrées/sorties, crée un mutex partagé, puis lance deux tasks FreeRTOS :

- `ledTask`
- `buttonTask`

La variable globale `g_blinkDelayMs` contient la période de clignotement actuelle.  
Cette valeur est protégée par `g_sharedMutex` pour éviter un accès concurrent non contrôlé entre les tasks.

---

## Point d’entrée principal

La fonction `setup()` initialise tout le système :

- ouverture de la liaison série
- création du mutex
- initialisation des modules LED et bouton
- création des deux tasks

**`main.cpp`**
```cpp
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
```

La fonction `loop()` ne contient pas de logique métier.  
Le vrai travail est délégué aux tasks FreeRTOS.

**`main.cpp`**
```cpp
void loop()
{
    vTaskDelay(pdMS_TO_TICKS(1000));
}
```

---

## Initialisation de la LED

Le module LED prépare la broche en sortie et force un état initial bas.

**`led.cpp`**
```cpp
void initLed()
{
    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, LOW);
}
```

Cette étape isole la configuration matérielle dans une fonction dédiée.  
Cela évite de mélanger la configuration GPIO avec la logique de scheduling FreeRTOS.

---

## Lecture sécurisée du délai partagé

La task LED n’utilise pas directement la variable globale `g_blinkDelayMs`.  
Elle passe par une fonction intermédiaire qui lit la valeur sous protection du mutex.

**`led.cpp`**
```cpp
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
```

Cette approche est utile pour deux raisons :

1. elle centralise l’accès à la donnée partagée
2. elle rend le code plus lisible qu’un accès mutex dispersé partout

---

## Task LED

La task LED tourne en boucle infinie.

Son comportement :

- lire le délai courant
- inverser l’état de la LED
- afficher une trace série
- attendre le délai demandé

**`led.cpp`**
```cpp
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
```

Ici, la LED représente un exemple simple d’action périodique.  
Dans un vrai projet embarqué, cette task pourrait être remplacée par :

- une lecture capteur
- un envoi MQTT
- une mise à jour d’écran
- une surveillance d’état machine

---

## Initialisation du bouton

Le bouton est configuré en `INPUT_PULLUP`.

**`button.cpp`**
```cpp
void initButton()
{
    pinMode(BUTTON_PIN, INPUT_PULLUP);
}
```

Cela implique généralement :

- état repos = `HIGH`
- appui = `LOW`

Ce choix est fréquent en embarqué car il simplifie le câblage.

---

## Mise à jour du délai de clignotement

Quand un appui est détecté, la task bouton appelle une fonction dédiée qui modifie `g_blinkDelayMs`.

**`button.cpp`**
```cpp
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
```

Le cycle retenu dans cet exemple est :

- `500 ms`
- `200 ms`
- `1000 ms`
- puis retour à `500 ms`

La mise à jour passe elle aussi par le mutex, ce qui garde une logique cohérente entre lecture et écriture.

---

## Task bouton

La task bouton lit régulièrement l’entrée numérique et détecte un front d’appui simple :

- état précédent = `HIGH`
- état courant = `LOW`

**`button.cpp`**
```cpp
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
```

Cette task inclut aussi un petit délai anti-rebond rudimentaire avec :

- un `vTaskDelay(200 ms)` après détection
- un polling périodique toutes les `20 ms`

Pour une version plus sérieuse, on pourrait ensuite améliorer :

- l’anti-rebond
- la gestion des événements
- l’envoi d’un signal via queue ou notification FreeRTOS

---

## Résumé architectural

Le projet montre un cas très simple mais réaliste de séparation des responsabilités :

### `main.cpp`

- initialise le système
- crée les tasks
- contient les ressources partagées globales

### `led.cpp`

- gère la sortie LED
- lit la configuration de clignotement
- exécute la task d’affichage lumineux

### `button.cpp`

- gère l’entrée bouton
- modifie la vitesse de clignotement
- exécute la task de surveillance d’entrée

---

## Blocs de code inclus dans ce document

Ce document référence actuellement les ancres suivantes :

- `MAIN_SETUP`
- `MAIN_LOOP`
- `LED_INIT`
- `LED_GET_DELAY`
- `LED_TASK`
- `BUTTON_INIT`
- `BUTTON_UPDATE_DELAY`
- `BUTTON_TASK`

Si ton script fonctionne correctement, chaque ligne `!INCLUDE ...` doit être remplacée par le bloc de code correspondant.

---

## Ce que tu dois vérifier pendant ton test

Après exécution du script :

1. chaque ancre `!INCLUDE ...` doit avoir disparu
2. chaque bloc doit apparaître dans une fenced code block Markdown
3. le langage du bloc doit être `cpp`
4. un bloc manquant doit être remplacé par un commentaire HTML

Exemple attendu pour un bloc absent :

```html
<!-- Missing block: NOM_DU_BLOC -->
```

## API du module LED

**`led.h`**
```cpp
void initLed();
uint32_t getBlinkDelay();
void ledTask(void *parameter);
```

## API du module bouton

**`button.h`**
```cpp
void initButton();
void updateBlinkDelay();
void buttonTask(void *parameter);
```

---

## Dashboard web (Vue.js)

Le projet expose également une interface web embarquée sur l'ESP32 permettant de visualiser l'état de la LED et de changer le délai de clignotement à distance.

### Template HTML

Structure du composant : un indicateur LED, l'affichage du délai courant et deux boutons de contrôle.

**`LedDashboard.vue`**
```html
<div class="dashboard">
    <h2>ESP32 LED Dashboard</h2>
    <div class="status">
      <span class="led-indicator" :class="{ active: ledOn }"></span>
      <span>Blink delay : <strong>{{ blinkDelay }} ms</strong></span>
    </div>
    <div class="controls">
      <button @click="changeDelay">Changer le délai</button>
      <button @click="fetchStatus">Rafraîchir</button>
    </div>
    <p class="hint">
      Cycle : 500 ms → 200 ms → 1000 ms → 500 ms
    </p>
  </div>
```

### Script

Le composant interroge l'ESP32 via `/api/status` toutes les secondes et envoie une requête POST sur `/api/button` pour simuler un appui.

**`LedDashboard.vue`**
```js
export default {
  name: 'LedDashboard',
  data() {
    return {
      blinkDelay: 500,
      ledOn: false,
      pollInterval: null,
    }
  },
  methods: {
    async fetchStatus() {
      const res = await fetch('/api/status')
      const data = await res.json()
      this.blinkDelay = data.blinkDelay
      this.ledOn = data.ledOn
    },
    async changeDelay() {
      await fetch('/api/button', { method: 'POST' })
      await this.fetchStatus()
    },
  },
  mounted() {
    this.fetchStatus()
    this.pollInterval = setInterval(this.fetchStatus, 1000)
  },
  beforeUnmount() {
    clearInterval(this.pollInterval)
  },
}
```

### Style

**`LedDashboard.vue`**
```css
.dashboard {
  font-family: sans-serif;
  max-width: 320px;
  padding: 1.5rem;
  border: 1px solid #ddd;
  border-radius: 8px;
}
.status {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
}
.led-indicator {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #ccc;
  margin-right: 10px;
  transition: background 0.2s;
}
.led-indicator.active {
  background: #4caf50;
  box-shadow: 0 0 6px #4caf50;
}
.controls button {
  margin-right: 8px;
  padding: 6px 14px;
  cursor: pointer;
}
.hint {
  font-size: 0.8rem;
  color: #888;
  margin-top: 1rem;
}
```

---

## Blocs imbriqués — test

Cette section vérifie le support des blocs imbriqués.

`BUTTON_INIT` est le bloc parent : il contient la fonction complète.  
`BUTTON_BODY` est le bloc enfant : il contient uniquement la ligne `pinMode`.

### Bloc parent (BUTTON_INIT)

Les lignes d'annotation `BUTTON_BODY` ne doivent pas apparaître dans le rendu.

**`button.cpp`**
```cpp
void initButton()
{
    pinMode(BUTTON_PIN, INPUT_PULLUP);
}
```

### Bloc enfant (BUTTON_BODY)

Seule la ligne `pinMode` doit apparaître.

**`button.cpp`**
```cpp
pinMode(BUTTON_PIN, INPUT_PULLUP);
```

---

## Paramètres `!INCLUDE` — test

### `filename:false` — masquer le nom de fichier

Le yaml a `include_filename: true`, donc le nom s'affiche partout par défaut.  
Ici on le masque explicitement pour ce bloc.

```cpp
void initLed()
{
    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, LOW);
}
```

### `lang:` — override du langage

Le même bloc `LED_INIT`, mais rendu en `c` au lieu de `cpp`.

```c
void initLed()
{
    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, LOW);
}
```

### Cumul des deux paramètres

`MAIN_SETUP` affiché avec `filename:true` (redondant ici car global = true, mais valide) et `lang:` forcé en `c`.

**`main.cpp`**
```c
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
```
