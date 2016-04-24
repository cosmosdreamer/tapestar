# -*- coding: utf-8 -*-
import curses  
import tushare as ts
from datetime import date, datetime, timedelta
import time
import sys  
import locale
import httplib
import json
from lxml import etree
import lxml.html.soupparser as soupparser
import unicodedata
import math
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

def get_silver_current():
    current = 0
    conn = httplib.HTTPConnection("www.icbc.com.cn")
    conn.request("GET", "/ICBCDynamicSite/Charts/GoldTendencyPicture.aspx")
    res = conn.getresponse()
    if res.status == 200:
        theData = res.read()
        #print theData
        dom = soupparser.fromstring(theData)
        # no tbody for first table. index starts from 1
        current_price = dom.xpath("//body/form/table/tr/td/table[6]/tbody/tr/td/div/table/tbody/tr[3]/td[4]")
        if len(current_price) > 0:
            current_price = current_price[0].text.strip()
            current = float(current_price);
    conn.close()
    return current

def get_euro_current():
    current = 0
    conn = httplib.HTTPConnection("www.icbc.com.cn")
    conn.request("GET", "/ICBCDynamicSite/Optimize/Quotation/QuotationListIframe.aspx")
    res = conn.getresponse()
    if res.status == 200:
        theData = res.read()
        #print theData
        dom = soupparser.fromstring(theData)
        # no tbody for all tables. index starts from 1
        current_price = dom.xpath("//body/form/div/table/tr/td/table/tr[2]/td/table/tr[5]/td[4]")
        #print current_price
        if len(current_price) > 0:
            current_price = current_price[0].text.strip()
            current = float(current_price);
    conn.close()
    return current

def get_oil_current():
    return 240

def get_sh_current():
    df = ts.get_realtime_quotes('sh')
    return float(df['price'][0])

def get_sh_pe():
    pe = 0
    conn = httplib.HTTPConnection("www.csindex.com.cn")
    conn.request("GET", "/sseportal/ps/zhs/hqjt/csi/show_zsgz.js")
    res = conn.getresponse()
    if res.status == 200:
        theData = res.read().split('\n')[2]
        theData = theData[12:-2]
        #print theData
        pe = float(theData)
    conn.close()
    return pe

def get_hs_current():
    current = 0
    theDate = date.today()
    count = 0
    while current == 0 and count < 5:
        theDateStr = theDate.strftime('%d%b%y').lstrip('0')
        conn = httplib.HTTPConnection("www.hsi.com.hk")
        conn.request("GET", "/HSI-Net/static/revamp/contents/en/indexes/report/hsi/idx_" + theDateStr + ".csv")
        res = conn.getresponse()
        if res.status == 200:
            theData = res.read().split('\t')
            current = theData[(3 - 1) * 12 + 6 - 1]
            current = current.replace('"', '').replace('\0', '')
            current = float(current)
        conn.close()
        count += 1
        theDate = theDate - timedelta(days=1)
    return current

def get_hs_pe():
    pe = 0
    theDate = date.today()
    count = 0
    while pe == 0 and count < 5:
        theDateStr = theDate.strftime('%d%b%y').lstrip('0')
        conn = httplib.HTTPConnection("www.hsi.com.hk")
        conn.request("GET", "/HSI-Net/static/revamp/contents/en/indexes/report/hsi/idx_" + theDateStr + ".csv")
        res = conn.getresponse()
        if res.status == 200:
            theData = res.read().split('\t')
            pe = theData[(3 - 1) * 12 + 10 - 1]
            pe = pe.replace('"', '').replace('\0', '')
            pe = float(pe)
        conn.close()
        count += 1
        theDate = theDate - timedelta(days=1)
    return pe

def get_hl_current():
    pe = 0
    conn = httplib.HTTPConnection("www.csindex.com.cn")
    conn.request("GET", "/sseportal/ps/zhs/hqjt/csi/show_zsbx.js")
    res = conn.getresponse()
    if res.status == 200:
        theData = res.read().split('\n')[74]
        theData = theData[12:-2]
        #print theData
        pe = float(theData)
    conn.close()
    return pe

