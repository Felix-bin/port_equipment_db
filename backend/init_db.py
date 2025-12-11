"""
数据库初始化脚本
运行此脚本以创建数据库表并插入初始数据
"""
from database import engine, SessionLocal
from models import Base, User, Equipment, Customer
from datetime import datetime
import hashlib

def hash_password(password: str) -> str:
    """使用 SHA256 哈希密码（简单实现，生产环境建议使用 bcrypt）"""
    return hashlib.sha256(password.encode()).hexdigest()


def init_database():
    """初始化数据库"""
    print("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成！")
    
    db = SessionLocal()
    
    try:
        # 检查是否已有数据
        existing_user = db.query(User).first()
        if existing_user:
            print("数据库已初始化，跳过初始数据插入")
            return
        
        print("正在插入初始数据...")
        
        # 创建管理员用户
        admin = User(
            username="admin",
            password_hash=hash_password("admin123"),
            real_name="系统管理员",
            role="admin",
            phone="13800138000",
            email="admin@example.com",
            status="active"
        )
        db.add(admin)
        
        # 创建操作员用户
        operator = User(
            username="zhanggong",
            password_hash=hash_password("123456"),
            real_name="张工",
            role="operator",
            phone="13800138001",
            status="active"
        )
        db.add(operator)
        
        # 创建初始设备
        equipments = [
            Equipment(
                equipment_code="CR-5001",
                equipment_name="门座式起重机配件包",
                category="起重配件",
                storage_location="A区-01-04",
                purchase_price=50000.0,
                daily_rental_rate=800.0,
                status="在库",
                specifications="适用于10-50吨门座式起重机"
            ),
            Equipment(
                equipment_code="FL-2002",
                equipment_name="重油输送泵",
                category="流体设备",
                storage_location="B区-02-11",
                purchase_price=35000.0,
                daily_rental_rate=600.0,
                status="维修中",
                specifications="流量200L/min，压力10MPa"
            ),
            Equipment(
                equipment_code="CN-1022",
                equipment_name="绑扎杆 (100根/组)",
                category="固缚索具",
                storage_location="C区-03-08",
                purchase_price=8000.0,
                daily_rental_rate=120.0,
                status="在库",
                specifications="长度2-4米可调"
            ),
            Equipment(
                equipment_code="HY-3305",
                equipment_name="液压千斤顶 (50T)",
                category="液压工具",
                storage_location="A区-02-05",
                purchase_price=18000.0,
                daily_rental_rate=300.0,
                status="在库",
                specifications="最大承载50吨"
            ),
            Equipment(
                equipment_code="FB-8801",
                equipment_name="钢丝绳索 (100米)",
                category="固缚索具",
                storage_location="B区-05-12",
                purchase_price=12000.0,
                daily_rental_rate=200.0,
                status="在库",
                specifications="直径20mm，破断力150KN"
            )
        ]
        
        for equipment in equipments:
            db.add(equipment)
        
        # 创建初始客户
        customers = [
            Customer(
                customer_name="长宏海运",
                contact_person="王船长",
                phone="13900139001",
                email="changhong@example.com",
                address="上海市浦东新区港务大道123号",
                credit_rating="A"
            ),
            Customer(
                customer_name="远洋荣耀",
                contact_person="李经理",
                phone="13900139002",
                email="ocean@example.com",
                address="宁波市北仑区港口路456号",
                credit_rating="A"
            ),
            Customer(
                customer_name="太平洋航运",
                contact_person="赵总",
                phone="13900139003",
                email="pacific@example.com",
                address="深圳市盐田区海港路789号",
                credit_rating="B"
            ),
            Customer(
                customer_name="马士基物流",
                contact_person="陈主管",
                phone="13900139004",
                email="maersk@example.com",
                address="广州市南沙区港湾路321号",
                credit_rating="A"
            )
        ]
        
        for customer in customers:
            db.add(customer)
        
        db.commit()
        print("初始数据插入完成！")
        
        print("\n默认账户信息：")
        print("管理员 - 用户名: admin, 密码: admin123")
        print("操作员 - 用户名: zhanggong, 密码: 123456")
        
    except Exception as e:
        print(f"初始化失败: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_database()

