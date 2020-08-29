function readTheFile(file) {
  const reader = new FileReader()

  return new Promise((resolve) => {
    reader.onload = (event) => {
      resolve(event.target.result)
    }
  
    reader.readAsDataURL(file)
  })
}

function drawImage(canvas, image, resizeCanvas) {
  const img = new Image()
  img.src = image

  img.onload = function () {
    const context = canvas.getContext('2d')
    resizeCanvas(img.width, img.height)
    context.clearRect(0, 0, img.width, img.height)
    context.drawImage(img, 0, 0)
  }
}

function resizeCanvas(canvas, width, height) {
  for (const c of canvas) {
    c.width = width
    c.height = height
  }
}

function loadAndDrawImage(canvas, resizeCanvas, event) {
  const file = [...event.target.files].pop()

  readTheFile(file)
    .then((image) => drawImage(canvas, image, resizeCanvas))
}

function prepareDOM() {
  const mainCanvas = document.getElementById('imageView')

  if (!mainCanvas) {
    throw new Error('Error: I cannot find the canvas element!')
  }

  // Add the temporary canvas.
  const container = mainCanvas.parentNode
  const tmpCanvas = document.createElement('canvas')

  tmpCanvas.id     = 'imageTemp'
  tmpCanvas.width  = mainCanvas.width
  tmpCanvas.height = mainCanvas.height

  container.appendChild(tmpCanvas)

  return {
    tmpCanvas, mainCanvas
  }
}


class PencilTool {
  constructor() {
    this.started = false
  }

  // This is called when you start holding down the mouse button.
  // This starts the pencil drawing.
  mousedown (e) {
    context.beginPath()
    context.moveTo(e.offsetX, e.offsetY)
    this.started = true
  }

  // This function is called every time you move the mouse. Obviously, it only 
  // draws if the this.started state is set to true (when you are holding down 
  // the mouse button).
  mousemove (e) {
    if (this.started) {
      context.lineTo(e.offsetX, e.offsetY)
      context.stroke()
    }
  }

  // This is called when you release the mouse button.
  mouseup (e) {
    if (this.started) {
      this.mousemove(e)
      this.started = false
      img_update()
    }
  }
}


class RectangleTool {
  constructor(canvas, applyChangesOnMainCanvas) {
    this.canvas = canvas
    this.canvas2DContext = canvas.getContext('2d')
    this.applyChangesOnMainCanvas = applyChangesOnMainCanvas
    this.started = false

    this.shape = {}
  }

  mousedown(e) {
    this.started = true
    this.x0 = e.offsetX
    this.y0 = e.offsetY
  }

  mousemove(e) {
    if (!this.started) {
      return
    }

    const x = Math.min(e.offsetX,  this.x0)
    const y = Math.min(e.offsetY,  this.y0)
    const w = Math.abs(e.offsetX - this.x0)
    const h = Math.abs(e.offsetY - this.y0)

    this.canvas2DContext.clearRect(0, 0, this.canvas.width, this.canvas.height)

    if (!w || !h) {
      return
    }

    this.shape = {x, y, w, h}
    this.canvas2DContext.strokeRect(x, y, w, h)
  }

  mouseup(e) {
    if (this.started) {
      this.mousemove(e)
      this.started = false
      this.applyChangesOnMainCanvas(this.shape)
    }
  }
}

class Drawing {

  constructor() {
    this.shapes = []

    const {mainCanvas, tmpCanvas} = prepareDOM()
    this.mainCanvas = mainCanvas
    this.tmpCanvas = tmpCanvas

    this.mainCanvas2DContext = this.mainCanvas.getContext('2d')
    this.tmpCanvas2DContext = this.tmpCanvas.getContext('2d')

    this.applyChangesOnMainCanvas = this.applyChangesOnMainCanvas.bind(this)

    this.tool = new RectangleTool(this.tmpCanvas, this.applyChangesOnMainCanvas)
    this._imageHandler()

    /**
     * * We are using arrow functions here to keep the "this" variable bounded to the instance.
     * * Otherwise, it's bounded to the event and not the instance, so undefined errors on the run!
     */
    this.tmpCanvas.addEventListener('mousedown', e => this.tool.mousedown(e), false)
    this.tmpCanvas.addEventListener('mousemove', e => this.tool.mousemove(e), false)
    this.tmpCanvas.addEventListener('mouseup',	 e => this.tool.mouseup(e), false)
  }

  _imageHandler() {
    const resizeCanvasBound = resizeCanvas.bind(null, [this.tmpCanvas, this.mainCanvas])

    const load = loadAndDrawImage.bind(null, this.mainCanvas, resizeCanvasBound)

    const loadInput = document.querySelector('#load')
    loadInput.addEventListener('change', (event) => load(event))
  }

  /**
   * This function draws the #imageTemp canvas on top of #imageView, after which
   * #imageTemp is cleared. This function is called each time when the user 
   * completes a drawing operation.
   */
  applyChangesOnMainCanvas(shape) {
    this.shapes.push(shape)
    this.mainCanvas2DContext.drawImage(this.tmpCanvas, 0, 0)
		this.tmpCanvas2DContext.clearRect(0, 0, this.mainCanvas.width, this.mainCanvas.height)
  }

}

window.addEventListener('load', () => {
  new Drawing()
}, false)
