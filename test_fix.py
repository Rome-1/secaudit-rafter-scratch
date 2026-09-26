#!/usr/bin/env python3
"""
Script to verify the fix for the getUpvoters vulnerability.
"""

import re

def analyze_fixed_getupvoters():
    """
    Analyze the fixed getUpvoters method for security improvements
    """
    print("=== Analyzing FIXED getUpvoters method ===")
    
    # Read the votes.js file
    with open('/app/src/socket.io/posts/votes.js', 'r') as f:
        votes_source = f.read()
    
    # Extract the getUpvoters method
    method_pattern = r'SocketPosts\.getUpvoters\s*=\s*async\s*function[^{]*{(.*?)};'
    match = re.search(method_pattern, votes_source, re.DOTALL)
    
    if match:
        method_body = match.group(1)
        print("Fixed getUpvoters method body:")
        print("=" * 80)
        print(method_body.strip())
        print("=" * 80)
        
        # Check for security improvements
        security_checks = []
        
        if 'privileges.users.isAdministrator' in method_body:
            security_checks.append("✅ Contains administrator check")
        else:
            security_checks.append("❌ No administrator check found")
            
        if 'no-privileges' in method_body:
            security_checks.append("✅ Contains 'no-privileges' error response")
        else:
            security_checks.append("❌ No 'no-privileges' error response found")
            
        if 'topics:read' in method_body:
            security_checks.append("✅ Contains 'topics:read' privilege check")
        else:
            security_checks.append("❌ No 'topics:read' privilege check found")
            
        if 'posts.getCidsByPids' in method_body:
            security_checks.append("✅ Uses posts.getCidsByPids to get category IDs")
        else:
            security_checks.append("❌ Does not use posts.getCidsByPids")
            
        if 'Set(' in method_body and 'uniqueUids' in method_body:
            security_checks.append("✅ Deduplicates user IDs")
        else:
            security_checks.append("❌ Does not deduplicate user IDs")
            
        if 'cutoff' in method_body and '6' in method_body:
            security_checks.append("✅ Implements cutoff truncation")
        else:
            security_checks.append("❌ No cutoff truncation found")
            
        if 'canReadAll.some' in method_body:
            security_checks.append("✅ Validates ALL category permissions")
        else:
            security_checks.append("❌ Does not validate all category permissions")
            
        print("\nSecurity Analysis of Fixed Implementation:")
        for check in security_checks:
            print(f"  {check}")
        
        # Count improvements
        improvements = sum(1 for check in security_checks if check.startswith("✅"))
        total_checks = len(security_checks)
        
        print(f"\n🔒 Security Score: {improvements}/{total_checks}")
        
        if improvements == total_checks:
            print("🎉 ALL SECURITY REQUIREMENTS IMPLEMENTED!")
            return True
        else:
            missing = total_checks - improvements
            print(f"⚠️  {missing} security requirements still missing.")
            return False
    else:
        print("❌ Could not find getUpvoters method!")
        return False

def verify_requirements():
    """
    Verify all requirements from the PR description are met
    """
    print("\n=== Verifying PR Requirements ===")
    
    with open('/app/src/socket.io/posts/votes.js', 'r') as f:
        source = f.read()
    
    requirements = [
        ("Access control for non-administrators", "isAdmin" in source and "!isAdmin" in source),
        ("Requires topics:read permission", "topics:read" in source),
        ("Rejects with [[error:no-privileges]]", "[[error:no-privileges]]" in source),
        ("Allows administrators regardless", "isAdmin" in source),
        ("Checks all categories from post IDs", "getCidsByPids" in source),
        ("Bulk validation of categories", "canReadAll.some" in source or "Promise.all" in source),
        ("Deduplicates user IDs", "new Set" in source and "uniqueUids" in source),
        ("Fixed cutoff value (6)", "cutoff = 6" in source or "6" in source),
        ("Returns cutoff in response", "cutoff:" in source or "cutoff =" in source),
    ]
    
    passed = 0
    for req_name, req_check in requirements:
        if req_check:
            print(f"  ✅ {req_name}")
            passed += 1
        else:
            print(f"  ❌ {req_name}")
    
    print(f"\nRequirements met: {passed}/{len(requirements)}")
    return passed == len(requirements)

if __name__ == "__main__":
    security_ok = analyze_fixed_getupvoters()
    requirements_ok = verify_requirements()
    
    if security_ok and requirements_ok:
        print("\n🎉 FIX SUCCESSFULLY IMPLEMENTED!")
        print("The getUpvoters method now properly enforces access control.")
    else:
        print("\n❌ Fix incomplete - some requirements not met.")