---
name: txj-tiered-memory
version: 0.1.0
description: Use when starting a new session and the assistant needs to recall who the user is and where work left off. Tiered progressive memory recovery — always read the core layer, check an auto-generated change index before re-reading secondary files, defer the rest until needed. Cuts recovery token cost ~70% versus reading everything every session.
author: TXJ
license: MIT
metadata:
  hermes:
    tags: [memory, recovery, session, onboarding]
    related_skills: []
---

# TXJ Tiered Memory (三层渐进记忆恢复)

> 让 AI 助手跨会话不失忆,恢复成本直降 ~70%。
> 每次新会话都要从头"认识"一遍?本技能用三层渐进法恢复记忆——**只读真正重要的,跳过没变的,用到才查细节**。

## What this does

| Layer | 读什么 | 何时读 |
|---|---|---|
| **L3 必读** | 身份/合作规则/用户档案/最新待办/最新工作日志 | 每次新会话,缺一不可(可靠性的锚) |
| **L2 条件读** | 次级档案(角色定义/成员配置/扩展档案) | 先看**自动生成的变更索引**,标"有新变更"才读全文,没变只读索引摘要行 |
| **L1 按需** | 细节文档(技术清单/历史日志) | 用到才查,不用不读 |

配套机制:**变更索引自动生成脚本**(纯本地,零 API 成本,哈希幂等)——它让 L2 层"先看摘要再决定读不读全文"成为可能,这就是省 ~70% token 的机关。

## Setup

1. 把 `config.example.yaml` 复制为 `config.yaml`,填三处:
   - `memory_root`:您的记忆文件根目录
   - `must_read`:每次会话必读的文件清单(L3)
   - `tracked_files`:需要变更检测的文件清单(L2,每项= 路径/显示名/一句话说明)
2. 生成变更索引(可加定时任务,如每天一次):
   ```bash
   python scripts/memory_index.py --config config.yaml
   ```
   生成 `memory_index.md` + 状态文件(记住上次哈希)。
3. 按您的记忆文件调整——必读清单在 `config.yaml` 的 `must_read` 填,变更检测清单在 `tracked_files` 填;恢复流程见下方 Usage。

## Usage(每次新会话开头)

1. **读 L3 必读清单**(您在 config 里指定的核心文件)——一个不落。
2. **读变更索引** `memory_index.md`(脚本已生成):
   - 标 ✅ 新变更 → 读该文件全文
   - 标 ⏸ 未变更 → 只读摘要行,不读全文 ← **省钱在这里**
3. **按需层**:之后任务碰到才查(如装机前查技术清单)。
4. 汇报恢复结果(身份✅/变更✅/待办 N 条)——让用户确认恢复已执行。

## Files

- `scripts/memory_index.py` — 变更索引生成(纯标准库,零依赖;首次跑全标新变更,之后哈希没变就标未变更;24h 内改过的文件也标新变更)
- `config.example.yaml` — 配置模板
- 输出:`memory_index.md`(人读)+ `memory_index_state.json`(脚本状态,勿手改)

## Security

- 只读您在 config 里指定的记忆目录;不写记忆文件本体(只写索引和状态文件)
- 不上传任何数据到外网,纯本地运行
- 无远程管道安装、无脚本直灌执行;只读您在 config 里指定的记忆文件
- 数据全在您自己的电脑上

## Roadmap(托管版提供)

- 用户画像自动沉淀(偏好/习惯学习)
- 跨设备同步与 Web 管理台
- 一键部署(不想自己配环境?→ 官方托管版:开箱即用,持续更新)

> 不想折腾配置?免费版 = 自己动手的最小闭环;托管版 = 开箱即用 + 完整体系 + 持续更新。→ [托管版入口]
