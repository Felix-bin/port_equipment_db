# 用户设置页面

## 概述

用户设置页面基于数据库 `users` 表的实际字段重新设计和实现。页面分为四个主要部分：

1. **用户面板** - 展示用户头像和基本信息
2. **基础信息** - 可编辑的个人信息
3. **账户信息** - 只读的账户详情
4. **安全设置** - 密码修改和安全相关功能

## 数据库字段映射

### users 表字段

根据 `backend/models.py` 中的 `User` 模型，以下字段被使用：

| 数据库字段 | 类型 | 说明 | 页面位置 |
|-----------|------|------|---------|
| `user_id` | Integer | 用户ID（主键） | 账户信息 |
| `username` | String | 用户名（唯一） | 用户面板、账户信息 |
| `password_hash` | String | 密码哈希 | 安全设置 |
| `real_name` | String | 真实姓名 | 用户面板、基础信息 |
| `role` | String | 角色 | 用户面板、账户信息 |
| `phone` | String | 电话 | 用户面板、基础信息、安全设置 |
| `email` | String | 邮箱 | 用户面板、基础信息、安全设置 |
| `status` | String | 状态（active/inactive） | 用户面板、账户信息 |
| `last_login` | DateTime | 最后登录时间 | 账户信息 |
| `nickname` | String | 昵称 | 基础信息 |
| `address` | String | 地址 | 基础信息 |
| `profile` | Text | 个人简介 | 基础信息 |
| `country_region` | String | 国家/地区 | 基础信息 |
| `area` | String | 地区 | 基础信息 |
| `avatar` | String | 头像URL | 用户面板 |
| `created_at` | DateTime | 创建时间 | 账户信息 |
| `updated_at` | DateTime | 更新时间 | 账户信息 |

## 组件结构

### 1. index.vue

主页面组件，包含面包屑导航和标签页布局。

**标签页：**
- 基础信息 (Basic Information)
- 账户信息 (Account Information)
- 安全设置 (Security Settings)

### 2. components/user-panel.vue

**功能：**
- 展示用户头像（支持上传）
- 显示用户基本信息（只读）
  - 用户名
  - 真实姓名
  - 角色（带颜色标签）
  - 状态（激活/停用）
  - 邮箱
  - 手机号

**特性：**
- 头像上传功能（调用 `/api/user/upload` 接口）
- 角色颜色映射：
  - admin（管理员）: 红色
  - warehouse（仓管员）: 蓝色
  - finance（财务）: 绿色
  - operator（操作员）: 橙色

### 3. components/basic-information.vue

**可编辑字段：**
- 真实姓名 (real_name)
- 昵称 (nickname)
- 手机号 (phone) - 带格式验证
- 邮箱 (email) - 带格式验证
- 国家/地区 (country_region) - 下拉选择
- 所在区域 (area)
- 详细地址 (address) - 文本域
- 个人简介 (profile) - 文本域，最多200字

**验证规则：**
- 手机号：正则验证（`/^1[3-9]\d{9}$/`）
- 邮箱：邮箱格式验证
- 个人简介：最大长度200字符

**API调用：**
- 加载数据：`GET /api/user/info?user_id={id}`
- 保存数据：`POST /api/user/save-info?user_id={id}`

### 4. components/account-info.vue

**只读信息展示：**
使用 `a-descriptions` 组件展示以下信息：
- 用户ID
- 用户名
- 角色（翻译后的文本）
- 状态（翻译后的文本）
- 注册时间
- 最后更新时间
- 最后登录时间

**日期格式化：**
- 格式：`YYYY-MM-DD HH:mm:ss`

### 5. components/security-settings.vue

**功能：**
1. **密码修改**
   - 原密码输入
   - 新密码输入（最少6位字符）
   - 确认新密码（必须匹配）
   - 展开/收起表单

2. **安全手机**
   - 显示绑定的手机号（脱敏显示）
   - 格式：`138****5678`

3. **安全邮箱**
   - 显示绑定的邮箱（脱敏显示）
   - 格式：`abc***@example.com`

**脱敏规则：**
- 手机号：保留前3位和后4位
- 邮箱：保留用户名前3位（或一半）

## API接口

