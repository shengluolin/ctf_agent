---
title: "[网鼎杯 2018]Fakebook"
platform: BUUCTF
category: Web
difficulty: 中等
tags: [sql-injection, ssrf, php-deserialization, waf-bypass, file-read]
vulnerability: SQL注入 + SSRF/PHP反序列化组合漏洞
solved: true
flag: "flag{593fd702-4a30-49c6-b1e4-e2a576738255}"
---

# [网鼎杯 2018]Fakebook

## 题目概述
一个模拟社交网站的 Web 应用，用户可以注册、登录，并在个人主页展示博客链接。题目提供了登录、注册功能，以及用户信息展示页面。

## 信息收集
1. **访问首页**：发现是 Fakebook 社交网站，有 `login.php` 和 `join.php` 入口
2. **robots.txt**：发现敏感文件泄露 `/user.php.bak`
3. **备份文件分析**：`user.php.bak` 包含 `UserInfo` 类源码：
   - `getBlogContents()` 方法使用 `curl` 获取 blog URL 内容
   - 存在 SSRF 漏洞点，可利用 `file://` 协议读取本地文件
   - 使用 `unserialize()` 反序列化用户数据

## 漏洞分析（漏洞类型、原理、判断过程）

### 1. SQL 注入
- **入口点**：`view.php?no=1`
- **判断过程**：测试 `no=1 and 1=1` 无响应，尝试 Union 注入
- **WAF 绕过**：直接使用 `union select` 返回 `no hack ~_~`，使用 MySQL 内联注释 `/*!union*//*!select*/` 成功绕过
- **列数判断**：4 列

### 2. PHP 反序列化 + SSRF
- **原理**：用户注册时，`UserInfo` 对象被序列化存入数据库 `data` 列；查看用户时反序列化并调用 `getBlogContents()` 获取博客内容
- **利用方式**：通过 SQL 注入直接注入恶意序列化对象，或利用 `load_file()` 直接读取文件

### 3. 直接文件读取
- **更简单的方法**：MySQL 的 `load_file()` 函数可直接读取服务器文件

## 利用过程（Payload + Flag）

### 方法：SQL 注入 + load_file() 直接读取

**Payload：**
```
view.php?no=-1 /*!union*//*!select*/ 1,load_file('/var/www/html/flag.php'),3,4
```

**步骤：**
1. 访问 `robots.txt` 发现 `/user.php.bak`
2. 分析备份文件发现 SSRF + 反序列化漏洞
3. 测试 `view.php?no=1` 发现 SQL 注入点
4. 使用内联注释绕过 WAF：`/*!union*//*!select*/`
5. 通过报错信息得知 Web 路径 `/var/www/html/`
6. 使用 `load_file('/var/www/html/flag.php')` 读取 flag

**Flag：** `flag{593fd702-4a30-49c6-b1e4-e2a576738255}`

## 复现步骤
1. 访问 `http://target/view.php?no=-1 /*!union*//*!select*/ 1,load_file('/var/www/html/flag.php'),3,4`
2. 在返回的 HTML 中找到 flag

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|--------|
| SQL注入 | view.php?no= | `/*!union*//*!select*/` | MySQL内联注释绕WAF |
| 敏感文件泄露 | robots.txt | /user.php.bak | 信息收集 |
| 文件读取 | SQL注入点 | load_file() | MySQL文件读取函数 |

## 知识总结（解题技巧、同类题型套路）

1. **robots.txt 必看**：CTF 中 robots.txt 常泄露敏感文件路径
2. **备份文件常见后缀**：`.bak`, `.swp`, `.old`, `~` 等
3. **WAF 绕过技巧**：
   - 内联注释 `/*!...*/` 绕过关键字过滤
   - 大小写混合、双写、URL编码等
4. **SQL 注入读取文件**：`load_file()` 是 MySQL 内置函数，可读取服务器本地文件
5. **路径获取**：通过报错信息、phpinfo、常见路径猜测等方式获取 Web 绝对路径
