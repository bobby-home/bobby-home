import {createApp} from 'vue'
import App from './App.vue'
import MountAlerts from './MountAlerts.vue'
import {DialogManager} from '../state/dialog-state'

const app = createApp(App)
export const mounted = app.mount('#app')

const alertsApp = createApp(MountAlerts)
export const alertsAppMounted = alertsApp.mount('#alerts')

alertsAppMounted.sendAlert({
    type: 'success',
    message: 'hello world'
})

alertsAppMounted.sendAlert({
    type: 'error',
    message: 'hello world'
})

export const dialogManager = new DialogManager(mounted)
