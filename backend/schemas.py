from pydantic import BaseModel, Field, field_validator, field_serializer
from typing import Optional, List
from datetime import datetime, date
from models import EquipmentStatus, OrderStatus, BillingStatus, InspectionResult


# 设备相关 Schemas
class EquipmentBase(BaseModel):
    equipment_code: Optional[str] = None
    equipment_name: str
    category: str
    storage_location: Optional[str] = None
    purchase_price: Optional[float] = 0.0
    daily_rental_rate: Optional[float] = 0.0
    specifications: Optional[str] = None
    remarks: Optional[str] = None


class EquipmentCreate(EquipmentBase):
    pass


class EquipmentUpdate(BaseModel):
    equipment_name: Optional[str] = None
    category: Optional[str] = None
    status: Optional[EquipmentStatus] = None
    storage_location: Optional[str] = None
    daily_rental_rate: Optional[float] = None
    specifications: Optional[str] = None
    remarks: Optional[str] = None

    @field_validator('status', mode='before')
    @classmethod
    def parse_status(cls, v):
        if v is None:
            return v

        # Handle both Chinese and English status values
        status_mapping = {
            "在库": EquipmentStatus.IN_STOCK,
            "已出库": EquipmentStatus.OUT,
            "维修中": EquipmentStatus.MAINTENANCE,
            "已报废": EquipmentStatus.SCRAPPED,
            "IN_STOCK": EquipmentStatus.IN_STOCK,
            "OUT": EquipmentStatus.OUT,
            "MAINTENANCE": EquipmentStatus.MAINTENANCE,
            "SCRAPPED": EquipmentStatus.SCRAPPED,
        }

        if isinstance(v, str):
            v_clean = v.strip()
            if v_clean in status_mapping:
                return status_mapping[v_clean]
            # Try to convert directly to enum if it's a valid value
            try:
                return EquipmentStatus(v_clean)
            except ValueError:
                raise ValueError(f"Invalid status value: {v}. Valid values are: {list(status_mapping.keys())}")

        return v


class Equipment(EquipmentBase):
    equipment_id: int
    status: EquipmentStatus
    created_at: datetime
    updated_at: datetime

    @field_serializer('status')
    def serialize_status(self, value: EquipmentStatus) -> str:
        # Convert enum values back to Chinese for frontend compatibility
        status_mapping = {
            EquipmentStatus.IN_STOCK: "在库",
            EquipmentStatus.OUT: "已出库",
            EquipmentStatus.MAINTENANCE: "维修中",
            EquipmentStatus.SCRAPPED: "已报废",
        }
        return status_mapping.get(value, str(value.value))

    class Config:
        from_attributes = True


# 客户相关 Schemas
class CustomerBase(BaseModel):
    customer_name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    credit_rating: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    customer_name: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    credit_rating: Optional[str] = None


class Customer(CustomerBase):
    customer_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# 订单明细 Schemas
class OrderItemBase(BaseModel):
    equipment_id: int
    equipment_code: str
    equipment_name: str
    daily_rate: float
    rental_days: Optional[int] = 0


class OrderItemCreate(OrderItemBase):
    pass


class OrderItem(OrderItemBase):
    item_id: int
    order_id: int
    subtotal: float
    created_at: datetime

    class Config:
        from_attributes = True


# 租赁订单 Schemas
class LeaseOrderBase(BaseModel):
    customer_id: int
    customer_name: str
    voyage_no: Optional[str] = None
    start_date: date
    expected_return_date: Optional[date] = None
    remarks: Optional[str] = None


class LeaseOrderCreate(LeaseOrderBase):
    order_items: List[OrderItemCreate]
    created_by: Optional[str] = None


class LeaseOrderUpdate(BaseModel):
    voyage_no: Optional[str] = None
    expected_return_date: Optional[date] = None
    actual_return_date: Optional[date] = None
    status: Optional[OrderStatus] = None
    remarks: Optional[str] = None


class LeaseOrder(LeaseOrderBase):
    order_id: int
    order_code: str
    status: OrderStatus
    total_amount: float
    actual_return_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime
    order_items: List[OrderItem] = []

    class Config:
        from_attributes = True


# 账单 Schemas
class BillingBase(BaseModel):
    order_id: int
    customer_name: str
    rental_fee: float = 0.0
    repair_fee: float = 0.0
    other_fee: float = 0.0


class BillingCreate(BillingBase):
    pass


class BillingUpdate(BaseModel):
    rental_fee: Optional[float] = None
    repair_fee: Optional[float] = None
    other_fee: Optional[float] = None
    status: Optional[BillingStatus] = None
    payment_date: Optional[date] = None
    remarks: Optional[str] = None


class Billing(BillingBase):
    bill_id: int
    bill_code: str
    total_amount: float
    status: BillingStatus
    billing_date: date
    payment_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 归还记录 Schemas
class ReturnRecordBase(BaseModel):
    order_id: int
    voyage_no: Optional[str] = None
    return_person: Optional[str] = None
    equipment_count: int = 0
    remarks: Optional[str] = None


