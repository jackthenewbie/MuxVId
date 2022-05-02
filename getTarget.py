import argparse
from operator import index
import re
import subprocess
import os
import json
#---------Connect to mongoDB-----------------------------
import pymongo
def getParentDirName(filePath):
    listPath=filePath.split('/')
    if(listPath[len(listPath)-1]==''):
        listPath.pop()
        return getParentDirName('/'.join(listPath))
    return listPath[len(listPath)-1]
data = json.load(open('conf.json'))
client = pymongo.MongoClient(data['linkMongoDb'])
db=client[data['dbName']]
dest=data['folderTarget']
session=getParentDirName(dest)
collection=db[f'Session:{session}']
bracket=['[]','()']
vidType="{"+''.join(re.findall("\S" ,data['vidType']))+"}"
subType="{"+''.join(re.findall("\S" ,data['subType']))+"}"
cmdVideo = ['rclone', 'lsf', dest, '--files-only', '-R', '--include', f'*.{vidType}']
cmdSub = ['rclone', 'lsf', dest, '--files-only', '-R', '--include', f'*.{subType}']
cmdSubFileFirstDepth=['rclone', 'lsf', dest, '--files-only', '--include', f'*.{subType}']
def getListFile(cmd,fileout):
    with open(fileout, 'w') as out:
        return_code = subprocess.call(cmd, stdout=out)
#---------------------Finished generated list file-------------------------------------------------------------------------------------------------
def removeWithPrefix(filePath,postfix):
    fileNameWithoutExtension=os.path.splitext(os.path.basename(filePath))[0]
    search=re.search(f'_{postfix}$', fileNameWithoutExtension)
    if(not search):
        return filePath #if not found with postfix return original filePath
def returnParentDir(filePath):
    listElementInFile=filePath.split('/')
    if(listElementInFile[-1]==''):
        listElementInFile.pop()
        return returnParentDir('/'.join(listElementInFile))
    if len(listElementInFile)<1:
        return None
    else:
        return '/'.join(listElementInFile[:-1])
def returnListDir(listfiles):
    listDir=[]
    for file in listfiles:
        parentPathFile=returnParentDir(file)
        if parentPathFile==None:
            continue
        listDir.append(parentPathFile)  #Get file directory->list
    return listDir
def returnAllFiles(files):
    listfiles=[]
    for file in files.split('\n'):
        if removeWithPrefix(file,'mux')==file:
            listfiles.append(file)  #Get file directory->list
                                       
        #print(listElementInFile[:-1]) 
    #listfolders=list(set(listfolders))
    print(f"All file: {listfiles}")
    for file in listfiles:
        print(file)
    return listfiles
def isnumber(word):
    word=word.lower()
    if(word.isdigit()):
        return True
    else:
        return False
def removeWordInBracket(line):
    return re.sub(r'\([^)]*\)', '', line)
def removeWordInIgnore(searchNameTarget, customIgnoreWords):
    temp=[]
    for wordTarget in searchNameTarget:
        for word in customIgnoreWords:
            if wordTarget.strip() in word.strip():
                print(wordTarget)
                temp.append(wordTarget) #Get the words support to be ignore
    for word in temp:
        if word in searchNameTarget: #Remove word that should be ignore
            if word.isdigit():
                if int(word)<100:
                    continue
            searchNameTarget.remove(word)
    return searchNameTarget
def replaceSlash(path):
    if "//" in path:
        return replaceSlash(path.replace("//", "/"))
    return path
def listNumSmallerThan100(sub):
    numList=re.findall(r"\b\d+\b", sub)
    temp=[]
    for num in numList:
        print(num)
        if int(num)<100:
            temp.append(num)
    return temp
def isNumIn(num ,numList):
    if numList==[]:
        return False
    for numI in numList:
        if not numI.isdigit():
            return False
        if int(numI)==num:
            return True
    return False
