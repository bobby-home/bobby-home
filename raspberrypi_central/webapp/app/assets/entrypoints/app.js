import '../css/app.scss'
import {jsonFetch} from '../js/ajaxify'


const form = document.querySelector('.ajaxify')

if (form) {

    form.addEventListener('submit', e => {
        e.preventDefault()
        const data = new FormData(form)

        jsonFetch(form.action, CSRF, {
            body: data
        }).then(() => {
          console.log('Request has been made - ok.')
        })
    })

}
