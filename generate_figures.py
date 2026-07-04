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
    # RTX 3090 measured results (15k docs, 200 queries)
    methods = ['BGE-M3', 'DriftSup', 'DriftSup\n+KG', 'BGE-M3\n+KG']
    ndcg = [0.0507, 0.0321, 0.0567, 0.0651]
    drift = [0.7086, 0.6366, 0.6011, 0.5520]
    colors = ['#9DC3E6', '#5B9BD5', '#2E75B6', '#1F4E79']

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))
    x = np.arange(len(methods))
    ax1.bar(x, ndcg, color=colors, edgecolor='white')
    ax1.set_xticks(x)
    ax1.set_xticklabels(methods, fontsize=8)
    ax1.set_ylabel('nDCG@10')
    ax1.set_title('(a) 检索性能对比', fontweight='bold')
    ax1.set_ylim(0, 0.08)
    for i, v in enumerate(ndcg):
        ax1.text(i, v + 0.02, f'{v:.3f}', ha='center', fontsize=7)

    ax2.bar(x, drift, color=colors, edgecolor='white')
    ax2.set_xticks(x)
    ax2.set_xticklabels(methods, fontsize=8)
    ax2.set_ylabel('Drift-Score ↓')
    ax2.set_title('(b) 语义漂移对比', fontweight='bold')
    ax2.set_ylim(0, 0.8)
    for i, v in enumerate(drift):
        ax2.text(i, v + 0.008, f'{v:.3f}', ha='center', fontsize=7)

    fig.suptitle('图2  整体性能与语义漂移对比（50组测试查询）', fontsize=12, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, 'fig2_drift.png'), dpi=200, bbox_inches='tight')
    plt.close()


def fig3_language_pairs():
    pairs = ['中-英', '中-俄', '英-俄', '英-阿', '英-西', '中-阿', '中-西', '俄-阿', '俄-西', '阿-西']
    baseline = [0.0527, 0.0512, 0.0134, 0.0134, 0.0134, 0.0512, 0.0512, 0.008, 0.0068, 0.014]
    ours = [0.0426, 0.0305, 0.019, 0.0167, 0.0167, 0.0262, 0.0315, 0.0074, 0.0069, 0.0014]
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
    ax.set_ylim(0, 0.07)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, 'fig3_langpairs.png'), dpi=200, bbox_inches='tight')
    plt.close()


def fig4_ablation():
    configs = ['BGE-M3\n基线', '+DriftSup\n对抗', '+KG\n增强', 'DriftSup\n+KG']
    ndcg = [0.0507, 0.0321, 0.0651, 0.0567]
    drift = [0.7086, 0.6366, 0.5520, 0.6011]
    reduction = [0, 10.2, 22.1, 15.2]

    fig, ax1 = plt.subplots(figsize=(8, 5))
    x = np.arange(len(configs))
    bars = ax1.bar(x, ndcg, color=['#BDD7EE', '#9DC3E6', '#5B9BD5', '#1F4E79'], edgecolor='white', width=0.5)
    ax1.set_ylabel('nDCG@10', color='#2E75B6')
    ax1.set_xticks(x)
    ax1.set_xticklabels(configs)
    ax1.set_ylim(0, 0.08)
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
    stages = ['文档编码\n(BGE-M3)', 'DriftSup训练\n(50 epochs)', '检索评估\n(200查询)', 'KG对齐\n(离线)', '总计']
    vram = [3.83, 0.04, 3.83, 0, 3.83]
    time_s = [164.6, 21.7, 197.6, 0, 384.0]
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