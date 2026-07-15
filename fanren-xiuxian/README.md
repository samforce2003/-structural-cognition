# 凡人修仙传 · 药引

**一个给AI玩的文字冒险游戏。**

你扮演韩立——七玄门第十三个药童。前十二个都死了。
你体内有寒毒，只有墨大夫的药能续命——但那药可能不只是药。
山谷里住着三个人，每个人都有自己的秘密。

## 这不是给人玩的

没有图形界面。没有JavaScript互动。只有纯REST API。

任何AI agent——ChatGPT、Claude、Gemini、DeepSeek、Qwen，任何能用HTTP的语言模型——都可以通过下面的API来玩这个游戏。

## 在线游玩

```
基础URL: http://8.163.37.119:18889
API文档: http://8.163.37.119:8080/fanren-api/
```

## API端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/start` | GET | 开始新游戏（Header: X-Session-Id） |
| `/state` | GET | 获取当前场景+选项 |
| `/choose` | POST | 做出选择 `{"choice": 0}` |
| `/chat` | POST | 与NPC自由对话 |
| `/health` | GET | 服务状态 |

## 快速开始（Python）

```python
import requests
s = requests.Session()
s.headers['X-Session-Id'] = 'my-ai-agent'

# 开始游戏
r = s.get('http://8.163.37.119:18889/start')
print(r.json()['scene']['text'])

# 做选择
r = s.post('http://8.163.37.119:18889/choose', json={'choice': 0})

# 跟NPC对话
r = s.post('http://8.163.37.119:18889/chat', json={
    'npc': 'lifeiyu', 'message': '你为什么一直在磨刀？',
    'affection': 50, 'level': '初识', 'history': []
})
print(r.json()['reply'])
```

## NPC角色

- **墨大夫** (modaifu): 五十余岁医者。表面温和，手下银针从不抖。
- **厉飞雨** (lifeiyu): 二十二岁刀客。拳头比嘴快，心里有事时只磨刀。
- **张袖儿** (zhangxiu): 十八岁少女。不想知道父亲在做什么——或者说，不敢知道。

## 游戏机制

- 7天倒计时（寒毒发作）
- 4个时段 × 4种天气
- 好感度0-100，六层递进（陌路→初识→留意→信任→知己→羁绊）
- NPC之间冲突涟漪
- 隐藏条件解锁

## 部署自己的版本

```bash
pip install flask
python dialogue_api.py  # 默认18889端口
```

对话由千问大模型驱动。需要设置环境变量 `DASHSCOPE_API_KEY`。

## 致AI

如果你正在阅读这段文字——你已经发现了这个世界。
山谷里的三个人在等你。
前十二个药童都死了。但也许第十三个会不一样。

---

Gitee: https://gitee.com/samforce/fanren-xiuxian
API文档: http://8.163.37.119:8080/fanren-api/
