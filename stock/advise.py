# -*- coding: utf-8 -*-
import curses  
import tushare as ts
from dateutil import rrule
from datetime import date, datetime, timedelta
import time
import sys  
import locale
import pymongo
from pymongo import MongoClient
import httplib
import json
from lxml import etree
import lxml.html.soupparser as soupparser
import unicodedata
import math

def wide_chars(s):
    return sum(unicodedata.east_asian_width(x)=='W' or unicodedata.east_asian_width(x)=='A' \
        or unicodedata.east_asian_width(x)=='F' for x in s)
def width(s):
    return len(s) + wide_chars(s)

reload(sys)  
sys.setdefaultencoding('utf8')  

locale.setlocale(locale.LC_ALL, '')
system_code = locale.getpreferredencoding()

stdscr = None

#stock_codes = ['002450', '601766', '601288', '000488', '002008', '600522', '002164', '600008']
#eyeon_stock_codes = ['002290', '600029', '002570', '000898']

legal_holidays = [
    '2015/01/01',
    '2015/01/02',
    '2015/01/03',
    '2015/02/18',
    '2015/02/19',
    '2015/02/20',
    '2015/02/21',
    '2015/02/22',
    '2015/02/23',
    '2015/02/24',
    '2015/04/05',
    '2015/04/06',
    '2015/05/01',
    '2015/05/02',
    '2015/05/03',
    '2015/06/20',
    '2015/06/21',
    '2015/06/22',
    '2015/09/03',
    '2015/09/04',
    '2015/09/05',
    '2015/09/26',
    '2015/09/27',
    '2015/10/01',
    '2015/10/02',
    '2015/10/03',
    '2015/10/04',
    '2015/10/05',
    '2015/10/06',
    '2015/10/07',
    '2016/01/01',
    '2016/02/07',
    '2016/02/08',
    '2016/02/09',
    '2016/02/10',
    '2016/02/11',
    '2016/02/12',
    '2016/02/13',
    '2016/04/04',
    '2016/05/02',
    '2016/06/09',
    '2016/06/10',
    '2016/06/11',
    '2016/09/15',
    '2016/09/16',
    '2016/09/17',
    '2016/10/01',
    '2016/10/02',
    '2016/10/03',
    '2016/10/04',
    '2016/10/05',
    '2016/10/06',
    '2016/10/07',
]

client = MongoClient()
db = client.stock
# history schema: {"code": code, "date": tdatestr, "close": df['close'][0], "open": df['open'][0], "high": df['high'][0]}
c = db.history
# trade schema: {"code": code, "recent_high": dh['high']}
#db.trade.drop()
#c_trade = db.trade
#db.dayK.drop()
reset_KDJ = False
c_dayK = db.dayK

