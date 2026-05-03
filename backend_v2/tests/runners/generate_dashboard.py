import os
import json
from datetime import datetime
from typing import Dict, List, Any

def generate_dashboard():
    report_dir = "backend_v2/tests/reports"
    reports = [f for f in os.listdir(report_dir) if f.startswith("report_") and f.endswith(".json")]
    
    # Categorize and find latest for each suite
    latest_reports: Dict[str, Dict] = {}
    for r in reports:
        suite_name = r.split("report_")[1].rsplit("_", 2)[0]
        full_path = os.path.join(report_dir, r)
        with open(full_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Simple versioning: latest by timestamp in filename
            if suite_name not in latest_reports or r > latest_reports[suite_name]["filename"]:
                latest_reports[suite_name] = {"data": data, "filename": r}

    # Generate Markdown
    md_path = os.path.join(report_dir, "vavf_master_dashboard.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# Veridex Autonomous Validation Framework (VAVF) Master Dashboard\n\n")
        f.write(f"**Generated at**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## 🏁 Overall System Readiness\n\n")
        f.write("| Suite | Pass Rate | Total Tests | Status |\n")
        f.write("| :--- | :--- | :--- | :--- |\n")
        
        for suite, info in latest_reports.items():
            d = info["data"]
            pass_rate = (d["passed"] / d["total_tests"] * 100) if d["total_tests"] > 0 else 0
            status = "🟢 PRODUCTION READY" if pass_rate > 90 else "🟡 REVIEW REQUIRED" if pass_rate > 60 else "🔴 CRITICAL FAILURES"
            f.write(f"| {suite} | {pass_rate:.1f}% | {d['total_tests']} | {status} |\n")
        
        f.write("\n## 📊 Performance Benchmarks\n\n")
        perf_data = latest_reports.get("L5_Performance_Stress")
        if perf_data:
            f.write("| Metric | Value | Target |\n")
            f.write("| :--- | :--- | :--- |\n")
            # We extract some avg from results
            results = perf_data["data"]["results"]
            avg_latency = sum(r["performance"]["total_latency_ms"] for r in results) / len(results)
            max_mem = max(r["performance"]["memory_usage_mb"] for r in results if r["performance"]["memory_usage_mb"])
            f.write(f"| Mean Latency (Concurrent) | {avg_latency:.2f}ms | < 500ms |\n")
            f.write(f"| Peak Memory Usage | {max_mem:.1f} MB | < 1024 MB |\n")

        f.write("\n## 🛠️ Suite Details\n\n")
        for suite, info in latest_reports.items():
            d = info["data"]
            f.write(f"### {suite}\n")
            f.write(f"- **File**: {info['filename']}\n")
            f.write(f"- **Results**: {d['passed']} Pass, {d['failed']} Fail, {d['errors']} Error\n\n")
            
            if d["failed"] > 0:
                f.write("#### ❌ Failures to Address:\n")
                for r in d["results"]:
                    if r["status"] == "FAIL":
                        f.write(f"- **{r['test_id']}**: {r['error_message']}\n")
                f.write("\n")

    print(f"Master Dashboard generated at {md_path}")

if __name__ == "__main__":
    generate_dashboard()
