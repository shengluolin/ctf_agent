import os
import re

def analyze_file(filepath):
    with open(filepath, 'r', errors='ignore') as f:
        content = f.read()
        lines = content.split('\n')
    
    results = []
    
    for i, line in enumerate(lines):
        # Check for dangerous function calls
        match = re.search(r"(system|exec|shell_exec|passthru|eval|assert)\s*\(\s*\$_GET\['([^']+)'\]", line)
        if match:
            func, param = match.groups()
            
            # Check if this line has a false condition
            false_condition = re.search(r"if\s*\(['\"]([^'\"]+)['\"]\s*==\s*['\"]([^'\"]+)['\"]\)", line)
            if false_condition:
                str1, str2 = false_condition.groups()
                if str1 != str2:
                    continue  # This is dead code
            
            # Check if previous line is a false condition (without braces)
            if i > 0:
                prev_line = lines[i-1].strip()
                false_condition_prev = re.search(r"if\s*\(['\"]([^'\"]+)['\"]\s*==\s*['\"]([^'\"]+)['\"]\)", prev_line)
                if false_condition_prev:
                    str1, str2 = false_condition_prev.groups()
                    if str1 != str2:
                        continue  # This is dead code
            
            # Check if parameter is overwritten before this line
            is_overwritten = False
            for j in range(i):
                if re.search(rf"\$_GET\['{param}'\]\s*=\s*['\"]", lines[j]):
                    is_overwritten = True
                    break
            if is_overwritten:
                continue
            
            results.append((filepath, i+1, func, param, line.strip()))
    
    return results

all_results = []
for filename in os.listdir('src'):
    if filename.endswith('.php'):
        filepath = os.path.join('src', filename)
        results = analyze_file(filepath)
        all_results.extend(results)

print(f"Found {len(all_results)} working backdoors:")
for filepath, line_num, func, param, line in all_results[:30]:
    print(f"{filepath}:{line_num} {func}($_GET['{param}'])")
    print(f"  {line[:100]}")
