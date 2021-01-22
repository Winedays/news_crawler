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
    parser.add_argument("-t", "--topic", default='政治', dest = "topic", choices=['即時', '要聞', '政治'], help = "Pass in a string.")
    parser.add_argument("-d", "--days", default=7, type=int, dest = "days", help = "Pass in a integer.")
    parser.add_argument("-s", "--sleep", default=1, type=float, dest = "sleep", help = "Pass in a float.")
    parser.add_argument("-p", "--page_id", default=None, dest = "page_id", help = "Pass in a string.")
    args = parser.parse_args()
    return args

def UbnWebCrawler( topic , days , page_id , sleep , docRecord ) :
    UBN_URL = 'https://udn.com/'
    
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'}
    
    dict = {}
    
    # get N days ago date
    NDaysAgo = datetime.now() - timedelta( days=days )
    lastDay = datetime.now()
    
    # index page
    if not page_id :
        page_id = '1'
        
    if topic == '即時' :
        url = UBN_URL + '/news/get_breaks_article/' + page_id + '/1/0'
    elif topic == '要聞' :
        url = UBN_URL + '/rank/ajax_newest/2/6638/' + page_id
    elif topic == '政治' :
        url = UBN_URL + '/news/get_article/' + page_id + '/2/6638/6656'
    
    page_id = int( page_id ) # change str to int
    
    try :
        isStop = False
        while not isStop :
            # get doc. link list from index page
            request = requests.get( url , headers=headers )
            soup = BeautifulSoup(request.text, 'html.parser')
            docList = soup.find_all("dt", recursive=False)
            if not docList :
                # this is the last page
                isStop = True
                break ;
            
            # get previous index page link
            page_id += 1
            pagesLinks = ''
            if topic == '即時' :
                pagesLinks = UBN_URL + '/news/get_breaks_article/' + str(page_id) + '/1/0'
            elif topic == '要聞' :
                pagesLinks = UBN_URL + '/rank/ajax_newest/2/6638/' + str(page_id)
            elif topic == '政治' :
                pagesLinks = UBN_URL + '/news/get_article/' + str(page_id) + '/2/6638/6656'
            # pagesLinks = soup.find("div", "pagination boxTitle").find("a","p_next")
            if pagesLinks : # and pagesLinks.get('href') 
                url = pagesLinks
            else :
                # this is the last page
                isStop = True
                
            # get all doc. info from index pages
            for i in range( len(docList) ) :
                # doc
                doc = docList[ i ]
                # git title & link
                title = doc.find("h2").text.strip()
                link = doc.find("a").get('href')
                if not link.startswith( "http" ) :
                    link = UBN_URL + link
                print( link , title )
                
                # get doc. pages
                request_doc = requests.get( link , headers=headers )
                soup_doc = BeautifulSoup(request_doc.text, 'html.parser')
                
                # get post data
                if not soup_doc.find("div", "story_bady_info_author") :
                    continue ;
                postDay = soup_doc.find("div", "story_bady_info_author").find("span").text.strip()
                if '-' in postDay and ':' in postDay :
                    postDay = datetime.strptime(postDay, "%Y-%m-%d %H:%M")
                else :
                    postDay = NDaysAgo
                
                # check post date
                if postDay >= NDaysAgo :
                    lastDay = postDay
                    
                    # document Content
                    if not soup_doc.find("div", id="story_body_content") :
                        break ;
                    paragraphs = soup_doc.find("div", id="story_body_content").find_all('p')
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
    if page_id and page_id < 0 :
        raise argparse.ArgumentTypeError('page_id exception, page_id should be a positive integer : '+page_id)
    
    # get record doc.
    recordDir = os.path.join( runDir , 'UBN' )
    docRecord = getDocRecord( path = recordDir , filename = 'UBN_' )
    
    # get data
    newDict , lastDay = UbnWebCrawler( topic , days , page_id , sleep , docRecord )
    
    # get time
    today = datetime.now()
    filename = "UBN_" + topic + '_' + str(today.day)+'-'+str(today.month)+'-'+str(today.year) + '_' + str(lastDay.day)+'-'+str(lastDay.month)+'-'+str(lastDay.year) 
    filename = os.path.join( recordDir , filename )
    
    if newDict :
        saveDict2Json( newDict , filename )
    else :
        print( "Not find Any relative Post!!!")