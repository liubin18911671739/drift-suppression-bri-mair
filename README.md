# DriftSup: 多语种学术文献检索语义漂移抑制

## 环境配置（持久化）

| 项目 | 配置 |
|------|------|
| GPU 服务器 | `server@100.75.203.102` |
| GPU | NVIDIA RTX 3090 (24GB) |
| 数据目录 | `/data/workspace/drift-suppression/` |
| HuggingFace 缓存 | `/data/workspace/huggingface_cache/` |
| GitHub | https://github.com/liubin18911671739/drift-suppression-bri-mair |

## 扩大实验规模（RTX 3090 实测）

| 参数 | 原稿 | 扩大后（实测） |
|------|------|----------------|
| 文献数 | 52,847 | **15,000** (OpenAlex) |
| 测试查询 | 50 | **200** |
| 训练 q-d 对 | 12,350 | **25,000** |
| 文档编码耗时 | — | **164.6s** (batch=64, VRAM 3.83GB) |
| DriftSup训练 | — | **21.7s** (50 epochs) |

## 实测结果摘要

| 方法 | nDCG@10 | Drift-Score |
|------|---------|-------------|
| BGE-M3 | 0.0507 | 0.7086 |
| BGE-M3+KG | **0.0651** | **0.5520** |
| DriftSup+KG | 0.0567 | 0.6011 |

## 运行

```bash
ssh server@100.75.203.102
cd /data/workspace/drift-suppression/code/experiments
bash run_all.sh
```

## 论文与 GitHub 策略

- **论文（Word/PDF）仅存本地**，不上传 GitHub
- **GitHub 同步**：实验代码 + `data/` 完整数据集（语料、嵌入、检查点、结果、日志）

## 可复现数据包（`data/`）

| 内容 | 规模 | 说明 |
|------|------|------|
| `corpus/bri_mair_corpus.json` | 15,000 篇 | OpenAlex 一带一路学术文献 |
| `corpus/test_queries.json` | 200 组 | 五语种测试查询 |
| `results/experiment_results.json` | — | 完整评测指标 |
| `results/embeddings/` | 59MB | BGE-M3 预计算向量 |
| `results/checkpoints/` | 3.3MB | DriftSup 模型权重 |

详见 [data/README.md](data/README.md)

## 服务器目录结构

```
/data/workspace/drift-suppression/   ← 与 GitHub data/ 同步
├── corpus/
├── results/
├── logs/
└── code/                            ← 与 GitHub experiments/ 同步
```