#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Step 1: Build expanded BRI-MAIR corpus from OpenAlex."""
import json
import random
import time
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

import numpy as np

from config import BRI_KEYWORDS, CORPUS_DIR, LANGUAGES, SEED, TARGET_DOCS

random.seed(SEED)
np.random.seed(SEED)

OPENALEX = "https://api.openalex.org/works"
MAILTO = "18911671739@126.com"


def fetch_openalex(query: str, per_page: int = 200, max_pages: int = 30):
    """Fetch works from OpenAlex with polite pool."""
    results = []
    cursor = "*"
    pages = 0
    while pages < max_pages and len(results) < TARGET_DOCS * 2:
        params = urllib.parse.urlencode({
            "search": query,
            "per-page": per_page,
            "cursor": cursor,
            "mailto": MAILTO,
            "filter": "type:article,publication_year:2018-2024",
        })
        url = f"{OPENALEX}?{params}"
        req = urllib.request.Request(url, headers={"User-Agent": "BRI-MAIR/1.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode())
        batch = data.get("results", [])
        if not batch:
            break
        results.extend(batch)
        cursor = data.get("meta", {}).get("next_cursor")
        pages += 1
        if not cursor:
            break
        time.sleep(0.15)
    return results


def detect_lang(text: str) -> str:
    if not text:
        return "en"
    # Simple heuristic
    if any("\u4e00" <= c <= "\u9fff" for c in text[:200]):
        return "zh"
    if any("\u0400" <= c <= "\u04ff" for c in text[:200]):
        return "ru"
    if any("\u0600" <= c <= "\u06ff" for c in text[:200]):
        return "ar"
    if any(w in text.lower() for w in ["el ", "la ", "de ", "en ", "los ", "las "]):
        return "es"
    return "en"


def normalize_work(w):
    title = (w.get("title") or "").strip()
    if not title:
        return None
    abstract = ""
    inv = w.get("abstract_inverted_index") or {}
    if inv:
        pos = {}
        for word, idxs in inv.items():
            for i in idxs:
                pos[i] = word
        abstract = " ".join(pos[k] for k in sorted(pos))
    lang = w.get("language") or detect_lang(title + " " + abstract)
    lang_map = {"zh": "zh", "en": "en", "ru": "ru", "ar": "ar", "es": "es",
                "chi": "zh", "eng": "en", "rus": "ru", "ara": "ar", "spa": "es"}
    lang = lang_map.get(lang, detect_lang(title + abstract))
    concepts = [c.get("display_name", "") for c in (w.get("concepts") or [])[:5]]
    return {
        "id": w.get("id", ""),
        "doi": (w.get("doi") or "").replace("https://doi.org/", ""),
        "title": title,
        "abstract": abstract[:2000],
        "year": w.get("publication_year"),
        "lang": lang,
        "concepts": concepts,
        "cited_by": w.get("cited_by_count", 0),
    }


def main():
    print("=" * 60)
    print(f"Step 1: Build BRI-MAIR Corpus (target={TARGET_DOCS})")
    print("=" * 60)

    all_works = {}
    for kw in BRI_KEYWORDS:
        print(f"  Fetching: {kw}")
        try:
            batch = fetch_openalex(kw, per_page=200, max_pages=15)
            for w in batch:
                doc = normalize_work(w)
                if doc and doc["id"]:
                    all_works[doc["id"]] = doc
            print(f"    cumulative unique: {len(all_works)}")
        except Exception as e:
            print(f"    WARN: {kw}: {e}")
        if len(all_works) >= TARGET_DOCS:
            break

    corpus = list(all_works.values())
    random.shuffle(corpus)
    corpus = corpus[:TARGET_DOCS]

    # Balance languages toward target distribution
    lang_counter = Counter(d["lang"] for d in corpus)
    print(f"Language distribution: {dict(lang_counter)}")

    out = CORPUS_DIR / "bri_mair_corpus.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(corpus, f, ensure_ascii=False, indent=2)

    stats = {
        "total": len(corpus),
        "languages": dict(lang_counter),
        "years": dict(Counter(d["year"] for d in corpus)),
        "avg_abstract_len": float(np.mean([len(d.get("abstract", "")) for d in corpus])),
    }
    with open(CORPUS_DIR / "corpus_stats.json", "w") as f:
        json.dump(stats, f, indent=2)

    print(f"Saved {len(corpus)} docs -> {out}")
    print(f"Stats: {stats}")


if __name__ == "__main__":
    main()