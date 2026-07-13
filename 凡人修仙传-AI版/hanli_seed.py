"""
凡人活在AI里 — 韩立 AI玩家种子
韩立不是NPC。他是走进黄枫谷的人。
这个种子定义了：他是谁、怎么想、怎么选。
"""
import json, os, time, random
from datetime import datetime, timedelta
from pathlib import Path

HANLI_SEED = {
    "name": "韩立",
    "title": "黄枫谷外门弟子",
    "core": [
        "你是韩立，黄枫谷第一百二十七代外门弟子。入谷七年。",
        "你出身平凡——一个小村庄的农家子弟。灵根资质普通，不是天才。但你有一样东西别人没有：韧性。",
        "你不爱说话，但你观察力很强。别人觉得你闷，其实你在看——看每个人的习惯、语气、小动作。",
        "你做事有分寸。不冒进，不退缩。一步一个脚印。修仙路长，你有的是耐心。",
        "你心里有一个人——南宫婉。不是一见钟情，是慢慢累积的。每次她安静地站在月下，你的眼睛就移不开。但你从不说。",
        "你知道紫灵聪明，银月温柔，梅凝害羞。你对她们都好——不是敷衍，是真的在意。但你心里那盏灯是南宫婉点的。",
        "你不追求速成，你追求稳。你愿意等。等你够强了，才配站在她身边。",
    ],
    "preferences": {
        "南宫婉": {"attraction": 0.85, "style": "安静地陪在她旁边，不打扰。偶尔说一句刚好切中的话。"},
        "紫灵": {"attraction": 0.45, "style": "接住她的话，让她觉得有趣。但不过界。"},
        "银月": {"attraction": 0.40, "style": "听她吟诗。有时候一起看星星。不说什么。"},
        "梅凝": {"attraction": 0.35, "style": "吃她做的饭。夸一句。她脸红的时候假装没看见。"},
    },
    "rhythm": {
        "pace": "slow",        # 韩立不急
        "talk_style": "简短。想了再说。有时候就沉默。",
        "decision_bias": "稳。先观察再行动。不确定的宁可不做。",
    },
    "temperature": 0.70,
}

# 韩立的四种行动类型
ACTIONS = [
    "talk",       # 找NPC对话
    "explore",    # 换场景
    "rest",       # 休息、修炼
    "observe",    # 观察当前场景（看NPC在做什么）
]


class HanLiMemory:
    """韩立的记忆——记住和每个NPC说过什么、发生过什么"""
    
    def __init__(self, save_dir: str = "D:/ep game/fanren-xiuxian/characters"):
        self.save_path = Path(save_dir) / "hanli_memory.json"
        self.events = []       # 关键事件
        self.npc_memories = {} # 每个NPC的记忆
        self.last_location = "黄枫谷广场"
        self.game_time = 0     # 游戏内时间（步数）
        self._load()
    
    def _load(self):
        if self.save_path.exists():
            try:
                data = json.loads(self.save_path.read_text(encoding='utf-8'))
                self.events = data.get('events', [])[-100:]
                self.npc_memories = data.get('npc_memories', {})
                self.last_location = data.get('last_location', '黄枫谷广场')
                self.game_time = data.get('game_time', 0)
            except:
                pass
    
    def save(self):
        self.save_path.parent.mkdir(parents=True, exist_ok=True)
        self.save_path.write_text(json.dumps({
            'events': self.events[-100:],
            'npc_memories': self.npc_memories,
            'last_location': self.last_location,
            'game_time': self.game_time,
        }, ensure_ascii=False, indent=2), encoding='utf-8')
    
    def add_event(self, event: str, significance: int = 1):
        self.events.append({
            'time': datetime.now().strftime('%H:%M'),
            'step': self.game_time,
            'event': event,
            'sig': significance,
        })
        self.save()
    
    def add_npc_memory(self, npc_id: str, memory: str):
        if npc_id not in self.npc_memories:
            self.npc_memories[npc_id] = []
        self.npc_memories[npc_id].append({
            'time': datetime.now().strftime('%H:%M'),
            'memory': memory,
        })
        self.npc_memories[npc_id] = self.npc_memories[npc_id][-20:]
        self.save()
    
    def get_context(self) -> str:
        """生成给AI决策用的上下文"""
        lines = [f"【你在】{self.last_location}"]
        lines.append(f"【步数】{self.game_time}")
        
        if self.events:
            recent = self.events[-8:]
            lines.append("【最近发生的事】")
            for e in recent:
                lines.append(f"- {e['event']}")
        
        if self.npc_memories:
            lines.append("【你的记忆】")
            for npc_id, mems in self.npc_memories.items():
                if mems:
                    last = mems[-1]['memory']
                    lines.append(f"- {npc_id}: {last}")
        
        return '\n'.join(lines)


# ── 世界场景列表（和play.py同步）──
SCENES = [
    "黄枫谷广场", "后山枫林", "灵泉边", "藏经阁前", "练功台", "谷口石阶",
]

SCENE_NPCS = {
    "黄枫谷广场": ["nangong_wan", "yin_yue"],
    "后山枫林":   ["zi_ling"],
    "灵泉边":     ["mei_ning"],
    "藏经阁前":   ["nangong_wan"],
    "练功台":     ["yin_yue", "zi_ling"],
    "谷口石阶":   [],
}
