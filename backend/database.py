from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 数据库连接信息
DB_USER = 'root@mysql001'
DB_PASSWORD = 'MySql123456.@'
DB_HOST = '127.0.0.1'
DB_PORT = 2881
DB_NAME = 'port_equipment_db'

# 对用户名和密码进行 URL 编码，处理特殊字符
encoded_user = quote_plus(DB_USER)
encoded_password = quote_plus(DB_PASSWORD)

# 创建数据库连接 URL
DATABASE_URL = f"mysql+mysqldb://{encoded_user}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 创建引擎
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=True  # 开发环境打印SQL，生产环境设为False
)

# 创建会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()


# 依赖注入：获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

