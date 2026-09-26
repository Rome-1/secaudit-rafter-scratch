#!/usr/bin/env node

'use strict';

const request = require('request');
const nconf = require('nconf');
const path = require('path');

// Load NodeBB configuration
nconf.file({
    file: path.join(__dirname, 'config.json')
});

nconf.defaults({
    url: 'http://127.0.0.1:4567'
});

const helpers = require('./test/helpers');

async function testUploadError() {
    try {
        // Start the server
        console.log('Starting NodeBB server...');
        const child = require('child_process').spawn('node', ['loader.js', '--no-silent'], {
            cwd: __dirname,
            stdio: 'inherit'
        });

        // Wait for server to start
        await new Promise(resolve => setTimeout(resolve, 5000));

        // Create admin user
        const adminUid = await new Promise((resolve, reject) => {
            require('./src/user').create({ username: 'admin', password: 'adminpass' }, (err, uid) => {
                if (err) reject(err);
                else resolve(uid);
            });
        });

        // Make user admin
        await new Promise((resolve, reject) => {
            require('./src/groups').join('administrators', adminUid, (err) => {
                if (err) reject(err);
                else resolve();
            });
        });

        // Login as admin
        const { jar, csrf_token } = await helpers.loginUser('admin', 'adminpass');

        console.log('\nTesting upload with invalid file type...');
        
        // Try to upload a text file as favicon (should fail - only .ico allowed)
        const testFile = path.join(__dirname, 'test/files/test.txt');
        
        // Create test file if it doesn't exist
        require('fs').writeFileSync(testFile, 'test content');

        // Attempt upload
        await new Promise((resolve) => {
            const formData = {
                'files[]': require('fs').createReadStream(testFile),
                params: JSON.stringify({})
            };

            request.post({
                url: `${nconf.get('url')}/api/admin/uploadfavicon`,
                formData: formData,
                jar: jar,
                headers: {
                    'x-csrf-token': csrf_token
                },
                json: true
            }, (err, res, body) => {
                console.log('\nResponse Status Code:', res.statusCode);
                console.log('Response Body:', JSON.stringify(body, null, 2));
                
                if (res.statusCode === 200) {
                    console.log('\n❌ ERROR: Server returned 200 OK for invalid upload!');
                    console.log('Expected: 4xx or 5xx error status code');
                } else {
                    console.log('\n✓ Correct: Server returned error status code');
                }
                
                resolve();
            });
        });

        // Kill the server
        child.kill();
        process.exit(0);
    } catch (err) {
        console.error('Test failed:', err);
        process.exit(1);
    }
}

// Run the test
testUploadError();