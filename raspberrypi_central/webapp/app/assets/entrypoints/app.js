import '../css/app.scss'
import {jsonFetch} from "../js/ajaxify"
console.log('hello world')


const form = document.querySelector('.ajaxify')

if (form) {

    form.addEventListener('submit', e => {
        e.preventDefault()
        const data = new FormData(form)

        // const running = data.set('running', 1)
        // console.log({running})

        jsonFetch(form.action, CSRF, {
            body: data
        })
    })

}
