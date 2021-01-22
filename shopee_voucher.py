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

def Counter( page, sleep ) :
    # board index page
    url = "https://shopee.tw/api/v2/item/get_list"
    headers = {
        'accept': 'application/json',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-length': '137',
        'content-type': 'application/json',
        'cookie': '_fbp=fb.1.1552665128008.981231120; __BWfp=c1552665129419x123104093; _ga=GA1.2.248058245.1552665131; cto_lwid=efb33282-fdda-4228-8157-8e44df3858bf; SPC_F=rKPoFYmQczwoJx1wos1HDNdTv5WVOnJ5; REC_T_ID=4b029696-473a-11e9-b2ff-f8f21e1a07d2; csrftoken=uw4ktOuUYZR4vh0e7hUwBadXExl1torb; UYOMAPJWEMDGJ=; SPC_SC_SA_TK=; SPC_SC_SA_UD=; welcomePkgShown=true; django_language=zh-hant; __utmc=88845529; _hjid=0d600be7-3c58-4c7e-b7f5-269ae1267659; _fbc=fb.1.1567993394465.IwAR1j0NJiOMg57uxlXD2lDICfgWL4ThLDI9sLHmtnG8Mno1jxOzeXNu5dKTQ; SPC_RW_HYBRID_ID=26; _gcl_au=1.1.1721565245.1568267229; _gid=GA1.2.1929893142.1572240976; __utma=88845529.248058245.1552665131.1568013723.1572365789.11; __utmz=88845529.1572365789.11.8.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=https://shopee.tw/events3/code/2132536377/; language=zhHant; SPC_SI=gxevi6i6ghrxw5ew3uc2nck63i9g83q9; SPC_EC="4uMmmzLm8LxsQSNKRA2MuqXUia3/m+YayKRUzOAoRjfb59ifzp25peCToBnpDZx3irQjPg7fT0315nYGSDLeHZB9C2BQnFX/hnYMtjziaJoihhpfB0CTPqNDT5b9NQcNDFUaN7naPHMQo73J/XaVaKaG34xbwy+Y4MUrlEegVmk="; SPC_U=59215735; SPC_IA=1; SPC_SC_TK=1e4e9a4c349fd264cd917a1c3bea4458; SPC_SC_UD=59215735; AMP_TOKEN=%24NOT_FOUND; REC_MD_30_2000182595=1572971044; REC_MD_14=1572970605; REC_MD_30_2000182614=1572971378; REC_MD_30_2000182611=1572970916; REC_MD_20=1572970870; SPC_T_IV="6jSX2gTozwsL8/LO5+cyFw=="; SPC_T_ID="TYOmPo/sOWmM3bCEa1HLatBhxlWO1qAViF3JiaKlQN4HoFwYGHvU2Ln3RanP/o5SQn0Qw6QigZ/tMibMKXAmKSFfyd8GycFAfJLh/iuEzJI="',
        'dnt': '1',
        'if-none-match-': '55b03-38eb68c3dab6922eead66b0c681b7dac',
        'origin': 'https://shopee.tw',
        'referer': 'https://shopee.tw/m/live-stream-1',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36',
        'x-api-source': 'pc',
        'x-csrftoken': 'uw4ktOuUYZR4vh0e7hUwBadXExl1torb',
        'x-requested-with': 'XMLHttpRequest'
        }
    
    request_payload = {"item_shop_ids":[{"itemid":1547660542,"shopid":3006586},{"itemid":1315122233,"shopid":36493642},{"itemid":100363610,"shopid":10126068}]}
    
    request = requests.post( url , headers=headers, data=request_payload )
    soup = BeautifulSoup(request.text, 'html.parser')

    # https://shopee.tw/api/v2/microsite/campaign_site_page?url=live-stream-1&platform=pc

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