def get_hl_pe():
    pe = 0
    conn = httplib.HTTPConnection("www.csindex.com.cn")
    conn.request("GET", "/sseportal/ps/zhs/hqjt/csi/show_zsgz.js")
    res = conn.getresponse()
    if res.status == 200:
        theData = res.read().split('\n')[74]
        theData = theData[12:-2]
        #print theData
        pe = float(theData)
    conn.close()
    return pe

def get_sz162411_current():
    df = ts.get_realtime_quotes('162411')
    return float(df['price'][0])

def get_msft_current():
    current = 0
    conn = httplib.HTTPConnection("hq.sinajs.cn")
    conn.request("GET", "/list=gb_msft")
    res = conn.getresponse()
    if res.status == 200:
        theData = res.read()
        current_price = theData[25:30]
        current = float(current_price)
    conn.close()
    return current

fixed_items = [
    {
        'code': 1,
        'name': '白    银',
        'high': 4.301,
        'low': 2.836,
        'current': get_silver_current,
        'margin': 0.04,
        'trades': [
            #['2015-12-14', 1, 3000, 2.87],
            ['2016-1-1', 1, 1000, 2.994],
            ['2016-1-1', 1, 2000, 2.939],
            ['2016-1-1', 1, 1000, 2.947],
            ['2016-1-1', 1, 2000, 2.904],
            ['2016-2-29', 1, 643, 3.106],
            ['2016-3-31', 1, 313, 3.191],
            ['2016-4-5', 1, 318, 3.146],
        ],
    },
    {
        'code': 2,
        'name': '账户欧元',
        'high': 871.0,
        'low': 654.0,
        'current': get_euro_current,
        'margin': 1.6,
        'trades': [
            ['2016-2-29', 1, 140, 716.28],
            ['2016-3-31', 1, 133, 733.91],
        ],
    },
    {
        'code': 'sh',
        'name': '上证指数',
        'high': 5178.19,
        'low': 1849.65,
        'current': get_sh_current,
        'pe': get_sh_pe,
        'trades': [
            ['2016-3-1', 1, 1000, 2733.17, 0.9190], # 工行 华夏沪深300指数
            ['2016-4-6', 1, 300, 3055.35, 3.253], # 300ETF
        ],
    },
    {
        'code': 'hl',
        'name': '红利指数',
        'high': 4195.20,
        'low': 1320.25,
        'current': get_hl_current,
        'pe': get_hl_pe,
        'trades': [
            ['2016-3-31', 1, 500, 2412.31, 2.404], # 红利ETF
        ],
    },
    {
        'code': 'hs',
        'name': '恒生指数',
        'high': 31958.41,
        'low': 10676.29,
        'current': get_hs_current,
        'pe': get_hs_pe,
        'trades': [
            ['2016-4-1', 1, 1000, 20616.25, 1.036], # 恒生ETF
        ],
    },
    {
        'code': 'sz162411',
        'name': '华宝油气',
        'high': 1.348,
        'low': 0.431,
        'current': get_sz162411_current,
        #'pe': get_sz162411_pe,
        'trades': [
        ],
    },
    {
        'code': 'msft',
        'name': '微    软',
        'current': get_msft_current,
        'trades': [
        ],
    },
]

c_highlight_blue = '\033[1;34;40m'
c_reset = '\033[0m'

def advice_all():
    print '\n'
    for item in fixed_items:
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
        number = '%2d.' % number

        buy = trade[3]
        margin = 0
        if item.has_key('margin'):
            margin = item['margin']
        profit_ratio = (float(current) - margin - buy) / buy
        advice = ''
        if profit_ratio > 0.06:
            advice = ' 卖出'
        trade_str = (' ' * 9) + ('%s    %9.3f    %6.2f%%    %s') % (number, buy, profit_ratio * 100, advice)
        print trade_str
 
if __name__=='__main__':
    advice_all()
    pass

