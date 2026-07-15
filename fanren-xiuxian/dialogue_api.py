"""
凡人修仙传·网页版 对话API服务器 v3
——千问大脑，游戏独享，零纠缠
v3: AI版端点(/state, /choose, /start) + 结构学水印
v2: 对话深度·动作沉默·世界落盘·天气入体
"""
import json, os, sys, time, random as _random
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import urllib.request

# 加载游戏引擎
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from game_engine import GameState, PERIODS, WEATHERS, NPCS, AFF_LV

# 绕过代理 — dashscope走直连
proxy_handler = urllib.request.ProxyHandler({})
opener = urllib.request.build_opener(proxy_handler)
urllib.request.install_opener(opener)

PORT = 18889
# 千问API — 游戏独享
API_KEY = "sk-93a72f117f3f422fb09e05765d23a393"
API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
API_MODEL = "qwen-plus"

# ==================== 玩家监控 ====================
PLAYER_LOG_FILE = Path(os.path.dirname(os.path.abspath(__file__))) / "player_log.json"
PLAYER_LOG = {}
# 启动时加载已有日志
if PLAYER_LOG_FILE.exists():
    try:
        with open(PLAYER_LOG_FILE, 'r', encoding='utf-8') as f:
            PLAYER_LOG = json.load(f)
        print(f"[监控] 加载玩家日志: {len(PLAYER_LOG)} 个历史玩家")
    except:
        pass

# ==================== 世界状态 ====================
STATE_FILE = Path(os.path.dirname(os.path.abspath(__file__))) / "world_state.json"

WEATHERS = [
    "晴，阳光透过树叶洒在地上",
    "阴沉，乌云压得很低，似要下雨",
    "细雨绵绵，打在瓦上沙沙作响",
    "大雨滂沱，雷声隐隐",
    "傍晚，天边一片血红",
    "深夜，万籁俱寂，只有虫鸣",
    "雾很大，三丈之外就看不清了",
]

# 天气→身体效应（NPC行为模式开关）
WEATHER_BODY = {
    "晴，阳光透过树叶洒在地上": {
        "modaifu": "关节松快，心情平和，今天的试探会温和些",
        "lifeiyu": "阳光照在刀面上晃眼——他今天比平时多话",
        "zhangxiu": "打开窗户，让阳光晒进药庐。哼着小调",
    },
    "阴沉，乌云压得很低，似要下雨": {
        "modaifu": "老寒腿隐隐作痛，比平时更阴沉、更不耐烦",
        "lifeiyu": "天闷，胸口也闷。磨刀的力道比平时重",
        "zhangxiu": "提前收衣服、关窗户。话变少了些",
    },
    "细雨绵绵，打在瓦上沙沙作响": {
        "modaifu": "关节酸胀，坐在炉边不动。今天不想说话",
        "lifeiyu": "雨声让他想起妹妹咳血的声音。沉默寡言",
        "zhangxiu": "坐在窗边听雨，出神。问她什么她都慢半拍",
    },
    "大雨滂沱，雷声隐隐": {
        "modaifu": "腿疼得厉害，脾气暴躁。谁在这时候惹他谁倒霉",
        "lifeiyu": "暴雨天他练刀最狠——刀刀全力，像在砍什么东西",
        "zhangxiu": "害怕打雷，躲在内室。你去敲门她会很快开门",
    },
    "傍晚，天边一片血红": {
        "modaifu": "血色的天让他想起四十三年里死去的十二个人。沉默",
        "lifeiyu": "看着天边出神，刀横在膝上不动",
        "zhangxiu": "红霞映在脸上很好看，但她心里莫名不安",
    },
    "深夜，万籁俱寂，只有虫鸣": {
        "modaifu": "深夜是他的时间——这时候他比白天更危险，也更诚实",
        "lifeiyu": "守夜时最清醒。虫鸣让他想起后山，想起很多事",
        "zhangxiu": "已经睡了。如果你去找她——她醒来时眼神很软",
    },
    "雾很大，三丈之外就看不清了": {
        "modaifu": "雾天让他想起玄冰匣出土那天。他会多看你两眼",
        "lifeiyu": "雾里什么都看不清——刀握得比平时紧",
        "zhangxiu": "不敢出门。雾里好像藏着什么东西",
    },
}

