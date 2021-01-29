"""
句子迷-数据库-管理中心
负责综合所有数据库相关的模块，并提供GUI的槽函数
版本号-0.1.0
"""
import os
import time
import Juzi_manage_core


# 定义异常
class StartError(Exception):
    """程序自检时发生错误，程序捕获此错误后退出"""
    pass


class MainDbLossError(Exception):
    """程序核心db文件丢失"""
    def __init__(self):
        pass  # TODO(JuziSlotFunction) 输出Log条目


# 以下为Log文件相关部分
class JuziLog(object):
    """
    负责Log文件相关部分的方法
    """
    def __init__(self):
        # 以下为Log核心数据
        self.logs_dir = r'Logs\\'  # Log文件储存地址
        self.new_log_name = self.logs_dir + 'Juzimi-re.0.txt'  # 新Log文件名称
        self.log_show_level = 3  # log文件显示等级
        self.log_dir_all = 4  # log文件个数
        # 以下为初始化执行部分
        self.new_log = self.log_start()

    def log_start(self):
        """
        初始化Log文件管理
        return-->file 当前Log文件的指针
        """
        # Log文件夹存在性检测
        logs_exists = os.path.exists(self.logs_dir)
        if not logs_exists:
            os.mkdir(self.logs_dir)
        else:
            logs_list = os.listdir(path=self.logs_dir)
            logs_list.sort(reverse=True)
            for log_old_name in logs_list:  # 之前的Log文件依次后移
                log_old_name_list = log_old_name.split('.')
                log_new_name = log_old_name_list[0] + '.' + str(int(log_old_name_list[1]) + 1) + '.txt'
                os.rename(self.logs_dir + log_old_name, self.logs_dir + log_new_name)
        new_log_create = open(self.new_log_name, 'x', encoding='utf8')
        new_log_create.close()
        new_log = open(self.new_log_name, 'r+', encoding='utf8')
        return new_log

    @staticmethod
    def time_get():
        """
        获取日志记录的时间
        """
        log_time_format = '[%m/%d/%Y - %I:%M:%S%p] '
        log_time = time.strftime(log_time_format)
        return log_time

    def log_add(self, log_str, log_lv):
        """
        添加log条目
        """
        log_time = self.time_get()
        log_level = '[未知] '
        if log_lv == 0:
            log_level = '[错误] '
        elif log_lv == 1:
            log_level = '[警告] '
        elif log_lv == 2:
            log_level = '[通知] '
        elif log_lv == 3:
            log_level = '[调试] '
        log_txt = log_time + log_level + log_str
        if log_lv < self.log_show_level:
            self.new_log.write(log_txt)
        return

    def log_dir_delete(self):
        """
        删除多余的log文件
        """
        logs_list = os.listdir(path=self.logs_dir)
        os.chdir(self.logs_dir)
        for log_dir in logs_list:
            log_code = int(log_dir.split('.')[-2])
            if log_code > self.log_dir_all - 1:
                os.remove(log_dir)
        return


# ini文件读取
class Juziini:
    """
    负责ini文件的读取和写入
    """

    def __init__(self):
        self.ini_address = 'settings.ini'  # ini文件相对地址

    def exist_check(self):
        """
        ini文件存在性检验
        """
        try:
            open(self.ini_address, 'r+', encoding='utf8')
        except FileNotFoundError:
            pass


# 数据库类
class JuziDatabase(Juzi_manage_core.JuziSql):
    """
    数据库类
    """

    def __init__(self):
        super(JuziDatabase, self).__init__()
        # 初始化部分
        self.main_db_check()  # settings.db文件检测
        # 以下为数据库核心数据
        self.main_db_address = 'settings.db'  # 核心db文件地址
        self.db_dir = r'Database\\'

    def main_db_check(self):
        """settings.db文件检测"""
        main_db_exists = os.path.exists(self.main_db_address)
        main_dir_exists = os.path.exists(self.db_dir)
        if not main_dir_exists:  # 检测Database\
            os.mkdir(self.db_dir)
        if not main_db_exists:
            raise MainDbLossError
        return


class JuziSlotFunction(JuziLog):
    """
    提供PYQT槽函数
    """
    def __init__(self):
        # 父类初始化，程序初始化运行，检测StartError异常
        JuziLog.__init__(self)  # 包括Log初始化检测


if __name__ == '__main__':
    test = JuziSlotFunction()
