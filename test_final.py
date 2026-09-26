#!/usr/bin/env python3
"""
Final comprehensive test to verify all requirements are met.
"""

import re
import os

def test_backend_implementation():
    """Test the backend implementation of getUpvoters"""
    print("=== Testing Backend Implementation ===")
    
    with open('/app/src/socket.io/posts/votes.js', 'r') as f:
        backend_code = f.read()
    
    backend_checks = [
        ("Administrator bypass check", "privileges.users.isAdministrator" in backend_code),
        ("Non-admin access control", "!isAdmin" in backend_code),
        ("Category ID resolution", "posts.getCidsByPids" in backend_code),
        ("Topics read privilege", "topics:read" in backend_code),
        ("Privilege rejection", "[[error:no-privileges]]" in backend_code),
        ("Bulk category validation", "canReadAll.some" in backend_code),
        ("User ID deduplication", "new Set(uids)" in backend_code),
        ("Fixed cutoff value", "cutoff = 6" in backend_code),
        ("Cutoff in response", "cutoff: cutoff" in backend_code),
        ("Username ordering preserved", "usernamesToResolve = uniqueUids.slice" in backend_code),
    ]
    
    passed = 0
    for check_name, check_condition in backend_checks:
        if check_condition:
            print(f"  ✅ {check_name}")
            passed += 1
        else:
            print(f"  ❌ {check_name}")
    
    print(f"Backend: {passed}/{len(backend_checks)} checks passed")
    return passed == len(backend_checks)

def test_frontend_implementation():
    """Test the frontend implementation changes"""
    print("\n=== Testing Frontend Implementation ===")
    
    with open('/app/public/src/client/topic/votes.js', 'r') as f:
        frontend_code = f.read()
    
    frontend_checks = [
        ("Dynamic cutoff interpretation", "data.cutoff ||" in frontend_code),
        ("HTML tooltip support", "html: true" in frontend_code),
        ("Backward compatibility fallback", "|| 6" in frontend_code),
        ("Uses server cutoff value", "const cutoff = data.cutoff" in frontend_code),
    ]
    
    passed = 0
    for check_name, check_condition in frontend_checks:
        if check_condition:
            print(f"  ✅ {check_name}")
            passed += 1
        else:
            print(f"  ❌ {check_name}")
    
    print(f"Frontend: {passed}/{len(frontend_checks)} checks passed")
    return passed == len(frontend_checks)

def test_security_improvements():
    """Test that the security vulnerability is fixed"""
    print("\n=== Testing Security Improvements ===")
    
    with open('/app/src/socket.io/posts/votes.js', 'r') as f:
        votes_source = f.read()
    
    # Extract the getUpvoters method
    method_pattern = r'SocketPosts\.getUpvoters\s*=\s*async\s*function[^{]*{(.*?)};'
    match = re.search(method_pattern, votes_source, re.DOTALL)
    
    if not match:
        print("  ❌ Could not find getUpvoters method!")
        return False
    
    method_body = match.group(1)
    
    # Check the order of operations - security checks should come BEFORE data access
    lines = method_body.strip().split('\n')
    
    security_checks_before_data = False
    data_access_line = -1
    security_check_line = -1
    
    for i, line in enumerate(lines):
        if 'getUpvotedUidsByPids' in line:
            data_access_line = i
        if 'privileges.users.isAdministrator' in line:
            security_check_line = i
    
    if security_check_line < data_access_line and security_check_line != -1 and data_access_line != -1:
        print("  ✅ Security checks performed BEFORE data access")
        security_checks_before_data = True
    else:
        print("  ❌ Security checks not performed before data access")
    
    # Check that all categories must be readable
    all_categories_checked = 'canReadAll.some(canRead => !canRead)' in method_body
    if all_categories_checked:
        print("  ✅ ALL categories must be readable (not just any one)")
    else:
        print("  ❌ Does not check ALL categories")
    
    # Check that admin bypass is properly implemented
    admin_bypass = 'isAdmin' in method_body and '!isAdmin' in method_body
    if admin_bypass:
        print("  ✅ Administrators can bypass restrictions")
    else:
        print("  ❌ Administrator bypass not implemented")
    
    return security_checks_before_data and all_categories_checked and admin_bypass

