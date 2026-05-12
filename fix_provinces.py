#!/usr/bin/env python3
"""
Fix unassigned provinces in incidents table.
Matches keywords in title to assign province_id and district_id.
"""
import psycopg2

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': 'P@ssw0rd18TraspaC',
    'dbname': 'korbanmbg',
}

# Extended location mapping: keyword -> (district_name, province_name)
# More comprehensive than the scraper's original map
LOCATION_RULES = [
    # Jawa Barat
    ('bandung barat', 'Bandung Barat', 'Jawa Barat'),
    ('bandugn barat', 'Bandung Barat', 'Jawa Barat'),  # typo in article
    ('kbb', 'Bandung Barat', 'Jawa Barat'),
    ('cipongkor', 'Bandung Barat', 'Jawa Barat'),
    ('cisarua', 'Bandung Barat', 'Jawa Barat'),
    ('jabar', '', 'Jawa Barat'),
    ('jawa barat', '', 'Jawa Barat'),
    ('garut', 'Garut', 'Jawa Barat'),
    ('tasikmalaya', 'Tasikmalaya', 'Jawa Barat'),
    ('ciamis', 'Ciamis', 'Jawa Barat'),
    ('sumedang', 'Sumedang', 'Jawa Barat'),
    ('cianjur', 'Cianjur', 'Jawa Barat'),
    ('sukabumi', 'Sukabumi', 'Jawa Barat'),
    ('bogor', 'Bogor', 'Jawa Barat'),
    ('kuningan', 'Kuningan', 'Jawa Barat'),
    ('bandung', 'Bandung', 'Jawa Barat'),
    ('cimahi', 'Cimahi', 'Jawa Barat'),

    # Jawa Tengah
    ('klaten', 'Klaten', 'Jawa Tengah'),
    ('demak', 'Demak', 'Jawa Tengah'),
    ('kudus', 'Kudus', 'Jawa Tengah'),
    ('rembang', 'Rembang', 'Jawa Tengah'),
    ('grobogan', 'Grobogan', 'Jawa Tengah'),
    ('cilacap', 'Cilacap', 'Jawa Tengah'),
    ('semarang', 'Semarang', 'Jawa Tengah'),
    ('jateng', '', 'Jawa Tengah'),

    # Jawa Timur
    ('surabaya', 'Surabaya', 'Jawa Timur'),
    ('mojokerto', 'Mojokerto', 'Jawa Timur'),
    ('kediri', 'Kediri', 'Jawa Timur'),
    ('tulungagung', 'Tulungagung', 'Jawa Timur'),
    ('bojonegoro', 'Bojonegoro', 'Jawa Timur'),
    ('lamongan', 'Lamongan', 'Jawa Timur'),
    ('jombang', 'Jombang', 'Jawa Timur'),
    ('jatim', '', 'Jawa Timur'),

    # DKI Jakarta
    ('jakarta timur', 'Jakarta Timur', 'DKI Jakarta'),
    ('jaktim', 'Jakarta Timur', 'DKI Jakarta'),
    ('pulogebang', 'Jakarta Timur', 'DKI Jakarta'),
    ('meruya', 'Jakarta Barat', 'DKI Jakarta'),
    ('jakarta barat', 'Jakarta Barat', 'DKI Jakarta'),
    ('jakarta', '', 'DKI Jakarta'),

    # DI Yogyakarta
    ('bantul', 'Bantul', 'DI Yogyakarta'),
    ('gunungkidul', 'Gunungkidul', 'DI Yogyakarta'),
    ('yogyakarta', '', 'DI Yogyakarta'),
    ('diy', '', 'DI Yogyakarta'),

    # NTT
    ('tts', 'TTS', 'NTT'),
    ('timor tengah selatan', 'TTS', 'NTT'),
    ('kupang', 'Kupang', 'NTT'),
    ('manggarai', 'Manggarai Barat', 'NTT'),
    ('sumba', 'Sumba', 'NTT'),
    ('soe', 'TTS', 'NTT'),
    ('ntt', '', 'NTT'),
    ('flores', '', 'NTT'),

    # NTB
    ('lombok timur', 'Lombok Timur', 'NTB'),
    ('lombok', 'Lombok', 'NTB'),
    ('sumbawa', 'Sumbawa', 'NTB'),
    ('bima', 'Bima', 'NTB'),
    ('ntb', '', 'NTB'),

    # Kalimantan Barat
    ('ketapang', 'Ketapang', 'Kalimantan Barat'),
    ('landak', 'Landak', 'Kalimantan Barat'),
    ('marau', 'Ketapang', 'Kalimantan Barat'),
    ('kalbar', '', 'Kalimantan Barat'),

    # Sulawesi Tengah
    ('buol', 'Buol', 'Sulawesi Tengah'),
    ('banggai', 'Banggai Kepulauan', 'Sulawesi Tengah'),
    ('bangkep', 'Banggai Kepulauan', 'Sulawesi Tengah'),
    ('sulteng', '', 'Sulawesi Tengah'),

    # Sulawesi Tenggara
    ('buton tengah', 'Buton Tengah', 'Sulawesi Tenggara'),
    ('buton', 'Buton', 'Sulawesi Tenggara'),
    ('kolaka', 'Kolaka', 'Sulawesi Tenggara'),
    ('baubau', 'Baubau', 'Sulawesi Tenggara'),
    ('sultra', '', 'Sulawesi Tenggara'),

    # Sulawesi Barat
    ('polman', 'Polewali Mandar', 'Sulawesi Barat'),
    ('polewali', 'Polewali Mandar', 'Sulawesi Barat'),
    ('majene', 'Majene', 'Sulawesi Barat'),

    # Sulawesi Utara
    ('tomohon', 'Tomohon', 'Sulawesi Utara'),
    ('manado', 'Manado', 'Sulawesi Utara'),

    # Sumatera Utara
    ('dairi', 'Dairi', 'Sumatera Utara'),
    ('deli serdang', 'Deli Serdang', 'Sumatera Utara'),
    ('sumut', '', 'Sumatera Utara'),

    # Sumatera Barat
    ('agam', 'Agam', 'Sumatera Barat'),
    ('sumbar', '', 'Sumatera Barat'),

    # Sumatera Selatan
    ('pali', 'PALI', 'Sumatera Selatan'),
    ('sumsel', '', 'Sumatera Selatan'),

    # Lampung
    ('lampung', 'Lampung', 'Lampung'),

    # Banten
    ('cilegon', 'Cilegon', 'Banten'),
    ('serang', 'Serang', 'Banten'),
    ('banten', '', 'Banten'),

    # Kepulauan Riau
    ('anambas', 'Kepulauan Anambas', 'Kepulauan Riau'),

    # Gorontalo
    ('gorontalo', 'Gorontalo', 'Gorontalo'),

    # Papua
    ('nabire', 'Nabire', 'Papua Tengah'),
]


