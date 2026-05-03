import os
import importlib.util
import inspect
import psutil
from backend_v2.tests.runners.base_runner import BaseRunner

class L5Runner(BaseRunner):
    def __init__(self):
        super().__init__(suite_name="L5_Performance_Stress")
        self.test_dir = "backend_v2/tests/suites/l5_performance"

    def discover_and_run(self):
        self.start_suite()
        
        process = psutil.Process(os.getpid())
        
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
                        
                        # Capture memory before
                        mem_start = process.memory_info().rss / 1024 / 1024
                        
                        result = self.run_test(
                            test_id=f"L5-{name[5:].upper()}",
                            category="PERFORMANCE",
                            description=f"Performance test from {filename}: {name}",
                            test_func=obj
                        )
                        
                        # Attach memory metrics to the result
                        mem_end = process.memory_info().rss / 1024 / 1024
                        result.performance.memory_usage_mb = mem_end
                        self.logger.logger.info(f"    Memory: {mem_end:.1f} MB (Delta: {mem_end - mem_start:.1f} MB)")
        
        self.finalize()

if __name__ == "__main__":
    runner = L5Runner()
    runner.discover_and_run()
