from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, text
from typing import List, Optional, Dict, Any
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
    status: Optional[str] = None,
    use_view: bool = False
):
    """
    获取设备列表
    如果 use_view=True，使用视图优化查询（包含租赁统计信息）
    """
    if use_view:
        return get_equipment_list_from_view(db, skip, limit, keyword, category, status)
    
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


def get_equipment_list_from_view(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    keyword: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None
) -> Dict[str, Any]:
    """
    从视图获取设备库存列表（优化版本）
    使用视图: v_equipment_inventory
    如果视图不存在，自动回退到原查询方式
    """
    try:
        query = "SELECT * FROM v_equipment_inventory WHERE 1=1"
        params = {}
        
        if keyword:
            query += " AND (equipment_code LIKE :keyword OR equipment_name LIKE :keyword)"
            params['keyword'] = f'%{keyword}%'
        
        if category:
            query += " AND category = :category"
            params['category'] = category
        
        if status:
            # 转换状态值
            status_map = {
                "在库": "在库",
                "已出库": "已出库",
                "维修中": "维修中",
                "available": "在库",
                "rented": "已出库",
                "maintenance": "维修中"
            }
            status_value = status_map.get(status, status)
            query += " AND status = :status"
            params['status'] = status_value
        
        # 获取总数
        count_query = query.replace("SELECT *", "SELECT COUNT(*)")
        total = db.execute(text(count_query), params).scalar()
        
        # 获取分页数据
        query += " ORDER BY created_at DESC LIMIT :limit OFFSET :skip"
        params['limit'] = limit
        params['skip'] = skip
        
        result = db.execute(text(query), params)
        items = []
        for row in result:
            # 转换状态显示值 - 同时支持枚举名称和枚举值
            status_display_map = {
                # 枚举值映射
                "在库": "available",
                "已出库": "rented",
                "维修中": "maintenance",
                "已报废": "maintenance",
                # 枚举名称映射（SQLAlchemy 可能返回枚举名称）
                "IN_STOCK": "available",
                "OUT": "rented",
                "MAINTENANCE": "maintenance",
                "SCRAPPED": "maintenance",
            }
            # 清理状态值（去除首尾空格）
            raw_status = str(row.status).strip() if row.status else ""
            display_status = status_display_map.get(raw_status, "maintenance")
            
            # 调试日志：如果状态不在映射中，记录警告
            if raw_status not in status_display_map and raw_status:
                print(f"警告: 设备 {row.equipment_code} 的状态值 '{raw_status}' 不在映射中，使用默认值 'maintenance'")
            
            items.append({
                'equipment_id': row.equipment_id,
                'equipment_code': row.equipment_code,
                'equipment_name': row.equipment_name,
                'category': row.category,
                'status': row.status,
                'storage_location': row.storage_location,
                'purchase_price': float(row.purchase_price) if row.purchase_price else 0.0,
                'daily_rental_rate': float(row.daily_rental_rate) if row.daily_rental_rate else 0.0,
                'supplier': row.supplier or "",
                'manufacturer': row.manufacturer or "",
                'purchase_date': row.purchase_date,
                'warranty_date': row.warranty_date,
                'last_maintenance_date': row.last_maintenance_date,
                'serial_number': row.serial_number or "",
                'specifications': row.specifications or "",
                'created_at': row.created_at,
                'updated_at': row.updated_at,
                # 视图提供的统计信息
                'available_quantity': int(row.available_quantity),
                'rented_quantity': int(row.rented_quantity),
                'maintenance_quantity': int(row.maintenance_quantity),
                'rental_count': int(row.rental_count),
                'total_rental_days': int(row.total_rental_days),
                'total_revenue': float(row.total_revenue) if row.total_revenue else 0.0,
                # 前端需要的字段
                'display_status': display_status,
            })
        
        return {"total": total, "items": items}
    except Exception as e:
        # 视图不存在或其他错误，回退到原查询方式
        import traceback
        print(f"视图查询失败，回退到原查询方式: {e}")
        traceback.print_exc()
        # 调用原查询方法（禁用视图）
        return get_equipment_list(
            db, skip=skip, limit=limit,
            keyword=keyword, category=category, status=status,
            use_view=False  # 禁用视图，使用原查询
        )


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
    
    # 使用 model_dump 替代 dict（Pydantic v2）或保持 dict（Pydantic v1）
    try:
        update_data = equipment.model_dump(exclude_unset=True)
    except AttributeError:
        # 兼容 Pydantic v1
        update_data = equipment.dict(exclude_unset=True)
    
    # 移除系统字段，防止意外修改
    system_fields = ['created_at', 'updated_at', 'equipment_id', 'equipment_code', 'is_deleted']
    for field in system_fields:
        update_data.pop(field, None)
    
    # 特殊处理状态字段，确保正确转换为枚举值
    if 'status' in update_data and update_data['status'] is not None:
        status_value = update_data['status']
        # 如果传入的是字符串，尝试转换为枚举值
        if isinstance(status_value, str):
            status_map = {
                "在库": models.EquipmentStatus.IN_STOCK,
                "已出库": models.EquipmentStatus.OUT,
                "维修中": models.EquipmentStatus.MAINTENANCE,
                "已报废": models.EquipmentStatus.SCRAPPED,
                "IN_STOCK": models.EquipmentStatus.IN_STOCK,
                "OUT": models.EquipmentStatus.OUT,
                "MAINTENANCE": models.EquipmentStatus.MAINTENANCE,
                "SCRAPPED": models.EquipmentStatus.SCRAPPED,
            }
            cleaned_status = status_value.strip()
            if cleaned_status in status_map:
                update_data['status'] = status_map[cleaned_status]
            else:
                # 如果状态值不在映射中，尝试直接使用（可能是枚举值的字符串表示）
                try:
                    update_data['status'] = models.EquipmentStatus(cleaned_status)
                except ValueError:
                    raise ValueError(f"无效的设备状态值: '{status_value}'。有效值: {list(status_map.keys())}")
        # 如果已经是枚举值，直接使用
        elif isinstance(status_value, models.EquipmentStatus):
            update_data['status'] = status_value
        # 如果是枚举值的值（字符串），尝试转换
        elif status_value in [e.value for e in models.EquipmentStatus]:
            update_data['status'] = models.EquipmentStatus(status_value)
    
    # 更新字段
    for key, value in update_data.items():
        setattr(db_equipment, key, value)
    
    # 提交更改并刷新对象
    try:
        db.commit()
        db.refresh(db_equipment)
        
        # 调试日志：记录更新后的状态值
        print(f"设备 {db_equipment.equipment_code} 更新成功，状态: {db_equipment.status} (类型: {type(db_equipment.status)}, 值: {db_equipment.status.value if hasattr(db_equipment.status, 'value') else db_equipment.status})")
        
        return db_equipment
    except Exception as e:
        db.rollback()
        print(f"更新设备失败: {e}")
        # 如果是 created_at 错误，尝试手动修复
        if "created_at" in str(e):
            print("尝试使用原始 SQL 更新...")
            try:
                # 使用原始 SQL 更新，避免触发 created_at 约束
                update_stmt = text("""
                    UPDATE equipment
                    SET status = :status, updated_at = NOW()
                    WHERE equipment_id = :equipment_id
                """)
                status_value = update_data.get('status')
                if isinstance(status_value, models.EquipmentStatus):
                    status_to_use = status_value.value
                else:
                    status_to_use = status_value
                db.execute(update_stmt, {
                    "status": status_to_use,
                    "equipment_id": equipment_id
                })
                db.commit()
                
                # 重新查询设备
                db_equipment = get_equipment_by_id(db, equipment_id)
                print(f"使用原始 SQL 更新成功")
                return db_equipment
            except Exception as e2:
                db.rollback()
                print(f"原始 SQL 更新也失败: {e2}")
                raise e
        raise e


