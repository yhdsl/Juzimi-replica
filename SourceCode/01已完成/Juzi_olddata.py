"""
句子迷-先前数据导入
导入之前的相关数据，不应当被其他模块使用
这并不是GUI中的单个句子导入（添加句子）或多个句子导入
不过有些代码可以复用
此模块只是为了保证向后兼容

现在已经停止维护！
"""

# ---------------------------------------------
#                   更新日志
# 2020/9/22 保证与目前的数据库管理系统API相同
# ---------------------------------------------

import Juzi_manage_core

address = r"D:\Programs\Programs\Working\Juzimi_re\Working\olddata\\"  # 数据库绝对位置
address_name1 = '旧句子迷.txt'  # 标准格式
address_name2 = '旧句子迷（补充）.txt'
address_name3 = '新句子迷.txt'
address_name4 = '句子集.txt'  # 非标准格式
address_name5 = '龙族.txt'
address_name6 = '漂亮的不像实力派.txt'
address_name7 = '随笔.txt'
address_name8 = '其他.txt'


def oldbase_add(data_name, sub, author, title):
    """
    负责导入数据
    提供表名，内容，作者，标题
    """
    mode = [0, 1, 2, 3]
    run_manage = Juzi_manage_core.Juzidata()
    run_manage.juzidata_add(data_name=data_name, mode=mode, sub=sub, author=author, title=title)
    run_manage.juzimain_close()
    return


def olddata_fin_add(sub_out_list, author_out_list, title_out_list, data_name):
    """数据提交"""
    add_name = 0  # 正序提交
    while add_name < len(sub_out_list):  # 调用oldbase_add函数添加到数据库
        sub = sub_out_list[add_name]
        author = author_out_list[add_name]
        title = title_out_list[add_name]
        oldbase_add(data_name=data_name, sub=sub, author=author, title=title)
        add_name += 1
    return


def olddata_get_juzi(olddata_name, mode, data_name):
    """
    从标准格式中返回内容，作者，标题
    提供名称
    mode为0反序，为1正序
    data_name为表名
    """
    olddata_address = address + olddata_name
    olddata_read = open(olddata_address)
    olddata_readlines = olddata_read.readlines()
    # 可以作为参考的代码
    i = 0  # 循环标识
    n = 0  # 上一个句子结尾标识，应处理为下一个句子的开头
    sub_out_list, author_out_list, title_out_list = [], [], []
    while i < len(olddata_readlines):
        newdata_read = olddata_readlines[i]  # 主循环，返回所有读取的行
        if '——' in newdata_read[0:2]:  # 如果该行中有非sub信息，则进行数据分类
            sub_out = ''  # 初始化字符串
            for sub_in in range(n, i):  # 提取sub
                sub_out += olddata_readlines[sub_in]
            sub_out_list.append(sub_out[:sub_out.find('\t')])  # 标准格式的sub，列表
            title_find1 = newdata_read.find('《')  # 《》的位置
            title_find2 = newdata_read.find('》')
            if title_find1 == -1:  # 缺少title的情况，title默认为""
                author_out = newdata_read[2:-1]
                title_out = ''
            else:  # 剩余的情况
                author_out = newdata_read[2:title_find1]
                title_out = newdata_read[title_find1+1:title_find2]
            author_out_list.append(author_out)  # 标准格式的author和title，列表
            title_out_list.append(title_out)
            n = i + 1
        i += 1
    if mode == 0:  # 句子迷添加
        add_name = len(sub_out_list) - 1
        while 0 <= add_name < len(sub_out_list):  # 调用oldbase_add函数添加到数据库
            sub = sub_out_list[add_name]
            author = author_out_list[add_name]
            title = title_out_list[add_name]
            oldbase_add(data_name=data_name, sub=sub, author=author, title=title)
            add_name -= 1  # 反序加入，确保按时间顺序
    else:  # 正序加入
        olddata_fin_add(sub_out_list=sub_out_list, author_out_list=author_out_list, title_out_list=title_out_list,
                        data_name=data_name)
    return


def olddata_get_longzhu(olddata_name, mode, data_name):
    """
    从其他格式中返回内容
    提供名称
    mode为0龙族，为1漂亮的不像实力派，其他值为其他
    data_name为表名
    """
    olddata_address = address + olddata_name
    olddata_read = open(olddata_address)
    olddata_readlines = olddata_read.readlines()
    i = 0  # 循环标识
    newdata_read, sub_out_list = '', []
    if mode == 0:  # 龙族
        author_out, title_out = '江南', '龙族'
    elif mode == 1:  # 漂亮的不像实力派
        author_out, title_out = '', '漂亮的不像实力派'
    else:  # 其他
        author_out, title_out = '', ''
    author_out_list, title_out_list = [], []
    while i < len(olddata_readlines):
        newdata_read = olddata_readlines[i][:-1]
        sub_out_list.append(newdata_read)
        author_out_list.append(author_out)
        title_out_list.append(title_out)
        i += 1
    olddata_fin_add(sub_out_list=sub_out_list, author_out_list=author_out_list, title_out_list=title_out_list,
                    data_name=data_name)
    return


def olddata_get_more(olddata_name):
    """处理非标准格式中的多行文本，文本以——单行隔开"""
    olddata_address = address + olddata_name
    olddata_read = open(olddata_address, encoding='utf-8')
    olddata_readlines = olddata_read.readlines()
    i = 0
    n = 0
    sub_out_list = []
    while i < len(olddata_readlines):
        newdata_read = olddata_readlines[i]
        if '——' in newdata_read:
            sub_out = ''  # 初始化字符串
            for sub_in in range(n, i):  # 提取sub
                sub_out += olddata_readlines[sub_in]
            sub_out_list.append(sub_out[:sub_out.find('\t')])  # 标准格式的sub，列表
            n = i + 1
        i += 1
    author_out, title_out = '', ''
    author_out_list, title_out_list = [], []
    n = 0
    while n < len(olddata_readlines):
        author_out_list.append(author_out)
        title_out_list.append(title_out)
        n += 1
    olddata_fin_add(sub_out_list=sub_out_list, author_out_list=author_out_list, title_out_list=title_out_list,
                    data_name=3)
    return


def run():  # 批量导入的包装
    olddata_get_juzi(address_name1, 0, 2)
    olddata_get_juzi(address_name2, 0, 2)
    olddata_get_juzi(address_name3, 0, 2)
    olddata_get_juzi(address_name4, 1, 3)
    olddata_get_longzhu(address_name5, 0, 3)
    olddata_get_longzhu(address_name6, 1, 3)
    olddata_get_longzhu(address_name7, 3, 3)
    olddata_get_more(address_name8)
    print('完成', end='')
    return


if __name__ == '__main__':
    run()
