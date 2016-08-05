import sys
import os
import executeSpssScript as scr
from bs4 import BeautifulSoup


html = """
<html><head><title>The Dormouse's story</title></head>
<body>
<p class="title" name="dromouse"><b>The Dormouse's story</b></p>
<p class="story">Once upon a time there were three little sisters; and their names were
<a href="http://example.com/elsie" class="sister" id="link1"><!-- Elsie --></a>,
<a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and
<a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>;
and they lived at the bottom of a well.</p>
<p class="story">...</p>
"""

soup = BeautifulSoup(html)


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
