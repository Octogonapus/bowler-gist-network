import requests as req
import re, urllib, os, shutil, sys
from bs4 import BeautifulSoup
from urllib.request import urlopen
sys.setrecursionlimit(3000)

if len(sys.argv) == 1:
    raise ValueError("Usage: python scraper.py <link>")
baseURL = sys.argv[1]

try:
    shutil.rmtree("bin")
except OSError:
    pass
os.mkdir("bin")

def convertToRaw(ghPretty):
    ghRaw = ghPretty
    if "github" in ghPretty:
        if "gist" not in ghPretty:
            ghRaw = ghPretty.replace("github.com/", "raw.githubusercontent.com/")[:-4]
            if "master" in sys.argv[1]:
                ghRaw += "/master/"
            else:
                ghRaw += "/dynamics/"
        elif "gist" in ghPretty:
             ghRaw = req.get(ghPretty).url
             soup = BeautifulSoup(urlopen(ghRaw), features="html.parser")
             ghRaw = "https://gist.githubusercontent.com" + soup.find('div', attrs={'class':'file-actions'}).find('a')['href']
        return ghRaw
    else:
        return "null"

def findGroovyUrls(link):
    r = req.get(link, allow_redirects=True)
    open("bin/" + link.split("/")[len(link.split("/"))-1] + ".tmp", 'wb').write(r.content)

    lines = []
    with open("bin/" + link.split("/")[len(link.split("/"))-1] + ".tmp", 'r') as f:
        for line in f:
            lines.append(line.split(" //")[0])
    os.remove("bin/" + link.split("/")[len(link.split("/"))-1] + ".tmp")

    with open("bin/" + link.split("/")[len(link.split("/"))-1], 'a') as f:
        for i in range(len(lines)):
            f.write(str(lines[i]))
            f.write("\n")
    
    with open("bin/" + link.split("/")[len(link.split("/"))-1], "r") as f:
        content = f.read()
        urls = (re.findall('\"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+\",\s+\"(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+\"', content))

    for i in range(len(urls)):
        urls[i] = "".join(urls[i].split())

    cleanURLS = []
    for i in range(len(urls)):
        cleanURLS.append(None)
        cleanURLS[i] = convertToRaw((urls[i].split(",")[0])[1:-1])
    
    for p in range(len(cleanURLS)):
        if cleanURLS[i] == "null":
            del cleanURLS[i]

    finalURL = []
    for i in range(len(cleanURLS)):
        finalURL.append(None)
        if "gist" in cleanURLS[i]:
            finalURL[i] = cleanURLS[i]
        else:
            finalURL[i] = cleanURLS[i] + urls[i].split(",")[1][1:-1]
    
    return finalURL

def findXMLUrls(link):
    r = req.get(link, allow_redirects=True)
    open("bin/" + link.split("/")[len(link.split("/"))-1] + ".tmp", 'wb').write(r.content)

    lines = []
    with open("bin/" + link.split("/")[len(link.split("/"))-1] + ".tmp", 'r') as f:
        for line in f:
            lines.append(line.split(" //")[0])
    os.remove("bin/" + link.split("/")[len(link.split("/"))-1] + ".tmp")

    with open("bin/" + link.split("/")[len(link.split("/"))-1], 'a') as f:
        for i in range(len(lines)):
            f.write(str(lines[i]))
            f.write("\n")
    
    with open("bin/" + link.split("/")[len(link.split("/"))-1], "r") as f:
        content = f.read()
        urls = (re.findall('<[git]+>http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+[\\r\\n]\s+<file>(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)) #+\",\s+\"(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+\

    for i in range(len(urls)):
        urls[i] = ",".join(urls[i].split("\n\n\t\t"))

    cleanURLS = []
    for i in range(len(urls)):
        cleanURLS.append(None)
        cleanURLS[i] = convertToRaw((urls[i].split(",")[0])[5:-6])
    
    for i in range(len(cleanURLS)):
        if cleanURLS[i] == "null":
            del cleanURLS[i]

    finalURL = []
    for i in range(len(cleanURLS)):
        finalURL.append(None)
        if "gist" in cleanURLS[i]:
            finalURL[i] = cleanURLS[i]
        else:
            finalURL[i] = cleanURLS[i] + urls[i].split(",")[1][6:-7]
    
    return finalURL

linksToVisit = []
linksVisited = [] 

def appendURLS(appensionItem, list):
    for i in range(len(appensionItem)):
        list.append(appensionItem[i])

linksToVisit.append(baseURL)
def recursiveSearch():
    if len(linksToVisit) > 0:
        if linksToVisit[0].split(".")[len(linksToVisit[0].split("."))-1] == "groovy" and linksToVisit[0] not in linksVisited:
            currentPlace = findGroovyUrls(linksToVisit[0])
            appendURLS(currentPlace, linksToVisit)
            linksVisited.append(linksToVisit[0])
            del linksToVisit[0]
        elif linksToVisit[0].split(".")[len(linksToVisit[0].split("."))-1] == "xml" and linksToVisit[0] not in linksVisited:
            currentPlace = findXMLUrls(linksToVisit[0])
            appendURLS(currentPlace, linksToVisit)
            linksVisited.append(linksToVisit[0])
            del linksToVisit[0]
        else:
            linksVisited.append(linksToVisit[0])
            print("DUPE OR UNSEARCHABLE - " + linksToVisit[0].split(".")[len(linksToVisit[0].split("."))-1] + " - " + linksToVisit[0])
            del linksToVisit[0]
        recursiveSearch()
    else:
        pass
    return(set(linksVisited))

files = recursiveSearch()
for f in files:
    r = req.get(f, allow_redirects=True)
    open("bin/" + f.split("/")[len(f.split("/"))-1], "wb").write(r.content)
print("Scan complete; check the bin folder for all files.")