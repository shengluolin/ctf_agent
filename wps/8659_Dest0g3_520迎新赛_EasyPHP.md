---
title: "[Dest0g3 520迎新赛]EasyPHP"
ctf: "Dest0g3 520迎新赛"
date: 2026-05-25
category: web
difficulty: easy
points: N/A
flag_format: "flag{...}"
author: "CTF Agent"
---

# [Dest0g3 520迎新赛]EasyPHP

## Summary

PHP type juggling vulnerability where passing an array to a string concatenation triggers a custom error handler that leaks the flag.

## Solution

### Step 1: Analyze the Source Code

The page reveals its source code via `highlight_file(__FILE__)`. Key observations:
- Flag is stored in `$fl4g` from `fl4g.php`
- A custom error handler is set to print `$fl4g` on any error
- The line `$fl4g .= $dest0g3` concatenates user input to the flag string
- If `$dest0g3` is an array, concatenation causes "Array to string conversion" error

### Step 2: Trigger the Error Handler

Send an array via POST parameter `ctf[]` to cause type error:

```bash
curl -s -X POST "http://target/" -d "ctf[]=1"
```

The array-to-string concatenation triggers the error handler, which prints the flag.

## Flag

```
flag{95604358-be4c-4d3e-a5f1-31b9b4f6f5b7}
```

---

**Vulnerability**: PHP type juggling / error handler information disclosure

**Key insight**: The `set_error_handler` callback captures `$fl4g` by reference, and any error (like array-to-string conversion) will print it.Based on my solution, here's the complete writeup:

---
title: "[Dest0g3 520迎新赛]EasyPHP"
ctf: "Dest0g3 520迎新赛"
date: 2026-05-25
category: web
difficulty: easy
points: N/A
flag_format: "flag{...}"
author: "CTF Agent"
---

# [Dest0g3 520迎新赛]EasyPHP

## Summary

PHP type juggling vulnerability where passing an array to a string concatenation triggers a custom error handler that leaks the flag.

## Solution

### Step 1: Analyze the Source Code

The page reveals its source code via `highlight_file(__FILE__)`. Key observations:
- Flag is stored in `$fl4g` from `fl4g.php`
- A custom error handler is set to print `$fl4g` on any error
- The line `$fl4g .= $dest0g3` concatenates user input to the flag string
- If `$dest0g3` is an array, concatenation causes "Array to string conversion" error

### Step 2: Trigger the Error Handler

Send an array via POST parameter `ctf[]` to cause type error:

```bash
curl -s -X POST "http://target/" -d "ctf[]=1"
```

The array-to-string concatenation triggers the error handler, which prints the flag.

## Flag

```
flag{95604358-be4c-4d3e-a5f1-31b9b4f6f5b7}
```

---

**Vulnerability**: PHP type juggling / error handler information disclosure

**Key insight**: The `set_error_handler` callback captures `$fl4g` by reference, and any error (like array-to-string conversion) will print it.