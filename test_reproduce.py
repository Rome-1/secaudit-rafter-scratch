#!/usr/bin/env python3
"""
Script to reproduce the issue described in the PR.

The issue is that SocketPosts.getUpvoters method exposes upvoter information
even when the requesting user lacks permission to read the topic/category
containing that post.
"""

import json
import subprocess
import sys

def test_current_behavior():
    """
    Test the current behavior of the getUpvoters method.
    This should demonstrate the security vulnerability.
    """
    print("=== Testing current getUpvoters behavior ===")
    
    # Create a Node.js test script that simulates the issue
    test_js = """
const path = require('path');

// Set the working directory
process.chdir('/app');

// Mock socket object for testing
const mockSocket = {
    uid: 0,  // Guest user (no privileges)
    ip: '127.0.0.1'
};

async function testGetUpvoters() {
    try {
        // Try to load the necessary modules to test the current behavior
        console.log('Testing current getUpvoters implementation...');
        
        // Load database first
        const db = require('./src/database');
        
        // Check if database is connected
        if (!db.client) {
            console.log('⚠️  Database not connected. Checking implementation instead.');
            
            // Load the SocketPosts module directly
            const socketPostsPath = path.join(__dirname, '../src/socket.io/posts.js');
            const SocketPosts = require(socketPostsPath);
            
            console.log('SocketPosts.getUpvoters function exists:', typeof SocketPosts.getUpvoters);
            
            // Read the source to see if there are privilege checks
            const fs = require('fs');
            const votesPath = path.join(__dirname, '../src/socket.io/posts/votes.js');
            const votesSource = fs.readFileSync(votesPath, 'utf8');
            
            if (votesSource.includes('privileges') || votesSource.includes('no-privileges')) {
                console.log('✅ Some privilege checks detected in votes.js');
            } else {
                console.log('❌ VULNERABILITY: No privilege checks detected in getUpvoters!');
            }
            
            return;
        }
        
        // If database is connected, try actual test
        const SocketPosts = require('./src/socket.io/posts');
        const pids = [1, 2, 3];
        
        const result = await SocketPosts.getUpvoters(mockSocket, pids);
        console.log('Result:', JSON.stringify(result, null, 2));
        console.log('❌ VULNERABILITY: Guest user can access upvoter data!');
        
    } catch (error) {
        if (error.message === '[[error:no-privileges]]') {
            console.log('✅ SECURE: Access properly denied');
        } else {
            console.log('❌ Error:', error.message);
        }
    }
}

testGetUpvoters();
"""
    
    with open('/tmp/test_getupvoters.js', 'w') as f:
        f.write(test_js)
    
    try:
        result = subprocess.run(['node', '/tmp/test_getupvoters.js'], 
                              capture_output=True, text=True, timeout=30)
        print("STDOUT:")
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        return result.returncode
    except subprocess.TimeoutExpired:
        print("Test timed out")
        return 1
    except Exception as e:
        print(f"Error running test: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(test_current_behavior())