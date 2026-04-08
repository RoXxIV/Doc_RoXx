<template>
  <!-- #VUE_TEMPLATE#BEGIN:html -->
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
  <!-- #VUE_TEMPLATE#END -->
</template>

<script>
// #VUE_SCRIPT#BEGIN:js
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
// #VUE_SCRIPT#END
</script>

<style>
/* #VUE_STYLE#BEGIN:css */
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
/* #VUE_STYLE#END */
</style>
