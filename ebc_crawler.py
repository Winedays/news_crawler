import os
import re
import sys
import json
import argparse
from bs4 import BeautifulSoup
import requests  #使用requests套件的requests.get()方法
from datetime import datetime, timedelta
from argparse import ArgumentParser
import time
from functions import getDocRecord , checkDoc , saveDict2Json

def setArgument() :
    parser = ArgumentParser()
    parser.add_argument("-t", "--topic", default='Hot', dest = "topic", choices=['Hot', 'Realtime', 'politics'], help = "Pass in a string.")
    parser.add_argument("-s", "--sleep", default=1, type=float, dest = "sleep", help = "Pass in a float.")
    parser.add_argument("-p", "--page_id", default=None, dest = "page_id", help = "Pass in a string.")
    parser.add_argument("-d", "--days", default=30, type=int, dest = "days", help = "Pass in a integer.")
    args = parser.parse_args()
    return args

def EbcWebCrawler( topic, sleep , docRecord ) :
    EBC_URL = 'https://news.ebc.net.tw/'
    # https://news.ebc.net.tw/News/List_Category_Realtime?cate_code=society&page=5
    # https://news.ebc.net.tw/News/List_Category_Realtime?cate_code=society&exclude=171769%2C171768%2C171765%2C171764%2C171760&page=4&width=1111&layout=web
    dict = {}
    lastDay = datetime.now()
    
    # index page
    url = EBC_URL + topic + '?page=1'
    
    try :
        isStop = False
        while not isStop :
            # get doc. link list from index page
            request = requests.get( url )
            soup = BeautifulSoup(request.text, 'html.parser')
            docList = soup.find_all("div", "style1 white-box")
            
            # get previous index page link
            pagesLinks = soup.find("div", "page-area white-box").find_all("a", "white-btn")
            if pagesLinks and ( pagesLinks[-1].text == '＞' or pagesLinks[-1].text == '>' ):
                url = EBC_URL + pagesLinks[-1].get('href')
            else :
                # this is the last page
                isStop = True
            
            # get all doc. info from index pages
            for i in range( len(docList) ) :
                # doc
                doc = docList[ i ]
                # git title & link
                title = doc.find("div", "title").find('span').text
                link = EBC_URL + doc.find('a').get('href')
                print( link , title )
                
                postDay = doc.find("span","small-gray-text").text
                postDay = datetime.strptime(postDay, "%m/%d %H:%M")
                # check post date
                if postDay :
                    lastDay = postDay
                    
                # get doc. pages
                request_doc = requests.get( link )
                soup_doc = BeautifulSoup(request_doc.text, 'html.parser')
                # document Content
                paragraphs = soup_doc.find("div", "raw-style").find_all('p')
                content = []
                for p in paragraphs :
                    if not( p.text == '\xa0' or p.text == ' ' or p.text == "&nbsp;"  or "【東森新聞官網】一手掌握全世界" in p.text ) :
                        content.append( p.text )
                content = ' '.join(content)
                
                # save title & content  
                if checkDoc( title , docRecord ) :
                    dict[ title ] = {'content': content, 'link': link} 
                    print( "-------save title & content" )  
                # print( content )
            # end for
            # wait time & run next index page
            time.sleep( sleep*60 ) ;
            
        # end while
    except Exception as e :
        print("Error fail : " , e )
    
    print( "end at page :" , url )
    return dict , lastDay ;


