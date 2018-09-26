import urllib
import urllib.request
from bs4 import BeautifulSoup
import re
import requests
from requests.exceptions import HTTPError
import random
from time import sleep

MATCH_CRITERIA = "&action=advanced&text=+![{B}]+![{W}]+![{R}]+![{G}]+[enters]+[the]+[battlefield]&format=+[\"Commander\"]&color=+@(+[C])&type=+[\"Artifact\"]+![\"Creature\"]"
NUMBER_OF_PAGES = 2

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

    sleep(random.uniform(2.8, 6.7))

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




urlTable = []

def buildURLTable(nextURL, numOfPages):
    baseurl = "http://gatherer.wizards.com/Pages/Search/Default.aspx?page="

    for x in range(0, numOfPages):
        fullstring = baseurl + str(x) + nextURL
        urlTable.append(fullstring)

#HERE WE START

buildURLTable(MATCH_CRITERIA, NUMBER_OF_PAGES)

stringofcards = "Card Name, Colors, CMC, Description, Price, URL"
count = 0
for url in urlTable:
    soup = make_soup(url)
    for record in soup.findAll("tr", {"class": "cardItem"}):

        cardTitle = record.findAll("span", {"class": "cardTitle"})

        colorElement = record.findAll("span", {"class": "manaCost"})
        color = getColors(colorElement[0])

        cardInfo = record.findAll("div", {"class": "cardInfo"})
        cmc = getCMC(cardInfo[0])

        description = record.findAll("div", {"class": "rulesText"})
        descriptionText = getDescription(description[0])

        set = record.findAll("td", {"class": "rightCol setVersions"})
        mtgurl, paperPrice = getURLFromSet(cardTitle[0].text, set[0])

        cardTitleString = cardTitle[0].text.replace(",", "")
        descriptionTextString = descriptionText.replace(",", "")
        stringofcards = stringofcards + cardTitleString + ", " + color + ", " + cmc + ", " + descriptionTextString + ", " + str(paperPrice) + ", " + mtgurl
        print(count)
        count = count + 1

f = open('cards.csv', 'w')
f.write(stringofcards)
f.close()


