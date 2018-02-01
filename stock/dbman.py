# -*- coding: utf-8 -*-

from pymongo import MongoClient

client = MongoClient()
db = client.stock
# history schema: {"code": code, "date": tdatestr, "close": df['close'][0], "open": df['open'][0], "high": df['high'][0]}
c = db.history
# trade schema: {"code": code, "recent_high": dh['high']}
#db.trade.drop()
#c_trade = db.trade
#db.dayK.drop()
reset_KDJ = False
# dayK schema: c_dayK.insert({"code": code, "real": True, "date": originDateStr, "close": df['close'][0], "open": df['open'][0], "high": df['high'][0], "low": df['low'][0]})
# "real": if false, means copy previous day's trade data.
# c_dayK.update({"code": stock['code'], "date": datestr}, {"$set": {"theK": k, "theD": d, "theJ": j}})
c_dayK = db.dayK