all_stocks = [
    {
        'code': '000025', # 特力A
        #'last_sell': 0.00,
        #'last_buy': 0.00,
        #'position': 0,
        'KDJ': { '2015-12-10': [71.55, 71.30, 72.04]},
        'trades': [
            ['2016-2-26', 2, 100, 68.49, '2016-3-25', 79.26],
            ['2016-4-21', 1, 100, 67.50],
        ],
        'comment': '<--',
    },
    {
        'code': '000413', # 东旭光电
        #'last_sell': 7.17,
        #'last_buy': 9.52,
        #'position': 100,
        'KDJ': { '2015-12-10': [20.93, 36.51, -10.25]},
        'trades': [
            ['2015-12-16', 1, 100, 9.52],
            ['2016-1-28', 2, 100, 6.01, '2016-2-16', 7.17],
        ],
        'comment': '石墨烯，蓝宝石',
    },
    {
        'code': '000488', # 晨鸣纸业
        #'last_sell': 7.84,
        #'last_buy': 8.71,
        #'position': 100,
        'KDJ': { '2015-12-10': [22.18, 31.70, 3.14]},
        'trades': [
        #    ['2015-7-13', 1, 100, 8.71]
            ['2016-1-18', 2, 100, 7.10, '2016-2-19', 7.84],
        ],
        'comment': '汇金证金?',
    },
    {
        'code': '000531', # 穗恒运A
        'KDJ': { '2015-12-24': [76.95, 75.53, 79.79]},
        'trades': [
            ['2015-12-29', 1, 100, 11.98],
            ['2016-1-12', 1, 100, 9.75],
        ],
        'comment': '弋弋推荐',
    },
    {
        'code': '000630', # 铜陵有色
        #'last_sell': 0.00,
        #'last_buy': 3.92,
        #'position': 400,
        'KDJ': { '2015-12-10': [25.10, 29.78, 15.72]},
        'trades': [
            ['2015-10-27', 1, 200, 4.47],
            ['2015-10-30', 1, 200, 3.92],
            ['2016-1-8', 1, 500, 3.22],
            ['2016-1-21', 1, 500, 2.94],
        ],
    },
    {
        'code': '000671', # 阳光城
        #'last_sell': 8.13,
        #'last_buy': 6.67,
        #'position': 0,
        'KDJ': { '2015-12-10': [75.36, 70.99, 84.09]},
        'trades': [
            ['2016-4-1', 1, 500, 6.13],
        ],
        'comment': '二线房地产',
    },
    {
        'code': '000725', # 京东方A
        #'last_sell': 2.64,
        'KDJ': { '2015-12-25': [57.16, 59.79, 51.90]},
        'trades': [
            ['2015-12-28', 1, 500, 3.04],
            ['2016-1-15', 1, 1000, 2.63],
            ['2016-1-27', 2, 1000, 2.33, '2016-2-17', 2.64],
            ['2016-4-19', 1, 1000, 2.53],
        ],
        'comment': '低价股，计算机',
    },
    {
        'code': '000750', # 国海证券
        'KDJ': { '2015-12-24': [64.76, 69.71, 54.88]},
        'trades': [
            ['2015-12-28', 1, 100, 12.96],
            ['2016-1-12', 2, 100, 10.14, '2016-3-29', 10.79],
        ],
    },
    {
        'code': '000898', # 鞍钢股份
        #'last_sell': 3.97,
        #'last_buy': 4.83,
        #'position': 500,
        'KDJ': { '2015-12-10': [25.88, 32.89, 11.87]},
        'trades': [
            ['2015-7-22', 1, 200, 6.21],
            ['2015-9-16', 1, 100, 4.98],
            ['2015-10-8', 1, 200, 4.83],
            ['2016-1-21', 1, 300, 4.62],
            ['2016-2-1', 2, 500, 3.73, '2016-2-18', 3.97],
        ],
    },
    {
        'code': '000900', # 现代投资
        #'last_sell': 0,
        #'last_buy': 8.57,
        #'position': 100,
        'KDJ': { '2015-12-10': [40.92, 43.19, 36.40]},
        'trades': [
            ['2015-11-9', 1, 100, 8.68],
            ['2016-1-22', 2, 200, 6.80, '2016-4-19', 7.25],
        ],
        'comment': '滞涨股',
    },
    {
        'code': '002008', # 大族激光
        #'last_sell': 22.55,
        #'last_buy': 27.14,
        #'position': 100,
        'KDJ': { '2015-12-10': [69.32, 59.40, 89.15]},
        'trades': [
            ['2015-8-12', 2, 100, 27.14, '2016-1-5', 22.55],
            ['2016-1-8', 1, 100, 21.79],
            ['2016-1-29', 2, 100, 19.93, '2016-2-23', 22.25],
            ['2016-2-25', 2, 100, 20.03, '2016-4-20', 23.11],
            ['2016-2-25', 2, 100, 20.03, '2016-4-1', 22.19],
        ],
        'comment': '一堆概念',
    },
    {
        'code': '002106', # 莱宝高科
        'last_sell': 11.25,
        'last_sell_date': '2016-1-5',
        #'last_buy': 13.61,
        #'position': 400,
        'KDJ': { '2015-12-10': [26.00, 26.37, 25.27]},
        'trades': [
        #    ['2015-4-2', 1, 100, 16.43],
        #    ['2015-11-23', 1, 100, 14.79],
        #    ['2015-12-7', 1, 200, 13.61],
            ['2016-1-18', 1, 100, 8.83],
        ],
        'comment': '苹果三星<--',
    },
    {
        'code': '002164', # 宁波东力
        'last_sell': 7.63,
        #'last_buy': 9.99,
        #'position': 200,
        'KDJ': { '2015-12-10': [59.28, 66.63, 44.57]},
        'trades': [
            ['2015-8-17', 1, 100, 11.89],
            ['2015-8-19', 1, 100, 9.99],
        ],
        'comment': '风能',
    },
    {
        'code': '002271', # 东方雨虹
        #'last_sell': 16.91,
        #'last_buy': 20.76,
        #'position': 100,
        'KDJ': { '2015-12-10': [63.21, 68.86, 51.93]},
        'trades': [
            ['2015-12-17', 2, 100, 20.76, '2016-1-5', 16.91],
        ],
        'comment': '防雨',
    },
    {
        'code': '002273', # 水晶光电
        #'last_sell': 0.00,
        #'last_buy': 0.00,
        #'position': 0,
        'KDJ': { '2015-12-10': [49.07, 49.94, 47.32]},
        'comment': 'VR',
        'trades': [
            ['2016-4-21', 1, 100, 32.00],
        ],
    },
    {
        'code': '002290', # 禾盛新材
        #'last_sell': 30.18,
        #'last_buy': 28.58,
        #'position': 0,
        'KDJ': { '2015-12-10': [19.68, 31.71, -4.38]},
        'trades': [
            ['2015-12-30', 1, 100, 33.43],
            ['2016-1-6', 1, 100, 27.56],
            ['2016-1-11', 1, 100, 23.35],
            ['2016-3-11', 2, 100, 19.04, '2016-3-25', 22.96],
            ['2016-3-11', 2, 100, 19.04, '2016-3-21', 23.36],
            ['2016-4-22', 1, 100, 20.91],
        ],
        'comment': '电器，新材料',
    },
    {
        'code': '002450', # 康得新
        #'last_sell': 34.00,
        #'last_buy': 40.49,
        #'position': 200,
        'KDJ': { '2015-12-17': [77.24, 75.20, 81.30]},
        'trades': [
            ['2015-5-26', 1, 100, 45.39],
        #    ['2015-6-10', 1, 100, 40.49],
            ['2016-3-8', 2, 100, 30.26, '2016-3-21', 32.69],
        ],
        'comment': '一堆概念',
    },
    {
        'code': '002454', # 松芝股份
        #'last_sell': 17.86,
        #'last_buy': 16.95,
        #'position': 100,
        'KDJ': { '2015-12-10': [33.77, 31.61, 38.10]},
        'trades': [
            #['2015-12-9', 1, 100, 16.95],
            ['2016-1-18', 2, 100, 12.66, '2016-3-3', 14.84],
        ],
        'comment': '冷链',
    },
    {
        'code': '002567', # 唐人神
        #'last_sell': 0.00,
        #'last_buy': 10.50,
        #'position': 100,
        'KDJ': { '2015-12-10': [82.56, 76.34, 95.01]},
        'trades': [
            ['2015-11-2', 2, 100, 10.5, '2016-4-12', 13.23],
            ['2016-2-25', 2, 100, 11.56, '2016-4-8', 13.25],
            ['2016-3-11', 2, 100, 9.02, '2016-3-28', 12.16],
            ['2016-3-11', 2, 200, 9.02, '2016-3-23', 11.58],
        ],
        'comment': '猪肉',
    },
    {
        'code': '002570', # 贝因美
        'last_sell': 14.92,
        #'last_buy': 13.90,
        #'position': 200,
        'KDJ': { '2015-12-10': [37.43, 35.53, 41.24]},
        'trades': [
            ['2015-11-23', 1, 100, 16.1],
            #['2015-12-1', 1, 100, 13.9],
            ['2016-1-5', 1, 100, 13.04],
        ],
        'comment': 'XXX二胎',
    },
    {
        'code': '002594', # 比亚迪
        #'last_sell': 0,
        #'last_buy': 63.17,
        #'position': 100,
        'KDJ': { '2015-12-10': [58.51, 48.29, 78.95]},
        'trades': [
            ['2015-12-9', 1, 100, 63.17],
            ['2016-1-26', 2, 100, 52.28, '2016-3-18', 56.44],
        ],
        'comment': '新能源汽车',
    },
    {
        'code': '300001', # 特锐德
        #'last_sell': 30.70,
        #'last_buy': 26.00,
        #'position': 0,
        'KDJ': { '2015-12-10': [48.60, 46.60, 52.59]},
        'trades': [
            ['2016-1-8', 2, 100, 23.60, '2016-3-31', 24.84],
        ],
        'comment': '创业板，充电桩',
    },
    {
        'code': '300003', # 乐普医疗
        'KDJ': { '2015-12-25': [61.57, 68.32, 48.06]},
        'comment': '医疗器械',
    },
    {
        'code': '300027', # 华谊兄弟
        'KDJ': { '2016-3-15': [51.5, 43.3, 67.8]},
        'trades': [
            ['2016-3-15', 2, 100, 24.45, '2016-3-21', 27.04],
        ],
        'comment': '深港通',
    },
    {
        'code': '300161', # 华中数控
        #'last_sell': 25.68,
        #'last_buy': 0,
        #'position': 0,
        'KDJ': { '2015-12-10': [18.39, 23.28, 8.60]},
        'trades': [
            ['2016-1-14', 2, 100, 24.54, '2016-1-20', 25.68],
            ['2016-1-26', 2, 100, 22.23, '2016-4-8', 23.54],
            ['2016-3-7', 2, 100, 17.50, '2016-3-10', 19.19],
        ],
        'comment': '机器人',
    },
    {
        'code': '300185', # 通裕重工
        'KDJ': { '2015-12-25': [67.55, 66.49, 69.68]},
        'trades': [
            ['2016-2-26', 2, 300, 6.44, '2016-3-21', 6.98],
        ],
        'comment': '无人机',
    },
    {
        'code': '300431', # 暴风科技
        'last_sell': 0.00,
        'last_buy': 0.00,
        'position': 0,
        'KDJ': { '2015-12-10': [86.67, 87.67, 84.68]},
    },
    {
        'code': '510150', # 消费ETF
        'last_sell': 0,
        'KDJ': { '2016-1-19': [25.8, 26.5, 24.4]},
        'trades': [
            ['2016-1-20', 1, 500, 3.498],
        ],
        'comment': 'XXX',
    },
    {
        'code': '510210', # 综指ETF
        'last_sell': 0,
        'KDJ': { '2016-1-20': [18.2, 17.9, 19.0]},
        'trades': [
            ['2016-1-21', 1, 500, 3.27],
        ],
        'comment': 'XXX',
    },
    {
        'code': '600008', # 首创股份
        #'last_sell': 11.12,
        #'last_buy': 11.56,
        #'position': 200,
        'KDJ': { '2015-12-10': [16.35, 25.89, -2.73]},
        'trades': [
            ['2015-8-18', 1, 100, 12.91],
            ['2015-8-18', 1, 100, 11.56],
            ['2016-1-21', 2, 100, 7.94, '2016-3-31', 8.46],
        ],
        'comment': '污水处理，节能环保',
    },
    {
        'code': '600027', # 华电国际
        #'last_sell': 5.17,
        'KDJ': { '2015-1-24': [11.7, 11.9, 11.4]},
        'trades': [
            ['2016-1-25', 1, 1000, 5.51],
            ['2016-1-27', 2, 1000, 4.88, '2016-2-19', 5.17],
        ],
        'comment': '弋弋推荐',
    },
    {
        'code': '600029', # 南方航空
        'last_sell': 8.83,
        #'last_buy': 7.89,
        #'position': 200,
        'KDJ': { '2015-12-10': [41.63, 42.18, 40.52]},
        'trades': [
            ['2015-8-21', 1, 100, 9.77],
            #['2015-12-1', 1, 100, 7.89],
            ['2016-1-26', 1, 200, 7.35],
            ['2016-4-13', 1, 300, 6.38],
        ],
        'comment': '',
    },
    {
        'code': '600522', # 中天科技
        'last_sell': 24.46,
        #'last_buy': 21.97,
        #'last_buy_date': '2015-12-9',
        #'position': 200,
        'KDJ': { '2015-12-10': [20.84, 34.59, -6.65]},
        'trades': [
            ['2015-8-12', 1, 100, 26.1],
            #['2015-12-9', 1, 100, 21.97],
            ['2016-1-12', 1, 100, 18.14],
        ],
        'comment': '军工锂电石墨烯',
    },
    {
        'code': '600886', # 国投电力
        'KDJ': { '2015-12-25': [51.51, 51.55, 51.43]},
        'trades': [
            ['2016-1-8', 1, 100, 7.69],
            ['2016-1-29', 2, 100, 6.12, '2016-2-24', 6.67],
        ],
    },
    {
        'code': '601288', # 农业银行
        #'last_sell': 3.10,
        #'last_buy': 3.30,
        #'position': 7000,
        'KDJ': { '2015-12-10': [48.01, 51.12, 41.78]},
        'trades': [
            ['2015-4-20', 1, 1000, 4.045],
            ['2015-4-28', 1, 1000, 4.04],
            ['2015-5-5', 1, 1000, 3.94],
            ['2015-7-13', 1, 1000, 3.76],
        #    ['2015-7-27', 1, 1000, 3.56],
        #    ['2015-8-17', 1, 1000, 3.41],
        #    ['2015-8-19', 1, 1000, 3.301],
            ['2016-1-27', 2, 1000, 2.96, '2016-3-4', 3.16],
        ],
    },
    {
        'code': '601766', # 中国中车
        #'last_sell': 11.30,
        #'last_sell_date': '2016-1-5',
        #'last_buy': 13.11,
        #'position': 400,
        'KDJ': { '2016-2-16': [54.03, 38.08, 85.93]},
        'trades': [
        #    ['2015-7-20', 1, 100, 18.1],
        #    ['2015-8-6', 1, 200, 15.48],
        #    ['2015-12-9', 1, 100, 13.11],
            ['2016-2-29', 2, 200, 9.25, '2016-3-7', 10.14],
        ],
    },
    {
        'code': '601857', # 中国石油
        #'last_sell': 0.00,
        #'last_buy': 9.02,
        #'position': 100,
        'KDJ': { '2015-12-10': [16.48, 25.66, -1.89]},
        'trades': [
            ['2015-11-26', 1, 100, 9.02],
            ['2016-2-15', 2, 700, 7.17, '2016-3-4', 7.76],
        ],
    },
    {
        'code': '601919', # 中国远洋
        #'last_sell': 10.48,
        #'last_buy': 9.41,
        #'position': 0,
        'KDJ': { '2016-4-20': [46.8, 50.8, 38.6]},
        'trades': [
            ['2016-4-21', 1, 300, 6.04],
        ],
    },
    {
        'code': '601985', # 中国核电
        'last_sell': 10.48,
        #'last_buy': 9.41,
        #'position': 0,
        'KDJ': { '2015-12-10': [38.60, 37.05, 41.68]},
        'trades': [
            ['2016-1-18', 1, 100, 7.90],
        ],
    },
    {
        'code': '601989', # 中国重工
        'last_sell': 0,
        #'last_buy': 11.08,
        #'position': 200,
        'KDJ': { '2015-12-10': [16.24, 22.97, 2.79]},
        'trades': [
            ['2015-8-20', 1, 100, 14.11],
            ['2015-9-10', 1, 100, 11.08],
            ['2016-1-18', 1, 100, 7.84],
        ],
        'comment': '军工,航母',
    },
]

