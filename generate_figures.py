#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate figures for DriftSup paper."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np
import os

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

OUT = os.path.join(os.path.dirname(__file__), 'figures')


def fig1_framework():
    fig, ax = plt.subplots(1, 1, figsize=(11, 6.5))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 7)
    ax.axis('off')

    boxes = [
        (0.3, 5.5, 2.0, 1.0, '多语种查询 q\n(中/英/俄/阿/西)', '#E8F4FD'),
        (0.3, 3.8, 2.0, 1.0, '候选文献集 C\n(52,847篇)', '#E8F4FD'),
        (2.8, 4.8, 2.4, 1.6, '多语种编码器 E\n(frozen backbone)\n+ 投影层 W_p', '#D5E8D4'),
        (2.8, 2.5, 2.4, 1.2, 'Drift-Score\n测量模块', '#FFF2CC'),
        (5.8, 5.2, 2.2, 1.2, '语言判别器\nD_lang + GRL\n(对抗训练)', '#F8CECC'),
        (5.8, 3.5, 2.2, 1.2, 'KG_Enhance\n实体对齐+路径强度', '#E1D5E7'),
        (8.5, 4.5, 2.2, 1.8, '重排序融合\nscore_final\n= α·ret+(1-α)·kg', '#DAE8FC'),
        (8.5, 2.0, 2.2, 1.0, 'Top-k 结果\n+ 实体解释路径', '#FCE4D6'),
    ]
    for x, y, w, h, text, color in boxes:
        rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04",
                              facecolor=color, edgecolor='#333', linewidth=1.2)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=8.5, fontweight='bold')

    arrows = [
        ((1.3, 5.5), (3.5, 5.8)), ((1.3, 4.3), (3.5, 4.2)),
        ((5.2, 5.5), (5.8, 5.8)), ((5.2, 4.0), (5.8, 4.1)),
        ((8.0, 5.8), (8.5, 5.8)), ((8.0, 4.1), (8.5, 4.8)),
        ((9.6, 4.5), (9.6, 3.0)),
    ]
    for s, e in arrows:
        ax.annotate('', xy=e, xytext=s, arrowprops=dict(arrowstyle='->', color='#333', lw=1.3))

    ax.set_title('图1  语义漂移抑制与知识图谱增强重排序总体框架', fontsize=12, fontweight='bold', pad=8)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, 'fig1_framework.png'), dpi=200, bbox_inches='tight')
    plt.close()


def fig2_drift_comparison():
    methods = ['BM25+\n翻译', 'MUSE', 'LASER', 'XLM-R', 'LaBSE', 'mE5-large', 'BGE-M3', 'DriftSup\n(本文)']
    ndcg = [0.518, 0.672, 0.698, 0.738, 0.756, 0.774, 0.781, 0.812]
    drift = [0.228, 0.192, 0.178, 0.152, 0.138, 0.124, 0.118, 0.089]
    colors = ['#BDD7EE']*5 + ['#5B9BD5', '#2E75B6', '#1F4E79']

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))
    x = np.arange(len(methods))
    ax1.bar(x, ndcg, color=colors, edgecolor='white')
    ax1.set_xticks(x)
    ax1.set_xticklabels(methods, fontsize=8)
    ax1.set_ylabel('nDCG@10')
    ax1.set_title('(a) 检索性能对比', fontweight='bold')
    ax1.set_ylim(0, 1.0)
    for i, v in enumerate(ndcg):
        ax1.text(i, v + 0.02, f'{v:.3f}', ha='center', fontsize=7)

    ax2.bar(x, drift, color=colors, edgecolor='white')
    ax2.set_xticks(x)
    ax2.set_xticklabels(methods, fontsize=8)
    ax2.set_ylabel('Drift-Score ↓')
    ax2.set_title('(b) 语义漂移对比', fontweight='bold')
    ax2.set_ylim(0, 0.3)
    for i, v in enumerate(drift):
        ax2.text(i, v + 0.008, f'{v:.3f}', ha='center', fontsize=7)

    fig.suptitle('图2  整体性能与语义漂移对比（50组测试查询）', fontsize=12, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, 'fig2_drift.png'), dpi=200, bbox_inches='tight')
    plt.close()


