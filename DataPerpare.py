import json
import jieba
import os
from os import path
import re
import cn2an
import numpy as np
import monpa
from ckiptagger import data_utils, construct_dictionary, WS, POS, NER

def titleFormat( title , reDict ) :
    if re.search( reDict['invertChineseRE'], title ) :
        title = re.sub( reDict['invertChineseRE'] , ' ' , title ) # remove all word not chinese/number
    title = contentNumber2Chinese( title , reDict['numberRE'] )  # change point number 阿拉伯数字 => 中文数字
    title = title.replace( '0' , '' ) # remove the prefix '0' for same case like "01" , "07".... that the have not totally convert 
    title = re.sub( "[\s]{2,}" , ' ' , title ) # remove all space which more that 2 chars
    title = title.strip()
    
    # title cut word
    wordStr = ''
    if title :
        wordStr = ' '.join( [ word for word in jieba.cut(title) ] )  # jieba cut
        # wordStr = ' '.join( [ word for word in monpa.cut(title) ] )  # monpa cut
        # wordStr = ' '.join( ws( [title] ) )  # ckiptagger cut
        wordStr = re.sub( "[ ]{2,}" , ' ' , wordStr ) # remove space witch more that once
    return wordStr

def contentFormat( content , reDict , ws = None ) :
    if re.search( reDict['invertChineseRE'], content ) :
        content = contentNumber2Chinese( content , reDict['pointnumberRE'] )  # change point number 阿拉伯数字 => 中文数字
        content = re.sub( reDict['urlRE'] , ' ' , content ) # remove url link
        content = re.sub( reDict['datetimeRE'] , ' ' , content ) # remove datetime
        content = re.sub( reDict['invertChineseRE'] , ' ' , content ) # remove all word not chinese/number
    content = contentNumber2Chinese( content , reDict['numberRE'] ) # change number 阿拉伯数字 => 中文数字
    content = content.replace( '0' , '' ) # remove the prefix '0' for same case like "01" , "07".... that the have not totally convert
    content = re.sub( "[\s]{2,}" , ' ' , content ) # remove all space which more that 2 chars
    content = content.strip()
    
    # content cut word
    wordStr = ''
    if content :
        wordStr = ' '.join( [ word for word in jieba.cut(content) ] )  # jieba cut
        # wordStr = ""
        # for string in content.split() :
            # wordStr += ' '.join( [ word for word in monpa.cut(string) ] ) + ' ' # monpa cut
        # contentList = content.split()  
        # wordStr = ' '.join( ws( contentList )[0] )  # ckiptagger cut
        wordStr = re.sub( "[ ]{2,}" , ' ' , wordStr ) # remove space witch more that once
    
    return wordStr

def contentNumber2Chinese( content , numberRE ) :
    numbers = re.findall( numberRE, content )
    for index in np.argsort( [ float(number) for number in numbers ] )[::-1] :  #  'heapsort' in case of ['01','1'] can make '01' > '1' maybe base on FIFO
        number = numbers[ index ]
        chineseNumber = cn2an.an2cn(number, "low")
        chineseNumber = chineseNumber.replace( '点' , '點' ).replace( '亿' , '億' ).replace( '万' , '萬' )
        content = content.replace( number , chineseNumber ) 
    return content

def readDataFile( file ) :
    # load json file 
    filepath = path.join( folder , file )
    f = open( filepath , 'r' )
    docDict = json.load( f )
    f.close()
    return docDict ;

def saveCorpus( corpusList , savefile ) : 
    f = open( savefile , 'w' )
    for corpus in corpusList :
        f.write( corpus + '\n' )
    f.close()
    return ;

if __name__ == "__main__" : 
    folderList = ["CTV", "EBC", "LTN", "PTT", "UBN", "ETT", "CNA", "NER"]
    invertChineseRE = "[^\u4e00-\u9fa50-9 ]"
    urlRE = "[(?:http(s)?:\/\/)?[A-Za-z0-9.-]+(?:\.[A-Za-z0-9\.-]+)+(?:[A-Za-z0-9\-\._~:/?#\[\]@!\$&'\(\)\*\+,;=.]|[A-Za-z0-9]{2}%)+]*"
    datetimeRE = "[0-9]{2,4}[\/\-\.\|\\_~,:;&年](?:[0-9]{2}[\/\-\.\|\\_~,:;&月])?(?:[0-9]{2})?(?:日)?|[0-9]{5,8}" 
    numberRE = "[0-9]+(?:\.[0-9]+)?"
    pointnumberRE = "[^0-9\.]([0-9]+\.[0-9]+)[^0-9\.]"
    pttRE = "1.媒體來源|2.記者署名|3.完整新聞標題|4.完整新聞內文|1.新聞網址|2.新聞來源|3.新聞內容|4.附註、心得、想法|5.完整新聞連結|5.完整新聞連結 (或短網址):|6.備註"
    reDict = {'invertChineseRE': invertChineseRE, 'urlRE': urlRE, 'datetimeRE': datetimeRE, 'numberRE': numberRE, 'pointnumberRE': pointnumberRE, 'pttRE': pttRE}
    
    # load jieba dict.
    jieba.load_userdict("./dict.txt")
    # load ckiptagger model
    # modelPath = "/HDD/adler.au/NEWS/data/"
    # ws = WS( modelPath )
    # pos = POS( modelPath )
    # ner = NER( modelPath )
    
    corpusList = []
    # read all files
    for folder in folderList :
        _path, dirs, files = next(os.walk( folder ))
        for file in files :
            print( "run file " + file + "..." )
            # load json file 
            docDict = readDataFile( file )
            
            # get all doc.
            for key in docDict :
                title = key
                content = docDict[ key ][ "content" ]

                # title format 
                if file.startswith("PTT") :
                    title = ''
                else :
                    title = ''
                    # title = titleFormat( title , reDict )
                # content Format
                if file.startswith("PTT") :
                    content = re.sub( reDict['pttRE'] , '' , content ) # remove format
                content = contentFormat( content , reDict )
                
                # save title and content
                # if title :
                    # corpusList.append( title )
                if content :
                    chars = ""
                    for char in content :
                        chars += char + " "
                    corpusList.append( content )
                # print( title )
                # print( content )
                # print( docDict[ key ][ "link" ] )
                
                # exit;
          
    _path, dirs, files = next(os.walk( "ASBC" ))
    for file in files :
        print( "run file " + file + "..." )
        # load json file 
        filepath = path.join( "ASBC" , file )
        f = open( filepath , 'r' )
        docDict = json.load( f )
        f.close()
        
        # get all doc.
        for key in docDict :
            content = docDict[ key ][ "content" ]
            chars = ""
            for char in content :
                chars += char + " "
            corpusList.append( content )

    saveCorpus( corpusList , './corpus.txt' )
    
