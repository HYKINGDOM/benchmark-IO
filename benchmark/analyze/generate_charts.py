#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图表生成模块
生成响应时间、吞吐量、资源消耗和多语言对比图表
"""

import os
from dataclasses import dataclass
from typing import Dict, List, Optional
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import numpy as np
import pandas as pd

from parse_results import (
    TestResult, ResultAggregator,
    LatencyMetrics, ThroughputMetrics, ResourceMetrics
)

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

sns.set_theme(style="whitegrid", palette="muted")

COLORS = {
    'java': '#E76F00',
    'golang': '#00ADD8',
    'python': '#3776AB',
    'rust': '#DEA584',
}

CHART_CONFIG = {
    'figsize': (12, 8),
    'dpi': 150,
    'title_fontsize': 16,
    'label_fontsize': 12,
    'legend_fontsize': 10,
}


@dataclass
class ChartConfig:
    output_dir: str = './charts'
    format: str = 'png'
    dpi: int = 150


class ChartGenerator:
    def __init__(self, config: Optional[ChartConfig] = None):
        self.config = config or ChartConfig()
        os.makedirs(self.config.output_dir, exist_ok=True)

    def generate_latency_chart(
        self,
        results: List[TestResult],
        title: str = "响应时间分布",
        output_name: str = "latency_distribution"
    ) -> str:
        data = []
        for result in results:
            if result.latency:
                for percentile, value in [
                    ('P50', result.latency.p50),
                    ('P75', result.latency.p75),
                    ('P90', result.latency.p90),
                    ('P95', result.latency.p95),
                    ('P99', result.latency.p99),
                ]:
                    data.append({
                        'Service': result.config.service,
                        'Percentile': percentile,
                        'Latency (ms)': value
                    })
        
        if not data:
            return ""
        
        df = pd.DataFrame(data)
        
        fig, ax = plt.subplots(figsize=CHART_CONFIG['figsize'])
        
        services = df['Service'].unique()
        percentiles = ['P50', 'P75', 'P90', 'P95', 'P99']
        x = np.arange(len(percentiles))
        width = 0.2
        
        for i, service in enumerate(services):
            service_data = df[df['Service'] == service]
            values = [service_data[service_data['Percentile'] == p]['Latency (ms)'].values[0] 
                     for p in percentiles]
            ax.bar(x + i * width, values, width, label=service, 
                   color=COLORS.get(service, f'C{i}'))
        
        ax.set_xlabel('Percentile', fontsize=CHART_CONFIG['label_fontsize'])
        ax.set_ylabel('Latency (ms)', fontsize=CHART_CONFIG['label_fontsize'])
        ax.set_title(title, fontsize=CHART_CONFIG['title_fontsize'])
        ax.set_xticks(x + width * (len(services) - 1) / 2)
        ax.set_xticklabels(percentiles)
        ax.legend(fontsize=CHART_CONFIG['legend_fontsize'])
        ax.grid(True, alpha=0.3)
        
        output_path = os.path.join(
            self.config.output_dir, 
            f"{output_name}.{self.config.format}"
        )
        plt.tight_layout()
        plt.savefig(output_path, dpi=self.config.dpi)
        plt.close()
        
        return output_path

    def generate_latency_boxplot(
        self,
        results: List[TestResult],
        title: str = "响应时间箱线图",
        output_name: str = "latency_boxplot"
    ) -> str:
        data = []
        for result in results:
            if result.latency:
                data.append({
                    'Service': result.config.service,
                    'P50': result.latency.p50,
                    'P75': result.latency.p75,
                    'P90': result.latency.p90,
                    'P95': result.latency.p95,
                    'P99': result.latency.p99,
                    'Avg': result.latency.avg,
                })
        
        if not data:
            return ""
        
        df = pd.DataFrame(data)
        
        fig, ax = plt.subplots(figsize=CHART_CONFIG['figsize'])
        
        services = df['Service'].unique()
        box_data = []
        labels = []
        
        for service in services:
            service_df = df[df['Service'] == service]
            for _, row in service_df.iterrows():
                box_data.append([row['P50'], row['P75'], row['P90'], row['P95'], row['P99']])
                labels.append(service)
        
        bp = ax.boxplot(box_data, patch_artist=True, labels=range(1, len(box_data) + 1))
        
        color_map = [COLORS.get(s, 'gray') for s in labels]
        for patch, color in zip(bp['boxes'], color_map):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        ax.set_xlabel('Test Run', fontsize=CHART_CONFIG['label_fontsize'])
        ax.set_ylabel('Latency (ms)', fontsize=CHART_CONFIG['label_fontsize'])
        ax.set_title(title, fontsize=CHART_CONFIG['title_fontsize'])
        ax.grid(True, alpha=0.3)
        
        handles = [plt.Rectangle((0,0),1,1, facecolor=COLORS[s], alpha=0.7) 
                   for s in services]
        ax.legend(handles, services, fontsize=CHART_CONFIG['legend_fontsize'])
        
        output_path = os.path.join(
            self.config.output_dir, 
            f"{output_name}.{self.config.format}"
        )
        plt.tight_layout()
        plt.savefig(output_path, dpi=self.config.dpi)
        plt.close()
        
        return output_path

    def generate_throughput_chart(
        self,
        results: List[TestResult],
        title: str = "吞吐量对比",
        output_name: str = "throughput_comparison"
    ) -> str:
        data = []
        for result in results:
            if result.throughput:
                data.append({
                    'Service': result.config.service,
                    'QPS': result.throughput.qps,
                    'Requests': result.throughput.total_requests,
                    'Errors': result.throughput.errors,
                })
        
        if not data:
            return ""
        
        df = pd.DataFrame(data)
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        ax1 = axes[0]
        services = df['Service'].unique()
        x = np.arange(len(services))
        qps_values = [df[df['Service'] == s]['QPS'].mean() for s in services]
        colors = [COLORS.get(s, f'C{i}') for i, s in enumerate(services)]
        
        bars = ax1.bar(x, qps_values, color=colors, alpha=0.8)
        ax1.set_xlabel('Service', fontsize=CHART_CONFIG['label_fontsize'])
        ax1.set_ylabel('QPS (requests/sec)', fontsize=CHART_CONFIG['label_fontsize'])
        ax1.set_title('平均 QPS 对比', fontsize=CHART_CONFIG['title_fontsize'])
        ax1.set_xticks(x)
        ax1.set_xticklabels(services)
        ax1.grid(True, alpha=0.3, axis='y')
        
        for bar, val in zip(bars, qps_values):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    f'{val:.1f}', ha='center', va='bottom', fontsize=10)
        
        ax2 = axes[1]
        width = 0.35
        requests_values = [df[df['Service'] == s]['Requests'].sum() for s in services]
        errors_values = [df[df['Service'] == s]['Errors'].sum() for s in services]
        
        ax2.bar(x - width/2, requests_values, width, label='Total Requests', color='steelblue', alpha=0.8)
        ax2.bar(x + width/2, errors_values, width, label='Errors', color='coral', alpha=0.8)
        ax2.set_xlabel('Service', fontsize=CHART_CONFIG['label_fontsize'])
        ax2.set_ylabel('Count', fontsize=CHART_CONFIG['label_fontsize'])
        ax2.set_title('请求总数与错误数', fontsize=CHART_CONFIG['title_fontsize'])
        ax2.set_xticks(x)
        ax2.set_xticklabels(services)
        ax2.legend(fontsize=CHART_CONFIG['legend_fontsize'])
        ax2.grid(True, alpha=0.3, axis='y')
        
        output_path = os.path.join(
            self.config.output_dir, 
            f"{output_name}.{self.config.format}"
        )
        plt.tight_layout()
        plt.savefig(output_path, dpi=self.config.dpi)
        plt.close()
        
        return output_path

    def generate_resource_chart(
        self,
        results: List[TestResult],
        title: str = "资源消耗趋势",
        output_name: str = "resource_usage"
    ) -> str:
        data = []
        for result in results:
            if result.resource:
                data.append({
                    'Service': result.config.service,
                    'CPU (%)': result.resource.cpu_usage,
                    'Memory (MB)': result.resource.memory_usage,
                    'Network I/O (MB)': result.resource.network_io,
                    'DB Connections': result.resource.db_connections,
                })
        
        if not data:
            return ""
        
        df = pd.DataFrame(data)
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        services = df['Service'].unique()
        colors = [COLORS.get(s, f'C{i}') for i, s in enumerate(services)]
        
        metrics = [
            ('CPU (%)', 'CPU 使用率 (%)'),
            ('Memory (MB)', '内存使用 (MB)'),
            ('Network I/O (MB)', '网络 I/O (MB)'),
            ('DB Connections', '数据库连接数')
        ]
        
        for ax, (metric, ylabel) in zip(axes.flat, metrics):
            for i, service in enumerate(services):
                service_data = df[df['Service'] == service][metric]
                ax.plot(range(len(service_data)), service_data.values, 
                       marker='o', label=service, color=colors[i], linewidth=2)
            
            ax.set_xlabel('Test Run', fontsize=CHART_CONFIG['label_fontsize'])
            ax.set_ylabel(ylabel, fontsize=CHART_CONFIG['label_fontsize'])
            ax.set_title(metric, fontsize=CHART_CONFIG['title_fontsize'])
            ax.legend(fontsize=CHART_CONFIG['legend_fontsize'])
            ax.grid(True, alpha=0.3)
        
        fig.suptitle(title, fontsize=CHART_CONFIG['title_fontsize'] + 2, y=1.02)
        
        output_path = os.path.join(
            self.config.output_dir, 
            f"{output_name}.{self.config.format}"
        )
        plt.tight_layout()
        plt.savefig(output_path, dpi=self.config.dpi)
        plt.close()
        
        return output_path

    def generate_comparison_radar(
        self,
        results: List[TestResult],
        title: str = "多语言性能对比",
        output_name: str = "comparison_radar"
    ) -> str:
        categories = ['QPS', 'P50延迟', 'P99延迟', 'CPU效率', '内存效率']
        
        service_scores = {}
        
        for result in results:
            service = result.config.service
            if service not in service_scores:
                service_scores[service] = {
                    'qps': [],
                    'p50': [],
                    'p99': [],
                    'cpu': [],
                    'memory': []
                }
            
            if result.throughput:
                service_scores[service]['qps'].append(result.throughput.qps)
            if result.latency:
                service_scores[service]['p50'].append(result.latency.p50)
                service_scores[service]['p99'].append(result.latency.p99)
            if result.resource:
                service_scores[service]['cpu'].append(result.resource.cpu_usage)
                service_scores[service]['memory'].append(result.resource.memory_usage)
        
        if not service_scores:
            return ""
        
        max_qps = max(np.mean(s['qps']) for s in service_scores.values() if s['qps']) or 1
        max_p50 = max(np.mean(s['p50']) for s in service_scores.values() if s['p50']) or 1
        max_p99 = max(np.mean(s['p99']) for s in service_scores.values() if s['p99']) or 1
        max_cpu = max(np.mean(s['cpu']) for s in service_scores.values() if s['cpu']) or 1
        max_memory = max(np.mean(s['memory']) for s in service_scores.values() if s['memory']) or 1
        
        normalized_scores = {}
        for service, scores in service_scores.items():
            avg_qps = np.mean(scores['qps']) if scores['qps'] else 0
            avg_p50 = np.mean(scores['p50']) if scores['p50'] else 0
            avg_p99 = np.mean(scores['p99']) if scores['p99'] else 0
            avg_cpu = np.mean(scores['cpu']) if scores['cpu'] else 0
            avg_memory = np.mean(scores['memory']) if scores['memory'] else 0
            
            normalized_scores[service] = [
                avg_qps / max_qps * 100 if max_qps > 0 else 0,
                (1 - avg_p50 / max_p50) * 100 if max_p50 > 0 else 100,
                (1 - avg_p99 / max_p99) * 100 if max_p99 > 0 else 100,
                (1 - avg_cpu / max_cpu) * 100 if max_cpu > 0 else 100,
                (1 - avg_memory / max_memory) * 100 if max_memory > 0 else 100,
            ]
        
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]
        
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
        
        for service, scores in normalized_scores.items():
            values = scores + scores[:1]
            ax.plot(angles, values, 'o-', linewidth=2, label=service, 
                   color=COLORS.get(service, 'gray'))
            ax.fill(angles, values, alpha=0.25, color=COLORS.get(service, 'gray'))
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=CHART_CONFIG['label_fontsize'])
        ax.set_ylim(0, 100)
        ax.set_title(title, fontsize=CHART_CONFIG['title_fontsize'], y=1.08)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0), 
                 fontsize=CHART_CONFIG['legend_fontsize'])
        
        output_path = os.path.join(
            self.config.output_dir, 
            f"{output_name}.{self.config.format}"
        )
        plt.tight_layout()
        plt.savefig(output_path, dpi=self.config.dpi)
        plt.close()
        
        return output_path

    def generate_concurrency_chart(
        self,
        results: List[TestResult],
        title: str = "并发性能曲线",
        output_name: str = "concurrency_curve"
    ) -> str:
        data = []
        for result in results:
            concurrency = result.config.concurrency or 1
            data.append({
                'Service': result.config.service,
                'Concurrency': concurrency,
                'QPS': result.throughput.qps if result.throughput else 0,
                'P99': result.latency.p99 if result.latency else 0,
            })
        
        if not data:
            return ""
        
        df = pd.DataFrame(data)
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        services = df['Service'].unique()
        colors = [COLORS.get(s, f'C{i}') for i, s in enumerate(services)]
        
        ax1 = axes[0]
        for i, service in enumerate(services):
            service_df = df[df['Service'] == service].sort_values('Concurrency')
            ax1.plot(service_df['Concurrency'], service_df['QPS'], 
                    marker='o', label=service, color=colors[i], linewidth=2)
        
        ax1.set_xlabel('Concurrency', fontsize=CHART_CONFIG['label_fontsize'])
        ax1.set_ylabel('QPS', fontsize=CHART_CONFIG['label_fontsize'])
        ax1.set_title('QPS vs Concurrency', fontsize=CHART_CONFIG['title_fontsize'])
        ax1.legend(fontsize=CHART_CONFIG['legend_fontsize'])
        ax1.grid(True, alpha=0.3)
        
        ax2 = axes[1]
        for i, service in enumerate(services):
            service_df = df[df['Service'] == service].sort_values('Concurrency')
            ax2.plot(service_df['Concurrency'], service_df['P99'], 
                    marker='o', label=service, color=colors[i], linewidth=2)
        
        ax2.set_xlabel('Concurrency', fontsize=CHART_CONFIG['label_fontsize'])
        ax2.set_ylabel('P99 Latency (ms)', fontsize=CHART_CONFIG['label_fontsize'])
        ax2.set_title('P99 Latency vs Concurrency', fontsize=CHART_CONFIG['title_fontsize'])
        ax2.legend(fontsize=CHART_CONFIG['legend_fontsize'])
        ax2.grid(True, alpha=0.3)
        
        fig.suptitle(title, fontsize=CHART_CONFIG['title_fontsize'] + 2, y=1.02)
        
        output_path = os.path.join(
            self.config.output_dir, 
            f"{output_name}.{self.config.format}"
        )
        plt.tight_layout()
        plt.savefig(output_path, dpi=self.config.dpi)
        plt.close()
        
        return output_path

    def generate_heatmap(
        self,
        results: List[TestResult],
        title: str = "性能热力图",
        output_name: str = "performance_heatmap"
    ) -> str:
        metrics = ['QPS', 'P50', 'P90', 'P99', 'CPU', 'Memory']
        
        service_metrics = {}
        for result in results:
            service = result.config.service
            if service not in service_metrics:
                service_metrics[service] = {m: [] for m in metrics}
            
            if result.throughput:
                service_metrics[service]['QPS'].append(result.throughput.qps)
            if result.latency:
                service_metrics[service]['P50'].append(result.latency.p50)
                service_metrics[service]['P90'].append(result.latency.p90)
                service_metrics[service]['P99'].append(result.latency.p99)
            if result.resource:
                service_metrics[service]['CPU'].append(result.resource.cpu_usage)
                service_metrics[service]['Memory'].append(result.resource.memory_usage)
        
        if not service_metrics:
            return ""
        
        data_matrix = []
        services = list(service_metrics.keys())
        
        max_values = {}
        for metric in metrics:
            values = [np.mean(service_metrics[s][metric]) for s in services if service_metrics[s][metric]]
            max_values[metric] = max(values) if values else 1
        
        for service in services:
            row = []
            for metric in metrics:
                values = service_metrics[service][metric]
                avg = np.mean(values) if values else 0
                normalized = avg / max_values[metric] if max_values[metric] > 0 else 0
                row.append(normalized)
            data_matrix.append(row)
        
        df = pd.DataFrame(data_matrix, index=services, columns=metrics)
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        sns.heatmap(df, annot=True, fmt='.2f', cmap='RdYlGn_r', 
                   linewidths=0.5, ax=ax, vmin=0, vmax=1)
        
        ax.set_title(title, fontsize=CHART_CONFIG['title_fontsize'])
        ax.set_xlabel('Metric', fontsize=CHART_CONFIG['label_fontsize'])
        ax.set_ylabel('Service', fontsize=CHART_CONFIG['label_fontsize'])
        
        output_path = os.path.join(
            self.config.output_dir, 
            f"{output_name}.{self.config.format}"
        )
        plt.tight_layout()
        plt.savefig(output_path, dpi=self.config.dpi)
        plt.close()
        
        return output_path

    def generate_all_charts(
        self,
        results: List[TestResult],
        output_prefix: str = ""
    ) -> Dict[str, str]:
        charts = {}
        
        prefix = f"{output_prefix}_" if output_prefix else ""
        
        charts['latency_distribution'] = self.generate_latency_chart(
            results, output_name=f"{prefix}latency_distribution"
        )
        
        charts['throughput_comparison'] = self.generate_throughput_chart(
            results, output_name=f"{prefix}throughput_comparison"
        )
        
        charts['resource_usage'] = self.generate_resource_chart(
            results, output_name=f"{prefix}resource_usage"
        )
        
        charts['comparison_radar'] = self.generate_comparison_radar(
            results, output_name=f"{prefix}comparison_radar"
        )
        
        charts['concurrency_curve'] = self.generate_concurrency_chart(
            results, output_name=f"{prefix}concurrency_curve"
        )
        
        charts['performance_heatmap'] = self.generate_heatmap(
            results, output_name=f"{prefix}performance_heatmap"
        )
        
        return {k: v for k, v in charts.items() if v}


def main():
    import sys
    import json
    
    if len(sys.argv) < 2:
        print("Usage: python generate_charts.py <results_json_file> [output_dir]")
        sys.exit(1)
    
    results_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else './charts'
    
    with open(results_file, 'r') as f:
        results_data = json.load(f)
    
    aggregator = ResultAggregator()
    results = aggregator.load_from_json(results_data)
    
    config = ChartConfig(output_dir=output_dir)
    generator = ChartGenerator(config)
    
    charts = generator.generate_all_charts(results)
    
    print("Generated charts:")
    for name, path in charts.items():
        print(f"  - {name}: {path}")


if __name__ == '__main__':
    main()
