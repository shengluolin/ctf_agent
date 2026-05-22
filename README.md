# CTF Agent - Claude Code 自动解题

## 结构

```
ctf-agent/
├── challenges/          # 每道题的下载数据
│   ├── 703_Havefun/
│   ├── 700_EasySQL/
│   └── ...
├── wps/                 # Writeup 文件
│   ├── 703_Havefun.md
│   └── ...
├── scripts/
│   ├── run.py           # 主脚本
│   └── buuctf.py        # BUUCTF API 辅助
└── logs/                # Claude Code 日志
```

## 使用

```bash
# 跑全部
python3 scripts/run.py

# 只跑一道
python3 scripts/run.py 703

# 跳过已有WP
python3 scripts/run.py --skip-solved
```

## 流程

1. 启动 BUUCTF 容器 → 拿到 URL
2. Claude Code 自己 curl 页面、分析源码、找漏洞
3. 找到 flag → 提交
4. 成功 → 写 WP 到 wps/
5. 销毁容器
