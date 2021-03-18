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
        console.log('remove automaticaly')
      }, 3500)

    },
    removeAlert(alert) {
      this.alerts = this.alerts.filter(a => a !== alert)
    }
  },
}
</script>
