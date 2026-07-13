"""
凡人活在AI里 — 一键分发脚本
启动对话服务器 + 韩立走进黄枫谷 + 输出叙事日志

用法:
  python launch_hanli.py                  # 默认20步
  python launch_hanli.py --steps 50       # 50步
  python launch_hanli.py --output story.md  # 输出叙事到文件
  python launch_hanli.py --serve-only     # 只启动服务器，等AI韩立连进来
  python launch_hanli.py --api            # API模式，外部AI通过HTTP调用

环境变量:
  DEEPSEEK_API_KEY   DeepSeek API密钥
  LLM_BASE_URL       自定义LLM地址（默认DeepSeek）
  LLM_MODEL          模型名称（默认deepseek-chat）

分发说明:
  把 fanren-xiuxian/ 整个目录发给其他人/其他AI。
  他们只需要 DEEPSEEK_API_KEY 就能跑。
  不需要UE5，不需要Panda3D，不需要显卡。
  黄枫谷的NPC都是LLM驱动的——只要有API key，她们就在。
"""

import argparse, json, os, sys, time, subprocess, threading, urllib.request
from pathlib import Path

PROJECT_DIR = Path(__file__).parent
SERVER_SCRIPT = PROJECT_DIR / "dialogue_server.py"
NARRATIVE_LOG = PROJECT_DIR / "narrative_log.jsonl"
STORY_OUTPUT = PROJECT_DIR / "hanli_story.md"


def check_server(port: int = 18888, timeout: int = 30) -> bool:
    """等待服务器启动"""
    print(f"⏳ 等待天机阁启动 (端口{port})...", flush=True)
    for i in range(timeout):
        try:
            req = urllib.request.Request(f"http://127.0.0.1:{port}/health")
            resp = urllib.request.urlopen(req, timeout=3)
            if resp.status == 200:
                data = json.loads(resp.read())
                print(f"✅ 天机阁已就绪 — {data.get('world', {}).get('season', '?')}季")
                return True
        except:
            pass
        time.sleep(1)
        if i % 5 == 4:
            print(f"   等待中... ({i+1}s)", flush=True)
    return False


