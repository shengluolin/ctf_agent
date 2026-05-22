#!/usr/bin/env python3
# 将已知字符串转换为 php_mt_seed 需要的格式

known = "wAdZ8iEIP0"
charset = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# 找到每个字符在字符集中的位置
for i, c in enumerate(known):
    pos = charset.index(c)
    # mt_rand(0, 61) 产生的值
    # php_mt_seed 格式: mt_rand(min, max) 的输出值
    print(f"{pos} 0 61 {i} {i}")