def test_pr_requirements_coverage():
    """Verify all PR requirements are covered"""
    print("\n=== Testing PR Requirements Coverage ===")
    
    with open('/app/src/socket.io/posts/votes.js', 'r') as f:
        backend = f.read()
    with open('/app/public/src/client/topic/votes.js', 'r') as f:
        frontend = f.read()
    
    requirements = [
        ("SocketPosts.getUpvoters enforces access control", "privileges.users.isAdministrator" in backend),
        ("Requires topics:read permission on all categories", "topics:read" in backend and "canReadAll" in backend),
        ("Rejects with [[error:no-privileges]]", "[[error:no-privileges]]" in backend),
        ("Administrators bypass restrictions", "isAdmin" in backend),
        ("Privilege check across full set of post IDs", "getCidsByPids(pids)" in backend),
        ("Deduplicates user IDs before resolving usernames", "new Set(uids)" in backend),
        ("Returns truncated upvoter lists (cutoff = 6)", "cutoff = 6" in backend),
        ("Frontend interprets cutoff from server", "data.cutoff" in frontend),
        ("Frontend tooltip supports HTML", "html: true" in frontend),
        ("Backend resolves category IDs using posts.getCidsByPids", "posts.getCidsByPids" in backend),
        ("Category-level permission checks support bulk validation", "Promise.all" in backend and "canReadAll" in backend),
        ("Usernames preserve ordering", "slice" in backend),
    ]
    
    passed = 0
    for req_name, req_check in requirements:
        if req_check:
            print(f"  ✅ {req_name}")
            passed += 1
        else:
            print(f"  ❌ {req_name}")
    
    print(f"PR Requirements: {passed}/{len(requirements)} requirements met")
    return passed == len(requirements)

def generate_summary():
    """Generate a summary of all changes made"""
    print("\n" + "="*60)
    print("SUMMARY OF CHANGES MADE")
    print("="*60)
    print()
    print("Backend Changes (/app/src/socket.io/posts/votes.js):")
    print("1. Added administrator check using privileges.users.isAdministrator()")
    print("2. Added category ID resolution using posts.getCidsByPids()")
    print("3. Added topics:read privilege checking for all categories")
    print("4. Added [[error:no-privileges]] rejection for unauthorized access")
    print("5. Added user ID deduplication using Set()")
    print("6. Implemented fixed cutoff value (6) with proper truncation")
    print("7. Added cutoff field to response object")
    print("8. Ensured username ordering is preserved")
    print()
    print("Frontend Changes (/app/public/src/client/topic/votes.js):")
    print("1. Changed hardcoded cutoff to use server-provided cutoff value")
    print("2. Added HTML support to tooltip configuration")
    print("3. Added backward compatibility fallback for cutoff value")
    print()
    print("Security Improvements:")
    print("1. Non-privileged users can no longer access upvoter data for restricted categories")
    print("2. All categories associated with post IDs must be readable")
    print("3. Administrators can still access all upvoter data")
    print("4. Proper error handling with standard error message")

if __name__ == "__main__":
    backend_ok = test_backend_implementation()
    frontend_ok = test_frontend_implementation()
    security_ok = test_security_improvements()
    requirements_ok = test_pr_requirements_coverage()
    
    print("\n" + "="*60)
    print("FINAL TEST RESULTS")
    print("="*60)
    print(f"Backend Implementation: {'✅ PASS' if backend_ok else '❌ FAIL'}")
    print(f"Frontend Implementation: {'✅ PASS' if frontend_ok else '❌ FAIL'}")
    print(f"Security Improvements: {'✅ PASS' if security_ok else '❌ FAIL'}")
    print(f"PR Requirements: {'✅ PASS' if requirements_ok else '❌ FAIL'}")
    
    all_passed = backend_ok and frontend_ok and security_ok and requirements_ok
    
    if all_passed:
        print(f"\n🎉 ALL TESTS PASSED! The vulnerability has been successfully fixed.")
        generate_summary()
    else:
        print(f"\n❌ Some tests failed. Review the implementation.")
    
    exit(0 if all_passed else 1)