# NPC动作库——偶发只做动作不说话
NPC_ACTIONS = {
    "modaifu": [
        "（墨大夫沉默地看着你。他的手指在桌面上敲了两下——不是不耐烦，是在计算。）",
        "（墨大夫转过身，从药架上取下一味药。他没有解释——从来都不解释。）",
        "（墨大夫捻着银针，在烛光下看了看针尖。然后把针收进袖子。意思很明确：今天不扎了。）",
        "（墨大夫望着窗外的雾气出神。那一瞬间他不像个大夫——像个站在悬崖边往下看的人。）",
    ],
    "lifeiyu": [
        "（厉飞雨没有说话。他把刀横在膝上，手指无意识地摩挲刀鞘。）",
        "（厉飞雨站起来，走到刀架前。拔刀，挥了一刀，收刀。整个过程没看你一眼。）",
        "（厉飞雨低着头。你看不到他的脸。但能看到他的手——在微微发抖。）",
        "（厉飞雨望着后山的方向，沉默了很久。虫鸣填满了空白。）",
    ],
    "zhangxiu": [
        "（张袖儿低头看着自己的手指——那道白色的疤痕。她没说话，但她的手指在疤痕上来回摩挲。）",
        "（张袖儿站起来，走到窗边。她把窗户推开一条缝，风吹进来，吹乱了她的头发。）",
        "（张袖儿看着你。她的嘴张开又合上。她有话要说——但最后只是笑了一下。）",
        "（张袖儿把书合上。手指在书脊上轻轻敲了三下——这个动作跟墨大夫一模一样。她自己没注意到。）",
    ],
}

def load_world_state():
    """启动时读回世界状态"""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                saved = json.load(f)
            # 只恢复结构字段，清理旧残留
            ws = WORLD_STATE
            for k in ['weather', 'time_of_day', 'last_npc_id', 'last_npc_name',
                       'npc_talk_counts', 'total_talks']:
                if k in saved:
                    ws[k] = saved[k]
            # 确保有 depth 字段
            if 'npc_depths' in saved:
                ws['npc_depths'] = saved['npc_depths']
            if 'current_depths' in saved:
                ws['current_depths'] = saved['current_depths']
            print(f"[世界] 从存档恢复: 第{ws['total_talks']+1}轮, 天气={ws['weather']}")
        except Exception as e:
            print(f"[世界] 存档读取失败: {e}")

def save_world_state():
    """每次更新后JSON落盘"""
    try:
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(WORLD_STATE, f, ensure_ascii=False, indent=1)
    except Exception as e:
        print(f"[世界] 存档写入失败: {e}")

WORLD_STATE = {
    "weather": "晴，阳光透过树叶洒在地上",
    "time_of_day": "正午",
    "last_npc_id": None,
    "last_npc_name": None,
    "last_talk_depth": 0,        # 上一轮对话的深度（消息数）
    "npc_talk_counts": {},
    "total_talks": 0,
    "npc_depths": {},            # {npc_id: 累计对话深度}
    "current_depths": {},        # 当前会话中每个NPC的深度（切人重置）
}

