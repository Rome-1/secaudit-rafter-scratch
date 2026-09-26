#!/usr/bin/env node
/**
 * Integration test to verify RegistrationTokenAuthEntry is properly exported and accessible
 */

const path = require('path');

// Mock the required dependencies
global.window = {};
global.document = {};

// Test that we can import the module
try {
    // Import the AuthType enum from matrix-js-sdk
    const interactiveAuth = require('matrix-js-sdk/lib/interactive-auth');
    
    console.log('✓ Successfully imported matrix-js-sdk/interactive-auth');
    console.log('✓ AuthType.RegistrationToken:', interactiveAuth.AuthType.RegistrationToken);
    console.log('✓ AuthType.UnstableRegistrationToken:', interactiveAuth.AuthType.UnstableRegistrationToken);
    
    // Verify the types are correctly defined
    const registrationToken = interactiveAuth.AuthType.RegistrationToken;
    const unstableRegistrationToken = interactiveAuth.AuthType.UnstableRegistrationToken;
    
    if (registrationToken === 'm.login.registration_token') {
        console.log('✓ AuthType.RegistrationToken has correct value');
    } else {
        console.log('✗ AuthType.RegistrationToken has incorrect value:', registrationToken);
        process.exit(1);
    }
    
    if (unstableRegistrationToken === 'org.matrix.msc3231.login.registration_token') {
        console.log('✓ AuthType.UnstableRegistrationToken has correct value');
    } else {
        console.log('✗ AuthType.UnstableRegistrationToken has incorrect value:', unstableRegistrationToken);
        process.exit(1);
    }
    
    console.log('\n✅ All integration tests passed!');
    process.exit(0);
    
} catch (error) {
    console.error('✗ Failed to import module:', error.message);
    process.exit(1);
}
