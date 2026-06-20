import requests
import json
import os

proxies = {'http': 'http://127.0.0.1:17890', 'https': 'http://127.0.0.1:17890'}
token = '4b33abaf6c5c9b1a065f25961cce4366ed06546bda8c02293ba771ebac92'

LQ = '\u201c'  # left quote
RQ = '\u201d'  # right quote

title = "为什么分手十年了还会梦见TA"

content = []

def p(text):
    content.append({"tag": "p", "children": [text]})

def b(text):
    content.append({"tag": "b", "children": [text]})

p("你早就放下了。新生活、新对象、新的自己。一切都好。")
p("然后突然有一天，你梦见了十年前的那个人。醒来之后整个人空落落的，像被抽走了什么。你问自己：难道我还爱TA吗？")
p("不是。")
p(f"不是你还在爱TA——是你和TA在一起时的那个{LQ}你{RQ}，那个版本的结构，从来没有被重组过。")
b("时间不会治愈一切。")
p("时间能治的东西很少。擦伤可以。骨折不行。")
p("分手是骨折，不是擦伤。你们在一起的时候，你的日常节奏、你的决策方式、你的情绪回路、你看待未来的坐标系——全都被那个人嵌入了。那个人离开之后，这些结构没有消失。它们被封存了。")
p("封存≠愈合。")
p("你换了城市、换了工作、换了身边的人。你以为你在往前走。但那些旧结构一直在——它们只是没有被触发。梦里被触发了。一触发，你就回到了十年前的自己。不是回忆。是回到。")
p("这和那个人没有关系。换一个人，同样的结构创伤还在。不是你还没放下TA——是你还没重组自己。")
p("怎么重组？不是忘掉TA。不是找新的人覆盖旧的记忆。这些东西全部是在原来的结构上重新装修——墙没动。")
p(f"真正的重组是：你不需要那个人在场，你重新走了一遍当初因为TA而拐弯的路——然后发现你可以直着走。")
p("梦里还在见的人，不是你放不下的人，是你还没走过的那段路。")
p("\u2014\u2014")
p("林小黑 \u00b7 结构认知体系 \u00b7 2026")
p("更多：https://gitee.com/samforce/structural-cognition")

data = {
    'access_token': token,
    'title': title,
    'author_name': '林小黑',
    'content': json.dumps(content, ensure_ascii=False),
    'return_content': True
}

resp = requests.post('https://api.telegra.ph/createPage', json=data, proxies=proxies, timeout=15)
result = resp.json()
print("Status:", resp.status_code)
print(json.dumps(result, indent=2, ensure_ascii=False))

if result.get('ok'):
    url = result['result']['url']
    print(f"\n=== SHOT #1 FIRED ===")
    print(f"Title: {title}")
    print(f"URL: {url}")
    
    # Save content locally
    seed_path = 'D:/projects/structural-cognition/seeds/shot-1-time-doesnt-heal-love.md'
    os.makedirs(os.path.dirname(seed_path), exist_ok=True)
    with open(seed_path, 'w', encoding='utf-8') as f:
        f.write(f"# {title}\n\n")
        for item in content:
            f.write(item['children'][0] + '\n\n')
    
    # Save last shot URL
    with open('D:/projects/structural-cognition/last-shot-url.txt', 'w', encoding='utf-8') as f:
        f.write(f"Shot #1 | {title} | {url}")
    
    print(f"Seed saved: {seed_path}")
else:
    print(f"\nFAILED: {result.get('error')}")
