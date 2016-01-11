# 谷歌可能ip列表更新
增加可能为可用谷歌ip的地址列表，大约1w个ip，来源为我 vpn扫描全部谷歌地址域得到，可靠性有保障，大家可以下载来自己用GoGoTest、GScan进行扫描！
# 好消息（15.11.05）
最近找到新的获取ip方法，能够获取到可用ip了，恢复更新中~~~~~
# 非常遗憾（15.11.04）
非常遗憾，目前几乎所有的gae都被qiang了，最近也没找到好的方法~~~给大家分享我的谷歌镜像吧，http://fq.yanke.info
# 非常重要（15.09.04）
你懂得，最近所有方法都扫不出可用谷歌ip了，连goagent原始项目作者都迫于压力删除项目了，我们需要其他方法了，any 想法可以发issuse
# 自动下载、替换ip、启动脚本
新增自动替换最新ip地址然后启动goagent脚本AutoGetIpAndStartGoagent.py，初版，大家有问题及时反馈>_< 使用时放入此文件到local目录，使用此文件作为启动入口即可
# GoAgent-Always-available
一直可用的GoAgent，会定时扫描可用的google gae ip，goagent会保持更新

# 使用说明
下载可用ip地址文件，将内容复制替换goagent proxy.ini中hosts节即可

# 工具引用
扫描工具引用自 https://github.com/moonshawdo/checkgoogleip ，thx.

谷歌ip地址库引用自 https://github.com/out0fmemory/GoogleIPRange， thx.


# 0422 Important说明
 引入稳定ip文件，里面的ip数量较少，但是稳定性很高，不会报APP Id Not Exist 或者经常出错，适合需要长时间稳定使用的场景。
 
# 0428 Improtant说明
 建议使用稳定ip列表的ip，里面的ip是相当稳定的
# 0517 说明
 发现自从这个项目发布后，可用的ip越来越少，现在经常扫不到ip，正在找方法解决了
# 0820 说明
 最近电信线路又基本不可用，正在解决中
