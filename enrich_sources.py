#!/usr/bin/env python3
"""
Enrich KorbanMBG data by scraping additional sources.
Targets: Kompas, CNN Indonesia, Tempo, Republika, media lokal
Uses different search approach to avoid blocks.
"""
import json
import os
import re
import time
import requests
import psycopg2
from datetime import datetime
from bs4 import BeautifulSoup

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': os.environ.get('DB_PASS', ''),
    'dbname': 'korbanmbg',
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'id-ID,id;q=0.9,en;q=0.5',
}

session = requests.Session()
session.headers.update(HEADERS)


def scrape_kompas():
    """Scrape Kompas.com search"""
    articles = []
    keywords = ['keracunan+MBG', 'keracunan+makan+bergizi+gratis']

    for kw in keywords:
        for page in range(1, 6):
            url = f"https://search.kompas.com/search/?q={kw}&per=10&page={page}"
            try:
                resp = session.get(url, timeout=15)
                if resp.status_code != 200:
                    print(f"  Kompas {kw} page {page}: HTTP {resp.status_code}")
                    continue

                soup = BeautifulSoup(resp.text, 'lxml')
                items = soup.select('.article__list, .gsc-webResult')

                for item in items:
                    link = item.select_one('a.article__link, a.gs-title')
                    if not link:
                        continue
                    href = link.get('href', '')
                    if not href or 'kompas.com' not in href:
                        continue

                    title = link.get_text(strip=True)
                    if not title or len(title) < 15:
                        continue

                    date_el = item.select_one('.article__date, .gsc-url-top')
                    date_text = date_el.get_text(strip=True) if date_el else ''

                    articles.append({
                        'title': title,
                        'url': href,
                        'date_text': date_text,
                        'source': 'kompas.com',
                    })

                time.sleep(2)
            except Exception as e:
                print(f"  Kompas error: {e}")
                continue

    return articles


def scrape_cnnindonesia():
    """Scrape CNN Indonesia search"""
    articles = []
    keywords = ['keracunan+MBG', 'keracunan+makan+bergizi']

    for kw in keywords:
        for page in range(1, 4):
            url = f"https://www.cnnindonesia.com/search?query={kw}&page={page}"
            try:
                resp = session.get(url, timeout=15)
                if resp.status_code != 200:
                    print(f"  CNN {kw} page {page}: HTTP {resp.status_code}")
                    continue

                soup = BeautifulSoup(resp.text, 'lxml')
                items = soup.select('article, .list-content__item, div[data-testid]')

                for item in items:
                    link = item.select_one('a[href*="cnnindonesia.com"]')
                    if not link:
                        continue
                    href = link.get('href', '')
                    title_el = item.select_one('h2, h3, .title')
                    title = title_el.get_text(strip=True) if title_el else link.get_text(strip=True)

                    if not title or len(title) < 15:
                        continue

                    articles.append({
                        'title': title,
                        'url': href,
                        'date_text': '',
                        'source': 'cnnindonesia.com',
                    })

                time.sleep(2)
            except Exception as e:
                print(f"  CNN error: {e}")
                continue

    return articles


def scrape_tempo():
    """Scrape Tempo.co search"""
    articles = []
    url = "https://www.tempo.co/search?q=keracunan+MBG"
    try:
        resp = session.get(url, timeout=15)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'lxml')
            items = soup.select('article, .card-box, .tempo-search-result')

            for item in items:
                link = item.select_one('a[href*="tempo.co"]')
                if not link:
                    continue
                href = link.get('href', '')
                title = link.get_text(strip=True)
                if title and len(title) > 15:
                    articles.append({
                        'title': title,
                        'url': href,
                        'date_text': '',
                        'source': 'tempo.co',
                    })
        else:
            print(f"  Tempo: HTTP {resp.status_code}")
    except Exception as e:
        print(f"  Tempo error: {e}")

    return articles


def scrape_republika():
    """Scrape Republika search"""
    articles = []
    url = "https://www.republika.co.id/search/keracunan%20MBG"
    try:
        resp = session.get(url, timeout=15)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'lxml')
            items = soup.select('.txt-oev-3, article, .list-content')

            for item in items:
                link = item.select_one('a[href*="republika.co.id"]')
                if not link:
                    continue
                href = link.get('href', '')
                if not href.startswith('http'):
                    href = 'https://www.republika.co.id' + href
                title = link.get_text(strip=True)
                if title and len(title) > 15:
                    articles.append({
                        'title': title,
                        'url': href,
                        'date_text': '',
                        'source': 'republika.co.id',
                    })
        else:
            print(f"  Republika: HTTP {resp.status_code}")
    except Exception as e:
        print(f"  Republika error: {e}")

    return articles