def delete_equipment(db: Session, equipment_id: int):
    """删除设备（软删除）"""
    db_equipment = get_equipment_by_id(db, equipment_id)
    if not db_equipment:
        return None
    
    db_equipment.is_deleted = 1
    db.commit()
    return db_equipment


# ========== 客户管理 CRUD ==========
def get_customer_list(
    db: Session, 
    skip: int = 0, 
    limit: int = 10, 
    keyword: Optional[str] = None,
    use_view: bool = False
):
    """
    获取客户列表
    如果 use_view=True，使用视图优化查询（包含租赁统计信息）
    """
    if use_view:
        return get_customer_list_from_view(db, skip, limit, keyword)
    
    query = db.query(models.Customer).filter(models.Customer.is_deleted == 0)
    
    if keyword:
        query = query.filter(models.Customer.customer_name.contains(keyword))
    
    total = query.count()
    items = query.order_by(models.Customer.created_at.desc()).offset(skip).limit(limit).all()
    
    return {"total": total, "items": items}


def get_customer_list_from_view(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    keyword: Optional[str] = None,
    credit_rating: Optional[str] = None
) -> Dict[str, Any]:
    """
    从视图获取客户租赁统计列表（优化版本）
    使用视图: v_customer_rental_stats
    """
    query = "SELECT * FROM v_customer_rental_stats WHERE 1=1"
    params = {}
    
    if keyword:
        query += " AND (customer_name LIKE :keyword OR contact_person LIKE :keyword)"
        params['keyword'] = f'%{keyword}%'
    
    if credit_rating:
        query += " AND credit_rating = :credit_rating"
        params['credit_rating'] = credit_rating
    
    # 获取总数
    count_query = query.replace("SELECT *", "SELECT COUNT(*)")
    total = db.execute(text(count_query), params).scalar()
    
    # 获取分页数据
    query += " ORDER BY total_rental_amount DESC LIMIT :limit OFFSET :skip"
    params['limit'] = limit
    params['skip'] = skip
    
    result = db.execute(text(query), params)
    items = []
    for row in result:
        items.append({
            'customer_id': row.customer_id,
            'customer_name': row.customer_name,
            'contact_person': row.contact_person,
            'phone': row.phone,
            'email': row.email,
            'address': row.address,
            'credit_rating': row.credit_rating,
            'created_at': row.created_at,
            # 视图提供的统计信息
            'total_orders': int(row.total_orders),
            'completed_orders': int(row.completed_orders),
            'in_progress_orders': int(row.in_progress_orders),
            'pending_orders': int(row.pending_orders),
            'total_rental_amount': float(row.total_rental_amount),
            'paid_amount': float(row.paid_amount),
            'pending_amount': float(row.pending_amount),
            'total_equipment_count': int(row.total_equipment_count),
            'last_order_date': row.last_order_date,
            'last_order_code': row.last_order_code,
        })
    
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
    keyword: Optional[str] = None,
    use_view: bool = False
):
    """
    获取订单列表
    如果 use_view=True，使用视图优化查询（包含客户、账单、归还等关联信息）
    """
    if use_view:
        return get_order_list_from_view(db, skip, limit, status, keyword)
    
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


