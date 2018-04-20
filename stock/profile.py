# -*- coding: utf-8 -*-
#import sys

#import advise
import dbman

if __name__=='__main__':
    #advise.profile_main()
    #dbman.query_history('603036', '2018-3-7')
    dh = dbman.c.aggregate([{"$match": {"date": {"$eq": '2018-3-7'}}}])
