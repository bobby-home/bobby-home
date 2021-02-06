class PencilTool {
    constructor() {
        this.started = false
    }

    // This is called when you start holding down the mouse button.
    // This starts the pencil drawing.
    mousedown(e) {
        context.beginPath()
        context.moveTo(e.offsetX, e.offsetY)
        this.started = true
    }

    // This function is called every time you move the mouse. Obviously, it only
    // draws if the this.started state is set to true (when you are holding down
    // the mouse button).
    mousemove(e) {
        if (this.started) {
            context.lineTo(e.offsetX, e.offsetY)
            context.stroke()
        }
    }

    // This is called when you release the mouse button.
    mouseup(e) {
        if (this.started) {
            console.log(`end draw (${e.offsetX}, ${e.offsetY})`)
            this.mousemove(e)
            this.started = false
            img_update()
        }
    }
}