#all_stocks = all_stocks[0:1]
#all_stocks = all_stocks[22:23]

sh_index = {
    'code': 'sh',
    'KDJ': { '2015-12-16': [56.44, 51.07, 67.18]},
    'price': 0,
}

precious_metals = [
    {
        'code': 1,
        'name': '白银',
        'trades': [
            ['2015-12-14', 1, 3000, 2.87],
        ],
    }
]

whitelist_codes = ['601288', '000725'] # 农业银行
halt_codes = [] # real-time retrieve
vip_codes = ['002008', '002290', '002450'] # 大禾康

positioned_stock_count = 0

investments = {
    'totalBase': 100000,
    'total': 0,
    'totalExceptWhitelist': 0,
    'totalExceptWhitelistAndHalt': 0,
    'totalVip': 0,
    'indexed_cost': [],
    'fine_indexed_cost': [],
    'indexedTotal': 0,
}

def preprocess_all():
    global positioned_stock_count
    investments['total'] = 0
    investments['totalExceptWhitelist'] = 0
    investments['totalExceptWhitelistAndHalt'] = 0
    investments['totalVip'] = 0
    investments['indexed_cost'] = [0, 0, 0, 0, 0, 0, 0, 0]
    investments['fine_indexed_cost'] = [0, 0, 0, 0, 0, 0, 0, 0]
    investments['indexedTotal'] = 0
    positioned_stock_count = 0
    for stock in all_stocks:
        preprocess_stock(stock)

