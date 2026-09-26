#!/usr/bin/env node

'use strict';

// Test script to reproduce current maintenance mode behavior
// and verify our changes work correctly

const path = require('path');

// Set up the environment
process.chdir('/app');
process.env.NODE_ENV = process.env.NODE_ENV || 'development';

// Load nconf first
const nconf = require('nconf');
nconf.file({ file: path.join('/app', 'config.json') });
nconf.defaults({
    base_dir: '/app',
    themes_path: path.join('/app', 'node_modules'),
    views_dir: path.join('/app', 'build/public/templates'),
});

async function testMaintenanceMode() {
    try {
        // Initialize database and meta
        await require('./src/database').init();
        const meta = require('./src/meta');
        const user = require('./src/user');
        const groups = require('./src/groups');
        
        await meta.configs.init();
        
        console.log('=== Current Maintenance Mode Configuration ===');
        console.log('Maintenance Mode Enabled:', meta.config.maintenanceMode);
        console.log('Maintenance Mode Status:', meta.config.maintenanceModeStatus);
        console.log('Maintenance Mode Message:', meta.config.maintenanceModeMessage);
        console.log('Groups Exempt from Post Queue:', meta.config.groupsExemptFromPostQueue);
        console.log('Groups Exempt from Maintenance Mode:', meta.config.groupsExemptFromMaintenanceMode || 'Not configured');
        
        console.log('\n=== Available Non-Privilege Groups ===');
        const allGroups = await groups.getNonPrivilegeGroups('groups:createtime', 0, -1);
        allGroups.forEach(group => {
            if (group) {
                console.log(`- ${group.name} (displayName: ${group.displayName || group.name}, system: ${group.system})`);
            }
        });
        
        console.log('\n=== Testing Admin User ===');
        // Create a test admin user (uid 1 is usually admin)
        const adminUsers = await user.getUidsFromSet('group:administrators:members', 0, 0);
        if (adminUsers.length > 0) {
            const isAdmin = await user.isAdministrator(adminUsers[0]);
            console.log(`User ${adminUsers[0]} is admin:`, isAdmin);
        }
        
        console.log('\n=== Testing Middleware Logic (Current) ===');
        // Simulate current maintenance mode middleware logic
        const testUid = adminUsers.length > 0 ? adminUsers[0] : 1;
        const isCurrentlyAdmin = await user.isAdministrator(testUid);
        const maintenanceMode = meta.config.maintenanceMode;
        
        console.log(`Maintenance mode enabled: ${maintenanceMode}`);
        console.log(`Test user ${testUid} is admin: ${isCurrentlyAdmin}`);
        
        if (maintenanceMode) {
            if (isCurrentlyAdmin) {
                console.log('✅ Current logic: Admin would have access');
            } else {
                console.log('❌ Current logic: Non-admin would be blocked');
            }
        } else {
            console.log('✅ Current logic: Maintenance mode disabled, all users have access');
        }
        
        process.exit(0);
    } catch (error) {
        console.error('Error testing maintenance mode:', error);
        process.exit(1);
    }
}

testMaintenanceMode();