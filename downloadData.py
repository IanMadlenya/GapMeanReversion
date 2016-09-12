#
# Copyright (c) 2016 Yatpang Cheung. All rights reserved.
#

# imports
import urllib
import requests
import numpy
import stock

#local paths to store data, change to local setting and create the folders
exchangeDataBase = '/Users/.../exchangeData/'
equitiesDataBase = '/Users/.../equitiesData/'

# NASDAQ link, can adjust additional parameters here
downloadLinkA = 'http://www.nasdaq.com/screening/companies-by-region.aspx?region=North+America&marketcap='
downloadLinkB = '&country=United%20States&render=download'

# Yahoo Finance historical data
yahooFinance = 'http://ichart.finance.yahoo.com/table.csv?s='

# download the file at a particular url and saves it to filename
# for this program, we will save the downloaded data for viewing purposes if needed
# get switch to GET REQUEST to avoid saving file
def downloadFile(url, filename):
    urllib.urlretrieve(url, filename)

# retrieves the data for some categories of stock universe
# getHistorical = True if you want to retrieve historical data as well
def getData(allCat, getHistorical):

    #csv file of all tickers and all columns
    allFile = open(exchangeDataBase+'All.csv', 'w')

    #text file of tickers with market cap and sector
    tickerFile = open(exchangeDataBase+'Tickers.txt', 'w')

    tracker = 0

    tickerList = []

    for cat in allCat:
        downloadFile(downloadLinkA+cat+downloadLinkB, exchangeDataBase+cat+'.csv')

        with open(exchangeDataBase+cat+'.csv') as f:
            content = f.read()

            for line in content.split('\n')[1:]:
                if line != '':
                    lineTemp = line[1:]
                    lineTemp = lineTemp[:-2]
                    col = lineTemp.split('","')

                    # clean up data and exclude ETFs and funds
                    # exclude share prices trading less than $5 during last trade session
                    if(col[7] != 'n/a' and col[8] != 'n/a' and float(col[2]) > 5.0 and float(col[3])> 0.0):
                        allFile.write(line+'\n')

                        # marketcap = float(col[3])
                        # above variable can be used to further constrain market cap if needed

                        tickerFile.write(col[0]+'\n')
                        tickerList.append(col[0])

                        # downloads historical data if true
                        if(getHistorical):
                            downloadFile(yahooFinance+col[0], equitiesDataBase+col[0]+'.csv')
                            tracker = tracker + 1
                            print "Count: "+str(tracker)+"."+" Ticker Downloaded: "+col[0]+'\n'

    allFile.close()
    tickerFile.close()

    return processTickers(tickerList)

# process the retrieved data to return a list of stocks satisfying trade criteria
def processTickers(tickerList):

    pTickerList = []

    for ticker in tickerList:
        with open(equitiesDataBase+ticker+'.csv') as f:
            content = f.read()
            priceList = []

            dayHigh = 0.0;
            dayLow = 0.0;
            day = 1
            for line in content.split('\n')[1:]:
                lineList = line.split(',')
                if len(lineList) == 7:

                    # get day high and low for the previous trading session
                    if day == 1:
                        dayHigh = float(lineList[2])
                        dayLow = float(lineList[3])
                    day = day + 1

                    # store list of adjusted close to std and mavg calculations
                    adjustedClose = float(lineList[6])
                    priceList.append(adjustedClose)
                    
            # retrieve opening trade price (last traded price during market open)
            openTrade = float(requestRealTime(ticker))

            # calculate standard deviation from past 90 day
            standardDev = numpy.std(calcReturns(priceList[:90]))

            # calculate 20 day moving average
            movingAvg = sum(priceList[:20])/len(priceList[:20])

            # is a potential ticker if satisfy criteria
            pTicker = None
            if openTrade > dayHigh and openTrade < movingAvg and (openTrade/dayHigh-1) < standardDev:
                pTicker = stock.stock(ticker, openTrade/dayHigh, openTrade)

            if openTrade < dayLow and openTrade > movingAvg and (1-openTrade/dayLow) < standardDev:
                pTicker = stock.stock(ticker, openTrade/dayLow, openTrade)

            if pTicker is not None:
                pTickerList.append(pTicker)
            
    return pTickerList

# retrieves real time data for most recet trade
def requestRealTime(ticker):

    yahooRealTimeURL = "http://finance.yahoo.com/d/quotes.csv?s="+ticker+"&f=l1"
    req = requests.get(yahooRealTimeURL)

    return req.content

# converts a price list into a return list
def calcReturns(priceList):

    returnList = []
    for i in range(len(priceList)-1):
        dailyReturn = (priceList[i]/priceList[i+1]-1)
        returnList.append(dailyReturn)
    return returnList

