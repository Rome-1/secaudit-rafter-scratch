#!/usr/bin/env node

'use strict';

/**
 * Script to reproduce the email confirmation issue
 * when requireEmailAddress is enabled
 */

const nconf = require('nconf');
const path = require('path');
const express = require('express');
const session = require('express-session');

// Setup nconf configuration (minimal mock)
nconf.set('relative_path', '');
nconf.set('url', 'http://localhost:4567');

// Mock meta config
const meta = {
    config: {
        requireEmailAddress: 1,  // Enable requireEmailAddress
        sessionDuration: 3600000 // 1 hour
    }
};

// Mock user functions
const user = {
    getUserField: async (uid, field) => {
        if (field === 'email:confirmed') return 0; // Simulate unconfirmed email
        if (field === 'userslug') return `user${uid}`;
        return null;
    },
    isAdministrator: async (uid) => false // Simulate non-admin user
};

// Mock plugins
const plugins = {
    hooks: {
        fire: async (hook, data) => {
            if (hook === 'filter:middleware.registrationComplete') {
                return { allowed: data.allowed || ['/register/complete'] };
            }
            return data;
        }
    }
};

// Mock helpers
const helpers = {
    redirect: (res, location) => {
        console.log(`REDIRECT: ${location}`);
        res.redirect(location);
    }
};

// Create the middleware function (copy from actual code)
const registrationComplete = async function (req, res, next) {
    const path = req.path.startsWith('/api/') ? req.path.replace('/api', '') : req.path;
    
    if (!req.session.hasOwnProperty('registration')) {
        if (req.uid && !path.endsWith('/edit/email')) {
            const [confirmed, isAdmin] = await Promise.all([
                user.getUserField(req.uid, 'email:confirmed'),
                user.isAdministrator(req.uid),
            ]);
            if (meta.config.requireEmailAddress && !confirmed && !isAdmin) {
                helpers.redirect(res, '/me/edit/email');
                return;
            }
        }
        
        return setImmediate(next);
    }
    
    const { allowed } = await plugins.hooks.fire('filter:middleware.registrationComplete', {
        allowed: ['/register/complete'],
    });
    if (!allowed.includes(path)) {
        // Append user data if present
        req.session.registration.uid = req.session.registration.uid || req.uid;
        
        helpers.redirect(res, '/register/complete');
    } else {
        setImmediate(next);
    }
};

// Test the middleware behavior
async function testEmailConfirmationRoutes() {
    console.log('=== Testing Email Confirmation Routes Issue ===\n');
    
    // Create mock request/response objects
    const createMockReq = (path, uid = 1, session = {}) => ({
        path: path,
        uid: uid,
        session: session
    });
    
    const createMockRes = () => ({
        redirect: (url) => {
            console.log(`Response: REDIRECT to ${url}`);
        }
    });
    
    const createMockNext = () => () => {
        console.log('Response: CONTINUE (next() called)');
    };
    
    // Test cases
    const testCases = [
        {
            name: 'User accessing /confirm/abc123 with unconfirmed email',
            req: createMockReq('/confirm/abc123', 1),
            expectedBehavior: 'Should allow access to confirm email, but currently redirects'
        },
        {
            name: 'User accessing /register/complete',
            req: createMockReq('/register/complete', 1),
            expectedBehavior: 'Should allow access (currently working)'
        },
        {
            name: 'User accessing /me/edit/email',
            req: createMockReq('/me/edit/email', 1),
            expectedBehavior: 'Should allow access (currently working)'
        },
        {
            name: 'User accessing regular page with unconfirmed email',
            req: createMockReq('/some-page', 1),
            expectedBehavior: 'Should redirect to /me/edit/email (currently working)'
        }
    ];
    
    for (const testCase of testCases) {
        console.log(`\n--- ${testCase.name} ---`);
        console.log(`Expected: ${testCase.expectedBehavior}`);
        console.log('Actual: ', { noNewLine: true });
        
        try {
            const res = createMockRes();
            const next = createMockNext();
            
            await registrationComplete(testCase.req, res, next);
        } catch (error) {
            console.log(`ERROR: ${error.message}`);
        }
    }
    
    console.log('\n=== Issue Analysis ===');
    console.log('PROBLEM: The registrationComplete middleware redirects users away from');
    console.log('         /confirm/* routes when requireEmailAddress is enabled, preventing');
    console.log('         email confirmation and creating a broken user experience.');
    console.log('\nSOLUTION NEEDED:');
    console.log('1. Allow access to /confirm/* routes in registrationComplete middleware');
    console.log('2. Handle updateEmail flag properly after successful confirmation');
    console.log('3. Set registration session with updateEmail for unconfirmed users');
}

// Run the test
testEmailConfirmationRoutes().catch(console.error);