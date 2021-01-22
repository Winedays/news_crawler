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
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.mime.multipart import MIMEMultipart

'''
How to get the date N days ago in Python : https://www.saltycrane.com/blog/2010/10/how-get-date-n-days-ago-python/
Python date string to date object : https://stackoverflow.com/questions/2803852/python-date-string-to-date-object
Python strptime() format directives : https://www.journaldev.com/23365/python-string-to-datetime-strptime
PTT 網路版爬蟲 : https://github.com/afunTW/ptt-web-crawler
Beautiful Soup 4.4.0 文档 : https://beautifulsoup.readthedocs.io/zh_CN/v4.4.0/index.html?highlight=extract
'''

def setArgument() :
    parser = ArgumentParser()
    parser.add_argument("-s", "--sleep", default=300, type=float, dest = "sleep", help = "Pass in a integer.")
    parser.add_argument("-p", "--page", default='https://www.ptt.cc/bbs/Lifeismoney/M.1566299724.A.9A1.html', dest = "page", help = "Pass in a string.")
    args = parser.parse_args()
    return args

def sendMail( url ) :
    
    mail_host = "smtp.gmail.com"
    mail_user = "adler.au@mirlab.org"
    mail_pass = "sspgps011014"
    sender = "shopee@shopee.com"
    receiver = "adler.au@mirlab.org" #, "adler011014@gmail.com" ]
    
    # mail massage
    msg = MIMEMultipart()
    msg['From'] = sender # "counter programe"
    msg['To'] = receiver # "test"
    msg['Subject'] = "Shopee 11/09 URL Find"
    body = "Shopee 11/09 URL!!!\n" + url
        
    msg.attach(MIMEText(body, 'plain'))
    # send mail
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(mail_user, mail_pass)
    text = msg.as_string()
    server.sendmail(msg['From'], msg['To'], text)
    server.quit()
    print( "Mail Send" )
    return ;

def Counter( page, sleep ) :
    # board index page
    url = "https://shopee.tw/api/v2/microsite/campaign_site_page?url=home-appliances-deals-1&platform=pc"
    # url = "https://shopee.tw/api/v2/microsite/campaign_site_page?url=lowest-price-guaranteed-sale-1&platform=pc"
    headers = { 'Content-Type': 'application/json', 'DNT': '1', 'Origin': 'https://play.shopee.tw', 
        'Referer': 'https://play.shopee.tw/milestone?campaigns=27' , 'Sec-Fetch-Mode': 'cors' , 
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36' , 
        'X-Tenant': 'TW' }
    
    urlList = ["https://shopee.tw/api/v2/microsite/campaign_site_page?url=11-11-11&platform=pc",
               "https://shopee.tw/api/v2/microsite/campaign_site_page?url=1111-1&platform=pc"]
    
    try :
        isStop = False
        while not isStop :
            
            for url in urlList :
                # get doc. link list from index page
                request = requests.get( url , headers=headers ) # 
                # soup = BeautifulSoup(request.text, 'html.parser')
                            
                # document id
                # document title
                data = json.loads( request.text )
                # counter = int(data["data"]["value"])
                print( "data :", data["data"], data["be_error"]  )
                
                if data["data"] or not data["be_error"] :
                    print( True )
                    sendMail( url )
                    isStop = True
                    
            sleep = 300
                
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
    Counter( page, sleep )
