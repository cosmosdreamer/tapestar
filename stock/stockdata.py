# -*- coding: utf-8 -*-

all_stocks = [
     {
        'code': '000002', # 万科Awka
        'KDJ': { '2016-7-21': [10.8, 10.4, 11.6]},
        'trades': [
            ['2016-7-20', 2, 100, 17.28, '2016-8-9', 21.44],
        ],
        'comment': '房地产',
    },
    {
        'code': '000025', # 特力Atla
        'KDJ': { '2015-12-10': [71.55, 71.30, 72.04]},
        'trades': [
            ['2016-2-26', 2, 100, 68.49, '2016-3-25', 79.26],
            ['2016-4-21', 2, 100, 67.50, '2016-8-17', 75.31],
            ['2016-5-13', 2, 100, 56.59, '2016-7-5', 73.69],
            ['2016-8-25', 1, 100, 65.97],
        ],
        'comment': '<--',
    },
    {
        'code': '000413', # 东旭光电dxgd
        'KDJ': { '2015-12-10': [20.93, 36.51, -10.25]},
        'margin': [10],
        'trades': [
            ['2015-12-16', 2, 100, 9.52, '2016-7-27', 13.55],
            ['2016-1-28', 2, 100, 6.01, '2016-2-16', 7.17],
        ],
        'comment': '石墨烯，蓝宝石<--',
    },
    {
        'code': '000488', # 晨鸣纸业cmzy
        'KDJ': { '2015-12-10': [22.18, 31.70, 3.14]},
        'trades': [
        #    ['2015-7-13', 1, 100, 8.71]
            ['2016-1-18', 2, 100, 7.10, '2016-2-19', 7.84],
        ],
        'comment': '汇金证金?',
    },
    {
        'code': '000531', # 穗恒运Ashya
        'KDJ': { '2015-12-24': [76.95, 75.53, 79.79]},
        'trades': [
            ['2015-12-29', 1, 100, 11.98],
            ['2016-1-12', 2, 100, 9.75, '2016-6-14', 12.73],
        ],
        'comment': '弋弋推荐',
    },
    {
        'code': '000630', # 铜陵有色tlys
        'KDJ': { '2015-12-10': [25.10, 29.78, 15.72]},
        'trades': [
            ['2015-10-27', 1, 200, 4.47],
            ['2015-10-30', 1, 200, 3.92],
            ['2016-1-8', 1, 500, 3.22],
            ['2016-1-21', 1, 600, 2.94],
            ['2016-6-15', 2, 1000, 2.51, '2016-7-8', 2.67],
            ['2016-8-1', 1, 1000, 2.56],
        ],
    },
    {
        'code': '000671', # 阳光城ygc
        'KDJ': { '2015-12-10': [75.36, 70.99, 84.09]},
        'trades': [
            ['2016-4-1', 1, 500, 6.13],
        ],
        'comment': '二线房地产',
    },
    {
        'code': '000725', # 京东方Ajdfa
        'KDJ': { '2015-12-25': [57.16, 59.79, 51.90]},
        'margin': [1.9],
        'trades': [
            ['2015-12-28', 1, 500, 3.04],
            ['2016-1-15', 1, 1000, 2.63],
            ['2016-1-27', 2, 1000, 2.33, '2016-2-17', 2.64],
            ['2016-4-19', 1, 1000, 2.53],
            ['2016-5-18', 1, 1000, 2.26],
        ],
        'comment': '低价股，计算机',
    },
    {
        'code': '000750', # 国海证券ghzq
        'KDJ': { '2015-12-24': [64.76, 69.71, 54.88]},
        'trades': [
            ['2015-12-28', 1, 150, 8.57],
            ['2016-1-12', 2, 100, 10.14, '2016-3-29', 10.79],
            ['2016-6-24', 2, 200, 7.28, '2016-7-15', 7.80],
            ['2016-7-20', 1, 500, 7.60],
            ['2016-8-2', 2, 500, 6.80, '2016-8-16', 7.42],
        ],
    },
    {
        'code': '000898', # 鞍钢股份aggf
        'KDJ': { '2015-12-10': [25.88, 32.89, 11.87]},
        'margin': [3.98],
        'trades': [
            ['2015-7-22', 1, 200, 6.21],
            ['2015-9-16', 1, 100, 4.98],
            ['2015-10-8', 1, 200, 4.83],
            ['2016-1-21', 1, 300, 4.62],
            ['2016-2-1', 2, 500, 3.73, '2016-2-18', 3.97],
            ['2016-6-15', 2, 500, 3.69, '2016-7-11', 4.01],
        ],
    },
    {
        'code': '000900', # 现代投资xdtz
        'KDJ': { '2015-12-10': [40.92, 43.19, 36.40]},
        'margin': [6, 9.5],
        'trades': [
            ['2015-11-9', 1, 100, 8.68],
            ['2016-1-22', 2, 200, 6.80, '2016-4-19', 7.25],
        ],
        'comment': '滞涨股',
    },
    {
        'code': '002008', # 大族激光dzjg
        'KDJ': { '2015-12-10': [69.32, 59.40, 89.15]},
        'trades': [
            ['2015-8-12', 2, 100, 27.14, '2016-1-5', 22.55],
            ['2016-1-8', 2, 100, 21.79, '2016-8-22', 23.78],
            ['2016-1-29', 2, 100, 19.93, '2016-2-23', 22.25],
            ['2016-2-25', 2, 100, 20.03, '2016-4-20', 23.11],
            ['2016-2-25', 2, 100, 20.03, '2016-4-1', 22.19],
            ['2016-5-18', 2, 100, 20.62, '2016-5-30', 23.10],
            ['2016-9-5', 1, 100, 22.30],
        ],
        'comment': '一堆概念',
    },
    {
        'code': '002022', # 科华生物khsw
        'KDJ': { '2016-5-5': [66.2, 49.1, 100.3]},
        'margin': [19],
        'trades': [
            ['2016-4-27', 2, 100, 19.73, '2016-7-7', 21.48],
        ],
    },
    {
        'code': '002027', # 分众传媒fzcm
        'KDJ': { '2016-6-29': [77.8, 68.1, 97.2]},
        'margin': [14.5],
        'trades': [
            ['2016-8-9', 1, 100, 15.63],
            ['2016-8-23', 1, 100, 15.32],
            ['2016-9-13', 1, 400, 14.54],
        ],
        'comment': '<--',
    },
    {
        'code': '002106', # 莱宝高科lbgk
        'KDJ': { '2015-12-10': [26.00, 26.37, 25.27]},
        'trades': [
        #    ['2015-4-2', 1, 100, 16.43],
        #    ['2015-11-23', 1, 100, 14.79],
        #    ['2015-12-7', 1, 200, 13.61],
            ['2016-1-18', 2, 100, 8.83, '2016-5-9', 10.41],
        ],
        'comment': '苹果三星<--',
    },
    {
        'code': '002164', # 宁波东力nbdl
        'KDJ': { '2015-12-10': [59.28, 66.63, 44.57]},
        'trades': [
            ['2015-8-17', 1, 100, 11.89],
            ['2015-8-19', 2, 100, 9.99, '2016-7-4', 11.74],
            ['2016-7-12', 1, 100, 10.18],
            ['2016-8-3', 1, 100, 8.88],
        ],
        'comment': '风能',
    },
    {
        'code': '002271', # 东方雨虹dfyh
        'KDJ': { '2015-12-10': [63.21, 68.86, 51.93]},
        'margin': [15],
        'trades': [
            ['2015-12-17', 2, 100, 20.76, '2016-1-5', 16.91],
        ],
        'comment': '防雨',
    },
    {
        'code': '002273', # 水晶光电sjgd
        'KDJ': { '2015-12-10': [49.07, 49.94, 47.32]},
        'comment': 'VR<--',
        'trades': [
            ['2016-4-21', 2, 50, 21.33, '2016-6-2', 26.27],
            ['2016-4-21', 2, 100, 21.33, '2016-5-23', 22.78],
            ['2016-7-28', 2, 100, 23.39, '2016-9-5', 26.18],
        ],
    },
    {
        'code': '002290', # 禾盛新材hsxc
        'KDJ': { '2015-12-10': [19.68, 31.71, -4.38]},
        'trades': [
            ['2015-12-30', 1, 100, 33.43],
            ['2016-1-6', 1, 100, 27.56],
            ['2016-1-11', 2, 100, 23.35, '2016-6-1', 26.47],
            ['2016-3-11', 2, 100, 19.04, '2016-3-25', 22.96],
            ['2016-3-11', 2, 100, 19.04, '2016-3-21', 23.36],
            ['2016-4-22', 2, 100, 20.91, '2016-5-13', 22.62],
            ['2016-7-22', 2, 100, 24.75, '2016-8-22', 26.06],
            ['2016-9-2', 2, 100, 24.70, '2016-9-7', 26.12],
        ],
        'comment': '电器，新材料',
    },
    {
        'code': '002450', # 康得新kdx
        'KDJ': { '2015-12-17': [77.24, 75.20, 81.30]},
        'margin': [17],
        'trades': [
            ['2015-5-26', 1, 200, 22.25],
        #    ['2015-6-10', 1, 100, 40.49],
            ['2016-3-8', 2, 100, 30.26, '2016-3-21', 32.69],
            ['2016-4-26', 2, 200, 15.7, '2016-6-6', 17.1],
            ['2016-6-14', 2, 200, 16.13, '2016-6-23', 17.58],
            ['2016-7-27', 1, 100, 18.04],
        ],
        'comment': '一堆概念',
    },
    {
        'code': '002454', # 松芝股份szgf
        'KDJ': { '2015-12-10': [33.77, 31.61, 38.10]},
        'trades': [
            #['2015-12-9', 1, 100, 16.95],
            ['2016-1-18', 2, 100, 12.66, '2016-3-3', 14.84],
        ],
        'comment': '冷链',
    },
    {
        'code': '002567', # 唐人神trs
        'KDJ': { '2015-12-10': [82.56, 76.34, 95.01]},
        'margin': [9],
        'trades': [
            ['2015-11-2', 2, 100, 10.5, '2016-4-12', 13.23],
            ['2016-2-25', 2, 100, 11.56, '2016-4-8', 13.25],
            ['2016-3-11', 2, 100, 9.02, '2016-3-28', 12.16],
            ['2016-3-11', 2, 200, 9.02, '2016-3-23', 11.58],
        ],
        'comment': '猪肉',
    },
    {
        'code': '002570', # 贝因美bym
        'KDJ': { '2015-12-10': [37.43, 35.53, 41.24]},
        'margin': [9, 14],
        'trades': [
            ['2015-11-23', 1, 100, 16.1],
            #['2015-12-1', 1, 100, 13.9],
            ['2016-1-5', 2, 100, 13.04, '2016-7-13', 14.41],
        ],
        'comment': 'XXX二胎',
    },
    {
        'code': '002594', # 比亚迪byd
        'KDJ': { '2015-12-10': [58.51, 48.29, 78.95]},
        'margin': [52, 66],
        'trades': [
            ['2015-12-9', 1, 100, 63.17],
            ['2016-1-26', 2, 100, 52.28, '2016-3-18', 56.44],
        ],
        'comment': '新能源汽车',
    },
    #{
    #    'code': '150022', # 深成指Ascza
    #    # 'KDJ': { '2016-7-21': [10.8, 10.4, 11.6]},
    #    'trades': [
    #        ['2016-7-13', 1, 600, 0.824],
    #    ],
    #    'comment': '分级A',
    #},
    {
        'code': '300001', # 特锐德trd
        'KDJ': { '2015-12-10': [48.60, 46.60, 52.59]},
        'trades': [
            ['2016-1-8', 2, 100, 23.60, '2016-3-31', 24.84],
            ['2016-5-16', 2, 100, 20.30, '2016-7-6', 21.88],
            ['2016-8-1', 1, 100, 20.40],
        ],
        'comment': '创业板，充电桩<--',
    },
    {
        'code': '300003', # 乐普医疗lpyl
        'KDJ': { '2015-12-25': [61.57, 68.32, 48.06]},
        'margin': [15],
        'comment': '医疗器械',
    },
    {
        'code': '300027', # 华谊兄弟hyxd
        'KDJ': { '2016-3-15': [51.5, 43.3, 67.8]},
        'trades': [
            ['2016-3-15', 2, 100, 24.45, '2016-3-21', 27.04],
            ['2016-5-8', 2, 300, 13.43, '2016-6-2', 15.08],
            ['2016-6-13', 1, 100, 13.85],
            ['2016-8-1', 1, 300, 12.46],
        ],
        'comment': '深港通',
    },
    {
        'code': '300161', # 华中数控hzsk
        'KDJ': { '2015-12-10': [18.39, 23.28, 8.60]},
        'trades': [
            ['2016-1-14', 2, 100, 24.54, '2016-1-20', 25.68],
            ['2016-1-26', 2, 100, 22.23, '2016-4-8', 23.54],
            ['2016-3-7', 2, 100, 17.50, '2016-3-10', 19.19],
            ['2016-5-20', 2, 100, 20.48, '2016-6-8', 26.07],
        ],
        'comment': '机器人<--',
    },
    {
        'code': '300185', # 通裕重工tyzg
        'KDJ': { '2015-12-25': [67.55, 66.49, 69.68]},
        'margin': [2.5],
        'trades': [
            ['2016-2-26', 2, 300, 6.44, '2016-3-21', 6.98],
        ],
        'comment': '无人机',
    },
    {
        'code': '300431', # 暴风科技bfkj
        'last_sell': 0.00,
        'last_buy': 0.00,
        'position': 0,
        'KDJ': { '2015-12-10': [86.67, 87.67, 84.68]},
        'margin': [50],
    },
    {
        'code': '510150', # 消费ETFxfetf
        #'last_sell': 0,
        'KDJ': { '2016-1-19': [25.8, 26.5, 24.4]},
        'margin': [3.2],
        'trades': [
            ['2016-1-20', 2, 500, 3.498, '2016-7-20', 3.771],
        ],
        'comment': 'XXX',
    },
    {
        'code': '510210', # 综指ETFzzetf
        'last_sell': 0,
        'KDJ': { '2016-1-20': [18.2, 17.9, 19.0]},
        'margin': [3, 3.5],
        'trades': [
            ['2016-1-21', 1, 500, 3.27],
        ],
        'comment': 'XXX',
    },
    {
        'code': '600008', # 首创股份scgf
        'KDJ': { '2015-12-10': [16.35, 25.89, -2.73]},
        'margin': [3.68],
        'trades': [
            ['2015-8-18', 1, 200, 6.38],
            ['2015-8-18', 1, 200, 5.71],
            ['2016-1-21', 2, 100, 7.94, '2016-3-31', 8.46],
            ['2016-7-29', 2, 300, 3.94, '2016-9-9', 4.54],
        ],
        'comment': '污水处理，节能环保',
    },
    {
        'code': '600027', # 华电国际hdgj
        'KDJ': { '2015-1-24': [11.7, 11.9, 11.4]},
        'margin': [4.8, 5.5],
        'trades': [
            ['2016-1-25', 1, 1000, 5.21],
            ['2016-1-27', 2, 1000, 4.88, '2016-2-19', 5.17],
        ],
        'comment': '弋弋推荐',
    },
    {
        'code': '600029', # 南方航空nfhk
        'KDJ': { '2015-12-10': [41.63, 42.18, 40.52]},
        'margin': [6.15],
        'trades': [
            ['2015-8-21', 1, 100, 9.77],
            #['2015-12-1', 1, 100, 7.89],
            ['2016-1-26', 2, 200, 7.35, '2016-7-14', 8.35],
            ['2016-4-13', 2, 300, 6.38, '2016-5-8', 7.28],
            ['2016-8-31', 1, 400, 7.26],
        ],
        'comment': '',
    },
    {
        'code': '600522', # 中天科技ztkj
        'KDJ': { '2015-12-10': [20.84, 34.59, -6.65]},
        'margin': [7.8],
        'trades': [
            ['2015-8-12', 2, 250, 10.4, '2016-7-22', 11.98],
            #['2015-12-9', 1, 100, 21.97],
            ['2016-1-12', 2, 100, 18.14, '2016-4-28', 20.90],
        ],
        'comment': '军工锂电石墨烯',
    },
    {
        'code': '600886', # 国投电力gtdl
        'KDJ': { '2015-12-25': [51.51, 51.55, 51.43]},
        'margin': [6, 8],
        'trades': [
            ['2016-1-8', 1, 100, 7.41],
            ['2016-1-29', 2, 100, 6.12, '2016-2-24', 6.67],
        ],
    },
    {
        'code': '601288', # 农业银行nyyh
        'KDJ': { '2015-12-10': [48.01, 51.12, 41.78]},
        'margin': [3, 3.6],
        'trades': [
            ['2015-4-20', 1, 1000, 3.885],
            ['2015-4-28', 1, 1000, 3.88],
            ['2015-5-5', 1, 1000, 3.78],
            ['2015-7-13', 1, 1000, 3.6],
        #    ['2015-7-27', 1, 1000, 3.56],
        #    ['2015-8-17', 1, 1000, 3.41],
        #    ['2015-8-19', 1, 1000, 3.301],
            ['2016-1-27', 2, 1000, 2.96, '2016-3-4', 3.16],
        ],
    },
    {
        'code': '601766', # 中国中车zgzc
        'KDJ': { '2016-2-16': [54.03, 38.08, 85.93]},
        'trades': [
        #    ['2015-7-20', 1, 100, 18.1],
        #    ['2015-8-6', 1, 200, 15.48],
        #    ['2015-12-9', 1, 100, 13.11],
            ['2016-2-29', 2, 200, 9.25, '2016-3-7', 10.14],
            ['2016-6-14', 1, 200, 9.06],
        ],
    },
    {
        'code': '601857', # 中国石油zgsy
        'KDJ': { '2015-12-10': [16.48, 25.66, -1.89]},
        'margin': [6.8, 7.7],
        'trades': [
            ['2015-11-26', 1, 100, 9.02],
            ['2016-2-15', 2, 700, 7.17, '2016-3-4', 7.76],
            ['2016-5-16', 1, 400, 7.19],
        ],
    },
    {
        'code': '601919', # 中国远洋zgyy
        'KDJ': { '2016-4-20': [46.8, 50.8, 38.6]},
        'margin': [4.5],
        'trades': [
            ['2016-4-21', 1, 300, 6.04],
            ['2016-4-28', 1, 300, 5.71],
            ['2016-5-26', 1, 400, 5.09],
            ['2016-8-31', 1, 500, 5.14],
        ],
    },
    {
        'code': '601933', # 永辉超市yhcs
        'KDJ': { '2016-5-5': [65.2, 51.9, 91.9]},
        'trades': [
            ['2016-4-29', 2, 600, 4.13, '2016-7-21', 4.51],
        ],
    },
    {
        'code': '601985', # 中国核电zghd
        'KDJ': { '2015-12-10': [38.60, 37.05, 41.68]},
        'margin': [6.3],
        'trades': [
            ['2016-1-18', 1, 100, 7.90],
        ],
    },
    {
        'code': '601989', # 中国重工zgzg
        'KDJ': { '2015-12-10': [16.24, 22.97, 2.79]},
        'margin': [6],
        'trades': [
            ['2015-8-20', 1, 100, 14.11],
            ['2015-9-10', 1, 100, 11.08],
            ['2016-1-18', 1, 100, 7.84],
            ['2016-5-20', 2, 200, 5.88, '2016-6-29', 6.43],
        ],
        'comment': '军工,航母',
    },
]

#all_stocks = all_stocks[0:1]
#all_stocks = all_stocks[22:23]

