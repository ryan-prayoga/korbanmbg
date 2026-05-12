#!/usr/bin/env python3
"""
Import MBG dataset into PostgreSQL database
"""

import json
import re
import psycopg2
from datetime import datetime

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': 'P@ssw0rd18TraspaC',
    'dbname': 'korbanmbg',
}

# Province mapping
PROVINCES = {
    'Jawa Barat': 'JB',
    'Jawa Timur': 'JT',
    'Jawa Tengah': 'JTG',
    'DKI Jakarta': 'DKI',
    'DI Yogyakarta': 'DIY',
    'Banten': 'BT',
    'Kalimantan Barat': 'KB',
    'NTB': 'NTB',
    'NTT': 'NTT',
    'Sumatera Utara': 'SU',
    'Sumatera Barat': 'SB',
    'Sumatera Selatan': 'SS',
    'Lampung': 'LP',
    'Kepulauan Riau': 'KR',
    'Sulawesi Barat': 'SLB',
    'Sulawesi Tenggara': 'SLT',
    'Sulawesi Utara': 'SLU',
    'Gorontalo': 'GR',
    'Papua Tengah': 'PT',
}

# Location dictionary (same as scraper)
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
    """Parse Indonesian date text to date object"""
    if not date_text:
        return None
    
    months = {
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'mei': 5, 'jun': 6,
        'jul': 7, 'agu': 8, 'sep': 9, 'okt': 10, 'nov': 11, 'des': 12,
    }
    
    # Pattern: "Hari, DD Mon YYYY HH:MM WIB"
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
    """Extract victim count from title/description"""
    text = (title + ' ' + (description or '')).lower()
    
    # Skip aggregate articles
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
            if 1 < n < 5000:  # reasonable per-incident range
                all_nums.append(n)
        except:
            pass
    
    return max(all_nums) if all_nums else 0


def extract_location(title, description):
    """Extract kabupaten and provinsi"""
    combined = (title + ' ' + (description or '')).lower()
    
    for key in sorted(LOCATION_MAP.keys(), key=len, reverse=True):
        if key in combined:
            return LOCATION_MAP[key]
    
    return ('', '')


def is_incident_article(title):
    """Check if article is about a specific incident (not aggregate/opinion)"""
    t = title.lower()
    # Must have incident indicator
    if not any(k in t for k in ['keracunan', 'korban', 'sakit', 'diare', 'muntah', 'rawat']):
        return False
    # Skip aggregate/opinion articles
    skip_patterns = ['kpai', 'jppi', 'cisdi', 'video top', 'dpr', 'bgn ungkap', 
                     'bos bgn', 'istana', 'prabowo', 'legislator', 'evaluasi',
                     'cegah', 'cara cegah', 'skema biaya']
    if any(k in t for k in skip_patterns):
        return False
    return True


