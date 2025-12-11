# 快速启动指南

## 1. 环境配置

### 创建环境变量文件

在 `web` 目录下创建 `.env.development` 文件：

**Windows (PowerShell):**
```powershell
echo "VITE_API_BASE_URL=http://localhost:8000" > .env.development
```

**Windows (CMD):**
```cmd
echo VITE_API_BASE_URL=http://localhost:8000 > .env.development
```

**Mac/Linux:**
```bash
echo "VITE_API_BASE_URL=http://localhost:8000" > .env.development
```

**或者手动创建：**
1. 在 `web` 目录下创建文件 `.env.development`
2. 添加以下内容：
```
VITE_API_BASE_URL=http://localhost:8000
```

## 2. 启动服务

### 启动后端服务

```bash
# 在项目根目录的 backend 文件夹中
cd backend
python main.py
```

后端服务将在 `http://localhost:8000` 启动

### 启动前端服务

```bash
# 在项目根目录的 web 文件夹中
cd web
npm run dev
# 或
pnpm dev
```

前端服务将在 `http://localhost:5173` 启动

## 3. 访问系统

打开浏览器访问：`http://localhost:5173`

### 测试账号

- 用户名：`test` 或 `admin`
- 密码：(使用你在数据库中设置的密码)

## 4. 功能说明

### 右上角用户区域

现在包含：
- 🌐 **语言切换** - 中文/English 切换
- 🌓 **主题切换** - 亮色/暗色模式切换
- 🖥️ **全屏切换** - 进入/退出全屏模式
- 👤 **用户名显示** - 显示真实姓名
- 🏷️ **角色标签** - 显示当前用户角色（管理员/仓管员/财务/操作员）
- 🖼️ **用户头像** - 显示真实头像（点击展开菜单）
  - ⚙️ 用户设置
  - 🚪 退出登录

### 用户设置页面

包含三个标签页：
1. **基础信息** - 可编辑个人信息
2. **账户信息** - 只读账户详情
3. **安全设置** - 密码修改

## 5. 常见问题

### 头像显示404错误

**原因：** 没有配置环境变量 `VITE_API_BASE_URL`

**解决：**
1. 创建 `.env.development` 文件（见上方步骤1）
2. 重启前端开发服务器

### 用户信息显示为空

**原因：** 使用了 mock 数据

**解决：**
1. 确保 `web/src/main.ts` 中的 `import './mock';` 已被注释
2. 确保后端服务正在运行
3. 重新登录

### API请求失败

**检查：**
1. 后端服务是否正在运行（`http://localhost:8000`）
2. 检查浏览器控制台的网络请求
3. 确认环境变量配置正确

## 6. 目录结构

```
port_equipment_db/
├── backend/              # 后端服务
│   ├── main.py          # 主程序入口
│   ├── models.py        # 数据库模型
│   └── uploads/         # 上传文件目录
│       └── avatars/     # 用户头像
└── web/                 # 前端应用
    ├── .env.development # 开发环境配置 (需要创建)
    ├── src/
    │   ├── api/         # API接口
    │   ├── components/  # 组件
    │   │   └── navbar/  # 导航栏组件
    │   └── views/       # 页面视图
    │       └── user/
    │           └── setting/  # 用户设置页面
    └── package.json
```

## 7. 开发提示

### 查看API文档

后端启动后，访问：`http://localhost:8000/docs`

### 调试模式

如需启用调试信息，在用户设置页面 `index.vue` 中：
```typescript
const isDevelopment = ref(true); // 设为 true
```

这将显示调试信息卡片，帮助诊断问题。

