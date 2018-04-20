# -*- coding: utf-8 -*-

from pymongo import MongoClient

c_mem = {}
c_dayK_mem = {}

def init():
    # read everything into mem.
    pass

def query_history(code, datestr):
    dh = c.aggregate([{"$match": {"code": {"$eq": code}}}, {"$match": {"date": {"$eq": datestr}}}])
    return list(dh)

def insert_history(code, datestr, open, close, high):
    c.insert({"code": code, "date": datestr, "close": close, "open": open, "high": high})

def update_history(code, datestr, high):
    c.update({"code": code, "date": datestr}, {"$set": {"high": high}})

def update_history_recent_low(code, datestr, recent_low):
    c.update({"code": code, "date": datestr}, {"$set": {"recent_low": recent_low}})

def query_dayK(code, datestr):
    dh = c_dayK.aggregate([{"$match": {"code": {"$eq": code}}}, {"$match": {"date": {"$eq": datestr}}}])
    return list(dh)

def insert_dayK(code, real, datestr, open, close, high, low):
    c_dayK.insert({"code": code, "real": real, "date": datestr, "close": close, "open": open, "high": high, "low": low})

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
