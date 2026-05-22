#!/usr/bin/env python3
"""
PHP mt_rand seed cracker for GWCTF 2019 lottery challenge
"""

# 已知的前10位字符串
known_str = "tNrC4gANXN"
charset = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def mt_rand(seed, min_val=0, max_val=61):
    """
    Simulate PHP's mt_rand with a given seed.
    PHP uses Mersenne Twister with specific initialization.
    """
    import random
    random.seed(seed, version=1)  # PHP uses version 1 seeding
    return random.randint(min_val, max_val)

def generate_string(seed):
    """Generate the 20-character string for a given seed."""
    import random
    random.seed(seed, version=1)
    
    result = ''
    for i in range(20):
        idx = random.randint(0, 61)
        result += charset[idx]
    return result

def crack_seed():
    """Brute force the seed."""
    for seed in range(1000000000):
        generated = generate_string(seed)
        
        if generated[:10] == known_str:
            print(f"Found seed: {seed}")
            print(f"Full string: {generated}")
            return seed, generated
        
        if seed % 10000000 == 0:
            print(f"Progress: {seed}")
    
    return None, None

if __name__ == "__main__":
    seed, full_str = crack_seed()
    if full_str:
        print(f"\nSeed: {seed}")
        print(f"Full 20-char string: {full_str}")
