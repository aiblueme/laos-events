#!/usr/bin/env python3
"""Fetch clean CC-licensed image replacements from Wikimedia Commons."""
import urllib.request
import urllib.parse
import json
import time
import os
from io import BytesIO
from PIL import Image

UA = "LaosEventsSite/1.0 (educational)"

def wiki_search(query, n=5):
    params = urllib.parse.urlencode({
        "action": "query",
        "generator": "search",
        "gsrnamespace": 6,
        "gsrsearch": query,
        "gsrlimit": n,
        "prop": "imageinfo",
        "iiprop": "url|size",
        "format": "json",
    })
    url = f"https://commons.wikimedia.org/w/api.php?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.load(r)
        pages = data.get("query", {}).get("pages", {})
        results = []
        for page in pages.values():
            ii = page.get("imageinfo", [{}])[0]
            src = ii.get("url", "")
            w   = ii.get("width", 0)
            h   = ii.get("height", 0)
            if src and w >= 800 and h >= 500:
                results.append((src, w, h))
        return sorted(results, key=lambda x: x[1] * x[2], reverse=True)
    except Exception as e:
        print(f"  search error: {e}")
        return []


def download_convert(url, dest_full, dest_thumb):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read()
    img = Image.open(BytesIO(raw)).convert("RGB")

    # full image ≤1MB
    q = 85
    while q >= 30:
        img.save(dest_full, "WEBP", quality=q)
        if os.path.getsize(dest_full) <= 1_000_000:
            break
        q -= 10

    # thumbnail 300×200
    thumb = img.copy()
    thumb.thumbnail((300, 200), Image.LANCZOS)
    canvas = Image.new("RGB", (300, 200), (249, 243, 227))
    off = ((300 - thumb.width) // 2, (200 - thumb.height) // 2)
    canvas.paste(thumb, off)
    canvas.save(dest_thumb, "WEBP", quality=80)
    print(f"  ✓ saved {dest_full} ({os.path.getsize(dest_full)//1024}KB)")
    return True


TARGETS = [
    (
        "Lao New Year Boun Pi Mai water festival celebration",
        "images/full/laos_0001.webp",
        "images/thumbs/laos_0001.webp",
    ),
    (
        "Buddhist monks alms giving procession Luang Prabang",
        "images/full/laos_0002.webp",
        "images/thumbs/laos_0002.webp",
    ),
]

for query, full_path, thumb_path in TARGETS:
    print(f"\nQuery: {query}")
    results = wiki_search(query)
    print(f"  {len(results)} candidates")
    for url, w, h in results:
        print(f"  → {w}x{h}  {url[:90]}")
        try:
            if download_convert(url, full_path, thumb_path):
                break
        except Exception as e:
            print(f"  ✗ {e}")
        time.sleep(1)
    else:
        print(f"  No replacement obtained for {full_path}")
    time.sleep(2)

print("\nDone.")
