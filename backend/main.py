from fastapi import FastAPI, Depends, HTTPException, Query, Body, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from datetime import date
import crud
import models
import schemas
from database import engine, get_db

# 创建数据库表
models.Base.metadata.create_all(bind=engine)

# 创建 FastAPI 应用
app = FastAPI(
    title="船舶作业装备租赁与港口仓储管理系统 API",
    description="Port Equipment Management System API",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 确保 uploads 目录存在
from pathlib import Path
upload_dir = Path("uploads")
upload_dir.mkdir(exist_ok=True)
(upload_dir / "avatars").mkdir(exist_ok=True)

# 挂载静态文件目录
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# ========== 根路由 ==========
@app.get("/")
def read_root():
    return {
        "message": "欢迎使用船舶作业装备租赁与港口仓储管理系统 API",
        "version": "1.0.0",
        "docs": "/docs"
    }


# ========== 工作台统计 ==========
@app.get("/api/dashboard/stats", response_model=schemas.DashboardStats, tags=["Dashboard"])
def get_dashboard_stats(db: Session = Depends(get_db)):
    """获取工作台统计数据"""
    return crud.get_dashboard_stats(db)


@app.get("/api/content-data", tags=["Dashboard"])
def get_content_data(db: Session = Depends(get_db)):
    """获取租赁数据趋势图表数据（最近7天）"""
    from datetime import timedelta
    
    today = date.today()
    chart_data = []
    
    # 统计最近7天的租赁订单数量
    for i in range(6, -1, -1):
        day_date = today - timedelta(days=i)
        
        # 统计当天创建的租赁订单数量
        count = db.query(func.count(models.LeaseOrder.order_id)).filter(
            models.LeaseOrder.is_deleted == 0,
            func.date(models.LeaseOrder.created_at) == day_date
        ).scalar() or 0
        
        # 格式化日期为 MM-DD
        date_str = day_date.strftime('%m-%d')
        
        chart_data.append({
            "x": date_str,
            "y": count
        })
    
    return {
        "code": 200,
        "message": "success",
        "data": chart_data
    }


@app.get("/api/popular/list", tags=["Dashboard"])
def get_popular_list(
    type: Optional[str] = Query(None, description="装备类型过滤"),
    db: Session = Depends(get_db)
):
    """获取热门装备列表（按租赁次数统计）"""
    from datetime import timedelta
    
    # 获取最近30天的日期范围
    today = date.today()
    thirty_days_ago = today - timedelta(days=30)
    
    # 统计每个装备的租赁次数（基于订单明细）
    query = db.query(
        models.Equipment.equipment_name,
        models.Equipment.equipment_code,
        models.Equipment.category,
        func.count(models.OrderItem.item_id).label('rental_count')
    ).join(
        models.OrderItem,
        models.Equipment.equipment_id == models.OrderItem.equipment_id
    ).join(
        models.LeaseOrder,
        models.OrderItem.order_id == models.LeaseOrder.order_id
    ).filter(
        models.Equipment.is_deleted == 0,
        models.LeaseOrder.is_deleted == 0,
        models.LeaseOrder.created_at >= thirty_days_ago
    ).group_by(
        models.Equipment.equipment_id,
        models.Equipment.equipment_name,
        models.Equipment.equipment_code,
        models.Equipment.category
    )
    
    # 如果有类型过滤（匹配类型关键词）
    if type:
        # 支持多种关键词匹配
        type_keywords = {
            'crane': ['起重机', '吊机', 'crane'],
            'forklift': ['叉车', 'forklift'],
            'container': ['集装箱', 'container', '箱'],
            'pallet': ['托盘', 'pallet'],
            'truck': ['货车', '卡车', 'truck'],
        }
        
        keywords = type_keywords.get(type.lower(), [type])
        or_conditions = [models.Equipment.category.contains(kw) for kw in keywords]
        from sqlalchemy import or_
        query = query.filter(or_(*or_conditions))
    
    # 按租赁次数降序排列，获取前10名
    results = query.order_by(func.count(models.OrderItem.item_id).desc()).limit(10).all()
    
    # 格式化结果
    data = []
    for idx, (equipment_name, equipment_code, category, rental_count) in enumerate(results, start=1):
        # 计算增长率（与前一天对比）
        yesterday = today - timedelta(days=1)
        yesterday_count = db.query(func.count(models.OrderItem.item_id)).join(
            models.Equipment,
            models.OrderItem.equipment_id == models.Equipment.equipment_id
        ).join(
            models.LeaseOrder,
            models.OrderItem.order_id == models.LeaseOrder.order_id
        ).filter(
            models.Equipment.equipment_name == equipment_name,
            models.LeaseOrder.is_deleted == 0,
            func.date(models.LeaseOrder.created_at) == yesterday
        ).scalar() or 0
        
        # 计算增长率
        if yesterday_count > 0:
            increases = round(((rental_count - yesterday_count) / yesterday_count) * 100, 1)
        else:
            increases = 100.0 if rental_count > 0 else 0.0
        
        data.append({
            "key": idx,
            "title": f"{equipment_name} ({equipment_code})",
            "clickNumber": str(rental_count),
            "increases": increases,
        })
    
    # 如果没有租赁数据，显示所有装备
    if not data:
        all_equipment = db.query(
            models.Equipment.equipment_name,
            models.Equipment.equipment_code
        ).filter(
            models.Equipment.is_deleted == 0
        ).limit(10).all()
        
        for idx, (equipment_name, equipment_code) in enumerate(all_equipment, start=1):
            data.append({
                "key": idx,
                "title": f"{equipment_name} ({equipment_code})",
                "clickNumber": "0",
                "increases": 0.0,
            })
    
    return {
        "code": 200,
        "message": "success",
        "data": data
    }


# ========== 租赁分析统计 ==========
@app.get("/api/rental/analysis", response_model=schemas.RentalAnalysisStats, tags=["Rental"])
def get_rental_analysis(db: Session = Depends(get_db)):
    """获取租赁分析统计数据"""
    return crud.get_rental_analysis_stats(db)


# ========== 多维数据分析统计 ==========
@app.get("/api/multi-dimension/analysis", response_model=schemas.MultiDimensionAnalysisStats, tags=["Analysis"])
def get_multi_dimension_analysis(db: Session = Depends(get_db)):
    """获取多维数据分析统计数据"""
    return crud.get_multi_dimension_analysis_stats(db)


@app.post("/api/data-overview", response_model=schemas.DataOverviewResponse, tags=["Analysis"])
def get_data_overview(db: Session = Depends(get_db)):
    """获取数据概览（兼容旧接口）"""
    stats = crud.get_multi_dimension_analysis_stats(db)
    return schemas.DataOverviewResponse(
        xAxis=stats.data_overview.get("xAxis", []),
        data=stats.data_overview.get("data", [])
    )


@app.post("/api/data-chain-growth", response_model=schemas.DataChainGrowthResponse, tags=["Analysis"])
def get_data_chain_growth(quota: dict, db: Session = Depends(get_db)):
    """获取数据链增长（兼容旧接口）"""
    stats = crud.get_multi_dimension_analysis_stats(db)
    quota_name = quota.get("quota", "") if isinstance(quota, dict) else ""
    growth_data = stats.data_chain_growth.get(quota_name, {})
    
    if not growth_data:
        # 返回默认数据
        return schemas.DataChainGrowthResponse(
            count=0,
            growth=0.0,
            chartData={
                "xAxis": [],
                "data": {"name": quota_name, "value": []}
            }
        )
    
    chart_data = growth_data.get("chartData", {})
    return schemas.DataChainGrowthResponse(
        count=growth_data.get("count", 0),
        growth=growth_data.get("growth", 0.0),
        chartData=chart_data
    )


# ========== 设备管理 API ==========
@app.get("/api/equipment", response_model=schemas.PageResponse, tags=["Equipment"])
def list_equipment(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    keyword: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取设备列表"""
    skip = (page - 1) * page_size
    result = crud.get_equipment_list(
        db, skip=skip, limit=page_size,
        keyword=keyword, category=category, status=status
    )
    
    return schemas.PageResponse(
        data=[schemas.Equipment.from_orm(item) for item in result["items"]],
        total=result["total"],
        page=page,
        page_size=page_size
    )


@app.get("/api/equipment/inventory", tags=["Equipment"])
def list_equipment_inventory(
    current: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
    keyword: Optional[str] = None,
    equipmentType: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取设备库存列表（使用视图优化）"""
    skip = (current - 1) * pageSize
    # 使用视图优化查询，包含租赁统计信息
    result = crud.get_equipment_list(
        db, skip=skip, limit=pageSize,
        keyword=keyword, category=equipmentType, status=status,
        use_view=True  # 启用视图优化
    )
    
    # 转换为前端期望的格式
    items = []
    for item in result["items"]:
        items.append({
            "id": str(item['equipment_id']),
            "equipmentCode": item['equipment_code'],
            "equipmentName": item['equipment_name'],
            "equipmentType": item['category'],
            "totalQuantity": 1,
            "availableQuantity": item['available_quantity'],
            "rentedQuantity": item['rented_quantity'],
            "warehouse": item['storage_location'] or "",
            "location": item['storage_location'] or "",
            "status": item['display_status'],
            "dailyRate": item['daily_rental_rate'],
            "purchaseDate": item['purchase_date'].strftime("%Y-%m-%d") if item['purchase_date'] else None,
            "inboundDate": item['created_at'].strftime("%Y-%m-%d") if item['created_at'] else None,
            "supplier": item['supplier'],
            "specifications": item['specifications'],
            # 新增：租赁统计信息
            "rentalCount": item['rental_count'],
            "totalRentalDays": item['total_rental_days'],
            "totalRevenue": item['total_revenue']
        })
    
    return {
        "code": 200,
        "message": "success",
        "list": items,
        "total": result["total"]
    }


@app.get("/api/equipment/inbound", response_model=dict, tags=["Equipment"])
def list_equipment_inbound(
    current: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
    equipmentCode: Optional[str] = None,
    equipmentName: Optional[str] = None,
    equipmentType: Optional[str] = None,
    supplier: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取设备入库记录列表"""
    skip = (current - 1) * pageSize
    result = crud.get_equipment_list(
        db, skip=skip, limit=pageSize,
        keyword=equipmentCode or equipmentName, 
        category=equipmentType,
        status=status
    )
    
    # 转换为前端期望的格式
    items = []
    for item in result["items"]:
        # 从remarks中提取supplier信息（如果存在）
        supplier_info = "默认供应商"
        if item.remarks and "供应商:" in item.remarks:
            supplier_info = item.remarks.split("供应商:")[1].split("\n")[0].strip()
        
        items.append({
            "id": str(item.equipment_id),
            "equipmentCode": item.equipment_code,
            "equipmentName": item.equipment_name,
            "equipmentType": item.category,
            "specification": item.specifications,
            "quantity": 1,
            "supplier": supplier_info,
            "warehouse": item.storage_location or "",
            "location": item.storage_location or "",
            "inboundTime": item.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "completed",
            "remark": item.remarks
        })
    
    return {
        "code": 200,
        "message": "success",
        "list": items,
        "total": result["total"]
    }


@app.post("/api/equipment/inbound", tags=["Equipment"])
def create_equipment_inbound(data: dict, db: Session = Depends(get_db)):
    """创建设备入库记录"""
    # 从前端camelCase格式转换为后端snake_case格式
    # equipment_code 不是必填项，如果未提供或为空，则设为None，由系统自动生成
    equipment_code_raw = data.get("equipmentCode")
    equipment_code = equipment_code_raw.strip() if equipment_code_raw and equipment_code_raw.strip() else None
    equipment_name = data.get("equipmentName", "").strip()
    category = data.get("equipmentType", "").strip()
    specifications = data.get("specification", "").strip() if data.get("specification") else None
    try:
        quantity = int(data.get("quantity", 1))
    except (ValueError, TypeError):
        quantity = 1
    supplier = data.get("supplier", "").strip() if data.get("supplier") else ""
    warehouse = data.get("warehouse", "").strip() if data.get("warehouse") else ""
    location = data.get("location", "").strip() if data.get("location") else ""
    remark = data.get("remark", "").strip() if data.get("remark") else ""
    
    # 验证必填字段（equipment_code不是必填项，由系统自动生成）
    if not equipment_name:
        raise HTTPException(status_code=400, detail="装备名称为必填项")
    if not category:
        raise HTTPException(status_code=400, detail="装备类型为必填项")
    if quantity < 1:
        raise HTTPException(status_code=400, detail="数量必须大于0")
    
    # 构建remarks，包含supplier信息
    remarks_parts = []
    if supplier:
        remarks_parts.append(f"供应商: {supplier}")
    if remark:
        remarks_parts.append(f"备注: {remark}")
    final_remarks = "\n".join(remarks_parts) if remarks_parts else None
    
    # 使用warehouse或location作为storage_location
    storage_location = warehouse or location
    
    # 根据quantity创建多个设备记录
    created_equipment = []
    for i in range(quantity):
        # 如果没有提供equipment_code，使用None让crud.create_equipment自动生成
        # 如果提供了equipment_code且数量大于1，为每个设备生成唯一的编号
        if equipment_code:
            if quantity > 1:
                unique_code = f"{equipment_code}-{i+1:03d}"
            else:
                unique_code = equipment_code
            
            # 检查设备编号是否已存在
            existing = db.query(models.Equipment).filter(
                models.Equipment.equipment_code == unique_code,
                models.Equipment.is_deleted == 0
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=400, 
                    detail=f"装备编号 {unique_code} 已存在"
                )
        else:
            # 不提供equipment_code，让系统自动生成
            unique_code = None
        
        # 创建EquipmentCreate对象
        equipment_data = schemas.EquipmentCreate(
            equipment_code=unique_code,
            equipment_name=equipment_name,
            category=category,
            specifications=specifications,
            storage_location=storage_location,
            remarks=final_remarks
        )
        
        result = crud.create_equipment(db, equipment_data)
        created_equipment.append({
            "id": result.equipment_id,
            "equipmentCode": result.equipment_code
        })
    
    return {
        "code": 200,
        "message": f"设备入库成功，共创建 {quantity} 条记录",
        "data": created_equipment[0] if len(created_equipment) == 1 else created_equipment
    }


def _convert_outbound_status_to_frontend(status):
    """将后端枚举状态转换为前端需要的字符串值"""
    # 处理枚举对象或字符串值
    status_value = status.value if hasattr(status, 'value') else str(status)
    
    # 根据中文值映射到英文值
    status_mapping = {
        "待出库": "pending",
        "已完成": "completed",
        "已取消": "cancelled"
    }
    
    return status_mapping.get(status_value, "completed")


@app.get("/api/equipment/outbound", response_model=dict, tags=["Equipment"])
def list_equipment_outbound(
    current: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    outboundCode: Optional[str] = None,
    equipmentCode: Optional[str] = None,
    rentalOrder: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取设备出库记录列表"""
    skip = (current - 1) * pageSize
    
    # 查询出库记录表
    query = db.query(models.OutboundRecord).filter(
        models.OutboundRecord.is_deleted == 0
    )
    
    # 搜索条件
    if outboundCode:
        query = query.filter(models.OutboundRecord.outbound_code.contains(outboundCode))
    if status:
        # 将前端的状态值转换为枚举值
        status_map = {
            "pending": models.OutboundStatus.PENDING,
            "completed": models.OutboundStatus.COMPLETED,
            "cancelled": models.OutboundStatus.CANCELLED
        }
        if status in status_map:
            query = query.filter(models.OutboundRecord.status == status_map[status])
    
    # 如果提供了订单号，需要关联查询
    if rentalOrder:
        # 使用 outerjoin 以包含所有出库记录，然后过滤匹配订单号的
        query = query.outerjoin(models.LeaseOrder).filter(
            models.LeaseOrder.order_code.contains(rentalOrder)
        )
    
    # 如果提供了装备编号过滤，需要在查询时就过滤
    if equipmentCode:
        # 先找到匹配装备编号的出库明细，获取对应的出库记录ID
        matching_item_ids = db.query(models.OutboundItem.outbound_id).filter(
            models.OutboundItem.equipment_code.contains(equipmentCode)
        ).distinct().all()
        matching_outbound_ids = [item[0] for item in matching_item_ids]
        if matching_outbound_ids:
            query = query.filter(models.OutboundRecord.outbound_id.in_(matching_outbound_ids))
        else:
            # 如果没有匹配的记录，返回空列表
            return {
                "code": 200,
                "message": "success",
                "list": [],
                "total": 0
            }
    
    total = query.count()
    # 按创建时间倒序排列，确保最新的记录在最前面
    outbound_records = query.order_by(models.OutboundRecord.created_at.desc()).offset(skip).limit(pageSize).all()
    
    items = []
    for record in outbound_records:
        # 获取关联的订单
        order = None
        if record.order_id:
            order = db.query(models.LeaseOrder).filter(
                    models.LeaseOrder.order_id == record.order_id,
                    models.LeaseOrder.is_deleted == 0
            ).first()
        
        # 获取出库明细
        outbound_items = db.query(models.OutboundItem).filter(
            models.OutboundItem.outbound_id == record.outbound_id
        ).all()
        
        # 如果提供了装备编号过滤，只返回匹配的明细
        if equipmentCode:
            outbound_items = [item for item in outbound_items if equipmentCode in item.equipment_code]
        
        # 为每个明细创建一条记录（如果有多条明细）
        if outbound_items:
            for item in outbound_items:
                items.append({
                    "id": str(record.outbound_id),
                    "outboundCode": record.outbound_code,
                    "rentalOrder": order.order_code if order else "",
                    "equipmentCode": item.equipment_code,
                    "equipmentName": item.equipment_name,
                    "quantity": item.quantity,
                    "outboundTime": record.outbound_date.strftime("%Y-%m-%d %H:%M:%S") if record.outbound_date else "",
                    "operator": record.operator or (order.created_by if order else "系统"),
                    "status": _convert_outbound_status_to_frontend(record.status),
                    "remark": record.remarks or ""
                })
        else:
            # 如果没有明细（理论上不应该发生，但为了安全起见保留）
            items.append({
                "id": str(record.outbound_id),
                "outboundCode": record.outbound_code,
                "rentalOrder": order.order_code if order else "",
                "equipmentCode": "",
                "equipmentName": "",
                "quantity": record.total_quantity,
                "outboundTime": record.outbound_date.strftime("%Y-%m-%d %H:%M:%S") if record.outbound_date else "",
                "operator": record.operator or (order.created_by if order else "系统"),
                "status": _convert_outbound_status_to_frontend(record.status),
                "remark": record.remarks or ""
            })
    
    return {
        "code": 200,
        "message": "success",
        "list": items,
        "total": total
    }


@app.post("/api/equipment/outbound", tags=["Equipment"])
def create_equipment_outbound(data: dict, db: Session = Depends(get_db)):
    """创建设备出库记录"""
    from datetime import datetime
    
    # 从前端camelCase格式转换为后端snake_case格式
    rental_order_code = data.get("rentalOrder", "").strip()
    equipment_code = data.get("equipmentCode", "").strip()
    quantity = int(data.get("quantity", 1))
    operator = data.get("operator", "").strip() or "系统"
    outbound_time = data.get("outboundTime")
    status_str = data.get("status", "completed").strip()
    remark = data.get("remark", "").strip()
    
    # 将前端状态值转换为枚举
    status_map = {
        "pending": models.OutboundStatus.PENDING,
        "completed": models.OutboundStatus.COMPLETED,
        "cancelled": models.OutboundStatus.CANCELLED
    }
    status = status_map.get(status_str, models.OutboundStatus.COMPLETED)
    
    # 验证必填字段
    if not equipment_code:
        raise HTTPException(status_code=400, detail="装备编号为必填项")
    if quantity < 1:
        raise HTTPException(status_code=400, detail="数量必须大于0")
    
    # 查找设备
    equipment = db.query(models.Equipment).filter(
        models.Equipment.equipment_code == equipment_code,
        models.Equipment.is_deleted == 0
    ).first()
    
    if not equipment:
        raise HTTPException(status_code=404, detail=f"装备编号 {equipment_code} 不存在")
    
    # 检查设备是否已在库
    if equipment.status != models.EquipmentStatus.IN_STOCK:
        raise HTTPException(status_code=400, detail=f"装备 {equipment_code} 当前状态为 {equipment.status.value}，无法出库")
    
    # 查找关联的订单（如果提供了订单号）
    order_id = None
    if rental_order_code:
        order = db.query(models.LeaseOrder).filter(
            models.LeaseOrder.order_code == rental_order_code,
            models.LeaseOrder.is_deleted == 0
        ).first()
        if order:
            order_id = order.order_id
    
    # 生成出库单号
    max_outbound = db.query(func.max(models.OutboundRecord.outbound_id)).filter(
        models.OutboundRecord.is_deleted == 0
    ).scalar()
    next_id = (max_outbound or 0) + 1
    outbound_code = f"OUT{datetime.now().strftime('%Y%m%d')}{next_id:06d}"
    
    # 检查出库单号是否已存在
    existing = db.query(models.OutboundRecord).filter(
        models.OutboundRecord.outbound_code == outbound_code,
        models.OutboundRecord.is_deleted == 0
    ).first()
    if existing:
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        outbound_code = f"OUT{timestamp}{next_id:04d}"
    
    # 解析出库时间
    outbound_date = datetime.now()
    if outbound_time:
        try:
            if isinstance(outbound_time, str):
                outbound_date = datetime.strptime(outbound_time, "%Y-%m-%d")
            elif hasattr(outbound_time, 'toISOString'):
                # 处理前端日期对象
                outbound_date = datetime.fromisoformat(outbound_time.replace('Z', '+00:00'))
        except Exception:
            pass
    
    # 创建出库记录
    outbound_record = models.OutboundRecord(
        outbound_code=outbound_code,
        order_id=order_id,
        outbound_date=outbound_date,
        operator=operator,
        total_quantity=quantity,
        status=status,
        remarks=remark
    )
    db.add(outbound_record)
    db.flush()  # 获取 outbound_id
    
    # 创建出库明细
    outbound_item = models.OutboundItem(
        outbound_id=outbound_record.outbound_id,
        equipment_id=equipment.equipment_id,
        equipment_code=equipment.equipment_code,
        equipment_name=equipment.equipment_name,
        quantity=quantity,
        daily_rate=equipment.daily_rental_rate or 0.0
    )
    db.add(outbound_item)
    
    # 触发器 trg_outbound_record_created 会自动更新设备状态为"已出库"
    db.commit()
    db.refresh(outbound_record)
    
    return {
        "code": 200,
        "message": "设备出库成功",
        "data": {
            "id": str(outbound_record.outbound_id),
            "outboundCode": outbound_record.outbound_code,
            "equipmentCode": equipment_code,
            "quantity": quantity
        }
    }


@app.delete("/api/equipment/outbound/{outbound_id}", tags=["Equipment"])
def delete_equipment_outbound(outbound_id: int, db: Session = Depends(get_db)):
    """删除出库记录（软删除）"""
    # 查找出库记录
    outbound_record = db.query(models.OutboundRecord).filter(
        models.OutboundRecord.outbound_id == outbound_id,
        models.OutboundRecord.is_deleted == 0
    ).first()
    
    if not outbound_record:
        raise HTTPException(status_code=404, detail="出库记录不存在")
    
    # 获取出库明细
    outbound_items = db.query(models.OutboundItem).filter(
        models.OutboundItem.outbound_id == outbound_id
    ).all()
    
    # 收集需要检查的设备ID
    equipment_ids = [item.equipment_id for item in outbound_items]
    
    # 软删除出库记录
    outbound_record.is_deleted = 1
    
    # 对于每个设备，检查是否还有其他未删除的出库记录
    for equipment_id in equipment_ids:
        # 查找该设备是否还有其他未删除的出库记录
        other_outbound_items = db.query(models.OutboundItem).join(
            models.OutboundRecord
        ).filter(
            models.OutboundItem.equipment_id == equipment_id,
            models.OutboundRecord.is_deleted == 0,
            models.OutboundRecord.outbound_id != outbound_id
        ).first()
        
        # 如果没有其他未删除的出库记录，恢复设备状态为在库
        if not other_outbound_items:
            equipment = db.query(models.Equipment).filter(
                models.Equipment.equipment_id == equipment_id
            ).first()
            if equipment and equipment.status == models.EquipmentStatus.OUT:
                equipment.status = models.EquipmentStatus.IN_STOCK
    
    db.commit()
    
    return {
        "code": 200,
        "message": "出库记录删除成功"
    }


@app.get("/api/equipment/{equipment_id}", response_model=schemas.Equipment, tags=["Equipment"])
def get_equipment(equipment_id: int, db: Session = Depends(get_db)):
    """获取设备详情"""
    equipment = crud.get_equipment_by_id(db, equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="设备不存在")
    return equipment


@app.post("/api/equipment", response_model=schemas.Equipment, tags=["Equipment"])
def create_equipment(equipment: schemas.EquipmentCreate, db: Session = Depends(get_db)):
    """创建设备"""
    return crud.create_equipment(db, equipment)


@app.put("/api/equipment/{equipment_id}", response_model=schemas.Equipment, tags=["Equipment"])
def update_equipment(
    equipment_id: int,
    equipment: schemas.EquipmentUpdate,
    db: Session = Depends(get_db)
):
    """更新设备"""
    updated = crud.update_equipment(db, equipment_id, equipment)
    if not updated:
        raise HTTPException(status_code=404, detail="设备不存在")
    return updated


@app.delete("/api/equipment/{equipment_id}", tags=["Equipment"])
def delete_equipment(equipment_id: int, db: Session = Depends(get_db)):
    """删除设备"""
    deleted = crud.delete_equipment(db, equipment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="设备不存在")
    return schemas.Response(message="删除成功")


# ========== 客户管理 API ==========
@app.get("/api/customers", response_model=schemas.PageResponse, tags=["Customer"])
def list_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    keyword: Optional[str] = None,
    credit_rating: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取客户列表（使用视图优化，包含租赁统计信息）"""
    skip = (page - 1) * page_size
    # 使用视图优化查询
    result = crud.get_customer_list(
        db, skip=skip, limit=page_size, 
        keyword=keyword, use_view=True
    )
    
    # 如果使用视图，返回包含统计信息的字典格式
    if result.get("items") and isinstance(result["items"][0], dict):
        return {
            "data": result["items"],
            "total": result["total"],
            "page": page,
            "page_size": page_size
        }
    else:
        # 兼容原有格式
        return schemas.PageResponse(
            data=[schemas.Customer.from_orm(item) for item in result["items"]],
            total=result["total"],
            page=page,
            page_size=page_size
        )


@app.post("/api/customers", response_model=schemas.Customer, tags=["Customer"])
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    """创建客户"""
    return crud.create_customer(db, customer)


# ========== 租赁订单 API ==========
@app.get("/api/orders", response_model=schemas.PageResponse, tags=["Order"])
def list_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取订单列表（使用视图优化，包含客户、账单、归还等关联信息）"""
    skip = (page - 1) * page_size
    # 使用视图优化查询
    result = crud.get_order_list(
        db, skip=skip, limit=page_size,
        status=status, keyword=keyword,
        use_view=True  # 启用视图优化
    )
    
    # 如果使用视图，需要转换为ORM对象格式
    if result.get("items") and isinstance(result["items"][0], dict):
        # 视图返回的是字典格式，需要转换为ORM对象或直接返回字典
        # 为了兼容现有schema，我们返回字典格式，让前端直接使用
        items = []
        for item in result["items"]:
            # 创建类似ORM对象的字典结构
            order_dict = {
                'order_id': item['order_id'],
                'order_code': item['order_code'],
                'customer_id': item['customer_id'],
                'customer_name': item['customer_name'],
                'voyage_no': item['voyage_no'],
                'start_date': item['start_date'],
                'expected_return_date': item['expected_return_date'],
                'actual_return_date': item['actual_return_date'],
                'status': item['order_status'],
                'total_amount': item['total_amount'],
                'created_by': item['created_by'],
                'created_at': item['created_at'],
                'updated_at': item['updated_at'],
                'is_deleted': 0,
                # 扩展信息（视图提供）
                'equipment_count': item['equipment_count'],
                'total_rental_days': item['total_rental_days'],
                'contact_person': item['contact_person'],
                'customer_phone': item['customer_phone'],
                'billing_status': item['billing_status'],
                'return_code': item['return_code'],
            }
            items.append(order_dict)
        
        # 使用字典创建PageResponse，需要调整schema或直接返回字典
        return {
            "data": items,
            "total": result["total"],
            "page": page,
            "page_size": page_size
        }
    else:
        # 兼容原有格式
        return schemas.PageResponse(
            data=[schemas.LeaseOrder.from_orm(item) for item in result["items"]],
            total=result["total"],
            page=page,
            page_size=page_size
        )


@app.get("/api/orders/{order_id}", response_model=schemas.LeaseOrder, tags=["Order"])
def get_order(order_id: int, db: Session = Depends(get_db)):
    """获取订单详情"""
    order = crud.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order


@app.post("/api/orders", response_model=schemas.LeaseOrder, tags=["Order"])
def create_order(order: schemas.LeaseOrderCreate, db: Session = Depends(get_db)):
    """创建租赁订单"""
    return crud.create_order(db, order)


@app.put("/api/orders/{order_id}", response_model=schemas.LeaseOrder, tags=["Order"])
def update_order(
    order_id: int,
    order: schemas.LeaseOrderUpdate,
    db: Session = Depends(get_db)
):
    """更新订单"""
    updated = crud.update_order(db, order_id, order)
    if not updated:
        raise HTTPException(status_code=404, detail="订单不存在")
    return updated


# ========== 账单管理 API ==========
@app.get("/api/billing", response_model=schemas.PageResponse, tags=["Billing"])
def list_billing(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取账单列表"""
    skip = (page - 1) * page_size
    result = crud.get_billing_list(
        db, skip=skip, limit=page_size,
        status=status, keyword=keyword
    )
    
    return schemas.PageResponse(
        data=[schemas.Billing.from_orm(item) for item in result["items"]],
        total=result["total"],
        page=page,
        page_size=page_size
    )


@app.post("/api/billing", response_model=schemas.Billing, tags=["Billing"])
def create_billing(billing: schemas.BillingCreate, db: Session = Depends(get_db)):
    """创建账单"""
    return crud.create_billing(db, billing)


@app.put("/api/billing/{bill_id}", response_model=schemas.Billing, tags=["Billing"])
def update_billing(
    bill_id: int,
    billing: schemas.BillingUpdate,
    db: Session = Depends(get_db)
):
    """更新账单"""
    updated = crud.update_billing(db, bill_id, billing)
    if not updated:
        raise HTTPException(status_code=404, detail="账单不存在")
    return updated


# ========== 租赁申请 API ==========
@app.get("/api/rental/application", response_model=dict, tags=["Rental"])
def list_rental_applications(
    current: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
    applicationCode: Optional[str] = None,
    applicant: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取租赁申请列表（实际映射到订单）"""
    skip = (current - 1) * pageSize
    
    query = db.query(models.LeaseOrder).filter(models.LeaseOrder.is_deleted == 0)
    
    if applicationCode:
        query = query.filter(models.LeaseOrder.order_code.contains(applicationCode))
    if applicant:
        query = query.filter(models.LeaseOrder.customer_name.contains(applicant))
    if status:
        status_map = {
            "pending": "待提货",
            "approved": "航次执行中",
            "completed": "已完结"
        }
        query = query.filter(models.LeaseOrder.status == status_map.get(status, status))
    
    total = query.count()
    items_db = query.order_by(models.LeaseOrder.created_at.desc()).offset(skip).limit(pageSize).all()
    
    items = []
    for order in items_db:
        # 获取订单中的设备信息
        equipment_codes = [item.equipment_code for item in order.order_items]
        equipment_type = order.order_items[0].equipment_name if order.order_items else ""
        
        status_map_reverse = {
            "待提货": "pending",
            "航次执行中": "approved",
            "已完结": "completed",
            "已取消": "rejected"
        }
        
        items.append({
            "id": str(order.order_id),
            "applicationCode": order.order_code,
            "applicant": order.customer_name,
            "equipmentType": equipment_type,
            "equipmentCode": ", ".join(equipment_codes[:3]),
            "quantity": len(order.order_items),
            "startDate": order.start_date.strftime("%Y-%m-%d"),
            "endDate": order.expected_return_date.strftime("%Y-%m-%d") if order.expected_return_date else "",
            "purpose": order.remarks or "",
            "applicationTime": order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "status": status_map_reverse.get(order.status, "pending"),
            "remark": order.remarks
        })
    
    return {
        "code": 200,
        "message": "success",
        "list": items,
        "total": total
    }


@app.post("/api/rental/application", tags=["Rental"])
def create_rental_application(data: dict, db: Session = Depends(get_db)):
    """创建租赁申请（实际创建订单）"""
    from datetime import datetime, date
    
    # 从前端获取数据
    applicant_name = data.get("applicant", "").strip()
    equipment_code = data.get("equipmentCode", "").strip()
    quantity = int(data.get("quantity", 1))
    start_date_str = data.get("startDate")
    end_date_str = data.get("endDate")
    purpose = data.get("purpose", "").strip()
    remark = data.get("remark", "").strip()
    equipment_type = data.get("equipmentType", "").strip()
    
    # 验证必填字段
    if not applicant_name:
        raise HTTPException(status_code=400, detail="申请人为必填项")
    if not equipment_code:
        raise HTTPException(status_code=400, detail="装备编号为必填项")
    if quantity < 1:
        raise HTTPException(status_code=400, detail="数量必须大于0")
    if not start_date_str:
        raise HTTPException(status_code=400, detail="开始日期为必填项")
    if not end_date_str:
        raise HTTPException(status_code=400, detail="结束日期为必填项")
    
    # 解析日期
    try:
        if isinstance(start_date_str, str):
            start_date = datetime.strptime(start_date_str.split('T')[0], "%Y-%m-%d").date()
        else:
            start_date = start_date_str
        if isinstance(end_date_str, str):
            end_date = datetime.strptime(end_date_str.split('T')[0], "%Y-%m-%d").date()
        else:
            end_date = end_date_str
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"日期格式错误: {str(e)}")
    
    if start_date >= end_date:
        raise HTTPException(status_code=400, detail="结束日期必须晚于开始日期")
    
    # 计算租赁天数
    rental_days = (end_date - start_date).days + 1
    
    # 查找或创建客户
    customer = db.query(models.Customer).filter(
        models.Customer.customer_name == applicant_name,
        models.Customer.is_deleted == 0
    ).first()
    
    if not customer:
        # 创建新客户
        customer = models.Customer(
            customer_name=applicant_name,
            contact_person=applicant_name
        )
        db.add(customer)
        db.flush()
    
    # 查找设备（根据装备编号）
    equipment = db.query(models.Equipment).filter(
        models.Equipment.equipment_code == equipment_code,
        models.Equipment.is_deleted == 0
    ).first()
    
    if not equipment:
        raise HTTPException(status_code=404, detail=f"装备编号 {equipment_code} 不存在")
    
    # 检查设备是否可用
    if equipment.status != models.EquipmentStatus.IN_STOCK:
        raise HTTPException(status_code=400, detail=f"装备 {equipment_code} 当前状态为 {equipment.status.value}，无法租赁")
    
    # 检查库存数量
    if quantity > 1:
        # 如果数量大于1，需要检查是否有足够的设备
        available_count = db.query(models.Equipment).filter(
            models.Equipment.equipment_code == equipment_code,
            models.Equipment.status == models.EquipmentStatus.IN_STOCK,
            models.Equipment.is_deleted == 0
        ).count()
        if available_count < quantity:
            raise HTTPException(status_code=400, detail=f"装备 {equipment_code} 可用数量不足，当前可用: {available_count}")
    
    # 构建订单明细
    order_items = []
    daily_rate = equipment.daily_rental_rate or 0.0
    
    # 如果数量大于1，需要查找多个相同类型的设备
    if quantity > 1:
        # 根据装备类型查找多个可用设备
        equipment_type = equipment.category
        available_equipments = db.query(models.Equipment).filter(
            models.Equipment.category == equipment_type,
            models.Equipment.status == models.EquipmentStatus.IN_STOCK,
            models.Equipment.is_deleted == 0
        ).limit(quantity).all()
        
        if len(available_equipments) < quantity:
            raise HTTPException(status_code=400, detail=f"可用设备数量不足，需要 {quantity} 个，但只有 {len(available_equipments)} 个")
        
        for eq in available_equipments:
            order_items.append(schemas.OrderItemCreate(
                equipment_id=eq.equipment_id,
                equipment_code=eq.equipment_code,
                equipment_name=eq.equipment_name,
                daily_rate=eq.daily_rental_rate or daily_rate,
                rental_days=rental_days
            ))
    else:
        # 单个设备
        order_items.append(schemas.OrderItemCreate(
            equipment_id=equipment.equipment_id,
            equipment_code=equipment.equipment_code,
            equipment_name=equipment.equipment_name,
            daily_rate=daily_rate,
            rental_days=rental_days
        ))
    
    # 构建备注（包含用途）
    remarks_parts = []
    if purpose:
        remarks_parts.append(f"用途: {purpose}")
    if remark:
        remarks_parts.append(f"备注: {remark}")
    final_remarks = "\n".join(remarks_parts) if remarks_parts else None
    
    # 创建订单
    order_data = schemas.LeaseOrderCreate(
        customer_id=customer.customer_id,
        customer_name=customer.customer_name,
        start_date=start_date,
        expected_return_date=end_date,
        remarks=final_remarks,
        order_items=order_items,
        created_by=applicant_name
    )
    
    # 调用CRUD函数创建订单
    created_order = crud.create_order(db, order_data)
    
    return {
        "code": 200,
        "message": "租赁申请创建成功",
        "data": {
            "id": str(created_order.order_id),
            "applicationCode": created_order.order_code
        }
    }


@app.post("/api/rental/application/{application_id}/approve", tags=["Rental"])
def approve_rental_application(application_id: str, db: Session = Depends(get_db)):
    """审批通过租赁申请"""
    order = db.query(models.LeaseOrder).filter(
        models.LeaseOrder.order_id == int(application_id)
    ).first()
    
    if order:
        order.status = models.OrderStatus.IN_PROGRESS
        db.commit()
    
    return {
        "code": 200,
        "message": "审批成功"
    }


@app.post("/api/rental/application/{application_id}/reject", tags=["Rental"])
def reject_rental_application(application_id: str, db: Session = Depends(get_db)):
    """拒绝租赁申请"""
    order = db.query(models.LeaseOrder).filter(
        models.LeaseOrder.order_id == int(application_id)
    ).first()
    
    if order:
        order.status = models.OrderStatus.CANCELLED
        db.commit()
    
    return {
        "code": 200,
        "message": "已拒绝"
    }


# ========== 航次管理 API ==========
@app.get("/api/rental/voyage", response_model=dict, tags=["Rental"])
def list_rental_voyages(
    current: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
    voyageNumber: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取航次列表（映射到租赁订单）"""
    skip = (current - 1) * pageSize
    
    query = db.query(models.LeaseOrder).filter(
        models.LeaseOrder.is_deleted == 0,
        models.LeaseOrder.voyage_no.isnot(None)
    )
    
    if voyageNumber:
        query = query.filter(models.LeaseOrder.voyage_no.contains(voyageNumber))
    if status:
        status_map = {
            "in-progress": "航次执行中",
            "completed": "已完结"
        }
        query = query.filter(models.LeaseOrder.status == status_map.get(status, status))
    
    total = query.count()
    items_db = query.order_by(models.LeaseOrder.created_at.desc()).offset(skip).limit(pageSize).all()
    
    items = []
    for order in items_db:
        equipment_list = ", ".join([item.equipment_name for item in order.order_items])
        
        status_map_reverse = {
            "航次执行中": "in-progress",
            "已完结": "completed"
        }
        
        items.append({
            "id": str(order.order_id),
            "voyageNumber": order.voyage_no or "",
            "rentalOrder": order.order_code,
            "vesselName": order.customer_name,
            "equipmentList": equipment_list,
            "usageHours": order.order_items[0].rental_days * 24 if order.order_items else 0,
            "voyageDate": order.start_date.strftime("%Y-%m-%d"),
            "status": status_map_reverse.get(order.status, "in-progress"),
            "remark": order.remarks
        })
    
    return {
        "code": 200,
        "message": "success",
        "list": items,
        "total": total
    }


@app.post("/api/rental/voyage", tags=["Rental"])
def create_rental_voyage(data: dict, db: Session = Depends(get_db)):
    """创建航次记录（更新订单的航次信息）"""
    from datetime import datetime
    
    rental_order_code = data.get("rentalOrder", "").strip()
    voyage_number = data.get("voyageNumber", "").strip()
    vessel_name = data.get("vesselName", "").strip()
    voyage_date_str = data.get("voyageDate")
    equipment_list = data.get("equipmentList", "").strip()
    usage_hours = int(data.get("usageHours", 0))
    remark = data.get("remark", "").strip()
    
    # 验证必填字段
    if not rental_order_code:
        raise HTTPException(status_code=400, detail="租赁订单号为必填项")
    if not voyage_number:
        raise HTTPException(status_code=400, detail="航次号为必填项")
    
    # 查找订单
    order = db.query(models.LeaseOrder).filter(
        models.LeaseOrder.order_code == rental_order_code,
        models.LeaseOrder.is_deleted == 0
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail=f"订单号 {rental_order_code} 不存在")
    
    # 更新订单的航次信息
    order.voyage_no = voyage_number
    if vessel_name:
        # 可以更新客户名称或添加备注
        pass
    
    # 解析航次日期
    if voyage_date_str:
        try:
            if isinstance(voyage_date_str, str):
                voyage_date = datetime.strptime(voyage_date_str.split('T')[0], "%Y-%m-%d").date()
                order.start_date = voyage_date
        except Exception:
            pass
    
    # 更新备注
    if remark:
        if order.remarks:
            order.remarks = f"{order.remarks}\n航次备注: {remark}"
        else:
            order.remarks = f"航次备注: {remark}"
    
    # 如果订单状态是"待提货"，更新为"航次执行中"
    if order.status == models.OrderStatus.PENDING:
        order.status = models.OrderStatus.IN_PROGRESS
    
    db.commit()
    db.refresh(order)
    
    return {
        "code": 200,
        "message": "航次创建成功",
        "data": {
            "id": str(order.order_id),
            "voyageNumber": voyage_number
        }
    }


@app.post("/api/rental/voyage/{voyage_id}/complete", tags=["Rental"])
def complete_rental_voyage(voyage_id: str, db: Session = Depends(get_db)):
    """完成航次"""
    order = db.query(models.LeaseOrder).filter(
        models.LeaseOrder.order_id == int(voyage_id)
    ).first()
    
    if order:
        order.status = models.OrderStatus.COMPLETED
        db.commit()
    
    return {
        "code": 200,
        "message": "航次已完成"
    }


# ========== 归还管理 API ==========
@app.get("/api/rental/return", response_model=dict, tags=["Rental"])
def list_rental_returns(
    current: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    returnCode: Optional[str] = None,
    rentalOrder: Optional[str] = None,
    equipmentCode: Optional[str] = None,
    inspectionStatus: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取归还记录列表"""
    skip = (current - 1) * pageSize
    
    query = db.query(models.ReturnRecord)
    
    if returnCode:
        query = query.filter(models.ReturnRecord.return_code.contains(returnCode))
    if inspectionStatus:
        status_map = {
            "pending": "待质检",
            "passed": "质检通过",
            "failed": "质检不通过"
        }
        query = query.filter(models.ReturnRecord.inspection_status == status_map.get(inspectionStatus, inspectionStatus))
    
    # 如果提供了订单号，需要关联查询
    if rentalOrder:
        query = query.join(models.LeaseOrder).filter(
            models.LeaseOrder.order_code.contains(rentalOrder),
            models.LeaseOrder.is_deleted == 0
        )
    
    # 如果提供了装备编号，需要关联查询归还明细
    if equipmentCode:
        query = query.join(models.ReturnItem).filter(
            models.ReturnItem.equipment_code.contains(equipmentCode)
        )
    
    total = query.count()
    items_db = query.order_by(models.ReturnRecord.created_at.desc()).offset(skip).limit(pageSize).all()
    
    items = []
    for ret in items_db:
        order = db.query(models.LeaseOrder).filter(
            models.LeaseOrder.order_id == ret.order_id
        ).first()
        
        # 获取归还明细
        return_items = db.query(models.ReturnItem).filter(
            models.ReturnItem.return_id == ret.return_id
        ).all()
        
        status_map_reverse = {
            "待质检": "pending",
            "质检通过": "passed",
            "质检不通过": "failed"
        }
        
        # 如果有归还明细，使用明细信息
        if return_items:
            for item in return_items:
                equipment_condition_str = "good"
                if item.equipment_condition == models.EquipmentCondition.NORMAL:
                    equipment_condition_str = "normal"
                elif item.equipment_condition == models.EquipmentCondition.DAMAGED:
                    equipment_condition_str = "damaged"
                
                items.append({
                    "id": str(ret.return_id),
                    "returnCode": ret.return_code,
                    "rentalOrder": order.order_code if order else "",
                    "equipmentCode": item.equipment_code,
                    "equipmentName": item.equipment_name,
                    "quantity": 1,
                    "returnTime": ret.return_date.strftime("%Y-%m-%d %H:%M:%S"),
                    "equipmentCondition": equipment_condition_str,
                    "damageDescription": item.damage_description or "",
                    "inspectionResult": ret.inspection_status,
                    "inspector": ret.return_person or "",
                    "inspectionStatus": status_map_reverse.get(ret.inspection_status, "pending"),
                    "remark": ret.remarks or ""
                })
        else:
            # 如果没有明细，至少返回主记录
            items.append({
                "id": str(ret.return_id),
                "returnCode": ret.return_code,
                "rentalOrder": order.order_code if order else "",
                "equipmentCode": "",
                "equipmentName": "",
                "quantity": ret.equipment_count,
                "returnTime": ret.return_date.strftime("%Y-%m-%d %H:%M:%S"),
                "equipmentCondition": "good",
                "damageDescription": "",
                "inspectionResult": ret.inspection_status,
                "inspector": ret.return_person or "",
                "inspectionStatus": status_map_reverse.get(ret.inspection_status, "pending"),
                "remark": ret.remarks or ""
            })
    
    return {
        "code": 200,
        "message": "success",
        "list": items,
        "total": total
    }


@app.post("/api/rental/return", tags=["Rental"])
def create_rental_return(data: dict, db: Session = Depends(get_db)):
    """创建归还记录"""
    from datetime import datetime
    
    rental_order_code = data.get("rentalOrder", "").strip()
    equipment_code = data.get("equipmentCode", "").strip()
    quantity = int(data.get("quantity", 1))
    return_time = data.get("returnTime")
    return_person = data.get("inspector", "").strip() or "系统"
    equipment_condition = data.get("equipmentCondition", "good")
    damage_description = data.get("damageDescription", "").strip()
    remark = data.get("remark", "").strip()
    
    # 验证必填字段
    if not rental_order_code:
        raise HTTPException(status_code=400, detail="租赁订单号为必填项")
    if not equipment_code:
        raise HTTPException(status_code=400, detail="装备编号为必填项")
    if quantity < 1:
        raise HTTPException(status_code=400, detail="数量必须大于0")
    
    # 查找订单
    order = db.query(models.LeaseOrder).filter(
        models.LeaseOrder.order_code == rental_order_code,
        models.LeaseOrder.is_deleted == 0
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail=f"订单号 {rental_order_code} 不存在")
    
    # 查找设备
    equipment = db.query(models.Equipment).filter(
        models.Equipment.equipment_code == equipment_code,
        models.Equipment.is_deleted == 0
    ).first()
    
    if not equipment:
        raise HTTPException(status_code=404, detail=f"装备编号 {equipment_code} 不存在")
    
    # 解析归还时间
    return_date = datetime.now()
    if return_time:
        try:
            if isinstance(return_time, str):
                return_date = datetime.strptime(return_time.split('T')[0], "%Y-%m-%d")
            elif isinstance(return_time, datetime):
                return_date = return_time
        except Exception:
            pass
    
    # 构建备注
    remarks_parts = []
    if damage_description:
        remarks_parts.append(f"损坏描述: {damage_description}")
    if remark:
        remarks_parts.append(f"备注: {remark}")
    final_remarks = "\n".join(remarks_parts) if remarks_parts else None
    
    # 创建归还记录
    return_record = schemas.ReturnRecordCreate(
        order_id=order.order_id,
        voyage_no=order.voyage_no,
        return_person=return_person,
        equipment_count=quantity,
        remarks=final_remarks
    )
    result = crud.create_return_record(db, return_record)
    
    # 创建归还明细
    equipment_condition_enum = models.EquipmentCondition.GOOD
    if equipment_condition == "normal":
        equipment_condition_enum = models.EquipmentCondition.NORMAL
    elif equipment_condition == "damaged":
        equipment_condition_enum = models.EquipmentCondition.DAMAGED
    
    db_return_item = models.ReturnItem(
        return_id=result.return_id,
        equipment_id=equipment.equipment_id,
        equipment_code=equipment.equipment_code,
        equipment_name=equipment.equipment_name,
        equipment_condition=equipment_condition_enum,
        damage_description=damage_description if damage_description else None,
        damage_fee=0.0  # 可以后续计算
    )
    db.add(db_return_item)
    
    # 更新订单的实际归还日期
    if not order.actual_return_date:
        order.actual_return_date = return_date.date()
    
    db.commit()
    db.refresh(result)
    
    return {
        "code": 200,
        "message": "归还记录创建成功",
        "data": {
            "id": str(result.return_id),
            "returnCode": result.return_code
        }
    }


@app.post("/api/rental/return/{return_id}/inspect", tags=["Rental"])
def inspect_rental_return(return_id: str, data: dict, db: Session = Depends(get_db)):
    """质检归还设备"""
    from datetime import datetime
    
    ret = db.query(models.ReturnRecord).filter(
        models.ReturnRecord.return_id == int(return_id)
    ).first()
    
    if not ret:
        raise HTTPException(status_code=404, detail="归还记录不存在")
    
    equipment_code = data.get("equipmentCode", "").strip()
    inspector = data.get("inspector", "").strip()
    appearance_status = data.get("equipmentCondition", "good")
    function_test = data.get("inspectionResult", "").strip()
    repair_needed = 1 if data.get("damageDescription") else 0
    repair_cost = float(data.get("repairCost", 0))
    remark = data.get("remark", "").strip()
    
    # 验证必填字段
    if not inspector:
        raise HTTPException(status_code=400, detail="质检员为必填项")
    
    # 查找设备
    equipment = None
    if equipment_code:
        equipment = db.query(models.Equipment).filter(
            models.Equipment.equipment_code == equipment_code,
            models.Equipment.is_deleted == 0
        ).first()
        
        if not equipment:
            raise HTTPException(status_code=404, detail=f"装备编号 {equipment_code} 不存在")
    
    # 如果没有指定设备，从归还明细中获取
    if not equipment:
        return_item = db.query(models.ReturnItem).filter(
            models.ReturnItem.return_id == ret.return_id
        ).first()
        if return_item:
            equipment = db.query(models.Equipment).filter(
                models.Equipment.equipment_id == return_item.equipment_id
            ).first()
    
    if not equipment:
        raise HTTPException(status_code=404, detail="未找到对应的设备")
    
    # 判断外观状态
    appearance_map = {
        "good": "完好",
        "normal": "轻微磨损",
        "damaged": "严重损坏"
    }
    appearance_status_str = appearance_map.get(appearance_status, "完好")
    
    # 判断功能测试结果
    function_test_str = "通过"
    if function_test and ("故障" in function_test or "不通过" in function_test):
        function_test_str = "故障"
        repair_needed = 1
    
    # 创建质检记录
    inspection_record = schemas.InspectionRecordCreate(
        return_id=ret.return_id,
        equipment_id=equipment.equipment_id,
        equipment_code=equipment.equipment_code,
        inspector=inspector,
        appearance_status=appearance_status_str,
        function_test=function_test_str,
        repair_needed=repair_needed,
        repair_cost=repair_cost,
        remarks=remark
    )
    
    crud.create_inspection_record(db, inspection_record)
    
    # 更新归还记录的质检状态
    inspection_status = data.get("inspectionStatus", "pending")
    status_map = {
        "passed": "质检通过",
        "failed": "质检不通过"
    }
    ret.inspection_status = status_map.get(inspection_status, "待质检")
    
    # 更新订单状态为已完成（如果所有设备都已归还并质检）
    order = db.query(models.LeaseOrder).filter(
        models.LeaseOrder.order_id == ret.order_id
    ).first()
    if order:
        # 检查是否所有设备都已归还
        total_order_items = len(order.order_items)
        total_returned = db.query(models.ReturnRecord).filter(
            models.ReturnRecord.order_id == order.order_id
        ).count()
        if total_returned >= total_order_items:
            order.status = models.OrderStatus.COMPLETED
    
        db.commit()
    
    return {
        "code": 200,
        "message": "质检完成"
    }


# ========== 结算管理 API ==========
@app.get("/api/settlement/fee", response_model=dict, tags=["Settlement"])
def list_settlement_fees(
    current: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
    settlementCode: Optional[str] = None,
    rentalOrder: Optional[str] = None,
    applicant: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取费用结算列表（映射到账单）"""
    skip = (current - 1) * pageSize
    
    query = db.query(models.Billing).filter(models.Billing.is_deleted == 0)
    
    if settlementCode:
        query = query.filter(models.Billing.bill_code.contains(settlementCode))
    if applicant:
        query = query.filter(models.Billing.customer_name.contains(applicant))
    if status:
        status_map = {
            "pending": "待确认",
            "paid": "已结清",
            "overdue": "逾期"
        }
        query = query.filter(models.Billing.status == status_map.get(status, status))
    
    # 如果提供了订单号，需要关联查询
    if rentalOrder:
        query = query.join(models.LeaseOrder).filter(
            models.LeaseOrder.order_code.contains(rentalOrder),
            models.LeaseOrder.is_deleted == 0
        )
    
    total = query.count()
    items_db = query.order_by(models.Billing.created_at.desc()).offset(skip).limit(pageSize).all()
    
    items = []
    for bill in items_db:
        order = db.query(models.LeaseOrder).filter(
            models.LeaseOrder.order_id == bill.order_id,
            models.LeaseOrder.is_deleted == 0
        ).first()
        
        rental_days = 0
        if order and order.order_items:
            rental_days = order.order_items[0].rental_days
        
        status_map_reverse = {
            "待确认": "pending",
            "已确认": "pending",
            "已结清": "paid",
            "逾期": "overdue"
        }
        
        # 转换支付方式
        payment_method_map = {
            "现金": "cash",
            "转账": "transfer",
            "支票": "check",
            "其他": "other"
        }
        payment_method = payment_method_map.get(bill.payment_method.value if bill.payment_method else "转账", "transfer")
        
        items.append({
            "id": str(bill.bill_id),
            "settlementCode": bill.bill_code,
            "rentalOrder": order.order_code if order else "",
            "applicant": bill.customer_name,
            "rentalDays": rental_days,
            "dailyRate": bill.rental_fee / rental_days if rental_days > 0 else 0,
            "equipmentFee": bill.rental_fee,
            "usageFee": bill.other_fee or 0,
            "damageFee": bill.repair_fee,
            "discount": bill.discount or 0,
            "totalAmount": bill.total_amount,
            "paymentMethod": payment_method,
            "settlementTime": bill.billing_date.strftime("%Y-%m-%d") if bill.billing_date else "",
            "status": status_map_reverse.get(bill.status.value if hasattr(bill.status, 'value') else bill.status, "pending"),
            "remark": bill.remarks or ""
        })
    
    return {
        "code": 200,
        "message": "success",
        "list": items,
        "total": total
    }


@app.post("/api/settlement/fee", tags=["Settlement"])
def create_settlement_fee(data: dict, db: Session = Depends(get_db)):
    """创建费用结算"""
    from datetime import datetime
    
    # 从前端获取数据
    rental_order_code = data.get("rentalOrder", "").strip()
    applicant = data.get("applicant", "").strip()
    rental_days = data.get("rentalDays")
    daily_rate = data.get("dailyRate")
    equipment_fee = data.get("equipmentFee")
    usage_fee = data.get("usageFee", 0)
    damage_fee = data.get("damageFee", 0)
    discount = data.get("discount", 0)
    total_amount = data.get("totalAmount", 0)
    payment_method_str = data.get("paymentMethod", "transfer").strip()
    remark = data.get("remark", "").strip()
    
    # 验证必填字段
    if not rental_order_code:
        raise HTTPException(status_code=400, detail="租赁订单号为必填项")
    
    # 查找订单
    order = db.query(models.LeaseOrder).filter(
        models.LeaseOrder.order_code == rental_order_code,
        models.LeaseOrder.is_deleted == 0
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail=f"订单号 {rental_order_code} 不存在")
    
    # 检查是否已经存在账单
    existing_bill = db.query(models.Billing).filter(
        models.Billing.order_id == order.order_id,
        models.Billing.is_deleted == 0
    ).first()
    
    if existing_bill:
        raise HTTPException(status_code=400, detail=f"订单 {rental_order_code} 已存在结算单")
    
    # 如果前端没有提供申请人，使用订单中的客户名称
    if not applicant:
        applicant = order.customer_name
    
    # 如果前端没有提供equipmentFee，从订单中计算
    if equipment_fee is None or equipment_fee == 0:
        equipment_fee = order.total_amount or 0.0
    
    # 如果前端没有提供rentalDays，从订单中获取
    if rental_days is None or rental_days == 0:
        if order.order_items:
            rental_days = order.order_items[0].rental_days
        else:
            # 计算租赁天数
            if order.start_date and order.expected_return_date:
                rental_days = (order.expected_return_date - order.start_date).days + 1
            else:
                rental_days = 0
    
    # 如果前端没有提供dailyRate，从订单明细中计算
    if daily_rate is None or daily_rate == 0:
        if order.order_items:
            daily_rate = order.order_items[0].daily_rate or 0.0
        else:
            daily_rate = equipment_fee / rental_days if rental_days > 0 else 0.0
    
    # 类型转换
    rental_days = int(rental_days) if rental_days else 0
    daily_rate = float(daily_rate) if daily_rate else 0.0
    equipment_fee = float(equipment_fee) if equipment_fee else 0.0
    usage_fee = float(usage_fee) if usage_fee else 0.0
    damage_fee = float(damage_fee) if damage_fee else 0.0
    discount = float(discount) if discount else 0.0
    total_amount = float(total_amount) if total_amount else 0.0
    
    # 转换支付方式
    payment_method_map = {
        "cash": models.PaymentMethod.CASH,
        "transfer": models.PaymentMethod.TRANSFER,
        "check": models.PaymentMethod.CHECK,
        "other": models.PaymentMethod.OTHER
    }
    payment_method = payment_method_map.get(payment_method_str, models.PaymentMethod.TRANSFER)
    
    # 生成账单编号
    max_bill = db.query(func.max(models.Billing.bill_id)).filter(
        models.Billing.is_deleted == 0
    ).scalar()
    next_id = (max_bill or 0) + 1
    bill_code = f"BILL{datetime.now().strftime('%Y%m%d')}{next_id:06d}"
    
    # 检查账单编号是否已存在
    existing_code = db.query(models.Billing).filter(
        models.Billing.bill_code == bill_code,
        models.Billing.is_deleted == 0
    ).first()
    if existing_code:
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        bill_code = f"BILL{timestamp}{next_id:04d}"
    
    # 计算总金额（如果前端没有提供，则根据各项费用计算）
    if total_amount == 0:
        base_amount = equipment_fee + usage_fee + damage_fee
        discount_amount = base_amount * (discount / 100)
        total_amount = base_amount - discount_amount
    
    # 直接创建账单记录（不使用CRUD函数，因为需要设置更多字段）
    bill = models.Billing(
        bill_code=bill_code,
        order_id=order.order_id,
        customer_name=applicant,
        rental_fee=equipment_fee,
        repair_fee=damage_fee,
        other_fee=usage_fee,
        discount=discount,
        total_amount=total_amount,
        payment_method=payment_method,
        billing_date=date.today(),
        status=models.BillingStatus.PENDING,
        remarks=remark if remark else None
    )
    
    db.add(bill)
    db.commit()
    db.refresh(bill)
    
    return {
        "code": 200,
        "message": "结算单创建成功",
        "data": {
            "id": str(bill.bill_id),
            "settlementCode": bill.bill_code
        }
    }


@app.post("/api/settlement/fee/{fee_id}/pay", tags=["Settlement"])
def pay_settlement_fee(fee_id: str, db: Session = Depends(get_db)):
    """支付结算费用"""
    bill = db.query(models.Billing).filter(
        models.Billing.bill_id == int(fee_id),
        models.Billing.is_deleted == 0
    ).first()
    
    if not bill:
        raise HTTPException(status_code=404, detail="结算单不存在")
    
    if bill.status == models.BillingStatus.PAID:
        raise HTTPException(status_code=400, detail="结算单已支付，无需重复支付")
    
    bill.status = models.BillingStatus.PAID
    bill.payment_date = date.today()
    db.commit()
    
    return {
        "code": 200,
        "message": "支付成功"
    }


# ========== 归还与质检 API ==========
@app.post("/api/returns", response_model=schemas.ReturnRecord, tags=["Return"])
def create_return(return_record: schemas.ReturnRecordCreate, db: Session = Depends(get_db)):
    """创建归还记录"""
    return crud.create_return_record(db, return_record)


@app.post("/api/inspections", response_model=schemas.InspectionRecord, tags=["Inspection"])
def create_inspection(inspection: schemas.InspectionRecordCreate, db: Session = Depends(get_db)):
    """创建质检记录"""
    return crud.create_inspection_record(db, inspection)


# ========== 认证 API ==========
@app.post("/api/auth/login", response_model=schemas.LoginResponse, tags=["Auth"])
def login(login_data: schemas.LoginRequest, db: Session = Depends(get_db)):
    """用户登录"""
    user = crud.authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    return schemas.LoginResponse(
        code=200,
        message="登录成功",
        data={
            "user_id": user.user_id,
            "username": user.username,
            "real_name": user.real_name,
            "role": user.role,
            "email": user.email,
            "phone": user.phone
        }
    )


@app.post("/api/auth/register", response_model=schemas.RegisterResponse, tags=["Auth"])
def register(register_data: schemas.RegisterRequest, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查用户名是否已存在
    existing_user = crud.get_user_by_username(db, register_data.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 创建用户
    user_create = schemas.UserCreate(
        username=register_data.username,
        password=register_data.password,
        real_name=register_data.real_name,
        email=register_data.email,
        phone=register_data.phone,
        role="operator"  # 默认角色为操作员
    )
    
    user = crud.create_user(db, user_create)
    
    return schemas.RegisterResponse(
        code=200,
        message="注册成功",
        data={
            "user_id": user.user_id,
            "username": user.username,
            "real_name": user.real_name,
            "email": user.email,
            "phone": user.phone
        }
    )


# ========== 用户信息管理 API ==========
@app.get("/api/user/info", response_model=schemas.User, tags=["User"])
def get_current_user_info(user_id: int = Query(..., description="用户ID"), db: Session = Depends(get_db)):
    """获取当前用户信息"""
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


@app.post("/api/user/my-project/list", tags=["User"])
def get_my_project_list(db: Session = Depends(get_db)):
    """获取我的项目列表（装饰性数据）"""
    # 返回系统项目信息
    return {
        "code": 200,
        "message": "success",
        "data": [
            {
                "id": 1,
                "name": "港口装备管理系统",
                "description": "船舶作业装备租赁与港口仓储管理系统",
                "peopleNumber": db.query(func.count(models.User.user_id)).filter(
                    models.User.is_deleted == 0,
                    models.User.status == "active"
                ).scalar() or 0,
                "contributors": []
            }
        ]
    }


@app.post("/api/user/my-team/list", tags=["User"])
def get_my_team_list(db: Session = Depends(get_db)):
    """获取我的团队列表（装饰性数据）"""
    # 按角色统计团队
    teams = []
    
    # 管理团队
    admin_count = db.query(func.count(models.User.user_id)).filter(
        models.User.is_deleted == 0,
        models.User.status == "active",
        models.User.role == "admin"
    ).scalar() or 0
    
    # 仓管团队
    warehouse_count = db.query(func.count(models.User.user_id)).filter(
        models.User.is_deleted == 0,
        models.User.status == "active",
        models.User.role == "warehouse"
    ).scalar() or 0
    
    # 财务团队
    finance_count = db.query(func.count(models.User.user_id)).filter(
        models.User.is_deleted == 0,
        models.User.status == "active",
        models.User.role == "finance"
    ).scalar() or 0
    
    # 操作团队
    operator_count = db.query(func.count(models.User.user_id)).filter(
        models.User.is_deleted == 0,
        models.User.status == "active",
        models.User.role == "operator"
    ).scalar() or 0
    
    teams = [
        {
            "id": 1,
            "avatar": "",
            "name": "管理团队",
            "peopleNumber": admin_count
        },
        {
            "id": 2,
            "avatar": "",
            "name": "仓管团队",
            "peopleNumber": warehouse_count
        },
        {
            "id": 3,
            "avatar": "",
            "name": "财务团队",
            "peopleNumber": finance_count
        },
        {
            "id": 4,
            "avatar": "",
            "name": "操作团队",
            "peopleNumber": operator_count
        }
    ]
    
    return {
        "code": 200,
        "message": "success",
        "data": teams
    }


@app.post("/api/user/latest-activity", tags=["User"])
def get_latest_activity(db: Session = Depends(get_db)):
    """获取最近活动（装饰性数据）"""
    # 获取最近的操作日志
    recent_logs = db.query(models.OperationLog).order_by(
        models.OperationLog.created_at.desc()
    ).limit(5).all()
    
    activities = []
    for log in recent_logs:
        activities.append({
            "id": log.log_id,
            "title": f"{log.username or '系统'} {log.action}",
            "description": log.description or f"{log.action} {log.table_name}",
            "avatar": ""
        })
    
    # 如果没有日志，返回默认活动
    if not activities:
        activities = [
            {
                "id": 1,
                "title": "系统初始化",
                "description": "装备租赁管理系统已就绪",
                "avatar": ""
            }
        ]
    
    return {
        "code": 200,
        "message": "success",
        "data": activities
    }


@app.put("/api/user/info/{user_id}", response_model=schemas.User, tags=["User"])
def update_current_user_info(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db)
):
    """更新当前用户信息"""
    user = crud.update_user(db, user_id, user_update)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


@app.post("/api/user/upload", tags=["User"])
async def upload_user_avatar(
    file: UploadFile = File(...),
    user_id: int = Form(...),
    db: Session = Depends(get_db)
):
    """上传用户头像"""
    try:
        # 读取文件内容
        contents = await file.read()
        
        # 创建上传目录
        import time
        import os
        from pathlib import Path
        
        # 创建 uploads/avatars 目录
        upload_dir = Path("uploads/avatars")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名（使用用户ID和时间戳）
        file_extension = os.path.splitext(file.filename)[1] if file.filename else '.jpg'
        filename = f"{user_id}_{int(time.time())}{file_extension}"
        file_path = upload_dir / filename
        
        # 保存文件到服务器
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # 生成可访问的URL
        avatar_url = f"/uploads/avatars/{filename}"
        
        # 更新用户头像URL到数据库
        user = crud.get_user_by_id(db, user_id)
        if user:
            user_update = schemas.UserUpdate(avatar=avatar_url)
            crud.update_user(db, user_id, user_update)
        
        return {
            "code": 200,
            "message": "上传成功",
            "data": {
                "url": avatar_url
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@app.post("/api/user/save-info", tags=["User"])
def save_user_info(
    user_id: int = Query(..., description="用户ID"),
    user_update: schemas.UserUpdate = Body(...),
    db: Session = Depends(get_db)
):
    """保存用户信息（兼容旧接口）"""
    user = crud.update_user(db, user_id, user_update)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {
        "code": 200,
        "message": "保存成功",
        "data": user
    }


# ========== 触发器日志管理 API ==========
@app.get("/api/trigger-logs", response_model=schemas.TriggerLogListResponse, tags=["System"])
def list_trigger_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    log_type: Optional[str] = None,
    trigger_name: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取触发器日志列表"""
    return crud.get_trigger_logs(
        db=db,
        page=page,
        page_size=page_size,
        log_type=log_type,
        trigger_name=trigger_name,
        start_date=start_date,
        end_date=end_date
    )


@app.get("/api/trigger-logs/{log_id}", response_model=schemas.TriggerLogResponse, tags=["System"])
def get_trigger_log(log_id: int, db: Session = Depends(get_db)):
    """获取单个触发器日志详情"""
    log = crud.get_trigger_log_by_id(db, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="日志不存在")
    return log


@app.post("/api/trigger-logs", response_model=schemas.TriggerLogResponse, tags=["System"])
def create_trigger_log(log_data: schemas.TriggerLogCreate, db: Session = Depends(get_db)):
    """创建触发器日志（供触发器调用）"""
    return crud.create_trigger_log(db, log_data)


# ========== 健康检查 ==========
@app.get("/health", tags=["System"])
def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "Port Equipment Management System"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

