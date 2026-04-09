# Doc_RoXx

Générateur de documentation Markdown à partir de blocs de code annotés dans des fichiers source.

Le principe : tu annotes des sections de ton code avec des balises, tu places des directives `!INCLUDE` dans un fichier Markdown template, et le script génère un nouveau fichier Markdown avec les blocs de code injectés automatiquement.

---

## Structure du projet

```
.
├── doc.py             # Script de génération
├── config.yaml        # Configuration (sources, langages, docs)
├── example/           # Exemple de projet source (C++ / Vue.js)
│   └── src/
└── docs/
    ├── doc.md         # Template Markdown (input)
    └── doc_generated.md  # Documentation générée (output)
```

---

## Utilisation

### 1. Annoter le code source

Encadre les sections à extraire avec des balises dans tes fichiers source :

```cpp
// #MON_BLOC#BEGIN
void maFonction() {
    // ...
}
// #MON_BLOC#END
```

Les balises fonctionnent dans tous les langages supportés (commentaires mis de côté, seul le contenu entre les balises est extrait).

#### Blocs imbriqués

Tu peux imbriquer des blocs les uns dans les autres. Le bloc enfant est extrait indépendamment, et ses lignes d'annotation sont automatiquement retirées du contenu du bloc parent :

```cpp
// #TASK_MARK_DONE#BEGIN
bool markDone(int id) {
    // #TASK_FIND#BEGIN
    for (auto& task : tasks) {
        if (task.id == id) {
            task.done = true;
            return true;
        }
    }
    return false;
    // #TASK_FIND#END
}
// #TASK_MARK_DONE#END
```

`!INCLUDE TASK_MARK_DONE` → fonction complète, sans les lignes `#TASK_FIND#...`  
`!INCLUDE TASK_FIND` → exactement ce qui est entre ses balises

### 2. Référencer les blocs dans le template Markdown

Dans ton fichier `.md` template, utilise la directive `!INCLUDE` :

```markdown
Voici l'implémentation de ma fonction :

!INCLUDE MON_BLOC

Ce bloc fait telle chose...
```

Des paramètres optionnels peuvent être ajoutés, dans n'importe quel ordre :

```markdown
!INCLUDE MON_BLOC lang:html
!INCLUDE MON_BLOC filename:true
!INCLUDE MON_BLOC lang:js filename:false
```

| Paramètre | Valeurs | Description |
|-----------|---------|-------------|
| `lang:xxx` | ex : `cpp`, `js`, `html` | Override le langage du fenced block pour cet include uniquement |
| `filename:true/false` | `true` ou `false` | Affiche ou masque le nom du fichier source, indépendamment du `include_filename` global du yaml |

### 3. Configurer `config.yaml`

```yaml
languages:
  .cpp: cpp
  .h: cpp
  .py: python
  # ... autres extensions

sources:
  - ./mon_projet   # Dossiers à scanner (récursif)

docs:
  - input: ./docs/template.md      # Fichier template
    output: ./docs/generated.md    # Fichier généré
    include_filename: true         # Optionnel, false par défaut
```

Le scan des sources est **récursif** : tous les sous-dossiers sont parcourus automatiquement.

#### `include_filename`

Quand `include_filename: true` est activé sur une entrée `docs`, le nom du fichier source est affiché en gras juste au-dessus de chaque bloc de code généré :

````markdown
**`led.cpp`**
```cpp
void initLed() { ... }
```
````

---

### Override de langage par bloc (`:lang`)

Par défaut, le langage d'un bloc est déterminé par l'extension du fichier source (via `languages` dans le config). Pour les fichiers mixtes comme `.vue`, `.svelte` ou les templates, tu peux forcer le langage directement dans la balise `#BEGIN` :

```html
<!-- #VUE_TEMPLATE#BEGIN:html -->
<div>...</div>
<!-- #VUE_TEMPLATE#END -->
```

```js
// #VUE_SCRIPT#BEGIN:js
export default { ... }
// #VUE_SCRIPT#END
```

```css
/* #VUE_STYLE#BEGIN:css */
.container { ... }
/* #VUE_STYLE#END */
```

Le `:lang` est **optionnel** — sans lui, le comportement est inchangé. Il ne sert que pour les blocs où l'extension du fichier ne suffit pas.

### 4. Lancer le script

```bash
pip install pyyaml   # une seule fois
python doc.py        # régénère tous les docs
```

#### Options CLI

| Option | Description |
|--------|-------------|
| `--file TaskDashboard.vue` | Ne régénère que les docs qui utilisent des blocs de ce fichier source |
| `--block TASK_ADD` | Ne régénère que les docs qui référencent cette ancre |

```bash
python doc.py --file TaskDashboard.vue   # cible un fichier source
python doc.py --block TASK_ADD           # cible une ancre précise
```

---

## Résultat

Chaque directive `!INCLUDE MON_BLOC` dans le template est remplacée par un bloc de code Markdown fenced avec le langage correspondant à l'extension du fichier source :

````markdown
```cpp
void maFonction() {
    // ...
}
```
````

Si un bloc référencé est introuvable, il est remplacé par un commentaire HTML :

```html
<!-- Missing block: MON_BLOC -->
```

---

## Langages supportés par défaut

| Extension | Langage Markdown |
|-----------|-----------------|
| `.cpp`    | `cpp`           |
| `.c`      | `c`             |
| `.h`      | `cpp`           |
| `.hpp`    | `cpp`           |
| `.ino`    | `cpp`           |
| `.js`     | `js`            |
| `.ts`     | `ts`            |
| `.html`   | `html`          |
| `.css`    | `css`           |
| `.py`     | `python`        |
| `.json`   | `json`          |

Tu peux ajouter ou modifier les mappings directement dans `config.yaml`.

---

## Exemple

Le dossier `example/` contient un projet de démonstration composé d'un backend C++ (`TaskManager.cpp`) et d'une interface Vue.js (`TaskDashboard.vue`). Le dossier `docs/` contient un template (`doc.md`) qui l'utilise et illustre toutes les fonctionnalités : blocs imbriqués, `lang:` inline, paramètres `!INCLUDE`.

Lance `python doc.py` pour voir le résultat dans `docs/doc_generated.md`.
