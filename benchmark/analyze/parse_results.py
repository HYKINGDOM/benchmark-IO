#!/usr/bin/env python3
"""
测试结果解析脚本

支持解析多种格式的测试结果：
1. wrk/wrk2 输出结果
2. JSON 格式的测试结果
3. Prometheus 指标数据
"""

import json
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class LatencyMetrics:
    """延迟指标"""
    avg: float = 0.0  # 平均延迟 (ms)
    min: float = 0.0  # 最小延迟 (ms)
    max: float = 0.0  # 最大延迟 (ms)
    p50: float = 0.0  # 50th 百分位 (ms)
    p75: float = 0.0  # 75th 百分位 (ms)
    p90: float = 0.0  # 90th 百分位 (ms)
    p95: float = 0.0  # 95th 百分位 (ms)
    p99: float = 0.0  # 99th 百分位 (ms)
    stdev: float = 0.0  # 标准差 (ms)


@dataclass
class ThroughputMetrics:
    """吞吐量指标"""
    qps: float = 0.0  # 每秒请求数
    total_requests: int = 0  # 总请求数
    total_duration: float = 0.0  # 总持续时间 (秒)
    data_rate: float = 0.0  # 数据传输速率 (MB/s)
    records_per_second: float = 0.0  # 记录导出速率 (条/秒)


@dataclass
class ResourceMetrics:
    """资源消耗指标"""
    cpu_usage: float = 0.0  # CPU 使用率 (%)
    memory_usage: float = 0.0  # 内存使用 (MB)
    memory_usage_percent: float = 0.0  # 内存使用率 (%)
    network_in: float = 0.0  # 网络入流量 (MB/s)
    network_out: float = 0.0  # 网络出流量 (MB/s)
    db_connections: int = 0  # 数据库连接数


@dataclass
class TestConfig:
    """测试配置"""
    language: str = ""  # 编程语言 (java/golang/python/rust)
    endpoint: str = ""  # 测试接口
    test_type: str = ""  # 测试类型 (query/export_sync/export_async/export_stream)
    concurrency: int = 1  # 并发数
    duration: int = 30  # 持续时间 (秒)
    threads: int = 1  # 线程数
    data_size: int = 0  # 数据量 (条)
    format: str = ""  # 导出格式 (csv/excel)
    filters: Dict[str, Any] = field(default_factory=dict)  # 查询过滤条件


@dataclass
class TestResult:
    """测试结果"""
    test_id: str = ""  # 测试ID
    timestamp: str = ""  # 时间戳
    config: TestConfig = field(default_factory=TestConfig)
    latency: LatencyMetrics = field(default_factory=LatencyMetrics)
    throughput: ThroughputMetrics = field(default_factory=ThroughputMetrics)
    resources: ResourceMetrics = field(default_factory=ResourceMetrics)
    success: bool = True  # 是否成功
    error_count: int = 0  # 错误数
    error_rate: float = 0.0  # 错误率
    raw_output: str = ""  # 原始输出
    metadata: Dict[str, Any] = field(default_factory=dict)  # 其他元数据

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'test_id': self.test_id,
            'timestamp': self.timestamp,
            'config': asdict(self.config),
            'latency': asdict(self.latency),
            'throughput': asdict(self.throughput),
            'resources': asdict(self.resources),
            'success': self.success,
            'error_count': self.error_count,
            'error_rate': self.error_rate,
            'raw_output': self.raw_output,
            'metadata': self.metadata
        }