def EbcWebCrawlerPolitics( topic, sleep , page_id , days , docRecord ) :
    EBC_URL = 'https://news.ebc.net.tw/'
    
    dict = {}
    NDaysAgo = datetime.now() - timedelta( days=days )
    lastDay = datetime.now()
        
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
        "accept": "text/html, */*; q=0.01", "accept-encoding": "gzip, deflate, br", "accept-language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "content-length": "98", "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "cookie": "__auc=6af8b9a516c6aaaab9e45d3def0; _ga=GA1.3.1904091057.1565157667; _ga=GA1.4.1904091057.1565157667; _fbp=fb.2.1565157666823.1796114008; __gads=ID=8e22b727adab5a25:T=1565157667:S=ALNI_Mb2RcWS1nLPSq0fZt0X00v4xNJaQg; NEWS_NEWS=172232,172129,172124,172203,171752,173738,173731,172221,172220,174798; __asc=c4315e3416d14090d86e0d0b028; _gid=GA1.3.1028777942.1567999202; _gid=GA1.4.1028777942.1567999202",
        "dnt": "1", "origin": "https://news.ebc.net.tw", "referer": "https://news.ebc.net.tw/News/politics", "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin", "x-requested-with": "XMLHttpRequest"
        }

    # index page
    if not page_id :
        page_id = '1'
        
    url = "https://news.ebc.net.tw/News/List_Category_Realtime" # EBC_URL + "News/" + topic 
    data={"cate_code": "politics", "page": page_id, "width": '1264', "layout": "web", "exclude": "177435,177419,177418,177411,177405"}
    
    try :
        isStop = False
        while not isStop :
            # get doc. link list from index page
            request = requests.post( url , headers=headers, data=data )
            soup = BeautifulSoup(request.text, 'html.parser')
            docList = soup.find_all("div", "style1 white-box")
            
            # get previous index page link
            pagesLinks = soup.find("div", "page-area white-box").find_all("a", "white-btn")
            if pagesLinks and ( pagesLinks[-1].text == '＞' or pagesLinks[-1].text == '>' ):
                data["page"] = pagesLinks[-1]['data-page']
            else :
                # this is the last page
                isStop = True
                
            # get all doc. info from index pages
            for i in range( len(docList) ) :
                # doc
                doc = docList[ i ]
                # git title & link
                title = doc.find("div", "title").find('span').text
                link = EBC_URL + doc.find('a').get('href')
                print( link , title )
                
                postDay = str(datetime.today().year) + '/' + doc.find("span","small-gray-text").text
                postDay = datetime.strptime(postDay, "%Y/%m/%d %H:%M")
                # check post date
                if postDay >= NDaysAgo :
                    lastDay = postDay
                    
                    # get doc. pages
                    request_doc = requests.get( link )
                    soup_doc = BeautifulSoup(request_doc.text, 'html.parser')
                    # document Content
                    paragraphs = soup_doc.find("div", "raw-style").find_all('p')
                    content = []
                    for p in paragraphs :
                        if not( p.text == '\xa0' or p.text == ' ' or p.text == "&nbsp;"  or "【東森新聞官網】一手掌握全世界" in p.text ) :
                            content.append( p.text )
                    content = ' '.join(content)
                    
                    # save title & content  
                    if checkDoc( title , docRecord ) :
                        dict[ title ] = {'content': content, 'link': link} 
                        print( "-------save title & content" )  
                    # print( content )
                else : # when NDaysAgo > postDay
                    isStop = True
                    break ;
            # end for
            # wait time & run next index page
            time.sleep( sleep*60 ) ;
            
        # end while
    except Exception as e :
        print("Error fail : " , e )
    
    print( "end at page :" , url , data )
    return dict , lastDay ;


if __name__ == "__main__" :  
    # set Argument
    args = setArgument()

    self = sys.argv[0]
    runDir , self = os.path.split(os.path.realpath(self))
    # read argument
    topic = args.topic
    sleep = args.sleep
    days = args.days
    page_id = args.page_id
    # check argument
    if sleep < 0 :
        raise argparse.ArgumentTypeError('sleep exception, sleep should be a positive integer : '+sleep)
    
    # get record doc.
    recordDir = os.path.join( runDir , 'EBC' )
    docRecord = getDocRecord( path = recordDir , filename = 'EBC_' )
    
    # get data
    if topic == "politics" :
        newDict , lastDay = EbcWebCrawlerPolitics( topic, sleep , page_id , days , docRecord )
    else :
        newDict , lastDay = EbcWebCrawler( topic, sleep , docRecord )
    
    # get time
    today = datetime.now()
    filename = "EBC_" + topic + '_' + str(today.day)+'-'+str(today.month)+'-'+str(today.year) + '_' + str(lastDay.day)+'-'+str(lastDay.month)+'-'+str(lastDay.year)
    filename = os.path.join( recordDir , filename )
    
    if newDict :
        saveDict2Json( newDict , filename )
    else :
        print( "Not find Any relative Post!!!")