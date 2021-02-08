import prefresh from '@prefresh/vite'
import cors from '@koa/cors'
import path from 'path'

const root = './assets'


/**
 * @type { import('vite').UserConfig }
 */
const config = {
  plugins: [prefresh()],
  root,
  configureServer: function ({ root, app, watcher }) {
    watcher.add(path.resolve(root, '../templates/**/*.html'))
    watcher.on('change', function (path) {
      if (path.endsWith('.html')) {
        watcher.send({
          type: 'full-reload',
          path
        })
      }
    })
  
    app.use(cors({origin: '*'}))
  
  }
}

export default config
