"""
Earth Engine Data Catalog Crawler (Selenium + Edge)
--------------------------------------------------
Requirements:
    pip install selenium beautifulsoup4 requests
    Download and install Microsoft Edge WebDriver (msedgedriver) matching your Edge version:
    https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/
    Ensure msedgedriver.exe is in your PATH or same directory as this script.
"""
import os
import time
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By

BASE_URL = "https://developers.google.com/earth-engine/datasets/catalog"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; EarthEngineCrawler/1.0)"}
OUTPUT_JSON = "satellite_catalog.json"
IMAGES_DIR = "satellite_thumbnails"

os.makedirs(IMAGES_DIR, exist_ok=True)

def get_rendered_html(url):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1920,1080')
    driver = webdriver.Edge(options=options)
    driver.get(url)
    # Wait for cards to load
    time.sleep(5)
    html = driver.page_source
    driver.quit()
    return html

def download_image(url, out_dir):
    if not url:
        return None
    parsed = urlparse(url)
    fname = os.path.basename(parsed.path)
    out_path = os.path.join(out_dir, fname)
    try:
        r = requests.get(url, headers=HEADERS, stream=True, verify=False)
        r.raise_for_status()
        with open(out_path, 'wb') as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
        return out_path
    except Exception as e:
        print(f"[WARN] Could not download {url}: {e}")
        return None

def parse_dataset_card(card):
    title = card.find('div', class_='devsite-article-title')
    title = title.get_text(strip=True) if title else None
    desc = card.find('div', class_='devsite-article-body')
    desc = desc.get_text(strip=True) if desc else None
    thumb = card.find('img')
    thumb_url = urljoin(BASE_URL, thumb['src']) if thumb and thumb.has_attr('src') else None
    detail_link = card.find('a', class_='devsite-article-title-link')
    detail_url = urljoin(BASE_URL, detail_link['href']) if detail_link and detail_link.has_attr('href') else None
    tags = [t.get_text(strip=True) for t in card.find_all('span', class_='devsite-chip-label')]
    return {
        'title': title,
        'description': desc,
        'thumbnail_url': thumb_url,
        'detail_url': detail_url,
        'tags': tags
    }

def parse_detail_page(url):
    html = get_rendered_html(url)
    soup = BeautifulSoup(html, "html.parser")
    info = {}
    desc = soup.find('div', class_='devsite-article-body')
    if desc:
        info['full_description'] = desc.get_text("\n", strip=True)
    meta = {}
    for row in soup.find_all('tr'):
        cols = row.find_all('td')
        if len(cols) == 2:
            k = cols[0].get_text(strip=True)
            v = cols[1].get_text(strip=True)
            meta[k] = v
    if meta:
        info['metadata'] = meta
    prov = soup.find('a', class_='devsite-link')
    if prov:
        info['provider'] = prov.get_text(strip=True)
    return info

def crawl_all():
    url = BASE_URL
    all_datasets = []
    seen = set()
    while url:
        print(f"[INFO] Crawling: {url}")
        html = get_rendered_html(url)
        soup = BeautifulSoup(html, "html.parser")
        cards = soup.find_all('article', class_='devsite-article')
        print(f"[INFO] Found {len(cards)} dataset cards on this page.")
        if cards:
            print("[DEBUG] First card HTML:\n", cards[0].prettify()[:2000])
        for card in cards:
            data = parse_dataset_card(card)
            if not data['detail_url'] or data['detail_url'] in seen:
                continue
            seen.add(data['detail_url'])
            img_path = download_image(data['thumbnail_url'], IMAGES_DIR)
            data['thumbnail_path'] = img_path
            if data['detail_url']:
                try:
                    detail_info = parse_detail_page(data['detail_url'])
                    data.update(detail_info)
                except Exception as e:
                    print(f"[WARN] Could not parse detail page {data['detail_url']}: {e}")
            all_datasets.append(data)
            time.sleep(0.5)
        # Find next page
        next_btn = soup.find('a', {'aria-label': 'Next'})
        if next_btn and next_btn.has_attr('href'):
            url = urljoin(BASE_URL, next_btn['href'])
        else:
            url = None
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(all_datasets, f, ensure_ascii=False, indent=2)
    print(f"[DONE] Crawled {len(all_datasets)} datasets. Data saved to {OUTPUT_JSON}")

if __name__ == "__main__":
    crawl_all() 