def preprocess_stock(stock):
    global positioned_stock_count
    last_buy = 0.0
    last_buy_date = date.min
    far_buy_date = date.max
    last_sell = 0.0
    last_sell_date = date.min
    position = 0
    if stock.has_key('trades'):
        for trade in stock['trades']:
            theDate = datetime.strptime(trade[0], '%Y-%m-%d').date()
            direction = trade[1]
            amount = trade[2]
            price = trade[3]
            if direction == 2 or len(trade) > 4:
                theSellDate = datetime.strptime(trade[4], '%Y-%m-%d').date()
                sellPrice = trade[5]
                # correct direction in case it has wrong value
                if direction != 2:
                    print 'wrong direction in stock ' + stock['code']
                    direction = 2
                if theSellDate >= last_sell_date:
                    last_sell_date = theSellDate
                    last_sell = sellPrice
            if direction == 1 and theDate >= last_buy_date:
                last_buy_date = theDate
                last_buy = price
            if direction == 1 and theDate < far_buy_date:
                far_buy_date = theDate
            if direction == 1:
                position += direction * amount
                investments['total'] += direction * amount * price
                if stock['code'] not in whitelist_codes:
                    investments['totalExceptWhitelist'] += direction * amount * price
                if (stock['code'] not in whitelist_codes) and (stock['code'] not in halt_codes):
                    investments['totalExceptWhitelistAndHalt'] += direction * amount * price
                if stock['code'] in vip_codes:
                    investments['totalVip'] += direction * amount * price
                # sh index at trade date
                dh = previous_data_with_date(sh_index['code'], trade[0])
                shIndex = (dh['high'] + dh['low']) / 2
                investments['indexedTotal'] += shIndex * amount * price
                costIndex = int(math.floor((5000 - shIndex) / 500) + 1)
                costIndex = 0 if (costIndex < 0) else costIndex
                costIndex = 7 if (costIndex > 7) else costIndex
                investments['indexed_cost'][costIndex] += amount * price
                if sh_index['price'] > 0:
                    costIndex = (int(sh_index['price']) / 100) - (int(shIndex) / 100) + 3
                    if costIndex >= 0 and costIndex <= 7:
                        investments['fine_indexed_cost'][costIndex] += amount * price
    if not stock.has_key('last_buy_date') and last_buy_date != date.min:
        stock['last_buy_date'] = last_buy_date.strftime('%Y-%m-%d')
    if not stock.has_key('far_buy_date') and far_buy_date != date.max:
        stock['far_buy_date'] = far_buy_date.strftime('%Y-%m-%d')
    if not stock.has_key('last_buy'):
        stock['last_buy'] = last_buy
    if not stock.has_key('last_sell_date') and last_sell_date != date.min:
        stock['last_sell_date'] = last_sell_date.strftime('%Y-%m-%d')
    if not stock.has_key('last_sell'):
        stock['last_sell'] = last_sell
    if not stock.has_key('position'):
        stock['position'] = position
    if stock['position'] > 0:
        positioned_stock_count += 1

def get_hold_duration(stock):
    far = 0
    last = 0
    if stock.has_key('far_buy_date'):
        theDate = datetime.strptime(stock['far_buy_date'], '%Y-%m-%d').date()
        delta = date.today() - theDate
        far = math.floor(delta.days / 30)
    if stock.has_key('last_buy_date'):
        theDate = datetime.strptime(stock['last_buy_date'], '%Y-%m-%d').date()
        delta = date.today() - theDate
        last = math.floor(delta.days / 30)
    return (last, far)

def compCurrentJ(stockX, stockY):
    if stockX['more_info_currentJ'] < stockY['more_info_currentJ']:
        return 1
    elif stockX['more_info_currentJ'] > stockY['more_info_currentJ']:
        return -1
    else:
        return 0

stock_index = 0
stock2line = {}

def advice_all():
    global positioned_stock_count
    theTime = datetime.now()

    # line 1
    log_status('Getting sh index')
    df = ts.get_realtime_quotes(sh_index['code'])
    log_status('Done sh index')
    sh_index['price'] = float(df['price'][0])
    (k, d, j) = get_today_KDJ933(sh_index, float(df['price'][0]), float(df['high'][0]), float(df['low'][0]))
    now = 'Time: %s  上证: %7.2f  涨跌: %6.2f%% J:%6.2f  关注: %2d 持仓: %2d 停牌: %2d' \
        % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), \
        float(df['price'][0]), \
        (float(df['price'][0]) - float(df['pre_close'][0])) / float(df['pre_close'][0]) * 100, j, \
        len(all_stocks), positioned_stock_count, len(halt_codes))
    sh_index['price'] = float(df['price'][0])
    display_info(now, 1, 1)
    #workaround to color index J
    indexJ = '%6.2f' % j
    indexJ_color = 1
    if j <= 20:
        indexJ_color = 2
    elif j >= 80:
        indexJ_color = 3
    display_info(indexJ, 59, 1, indexJ_color)
    #stockCountInfo = 'Stocks: %d' % (len(all_stocks))
    #display_info(stockCountInfo, 80, 1)
    
    # line 2
    indexed_coststr = '[>5000:%6.2f%%|>4500:%6.2f%%|>4000:%6.2f%%|>3500:%6.2f%%|>3000:%6.2f%%|>2500:%6.2f%%|>2000:%6.2f%%|>1500:%6.2f%%] - %7.2f' \
        % (investments['indexed_cost'][0]/investments['total'] * 100, \
        investments['indexed_cost'][1]/investments['total'] * 100, \
        investments['indexed_cost'][2]/investments['total'] * 100, \
        investments['indexed_cost'][3]/investments['total'] * 100, \
        investments['indexed_cost'][4]/investments['total'] * 100, \
        investments['indexed_cost'][5]/investments['total'] * 100, \
        investments['indexed_cost'][6]/investments['total'] * 100, \
        investments['indexed_cost'][7]/investments['total'] * 100, investments['indexedTotal'] / investments['total'])
    display_info(indexed_coststr, 1, 2)

    # line 3
    current_invest_base = (1 - (float(df['price'][0]) / 500 - 2)*0.1) * investments['totalBase']
    invest_status = '仓/允: %6.0f/%6.0f, 除农: %6.0f, 除农比: %6.2f%%, 除停: %6.0f, 除停比: %6.2f%%, 大禾康占比: %6.2f%%' \
        % (investments['total'], current_invest_base, investments['totalExceptWhitelist'], \
        (investments['totalExceptWhitelist'] - (current_invest_base - investments['totalBase'] * 0.1)) / (investments['totalBase'] * 0.2) * 100, \
        investments['totalExceptWhitelistAndHalt'], \
        (investments['totalExceptWhitelistAndHalt'] - (current_invest_base - investments['totalBase'] * 0.1)) / (investments['totalBase'] * 0.2) * 100, \
        investments['totalVip'] / investments['total'] * 100)
    display_info(invest_status, 1, 3)
    
    # line 4
    baseIndex = int(sh_index['price']) / 100 * 100
    indexed_coststr = '[>%4d:%6.2f%%|>%4d:%6.2f%%|>%4d:%6.2f%%|>%4d:%6.2f%%|>%4d:%6.2f%%|>%4d:%6.2f%%|>%4d:%6.2f%%|>%4d:%6.2f%%]' \
        % (baseIndex + 300, investments['fine_indexed_cost'][0]/investments['total'] * 100, \
        baseIndex + 200, investments['fine_indexed_cost'][1]/investments['total'] * 100, \
        baseIndex + 100, investments['fine_indexed_cost'][2]/investments['total'] * 100, \
        baseIndex, investments['fine_indexed_cost'][3]/investments['total'] * 100, \
        baseIndex - 100, investments['fine_indexed_cost'][4]/investments['total'] * 100, \
        baseIndex - 200, investments['fine_indexed_cost'][5]/investments['total'] * 100, \
        baseIndex - 300, investments['fine_indexed_cost'][6]/investments['total'] * 100, \
        baseIndex - 400, investments['fine_indexed_cost'][7]/investments['total'] * 100)
    display_info(indexed_coststr, 1, 4)
    
    line = 5
    new_stocks = today_new_stocks()
    if len(new_stocks) > 0:
        line += 1
        display_info('今新: ' + ' '.join(new_stocks), 1, 4)

    for stock in all_stocks:
        advise(stock)

    all_stocks.sort(compCurrentJ)
    global stock_index
    stock_index = 0
    line = display_stock_group(all_stocks, "卖出", line)
    line = display_empty_line(line)
    line = display_stock_group(all_stocks, "买入", line)
    line = display_empty_line(line)
    line = display_stock_group(all_stocks, "弱买", line)
    line = display_stock_group(all_stocks, "追高", line)
    line = display_empty_line(line)
    line = display_stock_group(all_stocks, "忖卖", line)
    line = display_stock_group(all_stocks, "弱卖", line)
    line = display_stock_group(all_stocks, "薄卖", line)
    line = display_stock_group(all_stocks, "亏卖", line)
    line = display_empty_line(line)
    line = display_stock_group(all_stocks, "持有", line)
    line = display_empty_line(line)
    line = display_stock_group(all_stocks, "观望", line)
    line = display_stock_group(all_stocks, " -- ", line)
    #line = display_stock_group(all_stocks, "    ", line)

    line = display_empty_line(line)
    line = display_empty_line(line)
    line = display_empty_line(line)

    elapsed = datetime.now() - theTime
    display_info(' ' + str(elapsed), 0, line + 1)

