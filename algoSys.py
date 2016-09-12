#
# Copyright (c) 2016 Yatpang Cheung. All rights reserved.
#

# imports
import stock
import time

# IBPy imports
from ib.ext.Contract import Contract
from ib.ext.Order import Order
from ib.opt import Connection

# class for algorithmic system
class algoSys(object):

    # initialize system
    def __init__(self, portID, clientID, possibleTickerList):
        self.port = portID
        self.client = clientID
        self.connection = None
        self.orderID = -1
        self.balance = -1
        self.pTickerList = possibleTickerList

    # connect to TWS using port and client ID
    # register listeners to process data from TWS server
    def IBConnect(self):
        self.connection = Connection.create(port=self.port, clientId=self.client)
        self.registerListeners()
        self.connection.connect()

    # disconnect client to TWS
    def IBDisconnect(self):
        if self.connection is not None:
            self.connection.disconnect()

    # set up listener
    def registerListeners(self):
        self.connection.registerAll(self.serverListener)

    # process message from server
    def serverListener(self, message):

        if message.typeName == "nextValidId":
            self.orderID = int(message.orderId)
        elif message.typeName == "accountSummary":
            self.balance = float(message.value)
        elif message.typeName == "error" and message.id != -1:
            print "Error message:", message

    # run the system
    def run(self):

        # if there are possible trade candidates
        if len(self.pTickerList) > 0:

            self.IBConnect()
            self.registerListeners()

            # request to see how much money is in account
            self.connection.reqAccountSummary(1000, 'All', 'TotalCashValue')

            time.sleep(1)

            # make sure that we retrieved the balance amount and the valid order ID
            # from the server before proceeding
            while self.connection is None and self.orderID == -1 and self.balance == -1:
                pass

            # sort the list based on returns so the worst performers (buy) will
            # be at the front of list and the best performers (sell) will be at the end
            pTickerListSorted = sorted(self.pTickerList, key = stock.getDayReturn)

            # trade 90% of amount, 10% kept as reserve for precautionary measures
            amtToTrade = self.balance * 0.9

            if len(pTickerListSorted) >= 30:

                # equal amount per position
                perPositionAmt = amtToTrade/15

                # first 15, which are worst performers (buy)
                for pLTicker in pTickerListSorted[:15]:

                    # place market order to buy and market-on-close order to sell
                    self.placeMktOrder(pLTicker.ticker, 'BUY', int(perPositionAmt/pLTicker.openTrade))
                    self.placeMOCOrder(pLTicker.ticker, 'SELL', int(perPositionAmt/pLTicker.openTrade))
                    time.sleep(1)

                # last 15, which are best performers (sell)
                for pSTticker in pTickerListSorted[-15:]:

                    # place market order to sell and market-on-close order to buy
                    self.placeMktOrder(pSTicker.ticker, 'SELL', int(perPositionAmt/pSTicker.openTrade))
                    self.placeMOCOrder(pSTicker.ticker, 'BUY', int(perPositionAmt/pSTicker.openTrade))
                    time.sleep(1)
            else:

                # less than 30 stocks in list, find the number of down performers
                down = 0
                for pTicker in pTickerListSorted:
                    if pTicker.dayReturn < 1:
                        down +=1

                # maintain respective even amount to maintain market neutrality
                perLongPositionAmt = amtToTrade/down
                perShortPositionAmt = amtToTrade/(len(pTickerListSorted)-down)

                # for all down performers
                for pLTicker in pTickerListSorted[:down]:

                    # place market order to buy and market-on-close order to sell
                    self.placeMktOrder(pLTicker.ticker, 'BUY', int(perLongPositionAmt/pLTicker.openTrade))
                    self.placeMOCOrder(pLTicker.ticker, 'SELL', int(perLongPositionAmt/pLTicker.openTrade))
                    time.sleep(1)

                # for remaining positive performers
                for pSTicker in pTickerListSorted[down:]:

                    # place market order to sell and market-on-close order to buy
                    self.placeMktOrder(pSTicker.ticker, 'BUY', int(perShortPositionAmt/pSTicker.openTrade))
                    self.placeMOCOrder(pSTicker.ticker, 'SELL', int(perShortPositionAmt/pSTicker.openTrade))
                    time.sleep(1)

            self.IBDisconnect()
        else:
            print "No activity for the day. Market quiet."

    # places a market order using SMART order routing
    def placeMktOrder(self, ticker, action, shares):
        contract = self.createContract(ticker, 'STK', 'SMART', 'SMART', 'USD')
        order = self.createOrder('MKT', action, shares)
        self.connection.placeOrder(self.orderID, contract, order)
        self.orderID += 1

    # places a market-on-close order using SMART order routing
    def placeMOCOrder(self, ticker, action, shares):
        contract = self.createContract(ticker, 'STK', 'SMART', 'SMART', 'USD')
        order = self.createOrder('MOC', action, shares)
        self.connection.placeOrder(self.orderID, contract, order)
        self.orderID += 1

    # creates an order 
    def createOrder(self, orderType, action, shares):
        order = Order()
        order.m_orderType = orderType
        order.m_action = action
        order.m_totalQuantity = shares
        return order

    # creates a contract meant to be binded with an order
    def createContract(self, ticker, secType, exchange, primaryExch, currency):
        contract = Contract()
        contract.m_symbol = ticker
        contract.m_secType = secType
        contract.m_exchange = exchange
        contract.m_primaryExch = primaryExch
        contract.m_currency = currency
        return contract
