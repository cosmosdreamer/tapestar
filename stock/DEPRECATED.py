



import httplib
import json
#from dateutil import rrule
import lxml.html.soupparser as soupparser

#def update_metal():
#    if g_arg_simplified:
#        return
#    conn = httplib.HTTPConnection("www.icbc.com.cn")
#    conn.request("GET", "/ICBCDynamicSite/Charts/GoldTendencyPicture.aspx")
#    res = conn.getresponse()
#    if res.status == 200:
#        theData = res.read()
#        #print theData
#        dom = soupparser.fromstring(theData)
#        # no tbody for first table. index starts from 1
#        current_price = dom.xpath("//body/form/table/tr/td/table[6]/tbody/tr/td/div/table/tbody/tr[3]/td[3]")
#        if len(current_price) > 0:
#            current_price = current_price[0].text.strip()
#            last_buy = precious_metals[0]["trades"][-1][3]
#            profit_percent = math.floor((float(current_price) - last_buy) / last_buy * 10000) / 100
#            if profit_percent > 0:
#                profit_percentstr = str(profit_percent) + "%"
#            else:
#                profit_percentstr = " "
#            display_info("银: " + current_price + " 盈: " + profit_percentstr, 100, 1)
#    conn.close()