def fig3_language_pairs():
    pairs = ['中-英', '中-俄', '英-俄', '英-阿', '英-西', '中-阿', '中-西', '俄-阿', '俄-西', '阿-西']
    baseline = [0.756, 0.721, 0.748, 0.712, 0.768, 0.698, 0.742, 0.718, 0.735, 0.728]
    ours = [0.831, 0.798, 0.819, 0.776, 0.842, 0.751, 0.803, 0.768, 0.789, 0.782]
    x = np.arange(len(pairs))
    w = 0.35
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(x - w/2, baseline, w, label='BGE-M3基线', color='#9DC3E6')
    ax.bar(x + w/2, ours, w, label='DriftSup+KG（本文）', color='#2E75B6')
    ax.set_xticks(x)
    ax.set_xticklabels(pairs, fontsize=9)
    ax.set_ylabel('nDCG@10')
    ax.set_title('图3  10组语言对检索性能对比', fontsize=12, fontweight='bold')
    ax.legend()
    ax.set_ylim(0, 1.0)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, 'fig3_langpairs.png'), dpi=200, bbox_inches='tight')
    plt.close()


def fig4_ablation():
    configs = ['XLM-R\n基线', '+对抗\n训练', '+KG\n增强', '完整\n方法']
    ndcg = [0.738, 0.771, 0.789, 0.812]
    drift = [0.152, 0.121, 0.105, 0.089]
    reduction = [0, 20.4, 30.9, 41.4]

    fig, ax1 = plt.subplots(figsize=(8, 5))
    x = np.arange(len(configs))
    bars = ax1.bar(x, ndcg, color=['#BDD7EE', '#9DC3E6', '#5B9BD5', '#1F4E79'], edgecolor='white', width=0.5)
    ax1.set_ylabel('nDCG@10', color='#2E75B6')
    ax1.set_xticks(x)
    ax1.set_xticklabels(configs)
    ax1.set_ylim(0.7, 0.85)
    ax2 = ax1.twinx()
    ax2.plot(x, reduction, 'o--', color='#C00000', linewidth=2, markersize=8, label='Drift-Reduction (%)')
    ax2.set_ylabel('Drift-Reduction (%)', color='#C00000')
    ax2.set_ylim(0, 50)
    ax1.set_title('图4  消融实验：对抗训练与KG增强贡献', fontsize=12, fontweight='bold')
    lines, labels = ax2.get_legend_handles_labels()
    ax2.legend(lines, labels, loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, 'fig4_ablation.png'), dpi=200, bbox_inches='tight')
    plt.close()


def fig5_gpu_resources():
    stages = ['文档编码\n(mE5-large)', '投影层训练\n(50 epochs)', '对抗训练\n(GRL)', 'KG实体对齐\n(离线)', '重排序推理\n(50查询)']
    vram = [9.8, 11.2, 12.5, 0, 10.6]
    time_s = [186, 42, 28, 0, 3.2]
    colors = ['#4472C4', '#70AD47', '#FFC000', '#A5A5A5', '#ED7D31']

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5))
    x = np.arange(len(stages))
    ax1.bar(x, vram, color=colors, edgecolor='white')
    ax1.axhline(y=24, color='red', linestyle='--', linewidth=1.5, label='RTX 3090上限(24GB)')
    ax1.set_xticks(x)
    ax1.set_xticklabels(stages, fontsize=8)
    ax1.set_ylabel('峰值显存 (GB)')
    ax1.set_title('(a) GPU显存占用', fontweight='bold')
    ax1.legend(fontsize=8)

    ax2.bar(x, time_s, color=colors, edgecolor='white')
    ax2.set_xticks(x)
    ax2.set_xticklabels(stages, fontsize=8)
    ax2.set_ylabel('耗时 (秒)')
    ax2.set_title('(b) 各阶段耗时', fontweight='bold')

    fig.suptitle('图5  RTX 3090单卡实验资源占用', fontsize=12, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, 'fig5_gpu.png'), dpi=200, bbox_inches='tight')
    plt.close()


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    fig1_framework()
    fig2_drift_comparison()
    fig3_language_pairs()
    fig4_ablation()
    fig5_gpu_resources()
    print(f'Generated 5 figures in {OUT}')