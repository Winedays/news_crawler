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

'''
How to get the date N days ago in Python : https://www.saltycrane.com/blog/2010/10/how-get-date-n-days-ago-python/
Python date string to date object : https://stackoverflow.com/questions/2803852/python-date-string-to-date-object
Python strptime() format directives : https://www.journaldev.com/23365/python-string-to-datetime-strptime
PTT 網路版爬蟲 : https://github.com/afunTW/ptt-web-crawler
Beautiful Soup 4.4.0 文档 : https://beautifulsoup.readthedocs.io/zh_CN/v4.4.0/index.html?highlight=extract
'''

def setArgument() :
    parser = ArgumentParser()
    parser.add_argument("-s", "--sleep", default=1, type=float, dest = "sleep", help = "Pass in a integer.")
    parser.add_argument("-p", "--page", default='https://www.ptt.cc/bbs/Lifeismoney/M.1571843967.A.457.html', dest = "page", help = "Pass in a string.")
    args = parser.parse_args()
    return args

def PttWebCrawler( page, sleep ) :
    # board index page
    url = page
    
    try :
        isStop = False
        while not isStop :
            
            # get doc. link list from index page
            request = requests.get( url, cookies={'over18': '1'} )
            soup = BeautifulSoup(request.text, 'html.parser')
            
            # document id
            # document title
                    
            # get Post Main Content, code clone form github 
            pushes = soup.find_all('div', class_='push')
            
            messages = []
            for i in range( len(pushes)-5 , len(pushes) ):
                push = pushes[ i ]
                if not push.find('span', 'push-content'):
                    continue
                # if find is None: find().strings -> list -> ' '.join; else the current way
                push_content = push.find('span', 'push-content').text
                print( push_content )
              
            print()
            # wait time & run next index page
            time.sleep( sleep ) ;
        # end while
    except Exception as e :
        print("Error fail : " , e )
    
    print( "end at page :" , url )
    return ;

if __name__ == "__main__" :  
    # set Argument
    args = setArgument()

    self = sys.argv[0]
    # read argument
    sleep = args.sleep
    page = args.page
    # check argument
    if sleep < 0 :
        raise argparse.ArgumentTypeError('sleep exception, sleep should be a positive integer : '+sleep)
    
    # get data
    PttWebCrawler( page, sleep )