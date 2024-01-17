const chokidar = require('chokidar')
const path = require('path')
const fs = require('fs')

const watchFilePath = path.resolve('../dist', 'index.html')

const destFilePath = path.resolve('../../webapps/graph-editor_graph-explorer/body.html')

const watcher = chokidar.watch(watchFilePath, { ignored: /^\./, persistent: true })

watcher
  .on('add', function (path) {
    console.log('File', path, 'has been added')
    fs.copyFile(watchFilePath, destFilePath, (err) => {
      console.log(err)
    })
  })
  .on('change', function (path) {
    console.log('File', path, 'has been changed')
    fs.copyFile(watchFilePath, destFilePath, (err) => {
      console.log(err)
    })
  })
  .on('error', function (error) {
    console.error('Error happened', error)
  })
