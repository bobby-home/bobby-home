import {RectangleTool} from '../js/draw/rectangle'
import {jsonFetch} from '../js/ajaxify'
import '../css/draw-shape.scss'


function drawImage(canvas, image, resizeCanvas, callback) {
  const img = new Image()
  img.src = image

  img.onload = function () {
    const context = canvas.getContext('2d')

    // we need to resize our canvas before drawing.
    resizeCanvas(img.width, img.height)

    context.clearRect(0, 0, img.width, img.height)
    context.drawImage(img, 0, 0)

    callback(img)
  }
}

class Drawing {

  constructor(initialShapes, image) {
    this.shapes = []
    this.initialShapes = initialShapes
    this.image = image

    for (const init of initialShapes) {
      this.shapes.push(init)
    }

    const {mainCanvas, tmpCanvas} = prepareDOM()

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

  clean() {
    if (this.image_object) {
      this.shapes = []
      this.mainCanvas2DContext.clearRect(0, 0, this.mainCanvas.width, this.mainCanvas.height)
      this.mainCanvas2DContext.drawImage(this.image_object, 0, 0)
    }
  }

  _imageHandler() {
    const resizeCanvasBound = resizeCanvas.bind(null, [this.tmpCanvas, this.mainCanvas])

    const loadedImage = (image) => {
      console.log({image})
      this.image_object = image

      for (const initialShape of this.initialShapes) {
        const {x, y, w, h} = initialShape
        this.mainCanvas2DContext.strokeRect(x, y, w, h)
      }

    }

    drawImage(this.mainCanvas, this.image, resizeCanvasBound, loadedImage)
  }

  /**
   * This function draws the #imageTemp canvas on top of #imageView, after which
   * #imageTemp is cleared. This function is called each time when the user
   * completes a drawing operation.
   */
  applyChangesOnMainCanvas(shape) {
    this.shapes.push(shape)

    console.log({shapes: this.shapes})

    this.mainCanvas2DContext.drawImage(this.tmpCanvas, 0, 0)
    this.tmpCanvas2DContext.clearRect(0, 0, this.mainCanvas.width, this.mainCanvas.height)
  }

}

function resizeCanvas(canvas, width, height) {
  for (const c of canvas) {
    c.width = width
    c.height = height
  }
}


function prepareDOM() {
  const mainCanvas = document.querySelector('#imageView')

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


const form = document.querySelector('.form-ajax')

const predefined_rectangles = window.RECTANGLES || []

const drawing = new Drawing(predefined_rectangles, FILE_URL)

form.addEventListener('submit', e => {
  e.preventDefault()

  const formData = new FormData(form)

  const shapes = drawing.shapes

  let i = 0;
  for (const shape of shapes) {
    formData.set(`form-${i}-x`, shape.x)
    formData.set(`form-${i}-y`, shape.y)
    formData.set(`form-${i}-w`, shape.w)
    formData.set(`form-${i}-h`, shape.h)
    i++
  }

  formData.set('form-TOTAL_FORMS', shapes.length)

  jsonFetch(form.action, CSRF, {
      body: formData
  }).then(() => {
    console.log('Request has been made - ok.')
  })

})

const cleanBtn = document.querySelector("#clean")

cleanBtn.addEventListener('click', e => {
  drawing.clean()
})

