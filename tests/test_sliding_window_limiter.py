import unittest

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname( __file__ ), '..'))


import time
from rate_limiter import SlidingWindowLimiter

class HitChangesCollector(object):
    def __init__(self):
        self.changes = []

    def __call__(self,hps):
        self.changes.append(hps)

class TestLimiter(unittest.TestCase):

    def test_slow_limiter(self):
        collector = HitChangesCollector()
        sensitivity = 1/60.0 # 1 hit a minute

        # 1 hit every second allowed
        total_hits = 3600
        remaining_hits = 3600

        limiter = SlidingWindowLimiter(sensitivity, collector)

        limiter.update(total_hits, remaining_hits)
        self.assertEqual(1, len(collector.changes))

        # hit the api 100 times in 1/10 sec
        for i in range(100):
            time.sleep(0.001)
            limiter.update(total_hits, remaining_hits)
            remaining_hits -= 1

        self.assertEqual(2, len(collector.changes))
        self.assertEqual(int(collector.changes[1]), int(collector.changes[0] - sensitivity))



    def test_speed_up_limiter(self):
        collector = HitChangesCollector()
        sensitivity = 0.01

        total_hits = 3600
        remaining_hits = (3600 / 2.0)

        limiter = SlidingWindowLimiter(sensitivity, collector)

        limiter.update(total_hits, remaining_hits)
        self.assertEqual(1, len(collector.changes))

        # we're running slow
        for i in range(5):
            time.sleep(5)
            limiter.update(total_hits, remaining_hits)
            remaining_hits += 10

        # should speed up
        self.assertEqual(2, len(collector.changes))
        self.assertEqual(int(collector.changes[1]), int(collector.changes[0] + sensitivity))

    def test_run_out_of_hits(self):
        collector = HitChangesCollector()
        sensitivity = 1/60.0 # 1 hit a minute

        # 1 hit every second allowed
        total_hits = 3600
        remaining_hits = 3600

        limiter = SlidingWindowLimiter(sensitivity, collector)

        # hit the api maximum times allowed
        for i in range(total_hits):
            limiter.update(total_hits, remaining_hits)
            remaining_hits -= 1

        self.assertEqual(60, len(collector.changes))

    def test_ignore_equals(self):
        collector = HitChangesCollector()
        sensitivity = 1/60.0 # 1 hit a minute

        # 1 hit every second allowed
        total_hits = 3600
        remaining_hits = 3600

        limiter = SlidingWindowLimiter(sensitivity, collector)

        # hit the api maximum times allowed
        for i in range(total_hits):
            limiter.update(total_hits, remaining_hits)

        self.assertEqual(1, len(collector.changes))

