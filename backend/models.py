from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Enum, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import enum


# 枚举类型定义
class EquipmentStatus(str, enum.Enum):
    IN_STOCK = "在库"
    OUT = "已出库"
    MAINTENANCE = "维修中"
    SCRAPPED = "已报废"


class OrderStatus(str, enum.Enum):
    PENDING = "待提货"
    IN_PROGRESS = "航次执行中"
    COMPLETED = "已完结"
    CANCELLED = "已取消"


class BillingStatus(str, enum.Enum):
    PENDING = "待确认"
    CONFIRMED = "已确认"
    PAID = "已结清"
    OVERDUE = "逾期"


class InspectionResult(str, enum.Enum):
    PASS = "合格"
    REPAIR_NEEDED = "需维修"
    FAILED = "不合格"


class InboundStatus(str, enum.Enum):
    PENDING = "待确认"
    COMPLETED = "已完成"
    CANCELLED = "已取消"


class OutboundStatus(str, enum.Enum):
    PENDING = "待出库"
    COMPLETED = "已完成"
    CANCELLED = "已取消"


class MaintenanceType(str, enum.Enum):
    ROUTINE = "例行维护"
    REPAIR = "维修"
    OVERHAUL = "大修"


class MaintenanceStatus(str, enum.Enum):
    PENDING = "待维修"
    IN_PROGRESS = "维修中"
    COMPLETED = "已完成"
    CANCELLED = "已取消"


class EquipmentCondition(str, enum.Enum):
    GOOD = "完好"
    NORMAL = "正常"
    DAMAGED = "损坏"


class PaymentMethod(str, enum.Enum):
    CASH = "现金"
    TRANSFER = "转账"
    CHECK = "支票"
    OTHER = "其他"


# 设备表
class Equipment(Base):
    __tablename__ = "equipment"

    equipment_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    equipment_code = Column(String(50), unique=True, nullable=False, index=True)
    equipment_name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    status = Column(Enum(EquipmentStatus), default=EquipmentStatus.IN_STOCK, nullable=False, index=True)
    storage_location = Column(String(100))
    purchase_price = Column(Float, default=0.0)
    daily_rental_rate = Column(Float, default=0.0)
    specifications = Column(Text)
    remarks = Column(Text)
    # 新增字段
    supplier = Column(String(200), index=True)  # 供应商
    manufacturer = Column(String(200))  # 制造商
    purchase_date = Column(Date)  # 采购日期
    warranty_date = Column(Date)  # 质保期限
    last_maintenance_date = Column(Date)  # 最后维护日期
    serial_number = Column(String(100))  # 序列号
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    is_deleted = Column(Integer, default=0)

    # 关系
    order_items = relationship("OrderItem", back_populates="equipment")
    inspection_records = relationship("InspectionRecord", back_populates="equipment")
    inbound_items = relationship("InboundItem", back_populates="equipment")
    maintenance_records = relationship("MaintenanceRecord", back_populates="equipment")


# 客户表
class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_name = Column(String(200), nullable=False, unique=True)
    contact_person = Column(String(100))
    phone = Column(String(50))
    email = Column(String(100))
    address = Column(String(500))
    credit_rating = Column(String(20))
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    is_deleted = Column(Integer, default=0)

    # 关系
    lease_orders = relationship("LeaseOrder", back_populates="customer")


# 租赁订单表
class LeaseOrder(Base):
    __tablename__ = "lease_orders"

    order_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_code = Column(String(50), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    customer_name = Column(String(200), nullable=False)
    voyage_no = Column(String(100), index=True)
    start_date = Column(Date, nullable=False)
    expected_return_date = Column(Date)
    actual_return_date = Column(Date)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False, index=True)
    total_amount = Column(Float, default=0.0)
    remarks = Column(Text)
    created_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    is_deleted = Column(Integer, default=0)

    # 关系
    customer = relationship("Customer", back_populates="lease_orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    billing = relationship("Billing", back_populates="order", uselist=False)


# 订单明细表
class OrderItem(Base):
    __tablename__ = "order_items"

    item_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("lease_orders.order_id"), nullable=False)
    equipment_id = Column(Integer, ForeignKey("equipment.equipment_id"), nullable=False)
    equipment_code = Column(String(50), nullable=False)
    equipment_name = Column(String(200), nullable=False)
    daily_rate = Column(Float, nullable=False)
    rental_days = Column(Integer, default=0)
    subtotal = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    # 关系
    order = relationship("LeaseOrder", back_populates="order_items")
    equipment = relationship("Equipment", back_populates="order_items")


