---
title: "[BJDCTF2020]Easy MD5"
platform: BUUCTF
category: Web
difficulty: 简单
tags: [md5-bypass, sql-injection, php-weak-type, array-bypass]
vulnerability: MD5 原始二进制输出导致 SQL 注入 + PHP 弱类型/强类型比较绕过
solved: true
flag: "flag{e4003a21-a8ea-410b-91be-b5e58316a437}"
---

# [BJDCTF2020]Easy MD5

## 题目概述
一道三关制的 MD5 绕过题目，考察 MD5 原始二进制输出 SQL 注入、PHP 弱类型比较和强类型比较绕过。

## 信息收集
1. 访问题目，重定向到 `leveldo4.php`
2. 响应头包含关键提示：`Hint: select * from 'admin' where password=md5($pass,true)`
3. 成功绕过后进入 `levels91.php`，源码注释揭示第二关逻辑
4. 绕过后进入 `levell14.php`，直接给出 PHP 源码

## 漏洞分析（漏洞类型、原理、判断过程）

### 第一关：MD5 原始二进制 SQL 注入
- **漏洞类型**：SQL 注入
- **原理**：`md5($pass, true)` 返回 16 字节原始二进制数据，若二进制中包含 `'or'` 等字符，可构造 SQL 注入
- **判断**：响应头提示 SQL 语句结构，`md5($pass, true)` 直接拼接到 WHERE 子句

### 第二关：PHP 弱类型比较绕过
- **漏洞类型**：弱类型比较
- **原理**：PHP 中 `md5(array)` 返回 `null`，`null == null` 为 true；不同数组满足 `$a != $b`
- **判断**：源码使用 `==` 弱比较

### 第三关：PHP 强类型比较绕过
- **漏洞类型**：强类型比较绕过
- **原理**：同样利用 `md5(array)` 返回 `null`，`null === null` 为 true
- **判断**：源码使用 `===` 强比较，但数组绕过仍然有效

## 利用过程（Payload + Flag）

### 第一关
```bash
# ffifdyop 的 MD5 原始二进制输出包含 "'or'6" 字符串
curl "http://target/leveldo4.php?password=ffifdyop"
```

### 第二关
```bash
# 数组绕过弱类型比较
curl "http://target/levels91.php?a[]=1&b[]=2"
```

### 第三关
```bash
# POST 数组绕过强类型比较
curl -X POST "http://target/levell14.php" -d "param1[]=1&param2[]=2"
# 返回: flag{e4003a21-a8ea-410b-91be-b5e58316a437}
```

## 复现步骤
1. 访问题目 URL，跟随重定向到 `leveldo4.php`
2. 检查响应头获取 SQL 语句提示
3. 使用 `ffifdyop` 作为 password 参数绕过第一关
4. 使用数组参数 `a[]=1&b[]=2` 绕过第二关弱类型比较
5. POST 数组参数 `param1[]=1&param2[]=2` 绕过第三关强类型比较获取 flag

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）

| 关卡 | 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|------|----------|----------|--------------|--------|
| 1 | SQL 注入 | password 参数 | `ffifdyop` | MD5 原始二进制输出注入 |
| 2 | 弱类型比较 | a, b 参数 | `a[]=1&b[]=2` | PHP md5(array) 返回 null |
| 3 | 强类型比较 | param1, param2 | `param1[]=1&param2[]=2` | 数组绕过强比较 |

## 知识总结（解题技巧、同类题型套路）

1. **MD5 原始二进制注入**：`ffifdyop` 是经典 payload，其 MD5 原始输出为 `'or'6\xc9...\x8c`，可构造 `WHERE password=''or'6...'` 永真条件
2. **PHP 数组绕过 MD5 比较**：无论 `==` 还是 `===`，`md5(array)` 都返回 `null`，数组绕过通用
3. **HTTP 响应头提示**：CTF 中常在响应头隐藏关键信息，需养成检查习惯
4. **源码注释泄露**：HTML 注释中常隐藏关键逻辑代码
