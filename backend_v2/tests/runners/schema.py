from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

class TestStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    ERROR = "ERROR"
    SKIPPED = "SKIPPED"
    REVIEW = "REVIEW"

class ModuleResult(BaseModel):
    name: str
    status: TestStatus
    latency_ms: float
    output: Dict[str, Any] = {}
    extracted_data: Dict[str, Any] = {} # New: Detailed OCR/Biometric data
    metrics: Dict[str, float] = {}       # New: Granular metrics
    confidence: Optional[float] = None
    alerts: List[str] = []
    red_flags: List[str] = []           # New: Risk-specific alerts

class PerformanceMetrics(BaseModel):
    total_latency_ms: float
    cpu_usage_pct: Optional[float] = None
    memory_usage_mb: Optional[float] = None

class TestResult(BaseModel):
    test_id: str
    category: str
    description: str
    status: TestStatus
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    modules: List[ModuleResult] = []
    performance: PerformanceMetrics
    error_message: Optional[str] = None
    extracted_data: Dict[str, Any] = {}
    metrics: Dict[str, float] = {}
    red_flags: List[str] = []
    deviation: float = 0.0
    expected_status: TestStatus = TestStatus.PASS

class SuiteReport(BaseModel):
    suite_name: str
    start_time: str
    end_time: str
    total_tests: int
    passed: int
    failed: int
    errors: int
    results: List[TestResult] = []
    
    @property
    def pass_rate(self) -> float:
        if self.total_tests == 0: return 0.0
        return (self.passed / self.total_tests) * 100.0
