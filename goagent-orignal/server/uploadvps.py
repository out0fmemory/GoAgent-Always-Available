#!/usr/bin/env python
# coding:utf-8

import sys
import sysconfig
import os
import glob
import getpass
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(asctime)s %(message)s', datefmt='[%b %d %H:%M:%S]')

def println(s, file=sys.stderr):
    assert type(s) is type(u'')
    file.write(s.encode(sys.getfilesystemencoding(), 'replace') + os.linesep)

sys.path = [(os.path.dirname(__file__) or '.') + '/../local/packages.egg/noarch'] + sys.path + [(os.path.dirname(__file__) or '.') + '/../local/packages.egg/' + sysconfig.get_platform().split('-')[0]]

_realgetpass = getpass.getpass
def getpass_getpass(prompt='Password:', stream=None):
    try:
        import msvcrt
    except ImportError:
        return _realgetpass(prompt, stream)
    password = ''
    sys.stdout.write(prompt)
    while True:
        ch = msvcrt.getch()
        if ch == '\b':
            if password:
                password = password[:-1]
                sys.stdout.write('\b \b')
            else:
                continue
        elif ch == '\r':
            sys.stdout.write(os.linesep)
            return password
        else:
            password += ch
            sys.stdout.write('*')
getpass.getpass = getpass_getpass


def upload(host, username, password):
    import paramiko
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
    logging.info('connect %s', host)
    client.connect(host, 22, username, password)
    client.exec_command('mkdir -p /opt/goagent/{vps,log}')
    logging.info('open sftp...')
    sftp = client.open_sftp()
    logging.info('open sftp ok')
    sftp.chdir('/opt/goagent/vps')
    uploadlist = ['../local/proxylib.py', 'vps/*']
    for filename in sum((glob.glob(x) for x in uploadlist), []):
        logging.info('upload %s', filename)
        sftp.put(filename, '/opt/goagent/vps/%s' % os.path.basename(filename))
    cmds = ['/bin/cp -f /opt/goagent/vps/sysctl.conf /etc/',
            '/bin/cp -f /opt/goagent/vps/limits.conf /etc/security/',
            '/bin/ln -sf /opt/goagent/vps/goagentvps.sh /etc/init.d/goagentvps',
            'chmod +x /opt/goagent/vps/goagentvps.sh',
            'which update-rc.d && update-rc.d goagentvps defaults'
            'which chkconfig && chkconfig goagentvps on'
            'sysctl -p']
    client.exec_command(' ; '.join(cmds))
    client.exec_command('/etc/init.d/goagentvps stop')
    client.exec_command('/etc/init.d/goagentvps start')


def main():
    host = raw_input('Host:')
    username = raw_input('Username[root]:') or 'root'
    password = getpass.getpass('Password:')
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    try:
        upload(host, username, password)
    except OSError:
        pass


if __name__ == '__main__':
    println(u'''\
===============================================================
 GoAgent 服务端部署程序, 开始上传 vps 应用文件夹
 Linux/Mac 用户, 请使用 python uploadvps.py 来上传应用
===============================================================

请输入您的主机名或 IP 地址:
        '''.strip())
    main()
    println(os.linesep + u'上传成功，请不要忘记编辑 proxy.ini 把你的 vps 服务端用户名密码填进去，谢谢。按回车键退出程序。')
    raw_input()
