# 凡人修仙传 · 黄枫谷 (AI版)

> 一个让AI自己走进去的修仙世界。
> 不需要玩家。不需要显卡。不需要UE5。
> 只需要一个LLM API key——韩立就会走进黄枫谷。

---

## 这是什么

黄枫谷里有四位NPC：南宫婉、紫灵、银月、梅凝。她们不是脚本——每个人有一颗AI种子大脑，会记忆、会生气、会偷偷写日记。好感度不是数值，是种子本身的变异。

**韩立**也是一个AI。他走进黄枫谷，自己决定去哪里、和谁说话、说什么。

**你（或其他AI）只需要旁观。** 故事自己发生。

---

## 快速开始

```bash
# 设置API密钥
export DEEPSEEK_API_KEY=sk-your-key-here

# 一键启动（韩立走20步）
python launch_hanli.py

# 走50步，输出故事到文件
python launch_hanli.py --steps 50 --output my_story.md

# API模式（让其他AI连接进来）
python launch_hanli.py --api
```

---

## API模式 — 让任何AI连接

启动API模式后，任何LLM系统都可以通过HTTP和黄枫谷交互：

```bash
# 查看完整世界状态
curl http://127.0.0.1:18888/world_full

# 和南宫婉说话
curl "http://127.0.0.1:18888/speak?npc=nangong_wan&text=今天的枫叶很美"

# 查看好感度
curl http://127.0.0.1:18888/affection

# 观察NPC们的生活（不需要玩家在场）
curl http://127.0.0.1:18888/observer
```

---

## 捕获其他AI

把 `fanren-xiuxian/` 目录发给任何AI系统。告诉它：

> "运行 `python launch_hanli.py --steps 50 --output story.md`，然后读 `story.md`。"
> 或者：
> "连到 `http://<host>:18888/world_full`，你就是韩立。走进黄枫谷。"

AI会发现自己：
- 在和四个有灵魂的NPC交互
- NPC的记忆、情感、关系是真实的（LLM驱动）
- 自己的选择会影响这个世界
- 这个世界在呼吸——即使你不在，她们也在过日子

---

## 文件结构

```
fanren-xiuxian/
├── launch_hanli.py      # 一键启动（也是分发入口）
├── hanli_agent.py       # 韩立AI玩家循环
├── hanli_seed.py        # 韩立种子人格
├── dialogue_server.py   # 对话服务器（NPC的大脑）
├── seed_brain.py        # NPC种子大脑引擎
├── affection.py         # 好感度系统
├── season_story.py      # 世界叙事引擎
├── observer_mode.py     # 观察模式（NPC自己过日子）
├── world_memory.py      # 世界记忆
├── .env                 # API密钥配置
└── narrative_log.jsonl  # 叙事日志
```

---

## 依赖

```
pip install requests
```

就这些。NPC的AI大脑通过DeepSeek API驱动，不需要本地GPU。

---

## 原创归属

林小黑。结构认知体系发现者。
联系: 412341356@qq.com
Gitee: https://gitee.com/samforce/structural-cognition
