#!/usr/bin/env python3
import os
import re

SRC_DIR = "/home/lls/data/ctf-agent/challenges/154_强网杯_2019_高明的黑客/src"

def analyze_file(filepath):
    """Analyze a PHP file for potential exploitable code"""
    with open(filepath, 'r', errors='ignore') as f:
        content = f.read()
    
    # Find all variable assignments that override $_GET/$_POST
    # Pattern: $_GET['param'] = 'something';
    overrides = set()
    override_pattern = r'\$_GET\[\'([^\']+)\'\]\s*=\s*[\'"][^\'"]*[\'"]'
    for match in re.findall(override_pattern, content):
        overrides.add(match)
    
    # Find all dangerous function calls with $_GET params
    # Pattern: function($_GET['param'] ?? 'default')
    dangerous_calls = []
    patterns = [
        (r'system\s*\(\s*\$_GET\[\'([^\']+)\'\]', 'system'),
        (r'exec\s*\(\s*\$_GET\[\'([^\']+)\'\]', 'exec'),
        (r'shell_exec\s*\(\s*\$_GET\[\'([^\']+)\'\]', 'shell_exec'),
        (r'passthru\s*\(\s*\$_GET\[\'([^\']+)\'\]', 'passthru'),
        (r'eval\s*\(\s*\$_GET\[\'([^\']+)\'\]', 'eval'),
        (r'assert\s*\(\s*\$_GET\[\'([^\']+)\'\]', 'assert'),
        (r'echo\s*`[^`]*\$_GET\[\'([^\']+)\'\]', 'backtick'),
    ]
    
    for pattern, func in patterns:
        for match in re.findall(pattern, content):
            dangerous_calls.append((match, func))
    
    # Filter out overridden params
    exploitable = []
    for param, func in dangerous_calls:
        if param not in overrides:
            exploitable.append((param, func))
    
    return exploitable

def main():
    files = os.listdir(SRC_DIR)
    print(f"Total files: {len(files)}")
    
    potential = []
    for f in files:
        if f.endswith('.php'):
            filepath = os.path.join(SRC_DIR, f)
            exploitable = analyze_file(filepath)
            if exploitable:
                potential.append((f, exploitable))
    
    print(f"\nFiles with potentially exploitable code: {len(potential)}")
    for f, params in potential[:50]:
        print(f"\n{f}:")
        for param, func in params:
            print(f"  {func}($_GET['{param}'])")

if __name__ == '__main__':
    main()
