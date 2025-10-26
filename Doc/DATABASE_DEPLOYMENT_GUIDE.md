# 心情烘焙坊 - 数据库部署指南

## 📋 目录

- [快速开始](#快速开始)
- [环境要求](#环境要求)
- [部署步骤](#部署步骤)
- [验证部署](#验证部署)
- [常见问题](#常见问题)
- [表结构说明](#表结构说明)

---

## 🚀 快速开始

### 一键部署

```bash
# Windows
mysql -u root -p < july_server\sql\july_complete_final.sql

# Linux/Mac
mysql -u root -p < july_server/sql/july_complete_final.sql
```

输入MySQL密码后,等待约10-30秒即可完成部署。

---

## 💻 环境要求

- **MySQL**: 8.0+ (推荐 8.0.26+)
- **字符集**: UTF-8 (utf8mb4)
- **存储引擎**: InnoDB
- **操作系统**: Windows / Linux / macOS

---

## 📖 部署步骤

### 步骤1: 准备工作

确保MySQL服务正在运行:

```bash
# Windows
net start MySQL80

# Linux
sudo systemctl start mysql

# macOS
brew services start mysql
```

### 步骤2: 创建数据库

如果数据库不存在,SQL脚本会自动创建。

如果需要重新部署(删除旧数据),请先删除数据库:

```sql
DROP DATABASE IF EXISTS july;
```

### 步骤3: 执行SQL脚本

#### 方法1: 命令行执行(推荐)

```bash
cd D:\SE\bakery
mysql -u root -p < july_server\sql\july_complete_final.sql
```

#### 方法2: MySQL客户端执行

```sql
USE july;
SOURCE /path/to/july_complete_final.sql;
```

#### 方法3: 使用MySQL Workbench

1. 打开MySQL Workbench
2. 连接到数据库
3. File → Open SQL Script → 选择 `july_complete_final.sql`
4. 点击 ⚡ Execute 按钮

### 步骤4: 验证部署

执行以下SQL验证:

```sql
USE july;

-- 检查表数量(应该有16个表)
SELECT COUNT(*) AS table_count 
FROM information_schema.TABLES 
WHERE TABLE_SCHEMA = 'july';

-- 检查字符集(应该全部是 utf8mb4_general_ci)
SELECT DISTINCT TABLE_COLLATION 
FROM information_schema.TABLES 
WHERE TABLE_SCHEMA = 'july';

-- 检查情绪标签数据(应该有10条)
SELECT COUNT(*) AS emotion_label_count 
FROM emotion_label;

-- 检查用户数据(应该至少有5个用户)
SELECT COUNT(*) AS user_count 
FROM user;
```

---

## ✅ 验证部署

### 预期结果

执行SQL脚本后,应该看到:

```
========================================
  数据库初始化完成！
  Database: july
  Charset: utf8mb4_general_ci
  Version: v2.0 Final
========================================

已创建的表:
+-------------------+------------------------+
| 表名              | 说明                   |
+-------------------+------------------------+
| alembic_version   |                        |
| chat              | 聊天表                 |
| comment           | 评论表                 |
| diary             | 日记表                 |
| emotion_label     | 情绪标签表             |
| emotion_stat      | 情绪统计表             |
| following         | 关注表                 |
| hole              | 树洞表                 |
| label             | 话题标签表             |
| message           | 消息表                 |
| soul_push         | 心灵鸡汤推送记录表     |
| star              | 收藏表                 |
| topic             | 话题表                 |
| topic_label_rel   | 话题标签关联表         |
| user              | 用户表                 |
| video             | 视频表                 |
+-------------------+------------------------+

数据库部署完成，可以启动服务器了！
```

---

## 🔧 常见问题

### 问题1: "Access denied for user 'root'@'localhost'"

**解决方案**: 检查MySQL用户名和密码

```bash
mysql -u root -p
# 输入正确的密码
```

### 问题2: "Unknown database 'july'"

**解决方案**: SQL脚本会自动创建数据库,无需手动创建。如果仍然报错,请手动执行:

```sql
CREATE DATABASE july DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
```

### 问题3: 字符集冲突错误

**解决方案**: 确保使用 `july_complete_final.sql`,该脚本已统一所有表的字符集为 `utf8mb4_general_ci`。

### 问题4: "Table 'xxx' already exists"

**解决方案**: SQL脚本会先删除旧表再创建。如果报错,可以手动删除数据库后重新执行:

```sql
DROP DATABASE IF EXISTS july;
```

### 问题5: 触发器相关问题

**说明**: 为避免开发环境字符集冲突,触发器已在SQL脚本中禁用(注释掉)。

**生产环境启用**: 如需启用自动情绪统计功能,请参考SQL脚本第19部分的注释,手动创建触发器。

---

## 📊 表结构说明

### 核心表

| 表名 | 说明 | 新增/修改 |
|------|------|----------|
| `user` | 用户信息 | 原有 |
| `topic` | 话题/帖子 | **扩展**(添加`emotion_label_id`) |
| `comment` | 评论 | 原有 |
| `label` | 话题标签 | 原有 |
| `star` | 收藏/互动 | **扩展**(添加`interaction_type`) |

### 新增表(心情烘焙坊功能)

| 表名 | 说明 | 用途 |
|------|------|------|
| `emotion_label` | 情绪标签 | 存储系统/自定义情绪标签 |
| `diary` | 日记 | 用户私密日记记录 |
| `soul_push` | 心灵鸡汤推送 | LLM生成的温暖句子推送记录 |
| `emotion_stat` | 情绪统计 | 用户情绪波动统计(用于图表) |

### 辅助表

| 表名 | 说明 |
|------|------|
| `message` | 系统消息通知 |
| `following` | 用户关注关系 |
| `video` | 视频资源 |
| `hole` | 树洞功能 |
| `chat` | 聊天记录 |

### 视图和存储过程

- **视图**: `v_user_emotion_trend` - 用户情绪趋势(最近30天)
- **存储过程**: `sp_update_emotion_stat` - 更新情绪统计

---

## 📝 初始数据

### 用户数据

脚本包含5个测试用户:
- `d8e5ae1bc666459e856e0e05d6bbdcbf` - 开发测试账号
- 其他4个为示例数据

### 情绪标签

脚本包含10个系统情绪标签:
- 😊 开心 (#FFD700)
- 😌 平静 (#87CEEB)
- 😢 难过 (#4682B4)
- 😰 焦虑 (#FFA500)
- 😠 愤怒 (#DC143C)
- 🤩 兴奋 (#FF69B4)
- 😴 疲惫 (#808080)
- 🥺 感动 (#FFB6C1)
- 😔 孤独 (#696969)
- 🤗 期待 (#32CD32)

---

## 🔐 安全建议

1. **生产环境**: 修改默认密码和用户信息
2. **备份**: 定期备份数据库
3. **权限**: 为应用创建独立的数据库用户,不使用root账户
4. **SSL**: 生产环境启用MySQL SSL连接

### 创建应用专用用户

```sql
CREATE USER 'july_app'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON july.* TO 'july_app'@'localhost';
FLUSH PRIVILEGES;
```

---

## 🚀 下一步

数据库部署完成后:

1. **配置后端**: 修改 `july_server/.env` 文件,配置数据库连接
2. **启动后端**: 运行 `python starter_no_socketio.py`
3. **配置前端**: 修改 `july_client/config/api.js`
4. **启动前端**: 在微信开发者工具中打开项目

---

## 📞 支持

如有问题,请参考:
- [项目README](../README.md)
- [开发日志](../log.md)
- [自定义指南](../CUSTOMIZATION_GUIDE.md)

---

**版本**: v2.0 Final  
**更新时间**: 2025-10-26  
**作者**: Mood Bakery Team

