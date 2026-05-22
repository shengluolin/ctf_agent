#!/usr/bin/env python3
"""
Fast PHP mt_rand seed cracker using php_mt_seed tool approach
"""
import struct

# 已知的前10位字符串
known_str = "tNrC4gANXN"
charset = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# 将已知字符转换为 mt_rand 的输出值
known_indices = [charset.index(c) for c in known_str]
print(f"Known indices: {known_indices}")

# PHP mt_rand(0, 61) 的实现
# mt_rand 使用 Mersenne Twister，输出范围映射

class MT19937:
    """Mersenne Twister 19937 implementation matching PHP's mt_srand/mt_rand"""
    
    def __init__(self, seed):
        self.mt = [0] * 624
        self.mt[0] = seed & 0xffffffff
        for i in range(1, 624):
            self.mt[i] = (0x6c078965 * (self.mt[i-1] ^ (self.mt[i-1] >> 30)) + i) & 0xffffffff
        self.index = 624
    
    def extract_number(self):
        if self.index >= 624:
            self.twist()
        y = self.mt[self.index]
        y ^= (y >> 11)
        y ^= ((y << 7) & 0x9d2c5680)
        y ^= ((y << 15) & 0xefc60000)
        y ^= (y >> 18)
        self.index += 1
        return y & 0xffffffff
    
    def twist(self):
        for i in range(624):
            y = (self.mt[i] & 0x80000000) | (self.mt[(i+1) % 624] & 0x7fffffff)
            self.mt[i] = self.mt[(i + 397) % 624] ^ (y >> 1)
            if y & 1:
                self.mt[i] ^= 0x9908b0df
        self.index = 0

def mt_rand(mt, min_val=0, max_val=61):
    """PHP's mt_rand implementation with range"""
    number = mt.extract_number()
    # PHP's range mapping for mt_rand(min, max)
    # This is how PHP maps 32-bit random to range
    return min_val + (number % (max_val - min_val + 1))

def generate_string(seed):
    """Generate the 20-character string for a given seed."""
    mt = MT19937(seed)
    result = ''
    for i in range(20):
        idx = mt_rand(mt, 0, 61)
        result += charset[idx]
    return result

def crack_seed():
    """Brute force the seed."""
    for seed in range(1000000000):
        generated = generate_string(seed)
        
        if generated[:10] == known_str:
            print(f"\nFound seed: {seed}")
            print(f"Full string: {generated}")
            return seed, generated
        
        if seed % 5000000 == 0:
            print(f"Progress: {seed}")
    
    return None, None

if __name__ == "__main__":
    seed, full_str = crack_seed()
    if full_str:
        print(f"\n=== RESULT ===")
        print(f"Seed: {seed}")
        print(f"Full 20-char string: {full_str}")
