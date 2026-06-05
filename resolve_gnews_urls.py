#!/usr/bin/env python3
"""
Resolve Google News (CBMi) redirect URLs ke URL artikel asli, lalu update DB.

Kenapa perlu: format CBMi baru tidak bisa di-decode offline (protobuf opaque),
harus lewat batchexecute RPC Google News. Script ini:
  - ambil semua incidents dengan source_url mengandung news.google.com
  - resolve satu per satu (dengan rate-limit + retry)
  - update source_url ke URL asli kalau berhasil; kalau gagal, biarkan URL lama
  - aman di-resume: URL yang sudah ke-resolve tidak match query lagi

Pemakaian:
  python3 resolve_gnews_urls.py            # backfill semua
  python3 resolve_gnews_urls.py --limit 20 # test sample
"""
import os
import re
import sys
import json
import time
import argparse
import requests
import psycopg2

DB_CONFIG = {
    'host': 'localhost', 'port': 5432, 'user': 'postgres',
    'password': os.environ.get('DB_PASS', ''), 'dbname': 'korbanmbg',
}

BASE = "https://news.google.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120 Safari/537.36",
}
DELAY = float(os.environ.get('GNEWS_DELAY', '1.2'))  # detik antar request


def resolve(article_url, timeout=20):
    """Return URL asli atau None kalau gagal."""
    m = re.search(r"/articles/([^?]+)", article_url)
    if not m:
        return None
    gn_id = m.group(1)

    page = requests.get(f"{BASE}/articles/{gn_id}", headers=HEADERS, timeout=timeout)
    text = page.text
    sig_m = re.search(r'data-n-a-sg="([^"]+)"', text)
    ts_m = re.search(r'data-n-a-ts="([^"]+)"', text)
    if not sig_m or not ts_m:
        return None
    sig, ts = sig_m.group(1), ts_m.group(1)

    inner = [
        "garturlreq",
        [
            ["X", "X", ["X", "X"], None, None, 1, 1, "US:en", None, 1,
             None, None, None, None, None, 0, 1],
            "X", "X", 1, [1, 1, 1], 1, 1, None, 0, 0, None, 0,
        ],
        gn_id, int(ts), sig,
    ]
    payload = [[["Fbv4je", json.dumps(inner), None, "generic"]]]
    body = "f.req=" + requests.utils.quote(json.dumps(payload))

    resp = requests.post(
        f"{BASE}/_/DotsSplashUi/data/batchexecute",
        data=body,
        headers={**HEADERS,
                 "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"},
        timeout=timeout,
    )
    for line in resp.text.split("\n"):
        if "http" not in line:
            continue
        try:
            arr = json.loads(line)
        except Exception:
            continue
        for item in arr:
            if isinstance(item, list) and len(item) > 2 and item[2]:
                try:
                    parsed = json.loads(item[2])
                except Exception:
                    continue
                if isinstance(parsed, list):
                    for el in parsed:
                        if isinstance(el, str) and el.startswith("http"):
                            return el
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="batasi jumlah (0=semua)")
    args = ap.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    q = ("SELECT id, source_url FROM incidents "
         "WHERE source_url LIKE '%news.google.com%' ORDER BY id")
    if args.limit:
        q += f" LIMIT {args.limit}"
    cur.execute(q)
    rows = cur.fetchall()
    total = len(rows)
    print(f"[gnews-resolve] {total} URL untuk di-resolve (delay={DELAY}s)", flush=True)

    ok = fail = 0
    for i, (inc_id, url) in enumerate(rows, 1):
        try:
            real = resolve(url)
        except Exception as e:
            real = None
            print(f"  [{i}/{total}] id={inc_id} ERR {e}", flush=True)

        if real and "news.google.com" not in real:
            cur.execute("UPDATE incidents SET source_url=%s WHERE id=%s", (real, inc_id))
            conn.commit()
            ok += 1
            if i % 25 == 0 or args.limit:
                print(f"  [{i}/{total}] OK -> {real[:70]}", flush=True)
        else:
            fail += 1

        time.sleep(DELAY)

    cur.close()
    conn.close()
    print(f"[gnews-resolve] selesai: {ok} resolved, {fail} gagal/dilewati", flush=True)


if __name__ == "__main__":
    main()
