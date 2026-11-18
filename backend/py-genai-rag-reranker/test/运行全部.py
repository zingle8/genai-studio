# -*- coding: utf-8 -*-
"""重排序服务（BGE-Reranker-v2-m3） — 运行全部测试：依次执行 冒烟/接口/压力/评估 并汇总

用法：python3 test/运行全部.py
"""
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).parent
SCRIPTS = ["冒烟测试.py", "接口测试.py", "压力测试.py", "评估测试.py"]

if __name__ == "__main__":
    results = {}
    for s in SCRIPTS:
        print(f"\n===== {s} =====")
        r = subprocess.run([sys.executable, str(HERE / s)])
        results[s] = "通过" if r.returncode == 0 else f"失败(code={r.returncode})"
    print("\n===== 汇总 =====")
    for s, v in results.items():
        print(f"{s}: {v}")
    raise SystemExit(1 if any(v != "通过" for v in results.values()) else 0)
