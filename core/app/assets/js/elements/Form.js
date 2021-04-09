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

        this.statusFieldName = form.dataset.statusField
        if (this.statusFieldName) {
            this.trueSuccessMessage = form.dataset.trueSuccess
            this.falseSuccessMessage = form.dataset.falseSuccess
            this.statusField = this.form[this.statusFieldName]
        } else {
            this.successMessage = form.dataset.successMessage
            if (!this.successMessage) {
                throw new Error(`Missing data-success-message property.`)
            }
        }

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

    sendSuccessAlert() {
        if (this.statusField) {
            if (this.statusField.checked && this.trueSuccessMessage) {
                return window.sendAlert({
                    type: 'success',
                    message: this.trueSuccessMessage
                })
            }

            if (!this.statusField.checked && this.falseSuccessMessage) {
                return window.sendAlert({
                    type: 'success',
                    message: this.falseSuccessMessage
                })
            }
        }

        return window.sendAlert({
            type: 'success',
            message: this.successMessage
        })
    }

    asyncSubmit() {
        const data = new FormData(this.form)

        jsonFetch(this.form.action, CSRF, {
            body: data
        }).then(() => {
            this.sendSuccessAlert()
        }).catch(e => {
            if (e.status === 400) {
                // @TODO
                console.log(this.form.elements)
                console.log('wrong form')
            }
            console.error(e)
        })

    }
}
