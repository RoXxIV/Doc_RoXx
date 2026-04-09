# Todo

## ~~1. Régénérer un fichier ou un bloc précis~~ ✓

Deux modes ciblés en CLI :

```bash
python doc.py --file TaskDashboard.vue   # régénère uniquement les docs qui utilisent des blocs de ce fichier source
python doc.py --block TASK_ADD           # régénère uniquement les docs qui contiennent l'ancre #TASK_ADD
```

---

## ~~3. Mode strict sur les doublons~~ ✓

Deux comportements au choix via flag :

```bash
python doc.py --strict   # arrête l'exécution au premier doublon, pointe le fichier et la ligne
python doc.py            # comportement actuel : continue avec un [WARN] et garde le premier bloc
```

Dans les deux cas, le message d'erreur doit indiquer les deux fichiers concernés et le nom du bloc.

---

## ~~4. Lister les ancres disponibles~~ ✓

```bash
python doc.py --list
```

Affiche tous les blocs trouvés avec leur fichier source :

```
TASK_STRUCT        TaskManager.cpp
TASK_ADD           TaskManager.cpp
TASK_REMOVE        TaskManager.cpp
TASK_LIST          TaskManager.cpp
TASK_MARK_DONE     TaskManager.cpp
TASK_FIND          TaskManager.cpp
DASHBOARD_TEMPLATE TaskDashboard.vue
DASHBOARD_SCRIPT   TaskDashboard.vue
DASHBOARD_STYLE    TaskDashboard.vue
```

---

## ~~5. CLI package~~ ✓

Transformer le projet en package pip installable.

```bash
pip install .        # install local
pip install -e .     # install en mode éditable (dev)
doc-roxx             # commande disponible partout
doc-roxx --list
doc-roxx --strict
doc-roxx --doc docs/specific.md
```

Restructuration nécessaire :
- Déplacer `doc.py` dans `doc_roxx/cli.py`
- Ajouter `doc_roxx/__init__.py`
- Ajouter `pyproject.toml` avec entry point `doc-roxx = "doc_roxx.cli:main"`
