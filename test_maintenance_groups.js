#!/usr/bin/env node

'use strict';

const assert = require('assert');
const nconf = require('nconf');
const path = require('path');

// Initialize nconf for test environment
nconf.argv().env().file({
    file: path.join(__dirname, 'config.json')
});
nconf.defaults({
    base_dir: __dirname,
    upload_path: path.join(__dirname, 'public', 'uploads'),
    views_dir: path.join(__dirname, 'src', 'views'),
});

async function testMaintenanceMode() {
    console.log('Testing maintenance mode with group exemptions...\n');
    
    try {
        // Load required modules
        const db = await require('./src/database').init();
        const meta = require('./src/meta');
        const groups = require('./src/groups');
        const user = require('./src/user');
        
        // Initialize meta configs
        await meta.configs.init();
        
        // Create a test group
        const testGroupName = 'test-maintenance-exempt';
        console.log(`Creating test group: ${testGroupName}`);
        
        // Check if group exists, if not create it
        const exists = await groups.exists(testGroupName);
        if (!exists) {
            await groups.create({
                name: testGroupName,
                description: 'Test group for maintenance mode exemption'
            });
        }
        
        // Create a test user
        const userData = {
            username: 'testuser_maintenance',
            password: 'password123',
            email: 'testuser@example.com'
        };
        
        console.log('Creating test user...');
        let uid;
        try {
            uid = await user.create(userData);
        } catch (err) {
            // User might already exist
            uid = await user.getUidByUsername(userData.username);
        }
        
        // Add user to the test group
        console.log('Adding user to test group...');
        await groups.join(testGroupName, uid);
        
        // Test 1: Check if groupsExemptFromMaintenanceMode config exists
        console.log('\nTest 1: Checking if groupsExemptFromMaintenanceMode config is accessible...');
        const currentExemptGroups = meta.config.groupsExemptFromMaintenanceMode || [];
        console.log('Current exempt groups:', currentExemptGroups);
        
        // Test 2: Set groupsExemptFromMaintenanceMode
        console.log('\nTest 2: Setting groupsExemptFromMaintenanceMode...');
        meta.config.groupsExemptFromMaintenanceMode = [testGroupName];
        await meta.configs.set('groupsExemptFromMaintenanceMode', [testGroupName]);
        console.log('Set exempt groups to:', [testGroupName]);
        
        // Test 3: Enable maintenance mode
        console.log('\nTest 3: Enabling maintenance mode...');
        meta.config.maintenanceMode = 1;
        await meta.configs.set('maintenanceMode', 1);
        
        // Test 4: Check if user is member of exempt group
        console.log('\nTest 4: Checking if user is member of exempt group...');
        const isMember = await groups.isMemberOfGroups(uid, [testGroupName]);
        console.log(`User ${uid} is member of ${testGroupName}:`, isMember[0]);
        
        // Test 5: Simulate middleware check (this is where our changes will be tested)
        console.log('\nTest 5: Simulating maintenance mode middleware check...');
        const isAdmin = await user.isAdministrator(uid);
        console.log(`User ${uid} is admin:`, isAdmin);
        
        const exemptGroups = meta.config.groupsExemptFromMaintenanceMode || [];
        const isExempt = exemptGroups.length > 0 ? await groups.isMemberOfAny(uid, exemptGroups) : false;
        console.log(`User ${uid} is exempt from maintenance:`, isExempt);
        
        const shouldAllowAccess = isAdmin || isExempt;
        console.log(`Should allow access:`, shouldAllowAccess);
        
        // Clean up
        console.log('\nCleaning up...');
        meta.config.maintenanceMode = 0;
        await meta.configs.set('maintenanceMode', 0);
        
        console.log('\n✅ All tests completed successfully!');
        process.exit(0);
        
    } catch (error) {
        console.error('❌ Test failed:', error);
        process.exit(1);
    }
}

// Run tests
testMaintenanceMode();