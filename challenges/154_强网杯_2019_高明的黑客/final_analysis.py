import os
import re

def analyze_php_file(filepath):
    with open(filepath, 'r', errors='ignore') as f:
        content = f.read()
        lines = content.split('\n')
    
    results = []
    
    for i, line in enumerate(lines):
        # Check for dangerous function calls
        match = re.search(r"(system|exec|shell_exec|passthru|eval|assert)\s*\(\s*\$_GET\['([^']+)'\]", line)
        if match:
            func, param = match.groups()
            
            # Check if this line has a false condition inline
            false_cond_inline = re.search(r"if\s*\(['\"]([^'\"]+)['\"]\s*==\s*['\"]([^'\"]+)['\"]\s*\)\s*" + func, line)
            if false_cond_inline:
                str1, str2 = false_cond_inline.groups()
                if str1 != str2:
                    continue  # False condition, skip
            
            # Check if previous line is a false condition (without braces)
            if i > 0:
                prev_line = lines[i-1].strip()
                false_cond_prev = re.search(r"if\s*\(['\"]([^'\"]+)['\"]\s*==\s*['\"]([^'\"]+)['\"]\s*\)\s*$", prev_line)
                if false_cond_prev:
                    str1, str2 = false_cond_prev.groups()
                    if str1 != str2:
                        continue  # False condition, skip
            
            # Check if parameter is overwritten before this line
            is_overwritten = False
            for j in range(i):
                if re.search(rf"\$_GET\['{param}'\]\s*=\s*['\"]", lines[j]):
                    is_overwritten = True
                    break
            if is_overwritten:
                continue
            
            results.append((i+1, func, param, line.strip()))
    
    return results

all_results = []
for filename in sorted(os.listdir('src')):
    if filename.endswith('.php'):
        filepath = os.path.join('src', filename)
        results = analyze_php_file(filepath)
        if results:
            for r in results:
                all_results.append((filename, r[0], r[1], r[2], r[3]))

print(f"Found {len(all_results)} working backdoors:")
for filename, line_num, func, param, line in all_results[:20]:
    print(f"\n{filename}:{line_num} {func}($_GET['{param}'])")
    print(f"  {line}")
