"""
句子迷-爬虫模块
负责爬取网页，并返回格式化数据并储存
版本号-0.1.0
"""

import requests
import time
import random
from bs4 import BeautifulSoup
import re


class Juzispider:
    """requests模块"""

    def __init__(self):
        # 爬虫模拟数据
        # 用户User-Agent头
        self.user_agent = "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 " \
                          "(KHTML, like Gecko) Chrome/27.0.1453.94 Safari/537.36"
        # 用户cookies
        self.cookies = "SESSfe7dc110f2d82eeddc336c4b4a78ec53=2pmr944j6tlo07iae3psqtmre4; " \
                       "xqrclbr=33013; _ga=GA1.2.1070900099.1595252957; " \
                       "Hm_lvt_99062fd40c87113b8be61ebc8113e7c2=1595252957; " \
                       "Hm_cv_99062fd40c87113b8be61ebc8113e7c2=1*login*PC-0!1*version*PC; " \
                       "xqrightqr=1; __cfduid=de73977d75dc2f4f080a9c447fa6537fb1598440760; " \
                       "visited=1; has_js=1; homere=3; " \
                       "xqrcli=MTYwMDg1OTkyOCwxNTM2Kjg2NCxXaW4zMixOZXRzY2FwZSwzMzAxMyw%3D; xqrclm=*516*"
        # 访问某些404网站时的代理
        self.proxies_url = 'http://127.0.0.1:10809'
        # 爬虫网站
        self.spider_url1 = r'https://www.mingyantong.com/'  # 名言通主页
        self.spider_url2 = r'https://his.sh/www.mingyantong.com/'  # 历史快照主页
        self.spider_url3 = r'http://www.shuoshuodaitupian.com/'  # 好句子迷主页

    # 以下为url爬取部分

    def juzispider_run(self, url, time_sleep=5, url_encoding='utf-8',
                       use_proxies='', not_use_cookies='', change_cookies=''):
        """
        负责爬取网页并返回相关爬取数据
        return-->tup(str, dir{str: str}, str) 返回一个元组，包括非空的爬取数据，包含在字典里的状态码和文本原因，和最终爬取的网站

        url-->str 爬取的网页
        time_sleep-->int 最小为5的爬取前等待时间
        url_encoding-->str 爬虫编码格式
        use_proxies-->str 传入则使用代理
        not_use_cookies-->str 传入则不使用cookies
        change_cookies-->str 自定义cookies
        """
        if not not_use_cookies:  # 使用cookies
            cookies = self.juzispider_cookies(change_cookies=change_cookies)
        else:  # 不使用cookies
            cookies = {}
        if not use_proxies:  # 不使用proxies
            proxies = {}
        else:  # 使用proxies
            proxies = {
                "http": self.proxies_url,
                "https": self.proxies_url,
            }
        headers = {'User-Agent': self.user_agent}
        if time_sleep < 5:
            time_sleep = 5
        time.sleep(random.uniform(time_sleep, time_sleep + 1))  # 爬虫等待
        spider_url = requests.get(url, headers=headers, cookies=cookies, proxies=proxies)
        spider_url.encoding = url_encoding
        if not spider_url.text:
            back_url = ''
        else:
            back_url = spider_url.text
        back_code_all = {spider_url.status_code: spider_url.reason}
        back_all = (back_url, back_code_all, spider_url.url)
        spider_url.close()
        return back_all

    def juzispider_cookies(self, change_cookies=''):
        """
        return-->dir 提供爬虫可用的cookies

        change_cookies-->str 防止cookies过期，不传入则使用默认cookies
        """
        if not change_cookies:
            cookies = self.cookies
        else:
            cookies = change_cookies
        cookies_dir = {}
        for i in cookies.split(';'):  # 按照字符：进行划分读取
            # 其设置为1就会把字符串拆分成2份
            name, value = i.strip().split('=', 1)
            cookies_dir[name] = value
        return cookies_dir

    # 以下为url构建部分
    def juzimake_url1(self, u_mode_1, u_mode_2=0, u_mode_str='', page='0'):
        """
        return-->str 构建并返回名言通网页

        u_mode_1,u_mode_2-->int 指定网页格式，其中u_mode_2默认为0
        u_mode_str-->str 指定网页具体类型，默认为空
        page-->str 翻页，默认为0

        网页格式说明：u_mode_1, u_mode_2, u_mode_str-介绍
        0，0，int-句子详情页
        0，1，int-句子详情页
        -暂缓-
        """
        url_add = ''
        if u_mode_1 == 0:  # 单个句子
            if u_mode_2 == 0:  # 句子详情页
                url_add = 'ju/' + u_mode_str
            elif u_mode_2 == 1:  # 包含此句子的句集
                url_add = 'jualbum/' + u_mode_str
        elif u_mode_1 == 1:  # 首页相关
            if u_mode_2 == 0:  # 推荐心语
                url_add = 'recommend/'
            elif u_mode_2 == 1:  # 今日热门
                url_add = 'todayhot/'
            elif u_mode_2 == 2:  # 最受欢迎
                url_add = 'totallike/'
        elif u_mode_1 == 2:  # 句集相关
            if u_mode_2 == 0:  # 精选句集
                url_add = 'albums'
            elif u_mode_2 == 1:  # 单个句集
                url_add = 'album' + u_mode_str
        elif u_mode_1 == 3:  # 中国名人名言
            use_tuple = ('先秦', '汉朝', '魏晋', '南北朝', '隋唐五代', '宋朝', '元朝', '明朝', '清朝', '近现代')
            url_add = 'dynasty/' + use_tuple[u_mode_2]
        elif u_mode_1 == 4:  # 外国名人名言
            use_tuple = ('美国', '英国', '法国', '德国', '日本', '俄国', '希腊', '罗马', '意大利', '奥地利', '印度')
            url_add = 'country/' + use_tuple[u_mode_2]
        elif u_mode_1 == 5:  # 句子类别
            if u_mode_2 == 0:  # 书籍名句
                url_add = 'books'
            elif u_mode_2 == 1:  # 电影台词
                url_add = 'allarticle/jingdiantaici'
            elif u_mode_2 == 2:  # 小说摘抄
                url_add = 'allarticle/zhaichao'
            elif u_mode_2 == 3:  # 散文美句
                url_add = 'allarticle/sanwen'
            elif u_mode_2 == 4:  # 动漫语录
                url_add = 'allarticle/dongmantaici'
            elif u_mode_2 == 5:  # 连续剧台词
                url_add = 'lianxujutaici'
            elif u_mode_2 == 6:  # 古文名句
                url_add = 'allarticle/guwen'
        elif u_mode_1 == 6:  # 句子类别下详情页
            if u_mode_2 == 0:  # 中国名人名言和外国名人名言
                url_add = 'writer/' + u_mode_str
            elif u_mode_2 == 1:  # 句子类别下其他
                url_add = 'article/' + u_mode_str
        elif u_mode_1 == 7:  # 详情和相似
            if u_mode_2 == 0:  # 作家详情页
                url_add = 'jianjie/' + u_mode_str
            elif u_mode_2 == 1:  # 类似作家
                url_add = 'leisi/' + u_mode_str
            elif u_mode_2 == 2:  # 作品详情页
                url_add = 'jianjiejieshao/' + u_mode_str
            elif u_mode_2 == 3:  # 相似作品
                url_add = 'xiangsi/' + u_mode_str
        if not url_add:
            url_back = ''  # 指定不存在返回的url为空
        else:
            url_back = self.spider_url1 + url_add
        if page != '0':
            url_back += f'?page={page}'
        return url_back

    def juzimake_url2(self, url):
        """
        构建并返回快照网页
        """
        url_back = self.spider_url2 + url[28:]
        return url_back

    def juzimake_url3(self):
        pass


