// 'use strict'
const path = require('path')
const glob = require('glob')

const ASSETS = './assets'

const entrypoints = glob.sync(path.resolve(ASSETS, 'entrypoints/*.js'))

const entrypointsForWebpack = entrypoints.reduce((acc, entrypoint) => {
    const entryName = path.basename(entrypoint, path.extname(entrypoint))
    acc[entryName] = entrypoint
    return acc
}, {})


const config = {
    entry: entrypointsForWebpack
}

module.exports = {
    ...config
}

// const config = require('./config/config')
// const alias = require('./config/alias')
// const StyleLintPlugin = require('stylelint-webpack-plugin')
// const plugins = require('./config/webpack.plugins.base')
// const { extractCss, extractSass } = require('./config/extract')

// const autoprefixer = require('autoprefixer')({browsers: config.browser})

// const webpackBase = {
//   entry: config.entry,
//   output: {
//     path: config.assets_path,
//     filename: '[name].js',
//     publicPath: config.assets_url
//   },
//   resolve: {
//     extensions: ['.js', '.vue', '.css', '.json'],
//     alias
//   },
//   module: {
//     rules: [
//       // {
//       //   test: /\.(js|vue)$/,
//       //   loader: 'eslint-loader',
//       //   exclude: [/node_modules/, /libs/, /build/],
//       //   enforce: 'pre',
//       //   options: {
//       //     formatter: require('eslint-friendly-formatter')
//       //   }
//       // },
//       {
//         test: /\.js$/,
//         exclude: [/node_modules/, /libs/],
//         loader: 'babel-loader'
//       },
//       {
//         test: /\.vue$/,
//         exclude: [/node_modules/],
//         loader: 'vue-loader',
//         options: {
//           // https://vue-loader.vuejs.org/en/configurations/pre-processors.html
//           loaders: {
//             // Contrary to what its name indicates, sass-loader parses SCSS syntax by default.
//             scss: 'vue-style-loader!css-loader!sass-loader', // <style lang="scss">
//             sass: 'vue-style-loader!css-loader!sass-loader?indentedSyntax', // <style lang="sass">
//             // scss: 'vue-style-loader!css-loader!sass-loader',
//             // https://github.com/vuejs/vue-loader/issues/363
//             // scss: extractSass.extract({
//             //   fallback: 'style-loader',
//             //   use: [{
//             //     loader: 'css-loader',
//             //     options: {
//             //       sourceMap: true
//             //     }
//             //   }, {
//             //     loader: 'sass-loader',
//             //     options: {
//             //       sourceMap: true
//             //     }
//             //   }]
//             // }),

//             js: 'babel-loader'
//             // sass: 'vue-style-loader!css-loader!sass-loader?indentedSyntax' // <style lang="sass">
//           }
//         }
//       },

//       /**
//        * Use the css-loader or the raw-loader to turn it into a JS module and the ExtractTextPlugin to extract it into a separate file.
//        */
//       {
//         test: /\.scss$/,
//         use: extractSass.extract({
//           use: [
//             {
//               // translates CSS into CommonJS
//               loader: 'css-loader',
//               options: {
//                 sourceMap: true
//               }
//             }, {
//               loader: 'postcss-loader',
//               options: {
//                 ident: 'postcss',
//                 sourceMap: true,
//                 plugins: () => [
//                   autoprefixer,
//                   require('css-mqpacker'),
//                   require('postcss-merge-rules'),
//                   require('csswring')
//                 ]
//               }
//             },
//             {
//               loader: 'sass-loader', // compiles Sass to CSS
//               options: { // You can also pass options directly to node-sass
//                 includePaths: [ path.join(__dirname, '../sass/') ],
//                 outputStyle: 'compressed',
//                 sourceMap: true
//               }
//             }
//           ],
//           // use style-loader in development
//           fallback: 'style-loader' // creates style nodes from JS strings
//         })
//       },

//       {
//         test: /\.css$/,
//         // loader: ['css-loader', 'postcss-loader']
//         use: extractCss.extract({
//           use: ['css-loader', 'sass-loader'],
//           fallback: 'style-loader'
//         })
//       }, {
//         test: /\.(png|jpe?g|gif|svg|woff2?|eot|ttf|otf|wav)(\?.*)?$/,
//         use: [{
//           loader: 'url-loader',
//           query: {
//             limit: 10,
//             name: '[name].[ext]'
//           }
//         }]
//         // use: [
//         //   'file-loader',
//         //   {
//         //     loader: 'image-webpack-loader',
//         //     query: {
//         //       limit: 10,
//         //       name: '[name].[ext]'
//         //     }
//         //   }
//         // ]
//       }
//     ]
//   },
//   plugins
// }

// if (config.stylelint) {
//   webpackBase.plugins.push(
//     new StyleLintPlugin({
//       files: config.stylelint
//     })
//   )
// }

// module.exports = { webpackBase }
