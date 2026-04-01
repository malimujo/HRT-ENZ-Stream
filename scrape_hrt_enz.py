#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import re
import urllib.parse

def scrape_hrt_enz():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print("🔍 Pronalazim HRT ENZ videe...")
    
    # 1. Glavna stranica
    response = requests.get("https://enz.hrt.hr/", headers=headers, timeout=15)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    all_videos = []
    
    # 2. Pronađi SMIL/m3u8 linkove
    for script in soup.find_all('script'):
        if script.string:
            smil_ids = re.findall(r'smil:([a-zA-Z0-9]{10,})', script.string)
            for smil_id in smil_ids:
                m3u8_url = f"https://streaming.hrt.hr/webstream/smil:{smil_id}/playlist.m3u8"
                
                # TESTIRAJ i izvuci MP4 varijante!
                mp4_variants = extract_mp4_from_m3u8(m3u8_url)
                for mp4_url in mp4_variants:
                    all_videos.append({
                        'url': mp4_url,
                        'title': f"HRT ENZ - {smil_id[:8]}",
                        'type': 'mp4_vod'
                    })
                    print(f"✅ MP4 VOD: {mp4_url}")
    
    # 3. Direktni MP4 linkovi (VOD)
    for link in soup.find_all('a', href=True):
        href = link['href']
        if '.mp4' in href or '.mkv' in href:
            full_url = urllib.parse.urljoin("https://enz.hrt.hr/", href)
            all_videos.append({
                'url': full_url,
                'title': link.get_text(strip=True) or 'HRT ENZ Film',
                'type': 'mp4_direct'
            })
            print(f"✅ Direct MP4: {full_url}")
    
    unique_videos = remove_duplicates(all_videos)
    generate_movies_m3u(unique_videos)

def extract_mp4_from_m3u8(m3u8_url):
    """Izvući MP4 segmentne linkove iz m3u8 playliste"""
    try:
        resp = requests.get(m3u8_url, headers={'User-Agent': 'VLC/3.0.20'}, timeout=10)
        if resp.status_code != 200:
            return []
        
        mp4_links = re.findall(r'(https?://[^\s]+\.mp4(?:\?[^"\s]+)?)', resp.text)
        return list(set(mp4_links))  # ukloni duplikate
        
    except:
        return []

def remove_duplicates(videos):
    seen = set()
    unique = []
    for video in videos:
        if video['url'] not in seen:
            unique.append(video)
            seen.add(video['url'])
    return unique

def generate_movies_m3u(videos):
    if not videos:
        print("❌ Nema VOD videa!")
        with open('hrt_enz.m3u', 'w') as f:
            f.write("#EXTM3U\n# HRT ENZ Movies - Nema sadržaja\n")
        return
    
    m3u_content = "#EXTM3U\n\n"
    for i, video in enumerate(videos, 1):
        # KRITIČNO za Movies: statički MP4 + dug trajanje + movie tag
        extinf = f'#EXTINF:10800 movie="yes" tvg-id="HRT_ENZ_{i}" tvg-logo="https://www.hrt.hr/favicon.ico" group-title="Movies",🎬 HRT ENZ {i} - {video["title"]}'
        m3u_content += extinf + "\n"
        m3u_content += video['url'] + "\n\n"
    
    with open('hrt_enz.m3u', 'w', encoding='utf-8') as f:
        f.write(m3u_content)
    
    print(f"✅ 🎬 {len(videos)} MP4 VOD filmova za Movies!")

if __name__ == "__main__":
    scrape_hrt_enz()
