<template>
  <app-alert :alerts="alerts"></app-alert>
</template>

<script>
import Alerts from './components/Alerts/Alerts.vue'

export default {
  name: 'Alerts',
  components: {
    AppAlert: Alerts
  },

  data() {
    return {
      alerts: []
    }
  },

  methods: {
    sendAlert(alert) {
      this.alerts.push(alert)

      window.setTimeout(() => {
        this.removeAlert(alert)
      }, 3500)
    },
    removeAlert(alert) {
      this.alerts.splice(this.alerts.indexOf(alert), 1);
    }
  },
}
</script>
