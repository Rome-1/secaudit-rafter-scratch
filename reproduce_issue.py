#!/usr/bin/env python3

"""
Script to reproduce the current function signatures for extended attributes
and demonstrate the changes needed according to the PR description.
"""

import os
import re
import subprocess


def check_current_signatures():
    """Check current function signatures in the codebase"""
    print("=== Current Extended Attributes Implementation ===\n")
    
    # Check the current createFileExtendedAttributes function signature
    with open('/app/applications/drive/src/app/store/_links/extendedAttributes.ts', 'r') as f:
        content = f.read()
        
    # Extract the createFileExtendedAttributes function
    create_file_match = re.search(
        r'export function createFileExtendedAttributes\((.*?)\): ExtendedAttributes \{',
        content,
        re.DOTALL
    )
    
    if create_file_match:
        print("Current createFileExtendedAttributes signature:")
        print("export function createFileExtendedAttributes(")
        params = create_file_match.group(1)
        # Clean up the parameters display
        params = re.sub(r'\s+', ' ', params.strip())
        print(f"    {params}")
        print("): ExtendedAttributes")
        print()
    
    # Extract the encryptFileExtendedAttributes function
    encrypt_file_match = re.search(
        r'export async function encryptFileExtendedAttributes\((.*?)\) \{',
        content,
        re.DOTALL
    )
    
    if encrypt_file_match:
        print("Current encryptFileExtendedAttributes signature:")
        print("export async function encryptFileExtendedAttributes(")
        params = encrypt_file_match.group(1)
        # Clean up the parameters display
        params = re.sub(r'\s+', ' ', params.strip())
        print(f"    {params}")
        print(")")
        print()

    # Check current type definitions
    print("Current ExtendedAttributes interface:")
    ext_attr_match = re.search(
        r'interface ExtendedAttributes \{(.*?)\}',
        content,
        re.DOTALL
    )
    if ext_attr_match:
        print("interface ExtendedAttributes {")
        print(ext_attr_match.group(1).strip())
        print("}")
        print()

    print("Current ParsedExtendedAttributes interface:")
    parsed_ext_attr_match = re.search(
        r'interface ParsedExtendedAttributes \{(.*?)\}',
        content,
        re.DOTALL
    )
    if parsed_ext_attr_match:
        print("interface ParsedExtendedAttributes {")
        print(parsed_ext_attr_match.group(1).strip())
        print("}")
        print()

    # Check usage in worker.ts
    print("=== Current Usage in Worker ===")
    worker_file = '/app/applications/drive/src/app/store/_uploads/worker/worker.ts'
    with open(worker_file, 'r') as f:
        worker_content = f.read()
        
    # Find encryptFileExtendedAttributes usage
    usage_match = re.search(
        r'encryptFileExtendedAttributes\((.*?)\)',
        worker_content,
        re.DOTALL
    )
    if usage_match:
        print("Current usage in worker:")
        print(f"encryptFileExtendedAttributes({usage_match.group(1).strip()})")
        print()

    print("=== Issues Identified ===")
    print("1. Functions accept multiple separate parameters instead of a single object")
    print("2. Type definitions could be more strict (SHA1 should be required)")
    print("3. Missing DeepPartial utility type")
    print("4. Parser functions don't use proper types")
    print("5. Function signatures are verbose and error-prone")


if __name__ == "__main__":
    check_current_signatures()