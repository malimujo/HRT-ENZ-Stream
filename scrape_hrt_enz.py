#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import re

def scrape_hrt_enz():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print("🔍 Scraping https://enz.hrt.hr/ za displayText + m3u8 parove...")
    response = requests.get("https://enz.hrt.hr/", headers=headers, timeout=15)
    response.raise_for_status()
    
    text = response.text
    
    # Regex: "displayText":"Naziv Datum" ... m3u8 URL
    pattern = r'"displayText"\s*:\s*"([^"]+)"[^}]*?(https://streaming\.hrt\.hr/webstream/smil:[^\s\'\"<>]+?/playlist\.m3u8)'
    matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
    
    streams = []
    for display_text, m3u8_url in matches:
        streams.append({
            'title': display_text.strip(),
            'url': m3u8_url.strip()
        })
        print(f"✅ '{display_text.strip()}' -> {m3u8_url.strip()}")
    
    generate_m3u(streams)

def generate_m3u(streams):
    if not streams:
        print("❌ Nema pronađenih displayText + m3u8 parova!")
        with open('hrt_enz.m3u', 'w') as f:
            f.write("#EXTM3U\n# Nema HRT ENZ emisija\n")
        return
    
    m3u_content = "#EXTM3U\n\n"
    for stream in streams:
        extinf = f'#EXTINF:-1 tvg-id="HRT_ENZ" tvg-logo="https://www.hrt.hr/favicon.ico" group-title="HRT ENZ",{stream["title"]}'
        m3u_content += extinf + "\n"
        m3u_content += stream['url'] + "\n\n"
    
    with open('hrt_enz.m3u', 'w', encoding='utf-8') as f:
        f.write(m3u_content)
    
    print(f"✅ Spremljeno {len(streams)} emisija u hrt_enz.m3u")
    print("📺 Spreman za TiviMate!")

if __name__ == "__main__":
    scrape_hrt_enz()
