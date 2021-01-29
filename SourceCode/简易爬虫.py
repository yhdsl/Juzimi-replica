import requests

use = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) App" \
      "leWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
use_all = {'User-Agent': use}

cookies = {}  # 初始化cookies字典变量
f = open(r'test.txt', 'r')  # 打开所保存的cookies内容文件
for line in f.read().split(';'):  # 按照字符：进行划分读取
    # 其设置为1就会把字符串拆分成2份
    name, value = line.strip().split('=', 1)
    cookies[name] = value  # 为字典cookies添加内容

url = r'www.google.com'
r = requests.get(url, proxies={}, headers=use_all)

print(r.text)