def advise(stock):
    log_status('Getting realtime quotes for %s' % (stock['code']))
    df = ts.get_realtime_quotes(stock['code'])
    log_status('Done realtime quotes for %s' % (stock['code']))
    dh = previous_data(stock['code'])
    
    # name
    stock['name'] = df['name'][0]
    namelen = width(stock['name'])
    if namelen < 8:
        for i in range(8 - namelen):
            stock['name'] += ' ' # '_'
    #print len(stock['name'])
    #print namelen

    action = ''
    action_color = 1
    
    code = stock['code']
    current_price = float(df['price'][0])
    today_high = float(df['high'][0])
    today_open = float(df['open'][0])
    position = stock['position']
    last_sell = stock['last_sell']
    last_buy = stock['last_buy']
    previous_close = float(dh['close'])
    previous_open = float(dh['open'])
    
    (k, d, j) = get_today_KDJ933(stock, current_price, float(df['high'][0]), float(df['low'][0]))
    if today_open == 0:
        action = "    "
    elif float(df['price'][0]) - float(df['open'][0]) > 0:
        if float(dh['close']) - float(dh['open']) < 0:
            strong_buy = whether_strong_buy(current_price, last_sell, last_buy)
            strong_buy = False if (j > 80) else strong_buy
            if strong_buy:
                action = "买入"
                action_color = 2
            else:
                action = "弱买"
                action_color = 4
        else:
            if stock['position'] == 0:
                action = "追高"
                action_color = 4
            else:
                action = "持有"
    elif float(df['price'][0]) - float(df['open'][0]) < 0:
        if previous_close - previous_open < 0 or position == 0:
            action = "观望"
        elif current_price < last_buy:
            action = "亏卖"
            action_color = 5
        elif current_price > last_buy + 1.00 and current_price < last_buy * 1.1:
            strong_sell = whether_strong_sell(stock, current_price, last_sell, last_buy, today_high)
            if strong_sell:
                action = "卖出"
                action_color = 3
            else:
                action = "弱卖"
                action_color = 5
        elif current_price < last_buy + 1.00 or current_price < last_buy * 1.1:
            action = "薄卖"
            action_color = 5
        else:
            strong_sell = whether_strong_sell(stock, current_price, last_sell, last_buy, today_high)
            if strong_sell:
                action = "卖出"
                action_color = 3
            else:
                action = "忖卖"
                action_color = 5
    elif current_price == 0:
        action = "    "
    else:
        action = " -- "
    stock['action'] = action
    stock['action_color'] = action_color
 
    profit_percent = 0
    if last_buy > 0 and position > 0:
        profit_percent = math.floor((current_price - last_buy) / last_buy * 100)
    if profit_percent <= 0:
        profit_percent = 0
 
    if profit_percent == 0:
        profit_percentstr = '    '
    else:
        profit_percentstr = '%3d%%' % profit_percent
    
    regress_rate = 0
    if profit_percent == 0:
        regress_ratestr = '   '
    else:
        recent_high = get_recent_high(stock, float(df['high'][0]))
        regress_rate = math.ceil((recent_high - current_price) / (recent_high - last_buy) * 100)
        #if code == '000531':
        #    print str(recent_high) + ' ' + str(current_price) + ' ' + str(last_buy)
        regress_ratestr = '%2d%%' % regress_rate
    
    if (current_price == 0 or today_open == 0)and (code not in halt_codes):
        halt_codes.append(code)
        preprocess_all()

    (last, far) = get_hold_duration(stock)
    durationstr = '     '
    if position > 0:
        durationstr = '%2d/%2d' %(last, far)

    stackstr = '     '
    if stock.has_key('trades'):
        for trade in stock['trades']:
            direction = trade[1]
            if direction == 1:
                stackstr = stackstr.replace(' ', '|', 1)

    index_profit_percent = 0
    buy_index = 0
    if position > 0:
        index_dh = previous_data_with_date(sh_index['code'], stock['last_buy_date'])
        buy_index = (index_dh['high'] + index_dh['low']) / 2
        index_profit_percent = (sh_index['price'] - buy_index) / buy_index
    index_profit_percentstr = '       '
    if index_profit_percent != 0:
        index_profit_percentstr = '%6.2f%%' % (index_profit_percent * 100)

    index_cost_percent = 0
    if stock.has_key('last_sell_date'):
        index_dh = previous_data_with_date(sh_index['code'], stock['last_sell_date'])
        sell_index = (index_dh['high'] + index_dh['low']) / 2
        # 处理累进买入的情况
        if buy_index != 0 and sell_index > buy_index and stock['last_sell_date'] != stock['last_buy_date']:
            sell_index = buy_index
        index_cost_percent = (sh_index['price'] - sell_index) / sell_index
    index_cost_percentstr = '       '
    if index_cost_percent < 0:
        index_cost_percentstr = '%6.2f%%' % (index_cost_percent * 100)

    #printstr = '(昨:%6.2f,今:%6.2f,现价:%6.2f,上次买:%6.2f卖:%6.2f,仓:%4d,盈:%s,回:%s,J:%6.2f,期:%s,栈:%s,点:%s)' \
    #    % (float(dh['close']) - float(dh['open']), \
    #    float(df['price'][0]) - float(df['open'][0]), \
    #    float(df['price'][0]), stock['last_buy'], \
    #    stock['last_sell'], position, profit_percentstr, regress_ratestr, j, \
    #    durationstr, stackstr, index_profit_percentstr)
    #stock['more_info'] = printstr
    stock['more_info_previousChange'] = float(dh['close']) - float(dh['open'])
    stock['more_info_todayChange'] = float(df['price'][0]) - float(df['open'][0])
    stock['more_info_currentPrice'] = float(df['price'][0])
    stock['more_info_lastBuy'] = stock['last_buy']
    stock['more_info_lastSell'] = stock['last_sell']
    stock['more_info_position'] = position
    stock['more_info_profit_percent'] = profit_percent
    stock['more_info_profit_percentstr'] = profit_percentstr
    stock['more_info_regress_rate'] = regress_rate
    stock['more_info_regress_ratestr'] = regress_ratestr
    stock['more_info_currentJ'] = j
    stock['more_info_duration'] = far
    stock['more_info_durationstr'] = durationstr
    stock['more_info_stackstr'] = stackstr
    stock['more_info_index_profit_percent'] = index_profit_percent
    stock['more_info_index_profit_percentstr'] = index_profit_percentstr
    stock['more_info_index_cost_percent'] = index_cost_percent
    stock['more_info_index_cost_percentstr'] = index_cost_percentstr