class WrkResultParser:
    """wrk 测试结果解析器"""

    @staticmethod
    def parse(output: str, config: Optional[TestConfig] = None) -> TestResult:
        """解析 wrk 输出"""
        result = TestResult(
            timestamp=datetime.now().isoformat(),
            config=config or TestConfig(),
            raw_output=output
        )

        # 解析总请求数和持续时间
        running_match = re.search(r'Running (\d+s) test @', output)
        if running_match:
            result.config.duration = int(running_match.group(1)[:-1])

        # 解析线程数和连接数
        threads_match = re.search(r'(\d+) threads and (\d+) connections', output)
        if threads_match:
            result.config.threads = int(threads_match.group(1))
            result.config.concurrency = int(threads_match.group(2))

        # 解析总请求数和持续时间
        requests_match = re.search(r'(\d+) requests in ([\d.]+)s', output)
        if requests_match:
            result.throughput.total_requests = int(requests_match.group(1))
            result.throughput.total_duration = float(requests_match.group(2))
            if result.throughput.total_duration > 0:
                result.throughput.qps = result.throughput.total_requests / result.throughput.total_duration

        # 解析延迟分布
        latency_match = re.search(
            r'Thread Stats\s+avg\s+([\d.]+)(\w+)\s+stdev\s+([\d.]+)(\w+)\s+'
            r'max\s+([\d.]+)(\w+)\s+\+/-\s+([\d.]+)(\w+)',
            output
        )
        if latency_match:
            # wrk 输出的延迟单位可能是 us 或 ms
            avg_unit = latency_match.group(2)
            stdev_unit = latency_match.group(4)
            max_unit = latency_match.group(6)

            result.latency.avg = WrkResultParser._convert_to_ms(
                float(latency_match.group(1)), avg_unit
            )
            result.latency.stdev = WrkResultParser._convert_to_ms(
                float(latency_match.group(3)), stdev_unit
            )
            result.latency.max = WrkResultParser._convert_to_ms(
                float(latency_match.group(5)), max_unit
            )

        # 解析延迟百分位
        latency_dist_match = re.search(
            r'Latency\s+([\d.]+)(\w+)\s+([\d.]+)(\w+)\s+([\d.]+)(\w+)\s+'
            r'([\d.]+)(\w+)\s+([\d.]+)(\w+)',
            output
        )
        if latency_dist_match:
            # 50% 75% 90% 99%
            result.latency.p50 = WrkResultParser._convert_to_ms(
                float(latency_dist_match.group(1)), latency_dist_match.group(2)
            )
            result.latency.p75 = WrkResultParser._convert_to_ms(
                float(latency_dist_match.group(3)), latency_dist_match.group(4)
            )
            result.latency.p90 = WrkResultParser._convert_to_ms(
                float(latency_dist_match.group(5)), latency_dist_match.group(6)
            )
            result.latency.p99 = WrkResultParser._convert_to_ms(
                float(latency_dist_match.group(7)), latency_dist_match.group(8)
            )

        # 解析 --latency 输出的百分位
        percentile_pattern = r'\s+(\d+)%\s+([\d.]+)(\w+)'
        percentiles = re.findall(percentile_pattern, output)
        for percentile, value, unit in percentiles:
            p_value = WrkResultParser._convert_to_ms(float(value), unit)
            if percentile == '50':
                result.latency.p50 = p_value
            elif percentile == '75':
                result.latency.p75 = p_value
            elif percentile == '90':
                result.latency.p90 = p_value
            elif percentile == '95':
                result.latency.p95 = p_value
            elif percentile == '99':
                result.latency.p99 = p_value

        # 解析 QPS
        qps_match = re.search(r'Requests/sec:\s+([\d.]+)', output)
        if qps_match:
            result.throughput.qps = float(qps_match.group(1))

        # 解析数据传输速率
        transfer_match = re.search(r'Transfer/sec:\s+([\d.]+)(\w+)', output)
        if transfer_match:
            value = float(transfer_match.group(1))
            unit = transfer_match.group(2)
            # 转换为 MB/s
            if unit == 'KB':
                result.throughput.data_rate = value / 1024
            elif unit == 'MB':
                result.throughput.data_rate = value
            elif unit == 'GB':
                result.throughput.data_rate = value * 1024

        # 解析错误数
        errors_match = re.search(r'Non-2xx or 3xx responses:\s+(\d+)', output)
        if errors_match:
            result.error_count = int(errors_match.group(1))
            if result.throughput.total_requests > 0:
                result.error_rate = result.error_count / result.throughput.total_requests

        # 解析 Socket 错误
        socket_errors = re.search(r'Socket errors: connect (\d+), read (\d+), write (\d+), timeout (\d+)', output)
        if socket_errors:
            result.error_count += sum(int(x) for x in socket_errors.groups())
            if result.throughput.total_requests > 0:
                result.error_rate = result.error_count / result.throughput.total_requests

        return result

    @staticmethod
    def _convert_to_ms(value: float, unit: str) -> float:
        """将时间单位转换为毫秒"""
        unit = unit.lower()
        if unit == 'us':
            return value / 1000
        elif unit == 'ms':
            return value
        elif unit == 's':
            return value * 1000
        return value


