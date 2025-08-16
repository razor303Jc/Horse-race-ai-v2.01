#!/usr/bin/env python3
"""
🛡️ Root Protection Checker
Script to check if files are protected from being moved from root directory

Usage:
    python check_root_protection.py [file_name]
    
Returns:
    0 if file can be moved
    1 if file is protected
    2 if protection file not found
"""

import sys
import os
from pathlib import Path


def load_protected_files():
    """Load list of protected files from .keep-in-root"""
    protection_file = Path(".keep-in-root")
    
    if not protection_file.exists():
        return None
    
    protected_files = []
    try:
        with open(protection_file, 'r') as f:
            content = f.read()
            
        # Extract protected files from markdown content
        lines = content.split('\n')
        in_protected_section = False
        
        for line in lines:
            line = line.strip()
            
            if "## 🔒 Protected Root Files:" in line:
                in_protected_section = True
                continue
            elif line.startswith("## ") and in_protected_section:
                break
            elif in_protected_section and line.startswith("- "):
                # Extract filename from markdown list item
                filename = line[2:].strip()
                protected_files.append(filename)
        
        return protected_files
        
    except Exception as e:
        print(f"Error reading protection file: {e}", file=sys.stderr)
        return None


def is_file_protected(filename):
    """Check if a file is protected from being moved"""
    protected_files = load_protected_files()
    
    if protected_files is None:
        return False, "Protection file not found"
    
    # Check exact matches
    if filename in protected_files:
        return True, f"File '{filename}' is protected"
    
    # Check with .md extension
    if f"{filename}.md" in protected_files:
        return True, f"File '{filename}' (with .md extension) is protected"
    
    # Check without extension
    base_name = os.path.splitext(filename)[0]
    if base_name in protected_files:
        return True, f"File '{filename}' (base name '{base_name}') is protected"
    
    return False, f"File '{filename}' can be moved"


def main():
    """Main function for command line usage"""
    if len(sys.argv) != 2:
        print("Usage: python check_root_protection.py <filename>")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    if not Path(".keep-in-root").exists():
        print("Protection file .keep-in-root not found")
        sys.exit(2)
    
    is_protected, message = is_file_protected(filename)
    print(message)
    
    if is_protected:
        sys.exit(1)  # Protected - do not move
    else:
        sys.exit(0)  # Can be moved


if __name__ == "__main__":
    main()
