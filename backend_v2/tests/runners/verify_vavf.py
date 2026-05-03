from backend_v2.tests.runners.base_runner import BaseRunner

def test_smoke_pass():
    assert 1 + 1 == 2

def test_smoke_fail():
    assert 1 + 1 == 3

def verify_framework():
    runner = BaseRunner(suite_name="VAVF_Core_Verification")
    runner.start_suite()
    
    runner.run_test(
        test_id="V-000",
        category="SMOKE",
        description="Verify framework can log passing tests",
        test_func=test_smoke_pass
    )
    
    runner.run_test(
        test_id="V-001",
        category="SMOKE",
        description="Verify framework can log failing tests",
        test_func=test_smoke_fail
    )
    
    runner.finalize()

if __name__ == "__main__":
    verify_framework()
