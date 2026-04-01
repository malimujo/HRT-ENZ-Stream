#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import re

def scrape_hrt_enz():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print("🔍 Analiziram https://enz.hrt.hr/...")
    response = requests.get("https://enz.hrt.hr/", headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    all_streams = []
    
    # 1. Anchor linkovi (.m3u8, .mp4, .mkv)
    print("🔍 Tražim video linkove...")
    for link in soup.find_all('a', href=True):
        href = link['href']
        if any(ext in href.lower() for ext in ['.m3u8', '.mp4', '.mkv', '.mov']):
            full_url = href if href.startswith('http') else f"https://enz.hrt.hr{href}"
            all_streams.append({
                'url': full_url.replace('.m3u8', '.mp4'),  # m3u8 → mp4 za Movies
                'title': link.get_text(strip=True) or 'HRT ENZ Film',
                'date': 'enz.hrt.hr'
            })
            print(f"✅ Anchor: {full_url}")
    
    # 2. Script tagovi (najčešće streamovi)
    for script in soup.find_all('script'):
        if script.string:
            # m3u8, mp4 linkovi u JavaScriptu
            matches = re.findall(r'(https?://[^\s"\']+\.(?:m3u8|mp4|mkv|mov)[^\s"\']*)', script.string)
            for match in matches:
                movie_url = match.replace('.m3u8', '.mp4')
                all_streams.append({
                    'url': movie_url,
                    'title': 'HRT ENZ Movie',
                    'date': 'script'
                })
                print(f"✅ Script: {movie_url}")
    
    # 3. Video/source tagovi
    for video in soup.find_all('video'):
        sources = video.find_all('source')
        for source in sources:
            src = source.get('src') or source.get('data-src')
            if src and any(ext in src.lower() for ext in ['.m3u8', '.mp4', '.mkv']):
                movie_url = src.replace('.m3u8', '.mp4')
                all_streams.append({
                    'url': movie_url,
                    'title': video.get('title') or 'HRT ENZ Video',
                    'date': 'video'
                })
    
    # Ukloni duplikate
    seen = set()
    unique = []
    for stream in all_streams:
        if stream['url'] not in seen:
            unique.append(stream)
            seen.add(stream['url'])
    
    generate_movies_m3u(unique)

def generate_movies_m3u(streams):
    if not streams:
        print("❌ Nema video sadržaja!")
        with open('hrt_enz.m3u', 'w') as f:
            f.write("#EXTM3U\n# HRT ENZ - Nema filmova\n")
        return
    
    m3u_content = "#EXTM3U\n\n"
    for i, stream in enumerate(streams, 1):
        # MOVIES format za TiviMate
        duration = "7200"  # 2 sata (dug sadržaj = Movies)
        extinf = f'#EXTINF:{duration} movie="yes" tvg-id="HRT_ENZ_{i}" tvg-logo="https://www.hrt.hr/favicon.ico" group-title="Movies",HRT ENZ - {stream["title"]}'
        m3u_content += extinf + "\n"
        m3u_content += stream['url'] + "\n\n"
    
    with open('hrt_enz.m3u', 'w', encoding='utf-8') as f:
        f.write(m3u_content)
    
    print(f"✅ 🎬 {len(streams)} FILMOVA u Movies grupi!")

if __name__ == "__main__":
    scrape_hrt_enz()
