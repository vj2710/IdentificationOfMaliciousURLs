import csv
import re
import whois
import urllib2
import urllib
import pygeoip
import requests
import socket
from xml.dom import minidom
from urlparse import urlparse
from bs4 import BeautifulSoup
from datetime import date, time, datetime
import time

opener = urllib2.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]

noMatch = -1
truereturn=1
falsereturn=0

def getSoup(url):
    try:
        page = requests.get(url,allow_redirects=False)
        return BeautifulSoup(page.content, 'html.parser')
    except requests.exceptions.ConnectionError:
        return None
    except:
        return noMatch

def findTokens(url):
    if url == '':
        return [0, 0, 0]
    token_word = re.split('\W+', url)  # split on the basis of special characters
    no_ele = sum_len = largest = 0
    for ele in token_word:
        l = len(ele)
        sum_len += l
        if l > 0:  ## for empty element exclusion in average length
            no_ele += 1
        if largest < l:
            largest = l
    try:
        return [float(sum_len) / no_ele, no_ele, largest]
    except:
        return [0, no_ele, largest]

def hasIp(tokens):
    cnt=0;
    for token in tokens:
        if unicode(token).isnumeric():
            cnt+=1
        else:
            if cnt>=4 :
                return 1
            else:
                cnt=0;
    if cnt>=4:
        return 1
    return 0

def hasExeInURL(url):
    if url.find('.exe')!=-1:
        return 1
    return 0

def websiteRank(host):
    xmlpath = 'http://data.alexa.com/data?cli=10&dat=snbamz&url=' + host
    # print xmlpath
    try:
        xml = urllib2.urlopen(xmlpath)
        dom = minidom.parse(xml)
        hostRank = findTag(dom, 'REACH', 'RANK')
        countryWiseRank = findTag(dom, 'COUNTRY', 'RANK')
        return [hostRank, countryWiseRank]
    except:
        return [-2, -2]

def findTag(dom, ele, attribute):
    for subelement in dom.getElementsByTagName(ele):
        if subelement.hasAttribute(attribute):
            return subelement.attributes[attribute].value
    return noMatch

def getASN(host):
    try:
        # to look up the asn number
        g = pygeoip.GeoIP('GeoIPASNum.dat')
        urlASN=str(g.org_by_name(host).split()[0][2:])
        with open('ASNlist.txt') as ASNlist:
            if urlASN in ASNlist.read():
                return truereturn
        return falsereturn
    except:
        return noMatch

def getIframeCounts(soup):
    heightWidthNullCount = 0
    iframeInvisibleCount = 0
    try:
        iframe = soup.find_all('iframe')
        for i in iframe:
            if str(i.get('height')) == '0' or str(i.get('width')) == '0':
                heightWidthNullCount = heightWidthNullCount + 1
            if 'visibility:hidden' in str(i.get('style')).replace(" ", ""):
                iframeInvisibleCount = iframeInvisibleCount + 1
        return [heightWidthNullCount, iframeInvisibleCount]
    except:
        return [noMatch,noMatch]

def javascriptMethodsUsage(soup):
    usageCount=0
    suspectedMethods=['escape(', 'eval(', 'link(', 'unescape(', 'exec(', 'search(']
    try:
        script = soup.find_all('script')
        for i in script:
            for method in suspectedMethods:
                if method in str(i):
                    usageCount = usageCount + str(i).count(method)
        return usageCount
    except:
        return noMatch

def isIPMatched(url):
    name='none'
    try:
        name=socket.gethostbyaddr(socket.gethostbyname(url))
        if name=='none':
            return falsereturn
        else:
            return truereturn
    except socket.herror:
        return noMatch
    except:
        return noMatch

def getHTMLTagCount(soup):
    htmlTags = soup.find_all('html')
    return len(htmlTags)

def getLinkCount(soup):
    links=soup.find_all('a')
    return len(links)

def googleSafeBrowsing(url):
    key = "AIzaSyDI-_0KokkOegB0glCuRcRhS3x3LOXO5HA"
    client = "findURLStatus"
    appVer = "1.5.2"
    pver="3.1"
    req = {}
    req["client"] = client
    req["key"] = key
    req["appver"] = appVer
    req["pver"] = pver
    req["url"] = url
    try:
        params = urllib.urlencode(req)
        req_url = "https://sb-ssl.google.com/safebrowsing/api/lookup?"+params
        res = urllib2.urlopen(req_url)
        if res.code==204:
            return 0
        elif res.code==200:
            return 1
        return noMatch
    except:
        return noMatch

def getwhoisInfo(host):
    time.sleep(1)
    try:
        whois_info = whois.whois(host)
        if whois_info.creation_date:
            current_date = date.today()
            if type(whois_info.creation_date) == list:
                if type(whois_info.creation_date[0]) == datetime:
                    created_on = whois_info.creation_date[0].date()
                else:
                    return noMatch
            elif type(whois_info.creation_date) == datetime:
                created_on = whois_info.creation_date.date()
            else:
                return noMatch
            diff=current_date-created_on
            return diff.days / 365
        return noMatch
    except:
        return noMatch


