import sqlite3
import pymysql
from config import Config  # 导入您的配置


def get_sqlite_tables(sqlite_conn):
    """获取SQLite中除user外的所有表"""
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'user'")
    return [row[0] for row in cursor.fetchall()]


def migrate_table(sqlite_conn, mysql_conn, table_name):
    """迁移单个表"""
    sqlite_cursor = sqlite_conn.cursor()
    mysql_cursor = mysql_conn.cursor()

    # 获取表结构
    sqlite_cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [col[1] for col in sqlite_cursor.fetchall()]

    # 获取数据
    sqlite_cursor.execute(f"SELECT * FROM {table_name}")
    rows = sqlite_cursor.fetchall()

    # 构建INSERT语句
    placeholders = ', '.join(['%s'] * len(columns))
    columns_str = ', '.join(columns)
    insert_sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"

    # 插入数据
    for row in rows:
        mysql_cursor.execute(insert_sql, row)

    print(f"已迁移表 {table_name}: {len(rows)} 条记录")


def main():
    # 连接SQLite
    sqlite_conn = sqlite3.connect('./data.db')  # 修改路径

    # 连接MySQL
    mysql_conn = pymysql.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        charset='utf8mb4'
    )

    # 获取并迁移所有表（除user外）
    tables = get_sqlite_tables(sqlite_conn)
    for table in tables:
        migrate_table(sqlite_conn, mysql_conn, table)

    # 提交并关闭连接
    mysql_conn.commit()
    mysql_conn.close()
    sqlite_conn.close()
    print("迁移完成！")


if __name__ == "__main__":
    main()
