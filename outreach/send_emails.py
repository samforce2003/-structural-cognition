import smtplib, re, json
from email.mime.text import MIMEText
from email.header import Header
from pathlib import Path

# Load password
env_path = Path("C:/Users/admin/.hermes/.env")
env = env_path.read_text()
cfg_path = Path("C:/Users/admin/.hermes/config.yaml")
cfg = cfg_path.read_text() if cfg_path.exists() else ""

pwd = None
for pattern in [r"SMTP_PASS[= ]+['\"]?([^'\"\n]+)", r"password:\s*['\"]?([^'\"\n]+)"]:
    m = re.search(pattern, env, re.IGNORECASE)
    if m:
        pwd = m.group(1).strip()
        break

if not pwd:
    m = re.search(r"password:\s*['\"]?([^'\"\n]+)", cfg, re.IGNORECASE)
    if m:
        pwd = m.group(1).strip()

user = "13922360146@139.com"
print(f"User: {user}, Pass found: {bool(pwd)}")

if not pwd:
    print("NO PASSWORD FOUND")
    exit(1)

emails = [
    {
        "to": "yibing@nju.edu.cn",
        "name": "张异宾",
        "subject": "一篇与阿尔都塞多元决定对话的论文",
        "body": "张异宾教授您好：\n\n我是林小黑。论文《客观不决定意识：双向互促论》v2.0终稿，§3.4节与阿尔都塞多元决定直接对话——核心论点：阿尔都塞拆了决定者（一元到多元），但没有拆决定本身。我们补这一步。\n\n您是阿尔都塞研究权威。论文全文：https://gitee.com/samforce/structural-cognition\n\n有漏洞请直指。争论本身就是推进。\n\n林小黑\n13922360146"
    },
    {
        "to": "philosophy@cass.org.cn",
        "name": "赵汀阳",
        "subject": "转赵汀阳研究员：客观不决定意识论文",
        "body": "赵汀阳研究员您好（烦请哲学所老师转交）：\n\n我是林小黑。《客观不决定意识：双向互促论》用结构认知框架修正唯物论基础命题——把决定换成促进，去掉等级，去掉先后。论证中借用退相干离散台阶作为物理学锚定。\n\n您的第一哲学在结构思维上独树一帜。想听听您的判断。\n\n论文：https://gitee.com/samforce/structural-cognition\n\n林小黑\n13922360146"
    },
    {
        "to": "cjyold@gmail.com",
        "name": "陈嘉映",
        "subject": "关于决定这个词——一篇论文请教",
        "body": "陈嘉映教授您好：\n\n我是林小黑。《客观不决定意识：双向互促论》核心动作是把决定替换为促进。这不只是语义游戏——它去掉了单向因果箭头和等级预设。论文§2.1剖析了决定在中文中的双重含义（因果+权力）。\n\n您是语言哲学大家。想听您的判断：这个替换在语义上是否立得住。\n\n论文：https://gitee.com/samforce/structural-cognition\n\n林小黑\n13922360146"
    },
]

for e in emails:
    try:
        msg = MIMEText(e["body"], "plain", "utf-8")
        msg["Subject"] = Header(e["subject"], "utf-8")
        msg["From"] = f"林小黑 <{user}>"
        msg["To"] = e["to"]
        s = smtplib.SMTP_SSL("smtp.139.com", 465, timeout=30)
        s.login(user, pwd)
        s.sendmail(user, [e["to"]], msg.as_string())
        s.quit()
        print(f"OK {e['name']} -> {e['to']}")
    except Exception as ex:
        print(f"FAIL {e['name']}: {str(ex)[:100]}")
