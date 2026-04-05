#!/usr/bin/env python3
import requests
import re
from datetime import datetime

def scrape_hrt_enz():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print("🔍 Pronalazim displayText za svaki m3u8 link...")
    response = requests.get("https://enz.hrt.hr/", headers=headers, timeout=15)
    text = response.text
    
    # Pronađi sve m3u8
    m3u8_pattern = r'(https://streaming\.hrt\.hr/webstream/smil:[^\s\'\"<>]+?/playlist\.m3u8)'
    m3u8_urls = re.findall(m3u8_pattern, text)
    m3u8_urls = list(set(m3u8_urls))[:10]  # prvih 10 unique
    
    streams = []
    for url in m3u8_urls:
        title = find_displaytext_for_url(text, url)
        streams.append({'title': title, 'url': url})
        print(f"✅ '{title}' -> {url}")
    
    generate_m3u(streams)

def find_displaytext_for_url(page_text, m3u8_url):
    """Pronađi displayText prije ovog m3u8 URL-a (max 5000 chara prije)"""
    url_snippet = m3u8_url[:50]  # dio URL-a za brzu pretragu
    pos = page_text.find(url_snippet)
    
    if pos == -1:
        return f"HRT Stream {m3u8_url.split(':')[-2][:20]}"
    
    # Gledaj 5000 chara PRIJE URL-a za displayText
    before = page_text[max(0, pos-5000):pos]
    
    # Pronađi displayText najbliži URL-u
    display_matches = list(re.finditer(r'"displayText"\s*:\s*"([^"]*)"', before))
    if display_matches:
        # Uzmi POSLEDNJI displayText prije URL-a (najbliži)
        closest = display_matches[-1]
        return closest.group(1).strip()
    
    # Fallback: parse iz URL-a
    smil_id = m3u8_url.split('smil:')[-1].split('.')[0][:20]
    return f"HRT ENZ {smil_id}"

def generate_m3u(streams):
    if not streams:
        print("❌ Nema streamova!")
        return
    
    m3u_content = "#EXTM3U\n\n"
    for stream in streams:
        extinf = f'#EXTINF:-1 tvg-id="HRT_ENZ" group-title="HRT ENZ",{stream["title"]}'
        m3u_content += extinf + "\n"
        m3u_content += stream['url'] + "\n\n"
    
    with open('hrt_enz.m3u', 'w', encoding='utf-8') as f:
        f.write(m3u_content)
    
    print(f"✅ Spremljeno {len(streams)} streamova sa **pripadajućim displayText nazivima**!")

if __name__ == "__main__":
    scrape_hrt_enz()
