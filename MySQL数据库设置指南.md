# MySQL数据库设置指南

## 1. 安装MySQL

### Windows系统
1. 下载MySQL Community Server: https://dev.mysql.com/downloads/mysql/
2. 安装时设置root密码（建议使用强密码）
3. 确保MySQL服务正在运行

### 验证安装
```bash
mysql --version
```

## 2. 创建数据库

连接到MySQL：
```bash
mysql -u root -p
```

创建数据库和用户：
```sql
-- 创建数据库
CREATE DATABASE caregiving_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户（可选，也可以使用root用户）
CREATE USER 'caregiving_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON caregiving_db.* TO 'caregiving_user'@'localhost';
FLUSH PRIVILEGES;

-- 退出
EXIT;
```

## 3. 配置环境变量

创建 `.env` 文件（如果不存在）：
```env
# MySQL数据库配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USERNAME=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=caregiving_db

# 其他配置
FLASK_SECRET_KEY=your_flask_secret_key
APP_SECRET=your_app_secret
ADMIN_PASSWORD=your_admin_password
```

## 4. 安装Python依赖

确保已安装MySQL相关依赖：
```bash
pip install PyMySQL==1.1.0
pip install cryptography==41.0.7
```

## 5. 测试数据库连接

启动应用后，访问测试页面：
- 测试页面: http://127.0.0.1:8000/test-comprehensive-messaging.html
- 直接API测试: http://127.0.0.1:8000/api/test/database

## 6. 常见问题解决

### 问题1: 连接被拒绝
```
错误: Can't connect to MySQL server on 'localhost' (10061)
解决: 确保MySQL服务正在运行
```

### 问题2: 认证失败
```
错误: Access denied for user 'root'@'localhost'
解决: 检查用户名和密码是否正确
```

### 问题3: 数据库不存在
```
错误: Unknown database 'caregiving_db'
解决: 确保已创建数据库
```

### 问题4: 字符集问题
```
错误: Incorrect string value
解决: 确保数据库使用utf8mb4字符集
```

## 7. 数据库表结构

应用启动后会自动创建以下表：
- users (用户表)
- caregivers (护工表)
- businesses (企业表)
- jobs (工作表)
- chat_messages (聊天消息表)
- chat_conversations (聊天会话表)
- notifications (通知表)
- employment_contracts (雇佣合同表)
- reviews (评价表)

## 8. 性能优化建议

1. 为经常查询的字段添加索引
2. 定期优化表结构
3. 监控数据库性能
4. 定期备份数据

## 9. 备份和恢复

### 备份数据库
```bash
mysqldump -u root -p caregiving_db > backup.sql
```

### 恢复数据库
```bash
mysql -u root -p caregiving_db < backup.sql
```
