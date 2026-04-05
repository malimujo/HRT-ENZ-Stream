#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import re
import json

def scrape_hrt_enz():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    print("🔍 https://enz.hrt.hr/...")
    resp = requests.get("https://enz.hrt.hr/", headers=headers, timeout=10)
    
    streams = []
    
    # TRAŽI "displayText":"Naziv Datum" + m3u8 URL
    pattern = r'"displayText"\s*:\s*"([^"]+)"[^}]*?(https://streaming\.hrt\.hr/webstream/smil:[^\'\"\s]+?/playlist\.m3u8)'
    
    matches = re.findall(pattern, resp.text, re.DOTALL | re.IGNORECASE)
    
    for display_text, m3u8_url in matches:
        streams.append({'title': display_text, 'url': m3u8_url})
        print(f"✅ '{display_text}' -> {m3u8_url}")
    
    generate_m3u(streams)

def generate_m3u(streams):
    if not streams:
        print("❌ Nema displayText + m3u8 parova!")
        return
    
    m3u = "#EXTM3U\n\n"
    for s in streams:
        extinf = f'#EXTINF:-1 group-title="HRT ENZ",{s["title"]}'
        m3u += extinf + "\n" + s['url'] + "\n\n"
    
    with open('hrt_enz.m3u', 'w', encoding='utf-8') as f:
        f.write(m3u)
    
    print(f"✅ {len(streams)} streamova!")

if __name__ == "__main__":
    scrape_hrt_enz()
