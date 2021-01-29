## 句子迷重生计划 
> 此仓库储存的代码为初代代码，目前**已经弃用**，重写后的代码将在另外一个仓库内发布。  

前天看到了小兔，昨天是小鹿，今天是你。   ------TO CLANNAD  

### 项目简述  
自从句子迷服务器维护以来，截至目前没有恢复的迹象，虽然原公司创建了名言通作为代替，但是缺少了账户，搜索等功能，如同鸡肋。  
不过高中时对句子迷中的收藏有过数次的备份，因此个人的用户数据丢失不是太多，因此决定搭建一个本地的仿句子迷软件。  
此项目主要由**数据库**，**爬虫**，**句子管理**，**GUI**几个部分构成，目前已经完成部分模块的编写，不过基于未来的可维护性考虑，决定**停止本项目的开发**，所有的代码将在另外一个项目中重新设计编写。  

### 项目构成
- **向后兼容模块**，已完成所有功能的编写，主要负责将之前备份的数据转为标准格式储存在数据库中。  
- **数据库模块**，已完成底层接口的编写，槽函数的设计还在进行
- **爬虫模块**，爬虫部分编写完成，BS部分尚在进行
- **数据管理模块**，未开始
- **GUI模块**，正在构思界面设计和PYQT的学习

