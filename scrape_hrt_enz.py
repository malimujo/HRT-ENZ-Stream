#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re

def scrape_hrt_enz():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print("🔍 Analiziram https://enz.hrt.hr/...")
    response = requests.get("https://enz.hrt.hr/", headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    all_streams = []
    
    # Traži sve m3u8 linkove na glavnoj stranici
    print("🔍 Tražim m3u8 linkove...")
    
    # 1. Anchor linkovi
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.endswith('.m3u8') or '.m3u8' in href:
            all_streams.append({
                'url': href if href.startswith('http') else f"https://enz.hrt.hr{href}",
                'title': link.get_text(strip=True) or 'HRT ENZ Stream',
                'date': 'danas'
            })
            print(f"✅ Anchor: {href}")
    
    # 2. Script tagovi (najčešće lokacija streamova)
    for script in soup.find_all('script'):
        if script.string:
            m3u8_matches = re.findall(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', script.string)
            for match in m3u8_matches:
                all_streams.append({
                    'url': match,
                    'title': 'HRT ENZ Live',
                    'date': 'danas'
                })
                print(f"✅ Script: {match}")
    
    # 3. Video tagovi
    for video in soup.find_all('video'):
        sources = video.find_all('source')
        for source in sources:
            src = source.get('src')
            if src and '.m3u8' in src:
                all_streams.append({
                    'url': src,
                    'title': 'HRT ENZ Video',
                    'date': 'danas'
                })
    
    # Ukloni duplikate
    seen_urls = set()
    unique_streams = []
    for stream in all_streams:
        if stream['url'] not in seen_urls:
            unique_streams.append(stream)
            seen_urls.add(stream['url'])
    
    generate_m3u(unique_streams)

def generate_m3u(streams):
    if not streams:
        print("❌ Nema pronađenih streamova!")
        with open('hrt_enz.m3u', 'w') as f:
            f.write("#EXTM3U\n# Nema HRT ENZ streamova\n")
        return
    
    m3u_content = "#EXTM3U\n\n"
    for stream in streams:
        extinf = f'#EXTINF:-1 tvg-id="HRT_ENZ" tvg-logo="https://www.hrt.hr/favicon.ico" group-title="Filmovi",HRT ENZ - {stream["title"]}'
        m3u_content += extinf + "\n"
        m3u_content += stream['url'] + "\n\n"
    
    with open('hrt_enz.m3u', 'w', encoding='utf-8') as f:
        f.write(m3u_content)
    
    print(f"✅ Spremljeno {len(streams)} streamova u hrt_enz.m3u")

if __name__ == "__main__":
    scrape_hrt_enz()
