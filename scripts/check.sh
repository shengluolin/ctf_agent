#!/bin/bash
# 检查 CTF Agent 是否还在跑，如果停了就重启
LOG="/home/lls/data/ctf-agent/logs/cron_check.log"
cd /home/lls/data/ctf-agent/scripts

# 检查 run.py 是否在运行
if pgrep -f "run.py --skip-solved" > /dev/null; then
    echo "$(date): CTF Agent 运行中" >> "$LOG"
else
    echo "$(date): CTF Agent 已停止，重启中..." >> "$LOG"
    nohup python3 -u run.py --skip-solved >> /home/lls/data/ctf-agent/logs/nohup.log 2>&1 &
    echo "$(date): 已重启 PID=$!" >> "$LOG"
fi

# 输出当前 WP 数量
WP_COUNT=$(ls /home/lls/data/ctf-agent/wps/*.md 2>/dev/null | wc -l)
echo "$(date): 当前 WP 数量: $WP_COUNT/320" >> "$LOG"
