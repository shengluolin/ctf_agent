---
title: "[Zer0pts2020]Can you guess it?"
platform: BUUCTF
category: Web
difficulty: 简单
tags: [php, basename-bypass, source-code-disclosure, php-self]
vulnerability: basename() 函数处理非 ASCII 字符时的特性导致正则绕过
solved: true
flag: "flag{c303a717-14d3-4d3d-94c5-78f4c6a0429c}"
---

# [Zer0pts2020]Can you guess it?

## 题目概述
题目是一个"猜数字"游戏，要求猜对一个 128 位随机十六进制字符串才能获得 flag。但页面提供了源码查看功能。

## 信息收集
访问 `?source` 参数可查看源码，关键代码如下：

```php
include 'config.php'; // FLAG is defined in config.php

if (preg_match('/config\.php\/*$/i', $_SERVER['PHP_SELF'])) {
  exit("I don't know what you are thinking, but I won't let you read it :)");
}

if (isset($_GET['source'])) {
  highlight_file(basename($_SERVER['PHP_SELF']));
  exit();
}
```

## 漏洞分析（漏洞类型、原理、判断过程）

**漏洞类型**：basename() 函数特性绕过正则检查

**原理**：
1. `$_SERVER['PHP_SELF']` 可通过 URL 路径控制
2. 正则 `/config\.php\/*$/i` 检查路径是否以 `config.php` 结尾
3. `basename()` 函数在处理某些非 ASCII 字符（如 `%ff`）时，会将其视为路径分隔符并去除
4. 当访问 `/index.php/config.php/%ff?source` 时：
   - 正则检查：`$_SERVER['PHP_SELF']` = `/index.php/config.php/\xff`，不以 `config.php` 结尾，绕过检查
   - `basename()` 返回 `config.php`（因为 `%ff` 被当作分隔符）
   - 最终 `highlight_file('config.php')` 泄露源码

## 利用过程（Payload + Flag）

**Payload**：
```
GET /index.php/config.php/%ff?source HTTP/1.1
```

或使用 curl：
```bash
curl -s "http://target/index.php/config.php/%ff?source"
```

**Flag**：`flag{c303a717-14d3-4d3d-94c5-78f4c6a0429c}`

## 复现步骤

1. 访问题目，点击 "Source" 链接查看源码
2. 分析源码发现 `highlight_file(basename($_SERVER['PHP_SELF']))` 可利用
3. 构造 URL：`/index.php/config.php/%ff?source`
4. 绕过正则检查，`basename()` 返回 `config.php`
5. 获取 config.php 源码中的 flag

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|--------|
| 函数特性绕过 | `$_SERVER['PHP_SELF']` + `basename()` | `/config.php/%ff?source` | basename() 对非 ASCII 字符的处理特性 |

## 知识总结（解题技巧、同类题型套路）

1. **basename() 特性**：在某些 locale 设置下，basename() 会将非 ASCII 字符（0x80-0xff）视为路径分隔符
2. **PHP_SELF 注入**：`$_SERVER['PHP_SELF']` 可通过 URL 路径控制，常用于构造攻击路径
3. **正则绕过技巧**：当正则检查和实际处理函数对同一输入有不同理解时，可利用差异绕过
