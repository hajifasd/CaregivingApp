# 护工资源管理系统 - 数据库管理文件夹

## 📁 文件夹说明

本文件夹包含护工资源管理系统的所有数据库相关文件，包括迁移脚本、管理工具和文档。

## 📋 文件列表

### 🔧 核心脚本
| 文件名 | 功能 | 说明 |
|--------|------|------|
| `migrate_to_mysql.py` | SQLite 到 MySQL 迁移 | 主要的数据迁移脚本 |
| `import_data_to_mysql.py` | 数据导入 | 将备份数据导入到 MySQL |
| `manage_database.py` | 数据库管理 | 日常数据库管理工具 |

### 📄 文档文件
| 文件名 | 功能 | 说明 |
|--------|------|------|
| `数据库迁移操作指南.md` | 迁移指南 | 完整的迁移操作文档 |
| `README.md` | 说明文档 | 本文件，文件夹说明 |

### 💾 数据文件
| 文件名 | 功能 | 说明 |
|--------|------|------|
| `sqlite_backup_20250901_231950.json` | SQLite 备份 | 原始 SQLite 数据备份 |

## 🚀 快速使用

### 1. 数据库连接测试
```bash
cd database
python manage_database.py test
```

### 2. 创建表结构
```bash
python manage_database.py create
```

### 3. 检查数据库状态
```bash
python manage_database.py status
```

### 4. 备份数据
```bash
python manage_database.py backup
```

### 5. 重置数据库（谨慎使用）
```bash
python manage_database.py reset
```

## 📦 迁移流程

### 完整迁移步骤
1. **测试连接**：`python manage_database.py test`
2. **创建表结构**：`python manage_database.py create`
3. **导入数据**：`python import_data_to_mysql.py`
4. **验证结果**：`python manage_database.py status`

### 一键迁移（如果已有备份）
```bash
# 1. 创建表结构
python manage_database.py create

# 2. 导入数据
python import_data_to_mysql.py
```

## ⚠️ 注意事项

1. **备份重要**：在进行任何操作前，建议先备份数据
2. **权限要求**：确保有 MySQL root 用户权限
3. **服务状态**：确保 MySQL 服务正在运行
4. **环境配置**：确保 `.env` 文件配置正确

## 🔧 故障排除

### 常见问题
1. **连接失败**：检查 MySQL 服务状态和密码
2. **权限错误**：确认用户有足够权限
3. **表已存在**：使用 `reset` 功能清空数据

### 获取帮助
- 查看 `数据库迁移操作指南.md` 获取详细说明
- 检查应用日志获取错误信息
- 联系技术团队获取支持

## 📞 技术支持

- **技术团队**：护工资源管理系统开发团队
- **文档版本**：1.0
- **最后更新**：2024年

---

*数据库管理文件夹说明*