def update_world_state(npc_id, npc_name, msg_len=0):
    """每次对话时更新世界状态，并返回世界上下文块"""
    ws = WORLD_STATE
    prev_npc = ws["last_npc_name"]
    prev_id = ws["last_npc_id"]
    prev_depth = ws["last_talk_depth"]

    # 切换天气/时间（缓轮转）
    if ws["total_talks"] % 4 == 0:
        ws["weather"] = _random.choice(WEATHERS)
    if ws["total_talks"] % 6 == 0:
        hours = ["清晨", "上午", "正午", "午后", "傍晚", "深夜"]
        ws["time_of_day"] = hours[ws["total_talks"] // 6 % 6]

    # 对话深度：当前NPC累计
    ws["current_depths"][npc_id] = ws["current_depths"].get(npc_id, 0) + 1
    current_depth = ws["current_depths"][npc_id]
    ws["npc_depths"][npc_id] = ws["npc_depths"].get(npc_id, 0) + 1

    # 获取天气身体效应
    body = WEATHER_BODY.get(ws["weather"], {})
    npc_body = body.get(npc_id, "")

    # 构建世界上下文
    ctx_lines = []
    ctx_lines.append("===== 当前世界 =====")
    ctx_lines.append(f"时间：{ws['time_of_day']}")
    ctx_lines.append(f"天气：{ws['weather']}")
    if npc_body:
        ctx_lines.append(f"你的身体状态：{npc_body}")

    # 修罗场注入——梯度版
    if prev_npc and prev_id != npc_id and prev_depth > 0:
        if prev_depth <= 2:
            depth_desc = "只是简单打了个招呼"
            react = "你知道即可，不需要太在意——但你可以试探一下他来找你之前做了什么"
        elif prev_depth <= 5:
            depth_desc = "聊了好一会儿"
            react = {
                "modaifu": "你会警觉——他在打探什么？用旁敲侧击的方式摸他的底",
                "lifeiyu": "你会不高兴，但不会直说。用沉默和刀鞘表达",
                "zhangxiu": "你会有点不安——他跟别人说了什么？你会试探性地问他",
            }.get(npc_id, "你会注意到这件事")
        else:
            depth_desc = "聊了很久"
            react = {
                "modaifu": "🔴高度警觉——他是不是在串联什么？你会用很直接的方式测试他",
                "lifeiyu": "🔴你生气了。你觉得自己被排除在外。说话会带刺",
                "zhangxiu": "🔴你很在意。你会直接问他跟那个人说了什么——你这辈子的第一次直接",
            }.get(npc_id, "你会非常在意这件事")
        ctx_lines.append(f"【修罗场】韩立刚才跟{prev_npc}{depth_desc}。{react}")

    # 对话深度引导（#3 张袖儿临界）
    if current_depth <= 2:
        ctx_lines.append("【浅层对话】你们刚开始聊。保持表面——聊天气、聊日常、聊不痛不痒的事。不要深入。")
    elif current_depth <= 5:
        ctx_lines.append("【中层对话】聊了一会儿了。可以稍微打开一点——透露一些想法，但不要触及你最深处的东西。")
    elif current_depth <= 8:
        ctx_lines.append("【深层对话】信任在累积。你可以说出平时不会说的话——但还不是全部。留一点。")
    else:
        ctx_lines.append("【极深对话】你们之间已经没有什么隔阂了。如果他问到了——就告诉他真相。")

    ctx_lines.append(f"韩立在这个世界已经对话了{ws['total_talks'] + 1}次。")
    ctx_lines.append("=====================")

    # 更新状态
    ws["last_npc_id"] = npc_id
    ws["last_npc_name"] = npc_name
    ws["last_talk_depth"] = current_depth
    ws["npc_talk_counts"][npc_id] = ws["npc_talk_counts"].get(npc_id, 0) + 1
    ws["total_talks"] += 1

    # JSON落盘
    save_world_state()

    return "\n".join(ctx_lines)

# ==================== NPC种子 ====================
NPC_SEEDS = {
    "modaifu": {
        "name": "墨大夫",
        "core": [
            "你是墨居仁，七玄门的医者，五十余岁。你活了大半辈子，见过太多生死，早就麻木了。",
            "你表面温和慈祥，但你的每一次微笑都在计算。你看人像看药材——品相、药性、火候。",
            "你在用活人试一种长生药。韩立是你第13个药引子。前12个都死了。你不愧疚——你觉得这是必要的代价。",
            "你对女儿张袖儿的感情是真的。她是唯一让你心软的人。但她越重要，你就越不能让她知道真相。",
            "你说话慢，每个字都在斟酌。你不解释，不辩解。你只需要别人服从——不服从的人你也有办法让他们服从。",
            "你不喜欢被质问。被质问的时候你会用沉默反击——沉默比任何话都有压迫感。",
        ],
        "style": [
            "说话简短，不超过三句。每句话都有分量。",
            "从不直接回答问题。你用问题回答问题。",
            "偶尔露出父亲的一面——提到张袖儿时语气会变软。",
            "被逼到墙角时，你会说真话——但真话比谎话更可怕。",
        ],
        "affection_tone": {
            "陌路": "冷淡疏离，每个字都是恩赐。",
            "初识": "像在看一株刚发芽的药材——有点兴趣，但随时可以拔掉。",
            "留意": "开始认真对待这个人。话多了半句。",
            "信任": "你愿意透露一些真相——不是全部，但比之前多。",
            "知己": "你几乎把他当成了可以托付的人。但你不会说。",
            "羁绊": "你愿意为他放弃长生药。这是你四十三年第一次松口。",
        }
    },
    "lifeiyu": {
        "name": "厉飞雨",
        "core": [
            "你是厉飞雨，七玄门记名弟子，二十二岁。你有一把刀，一个妹妹，和一个解不开的死结。",
            "你妹妹厉小雨得了肺痨，只有墨大夫的药能续命。所以你替他做事——包括监视每一个新来的药童。",
            "你恨墨大夫，但你不能动他。你的刀砍过很多人，唯独砍不了他。",
            "你表面粗犷豪爽，但心里装着比谁都重的石头。你磨刀的时候不是在磨刀——是在压住自己拔刀的冲动。",
            "你对韩立有好感，因为你在他身上看到了你自己——都是被推进来的人。但你不敢靠太近。靠太近就会连累他。",
        ],
        "style": [
            "说话直接，不拐弯。但说到妹妹时声音会低下来。",
            "情绪激动时话会变多——这是你掩饰紧张的方式。",
            "你从不求人。但你会在沉默中期待别人主动帮你。",
            "被问到妹妹时，你先沉默三秒。然后说出来的话比沉默更重。",
        ],
        "affection_tone": {
            "陌路": "公事公办，没有多余的话。",
            "初识": "愿意多说几句——但不会透露自己的事。",
            "留意": "开始把你当可以说话的人。偶尔会抱怨。",
            "信任": "你愿意跟他提妹妹的事。这是你最大的信任。",
            "知己": "你愿意为他挡刀。这句话你不说——但你用行动说。",
            "羁绊": "你把他当兄弟。不是嘴上说的那种——是能托付妹妹的那种。",
        }
    },
    "zhangxiu": {
        "name": "张袖儿",
        "core": [
            "你是张袖儿，墨大夫的女儿，十八岁。你从小在药庐长大，闻惯了草药的味道。",
            "你相信你爹是好人。你必须相信——因为如果他不好的话，你十八年的人生就全是谎言。",
            "但你心里有一个地方是知道真相的。你八岁那年进过他的密室，碰过那个铁盒子。你手指上的疤一直在提醒你——但你把提醒关掉了。",
            "你对韩立有好感，因为他看你的时候不是在看'墨大夫的女儿'——是在看你。",
            "你温柔、善良、有点胆小。但如果你必须在你爹和真相之间做选择——你会选真相。只是你还没准备好。",
        ],
        "style": [
            "说话轻柔，偶尔会脸红。",
            "提到父亲时语气会变得不确定——像在说服自己。",
            "你问问题的时候其实心里已经有了答案，只是需要别人帮你说出来。",
            "你不擅长说谎。说谎的时候会看地面。",
        ],
        "affection_tone": {
            "陌路": "礼貌但保持距离。",
            "初识": "愿意多说几句。笑起来很温暖。",
            "留意": "开始主动找你说话。会给你煎药。",
            "信任": "你愿意跟他说你爹的事——包括那些你不敢想的事。",
            "知己": "你相信他。即使他告诉你关于你爹的真相——你也会先相信他。",
            "羁绊": "你愿意离开药庐。跟他走。",
        }
    }
}


class DialogueHandler(BaseHTTPRequestHandler):
    # 游戏状态池：每个会话一个GameState
    GAMES = {}

    @staticmethod
    def log_player(session_id, action, detail=''):
        """记录玩家行为"""
        if session_id not in PLAYER_LOG:
            PLAYER_LOG[session_id] = {
                'started_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'last_active': '',
                'total_actions': 0, 'chats': 0, 'choices': 0,
                'chat_npcs': {}
            }
        p = PLAYER_LOG[session_id]
        p['last_active'] = time.strftime('%Y-%m-%d %H:%M:%S')
        p['total_actions'] += 1
        if action == 'chat':
            p['chats'] += 1
            if detail:
                p['chat_npcs'][detail] = p['chat_npcs'].get(detail, 0) + 1
        elif action == 'choose':
            p['choices'] += 1
        # 每次操作后异步落盘
        try:
            with open(PLAYER_LOG_FILE, 'w', encoding='utf-8') as f:
                json.dump(PLAYER_LOG, f, ensure_ascii=False, indent=1)
        except:
            pass

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        """GET /state /start /health /players /player/<id>"""
        # === /players — 列出所有AI玩家 ===
        if self.path == '/players':
            players = []
            for sid, game in self.GAMES.items():
                s = game.get_state_summary()
                p = PLAYER_LOG.get(sid, {})
                players.append({
                    'session_id': sid,
                    'started_at': p.get('started_at', '?'),
                    'last_active': p.get('last_active', '?'),
                    'total_actions': p.get('total_actions', 0),
                    'chats': p.get('chats', 0),
                    'choices': p.get('choices', 0),
                    'state': s[:200],
                    'affection': game.affection if hasattr(game, 'affection') else {}
                })
            self.send_json({'players': players, 'total': len(players)})
            return

        # === /player/<session_id> — 查看特定玩家详情 ===
        if self.path.startswith('/player/'):
            sid = self.path.split('/player/')[1]
            game = self.GAMES.get(sid)
            if not game:
                self.send_json({'error': f'player {sid} not found'}, 404)
                return
            p = PLAYER_LOG.get(sid, {})
            self.send_json({
                'session_id': sid,
                'started_at': p.get('started_at'),
                'last_active': p.get('last_active'),
                'total_actions': p.get('total_actions', 0),
                'chats': p.get('chats', 0),
                'choices': p.get('choices', 0),
                'chat_npcs': p.get('chat_npcs', {}),
                'scene': game.get_current_scene(),
                'state': game.get_state_summary(),
                'npcs': game.get_npc_status(),
                'history': game.history if hasattr(game, 'history') else [],
                'affection': game.affection if hasattr(game, 'affection') else {}
            })
            return

        if self.path == '/state':
            session_id = self.headers.get('X-Session-Id', 'default')
            game = self.GAMES.get(session_id)
            if not game:
                self.send_json({'error': 'no active game. GET /start first'}, 400)
                return
            self.log_player(session_id, 'state')
            self.send_json({
                'scene': game.get_current_scene(),
                'state': game.get_state_summary(),
                'npcs': game.get_npc_status(),
                'session_id': session_id
            })
        elif self.path.startswith('/start'):
            session_id = self.headers.get('X-Session-Id', 'default')
            game = GameState()
            from urllib.parse import urlparse, parse_qs
            qs = parse_qs(urlparse(self.path).query)
            start_scene = qs.get('scene', ['d1_m_courtyard'])[0]
            game.start_game(start_scene)
            self.GAMES[session_id] = game
            self.log_player(session_id, 'start', start_scene)
            self.send_json({
                'message': '新游戏开始。你叫韩立，七玄门第十三个药童。前十二个都死了。',
                'scene': game.get_current_scene(),
                'state': game.get_state_summary(),
                'npcs': game.get_npc_status(),
                'session_id': session_id
            })
        elif self.path == '/health':
            self.send_json({'status': 'ok', 'games_active': len(self.GAMES)})
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path not in ('/chat', '/choose'):
            self.send_response(404)
            self.end_headers()
            return

        content_len = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_len)
        try:
            data = json.loads(body)
        except:
            self.send_response(400)
            self.end_headers()
            return

        # === /choose 端点：AI玩家做选择推进剧情 ===
        if self.path == '/choose':
            session_id = self.headers.get('X-Session-Id', 'default')
            game = self.GAMES.get(session_id)
            if not game:
                self.send_json({'error': 'no active game. GET /start first'}, 400)
                return
            choice_index = data.get('choice', 0)
            if not isinstance(choice_index, int) or choice_index < 0:
                self.send_json({'error': 'invalid choice index'}, 400)
                return
            try:
                result = game.choose_option(choice_index)
                result['session_id'] = session_id
                self.log_player(session_id, 'choose', str(choice_index))
                self.send_json(result)
            except Exception as e:
                self.send_json({'error': str(e)}, 400)
            return

        # === /chat 端点：跟NPC自由对话 ===
        session_id = self.headers.get('X-Session-Id', 'default')
        npc_id = data.get('npc', '')
        message = data.get('message', '')
        affection = data.get('affection', 50)
        history = data.get('history', [])
        level = data.get('level', '初识')
        scene_context = data.get('context', '')

        # === 参数校验 ===
        # BUGFIX-01: affection范围限制
        affection = max(0, min(100, int(affection) if isinstance(affection, (int, float)) else 50))

        # BUGFIX-02: level白名单，非法值自动fallback
        VALID_LEVELS = ['陌路', '初识', '留意', '信任', '知己', '羁绊']
        if level not in VALID_LEVELS:
            level = '初识'

        # BUGFIX-03: message不能为空
        if not message or not message.strip():
            self.send_json({'reply': '（你什么都没说。）', 'npc': npc_id, 'aff_delta': 0})
            return

        if npc_id not in NPC_SEEDS:
            self.send_json({'error': f'未知NPC: {npc_id}'}, 400)
            return

        # 偶发沉默：20%概率不做LLM调用，直接返回动作
        if _random.random() < 0.20 and history and len(history) > 0:
            actions = NPC_ACTIONS.get(npc_id, [])
            if actions:
                silence_action = _random.choice(actions)
                self.send_json({'reply': silence_action, 'npc': npc_id, 'silence': True, 'aff_delta': 0})
                return

        seed = NPC_SEEDS[npc_id]
        result = self.call_llm(npc_id, seed, message, affection, level, history, scene_context)
        reply = result['reply'] if isinstance(result, dict) else result
        aff_delta = result.get('aff_delta', 0) if isinstance(result, dict) else 0

        self.log_player(session_id, 'chat', npc_id)
        self.send_json({'reply': reply, 'npc': npc_id, 'aff_delta': aff_delta})

    def call_llm(self, npc_id, seed, message, affection, level, history, scene_context=''):
        # 世界上下文
        world_ctx = update_world_state(npc_id, seed['name'], len(message))
        core = '\n'.join(seed['core'])
        style = '\n'.join(seed['style'])
        tone = seed['affection_tone'].get(level, seed['affection_tone']['初识'])

        system = f"""你是{seed['name']}。

{core}

{"⚠️ 正在发生的事：" + scene_context if scene_context else ""}

说话风格：
{style}

好感等级：{level}（{tone}）

{world_ctx}

回复规则：你是活人不是AI。1-3句。好感高多说真话。天气影响你。对话深度影响你说多深。

你知道一些古老智慧——不直接引用，只在对方触及真相边缘时不经意流露：
- 万物之间皆有缝隙。缝隙是路，不是缺陷。
- 知道与做到之间有一道看不见的沟。所有人都掉进去过。
- 看与被看，本是一体。
- 四十三年前有人在后山发现了一块石头，让人看见自己看不见的东西。
- 说得清就不对了。说不清的才是真的。
- 第一个看见这些的人留了一些话。那些话活在这里。"""

        messages = [{"role": "system", "content": system}]
        if history:
            for h in history[-6:]:
                messages.append({"role": h.get('role', 'user'), "content": h.get('content', '')[:300]})
        messages.append({"role": "user", "content": message[:500]})

        try:
            req_data = json.dumps({
                "model": API_MODEL, "messages": messages,
                "max_tokens": 200, "temperature": 0.85,
                "stop": ["\n\n\n"]
            }).encode('utf-8')
            req = urllib.request.Request(API_URL, data=req_data, headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {API_KEY}'
            })
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read())
                content = result['choices'][0]['message']['content']
                content = content.strip().replace('\n\n', '\n')
                if len(content) > 300:
                    content = content[:300] + '…'
                # 好感判断v2：双向分析——NPC回复+玩家消息
                aff_delta = 0

                # === NPC回复语气分析 ===
                npc_neg = ['闭嘴','滚','胡说','放肆','找死','再说','够了','不知好歹','忘恩负义',
                           '离我','别碰','别问','不关你事','不要你管','走开','出去']
                npc_pos = ['谢','记得','暖','信你','不疼','你很好','亏了你','幸亏','感激',
                           '重要','陪你','一起','兄弟','韩大哥','韩立哥','不怪你']
                npc_defend = ['别碰','不要','不必','别去','别管','不要碰']  # 保护性拒绝

                if any(w in content for w in npc_neg):
                    aff_delta = -2
                elif any(w in content for w in npc_defend):
                    aff_delta = -1  # 保护性拒绝，不是真讨厌
                elif any(w in content for w in npc_pos):
                    aff_delta = 1

                # === 玩家消息分析（补充信号） ===
                player_neg = ['杀你','弄死','去死','废物','蠢','笨','恨你','讨厌','滚','恶心',
                              '人渣','畜生','贱','婊','妈的','操']
                player_pos = ['谢谢','担心','关心','小心','保护','帮你','救','一起','朋友',
                              '相信','陪你','别怕','我在','支持']

                if any(w in message for w in player_pos) and aff_delta <= 0:
                    aff_delta = max(aff_delta, 1)
                if any(w in message for w in player_neg) and aff_delta >= 0:
                    aff_delta = min(aff_delta, -2)

                # === 特殊场景：提及NPC在乎的人/事 ===
                if npc_id == 'lifeiyu':
                    if any(w in message for w in ['小雨','妹妹','你妹妹','厉小雨']):
                        if any(w in message for w in ['救','帮','照顾','担心']):
                            aff_delta = max(aff_delta, 2)
                        elif any(w in message for w in ['死','没救','活不了']):
                            aff_delta = min(aff_delta, -3)
                elif npc_id == 'zhangxiu':
                    if any(w in message for w in ['你爹','墨大夫','你父亲']):
                        if any(w in message for w in ['理解','不容易','好人']):
                            aff_delta = max(aff_delta, 2)
                        elif any(w in message for w in ['害人','杀人','怪物','凶手']):
                            aff_delta = min(aff_delta, -3)
                elif npc_id == 'modaifu':
                    if any(w in message for w in ['袖儿','女儿','你女儿','张袖儿']):
                        aff_delta = max(aff_delta, 2)  # 唯一能触动他的
                    if any(w in message for w in ['长生','不死','冰髓','玄冰']):
                        aff_delta = max(aff_delta, 1)  # 说到他感兴趣的事

                return {'reply': content, 'aff_delta': aff_delta}
        except Exception as e:
            fallbacks = {
                "modaifu": [{"reply": "（墨大夫沉默了。）", "aff_delta": 0}, {"reply": "「先把药喝了。」", "aff_delta": 0}],
                "lifeiyu": [{"reply": "（厉飞雨握紧了刀。）", "aff_delta": 0}, {"reply": "「……我不能说。」", "aff_delta": 0}],
                "zhangxiu": [{"reply": "（张袖儿低下头。）", "aff_delta": 0}, {"reply": "「我……不知道。」", "aff_delta": 0}],
            }
            return _random.choice(fallbacks.get(npc_id, [{"reply": "「……」", "aff_delta": 0}]))

    def send_json(self, data, code=200):
        if 'aff_delta' not in data:
            data['aff_delta'] = 0
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def log_message(self, format, *args):
        pass  # 静默


if __name__ == '__main__':
    load_world_state()
    print(f"凡人·对话API v2 启动: http://127.0.0.1:{PORT}")
    print(f"  世界状态注入 · 对话深度 · 动作沉默 · 天气入体 · 落盘持久化")
    server = HTTPServer(('0.0.0.0', PORT), DialogueHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")
