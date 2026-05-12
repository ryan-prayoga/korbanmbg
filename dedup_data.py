#!/usr/bin/env python3
"""
Deduplicate victim counts in the database.
For each cluster of articles about the same incident (same province + district + similar victim count),
keep only the highest victim_count on one article, set the rest to 0.
Also marks articles that are clearly cumulative national reports.
"""
import psycopg2

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': 'P@ssw0rd18TraspaC',
    'dbname': 'korbanmbg',
}

# Keywords that indicate cumulative/national reports (not single incidents)
CUMULATIVE_KEYWORDS = [
    'kpai', 'jppi', 'cisdi', 'bgn ungkap', 'bos bgn', 'kepala bgn',
    'total korban', 'total keracunan', 'capai ribuan', 'tembus ribuan',
    'sepanjang 2025', 'selama 2025', 'sejak januari',
    'dpr minta', 'legislator', 'evaluasi mbg', 'prabowo',
    'video top 3', 'top 3 news', 'rangkuman',
]


def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Step 1: Zero out cumulative/national report articles
    cur.execute("SELECT id, title, victim_count FROM incidents WHERE victim_count > 0")
    rows = cur.fetchall()

    zeroed_cumulative = 0
    for row_id, title, vc in rows:
        t = title.lower()
        if any(kw in t for kw in CUMULATIVE_KEYWORDS):
            cur.execute("UPDATE incidents SET victim_count = 0 WHERE id = %s", (row_id,))
            zeroed_cumulative += 1

    print(f"Step 1: Zeroed {zeroed_cumulative} cumulative/national report articles")

    # Step 2: Deduplicate by province + district + similar victim count
    # Group articles by (province_id, district_id) and find clusters with same/similar victim_count
    cur.execute("""
        SELECT id, title, victim_count, province_id, district_id, incident_date
        FROM incidents 
        WHERE victim_count > 0 AND province_id IS NOT NULL
        ORDER BY province_id, district_id, incident_date
    """)
    all_incidents = cur.fetchall()

    # Group by (province_id, district_id)
    from collections import defaultdict
    groups = defaultdict(list)
    for row in all_incidents:
        key = (row[3], row[4])  # province_id, district_id
        groups[key].append({
            'id': row[0],
            'title': row[1],
            'victim_count': row[2],
            'date': row[5],
        })

    zeroed_dupes = 0
    for key, articles in groups.items():
        if len(articles) <= 1:
            continue

        # Within each location group, find clusters of similar victim counts
        # Sort by victim_count descending
        articles.sort(key=lambda x: x['victim_count'], reverse=True)

        # Cluster: if victim counts are within 20% of each other, they're about the same incident
        seen_clusters = []
        for art in articles:
            matched = False
            for cluster in seen_clusters:
                ref_count = cluster[0]['victim_count']
                if ref_count > 0 and abs(art['victim_count'] - ref_count) / ref_count < 0.25:
                    cluster.append(art)
                    matched = True
                    break
            if not matched:
                seen_clusters.append([art])

        # For each cluster with >1 article, keep only the highest, zero the rest
        for cluster in seen_clusters:
            if len(cluster) <= 1:
                continue
            # Keep the first (highest victim_count), zero the rest
            for art in cluster[1:]:
                cur.execute("UPDATE incidents SET victim_count = 0 WHERE id = %s", (art['id'],))
                zeroed_dupes += 1

    print(f"Step 2: Zeroed {zeroed_dupes} duplicate articles (same incident, multiple reports)")

    conn.commit()

    # Report new totals
    cur.execute("SELECT COUNT(*), COALESCE(SUM(victim_count), 0) FROM incidents WHERE victim_count > 0")
    active_count, total_victims = cur.fetchone()
    cur.execute("SELECT COUNT(*) FROM incidents")
    total_articles = cur.fetchone()[0]

    print(f"\nResult:")
    print(f"  Total articles: {total_articles}")
    print(f"  Articles with victim_count > 0: {active_count}")
    print(f"  Sum of victim_count (deduplicated): {total_victims}")

    # Show top incidents now
    cur.execute("""
        SELECT i.victim_count, COALESCE(p.name, '?'), COALESCE(d.name, '?'), i.title
        FROM incidents i
        LEFT JOIN provinces p ON i.province_id = p.id
        LEFT JOIN districts d ON i.district_id = d.id
        WHERE i.victim_count > 0
        ORDER BY i.victim_count DESC
        LIMIT 15
    """)
    print(f"\nTop 15 incidents (deduplicated):")
    for row in cur.fetchall():
        print(f"  {row[0]:5d} | {row[1]:15s} | {row[2]:20s} | {row[3][:60]}")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
