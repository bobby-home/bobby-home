import '../css/draw-shape.scss'


function readTheFile(file) {
  const reader = new FileReader()

  return new Promise((resolve) => {
    reader.onload = (event) => {
      resolve(event.target.result)
    }
  
    reader.readAsDataURL(file)
  })
}

function drawImage(canvas, image, resizeCanvas, callback) {
  const img = new Image()
  img.src = image

  img.onload = function () {
    const context = canvas.getContext('2d')
    resizeCanvas(img.width, img.height)
    context.clearRect(0, 0, img.width, img.height)
    context.drawImage(img, 0, 0)

    callback(img.width, img.height)
  }
}

function resizeCanvas(canvas, width, height) {
  for (const c of canvas) {
    c.width = width
    c.height = height
  }
}

function loadAndDrawImage(canvas, resizeCanvas, callback, event) {
  const file = [...event.target.files].pop()

  readTheFile(file)
    .then((image) => drawImage(canvas, image, resizeCanvas, callback))
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
      console.log(`end draw (${e.offsetX}, ${e.offsetY})`)
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

  // This is called when you release the mouse button.
  mouseup(e) {
    if (this.started) {
      this.mousemove(e)
      this.started = false
      this.applyChangesOnMainCanvas(this.shape)
    }
  }
}

class Drawing {

  constructor(form) {
    console.log('drawing constructor')
    this.shapes = []
    this.form = form

    const {mainCanvas, tmpCanvas} = prepareDOM()
    console.log({mainCanvas, tmpCanvas})

    this.mainCanvas = mainCanvas
    this.tmpCanvas = tmpCanvas

    this.mainCanvas2DContext = this.mainCanvas.getContext('2d')
    this.tmpCanvas2DContext = this.tmpCanvas.getContext('2d')

    this.applyChangesOnMainCanvas = this.applyChangesOnMainCanvas.bind(this)

    this.tool = new RectangleTool(this.tmpCanvas, this.applyChangesOnMainCanvas)
    this._imageHandler()

    /**
     * We are using arrow functions here to keep the "this" variable bounded to the instance.
     * Otherwise, it's bounded to the event and not the instance, so undefined errors on the run!
     */
    this.tmpCanvas.addEventListener('mousedown', e => this.tool.mousedown(e), false)
    this.tmpCanvas.addEventListener('mousemove', e => this.tool.mousemove(e), false)
    this.tmpCanvas.addEventListener('mouseup',	 e => this.tool.mouseup(e), false)
  }

  _imageHandler() {
    const resizeCanvasBound = resizeCanvas.bind(null, [this.tmpCanvas, this.mainCanvas])

    const loadedImage =(width, height) => {
      console.log({width, height})
      this.form.imageWidth.value = width
      this.form.imageHeight.value = height
    }

    const load = loadAndDrawImage.bind(null, this.mainCanvas, resizeCanvasBound, loadedImage)

    const loadInput = document.querySelector('#load')
    loadInput.addEventListener('change', (event) => load(event))
  }

  /**
   * This function draws the #imageTemp canvas on top of #imageView, after which
   * #imageTemp is cleared. This function is called each time when the user 
   * completes a drawing operation.
   */
  applyChangesOnMainCanvas(shape) {
    console.log({shape})
    this.shapes.push(shape)

    const {x, y, w, h} = shape

    this.form.xInput.value = x
    this.form.yInput.value = y
    this.form.wInput.value = w
    this.form.hInput.value = h

    this.mainCanvas2DContext.drawImage(this.tmpCanvas, 0, 0)
		this.tmpCanvas2DContext.clearRect(0, 0, this.mainCanvas.width, this.mainCanvas.height)
  }

}

const xInput = document.querySelector('#id_x')
const yInput = document.querySelector('#id_y')
const wInput = document.querySelector('#id_w')
const hInput = document.querySelector('#id_h')

const imageWidth = document.querySelector('#id_image_width')
const imageHeight = document.querySelector('#id_image_height')


const form = { xInput, yInput, wInput, hInput, imageWidth, imageHeight }
// console.log(form)

window.addEventListener('load', () => {
  new Drawing(form)
}, false)
