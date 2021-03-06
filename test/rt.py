import datetime
import sys
import unittest

sys.path.insert(0, '../stock/')

import dateutil2

class TestStockAdvise(unittest.TestCase):

    def test_is_trade_time(self):
        self.assertEqual(dateutil2.is_trade_time(datetime.datetime(2016, 1, 1, 9, 26)), False)
        self.assertEqual(dateutil2.is_trade_time(datetime.datetime(2016, 1, 1, 9, 30)), True)
        self.assertEqual(dateutil2.is_trade_time(datetime.datetime(2016, 1, 1, 11, 30)), True)
        self.assertEqual(dateutil2.is_trade_time(datetime.datetime(2016, 1, 1, 12, 30)), False)
        self.assertEqual(dateutil2.is_trade_time(datetime.datetime(2016, 1, 1, 13, 0)), True)
        self.assertEqual(dateutil2.is_trade_time(datetime.datetime(2016, 1, 1, 15, 0)), True)
        self.assertEqual(dateutil2.is_trade_time(datetime.datetime(2016, 1, 1, 15, 5)), False)

    def test_is_trade_date(self):
        self.assertFalse(dateutil2.is_trade_date(datetime.date(2016, 10, 7)))
        self.assertTrue(dateutil2.is_trade_date(datetime.date(2016, 10, 10)))
        self.assertFalse(dateutil2.is_trade_date(datetime.date(2016, 12, 31)))
        self.assertFalse(dateutil2.is_trade_date(datetime.date(2017, 1, 1)))
        self.assertFalse(dateutil2.is_trade_date(datetime.date(2017, 1, 2)))
        self.assertTrue(dateutil2.is_trade_date(datetime.date(2017, 1, 3)))

if __name__ == '__main__':
    unittest.main()
