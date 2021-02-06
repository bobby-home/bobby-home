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

const pictureCanvas = document.querySelector('#picture-canvas')

drawImage(pictureCanvas, FILE_URL).then(() => {
  console.log('loaded')
  drawRectangles(pictureCanvas, BOUNDING_BOXES)
  drawRectangles(pictureCanvas, CAMERA_ROI, 'blue')
})
