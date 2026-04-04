#!/usr/bin/env python3
"""
Lightweight Docker Container Metrics Exporter (cAdvisor replacement for macOS)
Provides Prometheus-compatible /metrics endpoint using Docker API
"""

import json
import os
import socket
import time
import http.server
import socketserver
from datetime import datetime

PORT = 8080


def docker_request(path, method="GET"):
    """Make HTTP request to Docker via Unix socket"""
    sock_path = os.environ.get("DOCKER_SOCK", "/var/run/docker.sock")
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        sock.connect(sock_path)
        req = f"{method} {path} HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n"
        sock.sendall(req.encode())

        response = b""
        while True:
            chunk = sock.recv(8192)
            if not chunk:
                break
            response += chunk

        response_str = response.decode("utf-8", errors="ignore")

        # Split headers and body
        if "\r\n\r\n" in response_str:
            header_part, body = response_str.split("\r\n\r\n", 1)

            # Check for chunked transfer encoding
            is_chunked = "Transfer-Encoding: chunked" in header_part

            if is_chunked and body:
                # Decode chunked transfer encoding
                decoded_body = ""
                pos = 0
                while pos < len(body):
                    # Find chunk size line (ends with \r\n)
                    crlf_pos = body.find("\r\n", pos)
                    if crlf_pos == -1:
                        break

                    # Parse chunk size (hex)
                    size_str = body[pos:crlf_pos].strip()
                    try:
                        chunk_size = int(size_str, 16)
                    except ValueError:
                        break

                    if chunk_size == 0:
                        break  # Last chunk

                    # Extract chunk data
                    chunk_start = crlf_pos + 2  # Skip \r\n after size
                    chunk_end = chunk_start + chunk_size
                    if chunk_end > len(body):
                        break

                    decoded_body += body[chunk_start:chunk_end]
                    pos = chunk_end + 2  # Skip \r\n after chunk data

                return json.loads(decoded_body) if decoded_body else None
            elif body.strip():
                # Try direct JSON parse
                body = body.strip()
                if body.startswith("["):
                    return json.loads(body)
                else:
                    items = []
                    for line in body.split("\n"):
                        line = line.strip()
                        if line:
                            try:
                                items.append(json.loads(line))
                            except json.JSONDecodeError:
                                continue
                    return items if items else None
        return None
    except Exception as e:
        print(f"Docker API error: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        sock.close()


def get_docker_stats():
    """Get container stats from Docker API"""
    containers = docker_request("/containers/json?all=true")
    if not containers:
        print("Warning: No containers returned from Docker API")
        return []

    # Ensure we have a list
    if not isinstance(containers, list):
        print(f"Warning: Expected list, got {type(containers)}: {str(containers)[:200]}")
        return []

    stats = []
    for container in containers:
        # Validate container object
        if not isinstance(container, dict):
            print(f"Warning: Skipping non-dict item: {type(container)}")
            continue

        if "Id" not in container or "Names" not in container:
            print(f"Warning: Missing required fields in container: {list(container.keys())}")
            continue

        cid = str(container["Id"])[:12]
        name = container["Names"][0].lstrip("/") if container.get("Names") else "unknown"
        state = container.get("State", "unknown")

        if state != "running":
            continue

        # Get container-specific stats
        cstats = docker_request(f"/containers/{container['Id']}/stats?stream=false&one-shot=true")
        if not cstats or not isinstance(cstats, dict):
            continue

        try:
            # Parse CPU usage
            cpu_stats = cstats.get("cpu_stats", {})
            precpu_stats = cstats.get("precpu_stats", {})
            cpu_delta = cpu_stats.get("cpu_usage", {}).get("total_usage", 0) - \
                       precpu_stats.get("cpu_usage", {}).get("total_usage", 0)
            system_delta = cpu_stats.get("system_cpu_usage", 0) - \
                          precpu_stats.get("system_cpu_usage", 0)
            online_cpus = cpu_stats.get("online_cpus", 1)
            cpu_percent = (cpu_delta / system_delta * online_cpus * 100.0) if system_delta > 0 else 0.01

            # Parse memory usage
            mem_stats = cstats.get("memory_stats", {})
            mem_usage = mem_stats.get("usage", 0)
            mem_limit = mem_stats.get("limit", 0)

            stats.append({
                "id": cid,
                "name": name,
                "image": container.get("Image", "unknown"),
                "cpu_percent": round(cpu_percent, 4),
                "mem_usage_bytes": mem_usage,
                "mem_limit_bytes": mem_limit,
            })
        except Exception as e:
            print(f"Warning: Could not parse stats for {name}: {e}")
            continue

    return stats


def format_prometheus_metrics(stats):
    """Format stats as Prometheus metrics"""
    lines = []
    timestamp = int(time.time() * 1000)

    lines.append("# HELP container_cpu_usage_seconds_total Total CPU time consumed (percentage)")
    lines.append("# TYPE container_cpu_usage_seconds_total counter")
    lines.append("# HELP container_memory_usage_bytes Current memory usage in bytes")
    lines.append("# TYPE container_memory_usage_bytes gauge")
    lines.append("# HELP container_memory_max_usage_bytes Memory limit in bytes")
    lines.append("# TYPE container_memory_max_usage_bytes gauge")
    lines.append("# HELP cadvisor_version_info Information about exporter version")
    lines.append("# TYPE cadvisor_version_info gauge")
    lines.append(f'cadvisor_version_info{{version="macos-exporter-1.0"}} 1 {timestamp}')

    for s in stats:
        name_safe = s["name"].replace("-", "_").replace(".", "_").replace("/", "_")
        labels = f'container="{s["name"]}",image="{s["image"]}",id="{s["id"]}"'

        lines.append(f'container_cpu_usage_seconds_total{{{labels}}} {s["cpu_percent"]} {timestamp}')
        lines.append(f'container_memory_usage_bytes{{{labels}}} {s["mem_usage_bytes"]} {timestamp}')
        lines.append(f'container_memory_max_usage_bytes{{{labels}}} {s["mem_limit_bytes"]} {timestamp}')

    return "\n".join(lines) + "\n"


class MetricsHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/metrics":
            stats = get_docker_stats()
            metrics = format_prometheus_metrics(stats)

            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(metrics.encode())
        elif self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "healthy"}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        print(f"[{datetime.now().isoformat()}] {format % args}")


def main():
    print(f"Starting Docker Metrics Exporter on port {PORT}")
    print(f"This is a lightweight cAdvisor replacement for macOS/Docker Desktop")

    with socketserver.TCPServer(("", PORT), MetricsHandler) as httpd:
        print(f"Server running at http://0.0.0.0:{PORT}/metrics")
        print(f"Health check: http://0.0.0.0:{PORT}/health")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
