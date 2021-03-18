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
        copyable.addEventListener('click', function() {
            const range = document.createRange()
            range.selectNode(this)
            window.getSelection().addRange(range)

            try {
                // Now that we've selected the anchor text, execute the copy command
                const successful = document.execCommand('copy')
                const msg = successful ? 'successful' : 'unsuccessful'
                console.log('Copy command was ' + msg)
            } catch(err) {
                console.log('Oops, unable to copy')
            }

            // Remove the selections - NOTE: Should use
            // removeRange(range) when it is supported
            window.getSelection().removeAllRanges()
        })
    }
}