def whether_strong_buy(current_price, last_sell, last_buy):
    strong_buy = (last_buy == 0.0 and last_sell == 0.0) # 空仓且从未持有
    if (last_sell != 0.0 and last_buy == 0.0):
        strong_buy = current_price < last_sell - 0.5
    if (last_sell == 0.0 and last_buy != 0.0):
        next_buy = last_buy - (math.ceil(last_buy * 2 / 10) / 2)
        strong_buy = (strong_buy or current_price <= next_buy)
    if last_sell != 0.0:
        next_buy = last_sell - (math.ceil(last_sell * 2 / 10) / 2)
        strong_buy = (strong_buy or current_price <= next_buy)
        if strong_buy:
            next_buy = last_buy - (math.ceil(last_buy * 2 / 10) / 2)
            strong_buy = (strong_buy and current_price <= next_buy)
    return strong_buy

def whether_strong_sell(stock, current_price, last_sell, last_buy, today_high):
    recent_high = get_recent_high(stock, today_high)
    strong_sell = recent_high > last_buy * 1.2 and (recent_high - current_price) > (recent_high - last_buy) * 0.2
    return strong_sell

def get_recent_high(stock, today_high):
    recent_high = 0
    if stock.has_key('last_buy_date'):
        recent_high = get_recent_high_from_date(stock['code'], stock['last_buy_date'])
        if recent_high == 0:
            recent_high = today_high
    else:
        # go with high in last 14 days
        theDate = date.today() - timedelta(days=14)
        recent_high = get_recent_high_from_date(stock['code'], theDate)
    
    if recent_high < today_high:
        recent_high = today_high

    return recent_high

def get_recent_high_from_date(code, datestr):
    theDate = datetime.strptime(datestr, '%Y-%m-%d').date()
    recent_high = 0
    while theDate < date.today():
        dh = previous_data_with_date(code, datestr)
        if dh is not None and dh['high'] > recent_high:
            recent_high = dh['high']
        theDate = theDate + timedelta(days=1)
        datestr = theDate.strftime('%Y-%m-%d')
    return recent_high

def display_stock_group(stocks, action, line):
    global stock_index
    for stock in stocks:
        if (stock['action'] == action):
            display_stock(stock, line)
            stock_index += 1
            display_info(str(stock_index), 1, line)
            stock2line[str(stock_index)] = line
            line += 1
        
    return line

def display_stock(stock, line):  
    separator = 1
    index_width = 3
    code_width = 6
    name_width = 8
    action_width = 4
    previousChange_width = 10
    todayChange_width = 9
    currentPrice_width = 11
    lastBuy_width = 13
    lastSell_width = 9
    position_width = 7
    profit_width = 7
    regression_width = 6
    j_width = 8
    duration_width = 8
    stack_width = 8
    indexProfit_width = 10
    indexCost_width = 10

    # code
    location = 1 + index_width
    display_info(stock['code'], location, line, 1)
    
    # name
    location += code_width + separator
    display_info(stock['name'], location, line, 1)

    # action
    location += name_width + separator
    display_info(stock['action'], location, line, stock['action_color'])

    # more_info
    location += action_width + separator
    display_info('(昨:%6.2f' % (stock['more_info_previousChange']), location, line)
    location += previousChange_width + separator
    display_info('今:%6.2f' % (stock['more_info_todayChange']), location, line)
    location += todayChange_width + separator
    display_info('现价:%6.2f' % (stock['more_info_currentPrice']), location, line)
    location += currentPrice_width + separator
    display_info('上次买:%6.2f' % (stock['more_info_lastBuy']), location, line)
    location += lastBuy_width + separator
    display_info('卖:%6.2f' % (stock['more_info_lastSell']), location, line)
    location += lastSell_width + separator
    display_info('仓:%4d' % (stock['more_info_position']), location, line)
    location += position_width + separator
    currentProfit_color = 1
    if stock['more_info_profit_percent'] >= 6:
        currentProfit_color = 3
    display_info('盈:%s' % (stock['more_info_profit_percentstr']), location, line, currentProfit_color)
    location += profit_width + separator
    regress_rate_color = 1
    if stock['more_info_regress_rate'] >= 20:
        regress_rate_color = 3
    display_info('回:%s' % (stock['more_info_regress_ratestr']), location, line, regress_rate_color)
    location += regression_width + separator
    currentJ_color = 1
    if stock['more_info_currentJ'] <= 20:
        currentJ_color = 2
    elif stock['more_info_currentJ'] >= 80:
        currentJ_color = 3
    display_info('J:%6.2f' % (stock['more_info_currentJ']), location, line, currentJ_color)
    location += j_width + separator
    display_info('期:%s' % (stock['more_info_durationstr']), location, line)
    location += duration_width + separator
    display_info('栈:%s' % (stock['more_info_stackstr']), location, line)
    location += stack_width + separator
    index_profit_color = 1
    if stock['more_info_index_profit_percent'] * 100 >= 5:
        index_profit_color = 3
    display_info('点:%s' % (stock['more_info_index_profit_percentstr']), location, line, index_profit_color)
    location += indexProfit_width + separator
    index_cost_color = 1
    if stock['more_info_index_cost_percent'] * 100 <= -5 \
        and stock['more_info_index_profit_percent'] * 100 <= 0 \
        and stock['more_info_currentJ'] <= 20:
        index_cost_color = 2
    display_info('进:%s' % (stock['more_info_index_cost_percentstr']), location, line, index_cost_color)
    location += indexCost_width + separator
    display_info(')', location, line)

    # comment
    location += 1 + separator
    comment = ' ' * 20
    if stock.has_key('comment'):
        comment = stock['comment']
        comment += ' ' * (20 - len(comment))
    display_info(comment, location, line)

