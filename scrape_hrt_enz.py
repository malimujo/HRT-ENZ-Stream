#!/usr/bin/env python3
import requests
import re

def scrape_hrt_enz():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print("🔍 TiviMate MOVIES - HRT ENZ VOD...")
    response = requests.get("https://enz.hrt.hr/", headers=headers, timeout=15)
    text = response.text
    
    pairs = []
    matches = list(re.finditer(r'"displayText"\s*:\s*"([^"]+)"(?=.*?https://streaming\.hrt\.hr/webstream/smil:([^\s\'\"<>]+?)\.smil/playlist\.m3u8)', text, re.DOTALL | re.IGNORECASE))
    
    for match in matches[:15]:
        display_text = match.group(1).strip()
        smil_id = match.group(2)
        url = f"https://streaming.hrt.hr/webstream/smil:{smil_id}.smil/playlist.m3u8"
        pairs.append({'title': display_text, 'url': url})
        print(f"✅ '{display_text}' -> {url}")
    
    generate_tivimate_movies_m3u(pairs)  # Piše u hrt_enz.m3u !

def generate_tivimate_movies_m3u(streams):
    m3u = "#EXTM3U\n"
    m3u += '# TiviMate MOVIES - HRT ENZ VOD (prevodi unaprijed/unazad)\n\n'
    
    for s in streams:
        # **KLJUČNO**: group-title="Movies" za VOD sekciju + seeking
        extinf = f'#EXTINF:-1 tvg-type="video" tvg-name="{s["title"]}" tvg-logo="https://www.hrt.hr/favicon.ico" group-title="Movies",{s["title"]}'
        m3u += extinf + "\n"
        m3u += s['url'] + "\n\n"
    
    # Piše u tvoju datoteku hrt_enz.m3u
    with open('hrt_enz.m3u', 'w', encoding='utf-8') as f:
        f.write(m3u)
    
    print(f"✅ 🎬 {len(streams)} FILMOVA u hrt_enz.m3u")
    print("✅ group-title=\"Movies\" - TiviMate VOD + seeking!")

if __name__ == "__main__":
    scrape_hrt_enz()
