// DreamPower.
// Copyright (C) DreamNet. All rights reserved.
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License 3.0 as published by
// the Free Software Foundation. See <https://www.gnu.org/licenses/gpl-3.0.html>
//
// Written by Ivan Bravo Bravo <ivan@dreamnet.tech>, 2019.

const Octokit = require('@octokit/rest')
const mime = require('mime-types')
const _ = require('lodash')
const Deferred = require('deferred')
const fs = require('fs')
const path = require('path')
const Seven = require('node-7z')

const GITHUB_ORG = 'dreamnettech'
const GITHUB_REPO = 'dreamtime'

if (!process.env.GITHUB_TOKEN) {
  console.log('API keys not found!')
  process.exit(0)
}

const octokit = new Octokit({
  auth: process.env.GITHUB_TOKEN
})

const isTagRelease = _.startsWith(process.env.GITHUB_REF, 'refs/tags')

const tagName = isTagRelease
  ? process.env.GITHUB_REF.split('/')[2]
  : _.truncate(process.env.GITHUB_SHA, { length: 7, omission: '' })

const version = tagName
const fileName = `DreamPower-${version}-${process.env.BUILD_OS}-${process.env.BUILD_PLATFORM}.7z`

const buildPath = path.resolve(__dirname, '../dist/dreampower')
const filePath = path.resolve(__dirname, '../', fileName)

async function getGithubReleaseUrl() {
  let response

  try {
    response = await octokit.repos.getReleaseByTag({
      owner: GITHUB_ORG,
      repo: GITHUB_REPO,
      tag: tagName,
    })
  } catch (err) {
    if (err.status !== 404) {
      throw err
    }

    console.log(`Creating release for tag: ${tagName}...`)

    try {
      response = await octokit.repos.createRelease({
        owner: GITHUB_ORG,
        repo: GITHUB_REPO,
        tag_name: tagName,
        name: version,
        prerelease: true,
        draft: false,
      })
    } catch (err) {
      console.warn(err)
      console.log('Retrying...')

      // eslint-disable-next-line no-return-await
      return await getGithubReleaseUrl()
    }
  }

  return response.data.upload_url
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

  // TODO: Upload to DreamLink
}

function zip() {
  console.log('Compressing build...')
  process.chdir(buildPath)

  const def = new Deferred()

  const sevenProcess = Seven.add(filePath, '*', {
    recursive: true
  })

  sevenProcess.on('error', (err) => {
    def.reject(err)
  })

  sevenProcess.on('end', (info) => {
    def.resolve()
  })

  return def.promise
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
