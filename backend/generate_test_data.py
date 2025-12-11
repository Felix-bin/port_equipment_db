"""
测试数据生成脚本
为港口装备租赁系统生成大量测试数据
"""
import random
from datetime import datetime, timedelta
from faker import Faker
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from models import (
    Equipment, Customer, LeaseOrder, OrderItem, Billing,
    ReturnRecord, InspectionRecord, User, Supplier,
    InboundRecord, InboundItem, OutboundRecord, OutboundItem,
    ReturnItem, MaintenanceRecord,
    EquipmentStatus, OrderStatus, BillingStatus, InspectionResult,
    InboundStatus, OutboundStatus, MaintenanceStatus, MaintenanceType,
    EquipmentCondition, PaymentMethod
)
import crud

# 初始化 Faker（支持中文）
fake = Faker('zh_CN')

# 配置：生成数据的数量
CONFIG = {
    'suppliers': 20,          # 供应商
    'customers': 50,          # 客户
    'users': 10,              # 用户
    'equipment': 200,         # 设备
    'inbound_records': 30,    # 入库记录
    'orders': 100,            # 租赁订单
    'outbound_records': 80,   # 出库记录
    'return_records': 60,     # 归还记录
    'maintenance_records': 40, # 维修记录
}


class DataGenerator:
    def __init__(self, db: Session):
        self.db = db
        self.suppliers = []
        self.customers = []
        self.users = []
        self.equipment = []
        self.inbound_records = []
        self.orders = []
        
    def generate_all(self):
        """生成所有测试数据"""
        print("="*60)
        print("开始生成测试数据")
        print("="*60)
        
        self.generate_users()
        self.generate_suppliers()
        self.generate_customers()
        self.generate_inbound_and_equipment()
        self.generate_orders()
        self.generate_outbound_records()
        self.generate_return_records()
        self.generate_maintenance_records()
        
        print("\n" + "="*60)
        print("测试数据生成完成！")
        print("="*60)
        self.print_summary()
    
    def generate_users(self):
        """生成用户数据"""
        print(f"\n生成 {CONFIG['users']} 个用户...")
        roles = ['admin', 'warehouse', 'finance', 'operator']
        
        # 检查现有用户数量，避免重复
        existing_count = self.db.query(User).filter(User.username.like('user%')).count()
        start_index = existing_count + 1
        
        for i in range(CONFIG['users']):
            username = f"user{start_index + i:03d}"
            
            # 检查用户名是否已存在
            existing_user = self.db.query(User).filter(User.username == username).first()
            if existing_user:
                print(f"⚠️ 用户 {username} 已存在，跳过")
                continue
            
            user = User(
                username=username,
                password_hash=crud.hash_password("123456"),
                real_name=fake.name(),
                role=random.choice(roles),
                phone=fake.phone_number(),
                email=fake.email(),
                status='active'
            )
            self.db.add(user)
            self.users.append(user)
        
        self.db.commit()
        print(f"✅ 已生成 {len(self.users)} 个用户")
    
    def generate_suppliers(self):
        """生成供应商数据"""
        print(f"\n生成 {CONFIG['suppliers']} 个供应商...")
        
        # 检查现有供应商数量
        existing_count = self.db.query(Supplier).count()
        start_index = existing_count + 1
        
        for i in range(CONFIG['suppliers']):
            supplier_code = f"SUP{start_index + i:04d}"
            
            # 检查供应商编号是否已存在
            existing_supplier = self.db.query(Supplier).filter(Supplier.supplier_code == supplier_code).first()
            if existing_supplier:
                print(f"⚠️ 供应商 {supplier_code} 已存在，跳过")
                continue
            
            supplier = Supplier(
                supplier_code=supplier_code,
                supplier_name=f"{fake.company()}供应商{start_index + i:02d}",
                contact_person=fake.name(),
                phone=fake.phone_number(),
                email=fake.company_email(),
                address=fake.address(),
                bank_account=fake.credit_card_number(),
                credit_rating=random.choice(['A+', 'A', 'B+', 'B', 'C']),
                remarks=fake.sentence() if random.random() > 0.5 else None
            )
            self.db.add(supplier)
            self.suppliers.append(supplier)
        
        self.db.commit()
        print(f"✅ 已生成 {len(self.suppliers)} 个供应商")
    
    def generate_customers(self):
        """生成客户数据"""
        print(f"\n生成 {CONFIG['customers']} 个客户...")
        
        # 检查现有客户数量
        existing_count = self.db.query(Customer).count()
        start_index = existing_count + 1
        
        for i in range(CONFIG['customers']):
            customer_name = f"{fake.company()}_{start_index + i:04d}"
            
            # 检查客户名称是否已存在
            existing_customer = self.db.query(Customer).filter(Customer.customer_name == customer_name).first()
            if existing_customer:
                # 如果重复，添加时间戳
                customer_name = f"{fake.company()}_{start_index + i:04d}_{datetime.now().strftime('%H%M%S')}"
            
            customer = Customer(
                customer_name=customer_name,
                contact_person=fake.name(),
                phone=fake.phone_number(),
                email=fake.company_email(),
                address=fake.address(),
                credit_rating=random.choice(['A+', 'A', 'B+', 'B', 'C'])
            )
            self.db.add(customer)
            self.customers.append(customer)
        
        self.db.commit()
        print(f"✅ 已生成 {len(self.customers)} 个客户")
    
    def generate_inbound_and_equipment(self):
        """生成入库记录和设备数据"""
        print(f"\n生成 {CONFIG['inbound_records']} 条入库记录和 {CONFIG['equipment']} 个设备...")
        
        equipment_types = ['起重机', '叉车', '集装箱', '装卸机', '牵引车', '堆高机']
        manufacturers = ['三一重工', '中联重科', '徐工集团', '柳工', '山推股份']
        
        # 检查现有设备数量
        existing_equipment_count = self.db.query(Equipment).count()
        equipment_count = existing_equipment_count
        equipment_per_inbound = CONFIG['equipment'] // CONFIG['inbound_records']
        
        # 检查现有入库记录数量
        existing_inbound_count = self.db.query(InboundRecord).count()
        
        for i in range(CONFIG['inbound_records']):
            # 创建入库记录
            supplier = random.choice(self.suppliers) if self.suppliers else None
            if not supplier:
                print("⚠️ 没有供应商，跳过入库记录生成")
                break
            
            total_qty = random.randint(3, 10)
            
            purchase_date = fake.date_between(start_date='-2y', end_date='today')
            inbound_code = f"IN{datetime.now().strftime('%Y%m%d%H%M')}{existing_inbound_count + i + 1:05d}"
            
            # 检查入库单号是否已存在
            existing_inbound = self.db.query(InboundRecord).filter(InboundRecord.inbound_code == inbound_code).first()
            if existing_inbound:
                inbound_code = f"IN{datetime.now().strftime('%Y%m%d%H%M%S')}{i+1:05d}"
            
            inbound_record = InboundRecord(
                inbound_code=inbound_code,
                supplier=supplier.supplier_name,
                purchase_date=purchase_date,
                inbound_date=fake.date_time_between(start_date='-2y', end_date='now'),
                operator=random.choice(self.users).real_name if self.users else fake.name(),
                total_quantity=total_qty,
                total_amount=round(random.uniform(50000, 500000), 2),
                status=InboundStatus.COMPLETED,
                remarks=fake.sentence() if random.random() > 0.7 else None
            )
            self.db.add(inbound_record)
            self.db.flush()
            self.inbound_records.append(inbound_record)
            
            # 为这条入库记录创建设备
            for j in range(min(total_qty, equipment_per_inbound)):
                if equipment_count >= CONFIG['equipment']:
                    break
                
                category = random.choice(equipment_types)
                manufacturer = random.choice(manufacturers)
                
                equipment_code = f"EQ{equipment_count+1:06d}"
                
                # 检查设备编号是否已存在
                existing_equipment = self.db.query(Equipment).filter(Equipment.equipment_code == equipment_code).first()
                if existing_equipment:
                    # 如果重复，使用时间戳
                    equipment_code = f"EQ{datetime.now().strftime('%Y%m%d%H%M%S')}{equipment_count+1:04d}"
                
                equipment = Equipment(
                    equipment_code=equipment_code,
                    equipment_name=f"{category}-{manufacturer}-{equipment_count+1:04d}",
                    category=category,
                    status=random.choice([
                        EquipmentStatus.IN_STOCK,
                        EquipmentStatus.IN_STOCK,
                        EquipmentStatus.IN_STOCK,
                        EquipmentStatus.OUT
                    ]),
                    storage_location=f"{random.choice(['A', 'B', 'C', 'D'])}区{random.randint(1, 20):02d}号",
                    purchase_price=round(random.uniform(50000, 800000), 2),
                    daily_rental_rate=round(random.uniform(200, 3000), 2),
                    specifications=f"{random.randint(3, 50)}吨",
                    supplier=supplier.supplier_name,
                    manufacturer=manufacturer,
                    purchase_date=inbound_record.purchase_date,
                    warranty_date=inbound_record.purchase_date + timedelta(days=365*random.randint(1, 3)),
                    serial_number=f"SN{equipment_count+1:010d}",
                    remarks=f"供应商: {supplier.supplier_name}"
                )
                self.db.add(equipment)
                self.db.flush()
                self.equipment.append(equipment)
                equipment_count += 1
                
                # 创建入库明细
                inbound_item = InboundItem(
                    inbound_id=inbound_record.inbound_id,
                    equipment_id=equipment.equipment_id,
                    equipment_code=equipment.equipment_code,
                    equipment_name=equipment.equipment_name,
                    category=equipment.category,
                    specifications=equipment.specifications,
                    quantity=1,
                    unit_price=equipment.purchase_price,
                    subtotal=equipment.purchase_price,
                    storage_location=equipment.storage_location
                )
                self.db.add(inbound_item)
        
        self.db.commit()
        print(f"✅ 已生成 {len(self.inbound_records)} 条入库记录")
        print(f"✅ 已生成 {len(self.equipment)} 个设备")
    
    def generate_orders(self):
        """生成租赁订单"""
        print(f"\n生成 {CONFIG['orders']} 个租赁订单...")
        
        for i in range(CONFIG['orders']):
            customer = random.choice(self.customers)
            start_date = fake.date_between(start_date='-1y', end_date='today')
            
            # 随机选择订单状态
            status_choices = [OrderStatus.PENDING, OrderStatus.IN_PROGRESS, OrderStatus.COMPLETED]
            order_status = random.choice(status_choices)
            
            # 根据状态设置日期
            if order_status == OrderStatus.COMPLETED:
                expected_return = start_date + timedelta(days=random.randint(7, 90))
                actual_return = expected_return + timedelta(days=random.randint(-3, 5))
            elif order_status == OrderStatus.IN_PROGRESS:
                expected_return = start_date + timedelta(days=random.randint(7, 90))
                actual_return = None
            else:
                expected_return = start_date + timedelta(days=random.randint(7, 90))
                actual_return = None
            
            order = LeaseOrder(
                order_code=f"ORD{datetime.now().strftime('%Y%m%d%H%M')}{i+1:06d}",
                customer_id=customer.customer_id,
                customer_name=customer.customer_name,
                voyage_no=f"V{datetime.now().strftime('%Y%m')}{random.randint(1000, 9999)}" if random.random() > 0.3 else None,
                start_date=start_date,
                expected_return_date=expected_return,
                actual_return_date=actual_return,
                status=order_status,
                total_amount=0,  # 稍后计算
                remarks=fake.sentence() if random.random() > 0.6 else None,
                created_by=random.choice(self.users).real_name if self.users else fake.name()
            )
            self.db.add(order)
            self.db.flush()
            
            # 为订单添加设备明细
            num_items = random.randint(1, 5)
            total_amount = 0
            
            for _ in range(num_items):
                equipment = random.choice(self.equipment)
                rental_days = (expected_return - start_date).days
                daily_rate = equipment.daily_rental_rate
                subtotal = daily_rate * rental_days
                total_amount += subtotal
                
                order_item = OrderItem(
                    order_id=order.order_id,
                    equipment_id=equipment.equipment_id,
                    equipment_code=equipment.equipment_code,
                    equipment_name=equipment.equipment_name,
                    daily_rate=daily_rate,
                    rental_days=rental_days,
                    subtotal=subtotal
                )
                self.db.add(order_item)
            
            order.total_amount = round(total_amount, 2)
            self.orders.append(order)
            
            # 为已完成的订单创建账单
            if order_status in [OrderStatus.COMPLETED, OrderStatus.IN_PROGRESS]:
                self.generate_billing(order)
        
        self.db.commit()
        print(f"✅ 已生成 {len(self.orders)} 个订单")
    
    def generate_billing(self, order: LeaseOrder):
        """为订单生成账单"""
        repair_fee = round(random.uniform(0, 5000), 2) if random.random() > 0.7 else 0
        other_fee = round(random.uniform(0, 2000), 2) if random.random() > 0.8 else 0
        discount = round(order.total_amount * random.uniform(0, 0.1), 2) if random.random() > 0.6 else 0
        
        billing_status = BillingStatus.PAID if order.status == OrderStatus.COMPLETED else random.choice([
            BillingStatus.PENDING, BillingStatus.CONFIRMED
        ])
        
        total = order.total_amount + repair_fee + other_fee - discount
        paid = total if billing_status == BillingStatus.PAID else round(total * random.uniform(0, 0.8), 2)
        
        billing = Billing(
            bill_code=f"BILL{datetime.now().strftime('%Y%m%d%H%M')}{order.order_id:06d}",
            order_id=order.order_id,
            customer_name=order.customer_name,
            rental_fee=order.total_amount,
            repair_fee=repair_fee,
            other_fee=other_fee,
            discount=discount,
            total_amount=total,
            status=billing_status,
            billing_date=order.start_date + timedelta(days=random.randint(1, 5)),
            payment_date=datetime.now().date() if billing_status == BillingStatus.PAID else None,
            payment_method=random.choice([PaymentMethod.TRANSFER, PaymentMethod.CASH]) if billing_status == BillingStatus.PAID else None,
            invoice_no=f"INV{datetime.now().strftime('%Y%m%d')}{order.order_id:08d}" if billing_status == BillingStatus.PAID else None,
            paid_amount=paid,
            remarks=fake.sentence() if random.random() > 0.7 else None
        )
        self.db.add(billing)
    
    def generate_outbound_records(self):
        """生成出库记录"""
        print(f"\n生成 {CONFIG['outbound_records']} 条出库记录...")
        
        completed_orders = [o for o in self.orders if o.status in [OrderStatus.IN_PROGRESS, OrderStatus.COMPLETED]]
        
        for i in range(min(CONFIG['outbound_records'], len(completed_orders))):
            order = completed_orders[i]
            
            outbound = OutboundRecord(
                outbound_code=f"OUT{datetime.now().strftime('%Y%m%d%H%M')}{i+1:05d}",
                order_id=order.order_id,
                outbound_date=order.start_date + timedelta(hours=random.randint(1, 24)),
                operator=random.choice(self.users).real_name if self.users else fake.name(),
                recipient=order.customer_name,
                recipient_phone=fake.phone_number(),
                total_quantity=len(order.order_items),
                status=OutboundStatus.COMPLETED,
                remarks=fake.sentence() if random.random() > 0.7 else None
            )
            self.db.add(outbound)
            self.db.flush()
            
            # 创建出库明细
            for item in order.order_items:
                outbound_item = OutboundItem(
                    outbound_id=outbound.outbound_id,
                    equipment_id=item.equipment_id,
                    equipment_code=item.equipment_code,
                    equipment_name=item.equipment_name,
                    quantity=1,
                    daily_rate=item.daily_rate
                )
                self.db.add(outbound_item)
        
        self.db.commit()
        print(f"✅ 已生成 {CONFIG['outbound_records']} 条出库记录")
    
    def generate_return_records(self):
        """生成归还记录和质检记录"""
        print(f"\n生成 {CONFIG['return_records']} 条归还记录...")
        
        completed_orders = [o for o in self.orders if o.status == OrderStatus.COMPLETED and o.actual_return_date]
        
        for i in range(min(CONFIG['return_records'], len(completed_orders))):
            order = completed_orders[i]
            
            return_record = ReturnRecord(
                return_code=f"RET{datetime.now().strftime('%Y%m%d%H%M')}{i+1:05d}",
                order_id=order.order_id,
                voyage_no=order.voyage_no,
                return_date=order.actual_return_date + timedelta(hours=random.randint(1, 12)),
                return_person=fake.name(),
                equipment_count=len(order.order_items),
                inspection_status="质检通过" if random.random() > 0.2 else "质检不通过",
                total_damage_fee=0,
                remarks=fake.sentence() if random.random() > 0.7 else None
            )
            self.db.add(return_record)
            self.db.flush()
            
            total_damage = 0
            
            # 为每个设备创建归还明细和质检记录
            for item in order.order_items:
                condition = random.choice([
                    EquipmentCondition.GOOD,
                    EquipmentCondition.GOOD,
                    EquipmentCondition.NORMAL,
                    EquipmentCondition.DAMAGED
                ])
                
                damage_fee = 0
                if condition == EquipmentCondition.DAMAGED:
                    damage_fee = round(random.uniform(1000, 10000), 2)
                    total_damage += damage_fee
                
                return_item = ReturnItem(
                    return_id=return_record.return_id,
                    equipment_id=item.equipment_id,
                    equipment_code=item.equipment_code,
                    equipment_name=item.equipment_name,
                    equipment_condition=condition,
                    damage_description=fake.sentence() if condition == EquipmentCondition.DAMAGED else None,
                    damage_fee=damage_fee
                )
                self.db.add(return_item)
                
                # 创建质检记录
                inspection = InspectionRecord(
                    return_id=return_record.return_id,
                    equipment_id=item.equipment_id,
                    equipment_code=item.equipment_code,
                    inspector=fake.name(),
                    appearance_status="完好" if condition == EquipmentCondition.GOOD else "轻微磨损" if condition == EquipmentCondition.NORMAL else "严重损坏",
                    function_test="通过" if condition != EquipmentCondition.DAMAGED else "故障",
                    repair_needed=1 if condition == EquipmentCondition.DAMAGED else 0,
                    repair_cost=damage_fee * 0.8 if damage_fee > 0 else 0,
                    result=InspectionResult.PASS if condition != EquipmentCondition.DAMAGED else InspectionResult.REPAIR_NEEDED,
                    inspection_date=return_record.return_date + timedelta(hours=random.randint(1, 4)),
                    remarks=fake.sentence() if random.random() > 0.7 else None
                )
                self.db.add(inspection)
            
            return_record.total_damage_fee = round(total_damage, 2)
        
        self.db.commit()
        print(f"✅ 已生成 {CONFIG['return_records']} 条归还记录")
    
    def generate_maintenance_records(self):
        """生成维修记录"""
        print(f"\n生成 {CONFIG['maintenance_records']} 条维修记录...")
        
        for i in range(CONFIG['maintenance_records']):
            equipment = random.choice(self.equipment)
            maintenance_date = fake.date_time_between(start_date='-1y', end_date='now')
            
            status = random.choice([
                MaintenanceStatus.COMPLETED,
                MaintenanceStatus.COMPLETED,
                MaintenanceStatus.IN_PROGRESS,
                MaintenanceStatus.PENDING
            ])
            
            parts_cost = round(random.uniform(500, 5000), 2)
            labor_cost = round(random.uniform(300, 2000), 2)
            
            maintenance = MaintenanceRecord(
                maintenance_code=f"MNT{datetime.now().strftime('%Y%m%d%H%M')}{i+1:05d}",
                equipment_id=equipment.equipment_id,
                equipment_code=equipment.equipment_code,
                maintenance_type=random.choice([MaintenanceType.ROUTINE, MaintenanceType.REPAIR, MaintenanceType.OVERHAUL]),
                problem_description=fake.sentence(),
                maintenance_content=fake.paragraph(),
                maintenance_date=maintenance_date,
                completion_date=maintenance_date + timedelta(days=random.randint(1, 7)) if status == MaintenanceStatus.COMPLETED else None,
                technician=fake.name(),
                maintenance_cost=parts_cost + labor_cost,
                parts_cost=parts_cost,
                labor_cost=labor_cost,
                status=status,
                remarks=fake.sentence() if random.random() > 0.7 else None
            )
            self.db.add(maintenance)
            
            # 更新设备的最后维护日期
            if status == MaintenanceStatus.COMPLETED:
                equipment.last_maintenance_date = maintenance_date.date()
        
        self.db.commit()
        print(f"✅ 已生成 {CONFIG['maintenance_records']} 条维修记录")
    
    def print_summary(self):
        """打印生成的数据统计"""
        print("\n📊 数据统计：")
        print(f"  - 用户: {len(self.users)}")
        print(f"  - 供应商: {len(self.suppliers)}")
        print(f"  - 客户: {len(self.customers)}")
        print(f"  - 设备: {len(self.equipment)}")
        print(f"  - 入库记录: {len(self.inbound_records)}")
        print(f"  - 租赁订单: {len(self.orders)}")
        
        # 统计数据库中的记录
        outbound_count = self.db.query(OutboundRecord).count()
        return_count = self.db.query(ReturnRecord).count()
        billing_count = self.db.query(Billing).count()
        maintenance_count = self.db.query(MaintenanceRecord).count()
        
        print(f"  - 出库记录: {outbound_count}")
        print(f"  - 归还记录: {return_count}")
        print(f"  - 账单: {billing_count}")
        print(f"  - 维修记录: {maintenance_count}")


def main():
    """主函数"""
    print("="*60)
    print("测试数据生成器")
    print("="*60)
    print("将生成以下数据：")
    for key, value in CONFIG.items():
        print(f"  - {key}: {value}")
    print("="*60)
    
    response = input("\n确认生成测试数据？(yes/no): ")
    if response.lower() not in ['yes', 'y', '是']:
        print("已取消")
        return
    
    print("\n⚠️ 注意：这将向数据库添加大量测试数据！")
    response = input("确定继续？(yes/no): ")
    if response.lower() not in ['yes', 'y', '是']:
        print("已取消")
        return
    
    db = SessionLocal()
    try:
        generator = DataGenerator(db)
        generator.generate_all()
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()

