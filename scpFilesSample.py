import paramiko
import os
import scp
import shutil

# ssh = paramiko.SSHClient()
# ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# ssh.connect('123.56.142.113', username='admin', password='Ddt123_')
# scp = scp.SCPClient(ssh.get_transport())
# scp.get(remote_path='/opt/pentaho/kettle_scripts/spss/loop/monthreport_data_201607', local_path = 'data', recursive=True)

# scp.put(files = u'result/201607', remote_path='/opt/apache-tomcat-7.0.57/servers/bigDataReport_test/webapps/spss', recursive=True)


yearMonth = '201512'
dataDir = os.path.join(os.getcwd(), 'data', 'monthreport_data_%s'%yearMonth)

error_file_dir = os.path.join(dataDir, 'error')
done_file_dir = os.path.join(dataDir, 'done')

if not os.path.exists(error_file_dir):
    os.makedirs(error_file_dir)

if not os.path.exists(done_file_dir):
    os.makedirs(done_file_dir)


error_file = os.path.join(dataDir, 'spss_233_201512gbk.csv')
# shutil.move(error_file, error_file_dir)
shutil.rmtree(error_file_dir)