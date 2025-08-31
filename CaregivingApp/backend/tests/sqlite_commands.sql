-- SQLite数据库操作命令集合
-- 可以在SQLite命令行工具中使用这些命令

-- 1. 查看所有表
.tables

-- 2. 查看表结构
.schema user
.schema caregiver
.schema service_type

-- 3. 查看用户表数据
SELECT * FROM user LIMIT 10;

-- 4. 查看护工表数据
SELECT * FROM caregiver LIMIT 10;

-- 5. 添加新用户
INSERT INTO user (name, phone, email, password_hash, is_approved, created_at) 
VALUES ('张三', '13800138001', 'zhangsan@example.com', 'hashed_password_123', 0, datetime('now'));

-- 6. 添加新护工
INSERT INTO caregiver (name, phone, password_hash, id_file, cert_file, is_approved, created_at) 
VALUES ('李护工', '13900139001', 'hashed_password_456', 'id_card_001.jpg', 'cert_001.jpg', 0, datetime('now'));

-- 7. 搜索用户
SELECT id, name, phone, email, is_approved, created_at 
FROM user 
WHERE name LIKE '%张%' OR phone LIKE '%138%';

-- 8. 更新用户审核状态
UPDATE user SET is_approved = 1, approved_at = datetime('now') WHERE id = 1;

-- 9. 查看表的所有列
PRAGMA table_info(user);
PRAGMA table_info(caregiver);

-- 10. 统计用户数量
SELECT COUNT(*) as total_users FROM user;
SELECT COUNT(*) as approved_users FROM user WHERE is_approved = 1;
SELECT COUNT(*) as pending_users FROM user WHERE is_approved = 0;

-- 11. 按创建时间排序查看用户
SELECT id, name, phone, created_at, is_approved 
FROM user 
ORDER BY created_at DESC;

-- 12. 查看特定手机号的用户
SELECT * FROM user WHERE phone = '13800138001';

-- 13. 删除测试数据（谨慎使用）
-- DELETE FROM user WHERE id = 1;

-- 14. 备份数据库
-- .backup backup_caregiving.db

-- 15. 导出数据为CSV格式
.mode csv
.headers on
.output users.csv
SELECT * FROM user;
.output stdout

-- 16. 设置输出格式
.mode column
.headers on

-- 17. 查看数据库文件信息
PRAGMA database_list;

-- 18. 优化数据库
VACUUM;
ANALYZE; 