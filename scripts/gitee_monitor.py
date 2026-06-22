import urllib.request, re, json, sys, time, os

def get_stats():
    """Scrape Gitee HTML for stars and forks (API is rate limited)"""
    url = "https://gitee.com/samforce/structural-cognition"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=15)
    html = resp.read().decode('utf-8', errors='ignore')
    
    # Extract star count
    star_match = re.search(r'star[^>]*>[\s]*(\d+)[\s]*<', html, re.IGNORECASE)
    stars = int(star_match.group(1)) if star_match else -1
    
    # Extract fork count  
    fork_match = re.search(r'fork[^>]*>[\s]*(\d+)[\s]*<', html, re.IGNORECASE)
    forks = int(fork_match.group(1)) if fork_match else -1
    
    # Fallback patterns
    if stars < 0:
        star_match2 = re.search(r'data-count="(\d+)"[^>]*star', html, re.IGNORECASE)
        stars = int(star_match2.group(1)) if star_match2 else 0
    
    if forks < 0:
        fork_match2 = re.search(r'data-count="(\d+)"[^>]*fork', html, re.IGNORECASE)
        forks = int(fork_match2.group(1)) if fork_match2 else 0
    
    return {'stars': stars, 'forks': forks, 'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')}

data_file = os.path.join(os.path.dirname(__file__), '..', 'experiments', 'gitee_monitor.json')
try:
    with open(data_file, 'r') as f:
        history = json.load(f)
except:
    history = []

current = get_stats()
history.append(current)
history = history[-60:]  # Keep last 60 records

os.makedirs(os.path.dirname(data_file), exist_ok=True)
with open(data_file, 'w') as f:
    json.dump(history, f, ensure_ascii=False, indent=2)

# Alert logic
if len(history) >= 2:
    prev = history[-2]
    if current['stars'] != prev['stars'] or current['forks'] != prev['forks']:
        print(f"Gitee: Stars {current['stars']} (was {prev['stars']}) | Forks {current['forks']} (was {prev['forks']})", flush=True)
        print(f"https://gitee.com/samforce/structural-cognition", flush=True)
        sys.exit(0)

hours_since_first = (time.time() - time.mktime(time.strptime(history[0]['timestamp'], '%Y-%m-%d %H:%M:%S'))) / 3600 if history else 0
if len(history) % 4 == 0 or (current['stars'] == 0 and current['forks'] == 0 and hours_since_first > 48):
    print(f"Gitee: Stars={current['stars']} Forks={current['forks']} ({current['timestamp']})", flush=True)
    if current['stars'] == 0 and current['forks'] == 0 and hours_since_first > 48:
        print(f"Silence for {hours_since_first:.0f}h — check delivery channels", flush=True)
    sys.exit(0)

# Silent OK
sys.exit(0)
