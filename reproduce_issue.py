#!/usr/bin/env python3

"""
Script to demonstrate the issue with deleted Git references.

The problem is that when a reference is cached but no longer exists on the remote,
the Git backend fails during polling because it tries to resolve a non-existent reference.
"""

import os
import tempfile
import shutil
import subprocess
import time
import sys

def run_command(cmd, cwd=None, capture=True):
    """Run a command and return the result."""
    try:
        if capture:
            result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
            return result.returncode == 0, result.stdout, result.stderr
        else:
            result = subprocess.run(cmd, shell=True, cwd=cwd)
            return result.returncode == 0, "", ""
    except Exception as e:
        return False, "", str(e)

def create_git_repo():
    """Create a temporary Git repository with a branch."""
    repo_dir = tempfile.mkdtemp(prefix="git_test_repo_")
    
    # Initialize git repo
    run_command("git init", cwd=repo_dir)
    run_command("git config user.name 'Test User'", cwd=repo_dir)
    run_command("git config user.email 'test@example.com'", cwd=repo_dir)
    
    # Create main branch with initial commit
    with open(os.path.join(repo_dir, "README.md"), "w") as f:
        f.write("# Test Repository\n")
    
    run_command("git add .", cwd=repo_dir)
    run_command("git commit -m 'Initial commit'", cwd=repo_dir)
    
    # Create a feature branch
    run_command("git checkout -b feature-branch", cwd=repo_dir)
    
    with open(os.path.join(repo_dir, "feature.txt"), "w") as f:
        f.write("Feature content\n")
    
    run_command("git add .", cwd=repo_dir)
    run_command("git commit -m 'Add feature'", cwd=repo_dir)
    
    # Go back to main
    run_command("git checkout master", cwd=repo_dir)
    
    return repo_dir

def demonstrate_issue():
    """Demonstrate the Git reference deletion issue."""
    print("Creating test Git repository...")
    repo_dir = create_git_repo()
    
    try:
        print(f"Repository created at: {repo_dir}")
        
        # List branches
        success, branches, stderr = run_command("git branch -a", cwd=repo_dir)
        print(f"Branches: {branches}")
        
        # Simulate what happens when we try to resolve a branch that exists
        print("\n1. Resolving existing feature-branch:")
        success, output, stderr = run_command("git rev-parse refs/heads/feature-branch", cwd=repo_dir)
        if success:
            print(f"✓ Successfully resolved: {output.strip()}")
        else:
            print(f"✗ Failed to resolve: {stderr}")
        
        # Delete the feature branch (switch to master first)
        print("\n2. Deleting feature-branch:")
        run_command("git checkout master", cwd=repo_dir)
        success, output, stderr = run_command("git branch -D feature-branch", cwd=repo_dir)
        if success:
            print("✓ Branch deleted successfully")
        else:
            print(f"✗ Failed to delete branch: {stderr}")
        
        # Try to resolve the deleted branch (this should fail)
        print("\n3. Trying to resolve deleted feature-branch:")
        success, output, stderr = run_command("git rev-parse refs/heads/feature-branch", cwd=repo_dir)
        if success:
            print(f"✓ Unexpectedly resolved: {output.strip()}")
        else:
            print(f"✗ Expected failure: {stderr.strip()}")
            
        # List remaining branches
        success, branches, stderr = run_command("git branch -a", cwd=repo_dir)
        print(f"\nRemaining branches: {branches}")
        
        print("\n" + "="*50)
        print("ISSUE DEMONSTRATION:")
        print("This shows what happens in the Git backend:")
        print("1. The cache retains 'feature-branch' reference")
        print("2. During polling, it tries to resolve 'feature-branch'")
        print("3. git rev-parse fails because the branch no longer exists")
        print("4. This causes the entire polling cycle to fail")
        print("="*50)
        
    finally:
        # Clean up
        shutil.rmtree(repo_dir)

if __name__ == "__main__":
    demonstrate_issue()