### 1. 获取用户信息
```
GET /api/user/info?user_id={id}
```

**响应：**
```json
{
  "user_id": 1,
  "username": "admin",
  "real_name": "张三",
  "role": "admin",
  "status": "active",
  "phone": "13800138000",
  "email": "admin@example.com",
  "nickname": "管理员",
  "address": "北京市朝阳区",
  "profile": "系统管理员",
  "country_region": "中国",
  "area": "北京",
  "avatar": "/uploads/avatars/1_xxx.jpg",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-10T12:00:00",
  "last_login": "2024-01-10T15:30:00"
}
```

### 2. 保存用户信息
```
POST /api/user/save-info?user_id={id}
```

**请求体：**
```json
{
  "real_name": "张三",
  "nickname": "管理员",
  "phone": "13800138000",
  "email": "admin@example.com",
  "country_region": "中国",
  "area": "北京",
  "address": "北京市朝阳区",
  "profile": "系统管理员"
}
```

### 3. 上传头像
```
POST /api/user/upload
Content-Type: multipart/form-data
```

**请求参数：**
- `file`: 图片文件
- `user_id`: 用户ID

**响应：**
```json
{
  "code": 200,
  "message": "上传成功",
  "data": {
    "url": "/uploads/avatars/1_1234567890.jpg"
  }
}
```

## 国际化

### 中文 (zh-CN)

所有翻译键都在 `locale/zh-CN.ts` 中定义，包括：
- 标签页标题
- 表单标签
- 按钮文本
- 验证错误消息
- 角色和状态标签

### 英文 (en-US)

对应的英文翻译在 `locale/en-US.ts` 中。

**关键翻译键：**
- `userSetting.tab.basicInformation` - 基础信息
- `userSetting.tab.accountInfo` - 账户信息
- `userSetting.tab.securitySettings` - 安全设置
- `userSetting.role.admin` - 管理员
- `userSetting.status.active` - 激活

## 样式

### 响应式设计

- 桌面端（>768px）：使用最大宽度容器，表单居中显示
- 移动端（≤768px）：全宽布局，减小内边距

### 主题支持

- 使用Arco Design的CSS变量系统
- 支持亮色/暗色主题切换
- 颜色使用语义化变量（如 `--color-bg-2`，`rgb(var(--gray-8))`）

## 使用指南

### 查看用户信息

1. 登录系统后，点击顶部导航栏的用户头像或用户名
2. 选择"用户设置"菜单项
3. 默认显示用户面板，展示头像和基本信息

### 修改基础信息

1. 切换到"基础信息"标签页
2. 编辑需要修改的字段
3. 点击"保存"按钮提交修改
4. 点击"重置"按钮可恢复到原始值

### 查看账户信息

1. 切换到"账户信息"标签页
2. 查看只读的账户详细信息

### 修改密码

1. 切换到"安全设置"标签页
2. 点击密码卡片中的"修改"按钮
3. 填写原密码和新密码
4. 点击"保存"按钮提交修改
5. 修改成功后需要重新登录

### 上传头像

1. 在用户面板区域，将鼠标悬停在头像上
2. 点击"更换头像"按钮
3. 选择图片文件（支持jpg、png等格式）
4. 上传成功后头像会自动更新

## 技术栈

- **Vue 3** - 组合式API (Composition API)
- **TypeScript** - 类型安全
- **Arco Design Vue** - UI组件库
- **Vue I18n** - 国际化
- **Axios** - HTTP客户端

## 注意事项

1. **权限控制**：用户只能修改自己的信息，角色和状态字段由管理员控制
2. **数据验证**：前端进行基本验证，后端需要进行完整的业务逻辑验证
3. **密码修改**：修改密码后建议引导用户重新登录
4. **头像上传**：建议限制文件大小（如2MB）和格式（jpg、png）
5. **敏感信息**：手机号和邮箱在显示时进行脱敏处理

## 后续优化建议

1. 添加密码强度校验（必须包含数字、字母、特殊字符等）
2. 实现手机号和邮箱的验证码验证
3. 添加头像裁剪功能
4. 实现密保问题设置
5. 添加操作日志记录
6. 支持更多的国家/地区选择
7. 实现二次验证（2FA）

