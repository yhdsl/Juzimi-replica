# 停止更新
"""
句子迷 - 数据库
负责句子的所有数据库管理
版本号-0.1.0

处于便于维护的目的，现停止维护
"""

import sqlite3


class Juzidata:
    """
    数据库，提供相关的API
    表：创建，删除，备份
    数据：添加，删除，修改，搜索
    """

    def __init__(self):
        # 数据库相关属性
        self.database_address = r'Database\database.db'  # 数据库相对存储地址和名称
        self.database_dataname_1 = 'Juzimi '  # 数据库1号名称，储存爬虫数据
        self.database_dataname_2 = 'Juzimi_old '  # 数据库2号名称，储存先前句子迷格式
        self.database_dataname_3 = 'Juzimi_other '  # 数据库3号名称，储存先前非句子迷格式
        self.listnull = ''  # weak error 消除
        self.listname = ['id', 'sub', 'author', 'title', 'like', 'comment']  # 提供列名
        # SQL语句语法，id越大时间越近
        self.database_new = 'CREATE TABLE '  # 创建表
        self.database_del = 'DROP TABLE '  # 删除表
        self.database_newformat = '''(id TEXT UNIQUE, sub TEXT NOT NULL, author TEXT DEFAULT '佚名'
        , title TEXT DEFAULT '', like TEXT DEFAULT '0', comment TEXT DEFAULT '0')'''  # 表单格式
        self.database_add = 'INSERT INTO '  # 添加数据
        self.database_find_1 = 'SELECT '  # 搜索功能
        self.database_find_2 = 'FROM '
        self.database_where = 'WHERE'  # where语句
        # 数据库的con和cur类，未提交和关闭
        self.database_con = sqlite3.connect(self.database_address)
        self.database_cur = self.database_con.cursor()

    def juzitable_name(self, mode):
        """
        为以下方法提供数据库表名，未来也可以新增表名
        数据库1号即mode=1，以此类推
        所有方法均需调用此方法获取表名！！！
        若无说明，则以下方法的data_name形参均为此函数的mode参数
        data_name仅接受int，数值在1到最大表之间
        """
        data_name = ''
        if mode == 1:
            data_name = self.database_dataname_1
        elif mode == 2:
            data_name = self.database_dataname_2
        elif mode == 3:
            data_name = self.database_dataname_3
        return data_name

    def juzitable_new(self, data_name):
        """负责创建一个新表单，仅当数据库不存在时调用"""
        data_name = self.juzitable_name(data_name)
        new_all = self.database_new + data_name + self.database_newformat
        self.database_con.execute(new_all)
        return

    def juzitable_del(self, data_name):
        """负责删除一个表单"""
        data_name = self.juzitable_name(data_name)
        del_all = self.database_del + data_name
        self.database_con.execute(del_all)
        return

    def juzitable_back(self):
        """负责备份一个表单"""
        pass

    def juzidata_mode(self, mode):
        """
        负责SQL语句中colum的构造
        负责SQL语句的函数均要调用此方法
        传入的mode为一个列表，以数字的方式指定要参与构造的数据
        id=0, sub=1, author=2, title=3, like=4, comment=5
        """
        namelist = self.listname
        name = ''
        for i in mode:  # 根据mode构建SQL语句
            add_name = namelist[i]
            name = name + add_name + ','
        return name

    def juzidata_add_id(self, id_list):
        """返回id中最大的一个，返回值为整数"""
        _ = self.listnull  # weak error 消除
        id_int = []
        for i in id_list:
            i = int(i)
            id_int.append(i)
        id_out = max(id_int)
        return id_out

    def juzidata_add(self, mode, sub, author='', title='', like='', comment='', data_name=1):
        """
        负责数据的增加，未提供合理性检验！！！
        API：要增加的数据列以列表的形式传给mode
        mode至少包含id和sub
        """
        dataa_formatstart1 = 'INSERT INTO '
        dataa_formatstart2 = 'VALUES '
        # 确保id唯一且递增，并确保空数据库的第一个id为1
        id_add = self.juzidata_find_all(data_name, 'id')
        if not id_add:
            main_id = 1
        else:
            main_id = self.juzidata_add_id(id_add) + 1
        # 提供SQL语句?的可选参数
        add_valueslist = [str(main_id), sub, author, title, like, comment]
        add_values, add_values_list = '', []
        for i in mode:  # 根据mode构建SQL中?语句对应的列表
            add_values = add_valueslist[i]
            add_values_list.append(add_values)
        colum = self.juzidata_mode(mode)
        data_name = self.juzitable_name(data_name)
        fin_name = '(' + colum[:-1] + ') '
        n = 1
        values = ''
        while n <= len(mode):  # 构建?语句
            values += '?,'
            n += 1
        fin_values = '(' + values[:-1] + ')'
        add_end = dataa_formatstart1 + data_name + fin_name + dataa_formatstart2 + fin_values
        self.database_cur.execute(add_end, add_values_list)
        return

    def juzifind_list(self, reason):
        """用于将curse中fetch方法返回的内容转化为一个列表，内容为字符串"""
        _ = self.listnull  # weak error 消除
        i = 0
        reason_fin = []
        while i < len(reason):
            reason_fin.append(reason[i][0])
            i += 1
        return reason_fin

    def juzidata_find_all(self, data_name, findname):
        """提供数据库的搜索功能 - 返回指定列的所有内容"""
        data_name = self.juzitable_name(data_name)
        namefindall = self.database_find_1 + findname + ' ' + self.database_find_2 + data_name
        self.database_cur.execute(namefindall)
        namefindall_fin = self.juzifind_list(self.database_cur.fetchall())
        return namefindall_fin  # 内容已整理为元素为字符串的列表

    def juzi_close(self):
        """提供数据的提交和安全退出，所有函数调用后都必须调用此函数！！！"""
        self.database_con.commit()
        self.database_cur.close()
        self.database_con.close()
        return


if __name__ == '__main__':
    print('未编写测试-数据库管理-已废弃', end='')