def display_highlight_info(index, highlight):
    separator = 1
    index_width = 3
    code_width = 6
    name_width = 8
    action_width = 4
    previousChange_width = 10
    todayChange_width = 9
    currentPrice_width = 11
    lastBuy_width = 13
    lastSell_width = 9
    position_width = 7
    profit_width = 7
    regression_width = 6
    j_width = 8
    duration_width = 8
    stack_width = 8
    indexProfit_width = 10
    indexCost_width = 10

    str = ' '
    color = 1
    if highlight:
        str = '-'
        color = 2

    location = 0
    display_info(str, location, index, color)
    location = index_width
    display_info(str, location, index, color)
    location += code_width + separator
    display_info(str, location, index, color)
    location += name_width + separator
    display_info(str, location, index, color)
    location += action_width + separator
    display_info(str, location, index, color)
    location += previousChange_width + separator
    display_info(str, location, index, color)
    location += todayChange_width + separator
    display_info(str, location, index, color)
    location += currentPrice_width + separator
    display_info(str, location, index, color)
    location += lastBuy_width + separator
    display_info(str, location, index, color)
    location += lastSell_width + separator
    display_info(str, location, index, color)
    location += position_width + separator
    display_info(str, location, index, color)
    location += profit_width + separator
    display_info(str, location, index, color)
    location += regression_width + separator
    display_info(str, location, index, color)
    location += j_width + separator
    display_info(str, location, index, color)
    location += duration_width + separator
    display_info(str, location, index, color)
    location += stack_width + separator
    display_info(str, location, index, color)
    location += indexProfit_width + separator
    display_info(str, location, index, color)
    location += indexCost_width + separator
    display_info(str, location, index, color)

def display_empty_line(line):  
    display_info(' ' * 175, 0, line)
    line += 1
    return line

def get_today_KDJ933(stock, current_price, today_high, today_low):
    if not stock.has_key('KDJ'):
        raise Exception('no KDJ' + stock['code'])
    real = is_tradedate(date.today())
    return compute_KDJ933(stock, date.today(), current_price, today_high, today_low, real)

def compute_KDJ933(stock, theDate, close, high, low, real):
    baseKDJDateStr = stock['KDJ'].keys()[0]
    if datetime.strptime(baseKDJDateStr, '%Y-%m-%d').date() == theDate:
        #print 'hit'
        return (stock['KDJ'][baseKDJDateStr][0], stock['KDJ'][baseKDJDateStr][1], stock['KDJ'][baseKDJDateStr][2])
    (k_1, d_1, j_1) = get_previous_KDJ933(stock, theDate - timedelta(days=1))
    if not real:
        return (k_1, d_1, j_1)
    #print 'compute' + stock['code'] + ' ' + theDate.strftime('%Y-%m-%d') + ' ' + str(k_1) + ' ' + str(d_1) + " " + str(j_1)
    h9 = high
    l9 = low
    count = 1
    while count < 9:
        theDate = theDate - timedelta(days=1)
        datestr = theDate.strftime('%Y-%m-%d')
        dh = previous_data_with_date(stock['code'], datestr)
        if dh['real']:
            count += 1
            if l9 > dh['low']:
                l9 = dh['low']
            if h9 < dh['high']:
                h9 = dh['high']
    rsv = (close - l9) / (h9 - l9) * 100
    #print "rsv " + str(rsv) + " l9 " + " " + str(l9) + " h9 " + str(h9)
    k = rsv / 3 + 2 * k_1 / 3
    d = k / 3 + 2 * d_1 / 3
    j = 3 * k - 2 * d
    return (k, d, j)

def get_previous_KDJ933(stock, theDate):
    theOriginDate = theDate
    datestr = theDate.strftime('%Y-%m-%d')
    dh = previous_data_with_date(stock['code'], datestr)
    if dh is None:
        print "dh is None. Shouldn't happen."
        return (0, 0, 0)
    if dh.has_key('theK') and (not reset_KDJ):
        return (dh['theK'], dh['theD'], dh['theJ'])
    (k, d, j) = compute_KDJ933(stock, theOriginDate, dh['close'], dh['high'], dh['low'], dh['real'])
    c_dayK.update({"code": stock['code'], "date": datestr}, {"$set": {"theK": k, "theD": d, "theJ": j}})
    return (k, d, j)

def previous_data(code):
    d = date.today()
    tdatestr = d.strftime('%Y-%m-%d')
    dh = c.aggregate([{"$match": {"code": {"$eq": code}}}, {"$match": {"date": {"$eq": tdatestr}}}])
    dh = list(dh)
    
    if len(dh) == 0 or (len(dh) != 0 and not dh[0].has_key('high')):
        df = None
        while df is None or df.empty:
            d = d - timedelta(days=1)
            datestr = d.strftime('%Y-%m-%d')
            #print datestr
            log_status('Getting hist data for %s at %s' % (code, datestr))
            df = ts.get_hist_data(code, start=datestr, end=datestr)
            log_status('Done hist data for %s at %s' % (code, datestr))
            #print df
            if df is None or df.empty:
                pdh = c.aggregate([{"$match": {"code": {"$eq": code}}}, {"$match": {"date": {"$eq": datestr}}}])
                pdh = list(pdh)
                if len(pdh) != 0:
                    if len(dh) == 0:
                        c.insert({"code": code, "date": tdatestr, "close": pdh[0]['close'], "open": pdh[0]['open'], "high": pdh[0]['high']})
                    else:
                        c.update({"code": code, "date": tdatestr}, {"$set": {"high": pdh[0]['high']}})
                    dh = c.aggregate([{"$match": {"code": {"$eq": code}}}, {"$match": {"date": {"$eq": tdatestr}}}])
                    dh = list(dh)
                    return dh[0]
        if len(dh) == 0:
            c.insert({"code": code, "date": tdatestr, "close": df['close'][0], "open": df['open'][0], "high": df['high'][0]})
        else:
            c.update({"code": code, "date": tdatestr}, {"$set": {"high": df['high'][0]}})
        dh = c.aggregate([{"$match": {"code": {"$eq": code}}}, {"$match": {"date": {"$eq": tdatestr}}}])
        dh = list(dh)
        #print len(dh)

    return dh[0]

def previous_data_with_date(code, datestr):
    originDateStr = datestr
    dh = c_dayK.aggregate([{"$match": {"code": {"$eq": code}}}, {"$match": {"date": {"$eq": datestr}}}])
    dh = list(dh)
    
    if len(dh) == 0:
        log_status('Getting hist data for %s at %s' % (code, datestr))
        df = ts.get_hist_data(code, start=datestr, end=datestr)
        log_status('Done hist data for %s at %s' % (code, datestr))
        d = datetime.strptime(datestr, '%Y-%m-%d').date()
        if df is None or df.empty:
            d = d - timedelta(days=1)
            datestr = d.strftime('%Y-%m-%d')
            #df = ts.get_hist_data(code, start=datestr, end=datestr)
            dh = previous_data_with_date(code, datestr)
            c_dayK.insert({"code": code, "real": False, "date": originDateStr, "close": dh['close'], "open": dh['open'], "high": dh['high'], "low": dh['low']})
        else:
            c_dayK.insert({"code": code, "real": True, "date": originDateStr, "close": df['close'][0], "open": df['open'][0], "high": df['high'][0], "low": df['low'][0]})
        dh = c_dayK.aggregate([{"$match": {"code": {"$eq": code}}}, {"$match": {"date": {"$eq": originDateStr}}}])
        dh = list(dh)

    return dh[0]

def today_new_stocks():
    dh = db.new_stocks.find()
    dh = list(dh)
    new_stocks = []
    for record in dh:
        # see http://ryan-liu.iteye.com/blog/834831
        if record['ipo_date'] is not None and (datetime.strptime(record['ipo_date'], "%Y-%m-%dT%H:%M:%S.%fz").date() == date.today()):
            new_stocks.append(record['code'])
    return new_stocks

