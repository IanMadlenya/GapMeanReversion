#
# Copyright (c) 2016 Yatpang Cheung. All rights reserved.
#

# imports
import downloadData
import algoSys

if __name__ == '__main__':

    # by market cap
    # comment out what is not needed 
    allCat = []
    allCat.append('Mega-cap')
    # allCat.append('Large-cap')
    # allCat.append('Mid-cap')
    # allCat.append('Small-cap')
    # allCat.append('Micro-cap')
    # allCat.append('Nano-cap')

    # True to retrieve historical data as well for each ticker
    # retrieves list of tickers that that satisfy trading criteria
    pTickerList = downloadData.getData(allCat, True)

    # Port and Client ID for program to connect to TWS
    port = 7497
    clientID = 22

    automatedSystem = algoSys.algoSys(port, clientID, pTickerList)
    automatedSystem.run()


