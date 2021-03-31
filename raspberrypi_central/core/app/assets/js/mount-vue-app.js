import {createApp} from 'vue'
import App from './App.vue'
import MountAlerts from './MountAlerts.vue'
import {DialogManager} from '../state/dialog-state'

const app = createApp(App)
export const mounted = app.mount('#app')

const alertsApp = createApp(MountAlerts)
export const alertsAppMounted = alertsApp.mount('#alerts')

window.sendAlert = alertsAppMounted.sendAlert

export const dialogManager = new DialogManager(mounted)
