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
- GitHub 仅同步：实验代码、`results/*.json`、配置与脚本

## 目录结构

```
/data/workspace/drift-suppression/
├── corpus/          # 语料与查询
├── results/         # 嵌入、检查点、实验结果
├── logs/            # 运行日志
└── code/            # 代码（同步自 GitHub）
```