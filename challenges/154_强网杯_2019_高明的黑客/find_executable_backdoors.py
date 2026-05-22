import os
import re

def find_executable_backdoors():
    results = []
    
    for filename in os.listdir('src'):
        if not filename.endswith('.php'):
            continue
        filepath = os.path.join('src', filename)
        
        with open(filepath, 'r', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Find all places where a variable is assigned from $_GET
        get_assignments = {}
        for i, line in enumerate(lines):
            match = re.search(r'\$([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*\$_GET\[\'([^\']+)\'\]', line)
            if match:
                var_name, param_name = match.groups()
                get_assignments[var_name] = (i, param_name)
        
        # Now find where these variables are used in dangerous functions
        for i, line in enumerate(lines):
            # Check for system($var), exec($var), etc.
            match = re.search(r'(system|exec|shell_exec|passthru)\s*\(\s*\$([a-zA-Z_][a-zA-Z0-9_]*)', line)
            if match:
                func, var_name = match.groups()
                if var_name in get_assignments:
                    assign_line, param_name = get_assignments[var_name]
                    # Check if assignment is before this line
                    if assign_line < i:
                        # Check for false conditions
                        false_cond = re.search(r"if\s*\(['\"]([^'\"]+)['\"]\s*==\s*['\"]([^'\"]+)['\"]\)", line)
                        if false_cond and false_cond.group(1) != false_cond.group(2):
                            continue
                        results.append((filename, i+1, func, param_name, var_name, line.strip()))
            
            # Check for backtick execution
            match = re.search(r'echo\s*`\{?\$([a-zA-Z_][a-zA-Z0-9_]*)\}?`', line)
            if match:
                var_name = match.group(1)
                if var_name in get_assignments:
                    assign_line, param_name = get_assignments[var_name]
                    if assign_line < i:
                        false_cond = re.search(r"if\s*\(['\"]([^'\"]+)['\"]\s*==\s*['\"]([^'\"]+)['\"]\)", line)
                        if false_cond and false_cond.group(1) != false_cond.group(2):
                            continue
                        results.append((filename, i+1, 'backtick', param_name, var_name, line.strip()))
    
    return results

results = find_executable_backdoors()
print(f"Found {len(results)} executable backdoors:")
for r in results[:30]:
    print(f"{r[0]}:{r[1]} {r[2]}(${r[4]}) from $_GET['{r[3]}']")
    print(f"  {r[5][:100]}")
