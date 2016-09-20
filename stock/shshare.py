import httplib

def get_realtime_quotes(code):
    quotes = {}
    conn = httplib.HTTPConnection("hq.sinajs.cn")
    conn.request("GET", "/list=" + code)
    res = conn.getresponse()
    if res.status == 200:
        theData = res.read().split(',')
        #print theData
        quotes = {
            'name': theData[0].split('"')[1],
            'price': float(theData[3]),
            'high': float(theData[4]),
            'open': float(theData[2]),
            'low': float(theData[5]),
            'close': float(theData[3]),
            'previous_close': float(theData[2]),
        }
    conn.close()
    return quotes

if __name__=='__main__':  
    df = get_realtime_quotes('sh201008')
    print df
