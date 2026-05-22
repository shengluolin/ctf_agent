import os
import re

def check_file(filepath):
    with open(filepath, 'r', errors='ignore') as f:
        content = f.read()
        lines = content.split('\n')
    
    results = []
    for i, line in enumerate(lines, 1):
        # Look for dangerous function calls
        if re.search(r'\b(system|exec|shell_exec|passthru|eval|assert)\s*\(', line):
            # Check if this line is inside a false if condition
            # Look backwards for the nearest if statement
            before = '\n'.join(lines[:i])
            
            # Find the last 'if' statement before this line
            if_match = None
            for m in re.finditer(r"if\s*\(\s*['\"]([^'\"]+)['\"]\s*==\s*['\"]([^'\"]+)['\"]\s*\)", before):
                if_match = m
            
            # Check if the dangerous call is inside a false condition
            is_dead = False
            if if_match:
                # Check if this line comes after the if and before any closing brace or else
                after_if = before[if_match.end():]
                # Simple check: if the condition compares two different strings, it's dead
                str1, str2 = if_match.groups()
                if str1 != str2:
                    # This is a false condition - check if our line is inside this block
                    # Count braces to see if we're inside
                    brace_count = 0
                    for ch in after_if:
                        if ch == '{':
                            brace_count += 1
                        elif ch == '}':
                            brace_count -= 1
                            if brace_count < 0:
                                break
                    # If we're still inside the block (brace_count >= 0), it's dead code
                    if brace_count >= 0:
                        is_dead = True
            
            if not is_dead:
                # Also check if line itself has a false condition
                inline_if = re.search(r"if\s*\(\s*['\"]([^'\"]+)['\"]\s*==\s*['\"]([^'\"]+)['\"]\s*\)\s*(system|exec|shell_exec|passthru|eval|assert)", line)
                if inline_if:
                    str1, str2 = inline_if.groups()
                    if str1 != str2:
                        is_dead = True
            
            if not is_dead:
                # Check if line is commented out
                stripped = line.strip()
                if not stripped.startswith('//') and not stripped.startswith('/*'):
                    results.append((i, line.strip()))
    
    return results

# Scan all PHP files
found = []
for filename in os.listdir('src'):
    if filename.endswith('.php'):
        filepath = os.path.join('src', filename)
        results = check_file(filepath)
        if results:
            for line_num, line in results:
                found.append((filename, line_num, line))

print(f"Found {len(found)} potentially reachable dangerous calls")
for filename, line_num, line in found[:50]:
    print(f"{filename}:{line_num}: {line[:100]}")
