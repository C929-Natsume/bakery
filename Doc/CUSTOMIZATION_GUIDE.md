# 项目定制化开发指南

## 📋 目录
1. [基础配置修改](#1-基础配置修改必须)
2. [品牌定制](#2-品牌定制)
3. [功能定制](#3-功能定制)
4. [数据库定制](#4-数据库定制)
5. [API定制](#5-api定制)
6. [UI定制](#6-ui定制)
7. [第三方服务配置](#7-第三方服务配置)

---

## 1. 基础配置修改（必须）

### 1.1 客户端基础配置

#### 📁 `july_client/app.json`
```json
{
  "window": {
    "navigationBarTitleText": "你的应用名称",  // 修改应用标题
    "navigationBarBackgroundColor": "#fff",    // 修改导航栏背景色
    "navigationBarTextStyle": "black"          // 修改导航栏文字颜色
  },
  "tabBar": {
    "color": "#8a8a8a",           // 修改Tab未选中颜色
    "selectedColor": "#337559",   // 修改Tab选中颜色（主题色）
    "list": [
      {
        "pagePath": "pages/topic/index",
        "text": "主页",           // 修改Tab文字
        "iconPath": "images/icon_tab/topic.png",
        "selectedIconPath": "images/icon_tab/topic_hl.png"
      }
      // ... 其他Tab配置
    ]
  }
}
```

#### 📁 `july_client/project.config.json`
```json
{
  "appid": "wx71dbe0db18ff0c4f",  // 修改为你的小程序AppID
  "projectname": "your_project"    // 修改项目名称
}
```

#### 📁 `july_client/app.js`
```javascript
App({
  globalData: {
    githubURI: 'YourGithub/your_project',  // 修改GitHub地址
    githubURL: 'https://github.com/YourGithub/your_project',
    likeAuthor: '',  // 修改赞赏码图片URL
    tokenExpires: 86400 * 27  // Token过期时间（可调整）
  }
})
```

#### 📁 `july_client/config/api.js`
```javascript
const baseAPI = 'http://your-domain.com/v2'  // 修改为你的服务器地址
const socketAPI = 'ws://your-domain.com/ws'  // 修改WebSocket地址
const ossDomain = 'https://your-oss-domain.com'  // 修改对象存储域名
```

#### 📁 `july_client/config/template.js`
```javascript
export default {
  messageTemplateId: 'your_message_template_id',  // 修改订阅消息模板ID
  reserveTemplateId: 'your_reserve_template_id'   // 修改预约订阅消息模板ID
}
```

### 1.2 服务端基础配置

#### 📁 `july_server/.env`（创建此文件）
```env
# 应用配置
APP_NAME=YOUR_APP_NAME
SECRET_KEY=your_secret_key_here

# 数据库配置
SQLALCHEMY_DATABASE_URI=mysql+cymysql://root:password@127.0.0.1:3306/your_db?charset=utf8mb4

# Redis配置
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# 微信小程序配置
MP_APP_ID=your_miniprogram_appid
MP_APP_SECRET=your_miniprogram_secret
COMMENT_TEMPLATE_ID=your_comment_template_id
RESERVE_HOLE_TEMPLATE_ID=your_reserve_template_id

# 七牛云配置（可选）
QINIU_ACCESS_KEY=your_qiniu_access_key
QINIU_SECRET_KEY=your_qiniu_secret_key
QINIU_BUCKET_URL=https://your-bucket.qiniucdn.com
QINIU_BUCKET_NAME=your_bucket_name

# Server酱配置（可选）
SERVER_CHAN_SEND_KEY=your_server_chan_key

# 腾讯位置服务配置（可选）
WEIXIN_LBS_KEY=your_weixin_lbs_key
```

#### 📁 `july_server/app/config/base.py`
```python
class BaseConfig(object):
    # 应用相关
    MAX_IMAGES_LENGTH = 9  # 最大图片数量（可调整）
    MAX_LABELS_LENGTH = 3  # 最大标签数量（可调整）
    VIDEO_REVIEW = False   # 是否开启视频审核
```

---

## 2. 品牌定制

### 2.1 修改应用名称和Logo

#### 客户端
- **应用名称**：`july_client/app.json` → `window.navigationBarTitleText`
- **Tab文字**：`july_client/app.json` → `tabBar.list[].text`
- **Tab图标**：替换 `july_client/images/icon_tab/` 下的图标文件

#### 服务端
- **数据库名称**：创建新数据库，修改 `.env` 中的数据库连接字符串

### 2.2 修改主题色

#### 客户端全局样式
📁 `july_client/app.wxss`
```css
/* 修改全局主题色 */
page {
  --theme-color: #337559;  /* 主题色 */
  --theme-light: #4a9d7a;  /* 浅色主题 */
  --theme-dark: #2a5f47;   /* 深色主题 */
}
```

#### 各个页面和组件
搜索并替换所有 `#337559` 为你的主题色

### 2.3 修改默认图片

- **默认头像**：`july_client/components/avatar/index.js`
- **默认封面**：`july_client/components/profile-card/index.js`
- **授权页背景**：`july_client/pages/auth/index.wxml`
- **空状态图片**：`july_client/images/icon_nothing/` 目录下的图片

---

## 3. 功能定制

### 3.1 修改或删除功能模块

#### 如果不需要"树洞"功能：
1. 删除 `july_client/pages/hole/` 和 `july_client/pages/hole-detail/`
2. 删除 `july_client/pages/chat-room/`
3. 从 `july_client/app.json` 中删除相关页面配置
4. 删除 `july_server/app/api/v2/hole.py`
5. 删除 `july_server/app/model/hole.py`

#### 如果不需要"关注"功能：
1. 删除 `july_client/pages/following/` 和 `july_client/pages/follower/`
2. 删除 `july_server/app/api/v2/following.py`
3. 删除 `july_server/app/model/following.py`

#### 如果不需要"视频"功能：
1. 修改 `july_client/pages/topic-edit/index.wxml`，删除视频上传按钮
2. 删除 `july_server/app/api/v2/video.py`
3. 删除 `july_server/app/model/video.py`

### 3.2 添加新功能模块

#### 添加新页面（客户端）：
1. 在 `july_client/pages/` 创建新页面目录
2. 在 `july_client/app.json` 的 `pages` 数组中添加页面路径
3. 如果需要Tab，在 `tabBar.list` 中添加配置

#### 添加新API（服务端）：
1. 在 `july_server/app/model/` 创建数据模型
2. 在 `july_server/app/api/v2/` 创建API接口
3. 在 `july_server/app/api/v2/__init__.py` 中注册新API
4. 在 `july_server/app/service/` 创建业务逻辑（可选）

---

## 4. 数据库定制

### 4.1 修改现有表结构

#### 示例：给用户表添加新字段
📁 `july_server/app/model/user.py`
```python
class User(BaseModel):
    # 原有字段...
    
    # 添加新字段
    phone = Column(String(11), comment='手机号')
    birthday = Column(Date, comment='生日')
    vip_level = Column(Integer, default=0, comment='VIP等级')
```

#### 生成数据库迁移
```bash
cd july_server
flask db migrate -m "add new fields to user"
flask db upgrade
```

### 4.2 添加新表

1. 在 `july_server/app/model/` 创建新模型文件
2. 继承 `BaseModel` 类
3. 运行数据库迁移命令

---

## 5. API定制

### 5.1 修改API路径前缀

如果想从 `/v2` 改为 `/api`：

#### 服务端
📁 `july_server/app/__init__.py`
```python
def register_resource(app):
    from .api.v2 import create_v2
    app.register_blueprint(create_v2(), url_prefix='/api')  # 修改这里
```

#### 客户端
📁 `july_client/config/api.js`
```javascript
const baseAPI = 'http://127.0.0.1:5000/api'  // 修改这里
```

### 5.2 添加自定义API

#### 服务端
📁 `july_server/app/api/v2/custom.py`（新建）
```python
from app.lib.red_print import RedPrint
from app.lib.exception import Success

api = RedPrint('custom')

@api.route('/hello', methods=['GET'])
def hello():
    return Success(data={'message': 'Hello World'})
```

#### 注册API
📁 `july_server/app/api/v2/__init__.py`
```python
from . import custom

def create_v2():
    bp = BluePrint('v2', __name__)
    # ... 其他注册
    custom.api.register(bp)
    return bp
```

#### 客户端调用
📁 `july_client/config/api.js`
```javascript
export default {
  // ... 其他配置
  customAPI: baseAPI + '/custom'
}
```

---

## 6. UI定制

### 6.1 修改全局样式

📁 `july_client/app.wxss`
```css
/* 修改全局字体 */
page {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB';
  font-size: 28rpx;  /* 修改默认字体大小 */
}

/* 修改全局按钮样式 */
button {
  border-radius: 8rpx;  /* 修改圆角 */
}
```

### 6.2 修改组件样式

每个组件都有独立的 `.wxss` 文件，可以单独修改：
- `july_client/components/topic-item/index.wxss`
- `july_client/components/profile-card/index.wxss`
- 等等...

### 6.3 修改页面布局

修改对应页面的 `.wxml` 文件：
- `july_client/pages/topic/index.wxml`
- `july_client/pages/profile/index.wxml`
- 等等...

---

## 7. 第三方服务配置

### 7.1 七牛云（图片/视频存储）

#### 注册并配置
1. 注册七牛云账号：https://www.qiniu.com/
2. 创建对象存储空间
3. 获取 AccessKey 和 SecretKey
4. 配置到 `.env` 文件中

#### 如果不使用七牛云
可以替换为其他云存储服务（阿里云OSS、腾讯云COS等）：
1. 修改 `july_server/app/manger/qiniu/` 目录下的代码
2. 修改 `july_client/utils/qiniuUploader.js`

### 7.2 Server酱（消息推送，可选）

1. 注册 Server酱：https://sct.ftqq.com/
2. 获取 SendKey
3. 配置到 `.env` 文件中

### 7.3 腾讯位置服务（IP归属地，可选）

1. 注册腾讯位置服务：https://lbs.qq.com/
2. 创建应用获取Key
3. 配置到 `.env` 文件中

---

## 8. 开发建议

### 8.1 版本控制
```bash
# 创建新分支进行开发
git checkout -b feature/your-feature

# 提交更改
git add .
git commit -m "描述你的更改"

# 推送到远程
git push origin feature/your-feature
```

### 8.2 测试环境
- 开发环境：本地测试
- 测试环境：使用测试服务器和测试小程序
- 生产环境：正式服务器和正式小程序

### 8.3 代码规范
- 遵循原项目的代码风格
- 添加必要的注释
- 保持代码整洁

### 8.4 性能优化
- 图片压缩和懒加载
- API请求合并和缓存
- 数据库索引优化
- 使用CDN加速静态资源

---

## 9. 常见定制场景

### 9.1 校园社区
- 添加学院/专业分类
- 添加课程表功能
- 添加失物招领模块
- 添加二手交易模块

### 9.2 企业内部社区
- 添加部门管理
- 添加审批流程
- 添加公告系统
- 添加考勤打卡

### 9.3 兴趣社区
- 添加活动报名
- 添加打卡签到
- 添加积分系统
- 添加等级体系

---

## 10. 部署上线

### 10.1 服务端部署
```bash
# 使用Docker部署（推荐）
docker build -t your-app .
docker run -d -p 5000:5000 --env-file .env --name your-app your-app

# 或使用Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 starter:app --worker-class eventlet
```

### 10.2 小程序发布
1. 在微信开发者工具中点击"上传"
2. 登录微信公众平台提交审核
3. 审核通过后发布

### 10.3 域名配置
1. 在微信公众平台配置服务器域名
2. 配置业务域名（如需要）
3. 配置WebSocket域名

---

## 📞 技术支持

如有问题，可以：
1. 查看原项目文档
2. 提交Issue到GitHub
3. 加入技术交流群

---

**祝开发顺利！🎉**

