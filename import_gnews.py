#!/usr/bin/env python3
"""Insert Google News RSS articles into database"""
import os
import requests, re, time, json
import xml.etree.ElementTree as ET
from datetime import datetime
import psycopg2

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
    'Accept-Language': 'id-ID,id;q=0.9',
}
session = requests.Session()
session.headers.update(HEADERS)

DB_CONFIG = {
    'host': 'localhost', 'port': 5432, 'user': 'postgres',
    'password': os.environ.get('DB_PASS', ''), 'dbname': 'korbanmbg',
}

LOCATION_MAP = {
    'bandung barat': ('Bandung Barat', 'Jawa Barat'),
    'cisarua': ('Bandung Barat', 'Jawa Barat'),
    'cipongkor': ('Bandung Barat', 'Jawa Barat'),
    'garut': ('Garut', 'Jawa Barat'),
    'tasikmalaya': ('Tasikmalaya', 'Jawa Barat'),
    'sumedang': ('Sumedang', 'Jawa Barat'),
    'cianjur': ('Cianjur', 'Jawa Barat'),
    'sukabumi': ('Sukabumi', 'Jawa Barat'),
    'bogor': ('Bogor', 'Jawa Barat'),
    'bekasi': ('Bekasi', 'Jawa Barat'),
    'cimahi': ('Cimahi', 'Jawa Barat'),
    'jabar': ('', 'Jawa Barat'),
    'jawa barat': ('', 'Jawa Barat'),
    'klaten': ('Klaten', 'Jawa Tengah'),
    'demak': ('Demak', 'Jawa Tengah'),
    'kudus': ('Kudus', 'Jawa Tengah'),
    'grobogan': ('Grobogan', 'Jawa Tengah'),
    'wonogiri': ('Wonogiri', 'Jawa Tengah'),
    'jatisrono': ('Wonogiri', 'Jawa Tengah'),
    'semarang': ('Semarang', 'Jawa Tengah'),
    'boyolangu': ('Tulungagung', 'Jawa Timur'),
    'pati': ('Pati', 'Jawa Tengah'),
    'jateng': ('', 'Jawa Tengah'),
    'jawa tengah': ('', 'Jawa Tengah'),
    'mojokerto': ('Mojokerto', 'Jawa Timur'),
    'surabaya': ('Surabaya', 'Jawa Timur'),
    'magetan': ('Magetan', 'Jawa Timur'),
    'malang': ('Malang', 'Jawa Timur'),
    'kediri': ('Kediri', 'Jawa Timur'),
    'tulungagung': ('Tulungagung', 'Jawa Timur'),
    'laguboti': ('Toba Samosir', 'Sumatera Utara'),
    'simalungun': ('Simalungun', 'Sumatera Utara'),
    'jatim': ('', 'Jawa Timur'),
    'jawa timur': ('', 'Jawa Timur'),
    'cakung': ('Jakarta Timur', 'DKI Jakarta'),
    'jakarta timur': ('Jakarta Timur', 'DKI Jakarta'),
    'jaktim': ('Jakarta Timur', 'DKI Jakarta'),
    'pasar rebo': ('Jakarta Timur', 'DKI Jakarta'),
    'jakarta': ('', 'DKI Jakarta'),
    'gunungkidul': ('Gunungkidul', 'DI Yogyakarta'),
    'bantul': ('Bantul', 'DI Yogyakarta'),
    'kulon progo': ('Kulon Progo', 'DI Yogyakarta'),
    'sleman': ('Sleman', 'DI Yogyakarta'),
    'yogyakarta': ('', 'DI Yogyakarta'),
    'jogjakarta': ('', 'DI Yogyakarta'),
    'ketapang': ('Ketapang', 'Kalimantan Barat'),
    'landak': ('Landak', 'Kalimantan Barat'),
    'singkawang': ('Singkawang', 'Kalimantan Barat'),
    'pontianak': ('Pontianak', 'Kalimantan Barat'),
    'kalbar': ('', 'Kalimantan Barat'),
    'kalimantan barat': ('', 'Kalimantan Barat'),
    'penajam': ('Penajam Paser Utara', 'Kalimantan Timur'),
    'ppu': ('Penajam Paser Utara', 'Kalimantan Timur'),
    'kaltim': ('', 'Kalimantan Timur'),
    'palangka raya': ('Palangka Raya', 'Kalimantan Tengah'),
    'kalteng': ('', 'Kalimantan Tengah'),
    'banjar': ('Banjar', 'Kalimantan Selatan'),
    'banjarmasin': ('Banjarmasin', 'Kalimantan Selatan'),
    'kalsel': ('', 'Kalimantan Selatan'),
    'amuntai': ('Hulu Sungai Utara', 'Kalimantan Selatan'),
    'hsu': ('Hulu Sungai Utara', 'Kalimantan Selatan'),
    'banggai': ('Banggai Kepulauan', 'Sulawesi Tengah'),
    'bangkep': ('Banggai Kepulauan', 'Sulawesi Tengah'),
    'palu': ('Palu', 'Sulawesi Tengah'),
    'buol': ('Buol', 'Sulawesi Tengah'),
    'sulteng': ('', 'Sulawesi Tengah'),
    'makassar': ('Makassar', 'Sulawesi Selatan'),
    'sulsel': ('', 'Sulawesi Selatan'),
    'tomohon': ('Tomohon', 'Sulawesi Utara'),
    'manado': ('Manado', 'Sulawesi Utara'),
    'lampung': ('', 'Lampung'),
    'bandar lampung': ('Bandar Lampung', 'Lampung'),
    'bandarlampung': ('Bandar Lampung', 'Lampung'),
    'lampung timur': ('Lampung Timur', 'Lampung'),
    'lampung utara': ('Lampung Utara', 'Lampung'),
    'lampung selatan': ('Lampung Selatan', 'Lampung'),
    'tulang bawang': ('Tulang Bawang', 'Lampung'),
    'menggala': ('Tulang Bawang', 'Lampung'),
    'punggur': ('Lampung Tengah', 'Lampung'),
    'dairi': ('Dairi', 'Sumatera Utara'),
    'sumut': ('', 'Sumatera Utara'),
    'agam': ('Agam', 'Sumatera Barat'),
    'sumbar': ('', 'Sumatera Barat'),
    'aceh selatan': ('Aceh Selatan', 'Aceh'),
    'aceh timur': ('Aceh Timur', 'Aceh'),
    'aceh singkil': ('Aceh Singkil', 'Aceh'),
    'bireuen': ('Bireuen', 'Aceh'),
    'simpang mamplam': ('Bireuen', 'Aceh'),
    'pasie raja': ('Aceh Selatan', 'Aceh'),
    'aceh': ('', 'Aceh'),
    'kupang': ('Kupang', 'NTT'),
    'manggarai': ('Manggarai Barat', 'NTT'),
    'malaka': ('Malaka', 'NTT'),
    'ntt': ('', 'NTT'),
    'ntb': ('', 'NTB'),
    'nabire': ('Nabire', 'Papua Tengah'),
    'manokwari': ('Manokwari', 'Papua Barat'),
    'papua': ('', 'Papua'),
    'gorontalo': ('', 'Gorontalo'),
    'palembang': ('Palembang', 'Sumatera Selatan'),
    'pali': ('PALI', 'Sumatera Selatan'),
    'sumsel': ('', 'Sumatera Selatan'),
    'muaro jambi': ('Muaro Jambi', 'Jambi'),
    'jambi': ('', 'Jambi'),
    'bengkulu utara': ('Bengkulu Utara', 'Bengkulu'),
    'bengkulu': ('', 'Bengkulu'),
    'pandeglang': ('Pandeglang', 'Banten'),
    'serang': ('Serang', 'Banten'),
    'kramatwatu': ('Serang', 'Banten'),
    'lebak': ('Lebak', 'Banten'),
    'tangerang': ('Tangerang', 'Banten'),
    'tangsel': ('Tangerang Selatan', 'Banten'),
    'cilegon': ('Cilegon', 'Banten'),
    'banten': ('', 'Banten'),
    'majene': ('Majene', 'Sulawesi Barat'),
    'waisai': ('Raja Ampat', 'Papua Barat Daya'),
    'kroton': ('', 'Jawa Barat'),
}

