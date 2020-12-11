import {jsonFetch} from '../ajaxify'

export class FormHandler {

    /**
     *
     * @param {HTMLFormElement} form
     * @param {DialogManager} dialogManager
     */
    constructor(form, dialogManager) {
        this.form = form
        this.isDialog = 'dialog' in form.dataset
        this.dialogManager = dialogManager

        this.submit = this.submit.bind(this)

        if (this.isDialog) {
            console.log(form.dataset)
            this.dialog = {
                title: form.dataset.dialogTitle,
                content: form.dataset.dialogContent
            }
        }

        this.form.addEventListener('submit', e => {
            e.preventDefault()

            if (this.isDialog) {
                this.openDialog()
            } else {
                this.submit()
            }

        })
    }

    openDialog() {
        this.dialogManager.open(this.dialog, this.submit)
    }

    submit() {
        const data = new FormData(this.form)

        jsonFetch(this.form.action, CSRF, {
            body: data
        }).then(() => {
            console.log('Request has been made - ok.')
        })

    }
}
