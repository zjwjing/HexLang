"""
HexLang - 符号编码系统

Copyright (c) 2026 zjwjing

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
import time
import os

LOG_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
LOG_PATH = os.path.join(LOG_DIR, 'health_log.jsonl')


def log_health(hex_result: dict, metrics: dict):
    """记录健康度数据，追加模式"""
    entry = {
        "timestamp": int(time.time()),
        "metrics": metrics,
        "hex_data": {
            "name": hex_result.get("name"),
            "bin": hex_result.get("bin"),
            "inter_hex": hex_result.get("inter_hex"),
            "yao_weights": hex_result.get("yao_weights"),
            "vector": hex_result.get("vector"),
        }
    }
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def read_history(limit=100):
    """读取最近 N 条健康度记录"""
    if not os.path.exists(LOG_PATH):
        return []
    records = []
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records[-limit:]


if __name__ == "__main__":
    from src.core.encoder import Hex64Encoder

    encoder = Hex64Encoder()
    test_metrics = {
        "cpu_usage": 85,
        "mem_usage": 70,
        "disk_io": 65,
        "network_latency": 120,
        "error_rate": 2,
        "uptime_days": 45,
    }

    # 计算卦象（模拟）
    bits = []
    for metric, threshold in [
        ("cpu_usage", 80), ("mem_usage", 75), ("disk_io", 70),
        ("network_latency", 100), ("error_rate", 1), ("uptime_days", 30)
    ]:
        bits.append(1 if test_metrics[metric] >= threshold else 0)
    bin_str = "".join(map(str, bits))
    inter_bits = [bits[1], bits[2], bits[3], bits[2], bits[3], bits[4]]
    inter_bin = "".join(map(str, inter_bits))

    result = {
        "name": "测试卦",
        "bin": bin_str,
        "inter_hex_bin": inter_bin,
        "yao_weights": [0.8, 0.9, 0.7, 1.2, 1.5, 0.6],
        "vector": [b * 0.5 for b in bits],
    }

    entry = log_health(result, test_metrics)
    print("记录成功:", json.dumps(entry, ensure_ascii=False, indent=2))
