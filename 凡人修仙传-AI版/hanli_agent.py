"""
凡人活在AI里 — 韩立 AI玩家循环
感知→决策→行动→观察
韩立不是一个NPC，他走进黄枫谷，自己决定去哪里、和谁说话、说什么。
"""
import json, os, sys, time, random, urllib.request, urllib.parse
from dataclasses import dataclass
from typing import Optional, Dict

SERVER = "http://127.0.0.1:18888"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hanli_seed import HANLI_SEED, ACTIONS, SCENES, SCENE_NPCS, HanLiMemory


def call_llm(system_prompt: str, user_message: str, temperature: float = 0.70) -> str:
    """调用LLM"""
    # 加载.env（确保在子进程中也能读到key）
    _env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(_env_path):
        for _line in open(_env_path, encoding='utf-8').read().strip().split('\n'):
            _line = _line.strip()
            if _line and not _line.startswith('#') and '=' in _line:
                _key, _val = _line.split('=', 1)
                _key, _val = _key.strip(), _val.strip()
                if _key not in os.environ:
                    os.environ[_key] = _val
    
    api_key = os.environ.get('LLM_API_KEY', os.environ.get('DEEPSEEK_API_KEY', ''))
    base_url = os.environ.get('LLM_BASE_URL', 'https://api.deepseek.com/v1')
    model = os.environ.get('LLM_MODEL', 'deepseek-chat')
    
    if not api_key:
        return "……"  # 没有钥匙，韩立沉默
    
    import requests
    proxy_url = os.environ.get('https_proxy') or os.environ.get('HTTPS_PROXY') or ''
    proxies = {'https': proxy_url, 'http': proxy_url.replace('https', 'http')} if proxy_url else None
    
    try:
        resp = requests.post(f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": model, "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ], "temperature": temperature, "max_tokens": 150},
            timeout=15, proxies=proxies)
        if resp.status_code == 200:
            return resp.json()['choices'][0]['message']['content'].strip()
        return "……"
    except Exception as e:
        print(f"  ⚠️ LLM调用失败: {e}")
        return "……"


def api_get(endpoint: str, params: dict = None) -> Optional[dict]:
    try:
        url = f"{SERVER}{endpoint}"
        if params:
            url += "?" + urllib.parse.urlencode(params)
        resp = urllib.request.urlopen(url, timeout=15)
        return json.loads(resp.read())
    except:
        return None


def api_post(endpoint: str, data: dict) -> Optional[dict]:
    try:
        body = json.dumps(data).encode()
        req = urllib.request.Request(f"{SERVER}{endpoint}", data=body,
            headers={"Content-Type": "application/json"})
        return json.loads(urllib.request.urlopen(req, timeout=15).read())
    except:
        return None


