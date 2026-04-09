<template>
  <!-- #DASHBOARD_TEMPLATE#BEGIN:html -->
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
  <!-- #DASHBOARD_TEMPLATE#END -->
</template>

<script>
// #DASHBOARD_SCRIPT#BEGIN:js
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
// #DASHBOARD_SCRIPT#END
</script>

<style>
/* #DASHBOARD_STYLE#BEGIN:css */
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
/* #DASHBOARD_STYLE#END */
</style>
