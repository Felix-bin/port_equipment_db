"""
数据库更新脚本
自动创建所有新表和添加新字段
"""
import sys
from sqlalchemy import text, inspect
from database import engine, Base
from models import (
    Equipment, Customer, LeaseOrder, OrderItem, Billing, 
    ReturnRecord, InspectionRecord, User, OperationLog,
    Supplier, InboundRecord, InboundItem, OutboundRecord, 
    OutboundItem, ReturnItem, MaintenanceRecord
)


def check_table_exists(table_name):
    """检查表是否存在"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


def check_column_exists(table_name, column_name):
    """检查表中的列是否存在"""
    inspector = inspect(engine)
    if not check_table_exists(table_name):
        return False
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def add_column_if_not_exists(table_name, column_name, column_definition):
    """如果列不存在则添加"""
    if not check_column_exists(table_name, column_name):
        sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"
        print(f"添加列: {table_name}.{column_name}")
        with engine.connect() as conn:
            conn.execute(text(sql))
            conn.commit()
        return True
    else:
        print(f"列已存在: {table_name}.{column_name}")
        return False


def update_existing_tables():
    """更新现有表结构"""
    print("\n" + "="*60)
    print("第一步：更新现有表结构")
    print("="*60)
    
    updates = []
    
    # 更新 equipment 表
    print("\n更新 equipment 表...")
    updates.append(add_column_if_not_exists(
        "equipment", "supplier", 
        "VARCHAR(200) COMMENT '供应商'"
    ))
    updates.append(add_column_if_not_exists(
        "equipment", "manufacturer", 
        "VARCHAR(200) COMMENT '制造商'"
    ))
    updates.append(add_column_if_not_exists(
        "equipment", "purchase_date", 
        "DATE COMMENT '采购日期'"
    ))
    updates.append(add_column_if_not_exists(
        "equipment", "warranty_date", 
        "DATE COMMENT '质保期限'"
    ))
    updates.append(add_column_if_not_exists(
        "equipment", "last_maintenance_date", 
        "DATE COMMENT '最后维护日期'"
    ))
    updates.append(add_column_if_not_exists(
        "equipment", "serial_number", 
        "VARCHAR(100) COMMENT '序列号'"
    ))
    
    # 更新 billing 表
    print("\n更新 billing 表...")
    updates.append(add_column_if_not_exists(
        "billing", "discount", 
        "FLOAT DEFAULT 0.0 COMMENT '折扣金额'"
    ))
    updates.append(add_column_if_not_exists(
        "billing", "payment_method", 
        "VARCHAR(20) COMMENT '支付方式'"
    ))
    updates.append(add_column_if_not_exists(
        "billing", "invoice_no", 
        "VARCHAR(50) COMMENT '发票号'"
    ))
    updates.append(add_column_if_not_exists(
        "billing", "paid_amount", 
        "FLOAT DEFAULT 0.0 COMMENT '已支付金额'"
    ))
    
    # 更新 return_records 表
    print("\n更新 return_records 表...")
    updates.append(add_column_if_not_exists(
        "return_records", "total_damage_fee", 
        "FLOAT DEFAULT 0.0 COMMENT '总损坏赔偿费'"
    ))
    
    updated_count = sum(updates)
    print(f"\n更新现有表完成，共添加 {updated_count} 个新字段")
    return updated_count > 0


def create_new_tables():
    """创建新表"""
    print("\n" + "="*60)
    print("第二步：创建新表")
    print("="*60)
    
    new_tables = [
        "suppliers",
        "inbound_records",
        "inbound_items",
        "outbound_records",
        "outbound_items",
        "return_items",
        "maintenance_records"
    ]
    
    created_tables = []
    for table_name in new_tables:
        if not check_table_exists(table_name):
            print(f"创建表: {table_name}")
            created_tables.append(table_name)
        else:
            print(f"表已存在: {table_name}")
    
    if created_tables:
        print(f"\n开始创建 {len(created_tables)} 个新表...")
        Base.metadata.create_all(bind=engine)
        print("新表创建完成")
    else:
        print("\n所有表都已存在，无需创建")
    
    return len(created_tables) > 0


def create_indexes():
    """创建索引"""
    print("\n" + "="*60)
    print("第三步：创建索引")
    print("="*60)
    
    indexes = [
        ("equipment", "idx_supplier", "supplier"),
        ("equipment", "idx_manufacturer", "manufacturer"),
        ("billing", "idx_invoice_no", "invoice_no"),
        ("billing", "idx_payment_method", "payment_method"),
    ]
    
    created = 0
    with engine.connect() as conn:
        for table_name, index_name, column_name in indexes:
            if check_table_exists(table_name) and check_column_exists(table_name, column_name):
                try:
                    sql = f"CREATE INDEX {index_name} ON {table_name}({column_name})"
                    conn.execute(text(sql))
                    conn.commit()
                    print(f"创建索引: {index_name} on {table_name}({column_name})")
                    created += 1
                except Exception as e:
                    if "Duplicate key name" in str(e) or "already exists" in str(e):
                        print(f"索引已存在: {index_name}")
                    else:
                        print(f"创建索引失败 {index_name}: {e}")
    
    print(f"\n索引创建完成，共创建 {created} 个新索引")
    return created > 0


def verify_database():
    """验证数据库结构"""
    print("\n" + "="*60)
    print("第四步：验证数据库结构")
    print("="*60)
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print(f"\n当前数据库共有 {len(tables)} 个表：")
    for table in sorted(tables):
        columns = inspector.get_columns(table)
        print(f"  - {table} ({len(columns)} 列)")
    
    # 检查关键表是否存在
    required_tables = [
        "equipment", "customers", "lease_orders", "order_items",
        "billing", "return_records", "inspection_records",
        "users", "operation_logs", "suppliers", "inbound_records",
        "inbound_items", "outbound_records", "outbound_items",
        "return_items", "maintenance_records"
    ]
    
    missing_tables = [t for t in required_tables if t not in tables]
    
    if missing_tables:
        print(f"\n⚠️ 警告：缺少以下表：")
        for table in missing_tables:
            print(f"  - {table}")
        return False
    else:
        print("\n✅ 所有必需的表都已存在")
        return True


def main():
    """主函数"""
    print("="*60)
    print("数据库更新脚本")
    print("="*60)
    print(f"数据库: {engine.url.database}")
    print(f"主机: {engine.url.host}:{engine.url.port}")
    print("="*60)
    
    try:
        # 测试数据库连接
        print("\n测试数据库连接...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        print("✅ 数据库连接成功")
        
        # 备份提醒
        print("\n" + "⚠️ "*20)
        print("重要提醒：执行数据库更新前，请先备份数据库！")
        print("⚠️ "*20)
        response = input("\n是否已经备份数据库？(yes/no): ")
        if response.lower() not in ['yes', 'y', '是']:
            print("请先备份数据库后再运行此脚本")
            return
        
        # 执行更新
        updated = update_existing_tables()
        created = create_new_tables()
        indexed = create_indexes()
        verified = verify_database()
        
        # 总结
        print("\n" + "="*60)
        print("数据库更新完成")
        print("="*60)
        if updated or created or indexed:
            print("✅ 数据库已成功更新")
            if updated:
                print("  - 更新了现有表结构")
            if created:
                print("  - 创建了新表")
            if indexed:
                print("  - 创建了新索引")
        else:
            print("ℹ️ 数据库已是最新版本，无需更新")
        
        if verified:
            print("\n✅ 数据库验证通过")
        else:
            print("\n⚠️ 数据库验证失败，请检查")
            
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