def get_order_list_from_view(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    status: Optional[str] = None,
    keyword: Optional[str] = None
) -> Dict[str, Any]:
    """
    从视图获取订单汇总列表（优化版本）
    使用视图: v_order_summary
    """
    query = "SELECT * FROM v_order_summary WHERE 1=1"
    params = {}
    
    if status:
        query += " AND order_status = :status"
        params['status'] = status
    
    if keyword:
        query += " AND (order_code LIKE :keyword OR customer_name LIKE :keyword OR voyage_no LIKE :keyword)"
        params['keyword'] = f'%{keyword}%'
    
    # 获取总数
    count_query = query.replace("SELECT *", "SELECT COUNT(*)")
    total = db.execute(text(count_query), params).scalar()
    
    # 获取分页数据
    query += " ORDER BY created_at DESC LIMIT :limit OFFSET :skip"
    params['limit'] = limit
    params['skip'] = skip
    
    result = db.execute(text(query), params)
    items = []
    for row in result:
        items.append({
            'order_id': row.order_id,
            'order_code': row.order_code,
            'customer_id': row.customer_id,
            'customer_name': row.customer_name,
            'contact_person': row.contact_person,
            'customer_phone': row.customer_phone,
            'customer_email': row.customer_email,
            'credit_rating': row.credit_rating,
            'voyage_no': row.voyage_no,
            'start_date': row.start_date,
            'expected_return_date': row.expected_return_date,
            'actual_return_date': row.actual_return_date,
            'order_status': row.order_status,
            'total_amount': float(row.total_amount) if row.total_amount else 0.0,
            'created_by': row.created_by,
            'created_at': row.created_at,
            'updated_at': row.updated_at,
            # 视图提供的统计信息
            'equipment_count': int(row.equipment_count),
            'total_rental_days': int(row.total_rental_days),
            'avg_daily_rate': float(row.avg_daily_rate) if row.avg_daily_rate else 0.0,
            # 账单信息
            'bill_id': row.bill_id,
            'bill_code': row.bill_code,
            'billing_status': row.billing_status,
            'billing_amount': float(row.billing_amount) if row.billing_amount else 0.0,
            'payment_method': row.payment_method,
            'paid_amount': float(row.paid_amount) if row.paid_amount else 0.0,
            # 归还信息
            'return_id': row.return_id,
            'return_code': row.return_code,
            'return_date': row.return_date,
            'inspection_status': row.inspection_status,
            'total_damage_fee': float(row.total_damage_fee) if row.total_damage_fee else 0.0,
        })
    
    return {"total": total, "items": items}


def get_order_by_id(db: Session, order_id: int):
    """根据ID获取订单"""
    return db.query(models.LeaseOrder).filter(
        models.LeaseOrder.order_id == order_id,
        models.LeaseOrder.is_deleted == 0
    ).first()


