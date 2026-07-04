# BRI-MAIR 实验数据（可复现支撑包）

本目录同步自 GPU 服务器 `/data/workspace/drift-suppression/`，为高校图书馆与情报机构提供**可复现**的多语种学术文献检索语义漂移抑制实验数据。

## 数据来源与采集

- **语料**：OpenAlex API，关键词覆盖"一带一路"、BRI、区域合作、跨境基础设施等 19 组多语种检索词
- **时间范围**：2018—2024 年学术文章
- **采集脚本**：`experiments/step1_build_corpus.py`
- **GPU 编码**：BGE-M3（`experiments/step3_encode_gpu.py`，RTX 3090 实测）

## 目录说明

```
data/
├── corpus/
│   ├── bri_mair_corpus.json    # 15,000 篇文献元数据（标题、摘要、语种、概念）
│   ├── test_queries.json       # 200 组多语种测试查询
│   ├── qd_pairs.json           # 25,000 组弱监督查询—文档相关性对
│   ├── corpus_stats.json       # 语料统计
│   └── query_stats.json        # 查询统计
├── results/
│   ├── experiment_results.json # 完整实验指标（nDCG、MAP、Drift-Score、消融）
│   ├── embeddings/             # BGE-M3 预计算向量（可跳过编码直接复现评估）
│   └── checkpoints/            # DriftSup 训练检查点
└── logs/                       # 五步流水线运行日志
```

## 语料概况（实测）

| 项目 | 数值 |
|------|------|
| 文献总数 | 15,000 |
| 测试查询 | 200（中/英/俄/阿/西 五语种） |
| 训练 q-d 对 | 25,000 |
| 语言分布 | 英语 84%、中文 13%、西班牙语 3%、俄语 0.4%、阿拉伯语 0.05% |

## 核心实验结果（RTX 3090 实测）

| 方法 | nDCG@10 | Drift-Score |
|------|---------|-------------|
| BGE-M3 | 0.0507 | 0.7086 |
| BGE-M3+KG | **0.0651** | **0.5520** |
| DriftSup+KG | 0.0567 | 0.6011 |

KG 增强使 Drift-Score 降低 **22.1%**，为图书馆多语种专题文献发现提供量化基准。

## 复现步骤

```bash
# 1. 克隆仓库
git clone https://github.com/liubin18911671739/drift-suppression-bri-mair.git
cd drift-suppression-bri-mair

# 2. 若已有 data/ 目录，可跳过 step1-3，直接运行评估
cd experiments
python step5_run_experiments.py

# 3. 完整重跑（需 GPU + OpenAlex 网络）
bash run_all.sh
```

## 引用与使用

数据遵循 OpenAlex 开放许可。使用本数据集请注明仓库地址：

https://github.com/liubin18911671739/drift-suppression-bri-mair

## 服务器原始路径

```
server@100.75.203.102:/data/workspace/drift-suppression/
```

论文 Word 稿仅存本地，不在本仓库中。