"""
句子迷-数据库-核心
负责提供数据库相关的底层API，数据库的相关访问需求
版本号-0.3.2

重构于Juzi_manage_old，更改了SQL语句的编写
"""

# -----------------------------------------------------------
#                      更新日志
# 2020/9/22 完成所有功能的编写和基本测试
# 2020/9/22 添加juzimain_info方法，返回所有表名和SQL构造语句
# 2020/9/22 添加名为url的columl，用于爬虫url构建
# 2020/9/23 修改juzicolumn_create，使其可以自定义columl的value
# 2020/9/28 调整部分方法参数类型为bool，方便调用
# -----------------------------------------------------------

import sqlite3
import time
import random


class Juzidata:
    """
    实现数据库的所有底层管理，大部分API未效验传入的数据，不建议调用此模块

    已包括
    -db文件-只负责创建，不负责创建地点是否存在
    -表(table)-创建，删除，备份
    -数据(columl)-创建，删除，修改，搜索

    自定义流程
    -.db文件-重载self.juzidata_addess
    -table-指定t_name形参
    -columl-重载self.useable_columl，指定format_add和value_change形参
    """

    def __init__(self):
        # 数据库的关键信息
        self.juzidata_addess = r'Database\Juzi_database.db'  # .db数据库相对存储地址和名称
        self.juzidata_table_old = 'Juzidata_old'  # 表名-储存向后兼容数据
        self.juzidata_table_spider = 'Juzidata_spider'  # 表名-储存爬虫数据
        self.juzidata_table_main0 = 'Juzidata_main0'  # 表名-储存0号数据库内容
        # 提供con和cur类以供调用，没有做提交和关闭处理，谨防数据泄露
        self.main_con = sqlite3.connect(self.juzidata_addess)
        self.main_cur = self.main_con.cursor()
        # 为以后拓展做准备
        # 所有的columl列表，向列表中添加新数据即可拓展可用的columl
        self.useable_columl = ['id', 'sub', 'author', 'title', 'like', 'comment', 'time', 'url']

    # ---以下为通用方法---

    def juzimain_close(self):
        """
        负责数据库的安全提交和退出，所有数据库API最后都要调用此方法
        """
        self.main_con.commit()  # 提交
        self.main_cur.close()  # 关闭
        self.main_con.close()
        return

    def juzimain_info(self):
        """
        return-->tuple(str) 返回数据库的所有表名和SQL构造语句
        """
        self.main_cur.execute("SELECT tbl_name FROM sqlite_master WHERE type = 'table'")  # 所有表名
        table_all_back = self.main_cur.fetchall()
        self.main_cur.execute("SELECT sql FROM sqlite_master WHERE type = 'table'")  # SQL构造语句
        table_sql_back = self.main_cur.fetchall()
        table_all_tuple = self.juzicolumn_search_handle(s_back=table_all_back, s_mode=[0])
        table_sql_tuple = self.juzicolumn_search_handle(s_back=table_sql_back, s_mode=[0])
        return table_all_tuple, table_sql_tuple

    # ---以下为表TABLE的方法---

    def juzitable_name(self, t_mode=2, t_name=''):
        """
        return-->str 以字符串的形式返回指定的表名，默认返回主数据库-'Juzidata_main0'

        t_mode-->int 若未传入name，则返回mode指定的自带表名
        t_name-->str 若传入name，则将其返回，可用于自定义的新表名
        目前已自带：0-Juzidata_old，1-Juzidata_spider，2-Juzidata_main0

        以下所有t_mode和t_name形参均为传入此方法的实参--获取表名
        """
        # 默认数据库列表
        name_old = [self.juzidata_table_old, self.juzidata_table_spider, self.juzidata_table_main0]
        if not t_name:  # 自带表名
            name_out = name_old[t_mode]
        else:  # 自定义的新表名
            name_out = t_name
        return name_out

    def juzitable_create(self, t_mode=2, t_name='', format_add=''):
        """
        return-->None 创建新的表，未检验是否存在

        format_add-->str 自定义的表单格式可由format_add指定
        """
        table_name = self.juzitable_name(t_mode=t_mode, t_name=t_name)  # 表名
        if not format_add:  # 默认创建格式
            table_format = "id INTEGER NOT NULL UNIQUE, " \
                           "sub TEXT NOT NULL, " \
                           "author TEXT DEFAULT '佚名', " \
                           "title TEXT, " \
                           "like INTEGER DEFAULT 0, " \
                           "comment INTEGER DEFAULT 0, " \
                           "time TEXT, " \
                           "url TEXT"
        else:  # 可传入自定义格式
            table_format = format_add
        self.main_cur.execute(f'CREATE TABLE [{table_name}] ({table_format})')
        return

    def juzitable_delete(self, t_mode=2, t_name=''):
        """
        return-->None 删除指定的表，未检验是否存在
        """
        table_name = '[' + self.juzitable_name(t_mode=t_mode, t_name=t_name) + ']'  # 表名
        self.main_cur.execute(f'DROP TABLE {table_name}')
        return

    def juzitable_backup(self, address=''):
        """
        return-->None 备份当前数据库

        address-->str 指定自定义的备份位置和名称，否则使用默认保存方式--随机数字+备份时间
        """
        if not address:
            back_time = str(random.randint(10, 99)) + time.strftime('+%Y+%m+%d+%H+%M+%S')
            back_address = 'data_backup+' + back_time + '.db'
        else:
            back_address = address
        back_con = sqlite3.connect(back_address)
        self.main_con.backup(back_con)
        return

    # ---以下为数据COLUMN的方法---

    def juzicolumn_create(self, c_mode, sub='', author='', title='', like=0, comment=0, times='',
                          url='', t_mode=2, t_name='', value_change=None):
        """
        return-->None 负责数据的添加，[不负责向后兼容]

        c_mode-->list[0,int] 传入要添加数据的columl，其中必须包括0，数值参考self.useable_columl，缺失的columl由SQL默认值决定
        sub~times-->str或int 传入待添加的values，其中times为time数据行，未传入的value默认为空或0
        value_change-->list[str] 传入自定义的values列表，必须保证与columl顺序一致
        """
        table_name = self.juzitable_name(t_mode=t_mode, t_name=t_name)  # 表名
        columl_str = ''
        for i in sorted(c_mode):
            columl_str = columl_str + self.useable_columl[i] + ','
        columl_str = '(' + columl_str[:-1] + ')'  # 已处理且排序的columl字符串合集
        all_id = self.juzicolumn_search_run(s_mode=[0], t_mode=t_mode, t_name=t_name)  # 搜索id
        if not all_id:  # 保证id从1开始增加，不保证递增
            id_add = 1
        else:
            id_add = max(all_id) + 1
        useable_value = [id_add, sub, author, title, like, comment, times, url]  # 已处理且排序的value
        value_list = []  # 新增columl未作处理
        for n in sorted(c_mode):
            value_list.append(useable_value[n])  # 待输入的value
        value_in = '(' + ('?,' * len(c_mode))[:-1] + ')'  # 构建的?语句
        if value_change is not None:  # 提供自定义的value列表
            value_list = value_change
            value_in = '(' + ('?,' * len(value_change))[:-1] + ')'
        create_execute = f'INSERT INTO {table_name} {columl_str} VALUES {value_in}'
        self.main_cur.execute(create_execute, value_list)
        return

    def juzidata_add(self, mode, sub, author='', title='', data_name=1):
        """
        -向后兼容模块，不再维护-
        return-->None 负责数据的添加
        """
        data_name = data_name * 0
        self.juzicolumn_create(c_mode=mode, sub=sub, author=author, title=title, t_mode=data_name)
        return

    def juzicolumn_delete(self, main_id, t_mode=2, t_name=''):
        """
        return-->None 负责删除指定id的所有内容，即一整行全部删除

        main_id-->int 指定数据的id值
        """
        table_name = self.juzitable_name(t_mode=t_mode, t_name=t_name)  # 表名
        delete_execute = f'DELETE FROM {table_name} WHERE {self.useable_columl[0]} = ?'
        id_tuple = (main_id,)  # 指定数据的id值
        self.main_cur.execute(delete_execute, id_tuple)
        return

    def juzicolumn_change(self, main_id, columl_set, value_set, t_mode=2, t_name=''):
        """
        return-->None 负责修改指定id的指定内容，限定每次只能修改一条

        main_id-->int 指定更改条目的id
        columl_set-->int 以整数指定columl，数值由self.useable_columl决定
        value_set-->str或int 传入新的数据
        """
        table_name = self.juzitable_name(t_mode=t_mode, t_name=t_name)  # 表名
        value_tuple = (value_set, main_id)  # 待输入的value
        change_execute = f'UPDATE {table_name} SET {self.useable_columl[columl_set]} = ? ' \
                         f'WHERE {self.useable_columl[0]} = ?'
        self.main_cur.execute(change_execute, value_tuple)
        return

    def juzicolumn_search_main(self, s_mode, t_mode=2, t_name='', s_where='', s_where_tuple=()):
        """
        -不应被其他方法调用-
        return-->tuple(list[]) 负责SQL搜索语句的构建和执行，返回未处理的数据

        s_mode-以列表的形式传入要搜索的columl，具体索引值由self.useable_columl决定-[0, 1, 2]
        """
        table_name = self.juzitable_name(t_mode=t_mode, t_name=t_name)  # 表名
        columl_str = ''
        for i in sorted(s_mode):
            columl_str = columl_str + self.useable_columl[i] + ','
        columl_str = columl_str[:-1]  # 已处理且排序的需搜索的columl字符串合集
        scarch_all_execute = f'SELECT {columl_str} FROM {table_name}'  # 返回指定列所有数据的SQL语句
        if not s_where:
            self.main_cur.execute(scarch_all_execute)
            search_back = self.main_cur.fetchall()
        else:
            scarch_some_execute = scarch_all_execute + ' ' + s_where  # 构建带where语句的SQL语句
            self.main_cur.execute(scarch_some_execute, s_where_tuple)
            search_back = self.main_cur.fetchall()
        return search_back

    @staticmethod
    def juzicolumn_search_handle(s_back, s_mode):
        """
        -不应被其他方法调用-
        return-->list[tuple()]或tuple() 处理search_main方法返回的数据。若只指定单行，则返回元组，否则暂时不做处理

        s_back-搜索的返回值，s_mode-同search_main
        """
        if len(s_mode) == 1:  # 只指定单行，则返回元组
            i, back_list = 0, []
            while i < len(s_back):
                back_list.append(s_back[i][0])
                i += 1
            back_tuple = tuple(back_list)
        else:
            back_tuple = s_back
        return back_tuple

    @staticmethod
    def juzicolumn_search_where(columl_tuple, value_tuple, where_mode, is_not=False, is_and=False, is_or=False):
        """
        -不应被其他方法调用-
        return-->str和tuple 负责search中where语句的构建，返回值为合法的whrer字符串和配套的 ? 元组

        columl_tuple-以元组的形式传入指定的columl，value_tuple以元组的形式传入所需的判断值
        where_mode-以列表的形式传入所选的where语句，以便与and或or构建语句，列表元素对应如下
        is_not，is_and，is_or-是否启用not，and，or

        当前已实现的where语句：
        0-lisk语句，用于模糊匹配，不支持NOT，指定is_not无效果
        1-is语句，用于精准匹配
        2-in语句，用于匹配给定数据中存在的值，注意传入值为列表
        3-betweem语句，用于匹配给定范围中存在的值，注意传入值为列表
        """
        n = 0
        if is_not:  # NOT选择
            add_not = 'NOT '
        else:
            add_not = ''
        search_execute_all, value_list_all = [], []
        while n < len(where_mode):  # 可添加if分支拓展可选的where语句
            value_list = []  # 每次循环重置此列表
            where_one = where_mode[n]
            if where_one == 0:  # lisk语句
                search_execute = f'{columl_tuple[n]} LIKE ?'
                value_list.append(value_tuple[n])
            elif where_one == 1:  # is语句
                search_execute = f'{columl_tuple[n]} {add_not}IS ?'
                value_list.append(value_tuple[n])
            elif where_one == 2:  # in语句
                search_execute = f'{columl_tuple[n]} {add_not}IN {"(" + ("?,"*len(value_tuple[n]))[:-1] + ")"}'
                value_list = value_tuple[n]
            elif where_one == 3:  # betweem语句
                search_execute = f'{columl_tuple[n]} {add_not}BETWEEN ? AND ?'
                value_list = value_tuple[n]
            else:  # 非指定选项返回空
                search_execute, value_list = '', []
            search_execute_all.append(search_execute)  # 合法的whrer列表
            value_list_all += value_list
            n += 1
        value_tuple_all = tuple(value_list_all)  # 配套的 ? 元组
        if is_and or is_or:  # and和or不为空
            if is_and:  # and不为空
                link_word = ' AND '
                link_end = -5
            else:  # or不为空
                link_word = ' OR '
                link_end = -4
        else:
            if len(where_mode) == 1:  # 如果传入单个，不做其他添加
                link_word = ''
                link_end = -1
            else:  # 如果传入了多个选择且未设置and和or，则默认为or
                link_word = ' OR '
                link_end = -4
        i, where_one = 0, ''
        while i < len(search_execute_all):
            where_one += search_execute_all[i] + link_word  # 构建where字符串
            i += 1
        if len(where_mode) == 1:  # 如果传入单个，不做句尾处理
            where_str_all = 'WHERE ' + where_one
        else:
            where_str_all = 'WHERE ' + where_one[:link_end]
        return where_str_all, value_tuple_all

    def juzicolumn_search_run(self, s_mode, t_mode=2, t_name='', where_or_not=False,
                              is_not=False, is_and=False, is_or=False,
                              columl_tuple=(), value_tuple=(), where_mode=None):
        """
        实现数据库的搜索功能，为搜索方法的API，搜索时应调用此方法
        return-->list[tuple()]或tuple() 如果只搜索单个columl，返回元组，否则返回内含元组的列表 [具有返回值]

        s_mode-->list[int] 指定要搜索的columl，具体索引值由self.useable_columl决定
        where_or_not-->bool 传入True启用where语句功能
        is_not-->bool 传入True启用where语句中not否定功能
        is_and-->bool 传入True启用where语句中and连接词功能
        is_or-->bool 传入True启用where语句中or连接词功能
        columl_tuple-->tuple(str,) 传入where语句中要参与过滤判定的columl，可由[字符串]指定自定义的columl
        value_tuple-->tuple(str或list[str],) 传入where语句中要参与过滤判定的columl的value，必须为[字符串]
        where_mode-->list[int] 指定where语句中不同的过滤类型，可多选，int取值如下

        目前已实现的过滤类型 注意传入单元组时不要忘记( ,)
        0--lisk语句，用于模糊匹配，不支持NOT，指定is_not无效果，需提供合法的LIKE通配符
        1--is语句，用于精准匹配
        2--in语句，用于匹配给定数据中存在的值  value_tuple-->tuple(list)
        3--betweem语句，用于匹配给定范围中存在的值  value_tuple-->tuple(list)
        """
        if not where_or_not:  # 不启用where
            search_back = self.juzicolumn_search_main(s_mode=s_mode, t_mode=t_mode, t_name=t_name)
            search_finally = self.juzicolumn_search_handle(s_back=search_back, s_mode=s_mode)
        else:  # 启用where
            search_where, search_where_tuple = self.juzicolumn_search_where(columl_tuple=columl_tuple,
                                                                            value_tuple=value_tuple,
                                                                            where_mode=where_mode,
                                                                            is_not=is_not,
                                                                            is_and=is_and,
                                                                            is_or=is_or)
            search_back = self.juzicolumn_search_main(s_mode=s_mode, t_mode=t_mode, t_name=t_name,
                                                      s_where=search_where, s_where_tuple=search_where_tuple)
            search_finally = self.juzicolumn_search_handle(s_back=search_back, s_mode=s_mode)
        return search_finally


if __name__ == '__main__':
    test = Juzidata()
    print('未编写测试-数据库管理', end='')
    test.juzimain_close()
