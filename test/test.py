from datetime import datetime
import sys

sys.path.insert(0, '../stock/')

import advise
import tdal

def test_recent_high():
    #print advise.get_recent_high_from_date('000025', '2018-2-9')

    #start = datetime.now()
    #advise.preprocess_stock(advise.all_stocks[1])
    #print datetime.now() - start

    print tdal.previous_data_with_date('000025', '2018-2-10')
    print tdal.previous_data_with_date('000025', '2018-2-11')
    print tdal.previous_data_with_date('000025', '2018-2-12')
    print tdal.previous_data_with_date('000025', '2018-2-13')
    print tdal.previous_data_with_date('000025', '2018-2-14')
    print tdal.previous_data_with_date('000025', '2018-2-15')
    print tdal.previous_data_with_date('000025', '2018-2-16')
    print tdal.previous_data_with_date('000025', '2018-2-17')
    print tdal.previous_data_with_date('000025', '2018-2-18')
    print tdal.previous_data_with_date('000025', '2018-2-19')
    print tdal.previous_data_with_date('000025', '2018-2-20')
    print tdal.previous_data_with_date('000025', '2018-2-21')
    print tdal.previous_data_with_date('000025', '2018-2-22')
    print tdal.previous_data_with_date('000025', '2018-2-23')

if __name__ == '__main__':
    test_recent_high()
