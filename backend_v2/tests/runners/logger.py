import json
import logging
import os
from datetime import datetime
from .schema import TestResult, SuiteReport

class ValidationLogger:
    def __init__(self, report_dir: str = "backend_v2/tests/reports"):
        self.report_dir = report_dir
        os.makedirs(report_dir, exist_ok=True)
        
        # Standard python logger for console output
        self.logger = logging.getLogger("VAVF")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def log_test_result(self, result: TestResult):
        color = "\033[92m" if result.status == "PASS" else "\033[91m"
        reset = "\033[0m"
        self.logger.info(f"Test {result.test_id}: {color}{result.status}{reset} ({result.performance.total_latency_ms:.1f}ms)")
        if result.status != "PASS" and result.error_message:
            self.logger.error(f"  Reason: {result.error_message}")

    def save_report(self, report: SuiteReport):
        filename = f"report_{report.suite_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.report_dir, filename)
        
        # Use serialization helper for safety
        from backend_v2.tests.runners.utils import to_jsonable
        data = to_jsonable(report.model_dump())
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        self.logger.info(f"Full report saved to {filepath}")
        
        # Also generate a markdown summary
        md_path = filepath.replace(".json", ".md")
        self.generate_markdown_summary(report, md_path)

    def generate_markdown_summary(self, report: SuiteReport, path: str):
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"# VAVF Validation Summary: {report.suite_name}\n\n")
            f.write(f"- **Time**: {report.start_time} to {report.end_time}\n")
            f.write(f"- **Pass Rate**: {report.pass_rate:.1f}%\n")
            f.write(f"- **Total/Passed/Failed**: {report.total_tests} / {report.passed} / {report.failed}\n\n")
            
            f.write("## Detailed Results\n\n")
            for r in report.results:
                status_emoji = "✅" if r.status == "PASS" else "❌" if r.status == "FAIL" else "⚠️"
                f.write(f"### {status_emoji} {r.test_id}: {r.description}\n")
                f.write(f"- **Status**: {r.status}\n")
                f.write(f"- **Latency**: {r.performance.total_latency_ms:.1f}ms\n")
                
                if r.extracted_data:
                    f.write("#### 📄 Extracted Details\n")
                    f.write("| Key | Value |\n")
                    f.write("| :--- | :--- |\n")
                    for k, v in r.extracted_data.items():
                        f.write(f"| {k} | {v} |\n")
                    f.write("\n")
                
                if r.metrics:
                    f.write("#### 📊 Metrics\n")
                    for m_name, m_val in r.metrics.items():
                        f.write(f"- **{m_name}**: {m_val}\n")
                    f.write("\n")
                
                if r.status != "PASS" and r.error_message:
                    f.write(f"> [!CAUTION]\n> **Failure Reason**: {r.error_message}\n\n")
                
                f.write("---\n\n")
