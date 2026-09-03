#!/usr/bin/env python
"""Portable HTTP benchmark for comparable monolith/microservice runs.

The request path and workload stay independent from the deployment. Run this
script against the monolith and the gateway with identical arguments, then
compare the generated JSON files.
"""

import argparse
import json
import math
import re
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def fetch(url, timeout, headers=None):
    started = time.perf_counter()
    request_headers = {"User-Agent": "food-master-benchmark/1.0"}
    if headers:
        request_headers.update(headers)
    try:
        request = Request(url, headers=request_headers)
        with urlopen(request, timeout=timeout) as response:
            response.read(256)
            return response.status, (time.perf_counter() - started) * 1000, ""
    except HTTPError as exc:
        return exc.code, (time.perf_counter() - started) * 1000, str(exc)
    except (URLError, TimeoutError, OSError) as exc:
        return None, (time.perf_counter() - started) * 1000, str(exc)


def percentile(values, fraction):
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, math.ceil(len(ordered) * fraction) - 1))
    return round(ordered[index], 3)


def run_once(url, requests, concurrency, timeout, headers=None):
    started = time.perf_counter()
    results = []
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = [pool.submit(fetch, url, timeout, headers) for _ in range(requests)]
        for future in as_completed(futures):
            results.append(future.result())
    elapsed = time.perf_counter() - started
    latencies = [item[1] for item in results]
    successful = sum(item[0] is not None and 200 <= item[0] < 400 for item in results)
    failed = len(results) - successful
    return {
        "requests": len(results),
        "successful": successful,
        "failed": failed,
        "error_rate": round(failed / len(results), 4) if results else 1.0,
        "throughput_rps": round(successful / elapsed, 3) if elapsed else 0.0,
        "elapsed_seconds": round(elapsed, 3),
        "average_ms": round(sum(latencies) / len(latencies), 3) if latencies else None,
        "p95_ms": percentile(latencies, 0.95),
        "status_codes": {
            str(code) if code is not None else "network_error": sum(
                item[0] == code for item in results
            )
            for code in sorted(
                {item[0] for item in results}, key=lambda value: str(value)
            )
        },
    }


def parse_size(value):
    match = re.match(r"\s*([\d.]+)\s*([KMG]i?B)?", value or "")
    if not match:
        return None
    number = float(match.group(1))
    unit = (match.group(2) or "B").lower()
    factors = {
        "b": 1,
        "kb": 1024,
        "kib": 1024,
        "mb": 1024**2,
        "mib": 1024**2,
        "gb": 1024**3,
        "gib": 1024**3,
    }
    return round(number * factors.get(unit, 1) / 1024**2, 3)


def docker_stats(service):
    process = subprocess.run(
        [
            "docker",
            "stats",
            "--no-stream",
            "--format",
            "{{.CPUPerc}},{{.MemUsage}}",
            service,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if process.returncode != 0 or not process.stdout.strip():
        return None
    cpu, memory = process.stdout.strip().split(",", 1)
    return {
        "cpu_percent": float(cpu.rstrip("%")),
        "memory_mb": parse_size(memory.split("/", 1)[0]),
    }


def host_process_stats(pid):
    """Sample CPU% and RSS (MB) of a local host process via psutil.

    Used when the benchmarked service runs directly on the host (e.g. a
    locally-launched monolith dev server) and Docker is not available.
    Returns None when psutil is missing or the process cannot be sampled.
    """
    try:
        import psutil  # type: ignore[import-not-found]  # optional, dev-only
    except ImportError:
        return None
    try:
        proc = psutil.Process(pid)
        # Prime the CPU counter so the next call returns a real delta.
        proc.cpu_percent(interval=None)
        memory_mb = proc.memory_info().rss / (1024**2)
        time.sleep(0.5)
        cpu_percent = proc.cpu_percent(interval=None)
        return {"cpu_percent": cpu_percent, "memory_mb": round(memory_mb, 3)}
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--target", required=True, help="Base URL, for example http://127.0.0.1"
    )
    parser.add_argument(
        "--path", default="/health/ready/", help="Same endpoint for both versions"
    )
    parser.add_argument("--label", default="target")
    parser.add_argument("--requests", type=int, default=120)
    parser.add_argument("--concurrency", type=int, default=12)
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument(
        "--docker-service", help="Optional container name for CPU/memory sampling"
    )
    parser.add_argument(
        "--host-pid",
        type=int,
        default=0,
        help="Optional PID of a host process for CPU/memory sampling",
    )
    parser.add_argument(
        "--cookie",
        default="",
        help="Optional Cookie header value, e.g. 'sessionid=...'",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if min(args.requests, args.concurrency, args.runs) <= 0:
        parser.error("requests, concurrency, and runs must be positive")

    url = args.target.rstrip("/") + "/" + args.path.lstrip("/")
    headers = {"Cookie": args.cookie} if args.cookie else None
    runs = []
    for number in range(1, args.runs + 1):
        if args.docker_service:
            resources = docker_stats(args.docker_service)
        elif args.host_pid:
            resources = host_process_stats(args.host_pid)
        else:
            resources = None
        result = run_once(url, args.requests, args.concurrency, args.timeout, headers)
        result["run"] = number
        result["resource_sample"] = resources
        runs.append(result)
        print(
            f"{args.label} run {number}: {result['successful']}/{result['requests']} ok, "
            f"{result['throughput_rps']} req/s, avg {result['average_ms']} ms, "
            f"p95 {result['p95_ms']} ms"
        )

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "label": args.label,
        "target": url,
        "workload": {
            "requests_per_run": args.requests,
            "concurrency": args.concurrency,
            "runs": args.runs,
            "timeout_seconds": args.timeout,
        },
        "runs": runs,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
