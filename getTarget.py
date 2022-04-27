import pymongo
import subprocess
import os
import json
data = json.load(open('conf.json'))
client = pymongo.MongoClient(data['linkMongoDb'])
db=client[data['dbName']]
dest=data['folderTarget']


def returnParentDir(filePath):
    listElementInFile=filePath.split('/')
    if(listElementInFile[-1]==''):
        listElementInFile.pop()
        return returnParentDir('/'.join(listElementInFile))
    if len(listElementInFile)<1:
        return None
    else:
        return '/'.join(listElementInFile[:-1])
def getParentDirName(filePath):
    listPath=filePath.split('/')
    if(listPath[len(listPath)-1]==''):
        listPath.pop()
        return getParentDirName('/'.join(listPath))
    return listPath[len(listPath)-1]

    count=0
    for line in open('dump.txt'): 
        if(line.strip()!=''):
            destNameWithoutExtension=os.path.splitext(os.path.basename(line.strip()))[0]
            print(f"sourceNameWithoutExtension: {sourceNameWithoutExtension}")
            print(f"destNameWithoutExtension: {destNameWithoutExtension}")
            if(sourceNameWithoutExtension in destNameWithoutExtension):
                count+=1
            if count>1:
                return True
    return False
session=getParentDirName(dest)
collection=db[f'Session:{session}']
session=getParentDirName(dest) #get session name down here
collection=db[f'Session:{session}']
def checkExist(destDir):
    #destNameWithoutExtension=os.path.splitext(os.path.basename(destDir))[0]
    cmdListFileInDir=['rclone', 'lsf', destDir]
    with open('dump.txt', 'w') as out:
        return subprocess.call(cmdListFileInDir, stdout=out)
def getValues():
    return collection.find({'destDir': {"$ne": ""}}, {'_id': 1,'destDir':1, 'sourceDir':1, 'sub':1 })
def checkMuxExistTotal(values): #Null destDir if destDir not exist
      markExist=False
      for doc in values:
        if checkExist(doc["destDir"]) != 0: #==0: exist and !=0: not exist
            print("Remove destDir, destDir not exist")
            collection.update_one( {'_id': doc['_id']}, {'$set': {'destDir': f''}} )
        else:
            print("------------------------Muxed file existed-----------------")
            print(session)
            collection.delete_one({'_id': doc['_id']})
            markExist=True
      return markExist
def checkSourceDirExist(values): #Delete session if sourceDir not exist
      for doc in values:
        if checkExist(doc["sourceDir"]) != 0: #==0: exist and !=0: not exist
            collection.delete_one({'_id': doc['_id']})
            return False
      return True
#print(checkMuxExist("oD_tutao:Course/LapTrinh/[ DevCourseWeb.com ] Udemy - MS SQL Server - Basics To Advanced//Get Your Files Here !/09 - PL SQL Final Session & Wind Up/001 PL SQL Final Session_en.srt"))

def checkSubExist(values):
      markExist=True
      for doc in values:
        for eachSub in doc['sub']:
            if checkExist(eachSub["subtitle"]) != 0: #==0: exist and !=0: not exist
                print("Try remove")#collection.delete_one({'_id': doc['_id']}, {'_id': eachSub['_id']})
                collection.update_one( { '_id': doc['_id'] },
                { '$pull': { "sub": { "subtitle":eachSub["subtitle"] } } } )
        if collection.find_one({'_id': doc['_id']}, {'sub': 1})['sub'] == []: #if sub is empty delete document
            collection.delete_one({'_id': doc['_id']})
            markExist=False
      return markExist
values=collection.find({'destDir': {"$ne": ""}, 'sub': {"$ne": []}}, {'_id': 1,'destDir':1, 'sourceDir':1, 'sub':1 }).limit(0)

checkMuxExistTotal(values)
