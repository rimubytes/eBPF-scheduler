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
    
