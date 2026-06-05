#!/usr/bin/env python3
"""
Pre-process GeoJSON files: inject victim_count data from DB into each feature's properties.
Output: 
  - geodata/processed/provinces.geojson  (all provinces with victim data)
  - geodata/processed/kabupaten/{prov_code}.geojson  (per-province kabupaten with victim data)
"""
import json
import os
import psycopg2

DB_CONFIG = {
    'host': 'localhost', 'port': 5432,
    'user': 'postgres', 'password': os.environ.get('DB_PASS', ''),
    'dbname': 'korbanmbg',
}

GEODATA_DIR = os.path.expanduser('~/projects/korbanmbg/geodata/geojson')
OUT_DIR = os.path.expanduser('~/projects/korbanmbg/geodata/processed')

# Kemendagri province code → name mapping
PROV_CODE_MAP = {
    '11': 'Aceh', '12': 'Sumatera Utara', '13': 'Sumatera Barat',
    '14': 'Riau', '15': 'Jambi', '16': 'Sumatera Selatan',
    '17': 'Bengkulu', '18': 'Lampung', '19': 'Kepulauan Bangka Belitung',
    '21': 'Kepulauan Riau', '31': 'DKI Jakarta', '32': 'Jawa Barat',
    '33': 'Jawa Tengah', '34': 'DI Yogyakarta', '35': 'Jawa Timur',
    '36': 'Banten', '51': 'Bali', '52': 'NTB', '53': 'NTT',
    '61': 'Kalimantan Barat', '62': 'Kalimantan Tengah',
    '63': 'Kalimantan Selatan', '64': 'Kalimantan Timur',
    '65': 'Kalimantan Utara', '71': 'Sulawesi Utara',
    '72': 'Sulawesi Tengah', '73': 'Sulawesi Selatan',
    '74': 'Sulawesi Tenggara', '75': 'Gorontalo',
    '76': 'Sulawesi Barat', '81': 'Maluku', '82': 'Maluku Utara',
    '91': 'Papua Barat', '92': 'Papua', '93': 'Papua Selatan',
    '94': 'Papua Tengah', '95': 'Papua Pegunungan', '96': 'Papua Barat Daya',
}

# Normalize province names for matching
PROV_NORMALIZE = {
    'dki jakarta': 'DKI Jakarta',
    'di yogyakarta': 'DI Yogyakarta',
    'ntt': 'NTT', 'ntb': 'NTB',
    'nusa tenggara barat': 'NTB',
    'nusa tenggara timur': 'NTT',
}