def extract_location(title):
    t = title.lower()
    for key in sorted(LOCATION_MAP.keys(), key=len, reverse=True):
        if key in t:
            return LOCATION_MAP[key]
    return ('', '')

def extract_victim_count(title):
    t = title.lower()
    # Skip aggregate/national articles
    skip = ['jppi', 'kpai', 'bgn:', 'data bgn', 'cisdi', 'nasional', 'sepanjang', 'sejak 2025']
    if any(s in t for s in skip):
        return 0
    matches = re.findall(r'(\d[\d.]*)\s*(?:siswa|orang|korban|anak|murid|santri|balita|warga|pelajar|guru)', t)
    matches2 = re.findall(r'(?:jadi|capai|mencapai|tembus|sebanyak|total)\s+(\d[\d.]*)', t)
    nums = []
    for m in matches + matches2:
        try:
            n = int(m.replace('.', ''))
            if 2 < n < 5000:
                nums.append(n)
        except: pass
    return max(nums) if nums else 0

def parse_rss_date(date_str):
    for fmt in ['%a, %d %b %Y %H:%M:%S %Z', '%a, %d %b %Y %H:%M:%S %z']:
        try:
            return datetime.strptime(date_str, fmt).date()
        except: pass
    return None

def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute('SELECT title FROM incidents')
    existing_titles = set(row[0].lower().strip() for row in cur.fetchall())
    cur.execute('SELECT id, name FROM provinces')
    province_ids = {row[1]: row[0] for row in cur.fetchall()}
    cur.execute('SELECT d.id, d.name, p.name FROM districts d JOIN provinces p ON d.province_id = p.id')
    district_ids = {(row[1], row[2]): row[0] for row in cur.fetchall()}

    # Queries
    queries = [
        'keracunan+MBG+2025', 'keracunan+MBG+2026',
        'siswa+keracunan+MBG+januari', 'siswa+keracunan+MBG+februari',
        'siswa+keracunan+MBG+maret', 'siswa+keracunan+MBG+april',
        'keracunan+MBG+NTT', 'keracunan+MBG+NTB',
        'keracunan+MBG+Sulawesi', 'keracunan+MBG+Sumatera',
        'keracunan+MBG+Kalimantan', 'keracunan+MBG+Aceh',
        'keracunan+MBG+Banten', 'keracunan+MBG+Lampung',
    ]

    articles = []
    for q in queries:
        url = f'https://news.google.com/rss/search?q={q}&hl=id&gl=ID&ceid=ID:id'
        try:
            resp = session.get(url, timeout=15)
            if resp.status_code == 200 and '<?xml' in resp.text[:100]:
                root = ET.fromstring(resp.text)
                for item in root.findall('.//item'):
                    title = (item.find('title').text or '').strip()
                    link = item.find('link').text or ''
                    pub_date = item.find('pubDate').text or ''
                    source = item.find('source').text or ''
                    articles.append({'title': title, 'url': link, 'date': pub_date, 'source': source})
        except: pass
        time.sleep(1)

    # Deduplicate
    seen_urls = set()
    new_articles = []
    for a in articles:
        title_lower = a['title'].lower().strip()
        if title_lower in existing_titles: continue
        prefix = title_lower[:40]
        if any(prefix in et for et in existing_titles): continue
        if a['url'] in seen_urls: continue
        seen_urls.add(a['url'])
        new_articles.append(a)
        existing_titles.add(title_lower)

    # Filter relevant
    relevant = [a for a in new_articles if 'mbg' in a['title'].lower() or 'makan bergizi' in a['title'].lower()]
    print(f'Total from RSS: {len(articles)}')
    print(f'New unique: {len(new_articles)}')
    print(f'Relevant: {len(relevant)}')

    # Insert
    inserted = 0
    for a in relevant:
        victim_count = extract_victim_count(a['title'])
        district_name, province_name = extract_location(a['title'])
        incident_date = parse_rss_date(a['date'])
        prov_id = province_ids.get(province_name)
        dist_id = district_ids.get((district_name, province_name))

        # Create district if needed
        if district_name and prov_id and not dist_id:
            cur.execute('INSERT INTO districts (name, province_id) VALUES (%s, %s) ON CONFLICT DO NOTHING RETURNING id',
                       (district_name, prov_id))
            result = cur.fetchone()
            if result:
                dist_id = result[0]
                district_ids[(district_name, province_name)] = dist_id
            else:
                cur.execute('SELECT id FROM districts WHERE name = %s AND province_id = %s', (district_name, prov_id))
                r = cur.fetchone()
                if r: dist_id = r[0]

        cur.execute('''
            INSERT INTO incidents (title, victim_count, incident_date, province_id, district_id,
                                   source_url, source_name, verified)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (a['title'], victim_count, incident_date, prov_id, dist_id, a['url'], a['source'], False))
        inserted += 1

    # Update aggregate data with new figures
    new_aggregates = [
        ('JPPI: 33.626 pelajar keracunan MBG (Jan 2025 - Apr 2026)', 'JPPI', 33626,
         '2025-01-06', '2026-04-09', 'Hasil monitoring Jaringan Pemantau Pendidikan Indonesia (JPPI), dilaporkan Kompas.id 9 Apr 2026. UGM (Prof Sri Raharjo) memberi analisa terpisah, bukan sumber data.'),
        ('JPPI: 16.109 korban keracunan MBG per 31 Oktober 2025', 'JPPI', 16109,
         '2025-01-06', '2025-10-31', 'Update dari 11.566. Sumber: Tempo.co'),
        ('Prabowo: 28.000 siswa keracunan MBG (Feb 2026)', 'Presiden', 28000,
         '2025-01-06', '2026-02-13', 'Presiden Prabowo mengakui 28.000 siswa keracunan. Sumber: harianfajar'),
    ]
    for name, org, total, start, end, notes in new_aggregates:
        cur.execute('''
            INSERT INTO aggregate_data (source_name, source_org, total_victims, period_start, period_end, notes)
            VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING
        ''', (name, org, total, start, end, notes))

    conn.commit()
    print(f'Inserted: {inserted} articles')

    # Final stats
    cur.execute('SELECT COUNT(*) FROM incidents')
    total = cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM incidents WHERE province_id IS NOT NULL')
    with_prov = cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM incidents WHERE victim_count > 0')
    with_vc = cur.fetchone()[0]
    cur.execute('''
        SELECT COALESCE(SUM(max_vc), 0) FROM (
            SELECT province_id, district_id, TO_CHAR(incident_date, 'YYYY-MM') as month,
                   MAX(victim_count) as max_vc
            FROM incidents WHERE victim_count > 0 AND province_id IS NOT NULL
            GROUP BY province_id, district_id, TO_CHAR(incident_date, 'YYYY-MM')
        ) t
    ''')
    dedup_total = cur.fetchone()[0]

    # Province count
    cur.execute('SELECT COUNT(DISTINCT province_id) FROM incidents WHERE province_id IS NOT NULL')
    prov_count = cur.fetchone()[0]

    # Source diversity
    cur.execute("SELECT source_name, COUNT(*) FROM incidents WHERE source_name IS NOT NULL GROUP BY source_name ORDER BY COUNT(*) DESC LIMIT 10")
    sources = cur.fetchall()

    print(f'\n=== FINAL DATABASE STATE ===')
    print(f'Total articles: {total}')
    print(f'With province: {with_prov} ({100*with_prov//total}%)')
    print(f'With victim_count: {with_vc} ({100*with_vc//total}%)')
    print(f'Provinces covered: {prov_count}')
    print(f'Deduplicated victim total: {dedup_total}')
    print(f'\nTop sources:')
    for src, cnt in sources:
        print(f'  {src:20s}: {cnt}')

    # Monthly coverage
    cur.execute('''
        SELECT TO_CHAR(incident_date, 'YYYY-MM') as m, COUNT(*)
        FROM incidents WHERE incident_date IS NOT NULL
        GROUP BY m ORDER BY m
    ''')
    print(f'\nMonthly coverage:')
    for row in cur.fetchall():
        print(f'  {row[0]}: {row[1]:4d} articles')

    conn.close()

if __name__ == '__main__':
    main()
