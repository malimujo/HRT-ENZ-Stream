#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import re

def scrape_hrt_enz_simple():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    print("🔍 https://enz.hrt.hr/...")
    resp = requests.get("https://enz.hrt.hr/", headers=headers, timeout=10)
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    streams = []
    
    # Pronađi SVE m3u8 (anchor, script, source)
    all_m3u8 = set()
    for tag in soup.find_all(string=re.compile(r'm3u8', re.I)):
        matches = re.findall(r'https?://[^\s\'\"<>]+m3u8[^\s\'\"<>]*', tag)
        all_m3u8.update(matches)
    
    for link in soup.find_all('a', href=re.compile(r'm3u8', re.I)):
        href = link['href']
        url = href if href.startswith('http') else 'https://enz.hrt.hr' + href
        all_m3u8.add(url)
    
    for source in soup.find_all('source', src=re.compile(r'm3u8', re.I)):
        all_m3u8.add(source['src'])
    
    # Za svaki m3u8 pronađi odgovarajući displayText/kategoriju
    for m3u8_url in all_m3u8:
        title = find_title_for_stream(soup, m3u8_url)
        streams.append({'url': m3u8_url, 'title': title})
        print(f"✅ '{title}' -> {m3u8_url}")
    
    generate_m3u(streams)

def find_title_for_stream(soup, m3u8_url):
    """Naziv iz displayText ili parent kategorije"""
    
    # 1. Traži data-display-text ili displayText u scriptu blizu
    display_elem = soup.find(attrs={'data-display-text': True}) or \
                   soup.find(text=re.compile(r'displayText', re.I))
    if display_elem:
        return display_elem.parent.get_text(strip=True)[:100] if display_elem.parent else 'HRT Stream'
    
    # 2. Najbliži h2/h3/p prije m3u8 mentiona
    scripts_with_url = soup.find_all('script', string=re.compile(re.escape(m3u8_url[:50])))
    for script in scripts_with_url:
        before = script.string[:script.string.find(m3u8_url[:50])][-200:]
        match = re.search(r'"([^"]+)"\s*,?\s*(url|src|href)', before)
        if match:
            return match.group(1)
    
    # 3. Parent kategorija (h2 prije linka)
    for link in soup.find_all('a', string=re.compile(r'm3u8', re.I)):
        if m3u8_url in link.get('href', ''):
            parent_h = link.find_parent(['h2', 'h3', 'div'])
            if parent_h:
                return parent_h.get_text(strip=True)[:100]
    
    return 'HRT ENZ Live'  # Default

def generate_m3u(streams):
    m3u = "#EXTM3U\n"
    for s in streams:
        extinf = f'#EXTINF:-1 group-title="HRT ENZ",{s["title"]}'
        m3u += extinf + "\n" + s['url'] + "\n\n"
    
    with open('hrt_enz.m3u', 'w', encoding='utf-8') as f:
        f.write(m3u)
    print(f"✅ {len(streams)} streamova sa **jedinstvenim nazivima**!")

if __name__ == "__main__":
    scrape_hrt_enz_simple()