def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # Create tables (in case API hasn't run yet)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS provinces (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE,
            code VARCHAR(10)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS districts (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            province_id INTEGER REFERENCES provinces(id),
            UNIQUE(name, province_id)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            victim_count INTEGER DEFAULT 0,
            hospitalized INTEGER DEFAULT 0,
            deaths INTEGER DEFAULT 0,
            incident_date DATE,
            province_id INTEGER REFERENCES provinces(id),
            district_id INTEGER REFERENCES districts(id),
            location_detail TEXT,
            menu_items TEXT[],
            symptoms TEXT[],
            source_url TEXT,
            source_name VARCHAR(100),
            verified BOOLEAN DEFAULT false,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS aggregate_data (
            id SERIAL PRIMARY KEY,
            source_name VARCHAR(200) NOT NULL,
            source_org VARCHAR(200),
            total_victims INTEGER NOT NULL,
            period_start DATE,
            period_end DATE,
            notes TEXT,
            source_url TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)
    conn.commit()
    
    # Insert provinces
    print("Inserting provinces...")
    province_ids = {}
    for name, code in PROVINCES.items():
        cur.execute(
            "INSERT INTO provinces (name, code) VALUES (%s, %s) ON CONFLICT (name) DO NOTHING RETURNING id",
            (name, code)
        )
        result = cur.fetchone()
        if result:
            province_ids[name] = result[0]
        else:
            cur.execute("SELECT id FROM provinces WHERE name = %s", (name,))
            province_ids[name] = cur.fetchone()[0]
    conn.commit()
    print(f"  {len(province_ids)} provinces")
    
    # Insert districts
    print("Inserting districts...")
    district_ids = {}
    for key, (district, province) in LOCATION_MAP.items():
        if district and province in province_ids:
            prov_id = province_ids[province]
            cur.execute(
                "INSERT INTO districts (name, province_id) VALUES (%s, %s) ON CONFLICT (name, province_id) DO NOTHING RETURNING id",
                (district, prov_id)
            )
            result = cur.fetchone()
            if result:
                district_ids[(district, province)] = result[0]
            else:
                cur.execute("SELECT id FROM districts WHERE name = %s AND province_id = %s", (district, prov_id))
                r = cur.fetchone()
                if r:
                    district_ids[(district, province)] = r[0]
    conn.commit()
    print(f"  {len(district_ids)} districts")
    
    # Load articles
    with open('/home/ubuntu/projects/mbg-scraper/output/full_detik_enriched.json', 'r') as f:
        articles = json.load(f)
    
    print(f"\nProcessing {len(articles)} articles...")
    
    # Deduplicate: group by incident (same location + date window + similar victim count)
    # For now, insert all incident articles and deduplicate later
    inserted = 0
    skipped = 0
    
    for a in articles:
        if not is_incident_article(a['title']):
            skipped += 1
            continue
        
        # Extract data
        victim_count = extract_victim_count(a['title'], a.get('description', ''))
        district_name, province_name = extract_location(a['title'], a.get('description', ''))
        incident_date = parse_date(a.get('date_text', ''))
        
        # Get IDs
        prov_id = province_ids.get(province_name)
        dist_id = district_ids.get((district_name, province_name))
        
        # Check for duplicate (same URL)
        cur.execute("SELECT id FROM incidents WHERE source_url = %s", (a['url'],))
        if cur.fetchone():
            skipped += 1
            continue
        
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
    print(f"  Inserted: {inserted}")
    print(f"  Skipped: {skipped}")
    
    # Insert aggregate data (credible sources)
    print("\nInserting aggregate data...")
    aggregates = [
        ("KPAI: 12.658 anak di 38 provinsi keracunan MBG sepanjang 2025",
         "KPAI", 12658, "2025-01-01", "2025-12-31",
         "Breakdown: Jabar 4.877, Jateng 1.961, DIY 1.517. Metode: monitoring media.",
         "https://news.detik.com/berita/d-8309812/data-kpai-12-658-anak-di-38-provinsi-keracunan-mbg-sepanjang-2025"),
        
        ("BGN: 6.517 orang keracunan MBG (Jan-Sep 2025)",
         "BGN", 6517, "2025-01-06", "2025-09-30",
         "Wilayah I (Sumatera): 1.307, Wilayah II (Jawa): 4.147+, Wilayah III (Indonesia Timur): 1.003. 75 kejadian total.",
         "https://news.detik.com/berita/d-8309812/"),
        
        ("JPPI: 10.482 anak keracunan MBG per 4 Oktober 2025",
         "JPPI", 10482, "2025-01-01", "2025-10-04",
         "Rata-rata Sep 2025: 1.531 anak/minggu. Tren: 1.376 (Jun) -> 6.452 (Sep) -> 10.482 (Okt).",
         "https://www.detik.com/edu/sekolah/d-8147008/jppi-catat-korban-keracunan-mbg-capai-10-482-anak-serukan-setop-semua-dapur-mbg"),
        
        ("CISDI: 5.626 kasus keracunan MBG di 16 provinsi",
         "CISDI", 5626, "2025-01-17", "2025-09-18",
         "Periode 17 Januari - 18 September 2025. Via LBH Bandung.",
         "https://www.detik.com/jabar/berita/d-8133228/desakan-lbh-bandung-usai-mbg-berbuntut-keracunan-massal"),
    ]
    
    for name, org, total, start, end, notes, url in aggregates:
        cur.execute("""
            INSERT INTO aggregate_data (source_name, source_org, total_victims, period_start, period_end, notes, source_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (name, org, total, start, end, notes, url))
    
    conn.commit()
    print("  Done")
    
    # Print summary
    cur.execute("SELECT COUNT(*) FROM incidents")
    total_inc = cur.fetchone()[0]
    cur.execute("SELECT COALESCE(SUM(victim_count), 0) FROM incidents")
    total_vic = cur.fetchone()[0]
    cur.execute("SELECT COUNT(DISTINCT province_id) FROM incidents WHERE province_id IS NOT NULL")
    total_prov = cur.fetchone()[0]
    
    print(f"\n{'=' * 50}")
    print(f"DATABASE SUMMARY")
    print(f"{'=' * 50}")
    print(f"Incidents: {total_inc}")
    print(f"Total victims (from incidents): {total_vic}")
    print(f"Provinces affected: {total_prov}")
    print(f"Aggregate sources: {len(aggregates)}")
    
    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
