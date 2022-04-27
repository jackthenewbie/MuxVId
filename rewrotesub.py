def rewrote(filePath): #rewrote uncorrect format subtitles
    import re
    import itertools
    import os
    import shutil
    fileToRewrite=filePath
    basename=os.path.basename(fileToRewrite)
    def returnParentDir(filePath):
        listElementInFile=filePath.split('/')
        if(listElementInFile[-1]==''):
            listElementInFile.pop()
            return returnParentDir('/'.join(listElementInFile))
        if len(listElementInFile)<1:
            return None
        else:
            return '/'.join(listElementInFile[:-1])

    def getTimeandIndex(fileToRewrite): 
        with open(fileToRewrite, 'r') as f:
            lines=f.readlines()
            setNum=[]
            timeStamp=[]
            f.seek(0)
            for line in f:
                #print(line.strip())
                findNum=re.search(r'(\d+:\d).+\s+-->\s+(\d+:\d).+\n', line)
                if findNum:
                    timeStamp.append(line.strip())
            f.seek(0)
            for i in range(len(lines)):
                index=re.search("^[0-9]+$\n", lines[i])
                try:
                    af=re.search(r'(\d+:\d).+\s+-->\s+(\d+:\d).+\n', lines[i+1])
                except:
                    af=None
                if index and af:
                    setNum.append(lines[i].strip())
            setNum=list(set(setNum))
            setNum=sorted(setNum, key=int)
            print(len(setNum))
            print(len(timeStamp))
        f.close()
        try:
            if setNum[0]=='0' and len(setNum) > len(timeStamp):
                setNum.pop(0)
            elif setNum[0]=='0' and len(setNum) == len(timeStamp):
                setNum.pop(0)
                setNum.append(len(setNum))
        except:
            pass

        return (setNum, timeStamp)
    def getValidLine(fileToRewrite):
        subLineList=[]
        f=open(fileToRewrite, "r")
        lines=f.readlines()
        for i in range(len(lines)):
            lines[i].strip() #in order to avoid mistaking index only, we must include number in this line
            findSubline=re.search(r'^([a-zA-Z]+)|([0-9]+.+[a-zA-Z]+)|(\.+(\w)?)|(\d+)', lines[i].strip())
            prev=re.search(r'^(\d+:\d).+\s+-->\s+(\d+:\d).+\n', lines[i-1])
            if(findSubline and prev):
                subLineList.append(lines[i].strip())
        f.close()
        return subLineList
    temp=getTimeandIndex(fileToRewrite)
    setNum=temp[0]
    timeStamp=temp[1]
    subLineList=getValidLine(fileToRewrite)
    print(len(subLineList))
    if len(setNum)==len(timeStamp) and len(setNum)==len(subLineList):
        print("All is good")
        os.makedirs("./rewroteDumpSub/", exist_ok=True)
        dumpFile=open("./rewroteDumpSub/dump.srt", "w")
        for (a, b, c) in itertools.zip_longest(setNum, timeStamp, subLineList):
                print(a)
                dumpFile.write(f"{str(a).strip()}\n")
                print(b)
                dumpFile.write(f"{str(b).strip()}\n")
                print(c + "\n")
                dumpFile.write(f"{str(c).strip()}\n\n")
        dumpFile.close()
    print(fileToRewrite)
    os.remove(f"{fileToRewrite.strip()}")
    shutil.copy("./rewroteDumpSub/dump.srt", f"{fileToRewrite}")
    os.remove("./rewroteDumpSub/dump.srt")
    os.removedirs("./rewroteDumpSub/")
