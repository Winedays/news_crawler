import os
from os import path
import re
import xml.etree.ElementTree as ET
from functions import saveDict2Json , getFilesFromFolder

# 用 ElementTree 在 Python 中解析 XML : https://pycoders-weekly-chinese.readthedocs.io/en/latest/issue6/processing-xml-in-python-with-element-tree.html

def readText( textFile , wordDict , textDict ) :
    invertChineseRE = "[^\u4e00-\u9fa5]"
    filename = path.basename( textFile )
    tree = ET.ElementTree(file=textFile)
    root = tree.getroot()
    print( textFile )
    
    # get text 
    for article in tree.iter(tag='article'):
        for elem in article.iter(tag='text'):
            textSeq = []
            for sentence in elem :
                if sentence.text :
                    sentenceText = sentence.text.split('\u3000')
                    for text in sentenceText :
                        if text.find('(') != -1 and text.find(')') != -1 :
                            word = text[ : text.rindex('(') ]
                            flag = text[ text.rindex('(')+1 : text.rindex(')') ]
                            if not re.search( invertChineseRE , word ) :
                                textSeq.append( word )
                                if word and word not in wordDict :
                                    wordDict[ word ] = {'flag': flag.lower(), 'count': 1}
                                elif word :
                                    wordDict[ word ]['count'] += 1
            textSeq = ' '.join( textSeq )
            textDict[ filename+'_'+article.attrib['no'] ] = {'content': textSeq}
    return wordDict , textDict

if __name__ == "__main__" : 
    foldersPath = "/HDD/adler.au/NEWS/中研院_平衡語料庫-ASBC4.0/"
    
    fileList = getFilesFromFolder( foldersPath , fileType = ".xml" )
    
    wordDict = {}
    textDict = {}
    for file in fileList :
        readText( file, wordDict , textDict )
    
    # save file 
    os.system( "mkdir -p ./ASBC" )
    saveDict2Json( textDict , "./ASBC/asbc_data" )
    saveDict2Json( wordDict , "./asbc_word" )