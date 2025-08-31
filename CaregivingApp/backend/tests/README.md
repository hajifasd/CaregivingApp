# 测试文件夹

这个文件夹包含了护工管理系统的各种测试工具和脚本。

## 文件说明

### 1. 数据库管理工具
- **`db_manager.py`** - 交互式数据库管理工具
  - 功能：查看、添加、搜索、审核用户和护工
  - 使用方法：`python db_manager.py`

### 2. 快速查看工具
- **`quick_view.py`** - 快速数据库概览工具
  - 功能：显示数据库表结构、记录数量、示例数据
  - 使用方法：`python quick_view.py`

### 3. 用户登录测试
- **`test_user_login.py`** - 用户登录功能测试
  - 功能：创建测试用户、测试登录验证
  - 使用方法：`python test_user_login.py`

### 4. 测试用户创建
- **`create_test_user.py`** - 直接创建测试用户
  - 功能：在数据库中直接创建已审核的测试用户
  - 使用方法：`python create_test_user.py`

### 5. 测试护工创建
- **`create_test_caregiver.py`** - 直接创建测试护工
  - 功能：在数据库中直接创建已审核的测试护工
  - 使用方法：`python create_test_caregiver.py`

### 6. 综合测试账号创建
- **`create_all_test_accounts.py`** - 创建所有测试账号
  - 功能：一次性创建用户、护工和服务类型
  - 使用方法：`python create_all_test_accounts.py`

### 7. 测试运行器
- **`run_tests.py`** - 测试套件运行器
  - 功能：一键运行所有测试脚本
  - 使用方法：`python run_tests.py`

### 8. SQL命令参考
- **`sqlite_commands.sql`** - SQLite命令参考文件
  - 功能：提供常用的SQLite操作命令
  - 使用方法：参考文件内容

## 测试账号

### 用户端测试账号
- **账号：** `13800138000`
- **密码：** `123456`
- **状态：** 已审核通过

### 管理员测试账号
- **账号：** `admin`
- **密码：** `admin123`

### 护工测试账号
- **账号：** `13800138001`
- **密码：** `123456`
- **状态：** 已审核通过

## 使用说明

### 快速开始
1. **一键创建所有测试账号**：
   ```bash
   cd tests
   python create_all_test_accounts.py
   ```

2. **运行完整测试套件**：
   ```bash
   python run_tests.py
   ```

### 单独使用
1. **创建测试用户**：
   ```bash
   python create_test_user.py
   ```

2. **创建测试护工**：
   ```bash
   python create_test_caregiver.py
   ```

3. **测试用户登录**：
   ```bash
   python test_user_login.py
   ```

4. **管理数据库**：
   ```bash
   python db_manager.py
   ```

5. **查看数据库概览**：
   ```bash
   python quick_view.py
   ```

## 注意事项

- 所有测试文件都使用相对路径访问数据库
- 测试用户创建后会自动设置为已审核状态
- 请在生产环境中删除或禁用测试账号
- 测试文件仅供开发和调试使用 