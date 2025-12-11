from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import datetime, date
import models
import schemas
import hashlib

def hash_password(password: str) -> str:
    """使用 SHA256 哈希密码"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return hash_password(plain_password) == hashed_password


# ========== 设备管理 CRUD ==========
def get_equipment_list(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    keyword: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None
):
    """获取设备列表"""
    query = db.query(models.Equipment).filter(models.Equipment.is_deleted == 0)
    
    if keyword:
        query = query.filter(
            or_(
                models.Equipment.equipment_code.contains(keyword),
                models.Equipment.equipment_name.contains(keyword)
            )
        )
    if category:
        query = query.filter(models.Equipment.category == category)
    if status:
        query = query.filter(models.Equipment.status == status)
    
    total = query.count()
    items = query.order_by(models.Equipment.created_at.desc()).offset(skip).limit(limit).all()
    
    return {"total": total, "items": items}


def get_equipment_by_id(db: Session, equipment_id: int):
    """根据ID获取设备"""
    return db.query(models.Equipment).filter(
        models.Equipment.equipment_id == equipment_id,
        models.Equipment.is_deleted == 0
    ).first()


def create_equipment(db: Session, equipment: schemas.EquipmentCreate):
    """创建设备"""
    equipment_dict = equipment.dict()
    
    # 如果没有提供设备编码，自动生成
    if not equipment_dict.get('equipment_code'):
        # 获取当前最大设备ID，生成新的编码
        max_equipment = db.query(func.max(models.Equipment.equipment_id)).filter(
            models.Equipment.is_deleted == 0
        ).scalar()
        next_id = (max_equipment or 0) + 1
        
        # 生成设备编码，确保唯一性
        equipment_code = f"EQ{next_id:06d}"
        # 检查编码是否已存在（虽然理论上不应该，但为了安全）
        existing = db.query(models.Equipment).filter(
            models.Equipment.equipment_code == equipment_code,
            models.Equipment.is_deleted == 0
        ).first()
        
        # 如果编码已存在，使用时间戳生成唯一编码
        if existing:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            equipment_code = f"EQ{timestamp}{next_id:04d}"
        
        equipment_dict['equipment_code'] = equipment_code
    
    db_equipment = models.Equipment(**equipment_dict)
    db.add(db_equipment)
    db.commit()
    db.refresh(db_equipment)
    return db_equipment


def update_equipment(db: Session, equipment_id: int, equipment: schemas.EquipmentUpdate):
    """更新设备"""
    db_equipment = get_equipment_by_id(db, equipment_id)
    if not db_equipment:
        return None
    
    update_data = equipment.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_equipment, key, value)
    
    db.commit()
    db.refresh(db_equipment)
    return db_equipment


def delete_equipment(db: Session, equipment_id: int):
    """删除设备（软删除）"""
    db_equipment = get_equipment_by_id(db, equipment_id)
    if not db_equipment:
        return None
    
    db_equipment.is_deleted = 1
    db.commit()
    return db_equipment


# ========== 客户管理 CRUD ==========
def get_customer_list(db: Session, skip: int = 0, limit: int = 10, keyword: Optional[str] = None):
    """获取客户列表"""
    query = db.query(models.Customer).filter(models.Customer.is_deleted == 0)
    
    if keyword:
        query = query.filter(models.Customer.customer_name.contains(keyword))
    
    total = query.count()
    items = query.order_by(models.Customer.created_at.desc()).offset(skip).limit(limit).all()
    
    return {"total": total, "items": items}


def create_customer(db: Session, customer: schemas.CustomerCreate):
    """创建客户"""
    db_customer = models.Customer(**customer.dict())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


# ========== 租赁订单 CRUD ==========
def get_order_list(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    status: Optional[str] = None,
    keyword: Optional[str] = None
):
    """获取订单列表"""
    query = db.query(models.LeaseOrder).filter(models.LeaseOrder.is_deleted == 0)
    
    if status:
        query = query.filter(models.LeaseOrder.status == status)
    if keyword:
        query = query.filter(
            or_(
                models.LeaseOrder.order_code.contains(keyword),
                models.LeaseOrder.customer_name.contains(keyword),
                models.LeaseOrder.voyage_no.contains(keyword)
            )
        )
    
    total = query.count()
    items = query.order_by(models.LeaseOrder.created_at.desc()).offset(skip).limit(limit).all()
    
    return {"total": total, "items": items}


def get_order_by_id(db: Session, order_id: int):
    """根据ID获取订单"""
    return db.query(models.LeaseOrder).filter(
        models.LeaseOrder.order_id == order_id,
        models.LeaseOrder.is_deleted == 0
    ).first()


def create_order(db: Session, order: schemas.LeaseOrderCreate):
    """创建租赁订单"""
    # 生成订单编号
    order_code = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # 创建订单
    order_dict = order.dict(exclude={'order_items'})
    db_order = models.LeaseOrder(**order_dict, order_code=order_code)
    db.add(db_order)
    db.flush()  # 获取 order_id
    
    # 创建订单明细并计算总额
    total_amount = 0.0
    for item in order.order_items:
        item_dict = item.dict()
        subtotal = item_dict['daily_rate'] * item_dict['rental_days']
        item_dict['subtotal'] = subtotal
        item_dict['order_id'] = db_order.order_id
        
        db_item = models.OrderItem(**item_dict)
        db.add(db_item)
        
        total_amount += subtotal
        
        # 更新设备状态为已出库
        db.query(models.Equipment).filter(
            models.Equipment.equipment_id == item.equipment_id
        ).update({"status": models.EquipmentStatus.OUT})
    
    db_order.total_amount = total_amount
    db.commit()
    db.refresh(db_order)
    
    return db_order


def update_order(db: Session, order_id: int, order: schemas.LeaseOrderUpdate):
    """更新订单"""
    db_order = get_order_by_id(db, order_id)
    if not db_order:
        return None
    
    update_data = order.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_order, key, value)
    
    db.commit()
    db.refresh(db_order)
    return db_order


# ========== 账单管理 CRUD ==========
def get_billing_list(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    status: Optional[str] = None,
    keyword: Optional[str] = None
):
    """获取账单列表"""
    query = db.query(models.Billing).filter(models.Billing.is_deleted == 0)
    
    if status:
        query = query.filter(models.Billing.status == status)
    if keyword:
        query = query.filter(
            or_(
                models.Billing.bill_code.contains(keyword),
                models.Billing.customer_name.contains(keyword)
            )
        )
    
    total = query.count()
    items = query.order_by(models.Billing.created_at.desc()).offset(skip).limit(limit).all()
    
    return {"total": total, "items": items}


def create_billing(db: Session, billing: schemas.BillingCreate):
    """创建账单"""
    bill_code = f"BILL-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    billing_dict = billing.dict()
    total_amount = billing_dict['rental_fee'] + billing_dict['repair_fee'] + billing_dict['other_fee']
    billing_dict['total_amount'] = total_amount
    billing_dict['bill_code'] = bill_code
    
    db_billing = models.Billing(**billing_dict)
    db.add(db_billing)
    db.commit()
    db.refresh(db_billing)
    return db_billing


def update_billing(db: Session, bill_id: int, billing: schemas.BillingUpdate):
    """更新账单"""
    db_billing = db.query(models.Billing).filter(
        models.Billing.bill_id == bill_id,
        models.Billing.is_deleted == 0
    ).first()
    
    if not db_billing:
        return None
    
    update_data = billing.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_billing, key, value)
    
    # 重新计算总额
    db_billing.total_amount = db_billing.rental_fee + db_billing.repair_fee + db_billing.other_fee
    
    db.commit()
    db.refresh(db_billing)
    return db_billing


# ========== 归还与质检 CRUD ==========
def create_return_record(db: Session, return_record: schemas.ReturnRecordCreate):
    """创建归还记录"""
    return_code = f"RET-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    db_return = models.ReturnRecord(
        **return_record.dict(),
        return_code=return_code
    )
    db.add(db_return)
    db.commit()
    db.refresh(db_return)
    return db_return


def create_inspection_record(db: Session, inspection: schemas.InspectionRecordCreate):
    """创建质检记录"""
    # 判断质检结果
    result = models.InspectionResult.PASS
    if inspection.repair_needed == 1 or inspection.function_test == "故障":
        result = models.InspectionResult.REPAIR_NEEDED
    
    db_inspection = models.InspectionRecord(
        **inspection.dict(),
        result=result
    )
    db.add(db_inspection)
    
    # 更新设备状态
    new_status = models.EquipmentStatus.IN_STOCK
    if inspection.repair_needed == 1:
        new_status = models.EquipmentStatus.MAINTENANCE
    
    db.query(models.Equipment).filter(
        models.Equipment.equipment_id == inspection.equipment_id
    ).update({"status": new_status})
    
    db.commit()
    db.refresh(db_inspection)
    return db_inspection


# ========== 统计数据 CRUD ==========
def get_dashboard_stats(db: Session):
    """获取工作台统计数据"""
    # 设备统计
    total_equipment = db.query(func.count(models.Equipment.equipment_id)).filter(
        models.Equipment.is_deleted == 0
    ).scalar()
    
    in_stock = db.query(func.count(models.Equipment.equipment_id)).filter(
        models.Equipment.is_deleted == 0,
        models.Equipment.status == models.EquipmentStatus.IN_STOCK
    ).scalar()
    
    out_stock = db.query(func.count(models.Equipment.equipment_id)).filter(
        models.Equipment.is_deleted == 0,
        models.Equipment.status == models.EquipmentStatus.OUT
    ).scalar()
    
    maintenance = db.query(func.count(models.Equipment.equipment_id)).filter(
        models.Equipment.is_deleted == 0,
        models.Equipment.status == models.EquipmentStatus.MAINTENANCE
    ).scalar()
    
    # 订单统计
    pending_checkout = db.query(func.count(models.LeaseOrder.order_id)).filter(
        models.LeaseOrder.is_deleted == 0,
        models.LeaseOrder.status == models.OrderStatus.PENDING
    ).scalar()
    
    in_progress_orders = db.query(func.count(models.LeaseOrder.order_id)).filter(
        models.LeaseOrder.is_deleted == 0,
        models.LeaseOrder.status == models.OrderStatus.IN_PROGRESS
    ).scalar()
    
    # 财务统计
    total_revenue = db.query(func.sum(models.Billing.total_amount)).filter(
        models.Billing.is_deleted == 0,
        models.Billing.status == models.BillingStatus.PAID
    ).scalar() or 0.0
    
    pending_amount = db.query(func.sum(models.Billing.total_amount)).filter(
        models.Billing.is_deleted == 0,
        models.Billing.status.in_([models.BillingStatus.PENDING, models.BillingStatus.CONFIRMED])
    ).scalar() or 0.0
    
    overdue_bills = db.query(func.count(models.Billing.bill_id)).filter(
        models.Billing.is_deleted == 0,
        models.Billing.status == models.BillingStatus.OVERDUE
    ).scalar()
    
    # 质检统计
    pending_inspection = db.query(func.count(models.ReturnRecord.return_id)).filter(
        models.ReturnRecord.inspection_status == "待质检"
    ).scalar()
    
    return schemas.DashboardStats(
        total_equipment=total_equipment or 0,
        in_stock=in_stock or 0,
        out_stock=out_stock or 0,
        maintenance=maintenance or 0,
        pending_checkout=pending_checkout or 0,
        in_progress_orders=in_progress_orders or 0,
        pending_inspection=pending_inspection or 0,
        total_revenue=total_revenue,
        pending_amount=pending_amount,
        overdue_bills=overdue_bills or 0
    )


# ========== 用户管理 CRUD ==========
def get_user_by_username(db: Session, username: str):
    """根据用户名获取用户"""
    return db.query(models.User).filter(
        models.User.username == username,
        models.User.is_deleted == 0
    ).first()


def create_user(db: Session, user: schemas.UserCreate):
    """创建用户"""
    hashed_pwd = hash_password(user.password)
    db_user = models.User(
        **user.dict(exclude={'password'}),
        password_hash=hashed_pwd
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, username: str, password: str):
    """验证用户登录"""
    user = get_user_by_username(db, username)
    if not user:
        return None
    
    if not verify_password(password, user.password_hash):
        return None
    
    if user.status != "active":
        return None
    
    # 更新最后登录时间
    user.last_login = datetime.now()
    db.commit()
    db.refresh(user)
    
    return user


def get_user_by_id(db: Session, user_id: int):
    """根据ID获取用户"""
    return db.query(models.User).filter(
        models.User.user_id == user_id,
        models.User.is_deleted == 0
    ).first()


def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    """更新用户信息"""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(db_user, key, value)
    
    db_user.updated_at = datetime.now()
    db.commit()
    db.refresh(db_user)
    return db_user


# ========== 租赁分析统计 CRUD ==========
def get_rental_analysis_stats(db: Session):
    """获取租赁分析统计数据"""
    from datetime import timedelta
    
    # 获取今日和昨日日期
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    # 1. 租赁订单总数
    total_orders = db.query(func.count(models.LeaseOrder.order_id)).filter(
        models.LeaseOrder.is_deleted == 0
    ).scalar() or 0
    
    # 昨日订单数
    yesterday_orders = db.query(func.count(models.LeaseOrder.order_id)).filter(
        models.LeaseOrder.is_deleted == 0,
        func.date(models.LeaseOrder.created_at) == yesterday
    ).scalar() or 0
    
    # 计算增长
    orders_growth = ((total_orders - yesterday_orders) / yesterday_orders * 100) if yesterday_orders > 0 else 0.0
    
    # 2. 装备出库量（已出库的设备数量）
    total_outbound = db.query(func.count(models.Equipment.equipment_id)).filter(
        models.Equipment.is_deleted == 0,
        models.Equipment.status == models.EquipmentStatus.OUT
    ).scalar() or 0
    
    # 昨日出库量（通过订单创建时间判断）
    yesterday_outbound = db.query(func.count(models.Equipment.equipment_id)).join(
        models.OrderItem, models.OrderItem.equipment_id == models.Equipment.equipment_id
    ).join(
        models.LeaseOrder, models.LeaseOrder.order_id == models.OrderItem.order_id
    ).filter(
        models.Equipment.is_deleted == 0,
        func.date(models.LeaseOrder.created_at) == yesterday
    ).scalar() or 0
    
    outbound_growth = ((total_outbound - yesterday_outbound) / yesterday_outbound * 100) if yesterday_outbound > 0 else 0.0
    
    # 3. 在租装备数（状态为已出库的设备）
    total_renting = total_outbound
    
    # 昨日在租数（通过昨日订单中的设备数量估算）
    yesterday_renting = db.query(func.count(models.OrderItem.item_id)).join(
        models.LeaseOrder, models.LeaseOrder.order_id == models.OrderItem.order_id
    ).filter(
        models.LeaseOrder.is_deleted == 0,
        func.date(models.LeaseOrder.created_at) == yesterday
    ).scalar() or 0
    
    renting_growth = ((total_renting - yesterday_renting) / yesterday_renting * 100) if yesterday_renting > 0 else 0.0
    
    # 4. 归还装备数（通过归还记录统计）
    total_returned = db.query(func.count(models.ReturnRecord.return_id)).scalar() or 0
    
    # 昨日归还数
    yesterday_returned = db.query(func.count(models.ReturnRecord.return_id)).filter(
        func.date(models.ReturnRecord.return_date) == yesterday
    ).scalar() or 0
    
    returned_growth = ((total_returned - yesterday_returned) / yesterday_returned * 100) if yesterday_returned > 0 else 0.0
    
    # 5. 装备类型租赁比例（按设备类别统计订单数量）
    category_stats = db.query(
        models.Equipment.category,
        func.count(models.OrderItem.item_id).label('count')
    ).join(
        models.OrderItem, models.OrderItem.equipment_id == models.Equipment.equipment_id
    ).join(
        models.LeaseOrder, models.LeaseOrder.order_id == models.OrderItem.order_id
    ).filter(
        models.Equipment.is_deleted == 0,
        models.LeaseOrder.is_deleted == 0
    ).group_by(models.Equipment.category).all()
    
    category_ratio = [{"name": cat, "value": cnt} for cat, cnt in category_stats]
    
    # 6. 热门租赁装备榜单（按租赁次数和天数排序）
    popular_stats = db.query(
        models.Equipment.equipment_name,
        func.count(models.OrderItem.item_id).label('rental_count'),
        func.sum(models.OrderItem.rental_days).label('rental_days')
    ).join(
        models.OrderItem, models.OrderItem.equipment_id == models.Equipment.equipment_id
    ).join(
        models.LeaseOrder, models.LeaseOrder.order_id == models.OrderItem.order_id
    ).filter(
        models.Equipment.is_deleted == 0,
        models.LeaseOrder.is_deleted == 0
    ).group_by(
        models.Equipment.equipment_id, models.Equipment.equipment_name
    ).order_by(
        func.count(models.OrderItem.item_id).desc()
    ).limit(10).all()
    
    popular_equipment = [
        {
            "equipment_name": name,
            "rental_count": int(count),
            "rental_days": int(days or 0)
        }
        for name, count, days in popular_stats
    ]
    
    # 7. 租赁时段分析（按月份统计订单数量）
    # 生成最近12个月的月份列表
    months_list = []
    for i in range(11, -1, -1):
        month_date = today - timedelta(days=30 * i)
        months_list.append(month_date.strftime('%Y-%m'))
    
    # 查询每个月的订单数量
    period_stats = db.query(
        func.date_format(models.LeaseOrder.created_at, '%Y-%m').label('month'),
        func.count(models.LeaseOrder.order_id).label('count')
    ).filter(
        models.LeaseOrder.is_deleted == 0,
        models.LeaseOrder.created_at >= today - timedelta(days=365)  # 最近一年
    ).group_by(func.date_format(models.LeaseOrder.created_at, '%Y-%m')).order_by('month').all()
    
    # 创建月份到数量的映射
    stats_dict = {month: count for month, count in period_stats}
    
    # 为每个月份填充数据，如果没有数据则为0
    xAxis = months_list
    period_values = [stats_dict.get(month, 0) for month in months_list]
    period_data = [{"name": "租赁订单", "value": period_values}]
    
    return schemas.RentalAnalysisStats(
        total_orders=total_orders,
        total_outbound=total_outbound,
        total_renting=total_renting,
        total_returned=total_returned,
        orders_growth=round(orders_growth, 2),
        outbound_growth=round(outbound_growth, 2),
        renting_growth=round(renting_growth, 2),
        returned_growth=round(returned_growth, 2),
        category_ratio=category_ratio,
        popular_equipment=popular_equipment,
        period_analysis={"xAxis": xAxis, "data": period_data}
    )


# ========== 多维数据分析统计 CRUD ==========
def get_multi_dimension_analysis_stats(db: Session):
    """获取多维数据分析统计数据"""
    from datetime import timedelta
    
    today = date.today()
    
    # 1. 数据概览 - 装备入库量、装备租赁量、装备利用率、活跃租户数（最近8天）
    days_list = []
    for i in range(7, -1, -1):
        day_date = today - timedelta(days=i)
        days_list.append(day_date.strftime('%m.%d'))
    
    # 装备入库量（最近8天）
    inbound_data = []
    for i in range(7, -1, -1):
        day_date = today - timedelta(days=i)
        count = db.query(func.count(models.InboundRecord.inbound_id)).filter(
            models.InboundRecord.is_deleted == 0,
            func.date(models.InboundRecord.created_at) == day_date
        ).scalar() or 0
        inbound_data.append(count)
    
    # 装备租赁量（最近8天）
    rental_data = []
    for i in range(7, -1, -1):
        day_date = today - timedelta(days=i)
        count = db.query(func.count(models.LeaseOrder.order_id)).filter(
            models.LeaseOrder.is_deleted == 0,
            func.date(models.LeaseOrder.created_at) == day_date
        ).scalar() or 0
        rental_data.append(count)
    
    # 装备利用率（最近8天）- 计算为：在租装备数 / 总装备数 * 100
    utilization_data = []
    total_equipment = db.query(func.count(models.Equipment.equipment_id)).filter(
        models.Equipment.is_deleted == 0
    ).scalar() or 1  # 避免除零
    
    for i in range(7, -1, -1):
        day_date = today - timedelta(days=i)
        # 计算该日期的在租装备数（通过订单状态判断）
        renting_count = db.query(func.count(models.Equipment.equipment_id)).join(
            models.OrderItem, models.OrderItem.equipment_id == models.Equipment.equipment_id
        ).join(
            models.LeaseOrder, models.LeaseOrder.order_id == models.OrderItem.order_id
        ).filter(
            models.Equipment.is_deleted == 0,
            models.LeaseOrder.is_deleted == 0,
            models.LeaseOrder.start_date <= day_date,
            or_(
                models.LeaseOrder.actual_return_date.is_(None),
                models.LeaseOrder.actual_return_date > day_date
            )
        ).scalar() or 0
        
        utilization = int((renting_count / total_equipment) * 100) if total_equipment > 0 else 0
        utilization_data.append(utilization)
    
    # 活跃租户数（最近8天）- 有订单的客户数
    active_customers_data = []
    for i in range(7, -1, -1):
        day_date = today - timedelta(days=i)
        count = db.query(func.count(func.distinct(models.LeaseOrder.customer_id))).filter(
            models.LeaseOrder.is_deleted == 0,
            func.date(models.LeaseOrder.created_at) == day_date
        ).scalar() or 0
        active_customers_data.append(count)
    
    # 计算总数
    total_inbound = sum(inbound_data)
    total_rental = sum(rental_data)
    avg_utilization = int(sum(utilization_data) / len(utilization_data)) if utilization_data else 0
    total_active_customers = db.query(func.count(func.distinct(models.LeaseOrder.customer_id))).filter(
        models.LeaseOrder.is_deleted == 0
    ).scalar() or 0
    
    data_overview = {
        "xAxis": days_list,
        "data": [
            {"name": "装备入库量", "value": inbound_data, "count": total_inbound},
            {"name": "装备租赁量", "value": rental_data, "count": total_rental},
            {"name": "装备利用率", "value": utilization_data, "count": avg_utilization},
            {"name": "活跃租户数", "value": active_customers_data, "count": total_active_customers},
        ]
    }
    
    # 2. 数据链增长 - 保留趋势、用户留存、内容消费趋势、内容消费
    # 保留趋势（订单保留率）
    retention_trends_count = db.query(func.count(models.LeaseOrder.order_id)).filter(
        models.LeaseOrder.is_deleted == 0,
        models.LeaseOrder.status == models.OrderStatus.IN_PROGRESS
    ).scalar() or 0
    
    # 用户留存（活跃客户数）
    user_retention_count = db.query(func.count(func.distinct(models.LeaseOrder.customer_id))).filter(
        models.LeaseOrder.is_deleted == 0,
        models.LeaseOrder.created_at >= today - timedelta(days=30)
    ).scalar() or 0
    
    # 内容消费趋势（装备使用天数）
    content_consumption_trends_count = db.query(func.sum(models.OrderItem.rental_days)).filter(
        models.OrderItem.order_id.in_(
            db.query(models.LeaseOrder.order_id).filter(
                models.LeaseOrder.is_deleted == 0
            )
        )
    ).scalar() or 0
    
    # 内容消费（总订单金额）
    content_consumption_count = db.query(func.sum(models.LeaseOrder.total_amount)).filter(
        models.LeaseOrder.is_deleted == 0
    ).scalar() or 0
    
    # 生成图表数据（最近12天）- 使用真实数据
    chart_days = []
    chart_values_retention = []
    chart_values_user = []
    chart_values_consumption_trends = []
    chart_values_consumption = []
    
    for i in range(11, -1, -1):
        day_date = today - timedelta(days=i)
        chart_days.append(f"{day_date.day}日")
        
        # 保留趋势：每日在租订单数
        daily_retention = db.query(func.count(models.LeaseOrder.order_id)).filter(
            models.LeaseOrder.is_deleted == 0,
            models.LeaseOrder.status == models.OrderStatus.IN_PROGRESS,
            func.date(models.LeaseOrder.created_at) <= day_date,
            or_(
                models.LeaseOrder.actual_return_date.is_(None),
                func.date(models.LeaseOrder.actual_return_date) > day_date
            )
        ).scalar() or 0
        chart_values_retention.append(daily_retention)
        
        # 用户留存：每日活跃客户数
        daily_users = db.query(func.count(func.distinct(models.LeaseOrder.customer_id))).filter(
            models.LeaseOrder.is_deleted == 0,
            func.date(models.LeaseOrder.created_at) == day_date
        ).scalar() or 0
        chart_values_user.append(daily_users)
        
        # 内容消费趋势：每日租赁天数总和
        daily_rental_days = db.query(func.sum(models.OrderItem.rental_days)).join(
            models.LeaseOrder, models.LeaseOrder.order_id == models.OrderItem.order_id
        ).filter(
            models.LeaseOrder.is_deleted == 0,
            func.date(models.LeaseOrder.created_at) == day_date
        ).scalar() or 0
        chart_values_consumption_trends.append(int(daily_rental_days or 0))
        
        # 内容消费：每日订单金额总和
        daily_amount = db.query(func.sum(models.LeaseOrder.total_amount)).filter(
            models.LeaseOrder.is_deleted == 0,
            func.date(models.LeaseOrder.created_at) == day_date
        ).scalar() or 0
        chart_values_consumption.append(int(daily_amount or 0))
    
    data_chain_growth = {
        "retentionTrends": {
            "count": retention_trends_count,
            "growth": 0.0,
            "chartData": {
                "xAxis": chart_days,
                "data": {
                    "name": "retentionTrends",
                    "value": chart_values_retention
                }
            }
        },
        "userRetention": {
            "count": user_retention_count,
            "growth": 0.0,
            "chartData": {
                "xAxis": chart_days,
                "data": {
                    "name": "userRetention",
                    "value": chart_values_user
                }
            }
        },
        "contentConsumptionTrends": {
            "count": content_consumption_trends_count or 0,
            "growth": 0.0,
            "chartData": {
                "xAxis": chart_days,
                "data": {
                    "name": "contentConsumptionTrends",
                    "value": chart_values_consumption_trends
                }
            }
        },
        "contentConsumption": {
            "count": int(content_consumption_count or 0),
            "growth": 0.0,
            "chartData": {
                "xAxis": chart_days,
                "data": {
                    "name": "contentConsumption",
                    "value": chart_values_consumption
                }
            }
        }
    }
    
    # 3. 用户行为 - 点赞量、评论量、分享量（映射到：订单数、归还数、质检数）
    user_actions = {
        "data": [
            db.query(func.count(models.LeaseOrder.order_id)).filter(
                models.LeaseOrder.is_deleted == 0
            ).scalar() or 0,  # 订单数
            db.query(func.count(models.ReturnRecord.return_id)).scalar() or 0,  # 归还数
            db.query(func.count(models.InspectionRecord.inspection_id)).scalar() or 0,  # 质检数
        ]
    }
    
    # 4. 内容类型分布（雷达图）- 装备类型分布
    equipment_categories = db.query(
        models.Equipment.category,
        func.count(models.Equipment.equipment_id).label('count')
    ).filter(
        models.Equipment.is_deleted == 0
    ).group_by(models.Equipment.category).all()
    
    # 按装备类型统计租赁次数
    category_rental_data = {}
    for cat, _ in equipment_categories:
        rental_count = db.query(func.count(models.OrderItem.item_id)).join(
            models.Equipment, models.Equipment.equipment_id == models.OrderItem.equipment_id
        ).filter(
            models.Equipment.category == cat,
            models.Equipment.is_deleted == 0
        ).scalar() or 0
        category_rental_data[cat] = rental_count
    
    # 获取所有装备类型的最大租赁次数
    max_rental = max([rental_count for rental_count in category_rental_data.values()], default=1)
    
    # 计算合理的max值（向上取整到最近的100或1000）
    if max_rental == 0:
        max_value = 100
    elif max_rental < 100:
        max_value = ((max_rental // 10) + 1) * 10  # 向上取整到最近的10
    elif max_rental < 1000:
        max_value = ((max_rental // 100) + 1) * 100  # 向上取整到最近的100
    else:
        max_value = ((max_rental // 1000) + 1) * 1000  # 向上取整到最近的1000
    
    # 最多6个装备类型
    categories_list = list(category_rental_data.keys())[:6]
    indicator = [{"name": cat, "max": max_value} for cat in categories_list]
    
    content_type_distribution = {
        "indicator": indicator,
        "data": [{
            "name": "装备租赁",
            "value": [category_rental_data.get(cat, 0) for cat in categories_list]
        }]
    }
    
    # 5. 内容发布来源 - 3个饼图（映射到：装备来源、租赁状态、归还状态）
    # 第一个饼图：装备来源（供应商）
    supplier_stats = db.query(
        models.InboundRecord.supplier,
        func.count(models.InboundRecord.inbound_id).label('count')
    ).filter(
        models.InboundRecord.is_deleted == 0,
        models.InboundRecord.supplier.isnot(None)
    ).group_by(models.InboundRecord.supplier).limit(5).all()
    
    # 确保value是数字而不是数组
    supplier_data = [{"name": name or "未知", "value": cnt} for name, cnt in supplier_stats]
    
    # 第二个饼图：租赁状态分布
    order_status_stats = db.query(
        models.LeaseOrder.status,
        func.count(models.LeaseOrder.order_id).label('count')
    ).filter(
        models.LeaseOrder.is_deleted == 0
    ).group_by(models.LeaseOrder.status).all()
    
    status_data = [{"name": str(status.value), "value": cnt} for status, cnt in order_status_stats]
    
    # 第三个饼图：归还状态分布
    return_status_stats = db.query(
        models.ReturnRecord.inspection_status,
        func.count(models.ReturnRecord.return_id).label('count')
    ).group_by(models.ReturnRecord.inspection_status).all()
    
    return_status_data = [{"name": status or "未知", "value": cnt} for status, cnt in return_status_stats]
    
    content_publishing_source = {
        "data": [supplier_data, status_data, return_status_data]
    }
    
    return schemas.MultiDimensionAnalysisStats(
        data_overview=data_overview,
        data_chain_growth=data_chain_growth,
        user_actions=user_actions,
        content_type_distribution=content_type_distribution,
        content_publishing_source=content_publishing_source
    )


# ========== 触发器日志管理 ==========
def get_trigger_logs(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    log_type: Optional[str] = None,
    trigger_name: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """获取触发器日志列表"""
    query = db.query(models.TriggerLog).filter(models.TriggerLog.id > 0)
    
    # 筛选条件
    if log_type and log_type != 'all':
        query = query.filter(models.TriggerLog.log_type == log_type)
    
    if trigger_name and trigger_name != 'all':
        query = query.filter(models.TriggerLog.trigger_name == trigger_name)
    
    if start_date:
        query = query.filter(models.TriggerLog.created_at >= start_date)
    
    if end_date:
        query = query.filter(models.TriggerLog.created_at <= end_date)
    
    # 总数
    total = query.count()
    
    # 分页查询
    logs = query.order_by(models.TriggerLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "items": logs,
        "total": total,
        "page": page,
        "page_size": page_size
    }


def create_trigger_log(db: Session, log_data: schemas.TriggerLogCreate):
    """创建触发器日志"""
    db_log = models.TriggerLog(**log_data.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def get_trigger_log_by_id(db: Session, log_id: int):
    """根据ID获取触发器日志"""
    return db.query(models.TriggerLog).filter(models.TriggerLog.id == log_id).first()

