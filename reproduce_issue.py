#!/usr/bin/env python3

"""
Script to identify duplicated CSS for buttons in encryption settings.
This script will look for the mx_ChangeRecoveryKey_footer and mx_ResetIdentityPanel_footer
classes in both CSS and TSX files and demonstrate the duplication issue.
"""

import os
import re
from typing import Dict, List, Set

def find_files_with_patterns(base_dir: str, file_extensions: List[str], patterns: List[str]) -> Dict[str, List[str]]:
    """Find files that contain any of the specified patterns."""
    matches = {}
    
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if any(file.endswith(ext) for ext in file_extensions):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        for pattern in patterns:
                            if pattern in content:
                                if file_path not in matches:
                                    matches[file_path] = []
                                matches[file_path].append(pattern)
                except Exception as e:
                    pass  # Skip files that can't be read
    return matches

def extract_css_rules(file_path: str, class_names: List[str]) -> Dict[str, str]:
    """Extract CSS rules for the specified class names."""
    rules = {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        for class_name in class_names:
            # Look for CSS rules for this class
            pattern = rf'\.{re.escape(class_name)}\s*\{{([^}}]+)\}}'
            matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
            if matches:
                # Clean up the rule content
                rule = matches[0].strip()
                rules[class_name] = rule
                
    except Exception as e:
        pass
        
    return rules

def count_tsx_usage(file_path: str, class_names: List[str]) -> Dict[str, int]:
    """Count how many times each class name is used in TSX files."""
    counts = {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        for class_name in class_names:
            # Count occurrences of className="class_name"
            pattern = rf'className\s*=\s*["\'].*?{re.escape(class_name)}.*?["\']'
            matches = re.findall(pattern, content)
            counts[class_name] = len(matches)
            
    except Exception as e:
        pass
        
    return counts

def main():
    print("=== Analyzing Duplicated CSS for Encryption Settings Buttons ===\n")
    
    base_dir = "/app"
    target_classes = ["mx_ChangeRecoveryKey_footer", "mx_ResetIdentityPanel_footer"]
    
    # Find all files that contain these patterns
    css_files = find_files_with_patterns(base_dir, ['.pcss', '.css'], target_classes)
    tsx_files = find_files_with_patterns(base_dir, ['.tsx'], target_classes)
    
    print("🔍 Files containing duplicated button CSS classes:\n")
    
    print("📄 CSS/PCSS Files:")
    for file_path, patterns in css_files.items():
        if 'test' not in file_path and 'node_modules' not in file_path:
            print(f"  {file_path}: {patterns}")
    
    print("\n📄 TSX Files:")
    for file_path, patterns in tsx_files.items():
        if 'test' not in file_path and 'node_modules' not in file_path:
            print(f"  {file_path}: {patterns}")
    
    print("\n" + "="*70)
    print("🔧 Analyzing CSS Rules Duplication:\n")
    
    # Extract CSS rules from each file
    all_rules = {}
    for file_path in css_files:
        if 'test' not in file_path and 'node_modules' not in file_path:
            rules = extract_css_rules(file_path, target_classes)
            if rules:
                all_rules[file_path] = rules
    
    # Display the duplicated rules
    for file_path, rules in all_rules.items():
        print(f"📁 {file_path}:")
        for class_name, rule in rules.items():
            print(f"  .{class_name} {{")
            for line in rule.split('\n'):
                if line.strip():
                    print(f"    {line.strip()}")
            print("  }")
        print()
    
    # Check for duplication by comparing rules
    print("🔍 Duplication Analysis:")
    rule_signatures = {}
    for file_path, rules in all_rules.items():
        for class_name, rule in rules.items():
            # Normalize the rule for comparison
            normalized = re.sub(r'\s+', ' ', rule.strip().lower())
            if normalized not in rule_signatures:
                rule_signatures[normalized] = []
            rule_signatures[normalized].append((file_path, class_name))
    
    duplicates_found = False
    for signature, usages in rule_signatures.items():
        if len(usages) > 1:
            duplicates_found = True
            print(f"\n❌ DUPLICATE RULE FOUND:")
            print(f"   Rule signature: {signature}")
            print(f"   Used in:")
            for file_path, class_name in usages:
                print(f"     - {class_name} in {file_path}")
    
    if not duplicates_found:
        print("\n✅ No exact duplicates found, but similar rules exist.")
    
    # Count TSX usage
    print("\n" + "="*70)
    print("📊 TSX Usage Analysis:\n")
    
    total_usage = {}
    for file_path in tsx_files:
        if 'test' not in file_path and 'node_modules' not in file_path:
            counts = count_tsx_usage(file_path, target_classes)
            if any(count > 0 for count in counts.values()):
                print(f"📁 {file_path}:")
                for class_name, count in counts.items():
                    if count > 0:
                        print(f"  {class_name}: {count} usage(s)")
                        total_usage[class_name] = total_usage.get(class_name, 0) + count
    
    print(f"\n📈 Total Usage Summary:")
    for class_name, count in total_usage.items():
        print(f"  {class_name}: {count} total usage(s)")
    
    print("\n" + "="*70)
    print("💡 Issue Summary:")
    print("   - Both mx_ChangeRecoveryKey_footer and mx_ResetIdentityPanel_footer")
    print("   - contain similar CSS properties (display: flex, flex-direction: column, etc.)")
    print("   - This creates maintenance overhead and inconsistency")
    print("   - Should be consolidated into mx_EncryptionCard_buttons")

if __name__ == "__main__":
    main()