import sys
import os
import executeSpssScript as scr
# from bs4 import BeautifulSoup


# default input data dir is ./data
# default output file dir is ./result
dataDir = os.path.join(os.getcwd(), 'data')
outDir = os.path.join(os.getcwd(), 'result')

if len(sys.argv) == 2:
    dataDir = sys.argv[1]

if len(sys.argv) == 3:
    dataDir = sys.argv[1]
    outDir = sys.argv[2]

if not os.path.isabs(dataDir):
    dataDir = os.path.abspath(dataDir)

if not os.path.isabs(outDir):
    outDir = os.path.abspath(outDir)


print "input data dir %s" %dataDir
print "output file dir %s" %outDir


files = scr.getFilesInDir(dataDir)
for f in files:
    scr.execute(f, outDir)