class JSONResultParser:
    """JSON 格式测试结果解析器"""

    @staticmethod
    def parse(data: Dict[str, Any]) -> TestResult:
        """解析 JSON 格式的测试结果"""
        result = TestResult()

        # 解析基本字段
        result.test_id = data.get('test_id', '')
        result.timestamp = data.get('timestamp', datetime.now().isoformat())
        result.success = data.get('success', True)
        result.error_count = data.get('error_count', 0)
        result.error_rate = data.get('error_rate', 0.0)

        # 解析配置
        config_data = data.get('config', {})
        result.config = TestConfig(
            language=config_data.get('language', ''),
            endpoint=config_data.get('endpoint', ''),
            test_type=config_data.get('test_type', ''),
            concurrency=config_data.get('concurrency', 1),
            duration=config_data.get('duration', 30),
            threads=config_data.get('threads', 1),
            data_size=config_data.get('data_size', 0),
            format=config_data.get('format', ''),
            filters=config_data.get('filters', {})
        )

        # 解析延迟指标
        latency_data = data.get('latency', {})
        result.latency = LatencyMetrics(
            avg=latency_data.get('avg', 0.0),
            min=latency_data.get('min', 0.0),
            max=latency_data.get('max', 0.0),
            p50=latency_data.get('p50', 0.0),
            p75=latency_data.get('p75', 0.0),
            p90=latency_data.get('p90', 0.0),
            p95=latency_data.get('p95', 0.0),
            p99=latency_data.get('p99', 0.0),
            stdev=latency_data.get('stdev', 0.0)
        )

        # 解析吞吐量指标
        throughput_data = data.get('throughput', {})
        result.throughput = ThroughputMetrics(
            qps=throughput_data.get('qps', 0.0),
            total_requests=throughput_data.get('total_requests', 0),
            total_duration=throughput_data.get('total_duration', 0.0),
            data_rate=throughput_data.get('data_rate', 0.0),
            records_per_second=throughput_data.get('records_per_second', 0.0)
        )

        # 解析资源指标
        resources_data = data.get('resources', {})
        result.resources = ResourceMetrics(
            cpu_usage=resources_data.get('cpu_usage', 0.0),
            memory_usage=resources_data.get('memory_usage', 0.0),
            memory_usage_percent=resources_data.get('memory_usage_percent', 0.0),
            network_in=resources_data.get('network_in', 0.0),
            network_out=resources_data.get('network_out', 0.0),
            db_connections=resources_data.get('db_connections', 0)
        )

        # 解析元数据
        result.metadata = data.get('metadata', {})
        result.raw_output = data.get('raw_output', '')

        return result


class PrometheusMetricsParser:
    """Prometheus 指标解析器"""

    @staticmethod
    def parse(metrics_text: str) -> Dict[str, Any]:
        """解析 Prometheus 格式的指标"""
        metrics = {}

        for line in metrics_text.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # 解析指标格式: metric_name{labels} value
            match = re.match(r'([\w_]+)(?:\{([^}]*)\})?\s+([\d.]+)', line)
            if match:
                metric_name = match.group(1)
                labels_str = match.group(2) or ''
                value = float(match.group(3))

                # 解析标签
                labels = {}
                if labels_str:
                    for label in labels_str.split(','):
                        if '=' in label:
                            key, val = label.split('=', 1)
                            labels[key.strip()] = val.strip('"')

                if metric_name not in metrics:
                    metrics[metric_name] = []

                metrics[metric_name].append({
                    'value': value,
                    'labels': labels
                })

        return metrics


