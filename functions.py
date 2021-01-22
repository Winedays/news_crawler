import os
import re
import sys
import json

# check is doc. already download
def checkDoc( title , docList ) :
    if title in docList :
        return False ;
    return True ;
    
# get all doc. record in folder
def getDocRecord( path = './' , filename = '' ) :
    os.system( "mkdir -p " + path )
    path, dirs, files = next(os.walk( path ))
    files = [ os.path.join( path, file ) for file in files if file.startswith( filename ) and file.endswith('.json') ]
    titleList = []
    for file in files :
        f = open( file , 'r' , encoding='utf-8')
        dict = json.load( f )
        for title in dict.keys() :
            titleList.append( title )
        f.close()
    return titleList
    
# save file
def saveDict2Json( dict , filename ) :
    # save dict as a json
    f = open(filename+'.json', 'w', encoding='utf-8')
    json.dump(dict, f, ensure_ascii=False)
    f.close()
    return 
    
# get all folder in this path
def getFolderFromFolder( folder ) :
    folderList = [ os.path.join( folder , file ) for file in os.path.listdir(folder) if os.path.isdir( os.path.join(folder, file) ) ]
    return folderList

# get all file with type in this path
def getFilesFromFolder( folder , fileType = None ) :
    fileList = []
    if fileType :
        fileList = [ os.path.join( folder , file ) for file in os.listdir(folder) if os.path.isfile( os.path.join(folder, file) ) and file.endswith( fileType ) ]
    elif not fileType :
        fileList = [ os.path.join( folder , file ) for file in os.listdir(folder) if os.path.isfile( os.path.join(folder, file) ) ]
    return fileList 

# get all folder under this path
def getAllFolderFromFolder( folder ) :
    folderList = []
    for _path, dirs, files in os.walk( folder ) :
        for dir in dirs :
            dirpath = os.path.join( _path , dir )
            folderList.append( dirpath )
    return folderList
    
# get all files with type under this path
def getAllFilesFromFolder( folder , fileType = None ) :
    fileList = []
    for _path, dirs, files in os.walk( folder ) :
        for file in files :
            filepath = os.path.join( _path , file )
            if fileType and file.endswith( fileType ) :
                fileList.append( filepath )
            elif not fileType :
                fileList.append( filepath )
    return fileList 
    