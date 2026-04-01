#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import os

def get_dates():
    today = datetime.now().strftime('%Y/%m/%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y/%m/%d')
    return [today, yesterday]

def scrape_hrt_enz():
    dates = get_dates()
    all_streams = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    for date in dates:
        print(f"Scraping {date}...")
        url = f"https://enz.hrt.hr/{date}/"
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Traži m3u8 linkove u stranici
            m3u8_links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.endswith('.m3u8'):
                    m3u8_links.append(href)
            
            # Traži embed/video tagove
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    m3u8_matches = re.findall(r'(https?://[^"\']+\.m3u8[^"\']*)', script.string)
                    m3u8_links.extend(m3u8_matches)
            
            # Ukloni duplikate
            m3u8_links = list(set(m3u8_links))
            
            for link in m3u8_links:
                # Izvuci naslov iz stranice ili URL-a
                title = f"HRT ENZ {date}"
                if '/' in link:
                    title = link.split('/')[-1].replace('.m3u8', '').replace('-', ' ').title()
                
                all_streams.append({
                    'url': link,
                    'title': title,
                    'date': date
                })
                
        except Exception as e:
            print(f"Greška za {date}: {e}")
    
    generate_m3u(all_streams)

def generate_m3u(streams):
    m3u_content = "#EXTM3U\n\n"
    
    for stream in streams:
        extinf = f'#EXTINF:-1 tvg-id="HRT_ENZ_{stream["date"]}" tvg-logo="https://www.hrt.hr/favicon.ico" group-title="HRT ENZ",HRT ENZ - {stream["title"]}'
        m3u_content += extinf + "\n"
        m3u_content += stream['url'] + "\n\n"
    
    with open('hrt_enz.m3u', 'w', encoding='utf-8') as f:
        f.write(m3u_content)
    
    print(f"✅ Generirano {len(streams)} streamova u hrt_enz.m3u")

if __name__ == "__main__":
    scrape_hrt_enz()
