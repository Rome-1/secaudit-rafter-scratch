#!/usr/bin/env python3
"""
Script to reproduce the issue described in the PR.

The issue is that non-legacy mails fail to decrypt and display their details
because the worker's EntityClient.load and loadMultiple calls don't propagate 
the mail's ownerEncSessionKey through the caching layers.
"""

import os
import subprocess
import sys

def check_current_implementation():
    """Check the current implementation to confirm the issue exists."""
    print("Checking current implementation...")
    
    # Check if EntityClient.load supports providedOwnerEncSessionKey
    result = subprocess.run([
        'grep', '-n', 'providedOwnerEncSessionKey', 
        '/app/src/api/common/EntityClient.ts'
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print("✗ EntityClient.load does NOT support providedOwnerEncSessionKey parameter")
    else:
        print("✓ EntityClient.load already supports providedOwnerEncSessionKey parameter")
    
    # Check if loadMultiple supports providedOwnerEncSessionKey
    result = subprocess.run([
        'grep', '-n', 'loadMultiple.*providedOwnerEncSessionKey',
        '/app/src/api/common/EntityClient.ts'
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print("✗ EntityClient.loadMultiple does NOT support providedOwnerEncSessionKey parameter")
    else:
        print("✓ EntityClient.loadMultiple already supports providedOwnerEncSessionKey parameter")
    
    # Check if DefaultEntityRestCache propagates the key
    result = subprocess.run([
        'grep', '-n', 'providedOwnerEncSessionKey',
        '/app/src/api/worker/rest/DefaultEntityRestCache.ts'
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print("✗ DefaultEntityRestCache does NOT propagate providedOwnerEncSessionKey")
    else:
        print("✓ DefaultEntityRestCache propagates providedOwnerEncSessionKey")
    
    # Check if sessionKeyCache exists in CryptoFacade
    result = subprocess.run([
        'grep', '-n', 'sessionKeyCache',
        '/app/src/api/worker/crypto/CryptoFacade.ts'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✗ CryptoFacade still contains sessionKeyCache (should be removed)")
    else:
        print("✓ CryptoFacade does NOT contain sessionKeyCache")
    
    print("\nCurrent implementation check completed.")
    return True

def main():
    print("Reproducing the mail decryption issue...")
    check_current_implementation()
    
    print("""
The issue is that when non-legacy mails are loaded, the system needs to:
1. Pass the mail's ownerEncSessionKey to EntityClient.load/loadMultiple
2. Propagate this key through caching layers (DefaultEntityRestCache)
3. Use the key directly for decryption instead of relying on sessionKeyCache

Without these changes, mail details, reply-tos, and attachments fail to decrypt.
""")

if __name__ == "__main__":
    main()