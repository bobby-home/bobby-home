import {jsonFetch} from '../ajaxify'
import {dialogManager} from "../mount-vue-app"

export class Form extends HTMLFormElement {

    constructor() {
        super()
        this.dialogManager = dialogManager

        this.submitListener = null
        this.form = null

        this.asyncSubmit = this.asyncSubmit.bind(this)
    }

    connectedCallback() {
        const form = this
        this.form = this

        this.isDialog = 'dialog' in form.dataset
        if (this.isDialog) {
            this.dialog = {
                title: form.dataset.dialogTitle,
                content: form.dataset.dialogContent
            }
        }

        this.submitListener = form.addEventListener('submit', e => {
            e.preventDefault()

            if (this.isDialog) {
                this.openDialog()
            } else {
                this.asyncSubmit()
            }
        })
    }

    disconnectedCallback() {
        if (this.this.submitListener) {
            this.removeEventListener('click', this.submitListener)
        }
    }

    openDialog() {
        this.dialogManager.open(this.dialog, this.asyncSubmit)
    }

    asyncSubmit() {
        const data = new FormData(this.form)

        jsonFetch(this.form.action, CSRF, {
            body: data
        }).then(() => {
            console.log('Request has been made - ok.')
        }).catch(e => {
            if (e.status === 400) {
                console.log(this.form.elements)
                console.log('wrong form')
            }
            console.error(e)
        })

    }
}
