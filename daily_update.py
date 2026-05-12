#!/usr/bin/env python3
"""Daily auto-update: fetch new articles from Google News RSS, then rebuild unique_incidents."""
import subprocess
import sys
import psycopg2
from datetime import datetime

DB_CONFIG = {
    'host': 'localhost', 'port': 5432, 'user': 'postgres',
    'password': '***REDACTED***', 'dbname': 'korbanmbg',
}

def run_import():
    """Run the Google News RSS importer."""
    result = subprocess.run(
        [sys.executable, '/home/ubuntu/projects/korbanmbg/import_gnews.py'],
        capture_output=True, text=True, timeout=300
    )
    print(result.stdout[-500:] if result.stdout else '(no output)')
    if result.returncode != 0:
        print(f'WARN: import exited {result.returncode}')
        if result.stderr:
            print(result.stderr[-300:])

def rebuild_unique_incidents():
    """Rebuild unique_incidents table from articles."""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # Clear and rebuild
    cur.execute('TRUNCATE unique_incidents CASCADE')
    cur.execute('TRUNCATE incident_articles')
    
    # Fetch all articles with province + date
    cur.execute('''
        SELECT id, province_id, district_id, incident_date, victim_count,
               hospitalized, deaths, location_detail, menu_items, symptoms
        FROM incidents
        WHERE province_id IS NOT NULL AND incident_date IS NOT NULL
        ORDER BY province_id, district_id, incident_date
    ''')
    articles = cur.fetchall()
    
    # Group into clusters: same province + district, dates within 7 days
    clusters = []
    current_cluster = []
    
    for art in articles:
        art_id, prov_id, dist_id, inc_date, vc, hosp, deaths, loc, menu, symp = art
        
        if not current_cluster:
            current_cluster = [art]
            continue
        
        last = current_cluster[-1]
        same_prov = (prov_id == last[1])
        same_dist = (dist_id == last[2]) or (dist_id is None and last[2] is None)
        date_close = abs((inc_date - last[3]).days) <= 7 if inc_date and last[3] else False
        
        if same_prov and same_dist and date_close:
            current_cluster.append(art)
        else:
            clusters.append(current_cluster)
            current_cluster = [art]
    
    if current_cluster:
        clusters.append(current_cluster)
    
    # Insert unique incidents
    for cluster in clusters:
        max_vc = max(a[4] for a in cluster)
        max_hosp = max(a[5] for a in cluster)
        max_deaths = max(a[6] for a in cluster)
        dates = [a[3] for a in cluster if a[3]]
        first_date = min(dates) if dates else None
        last_date = max(dates) if dates else None
        prov_id = cluster[0][1]
        dist_id = cluster[0][2]
        loc = next((a[7] for a in cluster if a[7]), None)
        menu = next((a[8] for a in cluster if a[8]), None)
        symp = next((a[9] for a in cluster if a[9]), None)
        
        cur.execute('''
            INSERT INTO unique_incidents 
                (province_id, district_id, incident_date, victim_count, hospitalized, deaths,
                 location_detail, menu_items, symptoms, article_count, first_reported, last_reported)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (prov_id, dist_id, first_date, max_vc, max_hosp, max_deaths,
              loc, menu, symp, len(cluster), first_date, last_date))
        
        ui_id = cur.fetchone()[0]
        for art in cluster:
            cur.execute('INSERT INTO incident_articles (unique_incident_id, article_id) VALUES (%s, %s) ON CONFLICT DO NOTHING',
                       (ui_id, art[0]))
    
    conn.commit()
    
    # Stats
    cur.execute('SELECT COUNT(*) FROM unique_incidents')
    total_ui = cur.fetchone()[0]
    cur.execute('SELECT SUM(victim_count) FROM unique_incidents')
    total_vc = cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM incidents')
    total_art = cur.fetchone()[0]
    
    print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M")}] Rebuild done: {total_art} articles → {total_ui} unique incidents, {total_vc:,} victims')
    conn.close()

if __name__ == '__main__':
    print(f'=== KorbanMBG Daily Update: {datetime.now().strftime("%Y-%m-%d %H:%M")} ===')
    run_import()
    rebuild_unique_incidents()
    print('Done.')
