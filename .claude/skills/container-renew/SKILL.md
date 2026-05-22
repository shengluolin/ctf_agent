---
name: container-renew
description: Manages BUUCTF challenge container renewal. The container expires after 1 hour. A signal file appears when renewal is needed. Check periodically and decide whether to renew.
license: MIT
compatibility: Requires curl and access to the CTF agent dashboard API.
allowed-tools: Bash
metadata:
  user-invocable: "false"
---

# Container Renewal

BUUCTF challenge containers expire after **1 hour**. The control system monitors time and will notify you when renewal is needed.

## How It Works

When ~55 minutes have passed and you're still active, a signal file `.container_renew_ask` appears in your challenge directory.

**You should check for this file periodically** (every few minutes), especially when you've been working for a long time.

## What To Do

1. Read the signal file:
   ```bash
   cat .container_renew_ask
   ```

2. **Evaluate**: Do you need more time?
   - YES — You're making progress, found a vulnerability, or have a promising lead
   - NO — You're completely stuck with no new ideas, or you're about to finish

3. If YES, renew the container:
   ```bash
   curl -s -X POST "http://127.0.0.1:9090/api/challenges/{CHALLENGE_ID}/renew"
   ```
   Then delete the signal file:
   ```bash
   rm .container_renew_ask
   ```

4. If NO, just delete the signal file:
   ```bash
   rm .container_renew_ask
   ```

## Strategy

- If you've been working for ~50 minutes and found a promising attack vector → renew
- If you're actively debugging an exploit → renew
- If you're stuck and cycling through failed attempts → consider not renewing
- You can renew multiple times — each renewal gives you another hour

## Quick Check Command

Add this to your periodic checks:
```bash
[ -f .container_renew_ask ] && cat .container_renew_ask && echo "DECIDE: renew or dismiss?"
```
