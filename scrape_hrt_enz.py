#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import re
import urllib.parse

def scrape_hrt_enz():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print("🔍 Analiziram https://enz.hrt.hr/...")
    response = requests.get("https://enz.hrt.hr/", headers=headers, timeout=15)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    all_videos = []
    
    # 1. Pronađi ispravne HRT streaming linkove
    print("🔍 Tražim radne video linkove...")
    
    for script in soup.find_all('script'):
        if script.string:
            # ISPRAVNO parsiranje SMIL: smil:ID → https://streaming.hrt.hr/webstream/smil:ID/playlist.m3u8
            smil_ids = re.findall(r'smil:([a-zA-Z0-9]+)', script.string)
            for smil_id in smil_ids:
                m3u8_url = f"https://streaming.hrt.hr/webstream/smil:{smil_id}/playlist.m3u8"
                
                all_videos.append({
                    'url': m3u8_url,
                    'title': f"HRT ENZ - Epizoda {smil_id[:8]}",
                    'type': 'hrt_smil'
                })
                print(f"✅ HRT SMIL: {m3u8_url}")
    
    # 2. Direktni m3u8/mp4 linkovi
    for link in soup.find_all('a', href=True):
        href = link['href']
        if '.m3u8' in href or '.mp4' in href:
            # Popravi relativne linkove
            full_url = urllib.parse.urljoin("https://enz.hrt.hr/", href)
            all_videos.append({
                'url': full_url,
                'title': link.get_text(strip=True) or 'HRT ENZ Stream',
                'type': 'direct'
            })
            print(f"✅ Direct: {full_url}")
    
    # 3. Video tagovi
    for video in soup.find_all('video'):
        src = video.get('src') or video.get('data-src')
        if src and ('.m3u8' in src or '.mp4' in src):
            full_url = urllib.parse.urljoin("https://enz.hrt.hr/", src)
            all_videos.append({
                'url': full_url,
                'title': video.get('title') or 'HRT ENZ Video',
                'type': 'video_tag'
            })
    
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
        # FALLBACK - dodaj poznate HRT streamove
        print("❌ Nema streamova, koristim fallback...")
        fallback = [
            {
                'url': 'https://playerservices.streamtheworld.com/api/livestream-redirect/PROGRAM1.mp3',
                'title': 'HRT HR1',
                'type': 'radio'
            }
        ]
        with open('hrt_enz.m3u', 'w') as f:
            f.write("#EXTM3U\n")
            for fb in fallback:
                f.write(f'#EXTINF:-1 tvg-id="HRT1" group-title="Movies",HRT HR1 Fallback\n')
                f.write(fb['url'] + "\n\n")
        return
    
    m3u_content = "#EXTM3U\n\n"
    for i, video in enumerate(videos, 1):
        # Movies format za TiviMate
        duration = "7200"  # 2h
        extinf = f'#EXTINF:{duration} tvg-id="HRT_ENZ_{i}" tvg-logo="https://www.hrt.hr/favicon.ico" group-title="Movies",HRT ENZ {i} - {video["title"]}'
        m3u_content += extinf + "\n"
        m3u_content += video['url'] + "\n\n"
    
    with open('hrt_enz.m3u', 'w', encoding='utf-8') as f:
        f.write(m3u_content)
    
    print(f"✅ 🎬 {len(videos)} FILMOVA za Movies rubriku!")

if __name__ == "__main__":
    scrape_hrt_enz()
