 # -*- coding: utf-8 -*-       <--------------采用utf-8
import io,sys,os,urllib2,shutil,time
# 全局变量
# 淘宝的接口是动态网页，不满足需求，改用chinaz
#GET_ISP_TYPE_URL = 'http://ip.taobao.com/ipSearch.php'
#GET_ISP_TYPE_URL = 'http://ip.chinaz.com/'
#站长之家抽风，暂时此地址不可用了
GET_ISP_TYPE_URL = 'http://ip.chinaz.com/getip.aspx'
#GET_ISP_TYPE_URL = 'http://www.123cha.com/ip/'
ISP_TYPE_DIANXIN = unicode('电信', "utf-8")
IPS_TYPE_TIETONG = unicode('铁通', "utf-8")
IPS_TYPE_YIDONG = unicode('移动', "utf-8")

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

# 从网络获取到的数据文件
NET_GSCAN_FILE = 'net_gsan_ip.txt'
GET_NET_IP_LIST_SEP = 60*60*10

# 获取运营商类型	
def getIpType():
	try:
		getIpurl = GET_ISP_TYPE_URL
		fd = urllib2.urlopen(getIpurl,timeout=5)
		Ipdata = fd.read()
		#print Ipdata
		#Ipdata = Ipdata.decode('utf-8').encode('gbk')
		ispType = ISP_TYPE_DIANXIN
		if IPS_TYPE_TIETONG in Ipdata:
			print "The Isp is TieTong"
			ispType = IPS_TYPE_TIETONG
		elif IPS_TYPE_YIDONG in Ipdata:
			print "The Isp is YiDong, use The TieTong Ips"
			ispType = IPS_TYPE_TIETONG
		elif ISP_TYPE_DIANXIN in Ipdata:
			print "The Isp is DianXin"
		else :
			print "The Isp is Others, use The Default DianXin Ips"
		fd.close()
		return ispType
	except Exception, e:
		print "The Isp is Others, use The Default DianXin Ips"
		return None

# 获取github上可用ip地址	
def getAvailableGoagentIp(ispType):
	try:
		# 下载github上的ip地址文件
		print "down Available Ip list from Github"
		url = GITHUB_DIANXIN_RAW_FILE
		if ispType == IPS_TYPE_TIETONG:
			url = GITHUB_TIETONG_RAW_FILE
		fd = urllib2.urlopen(url,timeout=5)
		content = fd.read()
		print 'Now Available Ip list:' + content
		fd.close()
		return content
	except Exception, e:
		return None

def getAvailableGoagentIpWithBackupSite(ispType):
	try:
		# 下载yanke.info上的ip地址文件
		print "down Available Ip list from yanke.info"
		url = BACKUP_SITE_DIANXIN_RAW_FILE
		if ispType == IPS_TYPE_TIETONG:
			url = BACKUP_SITE_TIETONG_RAW_FILE
		fd = urllib2.urlopen(url,timeout=10)
		content = fd.read()
		print 'Now Available Ip list:' + content
		fd.close()
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
				print "before replace " + GOOGLE_CN_TAG + line
				isInHostCn = 0
				line = HOSTS_TAG + ipList + '\n'
		elif isInHostHk == 1:
			if HOSTS_TAG in line and SEPIRATOR_TAG in line:
				print "before replace " + GOOGLE_HK_TAG + line
				isInHostHk = 0
				line = HOSTS_TAG  + ipList + '\n'
		out.write(line)
		line = inFile.readline()
	inFile.close()
	out.flush()
	out.close()
	shutil.copy(PROXY_PROP_TEM, PROXY_PROP)	
# 通过gscan获取可用ip
def gscanIp():
	#os.chdir(exe_path)
	os.system('cd gscan && gscan.exe -iprange="./my.conf"')
	fp = open('gscan\google_ip.txt','r')
	content = fp.readline()
   	fp.close
   	return content
# 获取文件修改时间
def getFileModifyTime(path):
	if path != None:
		ft = os.stat(path)
		return  ft.st_mtime
	return time.time()
# 获取第一次启动ip
def getFirstStartUpIp():
	if os.path.exists(NET_GSCAN_FILE) and time.time() - getFileModifyTime(NET_GSCAN_FILE) < GET_NET_IP_LIST_SEP:
		print 'use local ip_file because time short'
		fileIp = readIpFromFile(NET_GSCAN_FILE)
		if fileIp != None and len(fileIp) > 0:
			return fileIp
	print 'real get net ip_file'
	content = getAvailableIp()
	# 保存下载到的数据
	if content != None:
		print 'get net ip success, now save to files'
		saveIpToFile(content, NET_GSCAN_FILE)
	else:
		print 'get net ip fail, try to use the old file!'
		return readIpFromFile(NET_GSCAN_FILE)
	return content
def saveIpToFile(content, path):
	if content != None:
		file = open(path,"w+")
		file.write(content)
		file.flush()
		file.close
def readIpFromFile(path):
	if path != None:
		file = open(path)
		content = file.readline()
		file.close
		return content
	return None

# 获取已经扫描好的上传到github以及备用服务器的ip列表
def getAvailableIp():
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
		print 'get available Ip list fail'
	return ipList
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
		print 'get available Ip list fail'
		return
	localFileReplace(ipList)
	#启动goagent
	os.startfile(GOAGENT_EXE_FILE)
if __name__=="__main__": 
	startGoagentWithIpAutoGet()
