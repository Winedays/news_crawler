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
    parser.add_argument("-t", "--topic", default='politics', dest = "topic", choices=['all', 'politics', 'search'], help = "Pass in a string.")
    parser.add_argument("-d", "--days", default=7, type=int, dest = "days", help = "Pass in a integer.")
    parser.add_argument("-s", "--sleep", default=0, type=float, dest = "sleep", help = "Pass in a float.")
    parser.add_argument("-p", "--page_id", default=None, dest = "page_id", help = "Pass in a string.")
    args = parser.parse_args()
    return args

def LtnWebCrawler( topic , days , page_id , sleep , docRecord ) :
    LTN_URL = 'https://news.ltn.com.tw/'
    
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'}
    
    dict = {}
    
    # get N days ago date
    NDaysAgo = datetime.now() - timedelta( days=days )
    lastDay = datetime.now()
    
    # index page
    url = LTN_URL + 'list/breakingnews/' + topic + '/1'
    if page_id :
        url = LTN_URL + 'list/breakingnews/' + topic + '/' + page_id
        
    try :
        isStop = False
        while not isStop :
            # get doc. link list from index page
            request = requests.get( url , headers=headers )
            soup = BeautifulSoup(request.text, 'html.parser')
            docList = soup.find("div", "whitecon boxTitle").find("ul", "list imm").find_all("a","tit")
            
            # get previous index page link
            pagesLinks = soup.find("div", "pagination boxTitle").find("a","p_next")
            if pagesLinks and pagesLinks.get('href') :
                url = "https:" + pagesLinks.get('href') 
            else :
                # this is the last page
                isStop = True
                
            # get all doc. info from index pages
            for i in range( len(docList) ) :
                # doc
                doc = docList[ i ]
                # git title & link
                title = doc.find("p").text.strip()
                link = doc.get('href')
                if "https:" not in link :
                    link = "https:" + link
                print( link , title )
                
                postDay = doc.find("span").text.strip()
                if '-' not in postDay :
                    # post at today
                    today = date.today().strftime("%Y-%m-%d")
                    postDay = today + " " + postDay
                postDay = datetime.strptime(postDay, "%Y-%m-%d %H:%M")
                
                # check post date
                if postDay >= NDaysAgo :
                    lastDay = postDay
                    # get doc. pages
                    request_doc = requests.get( link , headers=headers )
                    soup_doc = BeautifulSoup(request_doc.text, 'html.parser')
                    # document Content
                    if not soup_doc.find("div", "text") :
                        break ;
                    paragraphs = soup_doc.find("div", "text").find_all('p',class_=None)
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


def LtnWebCrawlerSearch( topic , days , page_id , sleep , docRecord ) :
    LTN_URL = 'https://news.ltn.com.tw/'
    
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'}
    
    dict = {}
    
    # get N days ago date
    NDaysAgo = datetime.now() - timedelta( days=days )
    lastDay = datetime.now()
    
    # index page
    url = LTN_URL + 'search/?keyword=政治&page=1'
    if page_id :
        url = LTN_URL + 'search/?keyword=政治&page=' + page_id
        
    try :
        isStop = False
        while not isStop :
            # get doc. link list from index page
            request = requests.get( url , headers=headers )
            soup = BeautifulSoup(request.text, 'html.parser')
            docList = soup.find("div", "whitecon boxTitle").find("ul", "searchlist").find_all("li")
            
            # get previous index page link
            pagesLinks = soup.find("div", "pagination boxTitle").find("a","p_next")
            if pagesLinks and pagesLinks.get('href') :
                url = "https:" + pagesLinks.get('href') 
            else :
                # this is the last page
                isStop = True
                
            # get all doc. info from index pages
            for i in range( len(docList) ) :
                # doc
                doc = docList[ i ]
                # git title & link
                title = doc.find("a","tit").find("p").text.strip()
                link = LTN_URL + doc.find("a","tit").get('href')
                print( link , title )
                
                postDay = doc.find("span").text.strip()
                if '-' not in postDay :
                    # post at today
                    today = date.today().strftime("%Y-%m-%d")
                    postDay = today + " " + postDay
                if ':' not in postDay :
                    # post at today
                    postDay = postDay + " 23:59"
                postDay = datetime.strptime(postDay, "%Y-%m-%d %H:%M")
                
                # check post date
                if postDay >= NDaysAgo and 'politics' in link :
                    lastDay = postDay
                    # get doc. pages
                    request_doc = requests.get( link , headers=headers )
                    soup_doc = BeautifulSoup(request_doc.text, 'html.parser')
                    # document Content
                    if not soup_doc.find("div", "text") :
                        break ;
                    paragraphs = soup_doc.find("div", "text").find_all('p',class_=None)
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
    recordDir = os.path.join( runDir , 'LTN' )
    docRecord = getDocRecord( path = recordDir , filename = 'LTN_' )
    
    # get data
    if topic == 'search' :
        newDict , lastDay = LtnWebCrawlerSearch( topic , days , page_id , sleep , docRecord )
    else :
        newDict , lastDay = LtnWebCrawler( topic , days , page_id , sleep , docRecord )
    
    # get time
    today = datetime.now()
    filename = "LTN_" + topic + '_' + str(today.day)+'-'+str(today.month)+'-'+str(today.year) + '_' + str(lastDay.day)+'-'+str(lastDay.month)+'-'+str(lastDay.year)
    filename = os.path.join( recordDir , filename )
    
    if newDict :
        saveDict2Json( newDict , filename )
    else :
        print( "Not find Any relative Post!!!")
