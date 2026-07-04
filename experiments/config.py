# -*- coding: utf-8 -*-
"""Experiment configuration - persisted across local and server."""
import os
from pathlib import Path

# GPU server
GPU_HOST = "server@100.75.203.102"
GPU_DEVICE = "cuda"

# Data paths (server)
if Path("/data/workspace").exists():
    WORKSPACE = Path("/data/workspace/drift-suppression")
else:
    WORKSPACE = Path(__file__).resolve().parent.parent / "workspace"

CORPUS_DIR = WORKSPACE / "corpus"
MODELS_DIR = WORKSPACE / "models"
RESULTS_DIR = WORKSPACE / "results"
KG_DIR = WORKSPACE / "kg"
LOGS_DIR = WORKSPACE / "logs"
CODE_DIR = WORKSPACE / "code"

for d in [CORPUS_DIR, MODELS_DIR, RESULTS_DIR, KG_DIR, LOGS_DIR, CODE_DIR]:
    d.mkdir(parents=True, exist_ok=True)

os.environ.setdefault("HF_HOME", str(WORKSPACE.parent / "huggingface_cache"))
os.environ.setdefault("TRANSFORMERS_CACHE", os.environ["HF_HOME"])

# Expanded experiment scale (vs paper draft: 52,847 docs / 50 queries)
TARGET_DOCS = 15000          # expanded corpus
TARGET_TEST_QUERIES = 200    # expanded test queries
TARGET_TRAIN_PAIRS = 25000   # weak-supervision pairs
POOLING_DEPTH = 100            # candidates per query
BATCH_SIZE_ENCODE = 64
BATCH_SIZE_TRAIN = 32
SEED = 42

# Models (use cached on server)
BGE_M3_PATH = "BAAI/bge-m3"
MINILM_PATH = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
XLM_R_LARGE = "xlm-roberta-large"

# Languages
LANGUAGES = {
    "zh": "中文",
    "en": "English",
    "ru": "Русский",
    "ar": "العربية",
    "es": "Español",
}

LANG_PAIRS = [
    ("zh", "en"), ("zh", "ru"), ("en", "ru"), ("en", "ar"),
    ("en", "es"), ("zh", "ar"), ("zh", "es"), ("ru", "ar"),
    ("ru", "es"), ("ar", "es"),
]

# BRI topic keywords (multilingual)
BRI_KEYWORDS = [
    "belt and road", "一带一路", "BRI", "silk road",
    "infrastructure investment", "跨境基础设施",
    "regional cooperation", "区域合作",
    "trade facilitation", "贸易便利化",
    "cultural exchange", "文化交流",
    "green development", "绿色发展",
    "digital silk road", "数字丝绸之路",
    "connectivity", "互联互通",
    "south-south cooperation", "南南合作",
]

GITHUB_OWNER = "liubin18911671739"
GITHUB_REPO = "drift-suppression-bri-mair"