# 账单表
class Billing(Base):
    __tablename__ = "billing"

    bill_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    bill_code = Column(String(50), unique=True, nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("lease_orders.order_id"), nullable=False)
    customer_name = Column(String(200), nullable=False)
    rental_fee = Column(Float, default=0.0)
    repair_fee = Column(Float, default=0.0)
    other_fee = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    status = Column(Enum(BillingStatus), default=BillingStatus.PENDING, nullable=False, index=True)
    billing_date = Column(Date, default=datetime.now().date)
    payment_date = Column(Date)
    # 新增字段
    discount = Column(Float, default=0.0)  # 折扣金额
    payment_method = Column(Enum(PaymentMethod), index=True)  # 支付方式
    invoice_no = Column(String(50), index=True)  # 发票号
    paid_amount = Column(Float, default=0.0)  # 已支付金额
    remarks = Column(Text)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    is_deleted = Column(Integer, default=0)

    # 关系
    order = relationship("LeaseOrder", back_populates="billing")


# 归还记录表
class ReturnRecord(Base):
    __tablename__ = "return_records"

    return_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    return_code = Column(String(50), unique=True, nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("lease_orders.order_id"), nullable=False)
    voyage_no = Column(String(100))
    return_date = Column(DateTime, default=datetime.now, nullable=False)
    return_person = Column(String(100))
    equipment_count = Column(Integer, default=0)
    inspection_status = Column(String(50), default="待质检")
    total_damage_fee = Column(Float, default=0.0)  # 新增：总损坏赔偿费
    remarks = Column(Text)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    # 关系
    inspection_records = relationship("InspectionRecord", back_populates="return_record")
    return_items = relationship("ReturnItem", back_populates="return_record", cascade="all, delete-orphan")


# 质检记录表
class InspectionRecord(Base):
    __tablename__ = "inspection_records"

    inspection_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    return_id = Column(Integer, ForeignKey("return_records.return_id"), nullable=False)
    equipment_id = Column(Integer, ForeignKey("equipment.equipment_id"), nullable=False)
    equipment_code = Column(String(50), nullable=False)
    inspector = Column(String(100), nullable=False)
    appearance_status = Column(String(50))  # 完好、轻微磨损、严重损坏
    function_test = Column(String(50))  # 通过、故障
    repair_needed = Column(Integer, default=0)  # 0-否, 1-是
    repair_cost = Column(Float, default=0.0)
    result = Column(Enum(InspectionResult), default=InspectionResult.PASS)
    inspection_date = Column(DateTime, default=datetime.now, nullable=False)
    remarks = Column(Text)
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    # 关系
    return_record = relationship("ReturnRecord", back_populates="inspection_records")
    equipment = relationship("Equipment", back_populates="inspection_records")


# 用户表
class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    real_name = Column(String(100))
    role = Column(String(50), default="operator")  # admin, warehouse, finance, operator
    phone = Column(String(50))
    email = Column(String(100))
    status = Column(String(20), default="active")  # active, inactive
    last_login = Column(DateTime)
    # 用户信息扩展字段
    nickname = Column(String(100))  # 昵称
    address = Column(String(500))  # 地址
    profile = Column(Text)  # 个人简介
    country_region = Column(String(100))  # 国家/地区
    area = Column(String(200))  # 地区
    avatar = Column(String(500))  # 头像URL
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    is_deleted = Column(Integer, default=0)


# 操作日志表
class OperationLog(Base):
    __tablename__ = "operation_logs"

    log_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer)
    username = Column(String(100))
    action = Column(String(50), nullable=False)  # INSERT, UPDATE, DELETE, QUERY
    table_name = Column(String(100))
    record_id = Column(String(100))
    description = Column(Text)
    ip_address = Column(String(50))
    created_at = Column(DateTime, default=datetime.now, nullable=False, index=True)


class TriggerLog(Base):
    __tablename__ = "trigger_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    log_type = Column(String(20), nullable=False, index=True)  # success, info, warning, error
    trigger_name = Column(String(100), nullable=False, index=True)  # 触发器名称
    operation = Column(String(50), nullable=False)  # 操作类型
    table_name = Column(String(100))  # 影响的表名
    record_id = Column(Integer)  # 记录ID
    description = Column(Text)  # 描述
    created_at = Column(DateTime, default=datetime.now, nullable=False, index=True)


# ============================================================
# 新增业务表
# ============================================================

# 供应商表
class Supplier(Base):
    __tablename__ = "suppliers"

    supplier_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    supplier_code = Column(String(50), unique=True, nullable=False, index=True)
    supplier_name = Column(String(200), nullable=False, index=True)
    contact_person = Column(String(100))
    phone = Column(String(50))
    email = Column(String(100))
    address = Column(String(500))
    bank_account = Column(String(100))
    credit_rating = Column(String(20))
    remarks = Column(Text)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    is_deleted = Column(Integer, default=0)


