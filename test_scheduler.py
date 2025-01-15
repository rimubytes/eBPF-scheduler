import unittest
import subprocess
import time
import os
import psutil
from typing import List, Tuple
import threading

class SchedulerTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment before running tests."""
        # Check if running as root
        if os.geteuid() != 0:
            raise RuntimeError("Tests must be run as root")
        
        # Compile and load the scheduler
        cls.load_scheduler()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests are done."""
        cls.unload_scheduler()
    
    @classmethod
    def load_scheduler(cls):
        """Load the eBPF scheduler."""
        try:
            subprocess.run(['./start.sh'], check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to load scheduler: {e}")
    
    @classmethod
    def unload_scheduler(cls):
        """Unload the eBPF scheduler."""
        try:
            subprocess.run(['./stop.sh'], check=True)
        except subprocess.CalledProcessError:
            pass  # Ignore errors during cleanup
    
    def test_scheduler_loading(self):
        """Test if scheduler loads and unloads correctly."""
        # Check if scheduler is loaded
        with open('/sys/kernel/sched_ext/root/ops', 'r') as f:
            scheduler_name = f.read().strip()
        self.assertEqual(scheduler_name, 'minimal_scheduler')
    
    def test_process_scheduling(self):
        """Test if processes are being scheduled correctly."""
        def cpu_intensive_task():
            """CPU intensive task for testing."""
            start = time.time()
            while time.time() - start < 2:
                _ = [i * i for i in range(1000)]
        
        # Create and run multiple CPU-intensive processes
        threads: List[threading.Thread] = []
        for _ in range(4):
            thread = threading.Thread(target=cpu_intensive_task)
            thread.start()
            threads.append(thread)
        
        # Monitor CPU usage
        cpu_usage_samples = []
        for _ in range(10):
            cpu_usage_samples.append(psutil.cpu_percent(interval=0.2))
        
        # Wait for threads to complete
        for thread in threads:
            thread.join()
        
        # Check if CPU usage was distributed
        self.assertGreater(sum(cpu_usage_samples) / len(cpu_usage_samples), 0)
    
    def test_time_slice_distribution(self):
        """Test if time slices are being distributed fairly."""
        def monitor_process(duration: float) -> List[float]:
            """Monitor CPU usage of current process."""
            samples = []
            end_time = time.time() + duration
            while time.time() < end_time:
                samples.append(psutil.Process().cpu_percent(interval=0.1))
            return samples
        
        # Run two competing processes
        process1_samples: List[float] = []
        process2_samples: List[float] = []
        
        def run_process1():
            nonlocal process1_samples
            process1_samples = monitor_process(2.0)
        
        def run_process2():
            nonlocal process2_samples
            process2_samples = monitor_process(2.0)
        
        t1 = threading.Thread(target=run_process1)
        t2 = threading.Thread(target=run_process2)
        
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        
        # Calculate average CPU usage
        avg1 = sum(process1_samples) / len(process1_samples)
        avg2 = sum(process2_samples) / len(process2_samples)
        
        # Check if CPU time is roughly equal (within 20% margin)
        ratio = min(avg1, avg2) / max(avg1, avg2)
        self.assertGreater(ratio, 0.8)

    def test_scheduler_stress(self):
        """Stress test the scheduler with many processes."""
        def stress_task():
            """Short CPU-intensive task."""
            start = time.time()
            while time.time() - start < 0.5:
                _ = [i * i for i in range(1000)]
        
        # Launch many threads
        threads = []
        for _ in range(20):
            thread = threading.Thread(target=stress_task)
            thread.start()
            threads.append(thread)
        
        # Monitor system stability
        cpu_usage = []
        for _ in range(5):
            cpu_usage.append(psutil.cpu_percent(interval=0.2))
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Check if system remained responsive
        self.assertLess(max(cpu_usage), 100.0)
        
    def test_error_handling(self):
        """Test error handling in the scheduler."""
        # Try to load scheduler when already loaded
        result = subprocess.run(['./start.sh'], 
                              capture_output=True, 
                              text=True)
        self.assertNotEqual(result.returncode, 0)
        
        # Try to unload scheduler twice
        subprocess.run(['./stop.sh'])
        result = subprocess.run(['./stop.sh'], 
                              capture_output=True, 
                              text=True)
        self.assertNotEqual(result.returncode, 0)

if __name__ == '__main__':
    unittest.main(verbosity=2)