export class Copyable extends HTMLElement {
    connectedCallback() {
        const value = this.getAttribute("value")

        this.innerHTML = `
            <div class="copyable flex items-center">
                <span>${value}</span>
                <svg class="icon l-ml1">
                    <use xlink:href="${window.SPRITE}#clipboard-copy"></use>
                </svg>
            </div>
        `
        const copyable = this.querySelector('.copyable')
        const self = this

        copyable.addEventListener('click', function() {
            const range = document.createRange()
            range.selectNode(this)
            window.getSelection().addRange(range)

            try {
                // Now that we've selected the anchor text, execute the copy command
                const successful = document.execCommand('copy')
                if (successful) {
                    self.successCb()
                } else {
                    self.errorCb()
                }
            } catch(err) {
                self.errorCb()
            }

            // Remove the selections - NOTE: Should use
            // removeRange(range) when it is supported
            window.getSelection().removeAllRanges()
        })
    }

    successCb() {
        window.sendAlert({
            type: 'success',
            message: 'Copied to clipboard'
        })
    }

    errorCb() {
        window.sendAlert({
            type: 'error',
            message: 'Cannot copy to clipboard.'
        })
    }
}
