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
    parser.add_argument("-b", "--board", default='HatePolitics', dest = "board", choices=['Gossiping', 'HatePolitics'], help = "Pass in a board name.")
    parser.add_argument("-d", "--days", default=30, type=int, dest = "days", help = "Pass in a integer.")
    parser.add_argument("-t", "--topic", default='新聞', dest = "topic", help = "Pass in a string.")
    parser.add_argument("-s", "--sleep", default=1, type=float, dest = "sleep", help = "Pass in a float.")
    parser.add_argument("-p", "--page_id", default=None, dest = "page_id", help = "Pass in a string.")
    args = parser.parse_args()
    return args

def PttWebCrawler( board, days, topic, page_id, sleep, docRecord ) :
    PTT_URL = 'https://www.ptt.cc'
    
    dict = {}
    
    # get N days ago date
    NDaysAgo = datetime.now() - timedelta( days=days )
    lastDay = datetime.now()
    
    # board index page
    url = PTT_URL + '/bbs/' + board + '/index.html'
    url = PTT_URL + '/bbs/' + board + '/search?page=1&q=新聞'
    if page_id :
        url = PTT_URL + '/bbs/' + board + '/index' + page_id + '.html'
        url = PTT_URL + '/bbs/' + board + '/search?page=' + page_id + '&q=新聞'
    
    #prepare data
    topicRE = '^\[([\u4e00-\u9fa5]+)\]'
    
    try :
        isStop = False
        while not isStop :
            
            # get doc. link list from index page
            request = requests.get( url, cookies={'over18': '1'} )
            soup = BeautifulSoup(request.text, 'html.parser')
            docList = soup.find_all("div", "r-ent")
            
            # get previous index page link
            pagesLinks = soup.find_all("a", "btn wide")
            url = PTT_URL + pagesLinks[1].get('href')
            
            # get all doc. info from index pages
            for i in range( len(docList)-1 , -1 , -1 ) :
                # doc
                doc = docList[ i ]
                # git title & link
                # check is post deleted
                if doc.find("div", "title").find('a') : 
                    title = doc.find("div", "title").find('a').text
                    link = PTT_URL + doc.find("div", "title").find('a').get('href')
                    # check doc.Topic
                    docTopic = re.findall( topicRE , title )
                    print( link , title )
                    topicCheck = True ;
                    if docTopic and topic and docTopic[0] != topic :
                        topicCheck = False
                    elif not docTopic :
                        topicCheck = False
                    if topicCheck :
                        # get doc. pages
                        request_doc = requests.get( link, cookies={'over18': '1'} )
                        soup_doc = BeautifulSoup(request_doc.text, 'html.parser')
                        # document page info.
                        headers = soup_doc.find_all( "div", "article-metaline" )
                        if len( headers ) != 3 :
                            # except case 
                            continue ;
                        postDay = headers[2].find( "span", "article-meta-value" ).text
                        postDay = datetime.strptime(postDay, "%a %b %d %H:%M:%S %Y")
                        # check post date
                        print( NDaysAgo, postDay )
                        if postDay >= NDaysAgo :
                            lastDay = postDay
                            
                            # document id
                            articleId = link[ link.rindex('/')+1 : link.rindex(".html") ]
                            # document title
                            title = re.sub( topicRE , '' , headers[1].find( "span", "article-meta-value" ).text ).strip()
                                    
                            # get Post Main Content, code clone form github 
                            content = soup_doc.find( "div", id="main-container" )
                            # remove meta nodes
                            metas = content.find_all( "div", "article-metaline" )
                            for meta in metas:
                                meta.extract()
                            metas = content.find_all( "div", "article-metaline-right" )
                            for meta in metas:
                                meta.extract()
                            # remove push nodes
                            pushes = content.find_all('div', class_='push')
                            for push in pushes:
                                push.extract()
                            # 移除 '※ 發信站:' (starts with u'\u203b'), '◆ From:' (starts with u'\u25c6'), 空行及多餘空白
                            # 保留英數字, 中文及中文標點, 網址, 部分特殊符號
                            filtered = [ v for v in content.stripped_strings if v[0] not in [u'※', u'◆'] and v[:2] not in [u'--'] ]
                            expr = re.compile(r'[^\u4e00-\u9fa5\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b\s\w:/\-_.?~%()]')
                            for i in range(len(filtered)):
                                filtered[i] = re.sub(expr, '', filtered[i])

                            filtered = [_f for _f in filtered if _f]  # remove empty strings
                            filtered = [x for x in filtered if articleId not in x]  # remove last line containing the url of the article
                            content = ' '.join(filtered)
                            # content = re.sub(r'(\s)+', '', content)
                            # remove change line & footer
                            content = content.replace( "\n\n" , ' ' )
                            content = content.replace( "\n" , '' )
                            content = content.replace( "本網站已依台灣網站內容分級規定處理。此區域為限制級，未滿十八歲者不得瀏覽。" , '' )
                            
                            # save title & content
                            if checkDoc( title , docRecord ) :
                                dict[ title ] = {'content': content, 'link': link}
                                print( "-------save title & content" )    
                            
                        else : # when NDaysAgo > postDay
                            isStop = True
                            break ;
                    else : # when docTopic false
                        continue ;
                else : # when post is delete
                    continue ;
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
    board = args.board
    days = args.days
    topic = args.topic
    sleep = args.sleep
    page_id = args.page_id
    # check argument
    if days < 0 :
        raise argparse.ArgumentTypeError('days exception, days should be a positive integer : '+days)
    if sleep < 0 :
        raise argparse.ArgumentTypeError('sleep exception, sleep should be a positive integer : '+sleep)
    
    # get record doc.
    recordDir = os.path.join( runDir , 'PTT' )
    docRecord = getDocRecord( path = recordDir, filename = 'PTT_'  )
    
    # get data
    newDict , lastDay = PttWebCrawler( board, days, topic, page_id, sleep, docRecord )
    
    # get time
    today = datetime.now()
    filename = 'PTT_' + board + '_' + str(today.day)+'-'+str(today.month)+'-'+str(today.year) + '_' + str(lastDay.day)+'-'+str(lastDay.month)+'-'+str(lastDay.year)
    filename = os.path.join( recordDir , filename )
    
    if newDict :
        saveDict2Json( newDict , filename )
    else :
        print( "Not find Any relative Post!!!")