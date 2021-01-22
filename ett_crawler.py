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
    parser.add_argument("-t", "--topic", default='政治', dest = "topic", choices=['社會', '政治'], help = "Pass in a string.")
    parser.add_argument("-d", "--days", default=7, type=int, dest = "days", help = "Pass in a integer.")
    parser.add_argument("-s", "--sleep", default=1, type=float, dest = "sleep", help = "Pass in a float.")
    parser.add_argument("-p", "--page_id", default=None, dest = "page_id", help = "Pass in a string.")
    args = parser.parse_args()
    return args

def EttWebCrawler( topic , days , page_id , sleep , docRecord ) :
    ETT_URL = 'https://www.ettoday.net/'
    
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'}
    
    dict = {}
    
    # get N days ago date
    NDaysAgo = datetime.now() - timedelta( days=days )
    lastDay = datetime.now()
    
    # index page
    if not page_id :
        page_id = '1'

    page_id = int( page_id ) # change str to int
    tFile = ''
    if topic == '社會' :
        tFile = '6.json'
    elif topic == '政治' :
        tFile = '1.json'
    url = 'https://www.ettoday.net/show_roll.php'
    data={'offset':page_id, 'tPage':2, 'tFile':tFile, 'tOt':0, 'tSi':24, 'tAr':0}
    
    try :
        isStop = False
        while not isStop :
            # get doc. link list from index page
            request = requests.post( url , headers=headers, data=data )
            soup = BeautifulSoup(request.text, 'html.parser')
            docList = soup.find_all("div","piece clearfix")
            if not docList :
                # this is the last page
                isStop = True
                break ;
            
            # get previous index page link
            page_id += 1
            data['offset'] = page_id
            # pagesLinks = ''
            # pagesLinks = soup.find("div", "pagination boxTitle").find("a","p_next")
            # if pagesLinks : # and pagesLinks.get('href') 
                # url = pagesLinks
            # else :
                # this is the last page
                # isStop = True
                
            # get all doc. info from index pages
            for i in range( len(docList) ) :
                # doc
                doc = docList[ i ]
                # git title & link
                title = doc.find("h3").text.strip()
                link = doc.find("a").get('href')
                if not link.startswith( "http" ) :
                    link = ETT_URL + link
                print( link , title )
                
                # get doc. pages
                request_doc = requests.get( link , headers=headers )
                soup_doc = BeautifulSoup(request_doc.text, 'html.parser')
                
                # get post data
                postDay = soup_doc.find("time", "date").text.strip()
                postDay = datetime.strptime(postDay, "%Y年%m月%d日 %H:%M")
                
                # check post date
                if postDay >= NDaysAgo :
                    lastDay = postDay
                    
                    # document Content
                    if not soup_doc.find("div", "story") :
                        continue ;
                    paragraphs = soup_doc.find("div", "story").find_all('p')
                    content = []
                    for p in paragraphs :
                        content.append( p.text.replace('\n','').strip() )
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
    if days < 0 :
        raise argparse.ArgumentTypeError('days exception, days should be a positive integer : '+days)
    if sleep < 0 :
        raise argparse.ArgumentTypeError('sleep exception, sleep should be a positive integer : '+sleep)
    if page_id and page_id < 0 :
        raise argparse.ArgumentTypeError('page_id exception, page_id should be a positive integer : '+page_id)
    
    # get record doc.
    recordDir = os.path.join( runDir , 'ETT' )
    docRecord = getDocRecord( path = recordDir , filename = 'ETT_' )
    
    # get data
    newDict , lastDay = EttWebCrawler( topic , days , page_id , sleep , docRecord )
    
    # get time
    today = datetime.now()
    filename = "ETT_" + topic + '_' + str(today.day)+'-'+str(today.month) + '_' + str(lastDay.day)+'-'+str(lastDay.month)
    filename = os.path.join( recordDir , filename )
    
    if newDict :
        saveDict2Json( newDict , filename )
    else :
        print( "Not find Any relative Post!!!")