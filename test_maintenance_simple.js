#!/usr/bin/env node

'use strict';

// Simple test to validate our maintenance mode logic without database
console.log('=== Testing Maintenance Mode Logic ===');

// Mock the required modules
const mockMeta = {
    config: {
        maintenanceMode: true,
        groupsExemptFromMaintenanceMode: ['moderators', 'trusted-users']
    }
};

const mockGroups = {
    isMemberOfAny: async function(uid, groups) {
        // Mock implementation - simulate user 2 being a member of 'trusted-users'
        if (uid === 2 && groups.includes('trusted-users')) {
            return true;
        }
        return false;
    }
};

const mockUser = {
    isAdministrator: async function(uid) {
        // Mock implementation - simulate user 1 being admin
        return uid === 1;
    }
};

// Simulate the maintenance middleware logic
async function testMaintenanceLogic(uid, url = '/') {
    console.log(`\n--- Testing user ${uid} accessing ${url} ---`);
    
    // Skip maintenance check for login urls
    if (url.startsWith('/login') || url.startsWith('/api/login')) {
        console.log('✅ Login URL - access allowed');
        return true;
    }
    
    // Check if user is admin
    const isAdmin = await mockUser.isAdministrator(uid);
    if (isAdmin) {
        console.log('✅ Admin user - access allowed');
        return true;
    }
    
    // Check if user is member of any exempt groups
    const exemptGroups = mockMeta.config.groupsExemptFromMaintenanceMode || [];
    if (exemptGroups.length > 0) {
        const isMemberOfExemptGroup = await mockGroups.isMemberOfAny(uid, exemptGroups);
        if (isMemberOfExemptGroup) {
            console.log('✅ Member of exempt group - access allowed');
            return true;
        }
    }
    
    console.log('❌ Access blocked - maintenance mode');
    return false;
}

// Test different scenarios
async function runTests() {
    console.log('Configuration:');
    console.log('- Maintenance Mode:', mockMeta.config.maintenanceMode);
    console.log('- Exempt Groups:', mockMeta.config.groupsExemptFromMaintenanceMode);
    
    // Test admin user (should have access)
    await testMaintenanceLogic(1, '/');
    
    // Test trusted user (should have access due to group exemption)
    await testMaintenanceLogic(2, '/');
    
    // Test regular user (should be blocked)
    await testMaintenanceLogic(3, '/');
    
    // Test login page (should always have access)
    await testMaintenanceLogic(3, '/login');
    
    console.log('\n=== All tests completed ===');
}

runTests().catch(console.error);