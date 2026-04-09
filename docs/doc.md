# Task Manager — Documentation technique

Ce projet implémente un gestionnaire de tâches avec un backend C++ et une interface Vue.js.

- `TaskManager.cpp` : logique métier (ajout, suppression, listing, marquage)
- `TaskDashboard.vue` : interface web (template HTML, script JS, styles CSS)

---

## Modèle de données

Chaque tâche est représentée par une struct simple :

!INCLUDE TASK_STRUCT

Trois champs : un identifiant unique auto-incrémenté, un titre, et un état d'achèvement.

---

## Ajouter une tâche

!INCLUDE TASK_ADD

L'identifiant est attribué automatiquement via `nextId`.

---

## Supprimer une tâche

!INCLUDE TASK_REMOVE

La suppression se fait par id avec `std::remove_if`.

---

## Lister les tâches

!INCLUDE TASK_LIST

Si la liste est vide, un message explicite est affiché.

---

## Marquer une tâche comme terminée

`markDone` parcourt la liste pour trouver la tâche, puis met `done` à `true`.

### Fonction complète

!INCLUDE TASK_MARK_DONE

### Bloc de recherche seul (bloc imbriqué)

Le bloc `TASK_FIND` est imbriqué dans `TASK_MARK_DONE`.  
Il peut être inclus indépendamment — les lignes d'annotation du parent n'apparaissent pas.

!INCLUDE TASK_FIND

---

## Interface Vue.js

Le composant `TaskDashboard.vue` communique avec le backend via des appels REST.

### Template

Les blocs d'un fichier `.vue` utilisent `lang:` inline dans l'annotation `#BEGIN`  
pour que chaque section soit rendue avec le bon langage.

!INCLUDE DASHBOARD_TEMPLATE

### Script

!INCLUDE DASHBOARD_SCRIPT

### Styles

Le bloc suivant utilise `filename:false` pour masquer le nom de fichier sur ce bloc précis,  
même si `include_filename: true` est actif globalement dans le yaml.

!INCLUDE DASHBOARD_STYLE filename:false

---

## Démonstration du paramètre `lang:` dans `!INCLUDE`

Le même bloc `TASK_STRUCT` affiché une seconde fois, mais avec `lang:c` forcé dans la directive.  
Utile pour montrer qu'un même extrait peut être présenté dans un contexte de langage différent.

!INCLUDE TASK_STRUCT lang:c filename:false