def matchVideoAndSubtitle(filePath, subPath, bracketListIgnore=None):
    customIgnoreWords=['HEVC','BD','DBD', 'Webrip', 'BDRip', 'FLAC', "bluray", "BluRay"]
    fileNameWithoutExtension=os.path.splitext(os.path.basename(filePath))[0]
    subNameWithoutExtension=os.path.splitext(os.path.basename(subPath))[0]
    searchNameTarget=re.findall(r'\b([a-zA-Z]+|[0-9]+)\b', fileNameWithoutExtension)
    searchSeriesTarget=re.search(r'\b([sS][0-9]?[0-9][eE][0-9]?[0-9])\b', fileNameWithoutExtension)
    searchSeriesSub=re.search(r'\b([sS][0-9]?[0-9][eE][0-9]?[0-9])\b', subNameWithoutExtension)
    specialEncode=re.search(r'\b(h|H).?26[4-5]\b', fileNameWithoutExtension)
    #print(f"specialEncode: {specialEncode}")
    #Special encode removal
    if specialEncode!=None:
        temp=searchNameTarget
        for index in range(len(temp)):
            try:
                if searchNameTarget[index].lower()=='h' or searchNameTarget[index].lower()=='x'\
                    and searchNameTarget[index+1].lower()=='264' or searchNameTarget[index+1].lower()=='265':
                        print("Found encode info")
                        searchNameTarget=searchNameTarget[:index]+searchNameTarget[index+2:]
                        break
            except:
                continue
    #-----------------------------------------------------
    #Ignore words removal
    if bracketListIgnore!=None:
        for bracket in bracketListIgnore:
            toFind=f'\{bracket[0]}[^)]*\{bracket[1]}'
            searchWordInbracket=re.findall(toFind, fileNameWithoutExtension)
            if searchWordInbracket != None:
                print(f"Ignore: {searchWordInbracket}")
            customIgnoreWords.extend(searchWordInbracket)
    print(f"searchNameTarget: {searchNameTarget}")
    print(f"customIgnoreWords include: {customIgnoreWords}")
    if searchSeriesTarget!=None and searchSeriesSub!=None: #If series number is found
        print(f"searchSeriesTarget: {searchSeriesTarget.group()}")
    searchNameTarget=removeWordInIgnore(searchNameTarget, customIgnoreWords)
    
    print(f"searchNameTarget after ignore word: {searchNameTarget}")
    
    #print(f"searchNameTarget: {searchNameTarget}")
    #print(f"searchSeriesTarget: {searchSeriesTarget}")
    #print(f"searchSeriesSub: {searchSeriesSub}")
    if(fileNameWithoutExtension in subNameWithoutExtension):
        print(f"{fileNameWithoutExtension} in {subNameWithoutExtension}")
        return True
    elif(searchSeriesTarget!=None and searchSeriesSub!=None): #detech series
        def remove0(word):
            word=list(word)
            while c in word:
                if c=="0":
                    word.remove("0")
            return ''.join(word).upper().lower()
        countMatch=0
        seriesFromVideo=remove0(searchSeriesTarget.group())
        seriesFromSub=remove0(searchSeriesSub.group())
        if seriesFromVideo==seriesFromSub:
            countMatch+=1
        for word in searchNameTarget:
            #print(f"seriesFromVideo: {seriesFromVideo}")
            #print(f"seriesFromSub: {seriesFromSub}")
            #print(f"wordlower: {word.lower()}")
            #print(f"subNameWithoutExtensionLower: {subNameWithoutExtension.lower()}")
            if(word.lower() in subNameWithoutExtension.lower() 
                and seriesFromVideo == seriesFromSub ):
                countMatch+=1
        #print(f"countMatch: {countMatch}")
        if(float(countMatch*100/len(searchNameTarget))>=70):
            print(f"{fileNameWithoutExtension} in {subNameWithoutExtension}")
            return True
        #print(countMatch)
    else:
        tempNumInSub=listNumSmallerThan100(subNameWithoutExtension)
        for word in searchNameTarget:
            if word.isdigit():
               if isNumIn(int(word), tempNumInSub)==False: #Fix num 08 match with 1080p
                  return False
            if(word.lower() not in subNameWithoutExtension.lower()):
                print(f"{word} not in {subNameWithoutExtension}\n Not match")
                return False
        print(f"{fileNameWithoutExtension} in {subNameWithoutExtension}\n Input matched")
        return True
    return False
#getListFile(cmdSubFileFirstDepth, "currentSub.txt")
def generateDb():
    def generateSubDB(sub, startAt=0):
        subDB=[]
        for file in sub:
            file=replaceSlash(file)
            startAt+=1
            temp={"_id":startAt, "subtitle":file, "status":0}
            subDB.append(temp)
        return subDB
    def structureMux(index, sourceFile, destFile, subList):
        #fileNameWithoutExtension=os.path.splitext(os.path.basename(filePath))[0]
        #extensionWithDot=os.path.splitext(os.path.basename(sourceFile))[1]
        #fileVideoMuxed=f"{os.path.splitext(filePath)[0]}_{postfix}{extensionWithDot}" Full pat
        return {
            '_id': index,
            'sourceDir': f"{dest}/{sourceFile}",
            'destDir': f"{dest}/{destFile}",
            'sub': generateSubDB(subList),
            'delay': 0,
        }
    structureMuxMany=[]
    
    currentSub=open("list.txt", "r")
    count=0
    for line in currentSub:
        count+=1
        structureMuxMany.append(structureMux(count, line.strip(), line.strip(), sorted({"sub1","sub2","sub3"}) ))
    #collection.insert_many(structureMuxMany)        