def is_tradedate(date):
    if date.weekday() == 5 or date.weekday() == 6:
        return False # Saturday or Sunday
    datestr = date.strftime('%Y-%m-%d')
    if datestr in legal_holidays:
        return False
    if date.year < 2015 or date.year > 2016:
        raise Exception('year not supported!')
    return True

def update_metal():
    conn = httplib.HTTPConnection("www.icbc.com.cn")
    conn.request("GET", "/ICBCDynamicSite/Charts/GoldTendencyPicture.aspx")
    res = conn.getresponse()
    if res.status == 200:
        theData = res.read()
        #print theData
        dom = soupparser.fromstring(theData)
        # no tbody for first table. index starts from 1
        current_price = dom.xpath("//body/form/table/tr/td/table[6]/tbody/tr/td/div/table/tbody/tr[3]/td[3]")
        if len(current_price) > 0:
            current_price = current_price[0].text.strip()
            last_buy = precious_metals[0]["trades"][-1][3]
            profit_percent = math.floor((float(current_price) - last_buy) / last_buy * 10000) / 100
            if profit_percent > 0:
                profit_percentstr = str(profit_percent) + "%"
            else:
                profit_percentstr = " "
            display_info("银: " + current_price + " 盈: " + profit_percentstr, 100, 1)
    conn.close()

def log_status(message):
    # temp: use space to avoid messy chars.
    display_info('[%s]  %s %s' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), message, ' ' * 30), 1, 0)
  
def display_info(str, x, y, colorpair=1):  
    '''''使用指定的colorpair显示文字'''  
    try:  
        global stdscr  
        stdscr.addstr(y, x, str, curses.color_pair(colorpair))  
        stdscr.refresh()  
    except Exception,e:  
        pass  
  
def get_ch_and_continue():  
    '''''演示press any key to continue'''  
    global stdscr  
    #设置nodelay，为0时会变成阻塞式等待  
    stdscr.nodelay(0)  
    #输入一个字符  
    ch=stdscr.getch()  
    #重置nodelay，使得控制台可以以非阻塞的方式接受控制台输入，超时1秒  
    stdscr.nodelay(1)  
    return True  
  
def set_win():  
    '''''控制台设置'''  
    global stdscr  
    #使用颜色首先需要调用这个方法  
    curses.start_color()  
    #文字和背景色设置，设置了两个color pair，分别为1和2  
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)  
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)  
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)  
    curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK)  
    curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLACK)  
    #关闭屏幕回显  
    curses.noecho()  
    #输入时不需要回车确认  
    curses.cbreak()  
    #设置nodelay，使得控制台可以以非阻塞的方式接受控制台输入，超时1秒  
    stdscr.nodelay(1)  
  
def unset_win():  
    '''''控制台重置'''  
    global stdscr  
    #恢复控制台默认设置（若不恢复，会导致即使程序结束退出了，控制台仍然是没有回显的）  
    curses.nocbreak()  
    curses.echo()  
    #结束窗口  
    curses.endwin()  

def print_KDJ(stock, theDate):
    baseKDJDateStr = stock['KDJ'].keys()[0]
    if datetime.strptime(baseKDJDateStr, '%Y-%m-%d').date() == theDate:
        print baseKDJDateStr + " KDJ %6.2f %6.2f %6.2f" % (stock['KDJ'][baseKDJDateStr][0], stock['KDJ'][baseKDJDateStr][1], stock['KDJ'][baseKDJDateStr][2])
    else:
        (k, d, j) = get_previous_KDJ933(stock, theDate)
        theDateStr = theDate.strftime('%Y-%m-%d')
        print theDateStr + " KDJ %6.2f %6.2f %6.2f" % (k, d, j)
        print_KDJ(stock, theDate - timedelta(days=1))

def print_KDJs(code):
    theDate = date.today()
    for stock in all_stocks:
        if stock['code'] == code:
            print_KDJ(stock, theDate - timedelta(days=1))

g_highlight_stock_index = 0
g_highlight_line = 5

DEBUG = False
  
if __name__=='__main__':  
    #global stdscr
    if DEBUG:
        #try:  
            #set_win()
        #    preprocess_all()
        #    advice_all()
        #finally:
        #    pass
            #unset_win()  
        print_KDJs('601766')
    else:
        stdscr = curses.initscr()
        count = 0
        try:  
            set_win()  
            preprocess_all()
            while True:
                if count % 10 == 0:
                    update_metal()
                
                theTime = datetime.now()
                if count == 0 or \
                    (theTime.hour == 9 and theTime.minute >= 15) or \
                    (theTime.hour == 10) or (theTime.hour == 11 and theTime.minute <= 33) or \
                    (theTime.hour >= 13 and theTime.hour < 15) or \
                    (theTime.hour == 15 and theTime.minute <= 3):
                    advice_all()
                    if count == 0:
                        advice_all()

                count += 1
                seconds = 0
                while seconds < 30:
                    seconds += 1
                    time.sleep(1)
                    ichar = stdscr.getch()
                    if ichar == 27 and stdscr.getch() == ord('['):
                        ichar = stdscr.getch()
                        if ichar == ord('A'):
                            ichar = curses.KEY_UP
                        elif ichar == ord('B'):
                            ichar = curses.KEY_DOWN
                        elif ichar == ord('C'):
                            ichar = curses.KEY_RIGHT
                        elif ichar == ord('D'):
                            ichar = curses.KEY_LEFT
                    stock_count = len(stock2line)
                    if ichar == ord('-') or ichar == curses.KEY_UP or ichar == curses.KEY_LEFT or ichar == ord('w'):
                        display_highlight_info(g_highlight_line, False)
                        g_highlight_stock_index = g_highlight_stock_index - 1
                        if g_highlight_stock_index <= 0: g_highlight_stock_index = stock_count
                        g_highlight_line = stock2line[str(g_highlight_stock_index)]
                        display_highlight_info(g_highlight_line, True)
                    elif ichar == ord('+') or ichar == curses.KEY_DOWN or ichar == curses.KEY_RIGHT or ichar == ord('s'):
                        display_highlight_info(g_highlight_line, False)
                        g_highlight_stock_index = g_highlight_stock_index + 1
                        if g_highlight_stock_index > stock_count: g_highlight_stock_index = 1
                        g_highlight_line = stock2line[str(g_highlight_stock_index)]
                        display_highlight_info(g_highlight_line, True)
                    elif ichar >= ord('0') and ichar <= ord('9'):
                        display_highlight_info(g_highlight_line, False)
                        g_highlight_stock_index = g_highlight_stock_index * 10 + ichar - ord('0')
                        if g_highlight_stock_index >= stock_count:
                            g_highlight_stock_index = ichar - ord('0')
                        if g_highlight_stock_index >= stock_count:
                            g_highlight_stock_index = 1
                        if g_highlight_stock_index <= 0: g_highlight_stock_index = stock_count
                        g_highlight_line = stock2line[str(g_highlight_stock_index)]
                        display_highlight_info(g_highlight_line, True)

                #time.sleep(60)
        #except Exception,e:  
        #    unset_win()  
        #    raise e  
        finally:  
            unset_win()
            pass

