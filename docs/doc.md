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

!INCLUDE MAIN_SETUP

La fonction `loop()` ne contient pas de logique métier.  
Le vrai travail est délégué aux tasks FreeRTOS.

!INCLUDE MAIN_LOOP

---

## Initialisation de la LED

Le module LED prépare la broche en sortie et force un état initial bas.

!INCLUDE LED_INIT

Cette étape isole la configuration matérielle dans une fonction dédiée.  
Cela évite de mélanger la configuration GPIO avec la logique de scheduling FreeRTOS.

---

## Lecture sécurisée du délai partagé

La task LED n’utilise pas directement la variable globale `g_blinkDelayMs`.  
Elle passe par une fonction intermédiaire qui lit la valeur sous protection du mutex.

!INCLUDE LED_GET_DELAY

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

!INCLUDE LED_TASK

Ici, la LED représente un exemple simple d’action périodique.  
Dans un vrai projet embarqué, cette task pourrait être remplacée par :

- une lecture capteur
- un envoi MQTT
- une mise à jour d’écran
- une surveillance d’état machine

---

## Initialisation du bouton

Le bouton est configuré en `INPUT_PULLUP`.

!INCLUDE BUTTON_INIT

Cela implique généralement :

- état repos = `HIGH`
- appui = `LOW`

Ce choix est fréquent en embarqué car il simplifie le câblage.

---

## Mise à jour du délai de clignotement

Quand un appui est détecté, la task bouton appelle une fonction dédiée qui modifie `g_blinkDelayMs`.

!INCLUDE BUTTON_UPDATE_DELAY

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

!INCLUDE BUTTON_TASK

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

!INCLUDE LED_DECLARATIONS

## API du module bouton

!INCLUDE BUTTON_DECLARATIONS

---

## Dashboard web (Vue.js)

Le projet expose également une interface web embarquée sur l'ESP32 permettant de visualiser l'état de la LED et de changer le délai de clignotement à distance.

### Template HTML

Structure du composant : un indicateur LED, l'affichage du délai courant et deux boutons de contrôle.

!INCLUDE VUE_TEMPLATE

### Script

Le composant interroge l'ESP32 via `/api/status` toutes les secondes et envoie une requête POST sur `/api/button` pour simuler un appui.

!INCLUDE VUE_SCRIPT

### Style

!INCLUDE VUE_STYLE

---

## Blocs imbriqués — test

Cette section vérifie le support des blocs imbriqués.

`BUTTON_INIT` est le bloc parent : il contient la fonction complète.  
`BUTTON_BODY` est le bloc enfant : il contient uniquement la ligne `pinMode`.

### Bloc parent (BUTTON_INIT)

Les lignes d'annotation `BUTTON_BODY` ne doivent pas apparaître dans le rendu.

!INCLUDE BUTTON_INIT

### Bloc enfant (BUTTON_BODY)

Seule la ligne `pinMode` doit apparaître.

!INCLUDE BUTTON_BODY

---

## Paramètres `!INCLUDE` — test

### `filename:false` — masquer le nom de fichier

Le yaml a `include_filename: true`, donc le nom s'affiche partout par défaut.  
Ici on le masque explicitement pour ce bloc.

!INCLUDE LED_INIT filename:false

### `lang:` — override du langage

Le même bloc `LED_INIT`, mais rendu en `c` au lieu de `cpp`.

!INCLUDE LED_INIT lang:c filename:false

### Cumul des deux paramètres

`MAIN_SETUP` affiché avec `filename:true` (redondant ici car global = true, mais valide) et `lang:` forcé en `c`.

!INCLUDE MAIN_SETUP lang:c filename:true