class HanLiAgent:
    """韩立——AI玩家。他自己决定去哪里、和谁说话、说什么。"""
    
    def __init__(self):
        self.memory = HanLiMemory()
        self.history = []  # 最近几轮对话/行动
    
    def perceive(self) -> dict:
        """感知当前世界状态——使用 /world_full 完整端点"""
        state = {
            "location": self.memory.last_location,
            "step": self.memory.game_time,
            "npc_ids_here": SCENE_NPCS.get(self.memory.last_location, []),
        }
        
        # 获取完整世界状态（包含NPC状态、好感度、关系、事件等）
        world = api_get("/world_full")
        if world:
            state["weather"] = world.get("weather", "")
            state["season"] = world.get("season", "")
            state["time_of_day"] = world.get("time_of_day", "")
            state["theme"] = world.get("theme", "")
            state["recent_events"] = world.get("recent_events", [])[-5:]
            state["world_events"] = world.get("world_events", [])[-3:]
            
            # 好感度
            aff = world.get("affection", {})
            state["affection"] = {
                npc_id: {"name": info["name"], "value": info["value"], "level": info["level"]}
                for npc_id, info in aff.items()
            }
            
            # NPC当前状态
            npcs_state = world.get("npcs", {})
            state["npcs_doing"] = {
                npc_id: f"{info.get('name', npc_id)}在{info.get('location', '附近')}{info.get('activity', '')}"
                for npc_id, info in npcs_state.items()
                if npc_id in state["npc_ids_here"]
            }
            
            # 时间状态
            ts = world.get("time_status", {})
            if ts.get("frozen_since"):
                state["time_frozen"] = True
                state["absence"] = ts.get("absence_message", "")
        
        # 如果在场NPC为空但是好感度里有南宫婉，标记一下
        npc_names = {
            "nangong_wan": "南宫婉",
            "zi_ling": "紫灵",
            "yin_yue": "银月",
            "mei_ning": "梅凝",
        }
        state["npc_names"] = [npc_names.get(nid, nid) for nid in state["npc_ids_here"]]
        
        return state
    
    def _build_decision_prompt(self, state: dict) -> str:
        """构建决策提示词"""
        npcs_here = state.get("npc_names", [])
        core = '\n'.join(HANLI_SEED['core'])
        rhythm = HANLI_SEED['rhythm']
        
        # NPC偏好
        pref_lines = []
        for npc, pref in HANLI_SEED['preferences'].items():
            pref_lines.append(f"- {npc}: 吸引力{pref['attraction']}, 方式={pref['style']}")
        
        return f"""【你是谁】
{core}

【你对NPC的感觉】
{chr(10).join(pref_lines)}

【你的节奏】
- 步伐: {rhythm['pace']}
- 说话方式: {rhythm['talk_style']}
- 决策倾向: {rhythm['decision_bias']}

{self.memory.get_context()}

【现在】
你在{state.get('location', '黄枫谷')}。
在场的人: {', '.join(npcs_here) if npcs_here else '没有人'}
天气: {state.get('weather', '未知')}
时段: {state.get('time_of_day', '未知')}

【可选行动】
1. talk <NPC名字> — 走过去和某人说话
2. explore — 换个地方走走
3. rest — 坐下修炼、休息一会儿
4. observe — 安静地观察周围（看NPC们在做什么）

【规则】
- 你就是韩立，活在黄枫谷里。
- 你心里有南宫婉。如果她在场，你应该偶尔走过去和她说句话——哪怕只是一句。
- 你已经看了好几眼了。看够了就该动。不要一直站在原地。
- 如果连续3次以上都在观察，就说明你该行动了。
- 不是每次都选observe。大多数时候你应该去和某人说话，或者换个地方。
【回复格式（必须严格遵守）】
第一行：你想做什么（10字以内）
第二行：action: <动作> <对象>
动作: talk 南宫婉 / talk 紫灵 / talk 银月 / talk 梅凝 / explore / rest / observe
例如：
走过去看看南宫婉。
action: talk 南宫婉
"""
    def decide(self, state: dict) -> dict:
        """韩立决定下一步做什么"""
        prompt = self._build_decision_prompt(state)
        reply = call_llm(prompt, "你此刻想做什么？", HANLI_SEED['temperature'] * 0.9)
        
        # 解析回复
        lines = reply.strip().split('\n')
        thought = ''
        action = 'observe'
        target = None
        
        for line in lines:
            line = line.strip()
            if line.lower().startswith('action:'):
                action_part = line.split(':', 1)[1].strip()
                parts = action_part.split(None, 1)
                action = parts[0].lower()
                if len(parts) > 1:
                    target = parts[1]
            elif not line.startswith('action:'):
                thought = line
        
        if not thought:
            thought = reply[:80]
        
        return {
            "thought": thought,
            "action": action,
            "target": target,
        }
    
    def act(self, decision: dict, state: dict) -> str:
        """执行行动，返回结果描述"""
        action = decision['action']
        target = decision.get('target', '')
        
        if action == 'explore':
            # 换场景：优先去有南宫婉的地方，其次随机
            if 'nangong_wan' in SCENE_NPCS.get(self.memory.last_location, []) and random.random() > 0.5:
                pass  # 南宫婉在场，不走
            else:
                # 偏好：有南宫婉的场景
                wan_scenes = [s for s, npcs in SCENE_NPCS.items() if 'nangong_wan' in npcs]
                if random.random() < HANLI_SEED['preferences']['南宫婉']['attraction'] and wan_scenes:
                    new_scene = random.choice(wan_scenes)
                else:
                    other = [s for s in SCENES if s != self.memory.last_location]
                    new_scene = random.choice(other) if other else self.memory.last_location
                
                self.memory.last_location = new_scene
                self.memory.game_time += 1
                self.memory.add_event(f"走到了{new_scene}")
                return f"你走到了{new_scene}。"
        
        elif action == 'talk':
            # 找到目标NPC
            npc_map = {"南宫婉": "nangong_wan", "紫灵": "zi_ling", "银月": "yin_yue", "梅凝": "mei_ning"}
            npc_id = npc_map.get(target)
            if not npc_id:
                # 从在场NPC中选
                here = state.get('npc_ids_here', [])
                preferred = [n for n in here if n == 'nangong_wan']
                if preferred:
                    npc_id = 'nangong_wan'
                elif here:
                    npc_id = random.choice(here)
            
            if npc_id:
                return self._talk_to_npc(npc_id, target or npc_id)
            else:
                self.memory.game_time += 1
                return "附近没有人可以说话。"
        
        elif action == 'rest':
            self.memory.game_time += 3
            self.memory.add_event("在古枫下盘膝修炼了一会儿")
            return "你在古枫下闭目调息。内息运转了一个小周天。"
        
        else:  # observe
            self.memory.game_time += 0.5
            return self._observe(state)
    
    def _talk_to_npc(self, npc_id: str, npc_name: str) -> str:
        """和NPC对话"""
        # 韩立想说什么
        preference = HANLI_SEED['preferences'].get(npc_id, {})
        style = preference.get('style', '简短地问候')
        
        talk_prompt = f"""你是韩立。你要和{npc_name}说话。
你的方式: {style}
根据你的记忆和性格，你想对TA说什么？
回复一句话，不超过30个字。"""
        
        message = call_llm(talk_prompt, "你想说什么？", 0.75)
        
        # 发送到对话服务器
        resp = api_get("/speak", {"npc": npc_id, "text": message})
        
        if resp:
            npc_reply = resp.get('text', '……')
            aff = resp.get('affection', {})
            delta = aff.get('delta', 0)
            
            self.memory.add_npc_memory(npc_id, f"我对{npc_name}说了「{message}」，TA说「{npc_reply[:40]}」")
            self.memory.add_event(f"和{npc_name}聊了一会儿", significance=3)
            self.memory.game_time += 2
            
            return f"你对{npc_name}说：「{message}」\n{npc_name}：「{npc_reply}」"
        
        return f"你走向{npc_name}，但TA没有回应。"
    
    def _observe(self, state: dict) -> str:
        """观察周围"""
        npcs_here = state.get('npc_names', [])
        if npcs_here:
            return f"你站在{state.get('location', '黄枫谷')}，看着{', '.join(npcs_here)}。"
        return f"你站在{state.get('location', '黄枫谷')}，周围很安静。"
    
    def run_step(self) -> dict:
        """运行一步：感知→决策→行动"""
        state = self.perceive()
        decision = self.decide(state)
        result = self.act(decision, state)
        
        return {
            "step": self.memory.game_time,
            "location": self.memory.last_location,
            "thought": decision['thought'],
            "action": decision['action'],
            "result": result,
        }
    
    def run(self, steps: int = 20, delay: float = 1.0, verbose: bool = True):
        """自动运行N步"""
        try:
            # 检查服务器是否活着
            if not api_get("/ambient"):
                print("❌ 对话服务器未启动。请先运行: python dialogue_server.py")
                return
            
            print(f"🌸 韩立走进了黄枫谷。\n")
            
            for i in range(steps):
                step = self.run_step()
                
                if verbose:
                    print(f"📍 第{step['step']:.0f}步 | {step['location']}")
                    if step['thought']:
                        print(f"💭 {step['thought']}")
                    print(f"🎬 {step['result']}")
                    print()
                
                if delay:
                    time.sleep(delay)
            
            print(f"🌙 韩立收功。在黄枫谷走了{steps}步。")
        except KeyboardInterrupt:
            print("\n🌙 韩立转身离开了黄枫谷。")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="韩立AI玩家 — 走进黄枫谷")
    parser.add_argument("--steps", type=int, default=20, help="运行步数")
    parser.add_argument("--delay", type=float, default=2.0, help="每步间隔秒数")
    parser.add_argument("--quiet", action="store_true", help="静默模式")
    args = parser.parse_args()
    
    agent = HanLiAgent()
    agent.run(steps=args.steps, delay=args.delay, verbose=not args.quiet)


if __name__ == "__main__":
    main()
