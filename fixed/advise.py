# -*- coding: utf-8 -*-
import curses  
from datetime import date, datetime, timedelta
import fixeddata # own
import locale
from lxml import etree
import math
import sys  
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

def advice_all():
    print '\n'
    for item in fixeddata.fixed_items:
        advise(item)
    print '\n'

def advise(item):
    current = item['current']()
    percent = 0

    # pe
    pe = 0
    if item.has_key('pe'):
        pe = item['pe']()
    pe = ' ' * 5 if pe == 0 else '%5.2f' % pe

    advice = ''
    if item.has_key('high'):
        percent = (current - item['low']) / (item['high'] - item['low'])
        if percent <= 0.2:
            advice = '买入'
        elif percent >= 0.8:
            advice = '反向买入'

    # percent
    percent = ' ' * 7 if percent == 0.0 else '%6.2f%%' % (percent * 100)
    percent = '%s%s%s' % (c_highlight_blue, percent, c_reset)

    advice_str = '    %s    %9.3f    %s    %s    %s' % (item['name'], current, percent, pe, advice)
    print '    ' + '——' * 22
    #color = color.Color()
    #.stdout.write('\033[1;34;40m')
    print advice_str
    #sys.stdout.write('\033[0m')
    #color.print_blue_text(advice_str)
    print '    ' + '——' * 22
    for trade in item['trades']:
        # No. = month
        tradeDate = datetime.strptime(trade[0], '%Y-%m-%d').date()
        day = tradeDate.day
        number = tradeDate.month if day <= 10 else (tradeDate.month + 1)
        number = number if number <= 12 else (number - 12)
        kind = ((number - 1) % 3) + 1 
        theSellType = trade[1]
        number = '%2d.(%1d.%ld)' % (number, kind, theSellType)
        duration = math.floor((date.today() - tradeDate).days / 30)

        buy = trade[3]
        margin = 0
        if item.has_key('margin'):
            margin = item['margin']
        profit_ratio = (float(current) - margin - buy) / buy
        advice = ''
        profit_bar = 50
        if theSellType == 1:
            profit_bar = 10 + duration
        elif theSellType == 2:
            profit_bar = 20 + duration * 2
        else:
            profit_bar = 50 + duration * 3
        c_profit = c_default_white
        if profit_ratio * 100 >= profit_bar:
            advice = ' 卖出'
            c_profit = c_highlight_green
        profit_str = '%s%6.2f%%%s' % (c_profit, profit_ratio * 100, c_reset)
        trade_str = (' ' * 7) + ('%s %9.3f    %s    %s') % (number, buy, profit_str, advice)
        if not g_arg_simplified or advice != '':
            print trade_str
    if item.has_key('invertedTrades'):
        print '    ' + '——' * 22
        for trade in item['invertedTrades']:
            # No. = month
            tradeDate = datetime.strptime(trade[0], '%Y-%m-%d').date()
            day = tradeDate.day
            number = tradeDate.month if day <= 10 else (tradeDate.month + 1)
            number = number if number <= 12 else (number - 12)
            kind = ((number - 1) % 3) + 1 
            theSellType = trade[1]
            number = '%2d.(%1d.%ld)' % (number, kind, theSellType)
            duration = math.floor((date.today() - tradeDate).days / 30)

            buy = trade[3]
            margin = 0
            if item.has_key('margin'):
                margin = item['margin']
            profit_ratio = -(float(current) - buy) / buy
            advice = ''
            profit_bar = 20
            if theSellType == 1:
                profit_bar = 5 + duration * 0.5
            elif theSellType == 2:
                profit_bar = 10 + duration
            else:
                profit_bar = 20 + duration * 1.5
            c_profit = c_default_white
            if profit_ratio * 100 >= profit_bar:
                advice = ' 卖出'
                c_profit = c_highlight_green
            profit_str = '%s%6.2f%%%s' % (c_profit, profit_ratio * 100, c_reset)
            trade_str = (' ' * 7) + ('%s %9.3f    %s    %s') % (number, buy, profit_str, advice)
            if not g_arg_simplified or advice != '':
                print trade_str

g_arg_simplified = False

def parse_args():
    global g_arg_simplified
    if len(sys.argv) >= 2 and sys.argv[1] == '-s':
        g_arg_simplified = True


if __name__=='__main__':
    parse_args()
    advice_all()
    pass

