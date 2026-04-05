#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import json

def scrape_hrt_enz():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print("🔍 Analiziram https://enz.hrt.hr/...")
    response = requests.get("https://enz.hrt.hr/", headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    all_streams = []
    
    # 1. Anchor linkovi sa displayText fallback
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.endswith('.m3u8') or '.m3u8' in href:
            title = link.get('data-display-text') or link.get_text(strip=True) or 'HRT ENZ Stream'
            all_streams.append({
                'url': href if href.startswith('http') else f"https://enz.hrt.hr{href}",
                'title': title,
                'date': 'danas'
            })
            print(f"✅ Anchor: {title} -> {href}")
    
    # 2. Script tagovi - JSON sa displayText
    for script in soup.find_all('script'):
        if script.string:
            # Regex za m3u8
            m3u8_matches = re.findall(r'(https?://[^\s"\'<>]+?\.m3u8[^\s"\'<>]*)', script.string)
            for match in m3u8_matches:
                # Pokušaj naći displayText u kontekstu
                script_text = script.string
                display_match = re.search(r'"displayText"\s*:\s*"([^"]+)"', script_text)
                title = display_match.group(1) if display_match else 'HRT ENZ Live'
                # Čišćenje title-a (ukloni nepotrebno)
                title = re.sub(r'<[^>]+>', '', title).strip()
                all_streams.append({
                    'url': match,
                    'title': title,
                    'date': 'danas'
                })
                print(f"✅ Script JSON: {title} -> {match}")
            
            # JSON objekti u scriptu
            json_matches = re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', script.string, re.DOTALL)
            for json_str in json_matches:
                try:
                    data = json.loads(json_str)
                    if isinstance(data, dict):
                        # Traži displayText i m3u8 u istom objektu ili arrayu
                        display_text = data.get('displayText') or data.get('title') or data.get('name', '')
                        url = data.get('url') or data.get('streamUrl') or data.get('src', '')
                        if url and '.m3u8' in url:
                            all_streams.append({
                                'url': url,
                                'title': display_text or 'HRT ENZ Live',
                                'date': data.get('date', 'danas')
                            })
                            print(f"✅ JSON displayText: {display_text} -> {url}")
                except json.JSONDecodeError:
                    pass
    
    # 3. Video tagovi
    for video in soup.find_all('video'):
        sources = video.find_all('source')
        for source in sources:
            src = source.get('src') or source.get('data-src')
            if src and '.m3u8' in src:
                title = source.get('title') or source.get('data-display-text') or video.get('title') or 'HRT ENZ Video'
                all_streams.append({
                    'url': src if src.startswith('http') else f"https://enz.hrt.hr{src}",
                    'title': title,
                    'date': 'danas'
                })
                print(f"✅ Video: {title} -> {src}")
    
    # Ukloni duplikate po URL-u
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
        # Dodaj datum u title ako postoji, npr. "Dnevnik 3 04-04-2026"
        full_title = f"{stream['title']} {stream.get('date', '')}".strip()
        extinf = f'#EXTINF:-1 tvg-id="HRT_ENZ" tvg-logo="https://www.hrt.hr/favicon.ico" group-title="HRT ENZ",{full_title}'
        m3u_content += extinf + "\n"
        m3u_content += stream['url'] + "\n\n"
    
    with open('hrt_enz.m3u', 'w', encoding='utf-8') as f:
        f.write(m3u_content)
    
    print(f"✅ Spremljeno {len(streams)} streamova u hrt_enz.m3u")

if __name__ == "__main__":
    scrape_hrt_enz()
