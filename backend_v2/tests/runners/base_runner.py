import time
import traceback
from datetime import datetime
from typing import List, Callable, Any
from .schema import TestResult, SuiteReport, TestStatus, PerformanceMetrics
from .logger import ValidationLogger

class BaseRunner:
    def __init__(self, suite_name: str):
        self.suite_name = suite_name
        self.logger = ValidationLogger()
        self.results: List[TestResult] = []
        self.start_time = None

    def run_test(self, test_id: str, description: str, category: str, test_func: Callable, *args, **kwargs) -> TestResult:
        start_ts = time.perf_counter()
        status = TestStatus.PASS
        error_msg = None
        extracted_data = {}
        metrics = {}
        
        try:
            # Execute the test function and capture return value
            ret = test_func(*args, **kwargs)
            if isinstance(ret, dict):
                extracted_data = ret.get("extracted_data", {})
                metrics = ret.get("metrics", {})
        except Exception as e:
            status = TestStatus.FAIL
            error_msg = str(e)
            
        end_ts = time.perf_counter()
        latency = (end_ts - start_ts) * 1000
        
        result = TestResult(
            test_id=test_id,
            category=category,
            description=description,
            status=status,
            performance=PerformanceMetrics(total_latency_ms=latency),
            error_message=error_msg,
            extracted_data=extracted_data,
            metrics=metrics
        )
        
        self.results.append(result)
        self.logger.log_test_result(result)
        return result

    def finalize(self):
        end_time = datetime.now().isoformat()
        passed = sum(1 for r in self.results if r.status == TestStatus.PASS)
        failed = sum(1 for r in self.results if r.status == TestStatus.FAIL)
        errors = sum(1 for r in self.results if r.status == TestStatus.ERROR)
        
        report = SuiteReport(
            suite_name=self.suite_name,
            start_time=self.start_time or datetime.now().isoformat(),
            end_time=end_time,
            total_tests=len(self.results),
            passed=passed,
            failed=failed,
            errors=errors,
            results=self.results
        )
        
        self.logger.save_report(report)
        return report

    def start_suite(self):
        self.start_time = datetime.now().isoformat()
        self.logger.logger.info(f"=== Starting Test Suite: {self.suite_name} ===")
