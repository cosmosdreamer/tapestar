import bisect
from datetime import date, datetime, timedelta
import tushare as ts

# ts.get_h_data('399106', index=True)
# ts.get_h_data('002337', start='2015-01-01', end='2015-03-16')

def calc():
    df = ts.get_realtime_quotes('sh')
    current_index = float(df['price'][0])

    indexes = []
    year = 2019
    while year >= 2010:
        df = get_indexOfYear(year)
        print '\nGot data of year %d' % (year)
        for i in range(0, len(df)):
            middle = (df['high'][i] - df['low'][i]) / 2 + df['low'][i]
            indexes.append(middle)
        stat_indexes(indexes, year, current_index)
        year -= 1

def stat_indexes(indexes, year, current_index):
    indexes.sort()
    # statistics
    print '\n\n Year: %d' % (year)
    print '\nTrade Days:  %d' % (len(indexes))
    print '\nLow: %7.2f' % (indexes[0])
    print '\nHigh: %7.2f' % (indexes[-1])
    theIndex = len(indexes) * 2 / 3
    print '\n67%%: %7.2f' % (indexes[theIndex])
    theIndex = len(indexes) / 2
    print '\n50%%: %7.2f' % (indexes[theIndex])
    theIndex = len(indexes) / 3
    print '\n33%%: %7.2f' % (indexes[theIndex])
    theIndex = bisect.bisect(indexes, current_index)
    print '\nCurrent: %2.0f%%' % (float(theIndex) * 100  / len(indexes))
    print '\n\n'

def get_indexOfYear(year):
    start = '%d-01-01' % (year)
    end = '%d-12-31' % (year)
    theTime = datetime.now()
    if year == theTime.year:
        end = theTime.strftime('%Y-%m-%d')
    df = ts.get_h_data('000001', start=start, end=end, index=True)
    # print df
    return df

if __name__ == '__main__':
    calc()
