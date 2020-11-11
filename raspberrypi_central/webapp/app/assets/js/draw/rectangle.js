export class RectangleTool {
    constructor(canvas, applyChangesOnMainCanvas) {
        this.canvas = canvas
        this.canvas2DContext = canvas.getContext('2d')
        this.applyChangesOnMainCanvas = applyChangesOnMainCanvas
        this.started = false

        this.shape = {}
    }

    // This is called when you start holding down the mouse button.
    // This starts the pencil drawing.
    mousedown(e) {
        console.log('rectangle mousedown')
        this.started = true
        this.x0 = e.offsetX
        this.y0 = e.offsetY
    }

    // This function is called every time you move the mouse. Obviously, it only
    // draws if the this.started state is set to true (when you are holding down
    // the mouse button).
    mousemove(e) {
        if (!this.started) {
            return
        }

        const x = Math.min(e.offsetX, this.x0)
        const y = Math.min(e.offsetY, this.y0)
        const w = Math.abs(e.offsetX - this.x0)
        const h = Math.abs(e.offsetY - this.y0)

        this.canvas2DContext.clearRect(0, 0, this.canvas.width, this.canvas.height)

        if (!w || !h) {
            return
        }

        this.shape = {x, y, w, h}
        this.canvas2DContext.strokeRect(x, y, w, h)
    }

    // This is called when you release the mouse button.
    mouseup(e) {
        if (this.started) {
            this.mousemove(e)
            this.started = false
            this.applyChangesOnMainCanvas(this.shape)
        }
    }
}
