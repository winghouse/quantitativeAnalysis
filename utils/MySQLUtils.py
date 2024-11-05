import pymysql
import self

from Biance.common.ConfigManager import ConfigManager


class MySQLUtils:
    def __init__(self):

        config = ConfigManager()
        self.host = config.get('mysql', 'host')
        self.user = config.get('mysql', 'user')
        self.password = config.get('mysql', 'password')
        self.database = config.get('mysql', 'database')

        self.connection = pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        # 获取游标对象
        self.cursor = self.connection.cursor()

    def insert_data_to_mysql(self, table_name, data):
        """
        将数据插入MySQL表的通用函数。

        参数:
            host: 数据库主机地址 (通常为 'localhost' 或远程服务器IP)
            user: MySQL数据库的用户名
            password: MySQL数据库的密码
            database: 需要连接的数据库名称
            table_name: 要插入数据的表名称
            data: 插入的数据，类型为列表，列表中的每一项是一个字典，字典的键为列名，值为要插入的内容

        示例数据格式：
        data = [
            {"name": "John", "age": 25, "gender": "Male"},
            {"name": "Jane", "age": 28, "gender": "Female"}
        ]
        """

        # 创建数据库连接

        try:


            # 获取列名和占位符
            columns = ', '.join(data[0].keys())  # 从字典键获取列名
            placeholders = ', '.join(['%s'] * len(data[0]))  # 根据列生成占位符

            # 构造SQL插入语句
            sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

            # 将数据转换为元组列表
            values = [tuple(d.values()) for d in data]

            # 批量插入数据
            self.cursor.executemany(sql, values)

            # 提交到数据库
            self.connection.commit()

            print(f"成功插入 {self.cursor.rowcount} 条数据到表 {table_name}")

        except pymysql.MySQLError as e:
            # 如果出现异常，进行回滚
            print(f"插入数据失败: {e}")
            self.connection.rollback()

    def query_mysql_table(self, query):
        """
        查询MySQL表的通用函数。

        参数:
            host: 数据库主机地址 (通常为 'localhost' 或远程服务器IP)
            user: MySQL数据库的用户名
            password: MySQL数据库的密码
            database: 需要连接的数据库名称
            query: 要执行的SQL查询语句

        返回:
            查询结果：一个包含元组的列表，每个元组代表一行数据
        """

        try:

            # 执行SQL查询
            self.cursor.execute(query)

            # 获取查询结果
            results = self.cursor.fetchall()

            # 打印结果
            print(f"查询结果：{results}")
            return results

        except pymysql.MySQLError as e:
            # 如果出现异常
            print(f"查询失败: {e}")
            return None

    def close(self):
        # 关闭游标和连接
        self.cursor.close()
        self.connection.close()

# 使用示例
table_name = 'example_table'

# 假设你的表有 name, age, gender 三个字段
data = [
    {"name": "John", "age": 25, "gender": "Male"},
    {"name": "Jane", "age": 28, "gender": "Female"}
]

# MySQLUtils().insert_data_to_mysql(table_name, data)

query = "select * from example_table"

# MySQLUtils().query_mysql_table(query)
