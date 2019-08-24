/*
 * DreamTime | (C) 2019 by Ivan Bravo Bravo <ivan@dreamnet.tech>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License 3.0 as published by
 * the Free Software Foundation.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program. If not, see <https://www.gnu.org/licenses/>.
 */

const Octokit = require('@octokit/rest')
const AWS = require('aws-sdk')
const mime = require('mime-types')
const _ = require('lodash')
const Deferred = require('deferred')
const fs = require('fs')
const path = require('path')
const Seven = require('node-7z')

const octokit = new Octokit({
  auth: process.env.GITHUB_TOKEN
})

const S3Client = new AWS.S3({
  accessKeyId: process.env.S3_ACCESS_KEY_ID,
  secretAccessKey: process.env.S3_SECRET_ACCESS_KEY,
  endpoint: 'https://sfo2.digitaloceanspaces.com'
})

function getOS() {
  if (process.platform === 'win32') {
    return 'windows'
  }

  if (process.platform === 'darwin') {
    return 'macos'
  }

  return 'ubuntu'
}

const isTagRelease = _.startsWith(process.env.GITHUB_REF, 'refs/tags')

const tagName = isTagRelease
  ? process.env.GITHUB_REF.split('/')[2]
  : _.truncate(process.env.GITHUB_SHA, { length: 7, omission: '' })

const version = tagName
const fileName = `DreamPower-${version}-${getOS()}-${
  process.env.BUILD_DEVICE
}.7z`

const buildPath = path.resolve(__dirname, '../dist/dreampower')
const filePath = path.resolve(__dirname, '../', fileName)

/*
console.log({
  tagName,
  fileName,
  buildPath,
  filePath
})
*/

async function getGithubReleaseUrl() {
  let response

  try {
    response = await octokit.repos.getReleaseByTag({
      owner: 'private-dreamnet',
      repo: 'dreampower',
      tag: tagName
    })
  } catch (err) {
    if (err.status !== 404) {
      throw err
    }

    console.log(`Creating release for tag: ${tagName}...`)

    try {
      response = await octokit.repos.createRelease({
        owner: 'private-dreamnet',
        repo: 'dreampower',
        tag_name: tagName,
        name: version,
        prerelease: true,
        draft: false
      })
    } catch (err) {
      console.log(err)
      throw err
    }
  }

  return response.data.upload_url
}

function uploadToS3(filePath, fileName) {
  const deferred = new Deferred()

  S3Client.upload(
    {
      Bucket: 'dreamnet-cdn',
      Key: `releases/dreampower/${tagName}/${fileName}`,
      Body: fs.createReadStream(filePath)
    },
    (err, response) => {
      if (err) {
        deferred.reject(err)
        return
      }

      deferred.resolve(response)
    }
  )

  return deferred.promise
}

async function uploadToGithub(filePath, fileName) {
  const stats = fs.statSync(filePath)
  const url = await getGithubReleaseUrl()

  const response = await octokit.repos.uploadReleaseAsset({
    url,
    headers: {
      'content-length': stats.size,
      'content-type': mime.lookup(filePath)
    },
    name: fileName,
    file: fs.createReadStream(filePath)
  })

  return response
}

async function upload(filePath, fileName) {
  let response

  if (isTagRelease) {
    console.log(`Uploading ${fileName} to Github...`)
    response = await uploadToGithub(filePath, fileName)
    console.log('Github say: ', response)
  }

  console.log(`Uploading ${fileName} to S3...`)
  response = await uploadToS3(filePath, fileName)
  console.log('S3 say:', response)
}

function zip() {
  console.log('Compressing build...')
  process.chdir(buildPath)

  const deferred = new Deferred()

  const sevenProcess = Seven.add(filePath, '*', {
    recursive: true
  })

  sevenProcess.on('error', (err) => {
    deferred.reject(err)
  })

  sevenProcess.on('end', (info) => {
    deferred.resolve()
  })

  return deferred.promise
}

async function main() {
  if (!fs.existsSync(buildPath)) {
    throw Error('No build path!')
  }

  await zip()

  if (fs.existsSync(filePath)) {
    upload(filePath, fileName)
  } else {
    console.log('No release found!')
  }
}

process.on('unhandledRejection', (err) => {
  throw err
})

main()
