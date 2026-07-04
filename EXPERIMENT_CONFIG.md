# 实验环境配置（持久化）

## GPU 服务器
- **主机**: `server@100.75.203.102`
- **GPU**: NVIDIA RTX 3090 (24GB)
- **用途**: 全部 GPU 计算任务（编码、训练、检索推理）

## 数据存储
- **大容量数据根目录**: `/data/workspace/`
- **本项目数据目录**: `/data/workspace/drift-suppression/`
- **语料缓存**: `/data/workspace/drift-suppression/corpus/`
- **模型缓存**: `/data/workspace/drift-suppression/models/`
- **实验结果**: `/data/workspace/drift-suppression/results/`
- **知识图谱**: `/data/workspace/drift-suppression/kg/`

## 代码与版本管理
- **本地开发**: `/Users/robin/project/drift-suppression-paper/`
- **GitHub**: 仅上传代码、实验脚本与结果 JSON；**不上传论文**（*.docx / *.pdf）
- **论文存储**: 仅保存在本地（如 `/Users/robin/Downloads/论文/`）
- **远程工作目录**: `/data/workspace/drift-suppression/code/`

## 软件环境
- Ubuntu 22.04, Python 3.10+, PyTorch 2.1+, CUDA 12.1
- sentence-transformers, FAISS, transformers