class ResultAggregator:
    """测试结果聚合器"""

    def __init__(self):
        self.results: List[TestResult] = []

    def add_result(self, result: TestResult):
        """添加测试结果"""
        self.results.append(result)

    def load_from_file(self, file_path: Path):
        """从文件加载测试结果"""
        file_path = Path(file_path)

        if file_path.suffix == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    for item in data:
                        self.results.append(JSONResultParser.parse(item))
                else:
                    self.results.append(JSONResultParser.parse(data))
        elif file_path.suffix == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                output = f.read()
                self.results.append(WrkResultParser.parse(output))
        else:
            logger.warning(f"Unsupported file format: {file_path}")

    def load_from_directory(self, dir_path: Path, pattern: str = '*'):
        """从目录加载测试结果"""
        dir_path = Path(dir_path)
        for file_path in dir_path.glob(pattern):
            if file_path.is_file():
                try:
                    self.load_from_file(file_path)
                    logger.info(f"Loaded results from: {file_path}")
                except Exception as e:
                    logger.error(f"Failed to load {file_path}: {e}")

    def get_results_by_language(self, language: str) -> List[TestResult]:
        """按语言筛选结果"""
        return [r for r in self.results if r.config.language == language]

    def get_results_by_test_type(self, test_type: str) -> List[TestResult]:
        """按测试类型筛选结果"""
        return [r for r in self.results if r.config.test_type == test_type]

    def get_results_by_endpoint(self, endpoint: str) -> List[TestResult]:
        """按接口筛选结果"""
        return [r for r in self.results if r.config.endpoint == endpoint]

    def aggregate_by_concurrency(self) -> Dict[int, List[TestResult]]:
        """按并发数聚合"""
        aggregated = {}
        for result in self.results:
            concurrency = result.config.concurrency
            if concurrency not in aggregated:
                aggregated[concurrency] = []
            aggregated[concurrency].append(result)
        return aggregated

    def aggregate_by_language(self) -> Dict[str, List[TestResult]]:
        """按语言聚合"""
        aggregated = {}
        for result in self.results:
            language = result.config.language
            if language not in aggregated:
                aggregated[language] = []
            aggregated[language].append(result)
        return aggregated

    def calculate_statistics(self, results: List[TestResult]) -> Dict[str, Any]:
        """计算统计信息"""
        if not results:
            return {}

        stats = {
            'count': len(results),
            'latency': {
                'avg': sum(r.latency.avg for r in results) / len(results),
                'p50': sum(r.latency.p50 for r in results) / len(results),
                'p90': sum(r.latency.p90 for r in results) / len(results),
                'p95': sum(r.latency.p95 for r in results) / len(results),
                'p99': sum(r.latency.p99 for r in results) / len(results),
            },
            'throughput': {
                'qps': sum(r.throughput.qps for r in results) / len(results),
                'total_requests': sum(r.throughput.total_requests for r in results),
            },
            'errors': {
                'count': sum(r.error_count for r in results),
                'rate': sum(r.error_rate for r in results) / len(results),
            }
        }

        return stats

    def export_to_json(self, output_path: Path):
        """导出为 JSON 文件"""
        output_path = Path(output_path)
        data = [r.to_dict() for r in self.results]

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Exported {len(self.results)} results to {output_path}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='解析测试结果')
    parser.add_argument('input', type=str, help='输入文件或目录路径')
    parser.add_argument('-o', '--output', type=str, help='输出 JSON 文件路径')
    parser.add_argument('-l', '--language', type=str, help='按语言筛选')
    parser.add_argument('-t', '--test-type', type=str, help='按测试类型筛选')

    args = parser.parse_args()

    aggregator = ResultAggregator()

    input_path = Path(args.input)
    if input_path.is_file():
        aggregator.load_from_file(input_path)
    elif input_path.is_dir():
        aggregator.load_from_directory(input_path)
    else:
        logger.error(f"Input path does not exist: {input_path}")
        return

    # 筛选结果
    if args.language:
        aggregator.results = aggregator.get_results_by_language(args.language)
    if args.test_type:
        aggregator.results = aggregator.get_results_by_test_type(args.test_type)

    # 导出结果
    if args.output:
        aggregator.export_to_json(args.output)
    else:
        # 打印统计信息
        stats = aggregator.calculate_statistics(aggregator.results)
        print(json.dumps(stats, indent=2))


if __name__ == '__main__':
    main()
