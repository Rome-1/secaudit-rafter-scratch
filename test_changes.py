#!/usr/bin/env python3
"""
Test script to verify ReactRootManager and related changes
"""

import subprocess
import sys

def run_command(cmd):
    """Run a command and return the result"""
    print(f"\n{'='*60}")
    print(f"Running: {cmd}")
    print('='*60)
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    return result.returncode

def main():
    """Run tests to verify changes"""
    print("Testing ReactRootManager implementation...")
    
    # Check if the ReactRootManager file exists
    print("\n1. Checking if ReactRootManager exists...")
    ret = run_command("test -f /app/src/utils/react.tsx && echo 'ReactRootManager file exists' || echo 'ReactRootManager file missing'")
    
    # Check if imports are correct
    print("\n2. Checking imports in modified files...")
    run_command("grep -l 'ReactRootManager' /app/src/components/views/messages/TextualBody.tsx /app/src/components/views/messages/EditHistoryMessage.tsx /app/src/utils/pillify.tsx /app/src/utils/tooltipify.tsx")
    
    # Check if createRoot is used
    print("\n3. Checking if createRoot is used instead of ReactDOM.render...")
    run_command("grep -n 'createRoot' /app/src/components/views/elements/PersistedElement.tsx /app/src/utils/exportUtils/HtmlExport.tsx")
    
    # Check if ReactDOM.render is removed from pillify and tooltipify
    print("\n4. Checking if ReactDOM.render is removed from pillify and tooltipify...")
    ret1 = run_command("grep 'ReactDOM.render' /app/src/utils/pillify.tsx && echo 'FAIL: ReactDOM.render still present' || echo 'PASS: ReactDOM.render removed'")
    ret2 = run_command("grep 'ReactDOM.render' /app/src/utils/tooltipify.tsx && echo 'FAIL: ReactDOM.render still present' || echo 'PASS: ReactDOM.render removed'")
    
    # Check if unmountPills and unmountTooltips are removed
    print("\n5. Checking if legacy unmount functions are removed...")
    ret1 = run_command("grep 'export function unmountPills' /app/src/utils/pillify.tsx && echo 'FAIL: unmountPills still present' || echo 'PASS: unmountPills removed'")
    ret2 = run_command("grep 'export function unmountTooltips' /app/src/utils/tooltipify.tsx && echo 'FAIL: unmountTooltips still present' || echo 'PASS: unmountTooltips removed'")
    
    print("\n" + "="*60)
    print("Verification complete!")
    print("="*60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