def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Get province and district IDs
    cur.execute("SELECT id, name FROM provinces")
    province_map = {row[1]: row[0] for row in cur.fetchall()}

    cur.execute("SELECT d.id, d.name, p.name FROM districts d JOIN provinces p ON d.province_id = p.id")
    district_map = {(row[1], row[2]): row[0] for row in cur.fetchall()}

    # Get unassigned articles
    cur.execute("SELECT id, title FROM incidents WHERE province_id IS NULL")
    unassigned = cur.fetchall()
    print(f"Unassigned articles: {len(unassigned)}")

    # Also need to create missing provinces/districts
    def get_or_create_province(name):
        if name in province_map:
            return province_map[name]
        cur.execute("INSERT INTO provinces (name) VALUES (%s) RETURNING id", (name,))
        pid = cur.fetchone()[0]
        province_map[name] = pid
        print(f"  Created province: {name} (id={pid})")
        return pid

    def get_or_create_district(dist_name, prov_name):
        if not dist_name:
            return None
        key = (dist_name, prov_name)
        if key in district_map:
            return district_map[key]
        prov_id = get_or_create_province(prov_name)
        cur.execute("INSERT INTO districts (name, province_id) VALUES (%s, %s) RETURNING id",
                    (dist_name, prov_id))
        did = cur.fetchone()[0]
        district_map[key] = did
        print(f"  Created district: {dist_name}, {prov_name} (id={did})")
        return did

    assigned = 0
    for art_id, title in unassigned:
        t = title.lower()
        matched = False

        for keyword, dist_name, prov_name in LOCATION_RULES:
            if keyword in t:
                prov_id = get_or_create_province(prov_name)
                dist_id = get_or_create_district(dist_name, prov_name) if dist_name else None

                cur.execute(
                    "UPDATE incidents SET province_id = %s, district_id = %s WHERE id = %s",
                    (prov_id, dist_id, art_id)
                )
                assigned += 1
                matched = True
                break

        if not matched:
            # Skip generic national articles (no location info)
            pass

    conn.commit()

    # Report
    cur.execute("SELECT COUNT(*) FROM incidents WHERE province_id IS NULL")
    still_unassigned = cur.fetchone()[0]

    cur.execute("""
        SELECT p.name, COUNT(i.id), COALESCE(SUM(i.victim_count), 0)
        FROM incidents i JOIN provinces p ON i.province_id = p.id
        GROUP BY p.name ORDER BY SUM(i.victim_count) DESC
    """)
    print(f"\nAssigned: {assigned} articles")
    print(f"Still unassigned: {still_unassigned}")
    print(f"\nUpdated province stats:")
    for row in cur.fetchall():
        print(f"  {row[2]:6d} victims | {row[1]:3d} articles | {row[0]}")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