def normalize_prov(name: str) -> str:
    n = name.lower().strip()
    return PROV_NORMALIZE.get(n, name.strip())


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(OUT_DIR, 'kabupaten'), exist_ok=True)

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Get province stats (deduplicated)
    # Get province stats from unique_incidents (consistent with district stats)
    cur.execute("""
        SELECT p.name,
               COALESCE(SUM(ui.victim_count), 0) as total_victims,
               COUNT(ui.id) as incident_count
        FROM provinces p
        LEFT JOIN unique_incidents ui ON ui.province_id = p.id
        GROUP BY p.name
    """)
    prov_stats = {row[0]: {'victims': row[1], 'incidents': row[2]} for row in cur.fetchall()}

    # Get district stats from unique_incidents (consistent with DB view)
    cur.execute("""
        SELECT p.name as prov_name, d.id as dist_id, d.name as dist_name,
               COALESCE(SUM(ui.victim_count), 0) as total_victims,
               COUNT(ui.id) as incident_count
        FROM districts d
        JOIN provinces p ON d.province_id = p.id
        LEFT JOIN unique_incidents ui ON ui.district_id = d.id
        GROUP BY p.name, d.id, d.name
    """)
    dist_stats = {}
    for row in cur.fetchall():
        prov, dist_id, dist, victims, incidents = row
        if prov not in dist_stats:
            dist_stats[prov] = {}
        dist_stats[prov][dist] = {'id': dist_id, 'victims': victims, 'incidents': incidents, 'articles': 0}

    # Add raw article count per district
    cur.execute("""
        SELECT p.name as prov_name, d.name as dist_name, COUNT(i.id) as article_count
        FROM districts d
        JOIN provinces p ON d.province_id = p.id
        JOIN incidents i ON i.district_id = d.id
        GROUP BY p.name, d.name
    """)
    for row in cur.fetchall():
        prov, dist, articles = row
        if prov in dist_stats and dist in dist_stats[prov]:
            dist_stats[prov][dist]['articles'] = articles

    # Max victims for color scale
    max_victims = max((v['victims'] for v in prov_stats.values()), default=1)

    # --- Process provinces.geojson ---
    all_features = []
    for code, prov_name in PROV_CODE_MAP.items():
        fpath = os.path.join(GEODATA_DIR, 'provinsi', f'{code}.geo.json')
        if not os.path.exists(fpath):
            continue
        with open(fpath) as f:
            gj = json.load(f)

        stats = prov_stats.get(prov_name, {'victims': 0, 'incidents': 0})
        for feat in gj['features']:
            feat['properties']['prov_code'] = code
            feat['properties']['prov_name'] = prov_name
            feat['properties']['victims'] = stats['victims']
            feat['properties']['incidents'] = stats['incidents']
            feat['properties']['intensity'] = round(stats['victims'] / max_victims, 4) if max_victims > 0 else 0
            all_features.append(feat)

    provinces_gj = {'type': 'FeatureCollection', 'features': all_features}
    out_path = os.path.join(OUT_DIR, 'provinces.geojson')
    with open(out_path, 'w') as f:
        json.dump(provinces_gj, f, separators=(',', ':'))
    print(f"Provinces: {len(all_features)} features → {out_path}")

    # --- Process per-province kabupaten ---
    kab_dir = os.path.join(GEODATA_DIR, 'kabupaten')
    prov_kab_count = {}

    # Group kabupaten files by province code (XX.YY.geo.json → XX)
    from collections import defaultdict
    prov_files = defaultdict(list)
    for fname in sorted(os.listdir(kab_dir)):
        if not fname.endswith('.geo.json'):
            continue
        parts = fname.split('.')
        if len(parts) >= 2:
            prov_code = parts[0]
            prov_files[prov_code].append(fname)

    for prov_code, fnames in sorted(prov_files.items()):
        prov_name = PROV_CODE_MAP.get(prov_code, '')
        prov_dists = dist_stats.get(prov_name, {})
        max_dist_victims = max((v['victims'] for v in prov_dists.values()), default=1)

        merged_features = []
        for fname in fnames:
            fpath = os.path.join(kab_dir, fname)
            try:
                with open(fpath) as f:
                    gj = json.load(f)
            except Exception as e:
                print(f"  SKIP corrupt file: {fname} ({e})")
                continue

            for feat in gj['features']:
                kab_name = feat['properties'].get('WADMKK', '')
                stats = prov_dists.get(kab_name, {'id': None, 'victims': 0, 'incidents': 0, 'articles': 0})
                feat['properties']['kab_name'] = kab_name
                feat['properties']['kab_id'] = stats.get('id')
                feat['properties']['prov_name'] = prov_name
                feat['properties']['prov_code'] = prov_code
                feat['properties']['victims'] = stats['victims']
                feat['properties']['incidents'] = stats['incidents']
                feat['properties']['articles'] = stats.get('articles', 0)
                feat['properties']['intensity'] = round(stats['victims'] / max_dist_victims, 4) if max_dist_victims > 0 else 0
                merged_features.append(feat)

        if not merged_features:
            continue

        merged_gj = {'type': 'FeatureCollection', 'features': merged_features}
        out_kab = os.path.join(OUT_DIR, 'kabupaten', f'{prov_code}.geojson')
        with open(out_kab, 'w') as f:
            json.dump(merged_gj, f, separators=(',', ':'))

        prov_kab_count[prov_name] = len(merged_features)

    print(f"Kabupaten: {len(prov_kab_count)} provinces processed")
    for prov, count in sorted(prov_kab_count.items()):
        has_data = prov in prov_stats
        print(f"  {'*' if has_data else ' '} {prov}: {count} kabupaten")

    cur.close()
    conn.close()


if __name__ == '__main__':
    main()