#sourceV="/thisvideo/path.mp4"
#destV="/thisvideo/path_mux.mp4" #example
def generateMux(indexVid, indexSub, dest, sourceV, subList):
    def generateSubDB(sub, startAt=0):
        subDB=[]
        for file in sub:
            file=replaceSlash(file)
            startAt+=1
            temp={"_id":startAt, "subtitle":file, "status":0,'delay': 0}
            subDB.append(temp)
        return subDB
    sourceDir=replaceSlash(f"{dest}/{sourceV}")
    return {
        '_id': indexVid,
        'sourceDir': sourceDir,
        'destDir': "", #f"{dest}/{destFile}",
        'sub': generateSubDB(subList, indexSub),
        
    }
def theOnlyOneInFolder(currentV):
    def readFromFile(file):
        with file as f:
            return(f.read())
        
            
    count=0
    #listOfFile=readFromFile(currentV)
    for line in currentV:
        if(re.search('\w+', line.strip()) and count<=1):
            print(line.strip())
            count+=1
        else:
            break
    if count>1:
        return False
    return True
def returnLastIndexInCollection(collection):
    return collection.find().sort('_id', -1).limit(1)[0]['_id']
def returnLastIndexFromIndex(index, collection):
    return collection.find({'_id':index}, {'_id':0, 'sub':1})[0]['sub'][-1]['_id']
def getListFromFile(file):
    dict = {}
    count = 0
    for row in file:
        row=row.strip()
        count += 1
        if "//" in row:
            row = row.replace("//", "/")
        a = len(row)- len(row.split("/")[-1])-1
        if row[:(a+1)] in dict.keys():
            dict[row[:(a+1)]].append(row[(a+1):])
        else:
            dict.setdefault(row[:(a+1)], []).append(row[(a+1):])
    return dict
def isOnlyOne(list,folderKey):
    #print(list)
    count = 0
    for item in list:
        if folderKey in item:
            count=len(list[item])
    if count==1:
        return True
    else:
        return False
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-li', '--limit_search', type=int, default=0, help='limit search sub')
    args = parser.parse_args()
    db=[]
    getListFile(cmdVideo, "list.txt")
    currentV=open("list.txt", "r")
    try:
        lastVidIndexAt=returnLastIndexInCollection(collection)
    except:
        lastVidIndexAt=0
    count=lastVidIndexAt
    if count==None:
        count=0
    
    listKeyVid=getListFromFile(currentV)
    currentV.seek(0)
    for line in currentV:
        countMatch=0
        getAllSub=False
        subs=[]
        count+=1
        #print(f"Full path: \"{dest}/{returnParentDir(line.strip())}\"")
        fullPath=f"{dest}/{returnParentDir(line.strip())}"
        cmdFindSubFiles=['rclone', 'lsf', f"{dest}/{returnParentDir(line.strip())}", "--format", "p", '--files-only', '--include',  f'*.{subType}']
        os.makedirs("./dump", exist_ok=True)
        getListFile(cmdFindSubFiles, f"./dump/{count}.txt")
        if isOnlyOne(listKeyVid, returnParentDir(line.strip())):
            getAllSub=True
        for sub in open(f"./dump/{count}.txt"):
            if sub=="":
              continue
            if(getAllSub) is True:
                #print(f"{returnParentDir(line.strip())} is only one")
                subs.append(f"{fullPath}/{sub.strip()}")
                countMatch+=1
            elif(matchVideoAndSubtitle(line.strip(), sub.strip(), bracket)):
                print(f"{line.strip()} IS MATCHED {sub.strip()}")
                subs.append(f"{fullPath}/{sub.strip()}")
                countMatch+=1
            else:
                print(f"{line.strip()} NOT MATCHED {sub.strip()}")
            if (args.limit_search==0 and countMatch==1) or (args.limit_search>0 and countMatch==args.limit_search):
                break
        if subs != []:
            db.append(generateMux(count, 0, dest, replaceSlash(line.strip()), subs))
        else:
            print(f"This video: {line.strip()} has no subs")
        #print("\nSubs:",subs)
    print(f"\ndb: {db}")
    collection.insert_many(db)
main()
