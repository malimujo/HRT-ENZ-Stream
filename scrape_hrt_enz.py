#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import os

def scrape_hrt_enz():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # 1. Pronađi sitemap ili arhivu
    print("🔍 Tražim HRT ENZ arhivu...")
    response = requests.get("https://enz.hrt.hr/", headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    all_streams = []
    
    # 2. Traži datumske linkove u arhivi (posljednje 2 dana)
    date_links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        # Pattern za datume: /2026/04/01/ ili datum u textu
        if re.search(r'/20\d{2}/\d{2}/\d{2}/', href) or '2026' in href:
            date_links.append(href)
    
    # 3. Za svaki datum, traži m3u8
    for link in date_links[-4:]:  # zadnje 4 stranice
        try:
            print(f"Scraping {link}...")
            full_url = f"https://enz.hrt.hr{link}" if link.startswith('/') else link
            resp = requests.get(full_url, headers=headers, timeout=10)
            
            soup_page = BeautifulSoup(resp.text, 'html.parser')
            
            # Pronađi m3u8 linkove
            m3u8_links = []
            for a in soup_page.find_all('a', href=True):
                if a['href'].endswith('.m3u8'):
                    m3u8_links.append(a['href'])
            
            # U script tagovima
            for script in soup_page.find_all('script'):
                if script.string:
                    matches = re.findall(r'(https?://[^\s"\']+\.m3u8)', script.string)
                    m3u8_links.extend(matches)
            
            m3u8_links = list(set(m3u8_links))
            
            for m3u8 in m3u8_links:
                title = link.split('/')[-2] if '/' in link else "HRT ENZ"
                all_streams.append({
                    'url': m3u8,
                    'title': f"{title} - Stream",
                    'date': link
                })
                print(f"✅ {m3u8}")
                
        except Exception as e:
            print(f"⚠️ Greška {link}: {e}")
    
    generate_m3u(all_streams)

def generate_m3u(streams):
    if not streams:
        print("❌ Nema streamova!")
        with open('hrt_enz.m3u', 'w') as f:
            f.write("#EXTM3U\n# Nema HRT ENZ streamova\n")
        return
    
    m3u_content = "#EXTM3U\n\n"
    for stream in streams:
        extinf = f'#EXTINF:-1 tvg-id="HRT_ENZ" tvg-logo="https://www.hrt.hr/favicon.ico" group-title="HRT ENZ",HRT ENZ - {stream["title"]}'
        m3u_content += extinf + "\n" + stream['url'] + "\n\n"
    
    with open('hrt_enz.m3u', 'w', encoding='utf-8') as f:
        
