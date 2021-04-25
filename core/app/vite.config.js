import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import * as path from "path";

const root = './assets'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  root,
  build: {
    outDir: '../public/assets',
    assetsDir: '',
    manifest: true,
    rollupOptions: {
      input: {
        'app.js': `./assets/entrypoints/app.js`,
        'motion-detected.js': `./assets/entrypoints/motion-detected.js`,
      }
    }
  }
})