# 入库记录主表
class InboundRecord(Base):
    __tablename__ = "inbound_records"

    inbound_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    inbound_code = Column(String(50), unique=True, nullable=False, index=True)
    supplier = Column(String(200))
    purchase_date = Column(Date)
    inbound_date = Column(DateTime, default=datetime.now, nullable=False)
    operator = Column(String(100))
    total_quantity = Column(Integer, default=0)
    total_amount = Column(Float, default=0.0)
    status = Column(Enum(InboundStatus), default=InboundStatus.PENDING, nullable=False, index=True)
    remarks = Column(Text)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    is_deleted = Column(Integer, default=0)

    # 关系
    items = relationship("InboundItem", back_populates="inbound_record", cascade="all, delete-orphan")


# 入库明细表
class InboundItem(Base):
    __tablename__ = "inbound_items"

    item_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    inbound_id = Column(Integer, ForeignKey("inbound_records.inbound_id"), nullable=False)
    equipment_id = Column(Integer, ForeignKey("equipment.equipment_id"))
    equipment_code = Column(String(50), nullable=False, index=True)
    equipment_name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False)
    specifications = Column(Text)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, default=0.0)
    subtotal = Column(Float, default=0.0)
    storage_location = Column(String(100))
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    # 关系
    inbound_record = relationship("InboundRecord", back_populates="items")
    equipment = relationship("Equipment", back_populates="inbound_items")


# 出库记录主表
class OutboundRecord(Base):
    __tablename__ = "outbound_records"

    outbound_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    outbound_code = Column(String(50), unique=True, nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("lease_orders.order_id"))
    outbound_date = Column(DateTime, default=datetime.now, nullable=False)
    operator = Column(String(100))
    recipient = Column(String(100))
    recipient_phone = Column(String(50))
    total_quantity = Column(Integer, default=0)
    status = Column(Enum(OutboundStatus), default=OutboundStatus.COMPLETED, nullable=False, index=True)
    remarks = Column(Text)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    is_deleted = Column(Integer, default=0)

    # 关系
    items = relationship("OutboundItem", back_populates="outbound_record", cascade="all, delete-orphan")


# 出库明细表
class OutboundItem(Base):
    __tablename__ = "outbound_items"

    item_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    outbound_id = Column(Integer, ForeignKey("outbound_records.outbound_id"), nullable=False)
    equipment_id = Column(Integer, ForeignKey("equipment.equipment_id"), nullable=False)
    equipment_code = Column(String(50), nullable=False)
    equipment_name = Column(String(200), nullable=False)
    quantity = Column(Integer, default=1)
    daily_rate = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    # 关系
    outbound_record = relationship("OutboundRecord", back_populates="items")


# 归还明细表
class ReturnItem(Base):
    __tablename__ = "return_items"

    item_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    return_id = Column(Integer, ForeignKey("return_records.return_id"), nullable=False)
    equipment_id = Column(Integer, ForeignKey("equipment.equipment_id"), nullable=False)
    equipment_code = Column(String(50), nullable=False)
    equipment_name = Column(String(200), nullable=False)
    equipment_condition = Column(Enum(EquipmentCondition), default=EquipmentCondition.GOOD, index=True)
    damage_description = Column(Text)
    damage_fee = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    # 关系
    return_record = relationship("ReturnRecord", back_populates="return_items")


# 设备维修记录表
class MaintenanceRecord(Base):
    __tablename__ = "maintenance_records"

    maintenance_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    maintenance_code = Column(String(50), unique=True, nullable=False, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.equipment_id"), nullable=False)
    equipment_code = Column(String(50), nullable=False)
    maintenance_type = Column(Enum(MaintenanceType), default=MaintenanceType.ROUTINE)
    problem_description = Column(Text)
    maintenance_content = Column(Text)
    maintenance_date = Column(DateTime, default=datetime.now, nullable=False)
    completion_date = Column(DateTime)
    technician = Column(String(100))
    maintenance_cost = Column(Float, default=0.0)
    parts_cost = Column(Float, default=0.0)
    labor_cost = Column(Float, default=0.0)
    status = Column(Enum(MaintenanceStatus), default=MaintenanceStatus.PENDING, nullable=False, index=True)
    remarks = Column(Text)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    is_deleted = Column(Integer, default=0)

    # 关系
    equipment = relationship("Equipment", back_populates="maintenance_records")

