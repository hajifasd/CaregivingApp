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
│   ├── 📁 uploads/           # 文件上传目录
│   ├── *.html                # HTML页面文件
│   ├── style.css             # 样式文件
│   └── script.js             # JavaScript文件
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

### 5. 访问应用
- 主页: http://localhost:5000/
- 用户注册: http://localhost:5000/user-register.html
- 护工注册: http://localhost:5000/caregiver-register.html

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
- 📊 数据分析 (工作数据统计)
- 📁 文件上传 (身份证、证书等)

## 📝 技术栈

- **后端**: Flask + SQLAlchemy + PyMySQL
- **前端**: HTML5 + CSS3 + JavaScript
- **数据库**: MySQL 8.0
- **认证**: JWT + bcrypt
- **文件处理**: 支持图片和PDF上传

## 📚 文档

所有项目文档都在 `docs/` 目录中：
- 项目分析报告
- 数据库迁移指南
- MySQL配置说明
- 项目结构说明

## 🤝 贡献

欢迎提交Issue和Pull Request来改进项目！

## �� 许可证

本项目采用MIT许可证。
