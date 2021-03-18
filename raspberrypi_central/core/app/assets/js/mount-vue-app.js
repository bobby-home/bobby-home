import {createApp} from 'vue'
import App from './App.vue'
import {DialogManager} from '../state/dialog-state'

const app = createApp(App)
export const mounted = app.mount('#app')

export const dialogManager = new DialogManager(mounted)
