import time
import json
import logging
import traceback
from typing import Dict, Any, List
from pydantic import BaseModel, Field

class TestResult(BaseModel):
    test_id: str
    name: str
    category: str
    expected_output: str
    actual_output: str
    status: str  # PASS / FAIL
    logs: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    severity: str = "LOW"  # LOW/MEDIUM/HIGH/CRITICAL

class TestContext:
    def __init__(self):
        self.results: List[TestResult] = []
        self.passed = 0
        self.failed = 0
        self.total = 0
    
    def add_result(self, result: TestResult):
        self.results.append(result)
        self.total += 1
        if result.status == "PASS":
            self.passed += 1
        else:
            self.failed += 1

def generate_reports(context: TestContext, report_dir: str):
    import os
    os.makedirs(report_dir, exist_ok=True)
    
    # 1. JSON Report
    json_path = os.path.join(report_dir, "veridex_test_report.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump([r.model_dump() for r in context.results], f, indent=2)
    
    # 2. Markdown Report
    md_path = os.path.join(report_dir, "veridex_test_report.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# Veridex KYC Complete Test Report\n\n")
        f.write(f"**Total Tests**: {context.total}\n")
        f.write(f"**Passed**: {context.passed}\n")
        f.write(f"**Failed**: {context.failed}\n")
        pass_rate = (context.passed / context.total * 100) if context.total > 0 else 0
        f.write(f"**Pass Rate**: {pass_rate:.2f}%\n\n")
        
        for r in context.results:
            f.write(f"### {r.test_id}: {r.name} ({r.status})\n")
            f.write(f"- **Category**: {r.category}\n")
            f.write(f"- **Expected**: {r.expected_output}\n")
            f.write(f"- **Actual**: {r.actual_output}\n")
            f.write(f"- **Severity**: {r.severity}\n")
            if r.metrics:
                f.write(f"- **Metrics**: {r.metrics}\n")
            if r.errors:
                f.write(f"- **Errors**: {r.errors}\n")
            f.write("\n")
            
    # 3. Failures Only Markdown Report
    fail_path = os.path.join(report_dir, "failures_only.md")
    with open(fail_path, "w", encoding="utf-8") as f:
        f.write("# Veridex KYC Test Failures\n\n")
        failures = [r for r in context.results if r.status == "FAIL"]
        if not failures:
            f.write("No failures! Great job.\n")
        for r in failures:
            f.write(f"### {r.test_id}: {r.name}\n")
            f.write(f"- **Module**: {r.category}\n")
            f.write(f"- **Severity**: {r.severity}\n")
            f.write(f"- **Error**: {r.errors}\n\n")

