#!/usr/bin/env python3
import random

known = "wAdZ8iEIP0"
charset = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def mt_rand(seed, min_val, max_val):
    random.seed(seed)
    return random.randint(min_val, max_val)

# PHP 的 mt_rand 使用 Mersenne Twister，Python 的 random 也用这个
# 但 PHP 和 Python 的实现可能不同，需要用 PHP 来验证

# 先用 Python 尝试
for seed in range(1000000000):
    random.seed(seed)
    generated = ""
    for i in range(10):
        generated += charset[random.randint(0, 61)]
    if generated == known:
        print(f"Found seed: {seed}")
        # 生成完整字符串
        random.seed(seed)
        full_str = ""
        for i in range(20):
            full_str += charset[random.randint(0, 61)]
        print(f"Full string: {full_str}")
        break
    if seed % 10000000 == 0:
        print(f"Progress: {seed}")
