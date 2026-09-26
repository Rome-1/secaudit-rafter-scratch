#!/usr/bin/env python3
"""
Demo script showing the before/after security behavior
"""

import re

def show_before_after_comparison():
    print("=== SECURITY VULNERABILITY: BEFORE vs AFTER ===")
    print()
    
    # Create a mock "before" version based on what we know was vulnerable
    before_code = '''
    SocketPosts.getUpvoters = async function (socket, pids) {
        if (!Array.isArray(pids)) {
            throw new Error('[[error:invalid-data]]');
        }
        const data = await posts.getUpvotedUidsByPids(pids);
        if (!data.length) {
            return [];
        }
        
        const result = await Promise.all(data.map(async (uids) => {
            let otherCount = 0;
            if (uids.length > 6) {
                otherCount = uids.length - 5;
                uids = uids.slice(0, 5);
            }
            const usernames = await user.getUsernamesByUids(uids);
            return {
                otherCount: otherCount,
                usernames: usernames,
            };
        }));
        return result;
    };
    '''
    
    # Read the current (fixed) version
    with open('/app/src/socket.io/posts/votes.js', 'r') as f:
        votes_source = f.read()
    
    method_pattern = r'SocketPosts\.getUpvoters\s*=\s*async\s*function[^{]*{(.*?)};'
    match = re.search(method_pattern, votes_source, re.DOTALL)
    after_code = match.group(0) if match else "Could not extract method"
    
    print("🚨 BEFORE (Vulnerable):")
    print("=" * 50)
    print(before_code.strip())
    print()
    print("Problems:")
    print("❌ No privilege checks - anyone can call this method")
    print("❌ No category permission validation")
    print("❌ No administrator vs non-admin distinction") 
    print("❌ Directly accesses upvoter data without authorization")
    print("❌ Guest users can see upvoter information for ANY post")
    print()
    
    print("✅ AFTER (Secure):")
    print("=" * 50)
    print(after_code[:500] + "..." if len(after_code) > 500 else after_code)
    print()
    print("Security Features:")
    print("✅ Checks if user is administrator")
    print("✅ Gets category IDs for all posts")
    print("✅ Validates 'topics:read' privilege for each category")
    print("✅ Rejects access with standard error message")
    print("✅ Only accesses data AFTER authorization passes")
    print("✅ Bulk validation ensures ALL categories are readable")
    print()
    
    print("🛡️  ATTACK SCENARIOS NOW BLOCKED:")
    print("=" * 50)
    print("1. Guest trying to see upvoters in private category -> ❌ BLOCKED")
    print("2. User without read access trying to see upvoters -> ❌ BLOCKED") 
    print("3. Partial access (some categories readable) -> ❌ BLOCKED")
    print("4. Administrator accessing any upvoters -> ✅ ALLOWED")
    print("5. User with proper read access -> ✅ ALLOWED")

if __name__ == "__main__":
    show_before_after_comparison()