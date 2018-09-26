import urllib
import urllib.request
from bs4 import BeautifulSoup
import re
import requests
from requests.exceptions import HTTPError
import random
from time import sleep
from tkinter import *
import re


def make_soup(url):

    try:
        r = requests.get(url)
        r.raise_for_status()
    except HTTPError:
        tendies = urllib.request.urlopen("http://arepublixchickentendersubsonsale.com/")
        tenders = BeautifulSoup(tendies, "html.parser")
        return tenders
    else:
        thepage = urllib.request.urlopen(url)
        work = BeautifulSoup(thepage, "html.parser")
        return work

def getColors(soupElement):

    colorstring = ""

    for colorX in soupElement.find_all('img', alt=True):
        if "White" in colorX['alt'] and "W" not in colorstring:
            colorstring = colorstring + "W"
        if "Blue" in colorX['alt'] and "U" not in colorstring:
            colorstring = colorstring + "U"
        if "Black" in colorX['alt'] and "B" not in colorstring:
            colorstring = colorstring + "B"
        if "Red" in colorX['alt'] and "R" not in colorstring:
            colorstring = colorstring + "R"
        if "Green" in colorX['alt'] and "G" not in colorstring:
            colorstring = colorstring + "G"
    if "W" not in colorstring and "U" not in colorstring and "B" not in colorstring and "R" not in colorstring and "G" not in colorstring:
        colorstring = "C"

    return colorstring

def getCMC(soupElement):

    cmcString = soupElement.findAll("span", {"class": "convertedManaCost"})

    return cmcString[0].text

def getDescription(soupElement):

    descriptionString = ""

    paragraphs = soupElement.findAll('p')

    for paragraph in paragraphs:
        descriptionString = descriptionString + paragraph.text + " "


    return descriptionString

def formatStringForURL(aString):
    newString = aString
    newString = newString.replace(",", "")
    newString = newString.replace(":", "")
    newString = newString.replace(".", "")
    newString = newString.replace(" ", "+")
    return newString

def getURLFromSet(name, soupElement):

    url = ""
    setFinal = ""
    paperPrice = 9999999.99

    baseurl = "https://www.mtggoldfish.com/price/"

    for set in soupElement.findAll("img"):
        setString = set.get('title')
        setString = re.sub("\s\(([^)]+)\)", "", setString)

        urlName = formatStringForURL(name)
        urlSet = formatStringForURL(setString)

        tryurl = baseurl + urlSet + "/" + urlName + "#paper"
        tryurl = tryurl.replace("\n", "")

        tempSoup = make_soup(tryurl)
        if(tempSoup.findAll("div", {"class": "price-box paper"})):
            for pPrice in tempSoup.findAll("div", {"class": "price-box paper"}):
                trueprice =  pPrice.findAll("div", {"class": "price-box-price"})
                priceFloat = float(trueprice[0].text)
                if(priceFloat < paperPrice):
                    paperPrice = priceFloat

    sleep(random.uniform(1.5, 3))

    for set in soupElement.findAll("img"):
        setString = set.get('title')
        setString = re.sub("\s\(([^)]+)\)", "", setString)

        urlName = formatStringForURL(name)
        urlSet = formatStringForURL(setString)

        tryurl = baseurl + urlSet + "/" + urlName + "#paper"
        tryurl = tryurl.replace("\n", "")

        tempSoup = make_soup(tryurl)
        if(tempSoup.findAll("div", {"class": "price-box paper"})):
            for pPrice in tempSoup.findAll("div", {"class": "price-box paper"}):
                trueprice =  pPrice.findAll("div", {"class": "price-box-price"})
                priceFloat = float(trueprice[0].text)
                if(priceFloat == paperPrice):
                    url = tryurl

    return (url, paperPrice)




#HERE WE START

urlTable = []

def runGeneration():
    stringofcards = "Card Name, Colors, CMC, Description, Price, URL"
    count = 0
    for url in urlTable:
        soup = make_soup(url)
        for cardRow in soup.findAll("tr", {"class": "cardItem"}):

            cardTitle = cardRow.findAll("span", {"class": "cardTitle"})

            colorElement = cardRow.findAll("span", {"class": "manaCost"})
            color = getColors(colorElement[0])

            cardInfo = cardRow.findAll("div", {"class": "cardInfo"})
            cmc = getCMC(cardInfo[0])

            description = cardRow.findAll("div", {"class": "rulesText"})
            descriptionText = getDescription(description[0])

            set = cardRow.findAll("td", {"class": "rightCol setVersions"})
            mtgurl, paperPrice = getURLFromSet(cardTitle[0].text, set[0])

            cardTitleString = cardTitle[0].text.replace(",", "")
            descriptionTextString = descriptionText.replace(",", "")
            stringofcards = stringofcards + cardTitleString + ", " + color + ", " + cmc + ", " + descriptionTextString + ", " + str(paperPrice) + ", " + mtgurl
            print(count)
            count = count + 1

    f = open('cardlist.csv', 'w')
    f.write(stringofcards)
    f.close()

def getPageCount(url, soup):
    searchTextElement = soup.findAll("span", {"id": "ctl00_ctl00_ctl00_MainContent_SubContent_SubContentHeader_searchTermDisplay"})
    searchText = searchTextElement[0].text
    p = re.compile('(?<=\()([0-9]+)(?=\))')
    integer = int(p.search(searchText).group(1))
    pagecount = 0;
    pagecount = int(integer/100 + 1)
    return pagecount

def buildURLTable(url, app):

    app.destroy()
    baseurl = 'http://gatherer.wizards.com/Pages/Search/Default.aspx?'

    if baseurl in url:

        pagesoup = make_soup(url)
        pagecount = getPageCount(url, pagesoup)

        appender = re.compile('(?<=action=advanced).*')
        toAppend = appender.search(url).group(0)

        for i in range(pagecount):
            urlTable.append(baseurl + 'page='+ str(i) +'&action=advanced' + toAppend)

        runGeneration()


from tkinter import *
from tkinter import filedialog

WINDOW_TITLE = "Goldfish Gatherer"

class Application():
    def __init__(self):
        #widget declarations and inits__________________________________________________________________________________
        #INITIAL IMPORT/EXPORT
        self.app = Tk()
        self.app.focus_set()
        self.app.title(WINDOW_TITLE)
        self.app.resizable(width=False, height=False)
        self.importPathL = Label(self.app, text="Enter Gatherer search URL:")
        self.importPathE = Entry(self.app, width=40)
        self.importB = Button(self.app, text="Get Priced List", command=lambda : buildURLTable(self.importPathE.get(), self.app))

        #widget grid placement__________________________________________________________________________________________
        #INITIAL IMPORT/EXPORT
        self.importPathL.grid( rowspan=1, padx=(10, 0), pady=(20,0))
        self.importPathE.grid(row=1, rowspan=1, padx=(20, 20), pady=5)
        self.importB.grid(row=2,column=0, padx=(40, 40), pady=20)

    def start(self):
        self.app.mainloop()

app = Application()
app.start()




