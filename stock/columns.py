# -*- coding: utf-8 -*-

import keys

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
    },
    { # Previous change
        'id': 'previousChange',
        'header': '昨幅',
        'width': 6,
    },
    { # Today change
        'id': 'todayChange',
        'header': '今幅',
        'width': 6,
    },
    { # Price
        'id': 'price',
        'header': '现价',
        'width': 6,
    },
    { # Last buy
        'id': 'lastBuy',
        'header': '前买',
        'width': 6,
    },
    { # Last sell
        'id': 'lastSell',
        'header': '前卖',
        'width': 6,
    },
    { # Position
        'id': 'position',
        'header': '仓位',
        'width': 4,
    },
    { # Profit
        'id': 'profit',
        'header': '盈利',
        'width': 6,
    },
    { # Regression
        'id': 'regression',
        'header': '回撤',
        'width': 3,
    },
    { # J
        'id': 'j',
        'header': 'J',
        'width': 6,
    },
    { # Duration
        'id': 'duration',
        'header': '久期',
        'width': 5,
    },
    { # Stack
        'id': 'stack',
        'header': '档位',
        'width': 5,
    },
    { # Index profit
        'id': 'indexProfit',
        'header': '指盈',
        'width': 7,
    },
    { # Index cost
        'id': 'indexCost',
        'header': '指跌',
        'width': 7,
    },
    { # Turnover
        'id': 'turnover',
        'header': '转',
        'width': 3,
    },
    { # Today profit
        'id': 'todayProfit',
        'header': '浮盈',
        'width': 7,
    },
    { # Comment
        'id': 'comment',
        'header': '备注',
        'width': 20,
    }
]

