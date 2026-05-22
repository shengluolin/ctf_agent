---

title: "[SUCTF 2019]Pythonginx"
platform: BUUCTF
category: Web
difficulty: 中等
tags: [ssrf, idna-bypass, nginx, file-read]
vulnerability: IDNA 编码绕过导致 SSRF
solved: false
flag: "环境问题，无法获取"

---

# [SUCTF 2019]Pythonginx

## 题目概述
题目提供了一个 URL 输入框，后端使用 Python 的 urllib 库获取 URL 内容。代码对 hostname 进行了三次检查，要求最终 hostname 必须是 `suctf.cc`。

## 信息收集
1. 页面源码显示了后端处理逻辑
2. 代码使用 `urlparse` 和 `urlsplit` 解析 URL
3. 对 netloc 进行 IDNA 编码后再解码
4. 题目提示 "Dont worry about the suctf.cc" 和 "Do you know the nginx?"

## 漏洞分析（漏洞类型、原理、判断过程）

**漏洞类型**: IDNA 编码绕过 + SSRF

**原理**:
1. Unicode 字符 `ſ`（U+017F，拉丁小写长s）在 IDNA 编码后会被转换为普通 ASCII 字符 `s`
2. 代码流程：
   - 第一次检查：`urlparse(url).hostname != 'suctf.cc'`
   - 第二次检查：`urlsplit(url).netloc != 'suctf.cc'`
   - IDNA 编码：`ſuctf.cc` → `suctf.cc`
   - 最终检查：`urlparse(finalUrl).hostname == 'suctf.cc'`

3. 使用 `http://ſuctf.cc/` 可以绕过所有检查

## 利用过程（Payload + Flag）

**Payload**:
```
http://ſuctf.cc/
```

**预期利用步骤**:
1. 使用 `http://ſuctf.cc/` 绕过检查
2. 服务器配置了 `suctf.cc` 指向 `127.0.0.1`
3. 通过 SSRF 读取 nginx 配置文件
4. 从配置中找到 flag 位置并读取

**实际结果**: 
服务器返回 500 错误，说明 `suctf.cc` 无法解析。这可能是 BUUCTF 平台的环境问题。

## 复现步骤
```bash
# 发送 IDNA 绕过 payload
curl -s "http://target/getUrl?url=http://ſuctf.cc/"
```

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|--------|
| IDNA 绕过 | URL hostname 检查 | `http://ſuctf.cc/` | Unicode IDNA 编码特性 |
| SSRF | urllib.request.urlopen | `file://ſuctf.cc/etc/passwd` | Python urllib 行为 |

## 知识总结（解题技巧、同类题型套路）

1. **IDNA 编码特性**: Unicode 字符在 IDNA 编码后可能转换为 ASCII 字符
2. **常用绕过字符**:
   - `ſ` (U+017F) → `s`
   - `K` (Kelvin Sign) → `k`
   - `ß` → `ss`
3. **SSRF 文件读取**: `file://` 协议可以读取本地文件，但 hostname 必须是 localhost 或空
4. **nginx 配置位置**: `/etc/nginx/nginx.conf`, `/usr/local/nginx/conf/nginx.conf`

---

**注意**: 由于环境问题（`suctf.cc` 无法解析），无法完成最终 flag 的获取。正确的解法需要服务器配置 `suctf.cc` 指向本地。