def create_order(db: Session, order: schemas.LeaseOrderCreate):
    """
    创建租赁订单
    注意：订单总金额和设备状态更新由触发器自动处理
    - trg_order_item_insert: 自动计算订单总金额
    - trg_order_created: 自动更新设备状态为"已出库"
    """
    # 生成订单编号
    order_code = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # 创建订单（初始总金额设为0，触发器会自动计算）
    order_dict = order.dict(exclude={'order_items'})
    db_order = models.LeaseOrder(**order_dict, order_code=order_code, total_amount=0.0)
    db.add(db_order)
    db.flush()  # 获取 order_id
    
    # 创建订单明细（触发器会自动计算订单总金额）
    for item in order.order_items:
        item_dict = item.dict()
        # 计算小计
        subtotal = item_dict['daily_rate'] * item_dict['rental_days']
        item_dict['subtotal'] = subtotal
        item_dict['order_id'] = db_order.order_id
        
        db_item = models.OrderItem(**item_dict)
        db.add(db_item)
    
    # 提交事务（触发器会在此时自动执行）
    db.commit()
    db.refresh(db_order)
    
    # 重新查询以获取触发器计算后的总金额
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
    keyword: Optional[str] = None,
    use_view: bool = False
):
    """
    获取账单列表
    如果 use_view=True，使用视图优化查询（包含订单、客户等关联信息）
    """
    if use_view:
        return get_billing_list_from_view(db, skip, limit, status, keyword)
    
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


def get_billing_list_from_view(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    payment_method: Optional[str] = None
) -> Dict[str, Any]:
    """
    从视图获取财务汇总列表（优化版本）
    使用视图: v_billing_summary
    """
    query = "SELECT * FROM v_billing_summary WHERE 1=1"
    params = {}
    
    if status:
        query += " AND billing_status = :status"
        params['status'] = status
    
    if keyword:
        query += " AND (bill_code LIKE :keyword OR customer_name LIKE :keyword OR order_code LIKE :keyword)"
        params['keyword'] = f'%{keyword}%'
    
    if payment_method:
        query += " AND payment_method = :payment_method"
        params['payment_method'] = payment_method
    
    # 获取总数
    count_query = query.replace("SELECT *", "SELECT COUNT(*)")
    total = db.execute(text(count_query), params).scalar()
    
    # 获取分页数据
    query += " ORDER BY created_at DESC LIMIT :limit OFFSET :skip"
    params['limit'] = limit
    params['skip'] = skip
    
    result = db.execute(text(query), params)
    items = []
    for row in result:
        items.append({
            'bill_id': row.bill_id,
            'bill_code': row.bill_code,
            'order_id': row.order_id,
            'order_code': row.order_code,
            'customer_name': row.customer_name,
            'customer_id': row.customer_id,
            'contact_person': row.contact_person,
            'customer_phone': row.customer_phone,
            'customer_email': row.customer_email,
            'rental_fee': float(row.rental_fee) if row.rental_fee else 0.0,
            'repair_fee': float(row.repair_fee) if row.repair_fee else 0.0,
            'other_fee': float(row.other_fee) if row.other_fee else 0.0,
            'discount': float(row.discount) if row.discount else 0.0,
            'total_amount': float(row.total_amount) if row.total_amount else 0.0,
            'paid_amount': float(row.paid_amount) if row.paid_amount else 0.0,
            'unpaid_amount': float(row.unpaid_amount) if row.unpaid_amount else 0.0,
            'status': row.billing_status,
            'payment_method': row.payment_method,
            'invoice_no': row.invoice_no,
            'billing_date': row.billing_date,
            'payment_date': row.payment_date,
            'remarks': row.remarks,
            'created_at': row.created_at,
            'updated_at': row.updated_at,
            # 订单信息
            'voyage_no': row.voyage_no,
            'start_date': row.start_date,
            'expected_return_date': row.expected_return_date,
            'actual_return_date': row.actual_return_date,
            'order_status': row.order_status,
            # 订单明细统计
            'equipment_count': int(row.equipment_count),
            'total_rental_days': int(row.total_rental_days),
        })
    
    return {"total": total, "items": items}


def create_billing(db: Session, billing: schemas.BillingCreate):
    """
    创建账单
    注意：总金额计算由触发器 trg_billing_before_insert 自动处理
    如果total_amount未提供或为0，触发器会自动计算：rental_fee + repair_fee + other_fee - discount
    """
    bill_code = f"BILL-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    billing_dict = billing.dict()
    billing_dict['bill_code'] = bill_code
    # 如果未提供total_amount，设为0，让触发器自动计算
    if 'total_amount' not in billing_dict or billing_dict.get('total_amount') is None:
        billing_dict['total_amount'] = 0.0
    
    db_billing = models.Billing(**billing_dict)
    db.add(db_billing)
    db.commit()
    db.refresh(db_billing)
    return db_billing


