# -*- coding: utf-8 -*-
import sys

sys.path.insert(0, './tapestar/fixed/')
sys.path.insert(0, '../fixed/')

#import curses  
from datetime import date, datetime, timedelta
import fixeddatautil # own
import locale
from lxml import etree
import math
import time
import unicodedata
#import color

def wide_chars(s):
    return sum(unicodedata.east_asian_width(x)=='W' or unicodedata.east_asian_width(x)=='A' \
        or unicodedata.east_asian_width(x)=='F' for x in s)
def width(s):
    return len(s) + wide_chars(s)

reload(sys)  
sys.setdefaultencoding('utf8')  

locale.setlocale(locale.LC_ALL, '')
system_code = locale.getpreferredencoding()

c_highlight_blue = '\033[1;34;40m'
c_highlight_red = '\033[1;31;40m'
c_highlight_green = '\033[1;32;40m'
c_default_white = '\033[0;37;40m'
c_reset = '\033[0m'

def get_silver_advice(item, current):
    percent = (current - item['low']) / (item['high'] - item['low'])
    advice = ''
    if percent <= 0.2:
        advice = '买入'
    elif percent <= 0.4:
        advice = '反向卖出'
    elif percent >= 0.6:
        advice = '卖出'
    elif percent >= 0.8:
        advice = '卖出/反向买入'
    if advice != '' or g_arg_showAll:
        advice += ' (%2.0f%%)' % (percent * 100)
    return advice

def get_copper_advice(item, current):
    percent = (current - item['low']) / (item['high'] - item['low'])
    advice = ''
    if percent <= 0.2:
        advice = '买入'
    elif percent <= 0.4:
        advice = '反向卖出'
    elif percent >= 0.6:
        advice = '卖出'
    elif percent >= 0.8:
        advice = '卖出/反向买入'
    if advice != '' or g_arg_showAll:
        advice += ' (%2.0f%%)' % (percent * 100)
    return advice

def get_msft_advice(item, current):
    if current > item['high']:
        return '%s%s%s' % (c_highlight_blue, '卖出', c_reset)
    return ''

invest_items = [
    {
        'code': 'silver',
        'name': '白    银',
        'high': 4.301,
        'low': 2.836,
        'current': fixeddatautil.get_silver_current,
        'advice': get_silver_advice,
    },
    {
        'code': 'copper',
        'name': '黄    铜',
        'high': 8765.0,
        'low': 4318.0,
        'current': fixeddatautil.get_copper_current,
        'advice': get_copper_advice,
    },
    {
        'code': 'msft',
        'name': '微    软',
        'high': 70, # 超过该价格建议卖出
        'current': fixeddatautil.get_msft_current,
        'advice': get_msft_advice,
    },
]

def advice_all():
    print '\n'
    print '    ' + '——' * 22
    for item in invest_items:
        advise(item)
    print '    ' + '——' * 22
    print '\n'

def advise(item):
    current = item['current']()
    advice = item['advice'](item, current)

    if g_arg_showAll or advice != '':
        advice_str = '    %s    %9.3f    %s' % (item['name'], current, advice)
        print advice_str

g_arg_showAll = False

def parse_args():
    global g_arg_showAll 
    if len(sys.argv) >= 2:
        index = 1
        while index < len(sys.argv):
            if sys.argv[index] == '-a':
                g_arg_showAll = True
            index += 1

if __name__=='__main__':
    parse_args()
    advice_all()
    pass

