 # -*- coding: gbk -*-       <--------------采用gbk
import io,sys,os,urllib2,shutil
# 全局变量
# 淘宝的接口是动态网页，不满足需求，改用chinaz
#GET_ISP_TYPE_URL = 'http://ip.taobao.com/ipSearch.php'
#GET_ISP_TYPE_URL = 'http://ip.chinaz.com/'
GET_ISP_TYPE_URL = 'http://ip.chinaz.com/getip.aspx'
ISP_TYPE_DIANXIN = '电信'
IPS_TYPE_TIETONG = '铁通'
# 电信可用ip文件
GITHUB_DIANXIN_RAW_FILE = 'https://raw.githubusercontent.com/out0fmemory/GoAgent-Always-Available/master/%E7%94%B5%E4%BF%A1%E5%AE%BD%E5%B8%A6%E9%AB%98%E7%A8%B3%E5%AE%9A%E6%80%A7Ip.txt'
BACKUP_SITE_DIANXIN_RAW_FILE = 'http://yanke.info/ip/dianxin_ip.txt'

# 铁通可用ip文件
GITHUB_TIETONG_RAW_FILE = 'https://raw.githubusercontent.com/out0fmemory/GoAgent-Always-Available/master/%E9%93%81%E9%80%9A%E5%AE%BD%E5%B8%A6%E9%AB%98%E7%A8%B3%E5%AE%9A%E6%80%A7Ip.txt'
BACKUP_SITE_TIETONG_RAW_FILE = 'http://yanke.info/ip/tietong_ip.txt'

# 网络请求重试次数
NET_RETRY_CNT = 3
PROXY_PROP = 'proxy.ini'
PROXY_PROP_BACKUP = 'proxy.bak'
PROXY_PROP_TEM = 'proxy.tem'
GOOGLE_CN_TAG = '[google_cn]'
GOOGLE_HK_TAG = '[google_hk]'
HOSTS_TAG = 'hosts = '
SEPIRATOR_TAG = '.'
GOAGENT_EXE_FILE = 'goagent.exe'
	
# 获取运营商类型	
def getIpType():
	try:
		getIpurl = GET_ISP_TYPE_URL
		fd = urllib2.urlopen(getIpurl)
		Ipdata = fd.read()
		Ipdata = Ipdata.decode('utf-8').encode('gbk')
		ispType = ISP_TYPE_DIANXIN
		if IPS_TYPE_TIETONG in Ipdata:
			print "运营商为" + IPS_TYPE_TIETONG
			ispType = IPS_TYPE_TIETONG
		elif ISP_TYPE_DIANXIN in Ipdata:
			print "运营商为" + ISP_TYPE_DIANXIN
		else :
			print "运营商为其他，默认使用电信"
		return ispType
	except Exception, e:
		return None

# 获取github上可用ip地址	
def getAvailableGoagentIp(ispType):
	try:
		# 下载github上的ip地址文件
		print "下载github上的可用ip"
		url = GITHUB_DIANXIN_RAW_FILE
		if ispType == IPS_TYPE_TIETONG:
			url = GITHUB_TIETONG_RAW_FILE
		fd = urllib2.urlopen(url,timeout=5)
		content = fd.read()
		print '可用ip列表：' + content
		return content
	except Exception, e:
		return None

def getAvailableGoagentIpWithBackupSite(ispType):
	try:
		# 下载yanke.info上的ip地址文件
		print "下载yanke.info上的可用ip"
		url = BACKUP_SITE_DIANXIN_RAW_FILE
		if ispType == IPS_TYPE_TIETONG:
			url = BACKUP_SITE_TIETONG_RAW_FILE
		fd = urllib2.urlopen(url,timeout=10)
		content = fd.read()
		print '可用ip列表：' + content
		return content
	except Exception, e:
		return None


def localFileReplace(ipList):
	# 先备份配置文件
	shutil.copy(PROXY_PROP, PROXY_PROP_BACKUP)
	# 查找并替换配置文件
	isInHostCn = 0
	isInHostHk = 0
	inFile = open(PROXY_PROP,"r")
	out = open(PROXY_PROP_TEM,"w")
	line = inFile.readline()
	while line:
		#print line
		if line.find(GOOGLE_CN_TAG) != -1:
			isInHostCn = 1
		elif line.find(GOOGLE_HK_TAG) != -1:
			isInHostHk = 1
		if isInHostCn == 1:
			if HOSTS_TAG in line and SEPIRATOR_TAG in line:
				print "替换前 " + GOOGLE_CN_TAG + line
				isInHostCn = 0
				line = HOSTS_TAG + ipList + '\n'
		elif isInHostHk == 1:
			if HOSTS_TAG in line and SEPIRATOR_TAG in line:
				print "替换前 " + GOOGLE_HK_TAG + line
				isInHostHk = 0
				line = HOSTS_TAG  + ipList + '\n'
		out.write(line)
		line = inFile.readline()
	inFile.close()
	out.flush()
	out.close()
	shutil.copy(PROXY_PROP_TEM, PROXY_PROP)	
# 总调	
def startGoagentWithIpAutoGet():
	i = 0
	ispType = None
	while i < NET_RETRY_CNT and ispType == None:
		ispType = getIpType()
		i = i + 1
	if ispType == None:
		ispType = ISP_TYPE_DIANXIN
	i = 0
	ipList = None
	while i < NET_RETRY_CNT and ipList == None:
		ipList = getAvailableGoagentIp(ispType)
		if ipList == None:
			ipList = getAvailableGoagentIpWithBackupSite(ispType)
		i = i + 1
	if ipList == None:
		print '获取可用ip失败'
		return
	localFileReplace(ipList)
	#启动goagent
	os.startfile(GOAGENT_EXE_FILE)
if __name__=="__main__": 
	startGoagentWithIpAutoGet()