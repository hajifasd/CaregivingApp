# 护工资源管理系统

一个现代化的护工资源管理平台，提供用户注册、护工管理、预约服务等功能。

## 🏗️ 项目结构

```
CaregivingApp/
├── 📁 back/                    # 后端核心代码
│   ├── 📁 api/                # API接口模块
│   │   ├── admin.py          # 管理员API
│   │   ├── auth.py           # 认证API
│   │   └── caregiver.py      # 护工API
│   ├── 📁 config/            # 配置文件
│   │   └── settings.py       # 应用配置
│   ├── 📁 models/            # 数据模型
│   │   ├── user.py           # 用户模型
│   │   ├── caregiver.py      # 护工模型
│   │   ├── service.py        # 服务模型
│   │   └── business.py       # 业务模型
│   ├── 📁 services/          # 业务逻辑层
│   │   ├── user_service.py   # 用户服务
│   │   └── caregiver_service.py # 护工服务
│   ├── 📁 utils/             # 工具函数
│   │   ├── auth.py           # 认证工具
│   │   └── file_upload.py    # 文件上传工具
│   ├── app.py                # 主应用入口
│   └── extensions.py         # Flask扩展初始化
│
├── 📁 web/                    # 前端Web界面
│   ├── index.html            # 主入口页面
│   ├── script.js             # 公共脚本文件
│   ├── style.css             # 公共样式文件
│   ├── 📁 admin/             # 管理端模块
│   │   ├── admin-dashboard.html      # 管理仪表板
│   │   ├── admin-login.html          # 管理员登录
│   │   ├── admin-users.html          # 用户管理
│   │   ├── admin-caregivers.html    # 护工管理
│   │   ├── admin-job-analysis.html  # 工作分析
│   │   └── 📁 components/           # 管理端组件
│   ├── 📁 user/              # 用户端模块
│   │   ├── user-home.html            # 用户主页
│   │   ├── user-dashboard.html       # 用户仪表板
│   │   ├── user-register.html        # 用户注册
│   │   ├── user-caregivers.html      # 护工列表
│   │   ├── user-appointments.html    # 预约管理
│   │   ├── user-employments.html     # 雇佣管理
│   │   ├── user-messages.html        # 消息管理
│   │   ├── user-profile.html         # 用户资料
│   │   └── 📁 components/            # 用户端组件
│   ├── 📁 caregiver/         # 护工端模块
│   │   ├── caregiver-dashboard.html  # 护工仪表板
│   │   ├── caregiver-register.html   # 护工注册
│   │   └── 📁 components/            # 护工端组件
│   ├── 📁 components/        # 通用组件库
│   ├── 📁 js/                # JavaScript模块
│   ├── 📁 css/               # 样式文件
│   └── 📁 uploads/           # 文件上传目录
│
├── 📁 docs/                   # 项目文档
│   ├── DATABASE_STATUS.md     # 数据库状态
│   ├── PROJECT_ANALYSIS.md    # 项目分析
│   ├── PROJECT_STRUCTURE.md   # 项目结构
│   ├── 数据库迁移操作指南.md   # 数据库迁移指南
│   └── mysql_config.md       # MySQL配置说明
│
├── 📁 scripts/                # 实用脚本
│   ├── database_status.py     # 数据库状态检查
│   └── import_data_to_mysql.py # 数据导入脚本
│
├── 📁 database/               # 数据库相关文件
│   ├── caregiving.db         # SQLite备份数据库
│   ├── manage_database.py    # 数据库管理脚本
│   ├── migrate_to_mysql.py   # 迁移脚本
│   └── README.md             # 数据库说明
│
├── requirements.txt            # Python依赖包
└── README.md                  # 项目说明文档
```

## 🚀 快速开始

### 1. 环境要求
- Python 3.8+
- MySQL 8.0+
- 现代浏览器
- Node.js (用于Socket.IO服务器)

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 数据库配置
- 确保MySQL服务运行
- 创建数据库 `caregiving_db`
- 配置 `back/config/settings.py` 中的数据库连接信息

### 4. 启动应用
```bash
cd back
python app.py
```

### 5. 启动聊天服务器 (可选)
```bash
# 如果需要实时聊天功能
cd web
npm install socket.io
node chat-server.js
```

### 6. 访问应用
- 主页: http://localhost:5000/
- 管理端: http://localhost:5000/admin/admin-login.html
- 用户端: http://localhost:5000/user/user-home.html
- 护工端: http://localhost:5000/caregiver/caregiver-register.html

## 🔧 实用工具

### 检查数据库状态
```bash
python scripts/database_status.py
```

### 导入数据到MySQL
```bash
python scripts/import_data_to_mysql.py
```

## 📊 数据库状态

- **数据库类型**: MySQL 8.0.40
- **表数量**: 8个
- **总记录数**: 19条
- **连接状态**: ✅ 正常

详细状态请查看: `docs/DATABASE_STATUS.md`

## 🎯 主要功能

- 👥 用户管理 (注册、登录、个人资料)
- 👨‍⚕️ 护工管理 (注册、审核、资质管理)
- 📅 预约服务 (在线预约、时间管理)
- 💼 雇佣管理 (长期雇佣关系)
- 💬 实时聊天 (用户与护工即时沟通)
- 📊 数据分析 (工作数据统计)
- 📁 文件上传 (身份证、证书等)

## 📝 技术栈

- **后端**: Flask + SQLAlchemy + PyMySQL
- **前端**: HTML5 + CSS3 + JavaScript
- **数据库**: MySQL 8.0
- **认证**: JWT + bcrypt
- **实时通信**: Socket.IO + WebSocket
- **文件处理**: 支持图片和PDF上传

## 🎨 前端架构特点

### 模块化设计
- **管理端 (admin/)**: 系统管理、用户监控、数据分析
- **用户端 (user/)**: 护工预约、服务管理、沟通交流
- **护工端 (caregiver/)**: 工作管理、客户服务、收入统计

### 组件化开发
- 通用组件库 (`components/`) 提供一致的UI体验
- 各端独立组件目录，便于维护和扩展
- 响应式设计，支持多设备访问

### 实时通信系统
- **聊天管理器 (chat-manager.js)**: 核心通信模块
  - WebSocket实时消息收发
  - 多窗口聊天管理
  - 消息历史记录
  - 在线状态监控
  - 消息搜索功能

### 文件组织
- 按用户角色分离功能模块
- 共享资源统一管理
- 清晰的目录结构，便于开发维护

## 📚 文档

所有项目文档都在 `docs/` 目录中：
- 项目分析报告
- 数据库迁移指南
- MySQL配置说明
- 项目结构说明

### 前端文档
- **web前端结构.md**: 详细的前端架构说明，包含各端功能描述、组件说明和开发指南

## 🤝 贡献

欢迎提交Issue和Pull Request来改进项目！

## 📄 许可证

本项目采用MIT许可证。
