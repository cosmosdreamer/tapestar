# -*- coding: utf-8 -*-

import tushare as ts

def get_fund_current(code, log):
    log('Getting realtime quotes for %s' % (code))
    df = ts.get_realtime_quotes(code)
    log('Done realtime quotes for %s' % (code))
    return float(df['price'][0])

def get_fund_advice(item, current):
    percent = (current - item['low']) / (item['high'] - item['low'])
    advice = ''
    if percent <= 0.3:
        advice = '买入'
    #elif percent <= 0.4:
    #    advice = '反向卖出'
    #elif percent >= 0.6:
    #    advice = '卖出'
    elif percent >= 0.7:
        advice = '卖出'
    if advice != '':
        advice += ' (%2.0f%%)' % (percent * 100)
    return advice

all_etf = [
    {
        'code': '159901',
        'name': '深100ETF',
        'high': 6.35,
        'low': 0.479,
        'current': get_fund_current,
        'advice': get_fund_advice,
        'trades': [
        ],
    },
    {
        'code': '159902',
        'name': '中 小 板',
        'high': 5.61,
        'low': 0.938,
        'current': get_fund_current,
        'advice': get_fund_advice,
        'trades': [
        ],
    },
    {
        'code': '159915',
        'name': '  创业板',
        'high': 3.85,
        'low': 0.59,
        'current': get_fund_current,
        'advice': get_fund_advice,
        'trades': [
        ],
    },
    {
        'code': '159919',
        'name': '  300ETF',
        'high': 5.574,
        'low': 0.811,
        'current': get_fund_current,
        'advice': get_fund_advice,
        'trades': [
        ],
    },
    {
        'code': '159920',
        'name': ' 恒生ETF',
        'high': 1.725,
        'low': 0.884,
        'current': get_fund_current,
        'advice': get_fund_advice,
        'trades': [
        ],
    },
    {
        'code': '159949',
        'name': '创业板50',
        'high': 1.0,
        'low': 0.6,
        'current': get_fund_current,
        'advice': get_fund_advice,
        'trades': [
        ],
    },
    {
        'code': '159952',
        'name': '创业ETF ',
        'high': 1.083,
        'low': 0.89,
        'current': get_fund_current,
        'advice': get_fund_advice,
        'trades': [
        ],
    },
    {
        'code': '510050',
        'name': '   50ETF',
        'high': 4.67,
        'low': 1.29,
        'current': get_fund_current,
        'advice': get_fund_advice,
        'trades': [
        ],
    },
    {
        'code': '510300',
        'name': '300ETF_5',
        'high': 5.35,
        'low': 2.04,
        'current': get_fund_current,
        'advice': get_fund_advice,
        'trades': [
        ],
    },
    {
        'code': '510500',
        'name': '  500ETF',
        'high': 8.21,
        'low': 4.22,
        'current': get_fund_current,
        'advice': get_fund_advice,
        'trades': [
        ],
    },
    {
        'code': '510880',
        'name': '红利ETF ',
        'high': 5.29,
        'low': 1.29,
        'current': get_fund_current,
        'advice': get_fund_advice,
        'trades': [
        ],
    },
]

# 159937 博时黄金

# 150019 银华锐进 (分级B)

# 150153 创业板B
# 150201 券商B
# 150224 证券B级
# 150228 银行B
# 150172 证券B
# 150223 证券A级
# 150182 军工B
# 150200 券商A
# 150290 煤炭B级
# 150171 证券A
# 150152 创业板A
# 150118 房地产B
# 150222 中航军B
# 150131 医药B


all_sfunds = [
    {
        'code': '150200',
        'name': '券商A   ',
        'high': 1.10,
        'low': 0.76,
        'current': get_fund_current,
        'advice': get_fund_advice,
        'trades': [
        ],
    },
    {
        'code': '399004',
        'name': '深证100R',
        'high': 7187.62,
        'low': 1861.52,
        'current': get_fund_current,
        'advice': get_fund_advice,
        'trades': [
        ],
        'comment': '150019'
    },
    {
        'code': '399006',
        'name': '创业板指',
        'high': 4037.96,
        'low': 585.44,
        'current': get_fund_current,
        'advice': get_fund_advice,
        'trades': [
        ],
        'comment': '150153'
    },
    {
        'code': '399393',
        'name': '国证地产',
        'high': 10635.12,
        'low': 3041.88,
        'current': get_fund_current,
        'advice': get_fund_advice,
        'trades': [
        ],
        'comment': '150118'
    },
    {
        'code': '399394',
        'name': '国证医药',
        'high': 13264.63,
        'low': 4042.42,
        'current': get_fund_current,
        'advice': get_fund_advice,
        'trades': [
        ],
        'comment': '150131'
    },
    {
        'code': '399707',
        'name': 'CSSW证券',
        'high': 14500.70,
        'low': 5303.15,
        'current': get_fund_current,
        'advice': get_fund_advice,
        'trades': [
        ],
        'comment': '150172'
    },
    {
        'code': '399967',
        'name': '中证军工',
        'high': 22063.28,
        'low': 5587.53,
        'current': get_fund_current,
        'advice': get_fund_advice,
        'trades': [
        ],
        'comment': '150182'
    },
    {
        'code': '399975',
        'name': '证券公司',
        'high': 1746.18,
        'low': 650.84,
        'current': get_fund_current,
        'advice': get_fund_advice,
        'trades': [
        ],
        'comment': '150201 150224'
    },
    {
        'code': '399986',
        'name': '中证银行',
        'high': 7692.88,
        'low': 4479.42,
        'current': get_fund_current,
        'advice': get_fund_advice,
        'trades': [
        ],
        'comment': '150228'
    },
    {
        'code': '399998',
        'name': '中证煤炭',
        'high': 3390.25,
        'low': 907.67,
        'current': get_fund_current,
        'advice': get_fund_advice,
        'trades': [
        ],
        'comment': '150290 150322'
    },
]



#all_stocks = all_stocks[0:1]
#all_stocks = all_stocks[22:23]

all_sfunds = all_sfunds + all_etf

