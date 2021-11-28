import winreg  # 和注册表交互
import re  # 正则模块
import subprocess  # 用于执行cmd命令
import os
import urllib.request  	# 发送http请求
import urllib.parse  	# 拼接url
import zipfile  		# 操作.zip文件  
from configparser import RawConfigParser
import sys

import threading
version_re = re.compile(r'^[1-9]\d*\.\d*.\d*')  # 匹配前3位版本号的正则表达式

absPath = os.getcwd() + "\\chromedriver.exe"
os.remove("chromedriver_win32.zip")

def getChromeVersion():
    try:
        #   从注册表中获得版本号
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Google\Chrome\BLBeacon')
        _v, type = winreg.QueryValueEx(key, 'version')

        print('Current Chrome Version: {}'.format(_v))  # 这步打印会在命令行窗口显示
        return version_re.findall(_v)[0]  # 返回前3位版本号

    except WindowsError as e:
        print('check Chrome failed:{}'.format(e))


def getDriverVersion(absPath):
    """
    :param absPath: chromedriver.exe的绝对路径
    """
    cmd = r'{} --version'.format(absPath)  # 拼接成cmd命令

    try:
        # 执行cmd命令并接收命令回显
        out, err = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        out = out.decode('utf-8')

        _v = out.split(' ')[1]  # 拆分回显字符串，获取版本号
        print('Current chromedriver Version:{}'.format(_v))
        return version_re.findall(_v)[0]
    except IndexError as e:
        print('check chromedriver failed:{}'.format(e))
        return 0


def get_ini(file):
    _ini = RawConfigParser()
    _ini.read(file, encoding='utf-8')
    return _ini


def checkVersionMatch():
    # 读取conf.ini中的配置项
    conf = get_ini('conf.ini')
    c_v = getChromeVersion()
    d_v = getDriverVersion(absPath)
    if c_v == d_v:
        # 若匹配，在命令行窗口提示下面的信息
        input('Chrome and chromedriver are matched. Press Enter to exit.')  # 若匹配，在命令行窗口提示下面的信息
    else:
        # 若不匹配，走下面的流程去下载chromedriver
        _v = c_v
        url = conf.get('driver', 'url')  # 从conf.ini中获取淘宝镜像url
        save_d = os.path.dirname(absPath)  # 下载文件的保存路径，与chromedriver同级
        downLoadDriver(_v, url, save_d)  # call下载文件的方法


def downLoadDriver(__v, url, save_d):
    # 访问淘宝镜像首页
    rep = urllib.request.urlopen(url).read().decode('utf-8')
    # '<a href="/mirrors/chromedriver/84.0.4147.30/">84.0.4147.30/</a>'
    directory = re.compile(r'>(\d.*?/)</a>').findall(rep)  # 匹配文件夹（版本号）

    # 获取期望的文件夹（版本号）
    match_list = []
    for i in directory:
        v = version_re.findall(i)[0]
        if __v == v:
            match_list.append(i)

    # http://npm.taobao.org/mirrors/chromedriver/83.0.4103.39/chromedriver_win32.zip
    dirUrl = urllib.parse.urljoin(url, match_list[-1])
    downUrl = urllib.parse.urljoin(dirUrl, 'chromedriver_win32.zip')  # 拼接出下载路径
    print('will download {}'.format(downUrl))

    # 指定下载的文件名和保存位置
    file = os.path.join(save_d, os.path.basename(downUrl))
    print('will saved in {}'.format(file))

    # 开始下载，并显示下载进度(progressFunc)
    urllib.request.urlretrieve(downUrl, file, progressFunc)

    # 下载完成后解压
    zFile = zipfile.ZipFile(file, 'r')
    for fileM in zFile.namelist():
        zFile.extract(fileM, os.path.dirname(file))
    zFile.close()

    input('Complete, press Enter to exit')

def progressFunc(blocknum, blocksize, totalsize):
    '''回调函数
    :blocknum: 已经下载的数据块
    :blocksize: 数据块的大小
    :totalsize: 远程文件的大小
    '''
    percent = 100.0 * blocknum * blocksize / totalsize
    if percent > 100:
        percent = 100
        downsize = blocknum * blocksize
        if downsize >= totalsize:
            downsize = totalsize
            s = "%.2f%%" % (percent) + "====>" + "%.2f" % (downsize / 1024 / 1024) + "M/" + "%.2f" % (totalsize / 1024 / 1024) + "M \r"
            sys.stdout.write(s)
            sys.stdout.flush()
    if percent == 100:
        print('')


if __name__ == '__main__':
    threading.Thread(target=checkVersionMatch, args=('')).start()