class ReturnRecordCreate(ReturnRecordBase):
    pass


class ReturnRecord(ReturnRecordBase):
    return_id: int
    return_code: str
    return_date: datetime
    inspection_status: str
    created_at: datetime

    class Config:
        from_attributes = True


# 质检记录 Schemas
class InspectionRecordBase(BaseModel):
    equipment_id: int
    equipment_code: str
    inspector: str
    appearance_status: str
    function_test: str
    repair_needed: int = 0
    repair_cost: float = 0.0
    remarks: Optional[str] = None


class InspectionRecordCreate(InspectionRecordBase):
    return_id: int


class InspectionRecord(InspectionRecordBase):
    inspection_id: int
    return_id: int
    result: InspectionResult
    inspection_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# 用户 Schemas
class UserBase(BaseModel):
    username: str
    real_name: Optional[str] = None
    role: str = "operator"
    phone: Optional[str] = None
    email: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    real_name: Optional[str] = None
    role: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    status: Optional[str] = None
    nickname: Optional[str] = None  # 昵称
    address: Optional[str] = None  # 地址
    profile: Optional[str] = None  # 个人简介
    country_region: Optional[str] = None  # 国家/地区
    area: Optional[str] = None  # 地区
    avatar: Optional[str] = None  # 头像URL


class User(UserBase):
    user_id: int
    status: str
    nickname: Optional[str] = None
    address: Optional[str] = None
    profile: Optional[str] = None
    country_region: Optional[str] = None
    area: Optional[str] = None
    avatar: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# 认证相关 Schemas
class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    real_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class LoginResponse(BaseModel):
    code: int = 200
    message: str = "登录成功"
    data: dict
    token: Optional[str] = None


class RegisterResponse(BaseModel):
    code: int = 200
    message: str = "注册成功"
    data: dict


# 通用响应 Schema
class Response(BaseModel):
    code: int = 200
    message: str = "success"
    data: Optional[dict] = None


# 分页响应 Schema
class PageResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: List = []
    total: int = 0
    page: int = 1
    page_size: int = 10


# 统计数据 Schema
class DashboardStats(BaseModel):
    total_equipment: int = 0
    in_stock: int = 0
    out_stock: int = 0
    maintenance: int = 0
    pending_checkout: int = 0
    in_progress_orders: int = 0
    pending_inspection: int = 0
    total_revenue: float = 0.0
    pending_amount: float = 0.0
    overdue_bills: int = 0


# 租赁分析统计 Schema
class RentalAnalysisStats(BaseModel):
    # 基础统计
    total_orders: int = 0  # 租赁订单总数
    total_outbound: int = 0  # 装备出库量
    total_renting: int = 0  # 在租装备数
    total_returned: int = 0  # 归还装备数
    
    # 增长数据（较昨日）
    orders_growth: float = 0.0
    outbound_growth: float = 0.0
    renting_growth: float = 0.0
    returned_growth: float = 0.0
    
    # 图表数据
    category_ratio: List[dict] = []  # 装备类型租赁比例 [{name: str, value: int}]
    popular_equipment: List[dict] = []  # 热门租赁装备 [{equipment_name: str, rental_count: int, rental_days: int}]
    period_analysis: dict = {}  # 租赁时段分析 {xAxis: List[str], data: List[dict]}


# 多维数据分析 Schema
class MultiDimensionAnalysisStats(BaseModel):
    # 数据概览
    data_overview: dict = {}  # {xAxis: List[str], data: List[{name: str, value: List[int], count: int}]}
    
    # 数据链增长
    data_chain_growth: dict = {}  # {quota: str -> {count: int, growth: float, chartData: {xAxis: List[str], data: {name: str, value: List[int]}}}}
    
    # 用户行为
    user_actions: dict = {}  # {data: List[int]}  # 点赞量、评论量、分享量
    
    # 内容类型分布（雷达图）
    content_type_distribution: dict = {}  # {indicator: List[{name: str, max: int}], data: List[{name: str, value: List[int]}]}
    
    # 内容发布来源
    content_publishing_source: dict = {}  # {data: List[{name: str, value: List[int]}]}  # 3个饼图的数据


# 兼容旧接口的响应模型
class DataOverviewResponse(BaseModel):
    xAxis: List[str] = []
    data: List[dict] = []


class DataChainGrowthResponse(BaseModel):
    count: int = 0
    growth: float = 0.0
    chartData: dict = {}


# ========== 触发器日志相关 ==========
class TriggerLogBase(BaseModel):
    log_type: str  # success, info, warning, error
    trigger_name: str
    operation: str
    table_name: Optional[str] = None
    record_id: Optional[int] = None
    description: Optional[str] = None


class TriggerLogCreate(TriggerLogBase):
    pass


class TriggerLogResponse(TriggerLogBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class TriggerLogListResponse(BaseModel):
    items: List[TriggerLogResponse]
    total: int
    page: int
    page_size: int

