# 护工资源管理系统 - 项目分析文档

> **文档版本**: v1.0  
> **最后更新**: 2024年12月  
> **维护团队**: 护工资源管理系统开发团队  
> **适用对象**: 开发人员、产品经理、测试人员、新团队成员

---

## 📋 目录

- [1. 项目概览](#1-项目概览)
- [2. 快速开始](#2-快速开始)
- [3. 项目结构详解](#3-项目结构详解)
- [4. 开发指南](#4-开发指南)
- [5. 功能说明](#5-功能说明)
- [6. 部署运维](#6-部署运维)
- [7. 团队协作](#7-团队协作)
- [8. 附录](#8-附录)

---

## 1. 项目概览

### 1.1 系统介绍

**护工资源管理系统**是一个基于Web的护工服务平台，旨在连接需要护工服务的用户与专业的护工人员。系统提供用户注册、护工认证、服务预约、雇佣管理等核心功能。

**核心价值：**
- 🏠 为家庭提供可靠的护工服务
- 👨‍⚕️ 为护工提供就业机会和技能展示平台
- 🏢 为机构提供护工资源管理工具
- 📊 提供数据分析和业务洞察

### 1.2 技术栈

| 层级 | 技术 | 版本 | 说明 |
|------|------|------|------|
| **前端** | HTML5 + CSS3 + JavaScript | - | 原生Web技术，响应式设计 |
| **后端** | Python Flask | 2.3.3 | 轻量级Web框架 |
| **数据库** | SQLite | - | 轻量级关系型数据库 |
| **ORM** | SQLAlchemy | 3.0.5 | Python ORM框架 |
| **认证** | JWT + bcrypt | 2.8.0 + 4.0.1 | 安全认证和密码加密 |
| **部署** | Waitress | 2.1.2 | 生产级WSGI服务器 |

### 1.3 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端页面      │    │   API接口层     │    │   业务逻辑层    │
│  (HTML/CSS/JS) │◄──►│   (Flask API)   │◄──►│   (Services)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   数据访问层    │    │   数据存储层    │
                       │  (Models)      │◄──►│   (SQLite DB)   │
                       └─────────────────┘    └─────────────────┘
```

**架构特点：**
- **分层设计**: 清晰的职责分离，便于维护和扩展
- **模块化结构**: 按功能模块组织代码，降低耦合度
- **RESTful API**: 标准化的接口设计，支持前后端分离
- **安全认证**: JWT令牌机制，确保用户身份安全

---

## 2. 快速开始

### 2.1 环境要求

- **Python**: 3.8+ (推荐3.9+)
- **操作系统**: Windows 10/11, macOS, Linux
- **内存**: 最低2GB，推荐4GB+
- **磁盘空间**: 最低500MB

### 2.2 环境搭建

#### 2.2.1 安装Python
```bash
# 下载并安装Python 3.9+
# 验证安装
python --version
pip --version
```

#### 2.2.2 克隆项目
```bash
git clone <项目仓库地址>
cd CaregivingApp
```

#### 2.2.3 安装依赖
```bash
# 安装项目依赖
pip install -r requirements.txt

# 如果遇到网络问题，可以使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

### 2.3 项目启动

#### 2.3.1 开发环境启动
```bash
# 进入后端目录
cd back

# 启动Flask应用
python app.py

# 或者使用Flask命令
flask run --host=0.0.0.0 --port=8000
```

#### 2.3.2 访问系统
- **首页**: http://127.0.0.1:8000/
- **管理员登录**: http://127.0.0.1:8000/admin-login.html
- **用户注册**: http://127.0.0.1:8000/user-register.html

#### 2.3.3 默认账户
- **管理员**: admin / admin123
- **测试用户**: 需要先注册并通过审核

### 2.4 常见问题解决

| 问题 | 解决方案 |
|------|----------|
| `ModuleNotFoundError: No module named 'flask'` | 运行 `pip install -r requirements.txt` |
| 端口被占用 | 修改 `app.py` 中的端口号或关闭占用进程 |
| 数据库连接失败 | 检查 `database/` 目录是否存在，确保有写入权限 |

---

## 3. 项目结构详解

### 3.1 目录结构

```
CaregivingApp/
├── 📁 back/                    # 后端代码目录
│   ├── 📁 api/                # API接口模块
│   │   ├── __init__.py
│   │   ├── auth.py            # 认证相关API
│   │   └── admin.py           # 管理员相关API
│   ├── 📁 config/             # 配置模块
│   │   ├── __init__.py
│   │   └── settings.py        # 应用配置
│   ├── 📁 models/             # 数据模型
│   │   ├── __init__.py
│   │   ├── user.py            # 用户模型
│   │   ├── caregiver.py       # 护工模型
│   │   ├── service.py         # 服务类型模型
│   │   └── business.py        # 业务模型
│   ├── 📁 services/           # 业务逻辑服务
│   │   ├── __init__.py
│   │   └── user_service.py    # 用户服务
│   ├── 📁 utils/              # 工具函数
│   │   ├── __init__.py
│   │   ├── auth.py            # 认证工具
│   │   └── file_upload.py     # 文件上传工具
│   ├── 📁 web/                # 静态文件（临时）
│   ├── extensions.py          # Flask扩展初始化
│   └── app.py                 # 主应用入口
├── 📁 web/                    # 前端页面目录
│   ├── 📁 uploads/           # 文件上传目录
│   ├── index.html            # 首页（登录/注册）
│   ├── user-register.html    # 用户注册页面
│   ├── user-dashboard.html   # 用户仪表板
│   ├── admin-login.html      # 管理员登录页面
│   ├── admin-dashboard.html  # 管理员仪表板
│   ├── admin-users.html      # 用户管理页面
│   ├── admin-caregivers.html # 护工管理页面
│   ├── admin-job-analysis.html # 工作分析页面
│   ├── caregiver-register.html # 护工注册页面
│   ├── style.css             # 样式文件
│   └── script.js             # 通用脚本
├── 📁 database/              # 数据库相关
│   ├── database.py           # 数据库初始化
│   └── caregiving.db         # SQLite数据库文件
├── requirements.txt           # Python依赖包
└── PROJECT_ANALYSIS.md       # 本文档
```

### 3.2 核心模块功能

#### 3.2.1 配置模块 (`config/`)
- **功能**: 集中管理应用配置参数
- **核心文件**: `settings.py`
- **主要配置**: 数据库连接、文件上传、安全密钥等

#### 3.2.2 数据模型 (`models/`)
- **功能**: 定义数据库表结构和关系
- **核心模型**:
  - `User`: 用户信息管理
  - `Caregiver`: 护工信息管理
  - `ServiceType`: 服务类型定义
  - `Appointment`: 预约记录
  - `Employment`: 雇佣关系
  - `Message`: 消息通信

#### 3.2.3 API接口 (`api/`)
- **功能**: 提供RESTful API接口
- **主要接口**:
  - `auth.py`: 用户认证、注册、登录
  - `admin.py`: 管理员功能、审核、管理

#### 3.2.4 业务服务 (`services/`)
- **功能**: 封装业务逻辑，提供业务操作接口
- **核心服务**: `UserService` - 用户相关业务操作

#### 3.2.5 工具函数 (`utils/`)
- **功能**: 提供通用工具函数
- **主要工具**: 密码加密、JWT生成、文件上传等

### 3.3 文件命名规范

- **Python文件**: 小写字母 + 下划线 (snake_case)
- **HTML文件**: 小写字母 + 连字符 (kebab-case)
- **CSS/JS文件**: 小写字母 + 连字符 (kebab-case)
- **目录名**: 小写字母 + 下划线 (snake_case)

---

## 4. 开发指南

### 4.1 代码规范

#### 4.1.1 Python代码规范
- **PEP 8**: 遵循Python官方代码风格指南
- **命名约定**:
  - 类名: PascalCase (如 `UserService`)
  - 函数/变量: snake_case (如 `get_user_by_id`)
  - 常量: UPPER_CASE (如 `MAX_CONTENT_LENGTH`)
- **文档字符串**: 所有公共函数和类必须有docstring

#### 4.1.2 前端代码规范
- **HTML**: 语义化标签，合理的class命名
- **CSS**: BEM命名方法论，模块化样式
- **JavaScript**: ES6+语法，函数式编程风格

### 4.2 API接口规范

#### 4.2.1 接口命名
- **用户相关**: `/api/user/*`
- **护工相关**: `/api/caregiver/*`
- **管理员相关**: `/api/admin/*`
- **认证相关**: `/api/auth/*`

#### 4.2.2 响应格式
```json
{
  "success": true/false,
  "data": {...},
  "message": "操作结果描述"
}
```

#### 4.2.3 HTTP状态码
- `200`: 成功
- `400`: 请求参数错误
- `401`: 未授权
- `403`: 禁止访问
- `404`: 资源不存在
- `500`: 服务器内部错误

### 4.3 数据库设计

#### 4.3.1 核心表结构

**用户表 (user)**
```sql
CREATE TABLE user (
    id INTEGER PRIMARY KEY,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    name VARCHAR(100),
    phone VARCHAR(20),
    id_file VARCHAR(200),
    is_approved BOOLEAN DEFAULT FALSE,
    created_at DATETIME,
    approved_at DATETIME
);
```

**护工表 (caregiver)**
```sql
CREATE TABLE caregiver (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    id_file VARCHAR(200) NOT NULL,
    cert_file VARCHAR(200) NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    is_approved BOOLEAN DEFAULT FALSE,
    created_at DATETIME,
    approved_at DATETIME
);
```

**预约表 (appointment)**
```sql
CREATE TABLE appointment (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    caregiver_id INTEGER NOT NULL,
    service_type VARCHAR(50) NOT NULL,
    date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    status VARCHAR(20),
    created_at DATETIME,
    FOREIGN KEY(user_id) REFERENCES user(id),
    FOREIGN KEY(caregiver_id) REFERENCES caregiver(id)
);
```

#### 4.3.2 数据库操作
- **初始化**: 使用 `database/database.py` 中的 `init_database()` 函数
- **迁移**: 当前使用 `db.create_all()` 自动创建表结构
- **备份**: 定期备份 `caregiving.db` 文件

### 4.4 安全规范

#### 4.4.1 密码安全
- 使用bcrypt进行密码哈希
- 密码最小长度6位
- 不在日志中记录密码信息

#### 4.4.2 认证安全
- JWT令牌有效期2小时
- 敏感操作需要验证用户身份
- 管理员功能需要特殊权限验证

#### 4.4.3 文件上传安全
- 限制文件类型 (png, jpg, jpeg, gif, pdf)
- 限制文件大小 (最大16MB)
- 文件存储在安全的uploads目录

---

## 5. 功能说明

### 5.1 用户角色定义

#### 5.1.1 普通用户 (User)
**功能权限:**
- ✅ 注册账户
- ✅ 登录系统
- ✅ 查看护工信息
- ✅ 预约护工服务
- ✅ 管理个人预约
- ✅ 查看雇佣记录
- ✅ 发送/接收消息
- ❌ 审核护工
- ❌ 管理系统

**主要页面:**
- `index.html` - 首页登录
- `user-register.html` - 用户注册
- `user-dashboard.html` - 用户仪表板

#### 5.1.2 护工 (Caregiver)
**功能权限:**
- ✅ 注册护工账户
- ✅ 上传身份证明和证书
- ✅ 设置服务类型
- ✅ 查看预约请求
- ✅ 管理工作时间
- ✅ 接收服务评价
- ❌ 审核用户
- ❌ 管理系统

**主要页面:**
- `caregiver-register.html` - 护工注册

#### 5.1.3 管理员 (Admin)
**功能权限:**
- ✅ 登录管理后台
- ✅ 审核用户注册
- ✅ 审核护工申请
- ✅ 管理所有用户
- ✅ 查看系统统计
- ✅ 分析业务数据
- ✅ 系统配置管理

**主要页面:**
- `admin-login.html` - 管理员登录
- `admin-dashboard.html` - 管理仪表板
- `admin-users.html` - 用户管理
- `admin-caregivers.html` - 护工管理
- `admin-job-analysis.html` - 工作分析

### 5.2 核心业务流程

#### 5.2.1 用户注册流程
```
1. 用户填写注册信息 → 2. 提交注册申请 → 3. 等待管理员审核 → 4. 审核通过后可以登录
```

#### 5.2.2 护工认证流程
```
1. 护工填写申请信息 → 2. 上传身份证明和证书 → 3. 等待管理员审核 → 4. 审核通过后提供服务
```

#### 5.2.3 服务预约流程
```
1. 用户选择护工 → 2. 选择服务类型和时间 → 3. 提交预约请求 → 4. 护工确认预约 → 5. 服务完成
```

#### 5.2.4 雇佣管理流程
```
1. 用户发起雇佣请求 → 2. 护工确认雇佣条件 → 3. 建立雇佣关系 → 4. 服务执行和结算
```

### 5.3 页面功能详解

#### 5.3.1 首页 (`index.html`)
- **功能**: 统一的登录入口
- **特色**: 支持用户和护工两种角色登录
- **设计**: 响应式设计，移动端友好

#### 5.3.2 用户仪表板 (`user-dashboard.html`)
- **功能**: 用户个人中心
- **模块**: 统计信息、预约管理、雇佣记录、消息中心
- **交互**: 实时数据更新，动态加载内容

#### 5.3.3 管理员仪表板 (`admin-dashboard.html`)
- **功能**: 系统概览和管理入口
- **数据**: 用户统计、护工统计、系统状态
- **操作**: 快速审核、系统监控

---

## 6. 部署运维

### 6.1 开发环境部署

#### 6.1.1 本地开发
```bash
# 克隆项目
git clone <仓库地址>
cd CaregivingApp

# 安装依赖
pip install -r requirements.txt

# 启动应用
cd back
python app.py
```

#### 6.1.2 开发工具配置
- **VS Code**: 推荐使用Python扩展
- **PyCharm**: 专业版内置数据库工具
- **数据库工具**: 推荐使用DB Browser for SQLite

### 6.2 生产环境部署

#### 6.2.1 服务器要求
- **操作系统**: Ubuntu 20.04+ / CentOS 7+
- **Python**: 3.9+
- **内存**: 4GB+
- **磁盘**: 20GB+
- **网络**: 公网IP，开放80/443端口

#### 6.2.2 部署步骤
```bash
# 1. 安装系统依赖
sudo apt update
sudo apt install python3 python3-pip nginx

# 2. 部署应用
cd /var/www/
git clone <仓库地址>
cd CaregivingApp

# 3. 安装Python依赖
pip3 install -r requirements.txt

# 4. 配置Nginx
sudo cp nginx.conf /etc/nginx/sites-available/caregiving
sudo ln -s /etc/nginx/sites-available/caregiving /etc/nginx/sites-enabled/

# 5. 启动应用
cd back
nohup python3 app.py > app.log 2>&1 &

# 6. 重启Nginx
sudo systemctl restart nginx
```

#### 6.2.3 环境变量配置
```bash
# 创建环境变量文件
cat > .env << EOF
FLASK_ENV=production
FLASK_SECRET_KEY=your_production_secret_key
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password
EOF
```

### 6.3 监控和维护

#### 6.3.1 日志管理
- **应用日志**: `back/app.log`
- **错误日志**: 使用Python logging模块
- **访问日志**: Nginx access.log

#### 6.3.2 性能监控
- **数据库性能**: 监控SQL查询执行时间
- **应用性能**: 监控API响应时间
- **系统资源**: CPU、内存、磁盘使用率

#### 6.3.3 备份策略
- **数据库备份**: 每日备份 `caregiving.db`
- **代码备份**: 使用Git版本控制
- **文件备份**: 定期备份uploads目录

---

## 7. 团队协作

### 7.1 Git工作流程

#### 7.1.1 分支策略
```
main (主分支)
├── develop (开发分支)
├── feature/user-management (功能分支)
├── feature/caregiver-system (功能分支)
└── hotfix/critical-bug (热修复分支)
```

#### 7.1.2 提交规范
```
feat: 添加新功能
fix: 修复bug
docs: 更新文档
style: 代码格式调整
refactor: 代码重构
test: 添加测试
chore: 构建过程或辅助工具的变动
```

**提交示例:**
```bash
git commit -m "feat: 添加用户注册功能"
git commit -m "fix: 修复登录验证bug"
git commit -m "docs: 更新API文档"
```

#### 7.1.3 代码审查流程
1. **创建功能分支**: `git checkout -b feature/new-feature`
2. **开发功能**: 在分支上开发新功能
3. **提交代码**: `git push origin feature/new-feature`
4. **创建PR**: 在GitHub/GitLab上创建Pull Request
5. **代码审查**: 团队成员审查代码
6. **合并代码**: 审查通过后合并到develop分支

### 7.2 开发规范

#### 7.2.1 代码审查要点
- **功能完整性**: 功能是否按需求实现
- **代码质量**: 代码是否清晰、可维护
- **安全性**: 是否存在安全漏洞
- **性能**: 是否有性能问题
- **测试覆盖**: 是否有足够的测试

#### 7.2.2 测试要求
- **单元测试**: 核心业务逻辑必须有单元测试
- **集成测试**: API接口必须有集成测试
- **前端测试**: 关键页面功能必须有测试

#### 7.2.3 文档要求
- **代码注释**: 复杂逻辑必须有详细注释
- **API文档**: 新增接口必须更新文档
- **变更日志**: 重要变更必须记录在CHANGELOG.md

### 7.3 发布流程

#### 7.3.1 版本管理
- **版本号**: 遵循语义化版本 (Semantic Versioning)
- **格式**: MAJOR.MINOR.PATCH (如 1.2.3)
- **主版本**: 不兼容的API修改
- **次版本**: 向下兼容的功能性新增
- **修订版本**: 向下兼容的问题修正

#### 7.3.2 发布步骤
1. **功能冻结**: 在develop分支上冻结新功能开发
2. **测试验证**: 进行全面测试
3. **创建发布分支**: `git checkout -b release/v1.2.0`
4. **版本号更新**: 更新版本号和文档
5. **合并到main**: 测试通过后合并到main分支
6. **创建标签**: `git tag -a v1.2.0 -m "Release version 1.2.0"`
7. **部署生产**: 部署到生产环境

---

## 8. 附录

### 8.1 常用命令

#### 8.1.1 开发命令
```bash
# 启动应用
python app.py

# 安装依赖
pip install -r requirements.txt

# 数据库初始化
python -c "from database.database import init_database; init_database()"

# 运行测试
python -m pytest tests/
```

#### 8.1.2 Git命令
```bash
# 查看状态
git status

# 查看分支
git branch -a

# 切换分支
git checkout develop

# 合并分支
git merge feature/new-feature

# 查看提交历史
git log --oneline
```

#### 8.1.3 数据库命令
```sql
-- 查看所有表
.tables

-- 查看表结构
.schema user

-- 查看数据
SELECT * FROM user LIMIT 10;

-- 备份数据库
.backup backup.db
```

### 8.2 常见问题FAQ

#### 8.2.1 开发环境问题
**Q: Flask应用启动失败？**
A: 检查Python版本、依赖安装、端口占用情况

**Q: 数据库连接失败？**
A: 检查数据库文件路径、文件权限、SQLAlchemy配置

**Q: 前端页面无法访问？**
A: 检查web目录路径、静态文件配置、路由设置

#### 8.2.2 功能问题
**Q: 用户注册后无法登录？**
A: 检查用户审核状态、密码验证逻辑

**Q: 文件上传失败？**
A: 检查文件大小限制、文件类型、上传目录权限

**Q: API接口返回错误？**
A: 检查请求参数、认证状态、数据库连接

### 8.3 联系信息

- **项目负责人**: [待填写]
- **技术负责人**: [待填写]
- **产品负责人**: [待填写]
- **邮箱**: [待填写]
- **项目仓库**: [待填写]

### 8.4 更新日志

| 版本 | 日期 | 更新内容 | 更新人 |
|------|------|----------|--------|
| v1.0 | 2024-12 | 初始版本，包含基础功能 | 开发团队 |

---

## 📝 文档维护

本文档由护工资源管理系统开发团队维护，如有问题或建议，请通过以下方式联系：

1. **提交Issue**: 在项目仓库中创建Issue
2. **邮件反馈**: 发送邮件到团队邮箱
3. **团队会议**: 在定期团队会议中讨论

**最后更新时间**: 2024年12月  
**文档状态**: 活跃维护中

---

*感谢您阅读本项目的分析文档！希望这份文档能帮助您快速了解项目并顺利加入我们的开发团队。* 