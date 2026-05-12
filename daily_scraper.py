#!/usr/bin/env python3
"""
Daily scraper for KorbanMBG — fetches new articles from Detik.com
and inserts them into the database.
Run via cron: 0 6 * * * /usr/bin/python3 /home/ubuntu/projects/korbanmbg/daily_scraper.py
"""

import json
import re
import time
import requests
import psycopg2
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': 'P@ssw0rd18TraspaC',
    'dbname': 'korbanmbg',
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Accept-Language': 'id-ID,id;q=0.9',
}

LOCATION_MAP = {
    'surabaya': ('Surabaya', 'Jawa Timur'),
    'mojokerto': ('Mojokerto', 'Jawa Timur'),
    'kediri': ('Kediri', 'Jawa Timur'),
    'tulungagung': ('Tulungagung', 'Jawa Timur'),
    'bojonegoro': ('Bojonegoro', 'Jawa Timur'),
    'lamongan': ('Lamongan', 'Jawa Timur'),
    'bandung barat': ('Bandung Barat', 'Jawa Barat'),
    'kbb': ('Bandung Barat', 'Jawa Barat'),
    'cipongkor': ('Bandung Barat', 'Jawa Barat'),
    'cisarua': ('Bandung Barat', 'Jawa Barat'),
    'bandung': ('Bandung', 'Jawa Barat'),
    'cianjur': ('Cianjur', 'Jawa Barat'),
    'garut': ('Garut', 'Jawa Barat'),
    'tasikmalaya': ('Tasikmalaya', 'Jawa Barat'),
    'cisayong': ('Tasikmalaya', 'Jawa Barat'),
    'sumedang': ('Sumedang', 'Jawa Barat'),
    'cimahi': ('Cimahi', 'Jawa Barat'),
    'sukabumi': ('Sukabumi', 'Jawa Barat'),
    'bogor': ('Bogor', 'Jawa Barat'),
    'kuningan': ('Kuningan', 'Jawa Barat'),
    'ciamis': ('Ciamis', 'Jawa Barat'),
    'klaten': ('Klaten', 'Jawa Tengah'),
    'demak': ('Demak', 'Jawa Tengah'),
    'kudus': ('Kudus', 'Jawa Tengah'),
    'rembang': ('Rembang', 'Jawa Tengah'),
    'cilacap': ('Cilacap', 'Jawa Tengah'),
    'semarang': ('Semarang', 'Jawa Tengah'),
    'grobogan': ('Grobogan', 'Jawa Tengah'),
    'jaktim': ('Jakarta Timur', 'DKI Jakarta'),
    'jakarta timur': ('Jakarta Timur', 'DKI Jakarta'),
    'pulogebang': ('Jakarta Timur', 'DKI Jakarta'),
    'bantul': ('Bantul', 'DI Yogyakarta'),
    'gunungkidul': ('Gunungkidul', 'DI Yogyakarta'),
    'cilegon': ('Cilegon', 'Banten'),
    'serang': ('Serang', 'Banten'),
    'ketapang': ('Ketapang', 'Kalimantan Barat'),
    'landak': ('Landak', 'Kalimantan Barat'),
    'lombok timur': ('Lombok Timur', 'NTB'),
    'lombok': ('Lombok', 'NTB'),
    'sumbawa': ('Sumbawa', 'NTB'),
    'bima': ('Bima', 'NTB'),
    'sumba': ('Sumba', 'NTT'),
    'manggarai': ('Manggarai Barat', 'NTT'),
    'kupang': ('Kupang', 'NTT'),
    'soe': ('TTS', 'NTT'),
    'lampung': ('Lampung', 'Lampung'),
    'anambas': ('Kepulauan Anambas', 'Kepulauan Riau'),
    'kolaka': ('Kolaka', 'Sulawesi Tenggara'),
    'baubau': ('Baubau', 'Sulawesi Tenggara'),
    'polman': ('Polewali Mandar', 'Sulawesi Barat'),
    'majene': ('Majene', 'Sulawesi Barat'),
    'gorontalo': ('Gorontalo', 'Gorontalo'),
    'tomohon': ('Tomohon', 'Sulawesi Utara'),
    'dairi': ('Dairi', 'Sumatera Utara'),
    'deli serdang': ('Deli Serdang', 'Sumatera Utara'),
    'pali': ('PALI', 'Sumatera Selatan'),
    'agam': ('Agam', 'Sumatera Barat'),
    'nabire': ('Nabire', 'Papua Tengah'),
}


def parse_date(date_text):
    if not date_text:
        return None
    months = {
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'mei': 5, 'jun': 6,
        'jul': 7, 'agu': 8, 'sep': 9, 'okt': 10, 'nov': 11, 'des': 12,
    }
    m = re.search(r'(\d{1,2})\s+(\w+)\s+(\d{4})', date_text)
    if m:
        day = int(m.group(1))
        month_str = m.group(2).lower()[:3]
        year = int(m.group(3))
        month = months.get(month_str, 0)
        if month:
            try:
                return datetime(year, month, day).date()
            except:
                pass
    return None


