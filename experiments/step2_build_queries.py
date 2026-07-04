#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Step 2: Build expanded multilingual test queries (200) and train pairs."""
import json
import random
from collections import Counter
from pathlib import Path

import numpy as np

from config import (
    BRI_KEYWORDS, CORPUS_DIR, LANGUAGES, SEED,
    TARGET_TEST_QUERIES, TARGET_TRAIN_PAIRS,
)

random.seed(SEED)
np.random.seed(SEED)

QUERY_TEMPLATES = {
    "zh": [
        "一带一路{topic}合作研究",
        "{topic}跨境投资政策分析",
        "丝绸之路经济带{topic}发展",
        "{topic}区域互联互通",
        "中国与沿线国家{topic}合作",
    ],
    "en": [
        "Belt and Road {topic} cooperation",
        "{topic} infrastructure investment along BRI",
        "cross-border {topic} policy analysis",
        "Silk Road economic belt {topic}",
        "regional {topic} connectivity BRI",
    ],
    "ru": [
        "сотрудничество {topic} в рамках ОПОП",
        "инвестиции в {topic} по инициативе Шёлкового пути",
        "трансграничная политика {topic}",
        "региональная связность {topic}",
        "экономический пояс {topic}",
    ],
    "ar": [
        "تعاون {topic} في مبادرة الحزام والطريق",
        "استثمار {topic} عبر الحدود",
        "سياسة {topic} الإقليمية",
        "الحزام الاقتصادي {topic}",
        "الربط الإقليمي {topic}",
    ],
    "es": [
        "cooperación {topic} en la Franja y la Ruta",
        "inversión en {topic} de infraestructura BRI",
        "política transfronteriza de {topic}",
        "conectividad regional {topic}",
        "cinturón económico {topic}",
    ],
}

TOPICS = [
    "trade", "infrastructure", "energy", "environment", "culture",
    "education", "finance", "technology", "agriculture", "tourism",
    "贸易", "基础设施", "能源", "环境", "文化",
    "教育", "金融", "科技", "农业", "旅游",
]

QUERY_TYPES = {
    "literature_discovery": 0.50,
    "fact_query": 0.20,
    "relation_exploration": 0.18,
    "trend_analysis": 0.12,
}


def assign_query_type():
    r = random.random()
    cum = 0
    for qt, p in QUERY_TYPES.items():
        cum += p
        if r <= cum:
            return qt
    return "literature_discovery"


def build_queries(corpus):
    queries = []
    langs = list(QUERY_TEMPLATES.keys())
    for i in range(TARGET_TEST_QUERIES):
        lang = langs[i % len(langs)]
        topic = random.choice(TOPICS)
        template = random.choice(QUERY_TEMPLATES[lang])
        text = template.format(topic=topic)
        qtype = assign_query_type()
        # Target langs for retrieval: all except query lang
        target_langs = [l for l in langs if l != lang]
        queries.append({
            "id": f"Q{i+1:04d}",
            "text": text,
            "lang": lang,
            "type": qtype,
            "topic": topic,
            "target_langs": target_langs,
        })
    return queries


def label_relevance(query, doc, threshold_topic=True):
    """Weak relevance: topic overlap + BRI keyword in title/abstract."""
    text = (doc.get("title", "") + " " + doc.get("abstract", "")).lower()
    topic = query.get("topic", "").lower()
    score = 0.0
    if topic and topic in text:
        score += 0.5
    for kw in BRI_KEYWORDS:
        if kw.lower() in text:
            score += 0.15
            break
    # Language bonus if cross-lingual
    if doc.get("lang") in query.get("target_langs", []):
        score += 0.1
    # Concept overlap
    for c in doc.get("concepts", []):
        if topic in c.lower():
            score += 0.2
            break
    return min(1.0, score)


def build_qd_pairs(corpus, queries):
    pairs = []
    for q in queries:
        for doc in corpus:
            rel = label_relevance(q, doc)
            if rel >= 0.3:
                pairs.append({
                    "query_id": q["id"],
                    "doc_id": doc["id"],
                    "relevance": round(rel, 2),
                    "query_lang": q["lang"],
                    "doc_lang": doc["lang"],
                })
    random.shuffle(pairs)
    return pairs[:TARGET_TRAIN_PAIRS]


def main():
    print("=" * 60)
    print(f"Step 2: Build Queries (test={TARGET_TEST_QUERIES})")
    print("=" * 60)

    with open(CORPUS_DIR / "bri_mair_corpus.json") as f:
        corpus = json.load(f)

    queries = build_queries(corpus)
    qd_pairs = build_qd_pairs(corpus, queries)

    out_q = CORPUS_DIR / "test_queries.json"
    out_p = CORPUS_DIR / "qd_pairs.json"
    with open(out_q, "w", encoding="utf-8") as f:
        json.dump(queries, f, ensure_ascii=False, indent=2)
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(qd_pairs, f, ensure_ascii=False, indent=2)

    stats = {
        "num_queries": len(queries),
        "query_langs": dict(Counter(q["lang"] for q in queries)),
        "query_types": dict(Counter(q["type"] for q in queries)),
        "num_pairs": len(qd_pairs),
        "avg_relevance": float(np.mean([p["relevance"] for p in qd_pairs])) if qd_pairs else 0,
    }
    with open(CORPUS_DIR / "query_stats.json", "w") as f:
        json.dump(stats, f, indent=2)

    print(f"Saved {len(queries)} queries, {len(qd_pairs)} pairs")
    print(f"Stats: {stats}")


if __name__ == "__main__":
    main()