def update_billing(db: Session, bill_id: int, billing: schemas.BillingUpdate):
    """
    更新账单
    注意：总金额重新计算由触发器 trg_billing_before_update 自动处理
    当费用字段变更时，触发器会自动重新计算总金额
    """
    db_billing = db.query(models.Billing).filter(
        models.Billing.bill_id == bill_id,
        models.Billing.is_deleted == 0
    ).first()
    
    if not db_billing:
        return None
    
    update_data = billing.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_billing, key, value)
    
    # 触发器会自动重新计算total_amount，无需手动计算
    db.commit()
    db.refresh(db_billing)
    return db_billing


# ========== 归还与质检 CRUD ==========
def create_return_record(db: Session, return_record: schemas.ReturnRecordCreate):
    """
    创建归还记录
    注意：操作日志由触发器 trg_return_record_created 自动记录
    """
    return_code = f"RET-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    db_return = models.ReturnRecord(
        **return_record.dict(),
        return_code=return_code
    )
    db.add(db_return)
    db.commit()
    db.refresh(db_return)
    return db_return


# ========== 触发器日志 CRUD ==========
def get_trigger_logs(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    log_type: Optional[str] = None,
    trigger_name: Optional[str] = None,
    table_name: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Dict[str, Any]:
    """获取触发器日志列表"""
    query = db.query(models.TriggerLog)
    
    if log_type:
        query = query.filter(models.TriggerLog.log_type == log_type)
    if trigger_name:
        query = query.filter(models.TriggerLog.trigger_name.like(f'%{trigger_name}%'))
    if table_name:
        query = query.filter(models.TriggerLog.table_name == table_name)
    if start_date:
        query = query.filter(models.TriggerLog.created_at >= start_date)
    if end_date:
        query = query.filter(models.TriggerLog.created_at <= end_date)
    
    total = query.count()
    items = query.order_by(models.TriggerLog.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "items": items
    }


def get_trigger_log_by_id(db: Session, log_id: int):
    """根据ID获取触发器日志"""
    return db.query(models.TriggerLog).filter(models.TriggerLog.id == log_id).first()


def create_trigger_log(db: Session, log_data: schemas.TriggerLogCreate):
    """创建触发器日志（通常由触发器自动调用）"""
    db_log = models.TriggerLog(**log_data.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def create_inspection_record(db: Session, inspection: schemas.InspectionRecordCreate):
    """
    创建质检记录
    注意：设备状态更新由触发器 trg_inspection_record_created 自动处理
    触发器会根据repair_needed和function_test自动更新设备状态：
    - repair_needed=1 或 function_test='故障' → 设备状态='维修中'
    - 否则 → 设备状态='在库'
    """
    # 判断质检结果
    result = models.InspectionResult.PASS
    if inspection.repair_needed == 1 or inspection.function_test == "故障":
        result = models.InspectionResult.REPAIR_NEEDED
    
    db_inspection = models.InspectionRecord(
        **inspection.dict(),
        result=result
    )
    db.add(db_inspection)
    
    # 触发器会自动更新设备状态，无需手动更新
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
    
    # 5. 装备类型租赁比例（使用视图优化）
    try:
        # 尝试使用视图优化查询
        category_stats = db.execute(text("""
            SELECT category, total_rental_count as count
            FROM v_equipment_category_stats
            WHERE total_rental_count > 0
            ORDER BY total_rental_count DESC
        """)).fetchall()
        category_ratio = [{"name": row.category, "value": int(row.count)} for row in category_stats]
    except Exception:
        # 如果视图不存在，使用原查询方式
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
    
    # 6. 热门租赁装备榜单（使用视图优化）
    try:
        # 尝试使用视图优化查询
        popular_stats = db.execute(text("""
            SELECT 
                equipment_name,
                rental_count,
                total_rental_days as rental_days
            FROM v_equipment_usage
            WHERE rental_count > 0
            ORDER BY rental_count DESC, total_rental_days DESC
            LIMIT 10
        """)).fetchall()
        popular_equipment = [
            {
                "equipment_name": row.equipment_name,
                "rental_count": int(row.rental_count),
                "rental_days": int(row.rental_days or 0)
            }
            for row in popular_stats
        ]
    except Exception:
        # 如果视图不存在，使用原查询方式
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

