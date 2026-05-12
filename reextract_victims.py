#!/usr/bin/env python3
"""
Re-extract victim counts from article titles for articles that have victim_count=0
but clearly mention a number in the title.

Strategy:
- Each article gets its own victim_count from its title (for display purposes)
- The dedup logic for STATISTICS is handled separately at query time (MAX per incident cluster)
- This makes the list view useful — every article shows its reported number
"""
import psycopg2
import re

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': 'P@ssw0rd18TraspaC',
    'dbname': 'korbanmbg',
}

# Keywords that indicate cumulative/national reports — skip these
SKIP_KEYWORDS = [
    'kpai', 'jppi', 'cisdi', 'bgn ungkap', 'bos bgn', 'kepala bgn',
    'total nasional', 'seluruh indonesia', 'sepanjang 2025',
    'video top', 'top 3 news', 'rangkuman', 'dpr minta', 'evaluasi mbg',
    'prabowo', 'istana', 'legislator',
]


def extract_victim_from_title(title: str) -> int:
    t = title.lower()

    # Skip cumulative/national articles
    if any(kw in t for kw in SKIP_KEYWORDS):
        return 0

    # Pattern: number followed by victim keyword
    matches = re.findall(
        r'(\d[\d.]*)\s*(?:siswa|orang|korban|anak|murid|santri|balita|warga|pelajar|mahasiswa)',
        t
    )
    # Also: victim keyword followed by number
    matches2 = re.findall(
        r'(?:jadi|capai|mencapai|tembus|bertambah|total|sebanyak)\s+(\d[\d.]*)',
        t
    )

    nums = []
    for m in matches + matches2:
        try:
            n = int(m.replace('.', ''))
            if 2 < n < 5000:
                nums.append(n)
        except:
            pass

    return max(nums) if nums else 0


def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Get all articles with victim_count = 0
    cur.execute("SELECT id, title FROM incidents WHERE victim_count = 0")
    rows = cur.fetchall()
    print(f"Articles with victim_count=0: {len(rows)}")

    updated = 0
    for row_id, title in rows:
        vc = extract_victim_from_title(title)
        if vc > 0:
            cur.execute("UPDATE incidents SET victim_count = %s WHERE id = %s", (vc, row_id))
            updated += 1

    conn.commit()
    print(f"Updated: {updated} articles with victim counts from titles")

    # Now show stats
    cur.execute("SELECT COUNT(*), COALESCE(SUM(victim_count), 0) FROM incidents")
    total_inc, raw_sum = cur.fetchone()

    # For accurate total, use MAX per (province, district, month) cluster
    cur.execute("""
        SELECT COALESCE(SUM(max_vc), 0) FROM (
            SELECT province_id, district_id,
                   TO_CHAR(incident_date, 'YYYY-MM') as month,
                   MAX(victim_count) as max_vc
            FROM incidents
            WHERE victim_count > 0 AND province_id IS NOT NULL
            GROUP BY province_id, district_id, TO_CHAR(incident_date, 'YYYY-MM')
        ) t
    """)
    dedup_total = cur.fetchone()[0]

    print(f"\nStats:")
    print(f"  Total articles: {total_inc}")
    print(f"  Raw sum (all victim_counts): {raw_sum}")
    print(f"  Deduplicated total (max per location+month): {dedup_total}")

    # Top articles now
    cur.execute("""
        SELECT i.id, i.victim_count, COALESCE(p.name,'?'), i.title
        FROM incidents i
        LEFT JOIN provinces p ON i.province_id = p.id
        WHERE i.victim_count > 0
        ORDER BY i.victim_count DESC
        LIMIT 20
    """)
    print(f"\nTop 20 articles by victim_count:")
    for row in cur.fetchall():
        print(f"  {row[0]:4d} | {row[1]:5d} | {row[2]:15s} | {row[3][:60]}")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