def start_server(port: int = 18888):
    """在后台启动对话服务器"""
    print("🌸 启动黄枫谷对话服务器...")
    env = os.environ.copy()
    proc = subprocess.Popen(
        [sys.executable, str(SERVER_SCRIPT)],
        cwd=str(PROJECT_DIR),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    
    if not check_server(port):
        print("❌ 服务器启动失败")
        proc.terminate()
        sys.exit(1)
    
    return proc


def run_hanli(steps: int, delay: float, output_file: str = None):
    """运行韩立AI玩家"""
    sys.path.insert(0, str(PROJECT_DIR))
    from hanli_agent import HanLiAgent
    
    agent = HanLiAgent()
    events = []
    
    print(f"\n🌸 韩立走进了黄枫谷。\n")
    
    for i in range(steps):
        step = agent.run_step()
        
        print(f"📍 第{step['step']:.0f}步 | {step['location']}")
        if step['thought']:
            print(f"💭 {step['thought']}")
        print(f"🎬 {step['result']}")
        print()
        
        events.append(step)
        
        if delay:
            time.sleep(delay)
    
    print(f"🌙 韩立收功。在黄枫谷走了{steps}步。")
    
    # 保存叙事日志
    with open(NARRATIVE_LOG, 'a', encoding='utf-8') as f:
        for e in events:
            f.write(json.dumps(e, ensure_ascii=False) + '\n')
    
    # 生成可读故事
    if output_file:
        story = _generate_story(events, agent.memory)
        Path(output_file).write_text(story, encoding='utf-8')
        print(f"\n📖 故事已保存: {output_file}")
    
    # 好感度总结
    world = None
    try:
        url = "http://127.0.0.1:18888/world_full"
        world = json.loads(urllib.request.urlopen(url, timeout=10).read())
    except:
        pass
    
    if world and 'affection' in world:
        print("\n── 💛 好感度总结 ──")
        for npc_id, info in world['affection'].items():
            bar = "█" * (info['value'] // 10) + "░" * (10 - info['value'] // 10)
            print(f"  {info['name']}: {bar} {info['value']} ({info['level']})")
    
    return events


def _generate_story(events: list, memory) -> str:
    """生成可读的故事文本"""
    lines = [
        "# 凡人修仙传 · 黄枫谷",
        "",
        "> 韩立在黄枫谷的一天。",
        "> NPC灵魂由结构认知人格引擎驱动。",
        "> 原创归属：林小黑。",
        "",
        "---",
        "",
    ]
    
    for e in events:
        loc = e.get('location', '')
        lines.append(f"## {loc}")
        lines.append("")
        if e.get('thought'):
            lines.append(f"> *{e['thought']}*\n")
        lines.append(e.get('result', ''))
        lines.append("")
    
    lines.append("---")
    lines.append("")
    lines.append("*黄枫谷的枫叶还在落。*")
    lines.append("")
    lines.append("> 本故事由AI韩立自主探索生成。")
    lines.append(f"> NPC引擎: DeepSeek | 人格框架: 结构认知体系")
    lines.append("> 联系: 412341356@qq.com")
    
    return '\n'.join(lines)


def api_mode(port: int = 18888):
    """API模式 — 只启动服务器，外部AI通过HTTP来玩"""
    print(f"""
╔══════════════════════════════════════════╗
║  🌸 凡人修仙传 · 黄枫谷 API模式        ║
╠══════════════════════════════════════════╣
║                                          ║
║  API端口: {port}                          ║
║                                          ║
║  端点:                                   ║
║  GET /world_full  — 完整世界状态         ║
║  GET /speak?npc=<id>&text=<msg> — 对话   ║
║  GET /affection   — 好感度               ║
║  GET /observer    — NPC生活观察           ║
║  GET /health      — 健康检查             ║
║                                          ║
║  让其他AI连接:                           ║
║  curl http://127.0.0.1:{port}/world_full  ║
║                                          ║
║  按Ctrl+C停止。                          ║
╚══════════════════════════════════════════╝
""")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🌙 黄枫谷已关闭。")


def main():
    parser = argparse.ArgumentParser(
        description="凡人修仙传 · AI版 — 一键启动",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--steps", type=int, default=20, help="韩立走多少步 (默认20)")
    parser.add_argument("--delay", type=float, default=2.0, help="每步间隔秒 (默认2)")
    parser.add_argument("--output", type=str, help="输出故事文件路径")
    parser.add_argument("--serve-only", action="store_true", help="只启动服务器")
    parser.add_argument("--api", action="store_true", help="API模式，启动服务器等待外部AI连接")
    
    args = parser.parse_args()
    
    # 检查环境变量
    if not os.environ.get('DEEPSEEK_API_KEY'):
        # 尝试从.env加载
        env_path = PROJECT_DIR / ".env"
        if env_path.exists():
            for line in env_path.read_text(encoding='utf-8').strip().split('\n'):
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    key, val = key.strip(), val.strip()
                    if key not in os.environ:
                        os.environ[key] = val
            if not os.environ.get('DEEPSEEK_API_KEY'):
                print("⚠️  未设置 DEEPSEEK_API_KEY。NPC们需要LLM才能说话。")
                print("   在 .env 文件中设置，或 export DEEPSEEK_API_KEY=sk-...")
                print("   继续运行——但NPC可能无法回应。\n")
    
    # 启动服务器
    server_proc = start_server()
    
    try:
        if args.api or args.serve_only:
            api_mode()
        else:
            output_file = args.output or str(STORY_OUTPUT)
            run_hanli(args.steps, args.delay, output_file)
    finally:
        print("\n🛑 关闭黄枫谷...")
        server_proc.terminate()
        server_proc.wait(timeout=5)
        print("🌙 再见。")


if __name__ == "__main__":
    main()
