import os
import re

def find_clean_backdoors():
    results = []
    
    for filename in os.listdir('src'):
        if not filename.endswith('.php'):
            continue
        filepath = os.path.join('src', filename)
        
        with open(filepath, 'r', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # Look for direct system/exec calls with GET/POST
            # Pattern: system($_GET['xxx']) or system($_POST['xxx'])
            match = re.search(r"(system|exec|shell_exec|passthru)\s*\(\s*\$_(GET|POST)\s*\[\s*['\"]([^'\"]+)['\"]\s*\]", line)
            if match:
                func, method, param = match.groups()
                # Check if this line is NOT inside a false if condition
                # Look at previous lines for context
                prev_lines = '\n'.join(lines[:i])
                
                # Find the last unclosed if statement
                # Simple heuristic: check if the previous non-empty line is an if with false condition
                is_dead = False
                
                # Check if line itself has inline if with false condition
                inline_if = re.search(r"if\s*\(\s*['\"]([^'\"]+)['\"]\s*==\s*['\"]([^'\"]+)['\"]\s*\)\s*" + func, line)
                if inline_if:
                    str1, str2 = inline_if.groups()
                    if str1 != str2:
                        is_dead = True
                
                if not is_dead:
                    # Check previous line for false if
                    j = i - 1
                    while j >= 0 and lines[j].strip() == '':
                        j -= 1
                    if j >= 0:
                        prev_line = lines[j]
                        if_match = re.search(r"if\s*\(\s*['\"]([^'\"]+)['\"]\s*==\s*['\"]([^'\"]+)['\"]\s*\)", prev_line)
                        if if_match:
                            str1, str2 = if_match.groups()
                            if str1 != str2:
                                is_dead = True
                
                if not is_dead:
                    results.append((filename, i+1, func, method, param, line.strip()))
    
    return results

results = find_clean_backdoors()
print(f"Found {len(results)} potentially working backdoors:")
for r in results[:30]:
    print(f"{r[0]}:{r[1]}: {r[2]}($_{r[3]}['{r[4]}'])")
