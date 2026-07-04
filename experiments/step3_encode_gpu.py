#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Step 3: GPU encoding of corpus and queries with BGE-M3."""
import json
import time
from pathlib import Path

import numpy as np
import torch

from config import BATCH_SIZE_ENCODE, CORPUS_DIR, GPU_DEVICE, MODELS_DIR, RESULTS_DIR, SEED

np.random.seed(SEED)
torch.manual_seed(SEED)

BGE_SNAPSHOT = "/data/workspace/huggingface_cache/hub/models--BAAI--bge-m3/snapshots"


def find_snapshot():
    base = Path(BGE_SNAPSHOT)
    if base.exists():
        snaps = sorted(base.iterdir())
        if snaps:
            return str(snaps[-1])
    return "BAAI/bge-m3"


def main():
    print("=" * 60)
    print("Step 3: GPU Encoding (BGE-M3)")
    print("=" * 60)

    device = GPU_DEVICE if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")
    if device == "cuda":
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")

    from sentence_transformers import SentenceTransformer

    model_path = find_snapshot()
    print(f"Loading model: {model_path}")
    t0 = time.time()
    model = SentenceTransformer(model_path, device=device)
    dim = model.get_sentence_embedding_dimension()
    print(f"Embedding dim: {dim}, loaded in {time.time()-t0:.1f}s")

    with open(CORPUS_DIR / "bri_mair_corpus.json") as f:
        corpus = json.load(f)
    with open(CORPUS_DIR / "test_queries.json") as f:
        queries = json.load(f)

    doc_texts = [d["title"] + ". " + d.get("abstract", "")[:500] for d in corpus]
    q_texts = [q["text"] for q in queries]

    print(f"Encoding {len(doc_texts)} documents (batch={BATCH_SIZE_ENCODE})...")
    t1 = time.time()
    doc_embs = model.encode(
        doc_texts, batch_size=BATCH_SIZE_ENCODE, show_progress_bar=True,
        normalize_embeddings=True, convert_to_numpy=True,
    )
    doc_time = time.time() - t1
    if device == "cuda":
        peak_vram = torch.cuda.max_memory_allocated() / 1e9
        torch.cuda.reset_peak_memory_stats()
    else:
        peak_vram = 0

    print(f"Encoding {len(q_texts)} queries...")
    t2 = time.time()
    q_embs = model.encode(
        q_texts, batch_size=BATCH_SIZE_ENCODE, show_progress_bar=True,
        normalize_embeddings=True, convert_to_numpy=True,
    )
    q_time = time.time() - t2

    out = RESULTS_DIR / "embeddings"
    out.mkdir(parents=True, exist_ok=True)
    np.save(out / "doc_embeddings.npy", doc_embs)
    np.save(out / "query_embeddings.npy", q_embs)
    with open(out / "doc_ids.json", "w") as f:
        json.dump([d["id"] for d in corpus], f)
    with open(out / "query_ids.json", "w") as f:
        json.dump([q["id"] for q in queries], f)

    meta = {
        "model": model_path,
        "dim": dim,
        "num_docs": len(corpus),
        "num_queries": len(queries),
        "doc_encode_time_s": round(doc_time, 2),
        "query_encode_time_s": round(q_time, 2),
        "peak_vram_gb": round(peak_vram, 2),
        "batch_size": BATCH_SIZE_ENCODE,
        "device": device,
    }
    with open(out / "encode_meta.json", "w") as f:
        json.dump(meta, f, indent=2)

    print(f"Saved embeddings to {out}")
    print(f"Meta: {meta}")


if __name__ == "__main__":
    main()