#!/usr/bin/env node

'use strict';

// Test the actual maintenance middleware logic
console.log('=== Testing Updated Maintenance Middleware ===');

// Mock dependencies
const mockMeta = {
    config: {
        maintenanceMode: true,
        maintenanceModeStatus: 503,
        maintenanceModeMessage: 'Site is under maintenance',
        groupsExemptFromMaintenanceMode: ['moderators', 'trusted-users'],
        title: 'Test NodeBB'
    }
};

const mockUser = {
    isAdministrator: async function(uid) {
        return uid === 1; // uid 1 is admin
    }
};

const mockGroups = {
    isMemberOfAny: async function(uid, groups) {
        // uid 2 is member of 'trusted-users'
        if (uid === 2 && groups.includes('trusted-users')) {
            return true;
        }
        // uid 4 is member of 'moderators'
        if (uid === 4 && groups.includes('moderators')) {
            return true;
        }
        return false;
    }
};

const mockNconf = {
    get: function(key) {
        if (key === 'relative_path') return '';
        return null;
    }
};

// Mock the helpers.try function
const mockHelpers = {
    try: function(asyncFn) {
        return asyncFn;
    }
};

// Simulate the updated middleware
function createMaintenanceMiddleware() {
    return mockHelpers.try(async (req, res, next) => {
        if (!mockMeta.config.maintenanceMode) {
            return next();
        }

        const url = req.url.replace(mockNconf.get('relative_path'), '');
        if (url.startsWith('/login') || url.startsWith('/api/login')) {
            return next();
        }

        const isAdmin = await mockUser.isAdministrator(req.uid);
        if (isAdmin) {
            return next();
        }

        // Check if user is member of any exempt groups
        const exemptGroups = mockMeta.config.groupsExemptFromMaintenanceMode || [];
        if (exemptGroups.length > 0) {
            const isMemberOfExemptGroup = await mockGroups.isMemberOfAny(req.uid, exemptGroups);
            if (isMemberOfExemptGroup) {
                return next();
            }
        }

        res.status(mockMeta.config.maintenanceModeStatus);

        const data = {
            site_title: mockMeta.config.title || 'NodeBB',
            message: mockMeta.config.maintenanceModeMessage,
        };

        if (res.locals.isAPI) {
            return res.json(data);
        }
        
        // Simulate rendering the maintenance page
        res.render('503', data);
    });
}

// Create mock middleware
const maintenanceMiddleware = createMaintenanceMiddleware();

// Test helper function
async function testMiddleware(uid, url, isAPI = false) {
    console.log(`\n--- Testing UID ${uid} accessing ${url} ${isAPI ? '(API)' : '(Web)'} ---`);
    
    let nextCalled = false;
    let statusCode = null;
    let responseData = null;
    let renderTemplate = null;
    let renderData = null;
    
    const req = { 
        uid: uid, 
        url: url 
    };
    
    const res = {
        locals: { isAPI: isAPI },
        status: function(code) {
            statusCode = code;
            return this;
        },
        json: function(data) {
            responseData = data;
            return this;
        },
        render: function(template, data) {
            renderTemplate = template;
            renderData = data;
            return this;
        }
    };
    
    const next = function() {
        nextCalled = true;
    };
    
    try {
        await maintenanceMiddleware(req, res, next);
        
        if (nextCalled) {
            console.log('✅ Access allowed - next() called');
        } else if (statusCode) {
            console.log(`❌ Access blocked - Status: ${statusCode}`);
            if (isAPI && responseData) {
                console.log(`   API Response: ${JSON.stringify(responseData)}`);
            } else if (renderTemplate) {
                console.log(`   Rendered template: ${renderTemplate}`);
                console.log(`   Template data: ${JSON.stringify(renderData)}`);
            }
        }
    } catch (error) {
        console.log(`❌ Error: ${error.message}`);
    }
}

// Run comprehensive tests
async function runTests() {
    console.log('Configuration:');
    console.log('- Maintenance Mode:', mockMeta.config.maintenanceMode);
    console.log('- Status Code:', mockMeta.config.maintenanceModeStatus);
    console.log('- Exempt Groups:', mockMeta.config.groupsExemptFromMaintenanceMode);
    
    // Test admin user (uid 1) - should have access
    await testMiddleware(1, '/');
    await testMiddleware(1, '/api/topics');
    
    // Test trusted user (uid 2) - should have access due to group exemption
    await testMiddleware(2, '/');
    await testMiddleware(2, '/api/topics', true);
    
    // Test regular user (uid 3) - should be blocked
    await testMiddleware(3, '/');
    await testMiddleware(3, '/api/topics', true);
    
    // Test moderator user (uid 4) - should have access due to group exemption
    await testMiddleware(4, '/categories');
    
    // Test login page access - should always work
    await testMiddleware(3, '/login');
    await testMiddleware(3, '/api/login');
    
    console.log('\n=== Test completed ===');
}

runTests().catch(console.error);