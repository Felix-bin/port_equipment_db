"""
创建数据库脚本
使用前请确保 OceanBase/MySQL 服务已启动
"""
from urllib.parse import quote_plus
import MySQLdb

# 数据库连接信息
DB_USER = 'root@mysql001'
DB_PASSWORD = 'MySql123456.@'
DB_HOST = '127.0.0.1'
DB_PORT = 2881
DB_NAME = 'port_equipment_db'

# 对用户名和密码进行 URL 编码
encoded_user = quote_plus(DB_USER)
encoded_password = quote_plus(DB_PASSWORD)

def create_database():
    """创建数据库"""
    try:
        # 连接到 MySQL/OceanBase (不指定数据库)
        print(f"正在连接到 OceanBase ({DB_HOST}:{DB_PORT})...")
        conn = MySQLdb.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        
        # 检查数据库是否存在
        cursor.execute("SHOW DATABASES")
        databases = [db[0] for db in cursor.fetchall()]
        
        if DB_NAME in databases:
            print(f"数据库 '{DB_NAME}' 已存在")
            choice = input("是否删除并重新创建？(y/n): ")
            if choice.lower() == 'y':
                print(f"正在删除数据库 '{DB_NAME}'...")
                cursor.execute(f"DROP DATABASE {DB_NAME}")
                print(f"数据库 '{DB_NAME}' 已删除")
            else:
                print("跳过数据库创建")
                cursor.close()
                conn.close()
                return
        
        # 创建数据库
        print(f"正在创建数据库 '{DB_NAME}'...")
        cursor.execute(f"CREATE DATABASE {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"✓ 数据库 '{DB_NAME}' 创建成功！")
        
        cursor.close()
        conn.close()
        
        print("\n下一步：")
        print("1. 运行初始化脚本: python init_db.py")
        print("2. 启动后端服务: python main.py")
        
    except MySQLdb.Error as e:
        print(f"错误: {e}")
        print("\n请检查：")
        print("1. OceanBase/MySQL 服务是否已启动")
        print("2. 数据库连接参数是否正确")
        print("3. 用户是否有创建数据库的权限")
    except Exception as e:
        print(f"未知错误: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("OceanBase/MySQL 数据库创建工具")
    print("=" * 60)
    print(f"主机: {DB_HOST}:{DB_PORT}")
    print(f"用户: {DB_USER}")
    print(f"数据库名: {DB_NAME}")
    print("=" * 60)
    print()
    
    create_database()

