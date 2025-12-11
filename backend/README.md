# 港口装备管理系统 - 后端服务

船舶作业装备租赁与港口仓储管理系统的后端API服务

## 项目结构

```
backend/
├── main.py                 # FastAPI 应用主入口
├── database.py            # 数据库连接配置
├── models.py              # SQLAlchemy 数据模型
├── schemas.py             # Pydantic 数据验证模型
├── crud.py                # 数据库 CRUD 操作
├── init_db.py             # 数据库初始化脚本
├── pyproject.toml         # 项目配置文件
├── uv.lock                # 依赖锁定文件
├── migrations/            # 数据库迁移脚本
│   ├── add_user_profile_fields_safe.sql     # 用户字段扩展
│   ├── create_trigger_logs.sql              # 创建触发器日志表
│   ├── create_triggers_fixed.sql            # 创建数据库触发器
│   ├── create_views.sql                     # 创建数据库视图
│   ├── upgrade.sql                          # 数据库升级脚本
│   ├── TRIGGERS_README.md                   # 触发器说明文档
│   └── VIEWS_README.md                      # 视图说明文档
└── uploads/               # 文件上传目录
    └── avatars/          # 用户头像
```

## 核心文件说明

### 主要文件

- **main.py**: FastAPI 应用的主入口，包含所有 API 路由定义
  - 设备管理 API
  - 客户管理 API
  - 租赁订单 API
  - 账单管理 API
  - 归还与质检 API
  - 用户认证 API
  - 工作台统计 API

- **database.py**: 数据库连接配置，使用 SQLAlchemy 连接 MySQL/OceanBase

- **models.py**: 定义所有数据库表模型（ORM）
  - Equipment（设备）
  - Customer（客户）
  - LeaseOrder（租赁订单）
  - Billing（账单）
  - ReturnRecord（归还记录）
  - InspectionRecord（质检记录）
  - User（用户）
  等...

- **schemas.py**: Pydantic 数据验证模型，用于 API 请求/响应验证

- **crud.py**: 数据库 CRUD 操作封装，包含业务逻辑处理

- **init_db.py**: 数据库初始化脚本，创建表并插入初始数据

## 环境配置

### 数据库配置

在 `database.py` 中配置数据库连接：

```python
DB_USER = 'root'
DB_PASSWORD = '123456'
DB_HOST = '127.0.0.1'
DB_PORT = 3306
DB_NAME = 'port_equipment_db'
```

### 依赖安装

使用 uv 工具管理依赖：

```bash
# 安装依赖
uv sync

# 或使用 pip
pip install fastapi uvicorn sqlalchemy pymysql python-multipart
```

## 使用指南

### 1. 初始化数据库

首先确保 MySQL/OceanBase 服务已启动，并创建数据库：

```sql
CREATE DATABASE port_equipment_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

然后运行初始化脚本：

```bash
python init_db.py
```

这将创建所有表并插入初始数据（管理员账户等）。

### 2. 运行数据库迁移（可选）

如果需要创建触发器和视图，可以手动执行 SQL 脚本：

```bash
# 创建触发器
mysql -u root -p port_equipment_db < migrations/create_triggers_fixed.sql

# 创建视图
mysql -u root -p port_equipment_db < migrations/create_views.sql

# 添加用户扩展字段
mysql -u root -p port_equipment_db < migrations/add_user_profile_fields_safe.sql
```

### 3. 启动后端服务

```bash
# 开发模式（自动重载）
python main.py

# 或使用 uvicorn
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

服务启动后，访问：
- API 文档: http://localhost:8000/docs
- 备用文档: http://localhost:8000/redoc
- API 根路径: http://localhost:8000/

## API 接口说明

### 主要接口模块

1. **设备管理** (`/api/equipment`)
   - GET: 获取设备列表
   - POST: 创建设备
   - PUT: 更新设备
   - DELETE: 删除设备

2. **租赁管理** (`/api/orders`, `/api/rental`)
   - 租赁订单管理
   - 租赁申请管理
   - 航次管理
   - 归还管理

3. **账单管理** (`/api/billing`, `/api/settlement`)
   - 账单查询
   - 费用结算
   - 支付管理

4. **用户管理** (`/api/user`, `/api/auth`)
   - 用户登录/注册
   - 用户信息管理
   - 头像上传

5. **工作台** (`/api/dashboard`)
   - 统计数据
   - 图表数据
   - 热门设备列表

详细 API 文档请访问 http://localhost:8000/docs

## 数据库特性

### 触发器

系统使用触发器自动处理以下业务逻辑：
- 订单金额自动计算
- 设备状态自动更新
- 账单金额自动计算
- 操作日志自动记录

详见 `migrations/TRIGGERS_README.md`

### 视图

系统创建了多个视图以优化查询性能：
- `v_equipment_inventory`: 设备库存视图
- `v_order_summary`: 订单汇总视图
- `v_customer_rental_stats`: 客户租赁统计视图
- `v_billing_summary`: 财务汇总视图

详见 `migrations/VIEWS_README.md`

## 默认账户

初始化后可使用以下账户登录：

- **管理员**
  - 用户名: `admin`
  - 密码: `admin123`

- **操作员**
  - 用户名: `zhanggong`
  - 密码: `123456`

## 开发说明

### 添加新功能

1. 在 `models.py` 中添加/修改数据模型
2. 在 `schemas.py` 中添加对应的 Pydantic 模型
3. 在 `crud.py` 中实现业务逻辑
4. 在 `main.py` 中添加 API 路由

### 数据库迁移

如需修改数据库结构：
1. 在 `migrations/` 目录创建新的 SQL 文件
2. 按照现有格式编写迁移脚本
3. 手动执行 SQL 文件或编写 Python 脚本执行

## 技术栈

- **Web 框架**: FastAPI
- **ORM**: SQLAlchemy
- **数据验证**: Pydantic
- **数据库**: MySQL / OceanBase
- **服务器**: Uvicorn (ASGI)
- **包管理**: uv / pip

## 注意事项

1. 数据库连接信息（用户名/密码）应使用环境变量配置，不要直接写在代码中
2. 生产环境建议使用更安全的密码哈希算法（如 bcrypt）
3. 文件上传路径需要在生产环境配置正确的权限
4. 建议配置 CORS 白名单，不要使用 `allow_origins=["*"]`

## 故障排查

### 数据库连接失败
- 检查 MySQL/OceanBase 服务是否启动
- 检查数据库连接参数是否正确
- 检查用户权限是否足够

### 表不存在
- 运行 `python init_db.py` 初始化数据库
- 检查数据库名是否正确

### 触发器/视图错误
- 手动执行 migrations 目录下的 SQL 文件
- 检查 SQL 语法是否与数据库版本兼容

## 更新日志

### 2024-12-11
- 整理后端代码结构
- 删除无用的临时脚本文件：
  - create_database.py
  - create_triggers.py
  - create_triggers_fixed.py
  - create_triggers_simple.py
  - create_views.py
  - create_views_direct.py
  - crud_views.py
  - update_database.py
  - generate_test_data.py
- 删除重复的迁移文件
- 更新 README 文档

## 许可证

[请添加许可证信息]

