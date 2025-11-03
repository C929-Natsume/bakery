# 心情烘焙坊 - 云托管部署完整指南

本指南提供**微信云托管**部署方案，轻松将后端部署到云端。

---

## 📋 方案概述

**微信云托管 + 腾讯云MySQL + 小程序云存储**

- ✅ 后端：微信云托管（容器化）
- ✅ 数据库：腾讯云MySQL CDB
- ✅ 图片存储：小程序云存储
- ✅ 无需自建服务器，开箱即用

---

## 🎯 前置准备

1. ✅ 微信小程序开发者账号
2. ✅ 已开通云托管服务
3. ✅ 腾讯云账号（用于MySQL/CDN）
4. ✅ 已配置云开发环境（用于图片存储）

---

## 📦 第一步：准备代码

### **1.1 优化Dockerfile**

已创建优化版的 `Dockerfile`:

```dockerfile
FROM python:3.7-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 复制应用代码
COPY . .

# 创建日志目录
RUN mkdir -p log

# 启动命令（不使用SocketIO）
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:80", "starter_no_socketio:app", "--timeout", "120"]
```

**关键改动**:
- ✅ 使用`starter_no_socketio.py`避免SSL问题
- ✅ 监听`80`端口（云托管要求）
- ✅ 增加超时时间
- ✅ 轻量级slim镜像

### **1.2 创建`.dockerignore`**

```dockerignore
__pycache__
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info
dist
build
.git
.gitignore
README.md
log/*
.env
.venv
venv/
.env_template
```

### **1.3 配置环境变量**

在云托管控制台配置以下环境变量：

```env
# Flask配置
FLASK_ENV=production
SECRET_KEY=your-secret-key-here

# MySQL配置（腾讯云CDB）
MYSQL_HOST=your-mysql-host.cdb.myqcloud.com
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your-mysql-password
MYSQL_DB=july

# Redis配置（云托管Redis）
REDIS_HOST=your-redis-host.redis.tencent-cloud.com
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password

# 微信配置
WEIXIN_APPID=your-appid
WEIXIN_SECRET=your-secret
```

---

## 🚀 第二步：部署到云托管

### **2.1 推送代码到Git仓库**

```bash
# 在项目根目录执行
git add .
git commit -m "prepare for deployment"
git push origin main
```

### **2.2 在云托管控制台创建服务**

1. 打开[微信云托管控制台](https://console.cloud.tencent.com/tcb/env)
2. 点击**创建服务**
3. 配置服务：
   - **服务名称**: `mood-bakery-api`
   - **代码仓库**: 选择你的Git仓库
   - **构建配置**: 自动检测（Dockerfile）
   - **监听端口**: `80`
   - **流量配置**: 自动扩容

### **2.3 配置数据库**

#### **创建腾讯云MySQL实例**

1. 登录[腾讯云控制台](https://console.cloud.tencent.com/cdb)
2. 创建MySQL实例
3. 创建数据库：
   ```sql
   CREATE DATABASE july DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_general_ci;
   ```
4. 导入数据：
   ```bash
   mysql -h your-mysql-host -u root -p july < july_server/sql/july_complete_final.sql
   ```

#### **配置云托管Redis**

1. 在云托管控制台购买Redis实例
2. 记录连接地址和密码

### **2.4 配置域名**

在云托管控制台：
1. 点击**域名管理**
2. 添加自定义域名：`https://api.yourdomain.com`
3. 系统自动配置HTTPS证书

---

## 🔧 第三步：配置小程序

### **3.1 配置合法域名**

在小程序后台 > 开发 > 开发管理 > 开发设置：
- ✅ **request合法域名**: `https://api.yourdomain.com`
- ✅ **uploadFile合法域名**: `https://api.yourdomain.com`

### **3.2 更新前端API配置**

修改 `july_client/config/api.js`:

```javascript
const baseAPI = 'https://api.yourdomain.com/v2' // 👈 改成你的域名
const socketAPI = 'wss://api.yourdomain.com/ws'  // 👈 WebSocket（如果启用）
```

### **3.3 配置云存储**

按照 `CLOUD_STORAGE_SETUP.md` 配置微信云存储。

---

## ✅ 第四步：验证部署

### **健康检查**

访问以下接口验证部署成功：

```bash
# 检查API是否正常
curl https://api.yourdomain.com/v2/emotion/label

# 应该返回：
{
  "code": 0,
  "msg": "成功",
  "data": {
    "popular_labels": [...],
    "system_labels": [...]
  }
}
```

### **功能测试**

1. ✅ 打开小程序
2. ✅ 测试发帖功能（带图片）
3. ✅ 测试情绪标签功能
4. ✅ 测试日记功能

---

## 📊 成本估算

### **云托管**

| 资源 | 规格 | 价格 |
|------|------|------|
| **云托管** | 0.25核 0.5GB | ¥0.06/小时 ≈ ¥45/月 |
| **MySQL** | 1核 1GB | ¥60/月 |
| **Redis** | 256MB | ¥25/月 |
| **云存储** | 5GB | **免费** ✅ |
| **CDN流量** | 10GB/月 | **免费** ✅ |

**总计**: 约 **¥130/月**

---

## 🔍 监控和日志

### **查看日志**

在云托管控制台：
- **实时日志**: 查看实时输出
- **日志分析**: 分析错误日志
- **性能监控**: CPU、内存、请求量

### **告警配置**

1. 进入**云监控**
2. 配置告警规则：
   - CPU使用率 > 80%
   - 内存使用率 > 80%
   - 5xx错误率 > 5%

---

## 🆘 常见问题

### **Q1: 部署后无法访问？**

**A**: 检查以下几点：
1. 服务是否正常启动（查看日志）
2. 监听端口是否为80
3. 域名是否已正确配置
4. 安全组规则是否开放80端口

### **Q2: 数据库连接失败？**

**A**: 
1. 检查MySQL白名单，添加云托管IP段
2. 确认数据库用户名密码正确
3. 检查VPC网络配置

### **Q3: 图片上传失败？**

**A**:
1. 确认云开发环境已正确初始化
2. 检查云存储权限设置
3. 查看前端控制台错误信息

---

## 📝 部署清单

- [ ] 代码推送至Git仓库
- [ ] 在云托管创建服务
- [ ] 配置环境变量
- [ ] 创建MySQL数据库并导入数据
- [ ] 配置Redis实例
- [ ] 绑定域名并配置HTTPS
- [ ] 更新小程序合法域名
- [ ] 修改前端API配置
- [ ] 配置云存储
- [ ] 测试所有功能
- [ ] 配置监控告警

---

## 🎉 完成！

恭喜！你的心情烘焙坊已经成功部署到云托管，可以正式提供服务了！

**相关文档**:
- `CLOUD_STORAGE_SETUP.md` - 云存储配置
- `CLOUD_STORAGE_QUICKSTART.md` - 快速启动
- `DATABASE_DEPLOYMENT_GUIDE.md` - 数据库部署

