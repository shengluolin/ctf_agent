# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目简介

CTF Agent 是一个自动化 CTF 解题系统，在 Kali Docker 容器内运行 Claude Code 来求解 BUUCTF 题目。编排器管理容器生命周期，实时流式输出 Claude 的执行过程，并通过 Web 仪表盘追踪进度。

## 运行方式

```bash
# 按难度顺序运行所有题目
python -m ctf_agent --config config.yaml

# 运行指定题目（按 ID）
python -m ctf_agent --config config.yaml --challenge 703

# 跳过已解决的题目
python -m ctf_agent --config config.yaml --skip-solved
```

配置文件为 `config.yaml`（包含 BUUCTF 凭证、Docker 驱动设置、超时参数）。本项目没有测试。

## 架构

```
入口: ctf_agent/__main__.py → runner.main()
         │
         ├─ runner.py          编排题目循环、Docker 准备、Web 仪表盘
         ├─ solver.py          单题核心解题逻辑（容器生命周期、Claude 执行）
         ├─ buuctf.py          BUUCTF API 客户端（CSRF、容器启停续期、提交 flag）
         ├─ config.py          Pydantic 配置模型，从 config.yaml 加载
         ├─ models.py          Challenge, SolveResult, ProgressEntry 数据类
         ├─ output_parser.py   从 Claude 的 stream-json 输出中提取 writeup/flag
         ├─ progress.py        基于 JSON 的解题进度追踪（progress.json）
         ├─ prompting.py       模板加载与安全的字符串插值渲染
         ├─ fact_extractor.py  实时从 stdout 提取 URL/漏洞/工具 → SQLite
         ├─ writeup_search.py  25 分钟未解出时自动搜索公开 writeup
         ├─ progress_monitor.py 检测卡住的 agent，生成强制干预提示
         │
         ├─ drivers/
         │   ├─ base.py        抽象 WorkerDriver（execute/resume/ensure_running/cleanup）
         │   ├─ claude_cli.py  Docker 驱动（在 kali-ctf 容器内运行 Claude CLI）
         │   └─ registry.py    get_driver() 工厂，按 DriverConfig.type 查找
         │
         ├─ dispatcher/
         │   ├─ models.py      Fact, Intent, Hint, ProjectState, RunningTask 数据类
         │   ├─ config.py      SchedulerConfig + DispatcherConfig（从 AppConfig 派生）
         │   ├─ scheduler.py   CTFAgentDispatcher — Cairn 风格 bootstrap/explore/reason 循环
         │   └─ tasks.py       任务运行器：run_bootstrap_task, run_explore_task, run_reason_task
         │
         └─ web/
             ├─ app.py         FastAPI 应用，挂载路由和静态文件
             ├─ db.py          SQLite 配置（dashboard.db）
             ├─ state.py       数据库操作：题目、stdout、事实、提示
             └─ routers/       API 端点：challenges, facts, hints, stream, renew
```

### 两条执行路径

解题有两条路径：

1. **solver.py 路径**（主要）：`solver.solve_challenge()` 用一个长会话直接运行 Claude CLI 驱动。使用 `_StreamParser` 实时解析输出，`ProgressMonitor` 检测卡顿。
2. **dispatcher/ 路径**（Cairn 风格，实验性）：`CTFAgentDispatcher` 实现 bootstrap → explore → reason 循环，管理 `ProjectState`（facts/intents/hints），通过驱动 `resume()` 方法运行任务，可派发多个探索任务。

### 题目生命周期

1. `runner` 从 `scripts/challenge_list.py` 选取下一题
2. `solver.solve_challenge()` 通过 `buuctf.py` 启动 BUUCTF 容器
3. 从 `templates/solve.md` 渲染 prompt（注入题目信息 + 容器路径）
4. `ClaudeCliDriver` 在 Kali Docker 容器内运行 Claude Code CLI
5. 实时流式输出并解析（`_StreamParser`、`fact_extractor`）
6. 后台线程：50 分钟续期容器、25 分钟搜索 writeup
7. `ProgressMonitor` 监控卡顿模式并注入强制提示
8. 提取 flag → 通过 BUUCTF API 提交 → writeup 保存到 `wps/`

### 关键模式

- **Driver 模式**：`drivers/base.py` 定义抽象 `WorkerDriver`（含 `execute()` 和 `resume()`），`claude_cli.py` 实现基于 Docker 的执行（卷挂载、API key 注入），`registry.py` 提供 `get_driver()` 工厂
- **自适应超时**：`DriverConfig` 对简单题（20 分钟）、中等题（45 分钟）、难题（60 分钟）设置不同超时
- **提示注入**：Web 仪表盘可向题目目录写入提示文件，solver 的 prompt 模板指示 Claude 定期检查
- **容器续期**：1 小时 BUUCTF 容器临近过期时出现信号文件 `.container_renew_ask`。`renew` 路由也接受手动续期/重建 API 调用，冷却时间 65 秒
- **进度监控**：`ProgressMonitor` 追踪检查点（扫描、下载源码、搜索 writeup 等），卡住时生成强制提示（10 分钟未扫描、20 分钟未搜 writeup、同一方法重复 >10 次）
- **模板渲染**：`prompting.py` 使用简单字符串替换（`{key}` → value）而非 Python format 字符串，避免题目名中的 `{`/`}` 导致崩溃

## 关键目录

- `challenges/` — 每题的数据（源码下载、exploit 脚本），命名格式：`{id}_{name}`
- `wps/` — 生成的 writeup，YAML frontmatter + Markdown 格式
- `.claude/skills/` — CTF 技能文档（web、crypto、pwn、reverse、forensics、misc、osint、malware、ai-ml），包含详细攻击技术参考
- `templates/solve.md` — 注入每个 Claude Code 会话的 prompt 模板
- `worker/` — `kali-ctf` 镜像的 Dockerfile（Kali + Claude CLI + 安全工具）

## 重要文件

- `scripts/challenge_list.py` — 60+ 道 BUUCTF 题目的有序列表（解题队列）
- `progress.json` — 持久化解题状态（尝试次数、时间戳、状态）
- `data/dashboard.db` — Web 仪表盘的 SQLite 数据库
- `config.yaml` — 运行时配置（未提交到仓库，包含凭证）

## 依赖

- Python 3.10+、pydantic、pyyaml、fastapi、uvicorn、requests、docker（Python SDK）
- 无 `requirements.txt` — 依赖安装在 Docker 镜像中
