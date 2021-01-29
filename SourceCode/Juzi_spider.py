"""
句子迷-爬虫模块
负责爬取网页，数据清洗，最后返回格式化的数据
版本号-0.2.8

重构于Juzi_spider_old，更改了爬虫部分的逻辑设计
"""

# ----------------------------------------------------------------------
#                      更新日志
# 2020/10/30 完成爬虫模块所有方法的编写和测试，BS模块由于顶层API的问题延后编写
# ----------------------------------------------------------------------

import requests
import time
import re
from bs4 import BeautifulSoup


class JuziSpider:
    """
    爬虫模块，负责网页的爬取，调用数据清洗模块，返回标准格式的数据
    由juzispider_main控制所有功能，并对外提供调用api

    主要功能：
    -网页爬取，可断点运行，能自动处理部分错误
    -提供不同的爬取逻辑
    -调用BS模块清洗数据
    """

    def __init__(self):
        # 爬虫伪装
        # --用户User-Agent头
        self.user_agent = "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 " \
                          "(KHTML, like Gecko) Chrome/27.0.1453.94 Safari/537.36"
        # --用户cookies-名言通网站
        self.cookies = "SESSfe7dc110f2d82eeddc336c4b4a78ec53=2pmr944j6tlo07iae3psqtmre4; " \
                       "xqrclbr=33013; _ga=GA1.2.1070900099.1595252957; " \
                       "Hm_lvt_99062fd40c87113b8be61ebc8113e7c2=1595252957; " \
                       "Hm_cv_99062fd40c87113b8be61ebc8113e7c2=1*login*PC-0!1*version*PC; " \
                       "xqrightqr=1; __cfduid=de73977d75dc2f4f080a9c447fa6537fb1598440760; " \
                       "visited=1; has_js=1; homere=3; " \
                       "xqrcli=MTYwMDg1OTkyOCwxNTM2Kjg2NCxXaW4zMixOZXRzY2FwZSwzMzAxMyw%3D; xqrclm=*516*"
        # 访问某些404网站时的代理url
        self.proxies_url = 'http://127.0.0.1:10809'
        # 预置的网站
        self.spider_url1 = r'https://www.mingyantong.com/'  # 名言通主页
        self.spider_url2 = r'https://his.sh/www.mingyantong.com/'  # 快照主页
        self.spider_url3 = r'http://www.shuoshuodaitupian.com/'  # 好句子迷主页
        # BS实例
        self.bs = JuziBS()
        # 爬虫爬取数据备份文件夹位置，由于逻辑文件取消开发
        self.spider_text_backup = 'Spider_Backup/'

    # 以下为爬虫核心部分

    def juzispider_run(self, url, sleep_time=3.0, new_cookie='', url_encoding='utf-8', unlock_mintime=False,
                       change_cookie=False, use_proxies=False):
        """
        负责爬取url，返回爬取的内容和爬取日志，不负责异常的处理
        return-->dir{'text': str 网页内容, 'url': str 爬取的url, 'code': int 状态码, 'reason': str 状态码的文本原因}

        url-->str 要爬取的网页
        sleep_time-->int或float 爬取前的休眠时间，默认为 3
        new_cookie-->str 新的cookie
        url_encoding-->str 网页解码格式，默认为utf-8
        unlock_mintime-->bool 为True时允许sleep_time小于 3
        change_cookie-->bool 为True时可以更换cookie
        use_proxies-->bool 为True时使用代理
        """
        headers = {'User-Agent': self.user_agent}  # 构建用户User-Agent头
        if sleep_time < 3:  # 构建等待时间
            if unlock_mintime:  # 解锁爬虫等待时间
                times = sleep_time
            else:
                times = 3
        else:
            times = sleep_time
        if change_cookie:  # 构建cookie
            cookies = new_cookie
        else:
            cookies = self.cookies
        cookies_dir = {}  # cookie为空时返回空字典
        if cookies != '':  # 构建cookie字典
            for i in cookies.split(';'):
                name, value = i.strip().split('=', 1)  # 按 = 分割字符
                cookies_dir[name] = value
        if use_proxies:  # 构建代理
            proxies = {"http": self.proxies_url, "https": self.proxies_url}
        else:
            proxies = {}
        time.sleep(times)  # 程序休眠
        url_get = requests.get(url=url, headers=headers, cookies=cookies_dir, proxies=proxies)
        url_get.encoding = url_encoding  # 指定编码格式
        spider_back_dir = {'text': url_get.text, 'url': url_get.url,
                           'code': url_get.status_code, 'reason': url_get.reason}
        # if url == r'https://www.mingyantong.com/recommend':  # 测试部分，伪造403异常，便于测试
        #     spider_back_dir = {'text': url_get.text, 'url': url_get.url,
        #                        'code': 403, 'reason': url_get.reason}
        return spider_back_dir

    # 以下为url构建部分，不涉及逻辑运行

    def juzimake_url1(self, u_mode_1, u_mode_2=-1, u_mode_str='', page='0'):
        """
        return-->str 构建并返回合法的名言通网页

        u_mode_1,u_mode_2-->int 指定网页格式，其中u_mode_2默认为-1,即无效网页
        u_mode_str-->str 指定网页具体类型，默认为空
        page-->str 翻页，默认为0，内容为真实的页数-1
        """
        url_add = ''  # 非法的模式时内容为空
        if u_mode_1 == 0:  # ---单个句子---
            if u_mode_2 == 0:  # 单个句子详情页
                url_add = 'ju/' + u_mode_str
            elif u_mode_2 == 1:  # 包含此句子的句集
                url_add = 'jualbum/' + u_mode_str
        elif u_mode_1 == 1:  # ---首页相关---
            if u_mode_2 == 0:  # 推荐心语
                url_add = 'recommend/'
            elif u_mode_2 == 1:  # 今日热门
                url_add = 'todayhot/'
            elif u_mode_2 == 2:  # 最受欢迎
                url_add = 'totallike/'
        elif u_mode_1 == 2:  # ---句集相关---
            if u_mode_2 == 0:  # 精选句集
                url_add = 'albums/'
            elif u_mode_2 == 1:  # 单个句集
                url_add = 'album/' + u_mode_str
        elif u_mode_1 == 3:  # ---中国名人名言---
            use_tuple = ('先秦', '汉朝', '魏晋', '南北朝', '隋唐五代', '宋朝', '元朝', '明朝', '清朝', '近现代')
            url_add = 'dynasty/' + use_tuple[u_mode_2]
        elif u_mode_1 == 4:  # ---外国名人名言---
            use_tuple = ('美国', '英国', '法国', '德国', '日本', '俄国', '希腊', '罗马', '意大利', '奥地利', '印度')
            url_add = 'country/' + use_tuple[u_mode_2]
        elif u_mode_1 == 5:  # ---句子类别---
            if u_mode_2 == 0:  # 书籍名句
                url_add = 'books/'
            elif u_mode_2 == 1:  # 电影台词
                url_add = 'allarticle/jingdiantaici/'
            elif u_mode_2 == 2:  # 小说摘抄
                url_add = 'allarticle/zhaichao/'
            elif u_mode_2 == 3:  # 散文美句
                url_add = 'allarticle/sanwen/'
            elif u_mode_2 == 4:  # 动漫语录
                url_add = 'allarticle/dongmantaici/'
            elif u_mode_2 == 5:  # 连续剧台词
                url_add = 'lianxujutaici/'
            elif u_mode_2 == 6:  # 古文名句
                url_add = 'allarticle/guwen/'
        elif u_mode_1 == 6:  # ---句子类别下详情页---
            if u_mode_2 == 0:  # 中国名人名言和外国名人名言
                url_add = 'writer/' + u_mode_str
            elif u_mode_2 == 1:  # 句子类别下其他
                url_add = 'article/' + u_mode_str
        elif u_mode_1 == 7:  # ---详情和相似---
            if u_mode_2 == 0:  # 作家详情页
                url_add = 'jianjie/' + u_mode_str
            elif u_mode_2 == 1:  # 类似作家
                url_add = 'leisi/' + u_mode_str
            elif u_mode_2 == 2:  # 作品详情页
                url_add = 'jianjiejieshao/' + u_mode_str
            elif u_mode_2 == 3:  # 相似作品
                url_add = 'xiangsi/' + u_mode_str
        if not url_add:
            url_back = ''  # 指定非法的模式返回的url为空
        else:
            url_back = self.spider_url1 + url_add
        if page != '0':  # 翻页
            url_back += f'?page={page}'
        return url_back

    def juzimake_url2(self, url, get_old=False):
        """
        return-->str 构建并返回名言通的快照url

        url-->str 发生错误时的名言通url
        get_old-->bool 是否获取http格式的url快照
        """
        if get_old:
            url_back = self.spider_url2 + url[28:]
        else:  # https格式的快照
            url_back = f"https://2tool.top/kuaizhao.php?k={url.replace(':', '%3A').replace('/', '%2F')}"
        return url_back

    def juzimake_url3(self):
        """
        暂定为好句子迷url构建部分
        """
        pass

    # 以下为爬虫异常处理部分

    def juzispider_error(self, url, sleep_time=3.0, new_cookie='', url_encoding='utf-8', unlock_mintime=False,
                         change_cookie=False, use_proxies=False, is_reerror=False):
        """
        处理爬虫爬取过程中可能出现的错误，便于逻辑方法处理
        return-->tuple(bool 是否出现异常, str 自定义的异常文本, int 状态码, str 爬取的url, str 爬取的网页内容)

        部分形参与juzispider_run相同
        is_reerror-->bool 标记是否正在自动处理异常，若为True则只有正常和-403两种返回状态
        """
        url_back = {'text': '', 'url': '', 'code': 404, 'reason': ''}  # 防止url_back不存在
        spider_text = ''  # 出现未捕获的异常时的返回数据
        url_code = url_back['code']
        try:  # 异常处理
            url_back = self.juzispider_run(url=url, sleep_time=sleep_time, new_cookie=new_cookie,
                                           url_encoding=url_encoding, unlock_mintime=unlock_mintime,
                                           change_cookie=change_cookie, use_proxies=use_proxies)
        except requests.exceptions.ConnectionError:  # Connection异常，包括网络异常，网页无响应
            spider_code = False
            spider_code_text = 'ConnectionError'
            spider_url = url_back['url']
        except requests.exceptions.MissingSchema:  # URL异常，可能为空url
            spider_code = False
            spider_code_text = 'UrlError'
            spider_url = url_back['url']
        else:
            url_code = url_back['code']
            if url_code >= 400:  # 状态码异常
                spider_code = False
                spider_code_text = 'CodeError'
                spider_url = url_back['url']
            else:  # 一切正常
                spider_code = True
                spider_text = url_back['text']
                spider_code_text = 'OK'
                spider_url = url_back['url']
        if is_reerror and (not spider_code):  # 正在自动处理异常且再次触发异常
            spider_back = (False, '-403Error', f'-403+{spider_code_text}+{url_code}', spider_url, spider_text)
        else:
            spider_back = (spider_code, spider_code_text, url_code, spider_url, spider_text)
        return spider_back

    def juzispider_re403(self, spider_url_tup):
        """
        负责处理403异常，返回真实的快照url
        return-->dir{'str url列表中的某个url': dir{'str 快照id': str 快照的url}}

        spider_url_tup-->tuple 由juzispider_main运行过程中生成的url合集元组

        快照id:
        1-百度快照
        2-搜狗快照
        3-360快照
        4-bing快照
        5-谷歌快照-需要启用代理
        """
        api_text_list = []
        true_urls_dir = {}
        for url in spider_url_tup:  # 快照url列表
            url2 = self.juzimake_url2(url)
            url2_text = self.juzispider_main(main_mode=-1, url=url2, change_cookie=True, is_reerror=True,
                                             unlock_mintime=True, sleep_time=2)[0]['text']
            url2_api = self.bs.juzibs_url2_getapi(url2_text)
            for api in url2_api:
                api_back = self.juzispider_main(main_mode=-1, url=api[0], change_cookie=True,
                                                unlock_mintime=True, sleep_time=0.5)[0]['text']
                api_text = (api_back, api[1])
                api_text_list.append(api_text)
            true_url_dir = self.bs.juzibs_url2_trueurl(api_text_list)  # 当前url2存在的快照字典
            true_urls_dir[url] = true_url_dir
        return true_urls_dir

    # 以下为爬虫逻辑控制部分，主要负责批量生成url和数据清洗控制

    def juzispider_main(self, main_mode, else_mode_1=-1, else_mode_2=-1, m_mode_add=None, m_page_true='0', re_spider=0,
                        url='', sleep_time=3.0, new_cookie='', url_encoding='utf-8',
                        unlock_mintime=False, change_cookie=False, use_proxies=False, is_reerror=False):
        """
        负责爬虫程序的控制，主要流程为构建url-爬取数据-异常处理-调用数据清洗-打包数据
        return-->tuple( dir{'bool': bool 标记是否发生异常,
                            'report': dir{'error_reason': str或int 自定义的异常名称,
                                          'url_remake': tuple(main_mode, else_mode_1, else_mode_2,
                                                              m_mode_add, m_page_true, url)
                                                              用于重新构建url列表，包含juzispider_main部分形参的参数,
                                          'url': str 当前爬取的url,
                                          'count': int 发生错误时的循环计数器的值
                                          'api_id': str 快照的id} 详细的异常报告，
                            'text': str 爬取的网页内容,
                            'data': dir{str: str} 标准的数据库提交内容，键为数据库指定的名称，可能为空,
                            },
                        etc )

        main_mode-->int 主要爬虫爬取格式选择，-1为自定义的url，0为需要循环爬取的url集合，1为单次爬取的url
        else_mode_1-->int 指定url的主要模式，默认为无效内容
        else_mode_2-->int 指定url的次要模式，默认为无效内容
        m_mode_add-->list或tuple 构建循环的str的合集
        m_page_true-->str 真实的url的页数，循环爬取所有页
        re_spider-->int 断点数据，指定从url元组中上次的位置
        url-->str 自定义的url，仅当main_mode为-1时有用
        sleep_time-->int或float 爬虫休眠的时间，默认为3.0秒
        new_cookie-->str 自定义的cookie
        url_encoding-->str 爬取内容的编码格式
        unlock_mintime-->bool 允许sleep_time小于3.0
        change_cookie-->bool 使new_cookie被爬虫使用
        use_proxies-->bool 使用代理
        is_reerror-->bool 为True表明此次爬取为自动异常处理，只有爬取正常和-403两种状态

        自定义的异常名：
        -ConnectionError 连接异常，可能为网络断开，连接超时
        -UrlError url异常，可能为url为空或url不合法
        -CodeError 状态码异常，目前只处理403和404，前者可以自动异常处理
        - -403Error 自动异常处理错误，表明403异常处理出错，此情况下'error_reason'的内容为'-403+{自定义异常名}+{状态码}'

        自定义的快照id:
        1-百度快照
        2-搜狗快照
        3-360快照
        4-bing快照
        5-谷歌快照-需要启用代理
        """
        # URL的构建
        spider_url_tup = (r'',)  # 未定义的mode使用空URL，通过爬取时触发MissingSchema异常捕获
        if main_mode == -1:  # ---自定义模式---，url为传入的url
            spider_url_tup = (url,)
        elif main_mode == 0:  # ---循环模式---，else_mode_1和else_mode_2是为了与juzimake_url1兼容
            mode_add = tuple(m_mode_add)
            spider_url_list = []
            if m_page_true != '0':  # 构建传入的page参数
                m_page = str(int(m_page_true) - 1)
            else:
                m_page = m_page_true
            # 需要添加str的模式
            if (else_mode_1 == 0 and else_mode_2 == 0) or else_mode_1 == 6 or else_mode_1 == 7:
                for url_str in mode_add:
                    spider_url = self.juzimake_url1(u_mode_1=else_mode_1, u_mode_2=else_mode_2, u_mode_str=url_str)
                    spider_url_list.append(spider_url)
            # 需要添加page的模式
            elif (else_mode_1 == 0 and else_mode_2 == 1) or (else_mode_1 == 2 and else_mode_2 == 1) \
                    or else_mode_1 == 3 or else_mode_1 == 4:
                n = 0
                mode_add = mode_add[0]
                while n <= int(m_page):
                    spider_url = self.juzimake_url1(u_mode_1=else_mode_1, u_mode_2=else_mode_2,
                                                    u_mode_str=mode_add, page=str(n))
                    spider_url_list.append(spider_url)
                    n += 1
            spider_url_tup = tuple(spider_url_list)
        elif main_mode == 1:  # ---单个网页---
            spider_url = self.juzimake_url1(u_mode_1=else_mode_1, u_mode_2=else_mode_2)
            spider_url_tup = (spider_url,)
        # 爬虫运行
        if not re_spider:  # 处理断点
            spider_count = 0
        else:
            spider_count = re_spider
        can_remake = False  # 标记异常是否可以自动处理
        spider_report_list = []  # 返回值
        while spider_count < len(spider_url_tup):
            true_url = spider_url_tup[spider_count]  # 正在爬取的url
            spider_back = self.juzispider_error(url=true_url, sleep_time=sleep_time, new_cookie=new_cookie,
                                                url_encoding=url_encoding, unlock_mintime=unlock_mintime,
                                                change_cookie=change_cookie, use_proxies=use_proxies,
                                                is_reerror=is_reerror)
            # 异常处理
            if not spider_back[0]:  # 触发异常
                spider_report_bool = False
                error_reason = None  # 未定义的异常原因为None
                if (spider_back[1] == 'ConnectionError') or (spider_back[1] == 'UrlError'):  # 连接异常或网页异常，无法处理
                    error_reason = spider_back[1]
                elif spider_back[1] == 'CodeError':  # 状态码异常
                    if spider_back[2] == 404:  # 404错误码，无法处理
                        error_reason = 404
                    elif spider_back[2] == 403:  # 403错误码，尝试使用快照代替
                        error_reason = 403
                        can_remake = True
                elif spider_back[1] == '-403Error':  # -403错误，自动处理模式出现异常，无法自动处理
                    error_reason = spider_back[3]
                    can_remake = False
                spider_report_report = {
                    'error_reason': error_reason,
                    'url_remake': (main_mode, else_mode_1, else_mode_2, m_mode_add, m_page_true, url),
                    'url': spider_back[-2],
                    'count': spider_count
                }
                spider_report_text = spider_back[-1]
                spider_report = {'bool': spider_report_bool,
                                 'report': spider_report_report,
                                 'text': spider_report_text,
                                 'data': ''}
                spider_report_list.append(spider_report)
                break  # 跳出循环处理异常
            else:  # 未出现异常
                spider_report_bool = True
                spider_report_report = {'url': spider_back[-2]}
                spider_report_text = spider_back[-1]
                text_clean_dir = self.bs.juzibs_main(main_mode_1=else_mode_1, main_mode_2=else_mode_2,
                                                     url_text=spider_report_text, is_reerror=is_reerror)
                spider_report = {'bool': spider_report_bool,
                                 'report': spider_report_report,
                                 'text': spider_report_text,
                                 'data': text_clean_dir}
                spider_report_list.append(spider_report)
            spider_count += 1
        # 自动处理异常部分，通过重构spider_report实现异常处理
        if can_remake:
            spider_report_list = []
            true_urls_dir = self.juzispider_re403(spider_url_tup)  # 获取真实的快照url字典
            while spider_count < len(spider_url_tup):
                url1 = spider_url_tup[spider_count]  # 异常url
                true_url_dir = true_urls_dir[url1]
                for api_id in true_url_dir.keys():  # 快照id
                    true_url2 = true_url_dir[api_id]  # 真实的快照url
                    true_url2_back = self.juzispider_main(main_mode=-1, url=true_url2, change_cookie=True,
                                                          use_proxies=use_proxies, is_reerror=True)
                    if true_url2_back[0]['bool']:  # 未发生-403错误
                        true_url2_text = true_url2_back[0]['text']
                        text_clean_dir = self.bs.juzibs_main(main_mode_1=else_mode_1, main_mode_2=else_mode_2,
                                                             url_text=true_url2_text, is_reerror=is_reerror,
                                                             api_id=api_id)
                        spider_report = {'bool': True,
                                         'report': {'url': url1, 'api_id': api_id},
                                         'text': true_url2_text,
                                         'data': text_clean_dir}
                        spider_report_list.append(spider_report)
                spider_count += 1
        return tuple(spider_report_list)


