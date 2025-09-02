# MySQL 数据库配置说明

## 1. 安装 MySQL 依赖

```bash
pip install -r requirements.txt
```

## 2. 创建 MySQL 数据库

在 MySQL 中创建数据库：

```sql
CREATE DATABASE caregiving_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## 3. 配置环境变量

创建 `.env` 文件（复制以下内容并修改为您的实际配置）：

```env
# MySQL 数据库配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USERNAME=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=caregiving_db

# 应用安全配置
APP_SECRET=your_app_secret_key
FLASK_SECRET_KEY=your_flask_secret_key

# 管理员配置
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
```

## 4. 启动应用

```bash
cd back
python app.py
```

## 5. 验证连接

应用启动时会自动创建数据库表，如果看到"数据库表创建完成"消息，说明连接成功。

## 故障排除

如果遇到连接问题，请检查：
1. MySQL 服务是否正在运行
2. 数据库用户是否有足够权限
3. 防火墙是否阻止了连接
4. 数据库名称是否正确
