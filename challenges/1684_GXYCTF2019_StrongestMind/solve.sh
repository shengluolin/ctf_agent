#!/bin/bash

COOKIE_FILE="/tmp/ctf_cookies.txt"
URL="http://0168c74c-dba0-47e7-b3fe-ec2262a377a3.node5.buuoj.cn:81/index.php"

# 清理旧的cookie文件
rm -f $COOKIE_FILE

for i in $(seq 0 1005); do
    # 获取页面
    response=$(curl -s -c $COOKIE_FILE -b $COOKIE_FILE "$URL")
    
    # 检查是否有flag
    flag=$(echo "$response" | grep -oP "flag\{[^}]+\}" 2>/dev/null || true)
    if [ -n "$flag" ]; then
        echo "[+] Found flag at iteration $i!"
        echo "[+] FLAG: $flag"
        break
    fi
    
    # 检查是否被限速
    if echo "$response" | grep -q "429 Too Many Requests"; then
        echo "[!] Rate limited at iteration $i, waiting 5 seconds..."
        sleep 5
        ((i--))
        continue
    fi
    
    # 提取计算表达式 (匹配 数字 运算符 数字)
    expr=$(echo "$response" | grep -oP '\d+ [+*/\-] \d+' | head -1)
    
    if [ -z "$expr" ]; then
        echo "[-] No expression found at iteration $i"
        echo "$response"
        break
    fi
    
    # 计算答案
    answer=$(echo "$expr" | bc)
    
    # 提交答案
    curl -s -c $COOKIE_FILE -b $COOKIE_FILE -X POST -d "answer=$answer" "$URL" > /dev/null
    
    if [ $((i % 50)) -eq 0 ]; then
        echo "[*] Progress: $i/1000"
    fi
    
    # 添加延迟避免限速
    sleep 0.1
done

echo "[*] Final check:"
curl -s -c $COOKIE_FILE -b $COOKIE_FILE "$URL"
