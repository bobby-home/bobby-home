export class ReloadBtn extends HTMLElement {
    connectedCallback() {
        this.innerHTML = `
            <button class="btn btn-primary">${this.innerText}</button>
        `

        const btn = this.querySelector('.btn')
        this.clickEvent = btn.addEventListener('click', () => location.reload())
    }

    disconnectedCallback() {
        window.removeEventListener('click', this.clickEvent)
    }
}
