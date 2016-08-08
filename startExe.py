import sys
import os
import time
import datetime
import paramiko
import scp
import executeSpssScript as scr
# from bs4 import BeautifulSoup


def prev_month(date):
    """Calculate the first day of the previous month for a given date.

        >>> prev_month(date(2004, 8, 1))
        datetime.date(2004, 7, 1)
        >>> prev_month(date(2004, 8, 31))
        datetime.date(2004, 7, 1)
        >>> prev_month(date(2004, 12, 15))
        datetime.date(2004, 11, 1)
        >>> prev_month(date(2005, 1, 2)
        datetime.date(2004, 12, 1)

    """
    return (date.replace(day=1) - datetime.timedelta(1)).replace(day=1)

## get month report input data


# yearMonth = time.strftime('%Y%m', time.localtime(time.time()))
last_month = prev_month(datetime.datetime.now())

yearMonth = last_month.strftime('%Y%m')
remote_path = '/opt/pentaho/kettle_scripts/spss/loop/monthreport_data_' + yearMonth

# get remote files through SSH
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

ssh.connect('123.56.142.113', username='admin', password='Ddt123_')

client = scp.SCPClient(ssh.get_transport())
client.get(remote_path=remote_path, local_path = 'data', recursive=True)

"""
default input data dir is ./data
default output file dir is ./result
"""

dataDir = os.path.join(os.getcwd(), 'data', 'monthreport_data_%s'%yearMonth)


print 'dataDir is %s'%dataDir
print 'all files are %r'%os.listdir(dataDir)


outDir = os.path.join(os.getcwd() , 'result')
outDir = os.path.join(outDir , yearMonth)

if not os.path.exists(outDir):
    os.makedirs(outDir)

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


client.put(files = u'result/201607', remote_path='/opt/apache-tomcat-7.0.57/servers/bigDataReport_test/webapps/spss', recursive=True)