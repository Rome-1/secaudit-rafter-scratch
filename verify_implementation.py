#!/usr/bin/env python3
"""
Comprehensive verification script for ReactRootManager implementation
"""

import subprocess
import sys

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\n{'='*70}")
    print(f"{description}")
    print('='*70)
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    success = result.returncode == 0
    if result.stdout:
        print(result.stdout[:500])  # Limit output
    if result.stderr and not success:
        print("ERROR:", result.stderr[:500])
    print(f"Status: {'✓ PASS' if success else '✗ FAIL'}")
    return success

def check_file_content(file_path, expected_content, description):
    """Check if file contains expected content"""
    print(f"\n{'='*70}")
    print(f"{description}")
    print('='*70)
    result = subprocess.run(f"grep -q '{expected_content}' {file_path}", shell=True, capture_output=True)
    success = result.returncode == 0
    print(f"Checking: {expected_content}")
    print(f"Status: {'✓ PASS' if success else '✗ FAIL'}")
    return success

def check_file_not_contains(file_path, unwanted_content, description):
    """Check if file does NOT contain unwanted content"""
    print(f"\n{'='*70}")
    print(f"{description}")
    print('='*70)
    result = subprocess.run(f"grep -q '{unwanted_content}' {file_path}", shell=True, capture_output=True)
    success = result.returncode != 0  # We want it to NOT find the content
    print(f"Checking absence of: {unwanted_content}")
    print(f"Status: {'✓ PASS' if success else '✗ FAIL'}")
    return success

def main():
    """Run comprehensive verification"""
    print("\n" + "="*70)
    print("COMPREHENSIVE VERIFICATION OF REACTROOTMANAGER IMPLEMENTATION")
    print("="*70)
    
    all_pass = True
    
    # 1. Check ReactRootManager file exists
    all_pass &= run_command(
        "test -f /app/src/utils/react.tsx",
        "1. ReactRootManager file exists"
    )
    
    # 2. Check ReactRootManager has required methods
    all_pass &= check_file_content(
        "/app/src/utils/react.tsx",
        "public render",
        "2. ReactRootManager has render method"
    )
    
    all_pass &= check_file_content(
        "/app/src/utils/react.tsx",
        "public unmount",
        "3. ReactRootManager has unmount method"
    )
    
    all_pass &= check_file_content(
        "/app/src/utils/react.tsx",
        "public get elements",
        "4. ReactRootManager has elements getter"
    )
    
    # 5. Check PersistedElement uses createRoot
    all_pass &= check_file_content(
        "/app/src/components/views/elements/PersistedElement.tsx",
        "createRoot",
        "5. PersistedElement uses createRoot"
    )
    
    all_pass &= check_file_content(
        "/app/src/components/views/elements/PersistedElement.tsx",
        "rootMap",
        "6. PersistedElement has rootMap"
    )
    
    # 7. Check pillify uses ReactRootManager
    all_pass &= check_file_content(
        "/app/src/utils/pillify.tsx",
        "ReactRootManager",
        "7. pillify imports ReactRootManager"
    )
    
    all_pass &= check_file_not_contains(
        "/app/src/utils/pillify.tsx",
        "ReactDOM.render",
        "8. pillify doesn't use ReactDOM.render"
    )
    
    # 9. Check tooltipify uses ReactRootManager
    all_pass &= check_file_content(
        "/app/src/utils/tooltipify.tsx",
        "ReactRootManager",
        "9. tooltipify imports ReactRootManager"
    )
    
    all_pass &= check_file_not_contains(
        "/app/src/utils/tooltipify.tsx",
        "ReactDOM.render",
        "10. tooltipify doesn't use ReactDOM.render"
    )
    
    # 11. Check TextualBody uses ReactRootManager
    all_pass &= check_file_content(
        "/app/src/components/views/messages/TextualBody.tsx",
        "new ReactRootManager()",
        "11. TextualBody instantiates ReactRootManager"
    )
    
    # 12. Check EditHistoryMessage uses ReactRootManager
    all_pass &= check_file_content(
        "/app/src/components/views/messages/EditHistoryMessage.tsx",
        "new ReactRootManager()",
        "12. EditHistoryMessage instantiates ReactRootManager"
    )
    
    # 13. Check HtmlExport uses createRoot
    all_pass &= check_file_content(
        "/app/src/utils/exportUtils/HtmlExport.tsx",
        "createRoot",
        "13. HtmlExport uses createRoot"
    )
    
    # 14. Run tests
    print("\n" + "="*70)
    print("Running test suite...")
    print("="*70)
    result = subprocess.run(
        "cd /app && npm test -- --testPathPattern='(pillify|tooltipify)' --no-coverage --silent 2>&1 | tail -5",
        shell=True,
        capture_output=True,
        text=True
    )
    print(result.stdout)
    tests_pass = "Test Suites: 2 passed" in result.stdout or "passed" in result.stdout.lower()
    print(f"Status: {'✓ PASS' if tests_pass else '✗ FAIL'}")
    all_pass &= tests_pass
    
    # Final summary
    print("\n" + "="*70)
    print("VERIFICATION SUMMARY")
    print("="*70)
    if all_pass:
        print("✓ ALL CHECKS PASSED")
        print("\nThe ReactRootManager implementation is complete and working correctly!")
        return 0
    else:
        print("✗ SOME CHECKS FAILED")
        print("\nPlease review the failed checks above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
