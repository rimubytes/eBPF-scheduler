#!/usr/bin/env python3

import unittest
from typing import List

class SchedulerTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment before running tests."""
        # Check if running as root
        if os.geteuid() != 0:
            raise RuntimeError("Tests must be run as root")
        
        # Compile and load the scheduler
        cls.load_scheduler()