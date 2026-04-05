#!/usr/bin/env python3
import requests
import re

def scrape_hrt_enz():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print("🔍 Tražim HRT streaming smil playlist.m3u8 + displayText...")
    response = requests.get("https://enz.hrt.hr/", headers=headers, timeout=15)
    text = response.text
    
    # Pronađi PAROVE: displayText + njegov smil URL (redoslijedom pojavljivanja)
    pairs = []
    all_matches = list(re.finditer(r'"displayText"\s*:\s*"([^"]+)"(?=.*?https://streaming\.hrt\.hr/webstream/smil:([^\s\'\"<>]+?)\.smil/playlist\.m3u8)', text, re.DOTALL | re.IGNORECASE))
    
    for match in all_matches[:10]:  # prvih 10 parova
        display_text = match.group(1).strip()
        smil_id = match.group(2)
        url = f"https://streaming.hrt.hr/webstream/smil:{smil_id}.smil/playlist.m3u8"
        
        pairs.append({'title': display_text, 'url': url})
        print(f"✅ '{display_text}' -> {url}")
    
    generate_m3u(pairs)

def generate_m3u(streams):
    if not streams:
        print("❌ Nema parova!")
        return
    
    m3u = "#EXTM3U\n\n"
    for s in streams:
        extinf = f'#EXTINF:-1 tvg-id="HRT_ENZ" tvg-logo="https://www.hrt.hr/favicon.ico" group-title="HRT ENZ",{s["title"]}'
        m3u += extinf + "\n" + s['url'] + "\n\n"
    
    with open('hrt_enz.m3u', 'w', encoding='utf-8') as f:
        f.write(m3u)
    
    print(f"✅ {len(streams)} **TAČNIH** displayText + smil linkova!")

if __name__ == "__main__":
    scrape_hrt_enz()
