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
    parser.add_argument("-t", "--topic", default='社會', dest = "topic", choices=['社會', '政治'], help = "Pass in a string.")
    parser.add_argument("-d", "--days", default=30, type=int, dest = "days", help = "Pass in a integer.")
    parser.add_argument("-s", "--sleep", default=1, type=float, dest = "sleep", help = "Pass in a float.")
    parser.add_argument("-p", "--page_id", default=None, dest = "page_id", help = "Pass in a string.")
    args = parser.parse_args()
    return args

def CtvWebCrawler( topic , days , page_id , sleep , docRecord ) :
    CTV_URL = 'http://new.ctv.com.tw/'
    
    dict = {}
    
    # get N days ago date
    NDaysAgo = datetime.now() - timedelta( days=days )
    lastDay = datetime.now()
    
    # index page
    url = CTV_URL + 'Category/' + topic + '?PageIndex=1'
    if page_id :
        url = CTV_URL + 'Category/' + topic + '?PageIndex=' + page_id
    
    try :
        isStop = False
        while not isStop :
            # get doc. link list from index page
            request = requests.get( url )
            soup = BeautifulSoup(request.text, 'html.parser')
            docList = soup.find("div", "search_result").find("div", "list").find_all("a")
            
            # get previous index page link
            pagesLinks = soup.find("div", "pager").find_all("a")
            if pagesLinks and pagesLinks[-1].get('href') :
                url = CTV_URL + pagesLinks[-1].get('href') 
            else :
                # this is the last page
                isStop = True
                
            # get all doc. info from index pages
            for i in range( len(docList) ) :
                # doc
                doc = docList[ i ]
                # git title & link
                title = doc.find("div", "title").text
                if '│' in title :
                    title = title[ : title.rindex('│') ]
                if title == 'Private video' :
                    # except case
                    continue ;
                link = CTV_URL + doc.get('href')
                print( link , title )
                
                postDay = doc.find( "div", "time" ).text
                postDay = datetime.strptime(postDay, "%Y/%m/%d")
                # check post date
                if postDay >= NDaysAgo :
                    lastDay = postDay
                    
                    # get doc. pages
                    request_doc = requests.get( link )
                    soup_doc = BeautifulSoup(request_doc.text, 'html.parser')
                    # document Content
                    paragraphs = soup_doc.find("div", "editor").find_all('div')
                    content = []
                    for p in paragraphs :
                        content.append( p.text.replace('\n','') )
                    content = ' '.join(content)
                    # print( content )
                    
                    # save title & content  
                    if checkDoc( title , docRecord ) :
                        dict[ title ] = {'content': content, 'link': link} 
                        print( "-------save title & content" )  
                        
                else : # when NDaysAgo > postDay
                    isStop = True
                    break ;
            # end for
            # wait time & run next index page
            time.sleep( sleep*60 ) ;
            
        # end while
    except Exception as e :
        print("Error fail : " , e )
    
    print( "end at page :" , url )
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
    if days < 0 :
        raise argparse.ArgumentTypeError('days exception, days should be a positive integer : '+days)
    if sleep < 0 :
        raise argparse.ArgumentTypeError('sleep exception, sleep should be a positive integer : '+sleep)
    if page_id and int(page_id) < 0 :
        raise argparse.ArgumentTypeError('page_id exception, page_id should be a positive integer : '+page_id)
    
    # get record doc.
    recordDir = os.path.join( runDir , 'CTV' )
    docRecord = getDocRecord( path = recordDir , filename = 'CTV_' )
    
    # get data
    newDict , lastDay = CtvWebCrawler( topic , days , page_id , sleep , docRecord )
    
    # get time
    today = datetime.now()
    filename = "CTV_" + topic + '_' + str(today.day)+'-'+str(today.month)+'-'+str(today.year) + '_' + str(lastDay.day)+'-'+str(lastDay.month)+'-'+str(lastDay.year)
    filename = os.path.join( recordDir , filename )
    
    if newDict :
        saveDict2Json( newDict , filename )
    else :
        print( "Not find Any relative Post!!!")