class JuziBS:
    """
    负责爬虫数据的清洗以及格式化
    由juzibs_main控制url1的模式
    """

    # 以下为快照url处理部分-url2

    @staticmethod
    def juzibs_url2_getapi(url_text):
        """
        获取指定url的api网址
        return-->tuple(tuple(str api的url, int 此url的id), etc )

        url_text-->str 快照网页的爬取内容
        """
        bs_back = BeautifulSoup(url_text, "lxml")  # bs处理
        bs_find = bs_back.body.find('script').string  # str提取
        re_back = re.compile(r"doLoadKz\('.*',").findall(bs_find)  # 正则提取doLoadKz函数的参数
        doloadkz_list = []
        for i in re_back:
            doloadkz_list.append(i[10:-2])
        json_url_list, n = [], 0
        while n < 5:  # 构建API网页
            json_url = ('https://2tool.top/kz.php?s=' + doloadkz_list[n] + f'&num={n + 1}', n + 1)
            json_url_list.append(json_url)
            n += 1
        return tuple(json_url_list)

    @staticmethod
    def juzibs_url2_trueurl(api_text_tup):
        """
        将api返回的内容转换为真实的url
        return-->dir{int 'url的id': str 指定id的url} 不包含不存在的快照url

        api_text_tup-->tuple juzibs_url2_getapi的返回值
        """
        url_back_dir = {}
        for api_text in api_text_tup:
            true_url_str = api_text[0][10:-1]  # api返回的内容
            if true_url_str != '{}':  # api返回的内容不为空
                true_url = true_url_str[10:-2]  # api返回的url
                url_back_dir[api_text[-1]] = true_url
        return url_back_dir

    # 以下为url数据清洗部分

    @staticmethod
    def juzibs_clean_00(url_text, is_reerror):
        """
        数据清洗-单个句子详情页
        """
        if not is_reerror:  # 原始url
            url_text_bs = BeautifulSoup(url_text, "lxml")
            sub = url_text_bs.find(attrs={'id': "xqtitle"}).string  # 句子内容
            author_title = []
            author_title_list = url_text_bs.find_all(attrs={'rel': "tag"})
            if len(author_title_list) == 2:  # 保证author_title有两个元素
                for text in author_title_list:
                    author_title.append(text.string)
            elif len(author_title_list) == 1:
                if 'writer' in str(author_title_list[0]):
                    author_title = [author_title_list[0].string, ' ']
                elif 'article' in str(author_title_list[0]):
                    author_title = [' ', author_title_list[0].string]
            elif len(author_title_list) == 0:
                author_title = [' ', ' ']
            author = author_title[0]  # 作者
            title = author_title[1]  # 标题
            times = url_text_bs.find(attrs={'class': "albumtemhi"}).string[3:]  # 发布时间
            text_clean = {
                'sub': sub,
                'author': author,
                'title': title,
                'time': times
            }
        else:  # 快照，效果不好，此情况下不使用快照
            text_clean = {}
        return text_clean

    # 以下为数据清洗控制部分

    def juzibs_main(self, main_mode_1, main_mode_2, url_text, is_reerror, api_id=-1):
        """
        由juzispider_main提供的数据选择合适的清洗模式
        """
        text_clean = {}
        try:
            if (main_mode_1 == 0) and (main_mode_2 == 0):  # 指定句子的页面
                text_clean = self.juzibs_clean_00(url_text=url_text, is_reerror=is_reerror)
            elif (main_mode_1 == 0) and (main_mode_2 == 1):
                pass
            elif (main_mode_1 == 1) and (main_mode_2 == 0):
                pass
            elif (main_mode_1 == 1) and (main_mode_2 == 1):
                pass
            elif (main_mode_1 == 1) and (main_mode_2 == 2):
                pass
            elif (main_mode_1 == 2) and (main_mode_2 == 0):
                pass
            elif (main_mode_1 == 2) and (main_mode_2 == 1):
                pass
            elif main_mode_1 == 3:
                pass
            elif main_mode_1 == 4:
                pass
            elif (main_mode_1 == 5) and (main_mode_2 == 0):
                pass
            elif (main_mode_1 == 5) and (main_mode_2 == 1):
                pass
            elif (main_mode_1 == 5) and (main_mode_2 == 2):
                pass
            elif (main_mode_1 == 5) and (main_mode_2 == 3):
                pass
            elif (main_mode_1 == 5) and (main_mode_2 == 4):
                pass
            elif (main_mode_1 == 5) and (main_mode_2 == 5):
                pass
            elif (main_mode_1 == 5) and (main_mode_2 == 6):
                pass
            elif (main_mode_1 == 6) and (main_mode_2 == 0):
                pass
            elif (main_mode_1 == 6) and (main_mode_2 == 1):
                pass
            elif (main_mode_1 == 7) and (main_mode_2 == 0):
                pass
            elif (main_mode_1 == 7) and (main_mode_2 == 1):
                pass
            elif (main_mode_1 == 7) and (main_mode_2 == 2):
                pass
            elif (main_mode_1 == 7) and (main_mode_2 == 3):
                pass
        except AttributeError:  # find函数返回值为None
            text_clean = {'bs_error': 'AttributeError'}
        return text_clean


if __name__ == '__main__':
    test = JuziSpider()
    back = test.juzispider_main(main_mode=-1, else_mode_1=-1, else_mode_2=-1,
                                m_mode_add=['217170'], url='https://www.mingyantong.com/recommend')
    print(back)
