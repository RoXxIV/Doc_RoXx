# Task Manager — Documentation technique

Ce projet implémente un gestionnaire de tâches avec un backend C++ et une interface Vue.js.

- `TaskManager.cpp` : logique métier (ajout, suppression, listing, marquage)
- `TaskDashboard.vue` : interface web (template HTML, script JS, styles CSS)

---

## Modèle de données

Chaque tâche est représentée par une struct simple :

**`TaskManager.cpp`**
```cpp
struct Task {
    int id;
    std::string title;
    bool done;
};
```

Trois champs : un identifiant unique auto-incrémenté, un titre, et un état d'achèvement.

---

## Ajouter une tâche

**`TaskManager.cpp`**
```cpp
void addTask(const std::string& title) {
    tasks.push_back({ nextId++, title, false });
    std::cout << "[+] Task added: " << title << "\n";
}
```

L'identifiant est attribué automatiquement via `nextId`.

---

## Supprimer une tâche

**`TaskManager.cpp`**
```cpp
void removeTask(int id) {
    tasks.erase(
        std::remove_if(tasks.begin(), tasks.end(),
            [id](const Task& t) { return t.id == id; }),
        tasks.end()
    );
    std::cout << "[-] Task removed: " << id << "\n";
}
```

La suppression se fait par id avec `std::remove_if`.

---

## Lister les tâches

**`TaskManager.cpp`**
```cpp
void listTasks() {
    if (tasks.empty()) {
        std::cout << "(no tasks)\n";
        return;
    }
    for (const auto& task : tasks) {
        std::cout << "[" << (task.done ? "x" : " ") << "] "
                  << task.id << " - " << task.title << "\n";
    }
}
```

Si la liste est vide, un message explicite est affiché.

---

## Marquer une tâche comme terminée

`markDone` parcourt la liste pour trouver la tâche, puis met `done` à `true`.

### Fonction complète

**`TaskManager.cpp`**
```cpp
bool markDone(int id) {
    for (auto& task : tasks) {
        if (task.id == id) {
            task.done = true;
            return true;
        }
    }
    return false;
}
```

### Bloc de recherche seul (bloc imbriqué)

Le bloc `TASK_FIND` est imbriqué dans `TASK_MARK_DONE`.  
Il peut être inclus indépendamment — les lignes d'annotation du parent n'apparaissent pas.

**`TaskManager.cpp`**
```cpp
for (auto& task : tasks) {
        if (task.id == id) {
            task.done = true;
            return true;
        }
    }
    return false;
```

---

## Interface Vue.js

Le composant `TaskDashboard.vue` communique avec le backend via des appels REST.

### Template

Les blocs d'un fichier `.vue` utilisent `lang:` inline dans l'annotation `#BEGIN`  
pour que chaque section soit rendue avec le bon langage.

**`TaskDashboard.vue`**
```html
<div class="task-manager">
    <h2>Task Manager</h2>
    <div class="add-task">
      <input
        v-model="newTitle"
        placeholder="Nouvelle tâche..."
        @keyup.enter="addTask"
      />
      <button @click="addTask">Ajouter</button>
    </div>
    <ul class="task-list">
      <li
        v-for="task in tasks"
        :key="task.id"
        :class="{ done: task.done }"
      >
        <input type="checkbox" :checked="task.done" @change="toggleDone(task.id)" />
        <span>{{ task.title }}</span>
        <button class="remove" @click="removeTask(task.id)">✕</button>
      </li>
    </ul>
    <p class="summary">{{ remaining }} tâche(s) restante(s)</p>
  </div>
```

### Script

**`TaskDashboard.vue`**
```js
export default {
  name: 'TaskDashboard',
  data() {
    return {
      tasks: [],
      newTitle: '',
    }
  },
  computed: {
    remaining() {
      return this.tasks.filter(t => !t.done).length
    },
  },
  methods: {
    async fetchTasks() {
      const res = await fetch('/api/tasks')
      this.tasks = await res.json()
    },
    async addTask() {
      if (!this.newTitle.trim()) return
      await fetch('/api/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: this.newTitle }),
      })
      this.newTitle = ''
      await this.fetchTasks()
    },
    async removeTask(id) {
      await fetch(`/api/tasks/${id}`, { method: 'DELETE' })
      await this.fetchTasks()
    },
    async toggleDone(id) {
      await fetch(`/api/tasks/${id}/done`, { method: 'PATCH' })
      await this.fetchTasks()
    },
  },
  mounted() {
    this.fetchTasks()
  },
}
```

### Styles

Le bloc suivant utilise `filename:false` pour masquer le nom de fichier sur ce bloc précis,  
même si `include_filename: true` est actif globalement dans le yaml.

```css
.task-manager {
  max-width: 480px;
  font-family: sans-serif;
  padding: 1.5rem;
  border: 1px solid #ddd;
  border-radius: 8px;
}
.add-task {
  display: flex;
  gap: 8px;
  margin-bottom: 1rem;
}
.add-task input {
  flex: 1;
  padding: 6px 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
.task-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.task-list li {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}
.task-list li.done span {
  text-decoration: line-through;
  color: #aaa;
}
.task-list li .remove {
  margin-left: auto;
  background: none;
  border: none;
  cursor: pointer;
  color: #ccc;
}
.task-list li .remove:hover {
  color: #e55;
}
.summary {
  margin-top: 1rem;
  font-size: 0.85rem;
  color: #888;
}
```

---

## Démonstration du paramètre `lang:` dans `!INCLUDE`

Le même bloc `TASK_STRUCT` affiché une seconde fois, mais avec `lang:c` forcé dans la directive.  
Utile pour montrer qu'un même extrait peut être présenté dans un contexte de langage différent.

```c
struct Task {
    int id;
    std::string title;
    bool done;
};
```
