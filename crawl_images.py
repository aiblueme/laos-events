#!/usr/bin/env python3
"""
Image crawler for laos-events site.
Downloads images from Bing and Baidu, converts to WebP, resizes, and
creates thumbnails. Uses anti-bot mitigations: random delays, UA rotation,
throttling.
"""

import os
import time
import random
import shutil
import hashlib
import logging
from pathlib import Path
from PIL import Image

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s  %(message)s")
log = logging.getLogger(__name__)

# ── Config ────────────────────────────────────────────────────────────────────
RAW_DIR   = Path("images/raw")
FULL_DIR  = Path("images/full")
THUMB_DIR = Path("images/thumbs")
THUMB_SIZE = (300, 200)
MAX_BYTES  = 1_000_000   # 1 MB
QUALITY_START = 85

for d in (RAW_DIR, FULL_DIR, THUMB_DIR):
    d.mkdir(parents=True, exist_ok=True)

# ── User-Agent pool ───────────────────────────────────────────────────────────
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
]

# ── Keywords ──────────────────────────────────────────────────────────────────
KEYWORDS = [
    ("laos_festival", "Laos festival 2026"),
    ("pi_mai_water", "Boun Pi Mai Lao New Year celebration"),
    ("luang_prabang_street", "Luang Prabang festival street"),
    ("lantern_night", "Laos lantern ceremony night"),
    ("vientiane_temple", "Vientiane temple festival Laos"),
    ("traditional_dance", "Laos traditional dance ceremony"),
    ("mekong_celebration", "Mekong river Laos celebration"),
    ("jungle_landscape", "Laos jungle nature landscape"),
    ("monks_procession", "Lao monks procession street"),
    ("market_offerings", "Laos market flowers fruit offering"),
]


def crawl_bing(keyword_slug: str, query: str, max_num: int = 10) -> None:
    """Download images from Bing for a single query."""
    try:
        from icrawler.builtin import BingImageCrawler
        dest = RAW_DIR / keyword_slug
        dest.mkdir(exist_ok=True)
        ua = random.choice(USER_AGENTS)
        crawler = BingImageCrawler(
            storage={"root_dir": str(dest)},
            downloader_threads=1,
            parser_threads=1,
        )
        crawler.crawl(
            keyword=query,
            max_num=max_num,
            min_size=(400, 300),
            overwrite=False,
        )
        log.info("Bing done: %s (%d images requested)", keyword_slug, max_num)
    except Exception as exc:
        log.warning("Bing crawl failed for '%s': %s", keyword_slug, exc)


def crawl_baidu(keyword_slug: str, query: str, max_num: int = 8) -> None:
    """Download images from Baidu for a single query."""
    try:
        from icrawler.builtin import BaiduImageCrawler
        dest = RAW_DIR / (keyword_slug + "_baidu")
        dest.mkdir(exist_ok=True)
        crawler = BaiduImageCrawler(
            storage={"root_dir": str(dest)},
            downloader_threads=1,
            parser_threads=1,
        )
        crawler.crawl(
            keyword=query,
            max_num=max_num,
            overwrite=False,
        )
        log.info("Baidu done: %s (%d images requested)", keyword_slug, max_num)
    except Exception as exc:
        log.warning("Baidu crawl failed for '%s': %s", keyword_slug, exc)


def collect_raw_images() -> list[Path]:
    """Return all image files from RAW_DIR subdirectories."""
    exts = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
    return [p for p in RAW_DIR.rglob("*") if p.suffix.lower() in exts]


def fingerprint(path: Path) -> str:
    return f"{path.stat().st_size}_{path.stat().st_size}"


def deduplicate(paths: list[Path]) -> list[Path]:
    """Remove near-duplicates by (file-size, dimensions)."""
    seen: set[str] = set()
    unique: list[Path] = []
    for p in paths:
        try:
            with Image.open(p) as img:
                key = f"{p.stat().st_size}_{img.size}"
        except Exception:
            key = str(p.stat().st_size)
        if key not in seen:
            seen.add(key)
            unique.append(p)
    log.info("Dedup: %d → %d unique images", len(paths), len(unique))
    return unique


def to_webp(src: Path, dest: Path, max_bytes: int = MAX_BYTES, quality: int = QUALITY_START) -> bool:
    """Convert src image to WebP at dest, iterating quality down until under max_bytes."""
    try:
        with Image.open(src) as img:
            if img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGBA")
            else:
                img = img.convert("RGB")
            q = quality
            while q >= 30:
                img.save(dest, "WEBP", quality=q, method=4)
                if dest.stat().st_size <= max_bytes:
                    return True
                q -= 10
            img.save(dest, "WEBP", quality=30, method=4)
            return True
    except Exception as exc:
        log.warning("Failed to convert %s: %s", src, exc)
        return False


def make_thumb(src_webp: Path, dest: Path) -> bool:
    try:
        with Image.open(src_webp) as img:
            img = img.convert("RGB")
            img.thumbnail(THUMB_SIZE, Image.LANCZOS)
            # Crop/pad to exact THUMB_SIZE
            thumb = Image.new("RGB", THUMB_SIZE, (249, 243, 227))  # cream bg
            offset = ((THUMB_SIZE[0] - img.width) // 2, (THUMB_SIZE[1] - img.height) // 2)
            thumb.paste(img, offset)
            thumb.save(dest, "WEBP", quality=80)
        return True
    except Exception as exc:
        log.warning("Thumb failed for %s: %s", src_webp, exc)
        return False


def process_images(raw_paths: list[Path]) -> list[dict]:
    """Convert raw images to webp full + thumb. Return manifest."""
    manifest = []
    for i, src in enumerate(raw_paths):
        slug = f"laos_{i:04d}"
        full_path  = FULL_DIR  / f"{slug}.webp"
        thumb_path = THUMB_DIR / f"{slug}.webp"
        if to_webp(src, full_path):
            make_thumb(full_path, thumb_path)
            manifest.append({
                "slug": slug,
                "full":  f"images/full/{slug}.webp",
                "thumb": f"images/thumbs/{slug}.webp",
            })
        if i < len(raw_paths) - 1:
            time.sleep(random.uniform(0.3, 0.8))
    return manifest


def main():
    log.info("=== Starting Laos Events Image Crawler ===")

    # Sequential crawls with random delays between keywords
    for slug, query in KEYWORDS:
        max_bing = random.randint(8, 12)
        crawl_bing(slug, query, max_num=max_bing)
        time.sleep(random.uniform(2, 6))

        max_baidu = random.randint(6, 9)
        crawl_baidu(slug, query, max_num=max_baidu)
        time.sleep(random.uniform(2, 6))

    raw = collect_raw_images()
    log.info("Total raw images collected: %d", len(raw))

    unique = deduplicate(raw)
    manifest = process_images(unique)

    log.info("=== Processing complete: %d images ready ===", len(manifest))
    log.info("Full images:  %s", FULL_DIR)
    log.info("Thumbnails:   %s", THUMB_DIR)

    # Print a simple manifest to stdout for review
    for item in manifest:
        print(f"{item['slug']}  |  {item['full']}  |  {item['thumb']}")


if __name__ == "__main__":
    main()
