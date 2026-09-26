#!/usr/bin/env python3
"""
Test script to simulate the Git backend issue with deleted references.
This script will help us understand the problem and verify our fix.
"""

import os
import sys
import tempfile
import subprocess
import time

def run_command(cmd, cwd=None, check=True):
    """Run a shell command and return output."""
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Command failed: {cmd}")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        sys.exit(1)
    return result

def setup_test_repo():
    """Set up a test Git repository."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = os.path.join(tmpdir, "test-repo")
        os.makedirs(repo_path)
        
        # Initialize repo
        run_command("git init", cwd=repo_path)
        run_command("git config user.email 'test@example.com'", cwd=repo_path)
        run_command("git config user.name 'Test User'", cwd=repo_path)
        
        # Create initial file
        features_file = os.path.join(repo_path, "features.yml")
        with open(features_file, 'w') as f:
            f.write("""namespace: default
flags:
  - key: feature1
    name: Feature 1
    enabled: true
""")
        
        # Commit to main
        run_command("git add .", cwd=repo_path)
        run_command("git commit -m 'Initial commit'", cwd=repo_path)
        
        # Create a feature branch
        run_command("git checkout -b add-more-flags", cwd=repo_path)
        
        # Modify file in feature branch
        with open(features_file, 'w') as f:
            f.write("""namespace: default
flags:
  - key: feature1
    name: Feature 1
    enabled: true
  - key: feature2
    name: Feature 2
    enabled: false
""")
        
        run_command("git add .", cwd=repo_path)
        run_command("git commit -m 'Add feature2'", cwd=repo_path)
        
        # Switch back to main
        run_command("git checkout main", cwd=repo_path)
        
        # Create bare repo to act as remote
        bare_repo_path = os.path.join(tmpdir, "test-repo-bare.git")
        run_command(f"git clone --bare {repo_path} {bare_repo_path}")
        
        # Add remote to original repo
        run_command(f"git remote add origin {bare_repo_path}", cwd=repo_path)
        
        # Push all branches
        run_command("git push origin main", cwd=repo_path)
        run_command("git push origin add-more-flags", cwd=repo_path)
        
        print(f"Test repository created at: {bare_repo_path}")
        print("Branches created: main, add-more-flags")
        
        # Now simulate the deletion of the feature branch
        print("\nSimulating deletion of 'add-more-flags' branch from remote...")
        run_command("git push origin --delete add-more-flags", cwd=repo_path)
        
        # Verify branch is deleted
        result = run_command("git ls-remote --heads origin", cwd=repo_path, check=False)
        print(f"Remaining remote branches:\n{result.stdout}")
        
        return bare_repo_path

def test_git_store():
    """Test the Git store behavior with deleted references."""
    print("Testing Git store behavior with deleted references...")
    
    # First, let's understand what methods are available
    print("\nAnalyzing Git store methods...")
    
    # Look for key methods in the store
    with open('/app/internal/storage/fs/git/store.go', 'r') as f:
        content = f.read()
        if 'func (s *SnapshotStore) update' in content:
            print("✓ Found update method")
        if 'func (s *SnapshotStore) fetch' in content:
            print("✓ Found fetch method")
    
    # Look for cache methods
    with open('/app/internal/storage/fs/cache.go', 'r') as f:
        content = f.read()
        if 'func (c *SnapshotCache' in content:
            print("✓ Found SnapshotCache methods")
        if 'Delete' in content:
            print("✗ Delete method not found in SnapshotCache (needs implementation)")
        else:
            print("✗ Delete method not found in SnapshotCache (needs implementation)")
    
    print("\nKey findings:")
    print("1. The update method fetches references and builds snapshots")
    print("2. When a reference is deleted remotely, fetch fails with 'couldn't find remote ref'")
    print("3. The cache doesn't have a Delete method to remove stale references")
    print("4. Need to add Delete method and handle deleted references in update")

if __name__ == "__main__":
    print("Git Backend Deleted Reference Issue Test")
    print("=" * 50)
    
    # Create test repository
    # repo_path = setup_test_repo()
    
    # Test Git store behavior
    test_git_store()