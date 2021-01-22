import os
import re
import sys
import json
import argparse
from bs4 import BeautifulSoup
import requests  #使用requests套件的requests.get()方法
from datetime import datetime, timedelta, date
from argparse import ArgumentParser
import time
from functions import getDocRecord , checkDoc , saveDict2Json

def setArgument() :
    parser = ArgumentParser()
    parser.add_argument("-t", "--topic", default='政治', dest = "topic", choices=['search', '政治'], help = "Pass in a string.")
    parser.add_argument("-d", "--days", default=7, type=int, dest = "days", help = "Pass in a integer.")
    parser.add_argument("-s", "--sleep", default=1, type=float, dest = "sleep", help = "Pass in a float.")
    parser.add_argument("-p", "--page_id", default=None, type=int, dest = "page_id", help = "Pass in a string.")
    args = parser.parse_args()
    return args

def CnaWebCrawler( topic , days , page_id , sleep , docRecord ) :
    CNA_URL = 'https://www.cna.com.tw/'
    
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'}
    
    dict = {}
    
    # get N days ago date
    NDaysAgo = datetime.now() - timedelta( days=days )
    lastDay = datetime.now()
    
    # index page
    if not page_id :
        page_id = '1'

    page_id = int( page_id ) # change str to int
    api = ''
    if topic == '政治' :
        api = 'categorycode/aipl/'
    elif topic == 'search' :
        api = 'searchkeyword/%E6%94%BF%E6%B2%BB/' # 政治
    url = 'https://www.cna.com.tw/cna2018api/api/simplelist/' + api + 'pageidx/' + str(page_id) + '/'
    
    try :
        isStop = False
        while not isStop :
            # get doc. link list from index page
            request = requests.get( url , headers=headers )
            result = json.loads( request.text )
            # soup = BeautifulSoup(request.text, 'html.parser')
            docList = result[ "result" ][ "SimpleItems" ] # soup.find_all("div","piece clearfix")
            if not docList :
                # this is the last page
                isStop = True
                break ;
            
            # get previous index page link
            page_id = result[ "result" ][ "NextPageIdx" ]
            # pagesLinks = soup.find("div", "pagination boxTitle").find("a","p_next")
            if page_id : # and pagesLinks.get('href') 
                url = 'https://www.cna.com.tw/cna2018api/api/simplelist/' + api + 'pageidx/' + str(page_id) + '/'
            else :
                # this is the last page
                isStop = True
                
            # get all doc. info from index pages
            for i in range( len(docList) ) :
                # doc
                doc = docList[ i ]
                # git title & link
                title = doc["HeadLine"] # doc.find("h3").text.strip()
                link = doc["PageUrl"] # doc.find("a").get('href')
                className = doc["ClassName"]
                if not link.startswith( "http" ) :
                    link = CNA_URL + link
                print( link , title )
                
                # get post data
                postDay = doc["CreateTime"] # soup_doc.find("time", "date").text.strip()
                postDay = datetime.strptime(postDay, "%Y/%m/%d %H:%M")
                
                
                # check post date & class 
                if postDay >= NDaysAgo and className == "政治" :
                    lastDay = postDay
                
                    # get doc. pages
                    request_doc = requests.get( link , headers=headers )
                    soup_doc = BeautifulSoup(request_doc.text, 'html.parser')
                
                    # document Content
                    if not soup_doc.find("div", "paragraph") :
                        continue ;
                    paragraphs = soup_doc.find("div", "paragraph").find_all('p')
                    content = []
                    for p in paragraphs :
                        content.append( p.text.replace('\n','').strip() )
                    content = ' '.join(content)
                    # print( content )
                    
                    # save title & content  
                    if checkDoc( title , docRecord ) :
                        dict[ title ] = {'content': content, 'link': link} 
                        print( "-------save title & content" )  
                        
                elif NDaysAgo > postDay : # when NDaysAgo > postDay
                    isStop = True
                    break ;
            # end for
            # wait time & run next index page
            time.sleep( sleep*60 ) ;
            
        # end while
    except Exception as e :
        print("Error fail : " , e )
    
    print( "end at page :" , url )
    return dict, lastDay ;

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
    if days < 0 :
        raise argparse.ArgumentTypeError('days exception, days should be a positive integer : '+days)
    if sleep < 0 :
        raise argparse.ArgumentTypeError('sleep exception, sleep should be a positive integer : '+sleep)
    if page_id and page_id < 0 :
        raise argparse.ArgumentTypeError('page_id exception, page_id should be a positive integer : '+page_id)
    
    # get record doc.
    recordDir = os.path.join( runDir , 'CNA' )
    docRecord = getDocRecord( path = recordDir , filename = 'CNA_' )
    
    # get data
    newDict , lastDay = CnaWebCrawler( topic , days , page_id , sleep , docRecord )
    
    # get time
    today = datetime.now()
    filename = "CNA_" + topic + '_' + str(today.day)+'-'+str(today.month)+'-'+str(today.year) + '_' + str(lastDay.day)+'-'+str(lastDay.month)+'-'+str(lastDay.year)
    filename = os.path.join( recordDir , filename )
    
    if newDict :
        saveDict2Json( newDict , filename )
    else :
        print( "Not find Any relative Post!!!")