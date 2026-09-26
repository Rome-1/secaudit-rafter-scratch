#!/usr/bin/env node

'use strict';

const path = require('path');

// Mock request and response objects
const mockReq = {
    files: {
        files: [{
            name: 'test.txt',
            type: 'text/plain',
            path: '/tmp/test.txt'
        }]
    },
    body: {
        params: '{}'
    }
};

const mockRes = {
    statusCode: 200,
    json: function(data) {
        console.log('Response JSON:', data);
        console.log('Status Code:', this.statusCode);
        if (data.error && this.statusCode === 200) {
            console.log('\n❌ ERROR: Server returned 200 OK with error message!');
            console.log('Expected: Appropriate HTTP error status code');
        }
    },
    status: function(code) {
        this.statusCode = code;
        return this;
    }
};

const mockNext = function(err) {
    if (err) {
        console.log('Error passed to next():', err.message);
    }
};

// Load the admin uploads controller
const uploadsController = require('./src/controllers/admin/uploads');

// Mock file.delete
require('./src/file').delete = function(path) {
    console.log('File deleted:', path);
};

console.log('Testing uploadFavicon with invalid file type (text/plain instead of image/x-icon)...\n');

// Call the uploadFavicon function
uploadsController.uploadFavicon(mockReq, mockRes, mockNext);