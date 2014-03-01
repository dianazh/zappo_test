import requests
import re
from collections import defaultdict
import itertools

#Basic form of query: to find all the data with a certain rage, return only (price, productId) pair 
#http://api.zappos.com/Search?term=&excludes=[%22styleId%22,%22originalPrice%22,%22productUrl%22,%22thumbnailImageUrl%22,%22colorId%22,%22productName%22,%22brandName%22,%22percentOff%22]&filters={%22priceFacet%22:[%22$50.00%20and%20Under%22]}&sort={%22price%22:%22desc%22}&limit=100&page=457&key=a73121520492f88dc3d33daf2103d7574f1a3166

def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False

priceDict = defaultdict(list)
priceList = []

def query_price_list(queryBound,key,pageNum = None):
### Query and parse the data, i.e. price and productId
    if pageNum == None:
        pageNum = 1
    urlP1 = 'http://api.zappos.com/Search?term=&excludes=[%22styleId%22,%22originalPrice%22,%22productUrl%22,%22thumbnailImageUrl%22,%22colorId%22,%22productName%22,%22brandName%22,%22percentOff%22]&filters={%22priceFacet%22:[%22'
    urlP2 = '%22]}&sort={%22price%22:%22desc%22}&limit=100&page='
    urlP3 = '&key='+key  #key may subject to change
    url = urlP1+queryBound+urlP2+str(pageNum)+urlP3
    r = requests.get(url)
    while (r.status_code != 200):
            r = requests.get(url)
    ###find total page number, for later query by page
    totalResult = re.findall('"totalResultCount":"[0-9]*"',r.text)
    pagetemp = int(re.findall(r"[0-9]+",totalResult[0])[0])/100
    totalPage = int(pagetemp)
    if (isfloat(pagetemp)):
        totalPage += 1
    while (pageNum != totalPage+1):
        ###list possible price
        list_of_price = re.findall('"results":\[\S+\]',r.text)
        prices = re.findall(r"[0-9]*\.[0-9]*",list_of_price[0])
        pid = re.findall(r"[0-9]{7,7}",list_of_price[0])
        prices = map(float,prices)
        pid = map(int,pid)
        index = 0
        currPrice = 0
        pastPrice = 0
        for i in prices:
            if i == currPrice:
                priceDict[currPrice].append(pid[index])
                index += 1
            else:
                pastPrice = currPrice
                currPrice = i
                priceDict[currPrice].append(pid[index])
                priceList.append(currPrice)
                index += 1
        ###query the new page
        pageNum += 1
        url = urlP1+fiftyUnder+urlP2+str(pageNum)+urlP3
        r = requests.get(url)
        while (r.status_code != 200):
            r = requests.get(url)

def test_query_price_list(queryBound,pageNum = None):
#same as query_price_list(), for test purpose. Take provided input: testdata.txt
    if pageNum == None:
        pageNum = 1
    f = open('testdata.txt')
    lines = f.readlines()
    f.close()
    ###find total page number
    totalResult = re.findall('"totalResultCount":"[0-9]*"',lines[0])
    pagetemp = int(re.findall(r"[0-9]+",totalResult[0])[0])/100
    totalPage = int(pagetemp)
    if (isfloat(pagetemp)):
        totalPage += 1
    if (pageNum != totalPage+1):
        ###list possible price
        list_of_price = re.findall('"results":\[\S+\]',lines[0])
        prices = re.findall(r"[0-9]*\.[0-9]*",list_of_price[0])
        pid = re.findall(r"[0-9]{7,7}",list_of_price[0])
        prices = map(float,prices)
        pid = map(int,pid)
        index = 0
        currPrice = 0
        pastPrice = 0
        for i in prices:
            if i == currPrice:
                priceDict[currPrice].append(pid[index])
                index += 1
            else:
                pastPrice = currPrice
                currPrice = i
                priceDict[currPrice].append(pid[index])
                priceList.append(currPrice)
                index += 1
        ###query the new page
        '''pageNum += 1
        url = urlP1+fiftyUnder+urlP2+str(pageNum)+urlP3
        r = requests.get(url)
        while (r.status_code != 200):
            r = requests.get(url)'''

def print_price():
#For test purpose
    for price in priceDict:
        print price, ": "
        print priceDict[price]
    print priceList

def main():
    key = raw_input('Provide your zappo API key: \n')
    desireValue = int(raw_input('What is your desired total price?\n'))
    numItem = int(raw_input('How many present do you want?\n'))
    queryBound = ''
    fiftyUnder = '$50.00 and Under'
    hundredUnder = '$100.00 and Under'
    twoHunUnder = '$200.00 and Under'
    twoHunOver = '$200.00 and Over'
    
    if desireValue <= 50:
        queryBound = fiftyUnder
        test_query_price_list(queryBound,key) #for test purpose         
        #query_price_list(queryBound,key)
    elif desireValue > 50 and desireValue <= 100:
        queryBound = hundredUnder
        query_price_list(queryBound,key)
    elif desireValue >100 and desireValue <=200:
        queryBound = twoHunUnder
        query_price_list(queryBound,key)
    else:
        queryBound = twoHunOver
        query_price_list(queryBound,key)
        queryBound = twoHunUnder
        query_price_list(queryBound,key)

    #find the best result by considering all the possible results
    possible_comb = list(itertools.combinations(priceList,numItem))
    totalsum = 0
    mindiff = -1
    resultList = [] #resultList::list of price pair closest to desiredValue
    for it in possible_comb:
        for i in range(numItem):
            totalsum += it[i]
        diff = abs(totalsum-desireValue)
        if mindiff == -1:
            mindiff = diff
            resultList.append(it)
        elif mindiff > diff:
            mindiff = diff
            del resultList[0:len(resultList)]
            resultList.append(it)
        totalsum = 0
     
    ###print result, consider combination
    itemList = []   #itemList::list of list of pids corresponding to the satisfing price tuples
    looptime = 1
    looptimeArray = []
     
    #price = 0
    for it in resultList:
        #for each possible result(have same difference from desired price), 
        #find the item with same price and print them out
        for i in range(numItem):
            #price += it[i]
            itemPidList = priceDict[it[i]]  
                #priceDict::dictionary with price as key and list of items with same price as value
                #itemPidList::list of pids with same price
            itemList.append(itemPidList)
            looptimeArray.append(len(itemPidList))
            looptime *= len(itemPidList)
            itemPidList = []  #clear list
        #print "price: ",price ###test
        count = 0  #initialize final loop time
        index = [] #tuple of indices corresponding to the itemPidList stored in itemList
        printtuple = []  #all the tuple of item to be printed
        printresult = [] #tuple of item(represented as productid) to be printed

        #find all possible tuple of item (represented as their index in itemPidList)
        while (count < looptime):
            temp = count
            for i in range(numItem):
                index.append(temp%looptimeArray[i])
                temp = (temp-temp%looptimeArray[i])/looptimeArray[i]
            printtuple.append(index)
            index = []
            count += 1
            
        #print the productid tuple out
	print "Results are: "
        for it in printtuple:
            indexcount = 0
            for i in it: 
                printresult.append(itemList[indexcount][i])
                indexcount += 1
            print printresult
            del printresult[0:len(printresult)]
            
main()
