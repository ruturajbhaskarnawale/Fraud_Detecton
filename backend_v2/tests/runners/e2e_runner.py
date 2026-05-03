import os
import importlib.util
import inspect
from backend_v2.tests.runners.base_runner import BaseRunner

class E2ERunner(BaseRunner):
    def __init__(self):
        super().__init__(suite_name="E2E_Fraud_Scenarios")
        self.test_dir = "backend_v2/tests/suites/l3_e2e"

    def discover_and_run(self):
        self.start_suite()
        
        for filename in os.listdir(self.test_dir):
            if filename.startswith("test_") and filename.endswith(".py"):
                module_path = os.path.join(self.test_dir, filename)
                module_name = filename[:-3]
                
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                for name, obj in inspect.getmembers(module):
                    if name.startswith("test_") and inspect.isfunction(obj):
                        self.logger.logger.info(f"  Running {name}...")
                        self.run_test(
                            test_id=f"E2E-{name[5:].upper()}",
                            category="E2E",
                            description=f"E2E scenario from {filename}: {name}",
                            test_func=obj
                        )
        
        self.finalize()

if __name__ == "__main__":
    runner = E2ERunner()
    runner.discover_and_run()