FeatureRow={}
urlSet=[]
output=[]

hostName = []
indexPath = []

FeatureRow['noOfDots']=[]
FeatureRow['lengthOfURL']=[]
FeatureRow['lengthOfHost']=[]
FeatureRow['lengthOfPath']=[]
FeatureRow['avg_domain_token_length']=[]
FeatureRow['domain_token_count']=[]
FeatureRow['largest_domain']=[]
FeatureRow['avg_path_token']=[]
FeatureRow['path_token_count']=[]
FeatureRow['largest_path']=[]
FeatureRow['has_IP']=[]
FeatureRow['has_exe']=[]
FeatureRow['hostURLRank']=[]
FeatureRow['countryURLRank']=[]
FeatureRow['ASN']=[]
FeatureRow['iframeHeightWidth']=[]
FeatureRow['iframeInvisible']=[]
FeatureRow['suspectedMethodUsageCount']=[]
FeatureRow['IPMatched']=[]
FeatureRow['HTMLTagCount']=[]
FeatureRow['linkCount']=[]
FeatureRow['googleSafeBrowsing']=[]
FeatureRow['domainAge']=[]
FeatureRow['z_ouput']=[]

temp1 = []
temp2 = []

with open("dataset2.txt", "r") as URLFile:
# with open("C:/Users/Vasu/Desktop/machine_learning/Project_papers/dataset2.txt", "r") as URLFile:
    for line in URLFile:
        urlSet.append(line.split(',')[0])
        output.append(line.split(',')[1].rstrip('\n'))

for url in urlSet:
        urlParseObj = urlparse(url)
        hostName.append(urlParseObj.netloc)
        FeatureRow['googleSafeBrowsing'].append(googleSafeBrowsing(url))
        soup=getSoup(url)
        # detecting iframes
        if soup is None:
            FeatureRow['iframeHeightWidth'].append(noMatch)
            FeatureRow['iframeInvisible'].append(noMatch)
            # javascript suspected methods usage count
            FeatureRow['suspectedMethodUsageCount'].append(noMatch)
            # ip matched - returns true or false
            FeatureRow['HTMLTagCount'].append(noMatch)
            FeatureRow['linkCount'].append(noMatch)
        else:
            [heightWidthNullCount, iframeInvisibleCount]=getIframeCounts(soup)
            FeatureRow['iframeHeightWidth'].append(heightWidthNullCount)
            FeatureRow['iframeInvisible'].append(iframeInvisibleCount)
            # javascript suspected methods usage count
            FeatureRow['suspectedMethodUsageCount'].append(javascriptMethodsUsage(soup))
            # ip matched - returns true or false
            FeatureRow['HTMLTagCount'].append(getHTMLTagCount(soup))
            FeatureRow['linkCount'].append(getLinkCount(soup))

            # lexical features
            FeatureRow['lengthOfURL'].append(len(url))
            FeatureRow['lengthOfHost'].append(len(urlParseObj.netloc))
            FeatureRow['lengthOfPath'].append(len(urlParseObj.path))
            FeatureRow['noOfDots'].append(url.count('.'))
            avgLength, tokenCount, largestToken = findTokens(urlParseObj.netloc)
            FeatureRow['avg_domain_token_length'].append(avgLength)
            FeatureRow['domain_token_count'].append(tokenCount)
            FeatureRow['largest_domain'].append(largestToken)
            avgLength, tokenCount, largestToken = findTokens(urlParseObj.path)
            FeatureRow['avg_path_token'].append(avgLength)
            FeatureRow['path_token_count'].append(tokenCount)
            FeatureRow['largest_path'].append(largestToken)
            tokens = re.split('\W+', url)
            FeatureRow['has_IP'].append(hasIp(tokens))
            FeatureRow['has_exe'].append(hasExeInURL(url))

# calculating rank
hostRank = 0
countryRank = 0
for host in hostName:
    domain_Name = host.replace('www.', '')
    FeatureRow['domainAge'].append(getwhoisInfo(domain_Name))
    hostRank, countryRank = websiteRank(host)
    FeatureRow['hostURLRank'].append(hostRank)
    FeatureRow['countryURLRank'].append(countryRank)
    FeatureRow['ASN'].append(getASN(host))
    FeatureRow['IPMatched'].append(isIPMatched(host))

FeatureRow['z_ouput']=output
print(FeatureRow)

keys = sorted(FeatureRow.keys())
with open('testfile.txt','wb') as outfile:
   writer = csv.writer(outfile)
   writer.writerows(zip(*[FeatureRow[key] for key in keys]))

