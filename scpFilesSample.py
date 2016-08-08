import paramiko
import scp

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

ssh.connect('123.56.142.113', username='admin', password='Ddt123_')
scp = scp.SCPClient(ssh.get_transport())
#scp.get(remote_path='/opt/pentaho/kettle_scripts/spss/loop/monthreport_data_201607', local_path = 'data', recursive=True)

scp.put(files = u'result/201607', remote_path='/opt/apache-tomcat-7.0.57/servers/bigDataReport_test/webapps/spss', recursive=True)
