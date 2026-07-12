#!/usr/bin/env python3
"""
Daily Paper Scanner — scans arXiv hot papers, matches against structural cognition ammo.
Run: python daily_paper_scanner.py
Output: candidate matches with author emails for manual review + email writing.
"""

import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import re
import sys
import ssl
from datetime import datetime

AMMO_INDEX = "D:/projects/structural-cognition/ammo_index.json"
OUTPUT_DIR = "D:/projects/structural-cognition/candidates"

# arXiv categories to scan (rotate daily? for now: scan all, limited results each)
CATEGORIES = [
    "cs.AI", "cs.LG", "cs.CL", "cs.CY",
    "quant-ph",
    "stat.ML",
    "physics.soc-ph",
    "econ.TH",
]

MAX_PER_CAT = 10  # papers per category
MAX_RESULTS_TOTAL = 80

def load_ammo():
    with open(AMMO_INDEX, "r", encoding="utf-8") as f:
        return json.load(f)

PROXY = 'http://127.0.0.1:17890'

def _get_opener():
    """Build opener with proxy support and relaxed SSL."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    proxy_handler = urllib.request.ProxyHandler({'http': PROXY, 'https': PROXY})
    return urllib.request.build_opener(proxy_handler, urllib.request.HTTPSHandler(context=ctx))

def fetch_arxiv(category, max_results=10):
    """Fetch recent papers from arXiv for a given category."""
    url = (
        f"https://export.arxiv.org/api/query?"
        f"search_query=cat:{category}"
        f"&sortBy=submittedDate&sortOrder=descending"
        f"&max_results={max_results}"
    )
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/xml'
        })
        opener = _get_opener()
        with opener.open(req, timeout=30) as resp:
            return resp.read().decode('utf-8')
    except Exception as e:
        print(f"  [WARN] Failed to fetch {category}: {e}")
        return None

def parse_arxiv_xml(xml_data):
    """Parse arXiv Atom XML, return list of paper dicts."""
    ns = {
        'atom': 'http://www.w3.org/2005/Atom',
        'arxiv': 'http://arxiv.org/schemas/atom'
    }
    papers = []
    try:
        root = ET.fromstring(xml_data)
        for entry in root.findall('atom:entry', ns):
            title_el = entry.find('atom:title', ns)
            title = title_el.text.strip().replace('\n', ' ') if title_el is not None else ''
            
            summary_el = entry.find('atom:summary', ns)
            summary = summary_el.text.strip().replace('\n', ' ') if summary_el is not None else ''
            
            arxiv_id_el = entry.find('atom:id', ns)
            arxiv_id = arxiv_id_el.text.strip() if arxiv_id_el is not None else ''
            # Extract just the ID part
            arxiv_id = arxiv_id.split('/abs/')[-1] if '/abs/' in arxiv_id else arxiv_id
            
            authors = []
            for author_el in entry.findall('atom:author', ns):
                name_el = author_el.find('atom:name', ns)
                if name_el is not None:
                    authors.append(name_el.text.strip())
            
            published_el = entry.find('atom:published', ns)
            published = published_el.text.strip()[:10] if published_el is not None else ''
            
            papers.append({
                'arxiv_id': arxiv_id,
                'title': title,
                'summary': summary,
                'authors': authors,
                'published': published,
            })
    except ET.ParseError as e:
        print(f"  [WARN] XML parse error: {e}")
    return papers

def match_keywords(text, keywords):
    """Count keyword matches in text (case-insensitive)."""
    text_lower = text.lower()
    matches = []
    for kw in keywords:
        if kw.lower() in text_lower:
            matches.append(kw)
    return matches

def find_candidates(papers, ammo):
    """Match arXiv papers against ammo."""
    candidates = []
    for paper in papers:
        paper_text = paper['title'] + ' ' + paper['summary']
        for ammo_item in ammo:
            matched_kw = match_keywords(paper_text, ammo_item['keywords'])
            if len(matched_kw) >= 2:  # at least 2 keyword hits
                candidates.append({
                    'arxiv_paper': paper,
                    'ammo': ammo_item,
                    'matched_keywords': matched_kw,
                    'match_count': len(matched_kw),
                })
    # Deduplicate by arxiv_id + ammo_id, keep highest match
    seen = {}
    unique = []
    for c in candidates:
        key = (c['arxiv_paper']['arxiv_id'], c['ammo']['id'])
        if key not in seen or c['match_count'] > seen[key]['match_count']:
            seen[key] = c
    for c in seen.values():
        unique.append(c)
    
    # Sort by match_count desc
    unique.sort(key=lambda x: x['match_count'], reverse=True)
    return unique

def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] Starting daily paper scan...")
    
    ammo = load_ammo()
    print(f"Loaded {len(ammo)} ammo papers across {len(set(a['discipline'] for a in ammo))} disciplines")
    
    all_papers = []
    for cat in CATEGORIES:
        print(f"  Scanning {cat}...")
        xml_data = fetch_arxiv(cat, MAX_PER_CAT)
        if xml_data:
            papers = parse_arxiv_xml(xml_data)
            print(f"    Found {len(papers)} papers")
            all_papers.extend(papers)
    
    print(f"\nTotal papers scanned: {len(all_papers)}")
    
    candidates = find_candidates(all_papers, ammo)
    print(f"Candidates found: {len(candidates)}")
    
    if not candidates:
        print("No candidate matches today.")
        return
    
    # Output
    today = datetime.now().strftime('%Y-%m-%d')
    output_path = f"{OUTPUT_DIR}/candidates_{today}.json"
    
    output = {
        'date': today,
        'total_scanned': len(all_papers),
        'candidates': []
    }
    
    for i, c in enumerate(candidates, 1):
        ap = c['arxiv_paper']
        am = c['ammo']
        
        entry = {
            'rank': i,
            'match_score': c['match_count'],
            'matched_keywords': c['matched_keywords'],
            'arxiv_paper': {
                'id': ap['arxiv_id'],
                'title': ap['title'],
                'authors': ap['authors'],
                'published': ap['published'],
                'url': f"https://arxiv.org/abs/{ap['arxiv_id']}",
            },
            'our_ammo': {
                'id': am['id'],
                'title': am['title_en'],
                'file': am['file'],
                'discipline': am['discipline'],
                'angle': am['angle'],
            }
        }
        output['candidates'].append(entry)
        
        print(f"\n  #{i} [{c['match_count']} hits] {ap['title'][:100]}")
        print(f"     Authors: {', '.join(ap['authors'][:3])}")
        print(f"     Match: {c['matched_keywords']}")
        print(f"     → Our ammo: {am['id']} ({am['discipline']})")
    
    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\nSaved to {output_path}")

if __name__ == '__main__':
    main()
