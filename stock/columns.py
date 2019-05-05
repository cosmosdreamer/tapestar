# -*- coding: utf-8 -*-

import keys


def profit_color(stock, default):
    currentProfit_color = 1
    duration = stock['more_info_duration_last'] if stock.has_key('more_info_duration_last') else 0
    if stock['more_info_profit_percent'] >= 7 + duration:
        currentProfit_color = 3
    elif stock['more_info_lastBuy'] == 0 and stock['more_info_profit_percentstr'] != '':
        currentProfit_color = 2
    return currentProfit_color

def regress_color(stock, default):
    regress_rate_color = 1
    #if (not stock.has_key('last100') and stock['more_info_regress_rate'] >= 28) \
    #    or stock.has_key('last100') and stock['last100'] and stock['more_info_stack'] == 1 and stock['more_info_regress_rate'] >= 58:
    if (stock['more_info_stack'] != 1 and stock['more_info_regress_rate'] >= 28) \
        or (stock['more_info_stack'] == 1 and stock['more_info_regress_rate'] >= 48):
        regress_rate_color = 3
    return regress_rate_color

def j_color(stock, default):
    currentJ_color = 1
    if stock['more_info_currentJ'] <= 20:
        currentJ_color = 2
    elif stock['more_info_currentJ'] >= 80:
        currentJ_color = 3
    return currentJ_color

s_columns = [
    'no.',
    'name',
    'price',
    'profit',
    'regression',
]

columns = [
    { # No.
        'id': 'no.',
        'header': '',
        'width': 3,
    },
    { # Code
        'id': 'code',
        'header': '',
        'width': 6,
        'value': lambda stock: stock['code']
    },
    { # Name
        'id': 'name',
        'header': '',
        'width': 8,
        'value': lambda stock: stock['name']
    },
    { # Action
        'id': 'action',
        'header': '',
        'width': 4,
        'value': lambda stock: stock['action'],
        'color': lambda stock, default: stock['action_color'],
    },
    { # Previous change
        'id': 'previousChange',
        'header': '昨幅',
        'width': 6,
        'value': lambda stock: '%6.2f' % (stock['more_info_previousChange']),
    },
    { # Today change
        'id': 'todayChange',
        'header': '今幅',
        'width': 6,
        'value': lambda stock: '%6.2f' % (stock['more_info_todayChange']),
    },
    { # Price
        'id': 'price',
        'header': '现价',
        'width': 6,
        'value': lambda stock: '%6.2f' % (stock['more_info_currentPrice']),
    },
    { # Last buy
        'id': 'lastBuy',
        'header': '前买',
        'width': 6,
        'value': lambda stock: '%6.2f' % (stock['more_info_lastBuy']),
    },
    { # Last sell
        'id': 'lastSell',
        'header': '前卖',
        'width': 6,
        'value': lambda stock: '%6.2f' % (stock['more_info_lastSell']),
    },
    { # Position
        'id': 'position',
        'header': '仓位',
        'width': 5,
        'value': lambda stock: '%5d' % (stock['more_info_position']),
    },
    { # Profit
        'id': 'profit',
        'header': '盈利',
        'width': 4,
        'value': lambda stock: stock['more_info_profit_percentstr'],
        'color': profit_color,
    },
    { # Regression
        'id': 'regression',
        'header': '回撤',
        'width': 4,
        'value': lambda stock: stock['more_info_regress_ratestr'],
        'color': regress_color,
    },
    { # J
        'id': 'j',
        'header': 'J',
        'width': 6,
        'value': lambda stock: '%6.2f' % (stock['more_info_currentJ']),
        'color': j_color,
    },
    { # Duration
        'id': 'duration',
        'header': '久期',
        'width': 5,
        'value': lambda stock: stock['more_info_durationstr'],
    },
    { # Stack
        'id': 'stack',
        'header': '档位 ',
        'width': 5,
        'value': lambda stock: stock['more_info_stackstr'],
    },
#    { # Index profit
#        'id': 'indexProfit',
#        'header': '指盈',
#        'width': 7,
#    },
#    { # Index cost
#        'id': 'indexCost',
#        'header': '指跌',
#        'width': 7,
#    },
    { # Turnover
        'id': 'turnover',
        'header': '转',
        'width': 3,
        'value': lambda stock: '%3d' % stock['turnover'],
    },
    { # Today profit
        'id': 'todayProfit',
        'header': '浮盈',
        'width': 7,
        'value': lambda stock: '%7d' % stock['more_info_today_change'],
    },
    { # Amount
        'id': 'amount',
        'header': '持仓额',
        'width': 7,
        'value': lambda stock: '%7d' % stock['amount'],
    },
    { # CurrentAmount
        'id': 'currentAmount',
        'header': '市值',
        'width': 7,
        'value': lambda stock: '%7d' % stock['currentAmount'],
    },
    { # Comment
        'id': 'comment',
        'header': '备注                                            ',
        'width': 20,
        'value': lambda stock: stock['more_info_comment'],
    }
]

