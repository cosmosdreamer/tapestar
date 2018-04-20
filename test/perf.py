from datetime import datetime
import sys
# import unittest

sys.path.insert(0, '../stock/')

import advise

def test_preprocess_perf():
    start = datetime.now()
    #advise.preprocess_all()
    advise.preprocess_stock(advise.all_stocks[1])
    print datetime.now() - start

if __name__ == '__main__':
    test_preprocess_perf()
#    unittest.main()
