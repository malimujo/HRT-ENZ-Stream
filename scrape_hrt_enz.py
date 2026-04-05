#!/usr/bin/env python3
import requests
import re

def scrape_hrt_enz():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print("🔍 TiviMate FILMOVI - HRT ENZ VOD...")
    response = requests.get("https://enz.hrt.hr/", headers=headers, timeout=15)
    text = response.text
    
    # TIVIMATE: group-title="Movies" za VOD/filmove + seeking
    pairs = []
    matches = list(re.finditer(r'"displayText"\s*:\s*"([^"]+)"(?=.*?https://streaming\.hrt\.hr/webstream/smil:([^\s\'\"<>]+?)\.smil/playlist\.m3u8)', text, re.DOTALL | re.IGNORECASE))
    
    for match in matches[:15]:  # do 15 filmova
        display_text = match.group(1).strip()
        smil_id = match.group(2)
        url = f"https://streaming.hrt.hr/webstream/smil:{smil_id}.smil/playlist.m3u8"
        
        pairs.append({'title': display_text, 'url': url})
        print(f"✅ FILM: '{display_text}' -> {url}")
    
    generate_tivimate_vod_m3u(pairs)

def generate_tivimate_vod_m3u(streams):
    if not streams:
        print("❌ Nema filmova!")
        return
    
    m3u = "#EXTM3U\n"
    m3u += '# Playlist za TiviMate MOVIES - HRT ENZ VOD (prevoditi unaprijed/unazad)\n\n'
    
    for s in streams:
        # TIVIMATE MOVIES: group-title="Movies" + tvg-name za VOD
        extinf = f'#EXTINF:-1 tvg-name="{s["title"]}" tvg-logo="https://www.hrt.hr/favicon.ico" group-title="Movies",{s["title"]}'
        m3u += extinf + "\n"
        m3u += s['url'] + "\n\n"
    
    filename = 'hrt_enz_movies.m3u'  # posebno za Movies
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(m3u)
    
    print(f"✅ 🎬 {len(streams)} FILMOVA u '{filename}'")
    print("📱 TiviMate: Settings > Playlists > Add M3U > uvozi hrt_enz_movies.m3u")
    print("🎛️ Movies sekcija ← seeking (FF/RW) radi na HLS VOD!")

if __name__ == "__main__":
    scrape_hrt_enz()
