#!/usr/bin/env python3

import unittest

import timekeeper


class TestPrefixes(unittest.TestCase):
    def setUp(self):
        self.old_activities = timekeeper.ACTIVITIES

    def tearDown(self):
        timekeeper.ACTIVITIES = self.old_activities

    def test_prefixes_default(self):
        self.assertEqual({"testing"}, timekeeper.prefixes())

    def test_prefixes(self):
        timekeeper.ACTIVITIES = ["testing a", "testing b", "programming a", "programming b", "other"]
        self.assertEqual(["programming", "testing"], sorted(list(timekeeper.prefixes())))

    def test_prefixes_empty(self):
        timekeeper.ACTIVITIES = ["testing", "programming", "other"]
        self.assertEqual(set(), timekeeper.prefixes())


class TestHms(unittest.TestCase):
    def test_zero(self):
        self.assertEqual((0, 0, 0), timekeeper.hms(0))

    def test_one(self):
        self.assertEqual((0, 0, 1), timekeeper.hms(1))

    def test_59(self):
        self.assertEqual((0, 0, 59), timekeeper.hms(59))

    def test_60(self):
        self.assertEqual((0, 1, 0), timekeeper.hms(60))

    def test_61(self):
        self.assertEqual((0, 1, 1), timekeeper.hms(61))

    def test_3599(self):
        self.assertEqual((0, 59, 59), timekeeper.hms(3599))
    
    def test_3600(self):
        self.assertEqual((1, 0, 0), timekeeper.hms(3600))
    
    def test_3601(self):
        self.assertEqual((1, 0, 1), timekeeper.hms(3601))

    def test_large(self):
        self.assertEqual((12, 45, 38), timekeeper.hms(12 * 3600 + 45 * 60 + 38))
    

class TestDurationWithSeconds(unittest.TestCase):
    def test_no_hours(self):
        self.assertEqual("12:08 min", timekeeper.duration_with_seconds(12 * 60 + 8))

    def test_with_hours(self):
        self.assertEqual("1:02:38 h", timekeeper.duration_with_seconds(1 * 3600 + 2 * 60 + 38))


class TestDuration(unittest.TestCase):
    def test_no_hours(self):
        self.assertEqual("0:12 h", timekeeper.duration(12))

    def test_with_hours(self):
        self.assertEqual("1:02 h", timekeeper.duration(1 * 60 + 2))


class TestDurationStats(unittest.TestCase):
    def test_range(self):
        stats = timekeeper.duration_stats(list(range(10)))
        self.assertEqual(0, stats[0])
        self.assertEqual(9, stats[1])
        self.assertTrue(abs(4.5 - stats[2]) < 0.001)
        self.assertTrue(abs(2.8722 - stats[3]) < 0.001)

    def test_empty(self):
        self.assertEqual(None, timekeeper.duration_stats([]))

    def test_one(self):
        self.assertEqual((1, 1, 1, 0), timekeeper.duration_stats([1]))


class TestParseTimestamp(unittest.TestCase):
    def test_oldstyle(self):
        self.assertEqual(1, timekeeper.parse_timestamp("1"))

    def test_newstyle(self):
        self.assertEqual(1322125872, timekeeper.parse_timestamp("20111124-101112"))


if __name__ == "__main__":
    unittest.main()
