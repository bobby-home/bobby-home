import resolve from '@rollup/plugin-node-resolve' // be able to resolve dependencies from "node_modules" folder.
import postcss from 'rollup-plugin-postcss'
import rootImport from 'rollup-plugin-root-import'
import babel from '@rollup/plugin-babel'
import commonjs from '@rollup/plugin-commonjs'

const sources = ['app']

export default sources.map(source => ({
  input: `assets/entrypoints/${source}.js`,
  output: {
    dir: 'public/assets',
    format: 'es'
  },
  preserveEntrySignatures: false,
  plugins: [
    rootImport({
      root: `assets`
    }),
    resolve(),
    commonjs(),
    postcss({
      extract: true
    }),
    babel({
      babelHelpers: 'bundled',
      exclude: [
        'node_modules/**'
      ]
    })
  ]
}))
