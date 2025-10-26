# 心情烘焙坊 - 快速开始指南

## 🚀 立即开始

### 第一步：环境准备（Day 1）

#### 全员
```bash
# 1. 克隆项目
git clone <repository_url>
cd bakery

# 2. 创建开发分支
git checkout -b develop
git push origin develop

# 3. 创建个人分支
git checkout -b feature/your-name
```

#### 成员B（后端）
```bash
# 1. 进入服务端目录
cd july_server

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 创建数据库
mysql -u root -p
CREATE DATABASE mood_bakery CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

# 5. 导入基础数据
mysql -u root -p mood_bakery < sql/july.sql

# 6. 配置环境变量
cp .env_template .env
# 编辑 .env 文件
```

#### 成员A、C（前端）
```bash
# 1. 进入客户端目录
cd july_client

# 2. 安装依赖
npm install

# 3. 配置小程序AppID
# 编辑 project.config.json

# 4. 配置API地址
# 编辑 config/api.js
```

---

## 📋 每周任务清单

### 第1周任务（Day 1-7）

#### 成员A - 项目经理
- [ ] Day 1-2: 编写详细需求文档
- [ ] Day 3: 设计前端组件架构
- [ ] Day 4-5: 审查原型设计
- [ ] Day 6-7: 搭建前端基础框架

#### 成员B - 后端开发
- [ ] Day 1-2: 技术方案选型
- [ ] Day 3-4: 数据库设计
- [ ] Day 5: 编写API接口文档
- [ ] Day 6-7: 搭建后端基础框架

#### 成员C - 前端开发
- [ ] Day 1-2: 学习项目代码
- [ ] Day 3-5: 协助原型设计
- [ ] Day 6-7: 搭建前端基础框架

#### 成员D - 算法工程师
- [ ] Day 1-2: LLM API调研与测试
- [ ] Day 3-4: 设计推送算法
- [ ] Day 5-7: 搭建算法服务框架

#### 成员E - 测试&设计
- [ ] Day 1-2: 确定设计风格
- [ ] Day 3-5: 完成高保真原型
- [ ] Day 6-7: 制作基础图标资源

---

## 🔧 开发规范

### Git提交规范
```
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式调整
refactor: 重构
test: 测试相关
chore: 构建/工具相关
```

**示例：**
```bash
git commit -m "feat: 添加情绪标签选择器组件"
git commit -m "fix: 修复日历视图日期显示错误"
```

### 代码审查流程
1. 完成功能开发
2. 自测通过
3. 提交Pull Request
4. 成员A审查
5. 修改后合并

### 命名规范

#### 前端
```javascript
// 页面文件：小写+连字符
diary-edit/index.js

// 组件：小写+连字符
emotion-label/index.js

// 变量：驼峰命名
const emotionLabel = '开心'

// 常量：大写+下划线
const MAX_LABEL_LENGTH = 10
```

#### 后端
```python
# 文件名：小写+下划线
emotion_label.py

# 类名：大驼峰
class EmotionLabel(BaseModel):

# 函数名：小写+下划线
def get_emotion_list():

# 常量：大写+下划线
MAX_LABEL_LENGTH = 10
```

---

## 📱 功能开发快速指南

### 功能一：情绪标签（示例）

#### 后端开发（成员B）
```python
# 1. 创建模型 app/model/emotion_label.py
from app.model.base import BaseModel
from sqlalchemy import Column, String, Integer

class EmotionLabel(BaseModel):
    __tablename__ = 'emotion_label'
    
    name = Column(String(20), nullable=False)
    icon = Column(String(256))
    color = Column(String(7))
    use_count = Column(Integer, default=0)

# 2. 创建API app/api/v2/emotion.py
from app.lib.red_print import RedPrint

api = RedPrint('emotion')

@api.route('/label', methods=['GET'])
def get_labels():
    labels = EmotionLabel.get_all(delete_time=None)
    return Success(data=labels)

# 3. 注册API app/api/v2/__init__.py
from . import emotion

def create_v2():
    bp = BluePrint('v2', __name__)
    emotion.api.register(bp)
    return bp
```

#### 前端开发（成员A）
```javascript
// 1. 创建模型 models/emotion.js
import api from '../config/api'
import wxutil from '../miniprogram_npm/@yyjeffrey/wxutil/index'

class Emotion {
  static async getLabelList() {
    const res = await wxutil.request.get(`${api.baseAPI}/emotion/label`)
    if (res.code === 0) {
      return res.data
    }
    return []
  }
}

export { Emotion }

// 2. 创建组件 components/emotion-label/index.js
Component({
  properties: {
    selected: String
  },
  data: {
    labels: []
  },
  lifetimes: {
    async attached() {
      const labels = await Emotion.getLabelList()
      this.setData({ labels })
    }
  },
  methods: {
    onLabelTap(e) {
      const label = e.currentTarget.dataset.label
      this.triggerEvent('select', label)
    }
  }
})

// 3. 在页面中使用
<emotion-label selected="{{emotionLabel}}" bind:select="onEmotionSelect" />
```

---

## 🐛 常见问题解决

### 问题1：后端启动失败
```bash
# 检查端口占用
netstat -an | findstr :5000

# 检查虚拟环境
which python  # 应该指向venv中的python

# 检查依赖
pip list
```

### 问题2：前端无法连接后端
```javascript
// 检查 config/api.js
const baseAPI = 'http://127.0.0.1:5000/v2'  // 确保端口正确

// 检查微信开发者工具设置
// 详情 -> 本地设置 -> 不校验合法域名
```

### 问题3：数据库连接失败
```bash
# 检查MySQL服务
# Windows: services.msc
# Mac/Linux: sudo service mysql status

# 检查.env配置
SQLALCHEMY_DATABASE_URI=mysql+cymysql://root:password@127.0.0.1:3306/mood_bakery?charset=utf8mb4
```

---

## 📞 紧急联系

### 技术问题
- 后端问题 → 成员B
- 前端问题 → 成员A
- 算法问题 → 成员D
- UI问题 → 成员E

### 项目管理
- 进度问题 → 成员A
- 资源问题 → 成员A
- 冲突协调 → 成员A

---

## 🎯 本周目标（示例）

### Week 1 目标
- [ ] 完成需求文档
- [ ] 完成数据库设计
- [ ] 完成原型设计
- [ ] 完成环境搭建

### Week 2 目标
- [ ] 完成情绪标签功能
- [ ] 完成互动功能
- [ ] 完成单元测试

---

## 📚 学习资源

### 微信小程序
- [官方文档](https://developers.weixin.qq.com/miniprogram/dev/framework/)
- [Lin UI组件库](https://doc.mini.talelin.com/)

### Flask
- [官方文档](https://flask.palletsprojects.com/)
- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/)

### LLM
- [OpenAI API文档](https://platform.openai.com/docs)
- [提示词工程指南](https://www.promptingguide.ai/)

---

## ✅ 每日检查清单

### 开发前
- [ ] 拉取最新代码 `git pull origin develop`
- [ ] 检查任务列表
- [ ] 准备开发环境

### 开发中
- [ ] 遵循代码规范
- [ ] 及时提交代码
- [ ] 编写必要注释

### 开发后
- [ ] 自测功能
- [ ] 提交代码
- [ ] 更新任务状态

---

**开始你的开发之旅吧！🚀**

