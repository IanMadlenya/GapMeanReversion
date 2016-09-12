#
# Copyright (c) 2016 Yatpang Cheung. All rights reserved.
#

# stock class object
class stock(object):
    def __init__ (self, Ticker, dReturn, openTradePrice):
        self.ticker = Ticker
        self.dayReturn = dReturn
        self.openTrade = openTradePrice

# gets the return (from previous day high/low to open)
def getDayReturn(aStock):
    return aStock.dayReturn