def extract_victim_count(title, description):
    text = (title + ' ' + (description or '')).lower()
    if any(k in text for k in ['kpai', 'jppi', 'cisdi', 'bgn ungkap', 'kepala bgn']):
        if any(k in text for k in ['12.658', '10.482', '6.517', '6.452', '5.914']):
            return 0
    matches = re.findall(r'(\d[\d.]*)\s*(?:siswa|orang|korban|anak|murid|santri|balita|warga|pelajar)', text)
    matches2 = re.findall(r'(?:capai|mencapai|sebanyak|total|tembus|jadi)\s*(\d[\d.]*)', text)
    all_nums = []
    for m in matches + matches2:
        m_clean = m.replace('.', '')
        try:
            n = int(m_clean)
            if 1 < n < 5000:
                all_nums.append(n)
        except:
            pass
    return max(all_nums) if all_nums else 0


def extract_location(title, description):
    combined = (title + ' ' + (description or '')).lower()
    for key in sorted(LOCATION_MAP.keys(), key=len, reverse=True):
        if key in combined:
            return LOCATION_MAP[key]
    return ('', '')


def is_incident_article(title):
    t = title.lower()
    if not any(k in t for k in ['keracunan', 'korban', 'sakit', 'diare', 'muntah', 'rawat']):
        return False
    skip = ['kpai', 'jppi', 'cisdi', 'video top', 'dpr', 'bgn ungkap',
            'bos bgn', 'istana', 'prabowo', 'legislator', 'evaluasi',
            'cegah', 'cara cegah', 'skema biaya']
    if any(k in t for k in skip):
        return False
    return True


def scrape_detik_recent():
    """Scrape recent articles about MBG keracunan from Detik"""
    session = requests.Session()
    session.headers.update(HEADERS)

    articles = []
    keywords = ['keracunan MBG', 'keracunan makan bergizi gratis']

    for keyword in keywords:
        for page in range(1, 4):  # 3 pages per keyword
            url = f"https://www.detik.com/search/searchall?query={keyword}&page={page}"
            try:
                resp = session.get(url, timeout=15)
                soup = BeautifulSoup(resp.text, 'lxml')
                items = soup.select('article, div.list-content__item, div.media')

                for item in items:
                    link = item.select_one('a[href*="detik.com"]')
                    if not link:
                        continue
                    href = link.get('href', '')
                    if not href or '/tag/' in href:
                        continue

                    title_el = item.select_one('h2, h3, .media__title, .list-content__title')
                    title = title_el.get_text(strip=True) if title_el else link.get_text(strip=True)

                    if not title or len(title) < 10:
                        continue

                    date_el = item.select_one('.media__date, .list-content__date, time, span.date')
                    date_text = date_el.get_text(strip=True) if date_el else ''

                    desc_el = item.select_one('.media__desc, .list-content__desc, p')
                    desc = desc_el.get_text(strip=True) if desc_el else ''

                    articles.append({
                        'title': title,
                        'url': href,
                        'date_text': date_text,
                        'description': desc,
                    })

                time.sleep(2)  # Be polite
            except Exception as e:
                print(f"  Error scraping {keyword} page {page}: {e}")
                continue

    # Deduplicate by URL
    seen = set()
    unique = []
    for a in articles:
        if a['url'] not in seen:
            seen.add(a['url'])
            unique.append(a)

    return unique


def main():
    print(f"[{datetime.now().isoformat()}] KorbanMBG daily scraper starting...")

    # Connect to DB
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Get existing URLs to avoid duplicates
    cur.execute("SELECT source_url FROM incidents")
    existing_urls = set(row[0] for row in cur.fetchall() if row[0])
    print(f"  Existing incidents: {len(existing_urls)}")

    # Get province/district IDs
    cur.execute("SELECT id, name FROM provinces")
    province_ids = {row[1]: row[0] for row in cur.fetchall()}

    cur.execute("SELECT d.id, d.name, p.name FROM districts d JOIN provinces p ON d.province_id = p.id")
    district_ids = {(row[1], row[2]): row[0] for row in cur.fetchall()}

    # Scrape
    articles = scrape_detik_recent()
    print(f"  Scraped: {len(articles)} articles")

    # Insert new ones
    inserted = 0
    for a in articles:
        if a['url'] in existing_urls:
            continue
        if not is_incident_article(a['title']):
            continue

        victim_count = extract_victim_count(a['title'], a.get('description', ''))
        district_name, province_name = extract_location(a['title'], a.get('description', ''))
        incident_date = parse_date(a.get('date_text', ''))

        prov_id = province_ids.get(province_name)
        dist_id = district_ids.get((district_name, province_name))

        cur.execute("""
            INSERT INTO incidents (title, description, victim_count, incident_date,
                                   province_id, district_id, location_detail,
                                   source_url, source_name, verified)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            a['title'],
            a.get('description', ''),
            victim_count,
            incident_date,
            prov_id,
            dist_id,
            district_name if district_name else None,
            a['url'],
            'detik.com',
            False,
        ))
        inserted += 1

    conn.commit()
    print(f"  Inserted: {inserted} new incidents")

    # Update stats
    cur.execute("SELECT COUNT(*), COALESCE(SUM(victim_count), 0) FROM incidents")
    total_inc, total_vic = cur.fetchone()
    print(f"  Total now: {total_inc} incidents, {total_vic} victims")

    cur.close()
    conn.close()
    print(f"[{datetime.now().isoformat()}] Done.")


if __name__ == "__main__":
    main()