def scrape_liputan6():
    """Scrape Liputan6 search"""
    articles = []
    for page in range(1, 4):
        url = f"https://www.liputan6.com/search?q=keracunan+MBG&page={page}"
        try:
            resp = session.get(url, timeout=15)
            if resp.status_code != 200:
                print(f"  Liputan6 page {page}: HTTP {resp.status_code}")
                continue

            soup = BeautifulSoup(resp.text, 'lxml')
            items = soup.select('article, .articles--iridescent-list--item')

            for item in items:
                link = item.select_one('a[href*="liputan6.com"]')
                if not link:
                    continue
                href = link.get('href', '')
                title_el = item.select_one('h4, h3, .articles--iridescent-list--text-item__title')
                title = title_el.get_text(strip=True) if title_el else link.get_text(strip=True)
                if title and len(title) > 15:
                    articles.append({
                        'title': title,
                        'url': href,
                        'date_text': '',
                        'source': 'liputan6.com',
                    })

            time.sleep(2)
        except Exception as e:
            print(f"  Liputan6 error: {e}")
            continue

    return articles


def parse_date_from_url(url):
    """Try to extract date from URL pattern like /2025/09/15/..."""
    m = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', url)
    if m:
        try:
            return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3))).date()
        except:
            pass
    # Try pattern like /d-7654321 (detik) or /20250915 (kompas)
    m = re.search(r'/(\d{4})(\d{2})(\d{2})', url)
    if m:
        try:
            return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3))).date()
        except:
            pass
    return None


def extract_victim_count(title):
    t = title.lower()
    matches = re.findall(r'(\d[\d.]*)\s*(?:siswa|orang|korban|anak|murid|santri|balita|warga|pelajar)', t)
    matches2 = re.findall(r'(?:jadi|capai|mencapai|tembus|sebanyak|total)\s+(\d[\d.]*)', t)
    nums = []
    for m in matches + matches2:
        try:
            n = int(m.replace('.', ''))
            if 2 < n < 5000:
                nums.append(n)
        except:
            pass
    return max(nums) if nums else 0


LOCATION_MAP = {
    'bandung barat': ('Bandung Barat', 'Jawa Barat'),
    'kbb': ('Bandung Barat', 'Jawa Barat'),
    'cipongkor': ('Bandung Barat', 'Jawa Barat'),
    'cisarua': ('Bandung Barat', 'Jawa Barat'),
    'garut': ('Garut', 'Jawa Barat'),
    'tasikmalaya': ('Tasikmalaya', 'Jawa Barat'),
    'ciamis': ('Ciamis', 'Jawa Barat'),
    'sumedang': ('Sumedang', 'Jawa Barat'),
    'cianjur': ('Cianjur', 'Jawa Barat'),
    'sukabumi': ('Sukabumi', 'Jawa Barat'),
    'bogor': ('Bogor', 'Jawa Barat'),
    'bandung': ('Bandung', 'Jawa Barat'),
    'jabar': ('', 'Jawa Barat'),
    'klaten': ('Klaten', 'Jawa Tengah'),
    'demak': ('Demak', 'Jawa Tengah'),
    'kudus': ('Kudus', 'Jawa Tengah'),
    'rembang': ('Rembang', 'Jawa Tengah'),
    'grobogan': ('Grobogan', 'Jawa Tengah'),
    'jateng': ('', 'Jawa Tengah'),
    'surabaya': ('Surabaya', 'Jawa Timur'),
    'mojokerto': ('Mojokerto', 'Jawa Timur'),
    'kediri': ('Kediri', 'Jawa Timur'),
    'tulungagung': ('Tulungagung', 'Jawa Timur'),
    'bojonegoro': ('Bojonegoro', 'Jawa Timur'),
    'lamongan': ('Lamongan', 'Jawa Timur'),
    'jombang': ('Jombang', 'Jawa Timur'),
    'jatim': ('', 'Jawa Timur'),
    'jakarta': ('', 'DKI Jakarta'),
    'meruya': ('Jakarta Barat', 'DKI Jakarta'),
    'bantul': ('Bantul', 'DI Yogyakarta'),
    'gunungkidul': ('Gunungkidul', 'DI Yogyakarta'),
    'tts': ('TTS', 'NTT'),
    'kupang': ('Kupang', 'NTT'),
    'manggarai': ('Manggarai Barat', 'NTT'),
    'sumba': ('Sumba', 'NTT'),
    'ntt': ('', 'NTT'),
    'lombok': ('Lombok', 'NTB'),
    'ntb': ('', 'NTB'),
    'ketapang': ('Ketapang', 'Kalimantan Barat'),
    'landak': ('Landak', 'Kalimantan Barat'),
    'kalbar': ('', 'Kalimantan Barat'),
    'buol': ('Buol', 'Sulawesi Tengah'),
    'banggai': ('Banggai Kepulauan', 'Sulawesi Tengah'),
    'bangkep': ('Banggai Kepulauan', 'Sulawesi Tengah'),
    'sulteng': ('', 'Sulawesi Tengah'),
    'buton': ('Buton', 'Sulawesi Tenggara'),
    'kolaka': ('Kolaka', 'Sulawesi Tenggara'),
    'lampung': ('Lampung', 'Lampung'),
    'dairi': ('Dairi', 'Sumatera Utara'),
    'agam': ('Agam', 'Sumatera Barat'),
    'gorontalo': ('Gorontalo', 'Gorontalo'),
    'tomohon': ('Tomohon', 'Sulawesi Utara'),
}


