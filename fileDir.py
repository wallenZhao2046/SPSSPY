#coding=gbk
import os

def getFilesInDir(rootDir):
    rootAbsDir = os.path.abspath(rootDir)
    print rootAbsDir
    fileList = []
    list_dirs = os.walk(rootDir)
    for root, dirs, files in list_dirs:
        for f in files:
            fileList.append(os.path.join(rootAbsDir, f))
    return fileList


