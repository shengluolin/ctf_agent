---
name: container-renew
description: Container renewal is handled automatically by the backend. You do NOT need to manage containers yourself.
license: MIT
compatibility: None - this skill is disabled
allowed-tools: []
metadata:
  user-invocable: "false"
---

# Container Management - Automatic

**容器由后台自动管理，你不需要做任何事情。**

## 工作原理

- 后台每 8 分钟自动检查并续期活跃的容器
- 如果容器过期，后台会自动重建并注入新 URL
- 你只需要专注于解题

## 当你看到 "实例无法访问"

**不要尝试续期！** 等待后台注入新 URL，然后继续解题。

后台会在几秒到一分钟后注入新 URL：
```
## ✅ 新容器已就绪

新的 URL: http://xxx.node5.buuoj.cn:81
请立即使用新 URL 继续解题！
```

## 你只需要做的

1. **专注于解题** - 分析漏洞，编写 exploit
2. **等待新 URL** - 如果容器过期，后台会通知你
3. **不要调用任何续期 API 或脚本**
