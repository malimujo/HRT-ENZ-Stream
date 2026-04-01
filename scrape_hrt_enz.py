#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import re

def scrape_hrt_enz():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print("🔍 Analiziram https://enz.hrt.hr/...")
    response = requests.get("https://enz.hrt.hr/", headers=headers, timeout=15)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    all_videos = []
    
    # 1. Pronađi SMIL playlistove (HRT format)
    print("🔍 Tražim SMIL i video linkove...")
    for script in soup.find_all('script'):
        if script.string:
            # HRT SMIL: smil:ID.smil/playlist.m3u8/mp4
            smil_matches = re.findall(r'(streaming\.hrt\.hr/webstream/smil:[^\s"\']+)', script.string)
            for smil in smil_matches:
                # Testiraj m3u8 (radi) i mp4 (možda)
                m3u8_url = f"https://streaming.hrt.hr/webstream/{smil}/playlist.m3u8"
                mp4_url = f"https://streaming.hrt.hr/webstream/{smil}/playlist.mp4"
                
                all_videos.append({
                    'url': m3u8_url,  # Koristi m3u8 (radi!)
                    'title': f"HRT ENZ - {smil.split(':')[1]}",
                    'type': 'm3u8'
                })
                print(f"✅ SMIL m3u8: {m3u8_url}")
    
    # 2. Direktni video linkovi
    for link in soup.find_all('a', href=True):
        href = link['href']
        if any(ext in href for ext in ['.m3u8', '.mp4', '.mkv']):
            full_url = href if href.startswith('http') else f"https://enz.hrt.hr{href}"
            all_videos.append({
                'url': full_url,
                'title': link.get_text(strip=True) or 'HRT ENZ Video',
                'type': 'direct'
            })
            print(f"✅ Direct: {full_url}")
    
    # Ukloni duplikate
    seen = set()
    unique = []
    for video in all_videos:
        if video['url'] not in seen:
            unique.append(video)
            seen.add(video['url'])
    
    generate_movies_m3u(unique)

def generate_movies_m3u(videos):
    if not videos:
        print("❌ Nema video sadržaja!")
        with open('hrt_enz.m3u', 'w') as f:
            f.write("#EXTM3U\n# HRT ENZ - Nema filmova\n")
        return
    
    m3u_content = "#EXTM3U\n\n"
    for i, video in enumerate(videos, 1):
        # TiviMate MOVIES format
        duration = "7200"  # 2h = film
        extinf = f'#EXTINF:{duration} tvg-id="HRT_ENZ_{i}" tvg-logo="https://www.hrt.hr/favicon.ico" group-title="Movies",HRT ENZ {i} - {video["title"]}'
        m3u_content += extinf + "\n"
        m3u_content += video['url'] + "\n\n"
    
    with open('hrt_enz.m3u', 'w', encoding='utf-8') as f:
        f.write(m3u_content)
    
    print(f"✅ 🎬 {len(videos)} FILMOVA za TiviMate Movies!")

if __name__ == "__main__":
    scrape_hrt_enz()