def extract_location(title):
    t = title.lower()
    for key in sorted(LOCATION_MAP.keys(), key=len, reverse=True):
        if key in t:
            return LOCATION_MAP[key]
    return ('', '')


def is_relevant(title):
    t = title.lower()
    relevant_kw = ['keracunan', 'korban', 'sakit', 'diare', 'muntah', 'rawat', 'mbg', 'makan bergizi']
    return any(kw in t for kw in relevant_kw) and 'mbg' in t


def main():
    print(f"[{datetime.now().isoformat()}] Enrichment scraper starting...")

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Get existing URLs
    cur.execute("SELECT source_url FROM incidents WHERE source_url IS NOT NULL")
    existing_urls = set(row[0] for row in cur.fetchall())
    print(f"  Existing URLs: {len(existing_urls)}")

    # Get province/district IDs
    cur.execute("SELECT id, name FROM provinces")
    province_ids = {row[1]: row[0] for row in cur.fetchall()}
    cur.execute("SELECT d.id, d.name, p.name FROM districts d JOIN provinces p ON d.province_id = p.id")
    district_ids = {(row[1], row[2]): row[0] for row in cur.fetchall()}

    # Scrape all sources
    all_articles = []

    print("\n  Scraping Kompas...")
    kompas = scrape_kompas()
    print(f"    Got {len(kompas)} articles")
    all_articles.extend(kompas)

    print("  Scraping CNN Indonesia...")
    cnn = scrape_cnnindonesia()
    print(f"    Got {len(cnn)} articles")
    all_articles.extend(cnn)

    print("  Scraping Tempo...")
    tempo = scrape_tempo()
    print(f"    Got {len(tempo)} articles")
    all_articles.extend(tempo)

    print("  Scraping Republika...")
    republika = scrape_republika()
    print(f"    Got {len(republika)} articles")
    all_articles.extend(republika)

    print("  Scraping Liputan6...")
    liputan6 = scrape_liputan6()
    print(f"    Got {len(liputan6)} articles")
    all_articles.extend(liputan6)

    # Deduplicate by URL
    seen = set()
    unique = []
    for a in all_articles:
        if a['url'] not in seen and a['url'] not in existing_urls:
            seen.add(a['url'])
            unique.append(a)

    print(f"\n  Total new unique articles: {len(unique)}")

    # Filter relevant
    relevant = [a for a in unique if is_relevant(a['title'])]
    print(f"  Relevant (MBG keracunan): {len(relevant)}")

    # Insert
    inserted = 0
    for a in relevant:
        victim_count = extract_victim_count(a['title'])
        district_name, province_name = extract_location(a['title'])
        incident_date = parse_date_from_url(a['url'])

        prov_id = province_ids.get(province_name)
        dist_id = district_ids.get((district_name, province_name))

        cur.execute("""
            INSERT INTO incidents (title, victim_count, incident_date,
                                   province_id, district_id, location_detail,
                                   source_url, source_name, verified)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            a['title'],
            victim_count,
            incident_date,
            prov_id,
            dist_id,
            district_name if district_name else None,
            a['url'],
            a['source'],
            False,
        ))
        inserted += 1

    conn.commit()
    print(f"  Inserted: {inserted} new articles")

    # Final stats
    cur.execute("SELECT COUNT(*), COALESCE(SUM(victim_count), 0) FROM incidents WHERE victim_count > 0")
    active, total = cur.fetchone()
    cur.execute("SELECT COUNT(*) FROM incidents")
    total_all = cur.fetchone()[0]
    print(f"\n  Final: {total_all} total articles, {active} with victim counts")

    cur.close()
    conn.close()
    print(f"[{datetime.now().isoformat()}] Done.")


if __name__ == "__main__":
    main()
