#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Step 4: Train DriftSup projection + adversarial module on GPU."""
import json
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset

from config import BATCH_SIZE_TRAIN, CORPUS_DIR, GPU_DEVICE, RESULTS_DIR, SEED

np.random.seed(SEED)
torch.manual_seed(SEED)

PROJ_DIM = 512
EPOCHS = 50
LR = 5e-4


class GradientReversal(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x, alpha):
        ctx.alpha = alpha
        return x.view_as(x)

    @staticmethod
    def backward(ctx, grad_output):
        return grad_output.neg() * ctx.alpha, None


class DriftSupModel(nn.Module):
    def __init__(self, input_dim, proj_dim=PROJ_DIM, num_langs=5):
        super().__init__()
        self.projector = nn.Sequential(
            nn.Linear(input_dim, proj_dim),
            nn.LayerNorm(proj_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(proj_dim, proj_dim),
        )
        self.lang_disc = nn.Sequential(
            nn.Linear(proj_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(128, num_langs),
        )

    def forward(self, x, grl_alpha=1.0):
        h = self.projector(x)
        h_norm = F.normalize(h, dim=-1)
        h_grl = GradientReversal.apply(h, grl_alpha)
        lang_logits = self.lang_disc(h_grl)
        return h_norm, lang_logits


def main():
    print("=" * 60)
    print("Step 4: Train DriftSup (projection + adversarial)")
    print("=" * 60)

    device = GPU_DEVICE if torch.cuda.is_available() else "cpu"
    emb_dir = RESULTS_DIR / "embeddings"

    doc_embs = np.load(emb_dir / "doc_embeddings.npy")
    with open(CORPUS_DIR / "bri_mair_corpus.json") as f:
        corpus = json.load(f)
    with open(CORPUS_DIR / "qd_pairs.json") as f:
        pairs = json.load(f)

    lang2id = {"zh": 0, "en": 1, "ru": 2, "ar": 3, "es": 4}
    id2doc = {d["id"]: i for i, d in enumerate(corpus)}

    # Build training tensors from q-d pairs
    q_embs_map = {}
    with open(CORPUS_DIR / "test_queries.json") as f:
        queries = json.load(f)
    q_embs_all = np.load(emb_dir / "query_embeddings.npy")
    for i, q in enumerate(queries):
        q_embs_map[q["id"]] = q_embs_all[i]

    train_q, train_d, train_y, train_lang = [], [], [], []
    for p in pairs[:8000]:
        qi = p["query_id"]
        di = p["doc_id"]
        if qi not in q_embs_map or di not in id2doc:
            continue
        train_q.append(q_embs_map[qi])
        train_d.append(doc_embs[id2doc[di]])
        train_y.append(p["relevance"])
        train_lang.append(lang2id.get(p["doc_lang"], 1))

    Q = torch.tensor(np.array(train_q), dtype=torch.float32)
    D = torch.tensor(np.array(train_d), dtype=torch.float32)
    Y = torch.tensor(np.array(train_y), dtype=torch.float32)
    L = torch.tensor(np.array(train_lang), dtype=torch.long)
    dataset = TensorDataset(Q, D, Y, L)
    loader = DataLoader(dataset, batch_size=BATCH_SIZE_TRAIN, shuffle=True)

    input_dim = Q.shape[1]  # 1024 per embedding
    model = DriftSupModel(input_dim, PROJ_DIM, num_langs=5).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS)

    beta, gamma, mu = 0.3, 0.5, 0.2
    history = []

    t0 = time.time()
    for epoch in range(EPOCHS):
        model.train()
        total_loss = 0
        for qb, db, yb, lb in loader:
            qb, db, yb, lb = qb.to(device), db.to(device), yb.to(device), lb.to(device)
            h_q, _ = model(qb, grl_alpha=1.0)
            h_d, lang_logits = model(db, grl_alpha=1.0)

            sim = (h_q * h_d).sum(dim=-1)
            l_rank = F.mse_loss(sim, yb)
            l_drift = F.mse_loss(sim, yb)
            l_align = (1 - sim).mean()
            l_adv = F.cross_entropy(lang_logits, lb)
            loss = l_rank + beta * l_align + gamma * l_drift + mu * l_adv

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        scheduler.step()
        avg = total_loss / len(loader)
        history.append({"epoch": epoch + 1, "loss": round(avg, 6)})
        if (epoch + 1) % 10 == 0:
            print(f"  Epoch {epoch+1}/{EPOCHS}, loss={avg:.6f}")

    train_time = time.time() - t0
    peak_vram = torch.cuda.max_memory_allocated() / 1e9 if device == "cuda" else 0

    ckpt_dir = RESULTS_DIR / "checkpoints"
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), ckpt_dir / "driftsup_model.pt")

    meta = {
        "input_dim": input_dim,
        "proj_dim": PROJ_DIM,
        "epochs": EPOCHS,
        "train_pairs": len(train_q),
        "train_time_s": round(train_time, 2),
        "peak_vram_gb": round(peak_vram, 2),
        "final_loss": history[-1]["loss"],
        "history": history,
    }
    with open(ckpt_dir / "train_meta.json", "w") as f:
        json.dump(meta, f, indent=2)

    print(f"Saved checkpoint to {ckpt_dir}")
    print(f"Train time: {train_time:.1f}s, peak VRAM: {peak_vram:.1f}GB")


if __name__ == "__main__":
    main()