class JuziBS:
    """BS模块"""
    def __init__(self):
        pass

    # 以下为快照处理方法
    def juziurl2_json(self, url_back):
        """
        快照处理
        """
        bs_back = BeautifulSoup(url_back, "lxml")
        bs_find = bs_back.body.find('script').string
        re_back = re.compile(r"doLoadKz\('.*',").findall(bs_find)
        doloadkz_list = []
        for i in re_back:
            doloadkz_list.append(i[10:-2])
        json_url_list, n = [], 0
        while n < 5:
            json_url = 'https://2tool.top/kz.php?s=' + doloadkz_list[n] + f'&num={n + 1}'
            json_url_list.append(json_url)
            n += 1
        return json_url_list

    def juziurl2_true_url(self, json_url_list):
        """
        真实的网站
        """
        i = 0
        true_url_list = []
        while i < 5:
            url_get = Juzispider().juzispider_run(json_url_list[i])[0]
            url_re = re.compile(r':".*"}').findall(url_get)
            if not url_re:
                true_url = ''
            else:
                true_url = url_re[0][2:-2]
            true_url_list.append(true_url)
            i += 1
        return true_url_list


if __name__ == '__main__':
    test1 = Juzispider()
    test2 = JuziBS()
    a = open('../01.html', encoding='UTF-8').read()
