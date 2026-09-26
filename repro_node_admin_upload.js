#!/usr/bin/env node
'use strict';

const path = require('path');
const fs = require('fs');
const nconf = require('nconf');

// Minimal nconf setup for testing
nconf.use('memory');
nconf.set('base_dir', __dirname);
nconf.set('upload_path', path.join(__dirname, 'public', 'uploads'));
nconf.set('upload_url', '/assets/uploads');

(async () => {
  const folder = process.argv[2] || 'nonexistent-admin-upload-folder';

  // Ensure folder does not exist under upload_path
  const baseUploadPath = nconf.get('upload_path');
  console.log('DEBUG baseUploadPath=', baseUploadPath, 'folder=', folder);
  const destDir = path.join(baseUploadPath || '', folder || '');
  try {
    await fs.promises.rm(destDir, { recursive: true, force: true });
  } catch (e) {}

  const controllers = require('./src/controllers/admin/uploads');
  // Prepare a temp copy of test file so the handler can delete it safely
  const srcPath = path.join(__dirname, 'test', 'files', 'test.png');
  const tmpPath = path.join(require('os').tmpdir(), `tmp-${Date.now()}-test.png`);
  await fs.promises.copyFile(srcPath, tmpPath);
  // Construct fake req/res/next
  const req = {
    uid: 1,
    files: { files: [ { name: 'test.png', path: tmpPath, type: 'image/png', size: 1024 } ] },
    body: { params: JSON.stringify({ folder }) },
  };
  const out = { status: null, err: null };
  const res = { json(body) { out.status = 200; out.body = body; console.log(JSON.stringify({ ok: true, body })); } };
  const next = (err) => { out.status = 500; out.err = err; console.log(JSON.stringify({ ok: false, error: err && err.message })); };

  try {
    await controllers.uploadFile(req, res, next);
  } catch (e) {
    console.log(JSON.stringify({ ok: false, error: e.message }));
  }
})();
