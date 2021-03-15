import '../css/app.scss'

import {createApp} from 'vue'
import App from '../App.vue'
import {DialogManager} from '../state/dialog-state'
import {FormHandler} from '../js/form/form-handler'
import {ThemeChoice} from "../js/elements/ThemeChoice";

const app = createApp(App)
const mounted = app.mount('#app')

const dialogManager = new DialogManager(mounted)


const forms = document.querySelectorAll('form.ajaxify')

forms.forEach(form => {
  new FormHandler(form, dialogManager)
})

customElements.define('theme-choice', ThemeChoice)
