import os
from os import path
import re
from functions import saveDict2Json , getAllFilesFromFolder

def readText( textFile ) :
    textRE = "(<[SOLNETI]>)|(\\ufeff)|(\\n)"
    f = open( textFile , 'r' , encoding = 'utf-8' ) 
    text = f.readline()
    f.close()
    text = re.sub( textRE , ' ' , text ).strip()
    return text 

if __name__ == "__main__" : 
    foldersPath = "/HDD/adler.au/NEWS/NER-PhA-Vol1/Train/data/"
    
    fileList = getAllFilesFromFolder( foldersPath , fileType = ".txt" )
    
    textDict = {}
    for file in fileList :
        print( file )
        text = readText( file )
        filename = path.basename( file )
        textDict[filename] = {'content' : text}
    # save file 
    os.system( "mkdir -p ./NER" )
    saveDict2Json( textDict , "./NER/ner_data" )