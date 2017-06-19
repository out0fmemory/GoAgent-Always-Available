# GoAgent-Always-available
一直可用的GoAgent，会定时扫描可用的google gae ip，goagent为2015年5月份左右的源码 

## 重要： 最新版本已经更新了自动获取ip逻辑，可以不依赖git仓库上每日上传的ip文件了，大家可以更新代码，直接运行local文件夹下的proxy.py, 问题请发issues😆
## 重要： 由于公共的local翻墙客户端使用了有限的APP id，会导致大家用的多了出现只能访问谷歌，不能访问其他网址的问题，请自行更换成自己的 APPID！！
## 重要： 关于最新版本chrome（chrome58）提示“不是私密连接问题”，可以参考http://yanke.info/?id=57
## 重要： 增加历史所有扫描到的可用ip目录history_all_ips，有需要的搜集ip的同学可以自取
# 使用说明
0、若你想部署服务端  
直接下载源码，解压后进入server文件夹，按照操作执行脚本即可，注意要保持127.0.0.1:8087代理正常运行(可以按照下一条所述运行local下的代理)

1、若你是新手  
直接下载源码，解压后进入local文件夹，Windows系统直接打开GoAgent.exe，Mac os或者Linux系统直接运行proxy.py，开始全自动的翻墙吧，enjoys^_^

2、若你有自己的一套GoAgent以及布置好的服务端  
根据自己的ip地址下载对应的线路稳定可用ip地址文件，将内容复制替换goagent proxy.ini中hosts节或者iplist段中相应ip地址即可

3、若你有自己有扫描工具  
可以下载googleip.txt文件，其为为可用谷歌ip的地址列表，大约2w个ip，来源为我vpn扫描全部谷歌地址域得到，可靠性有保障，大家可以下载来自己用GoGoTest、GScan进行扫描！

4、若你想自己用gscan扫描  
直接下载源码，解压后使用gsan目录的工具即可扫描了，已经内置了可用ip列表大约1.6w ip

5、若只是想访问谷歌
直接访问我的镜像也可以，https://fanqiang.yanke.info/

# 工具引用
扫描工具引用自 https://github.com/moonshawdo/checkgoogleip ，thx.  
谷歌ip地址库引用自 https://github.com/peqing/GoogleIPRange ， thx.  
扫描工具gscan 引用自https://github.com/yinqiwen/gscan ，thx.  
部署工具引用自XX-NET https://github.com/XX-net/XX-Net/tree/master/code/default/gae_proxy/server ， thx.
