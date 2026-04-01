#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
报告生成模块
生成 HTML 格式的性能测试报告
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

from jinja2 import Environment, FileSystemLoader

from parse_results import TestResult, ResultAggregator
from generate_charts import ChartGenerator, ChartConfig


@dataclass
class ReportSummary:
    total_tests: int
    total_requests: int
    total_errors: int
    avg_qps: float
    avg_latency: float
    best_service: str
    test_duration: str
    generated_at: str


@dataclass
class ServiceSummary:
    service: str
    total_tests: int
    avg_qps: float
    avg_p50: float
    avg_p99: float
    avg_cpu: float
    avg_memory: float
    error_rate: float


class ReportGenerator:
    def __init__(
        self,
        template_dir: str = './templates',
        output_dir: str = './reports',
        charts_dir: str = './charts'
    ):
        self.output_dir = output_dir
        self.charts_dir = charts_dir
        os.makedirs(output_dir, exist_ok=True)
        
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=True
        )
    
    def _calculate_summary(self, results: List[TestResult]) -> ReportSummary:
        total_requests = 0
        total_errors = 0
        qps_values = []
        latency_values = []
        service_qps = {}
        
        for result in results:
            if result.throughput:
                total_requests += result.throughput.total_requests
                total_errors += result.throughput.errors
                qps_values.append(result.throughput.qps)
                service = result.config.service
                if service not in service_qps:
                    service_qps[service] = []
                service_qps[service].append(result.throughput.qps)
            
            if result.latency:
                latency_values.append(result.latency.avg)
        
        avg_qps = sum(qps_values) / len(qps_values) if qps_values else 0
        avg_latency = sum(latency_values) / len(latency_values) if latency_values else 0
        
        best_service = ""
        best_avg_qps = 0
        for service, qps_list in service_qps.items():
            avg = sum(qps_list) / len(qps_list)
            if avg > best_avg_qps:
                best_avg_qps = avg
                best_service = service
        
        return ReportSummary(
            total_tests=len(results),
            total_requests=total_requests,
            total_errors=total_errors,
            avg_qps=round(avg_qps, 2),
            avg_latency=round(avg_latency, 2),
            best_service=best_service,
            test_duration="N/A",
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    
    def _calculate_service_summaries(self, results: List[TestResult]) -> List[ServiceSummary]:
        service_data = {}
        
        for result in results:
            service = result.config.service
            if service not in service_data:
                service_data[service] = {
                    'tests': 0,
                    'qps': [],
                    'p50': [],
                    'p99': [],
                    'cpu': [],
                    'memory': [],
                    'requests': 0,
                    'errors': 0
                }
            
            data = service_data[service]
            data['tests'] += 1
            
            if result.throughput:
                data['qps'].append(result.throughput.qps)
                data['requests'] += result.throughput.total_requests
                data['errors'] += result.throughput.errors
            
            if result.latency:
                data['p50'].append(result.latency.p50)
                data['p99'].append(result.latency.p99)
            
            if result.resource:
                data['cpu'].append(result.resource.cpu_usage)
                data['memory'].append(result.resource.memory_usage)
        
        summaries = []
        for service, data in service_data.items():
            error_rate = (data['errors'] / data['requests'] * 100) if data['requests'] > 0 else 0
            
            summaries.append(ServiceSummary(
                service=service,
                total_tests=data['tests'],
                avg_qps=round(sum(data['qps']) / len(data['qps']), 2) if data['qps'] else 0,
                avg_p50=round(sum(data['p50']) / len(data['p50']), 2) if data['p50'] else 0,
                avg_p99=round(sum(data['p99']) / len(data['p99']), 2) if data['p99'] else 0,
                avg_cpu=round(sum(data['cpu']) / len(data['cpu']), 2) if data['cpu'] else 0,
                avg_memory=round(sum(data['memory']) / len(data['memory']), 2) if data['memory'] else 0,
                error_rate=round(error_rate, 2)
            ))
        
        return sorted(summaries, key=lambda x: x.avg_qps, reverse=True)
    
    def _get_chart_paths(self, prefix: str = "") -> Dict[str, str]:
        charts = {}
        chart_names = [
            'latency_distribution',
            'throughput_comparison',
            'resource_usage',
            'comparison_radar',
            'concurrency_curve',
            'performance_heatmap'
        ]
        
        prefix = f"{prefix}_" if prefix else ""
        
        for name in chart_names:
            path = os.path.join(self.charts_dir, f"{prefix}{name}.png")
            if os.path.exists(path):
                charts[name] = f"../charts/{prefix}{name}.png"
        
        return charts
    
    def generate_report(
        self,
        results: List[TestResult],
        output_name: str = "benchmark_report",
        title: str = "性能基准测试报告",
        generate_charts: bool = True
    ) -> str:
        if generate_charts:
            chart_config = ChartConfig(output_dir=self.charts_dir)
            chart_generator = ChartGenerator(chart_config)
            chart_generator.generate_all_charts(results, output_prefix=output_name)
        
        summary = self._calculate_summary(results)
        service_summaries = self._calculate_service_summaries(results)
        chart_paths = self._get_chart_paths(output_name)
        
        results_data = []
        for result in results:
            result_dict = {
                'service': result.config.service,
                'test_type': result.config.test_type,
                'concurrency': result.config.concurrency,
                'duration': result.config.duration,
            }
            
            if result.latency:
                result_dict.update({
                    'latency_avg': result.latency.avg,
                    'latency_p50': result.latency.p50,
                    'latency_p90': result.latency.p90,
                    'latency_p99': result.latency.p99,
                })
            
            if result.throughput:
                result_dict.update({
                    'qps': result.throughput.qps,
                    'total_requests': result.throughput.total_requests,
                    'errors': result.throughput.errors,
                })
            
            if result.resource:
                result_dict.update({
                    'cpu_usage': result.resource.cpu_usage,
                    'memory_usage': result.resource.memory_usage,
                })
            
            results_data.append(result_dict)
        
        template = self.env.get_template('report.html')
        
        html_content = template.render(
            title=title,
            summary=asdict(summary),
            service_summaries=[asdict(s) for s in service_summaries],
            charts=chart_paths,
            results=results_data,
            generated_at=summary.generated_at
        )
        
        output_path = os.path.join(self.output_dir, f"{output_name}.html")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path
    
    def generate_comparison_report(
        self,
        results_by_scenario: Dict[str, List[TestResult]],
        output_name: str = "comparison_report",
        title: str = "多场景性能对比报告"
    ) -> str:
        all_results = []
        for scenario_results in results_by_scenario.values():
            all_results.extend(scenario_results)
        
        summary = self._calculate_summary(all_results)
        
        scenario_summaries = {}
        for scenario, results in results_by_scenario.items():
            scenario_summaries[scenario] = {
                'summary': asdict(self._calculate_summary(results)),
                'service_summaries': [asdict(s) for s in self._calculate_service_summaries(results)]
            }
        
        if all_results:
            chart_config = ChartConfig(output_dir=self.charts_dir)
            chart_generator = ChartGenerator(chart_config)
            chart_generator.generate_all_charts(all_results, output_prefix=output_name)
        
        chart_paths = self._get_chart_paths(output_name)
        
        template = self.env.get_template('report.html')
        
        html_content = template.render(
            title=title,
            summary=asdict(summary),
            service_summaries=[asdict(s) for s in self._calculate_service_summaries(all_results)],
            charts=chart_paths,
            scenario_summaries=scenario_summaries,
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        output_path = os.path.join(self.output_dir, f"{output_name}.html")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python generate_report.py <results_json_file> [output_name]")
        sys.exit(1)
    
    results_file = sys.argv[1]
    output_name = sys.argv[2] if len(sys.argv) > 2 else "benchmark_report"
    
    with open(results_file, 'r') as f:
        results_data = json.load(f)
    
    aggregator = ResultAggregator()
    results = aggregator.load_from_json(results_data)
    
    generator = ReportGenerator(
        template_dir=os.path.join(os.path.dirname(__file__), 'templates'),
        output_dir='./reports',
        charts_dir='./charts'
    )
    
    report_path = generator.generate_report(results, output_name=output_name)
    
    print(f"Report generated: {report_path}")


if __name__ == '__main__':
    main()
