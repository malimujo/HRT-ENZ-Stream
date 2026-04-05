#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

def scrape_hrt_enz():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print("🔍 Scraping https://enz.hrt.hr/ - prvih 10 m3u8 linkova...")
    response = requests.get("https://enz.hrt.hr/", headers=headers, timeout=15)
    
    # Pronađi SVE m3u8 linkove
    m3u8_urls = re.findall(r'(https?://[^\s\'\"<>]+\.m3u8[^\s\'\"<>]*)', response.text)
    m3u8_urls = list(set(m3u8_urls))[:10]  # Jedinstveni, prvih 10
    
    streams = []
    for i, url in enumerate(m3u8_urls, 1):
        title = f"HRT ENZ Stream {i} {datetime.now().strftime('%d-%m-%Y')}"
        streams.append({'title': title, 'url': url})
        print(f"✅ {i}. '{title}' -> {url}")
    
    generate_m3u(streams)

def generate_m3u(streams):
    m3u_content = "#EXTM3U\n\n"
    for stream in streams:
        extinf = f'#EXTINF:-1 tvg-id="HRT_ENZ" tvg-logo="https://www.hrt.hr/favicon.ico" group-title="HRT ENZ",{stream["title"]}'
        m3u_content += extinf + "\n"
        m3u_content += stream['url'] + "\n\n"
    
    with open('hrt_enz.m3u', 'w', encoding='utf-8') as f:
        f.write(m3u_content)
    
    print(f"✅ Spremljeno {len(streams)} streamova u hrt_enz.m3u")
    print("📺 Spremno za TiviMate!")

if __name__ == "__main__":
    scrape_hrt_enz()
