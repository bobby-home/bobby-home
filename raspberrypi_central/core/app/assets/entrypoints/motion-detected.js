function drawImage(canvas, imageUrl) {
    const img = new Image()
    img.src = imageUrl

    return new Promise((resolve, reject) => {
        img.onload = function () {
            const context = canvas.getContext('2d')

            // we need to resize our canvas before drawing.
            canvas.width = img.width
            canvas.height = img.height

            context.clearRect(0, 0, img.width, img.height)
            context.drawImage(img, 0, 0)

            resolve(img)
        }
    })
}


function drawRectangles(canvas, rectangles, color = 'red') {
    const context2d = canvas.getContext('2d')

    for (const {x, y, w, h} of rectangles) {
        context2d.beginPath()
        context2d.strokeStyle = color
        context2d.lineWidth = 2

        context2d.rect(x, y, w, h)

        context2d.closePath()
        context2d.stroke()
    }

}


class MotionPicture extends HTMLElement {
    constructor() {
        super()
    }

    connectedCallback() {
        this.innerHTML = `
        <canvas class="motion-picture"></canvas>
        `

        this.canvas = this.querySelector('.motion-picture')
        this.pictureUrl = this.dataset.picture
        if (!this.pictureUrl) {
            throw Error(`data-picture should be defined as the picture url to render.`)
        }

        try {
            this.boundingBoxes = JSON.parse(this.dataset.boundingBoxes)
            this.cameraBoxes = JSON.parse(this.dataset.cameraBoxes)
        } catch(e) {
            // do nothing, just information won't be displayed.
            // hint: cameraBoxes is often null because it watches the whole camera view.
        }

        drawImage(this.canvas, this.pictureUrl).then(() => {
            drawRectangles(this.canvas, this.boundingBoxes)
            drawRectangles(this.canvas, this.cameraBoxes, 'blue')
        })
    }
}

customElements.define('motion-picture', MotionPicture)
