# 心情烘焙坊 - 开发计划书

## 📋 项目概述

**项目名称：** 心情烘焙坊  
**开发周期：** 6周（42天）  
**团队规模：** 5人  
**技术栈：** 微信小程序 + Flask + MySQL + Redis + LLM API

---

## 🎯 功能需求分析

### 功能一：情绪烘焙屋（帖子系统增强）
**基于原有主页，新增：**
- ✅ 互动设计：用"拥抱"或"拍拍"代替点赞
- ✅ 情绪标签：发帖时选择/自定义心情标签

### 功能二：今日订单（日记系统）
**全新页面：**
- ✅ 日历视图展示日记
- ✅ 不同心情用不同颜色/图标
- ✅ 默认私密，可选公开

### 功能三：巧克力罐（心灵鸡汤推送）
**智能推送系统：**
- ✅ 基于LLM的智能推送
- ✅ 分析心情标签、帖子内容、日记关键词
- ✅ 浮动按钮 + 弹窗展示

### 功能四：烘焙后厨（个人空间增强）
**基于原有"我的"页面，新增：**
- ✅ 情绪波动图表
- ✅ 情绪统计分析

---

## 👥 团队分工

### 成员A - 项目经理 & 前端开发（Leader）
**职责：**
- 项目管理与进度把控
- 前端架构设计
- 功能一：情绪烘焙屋前端开发
- 功能四：烘焙后厨前端开发
- 代码审查与集成

### 成员B - 后端开发（核心）
**职责：**
- 后端架构设计
- 数据库设计与优化
- 功能一：帖子系统后端API
- 功能二：日记系统后端API
- LLM接口封装

### 成员C - 前端开发
**职责：**
- 功能二：今日订单页面开发
- 功能三：巧克力罐前端开发
- UI组件开发
- 动画效果实现

### 成员D - 算法工程师 & 后端开发
**职责：**
- LLM集成与调优
- 功能三：智能推送算法
- 功能四：情绪分析算法
- 数据分析与可视化

### 成员E - 测试工程师 & UI设计
**职责：**
- UI/UX设计
- 图标与视觉资源制作
- 功能测试
- 用户体验优化

---

## 📅 开发时间表（6周）

### 第1周：需求分析与设计（Day 1-7）

#### Day 1-2：需求细化与技术调研
**全员参与**
- [ ] 详细需求文档编写（成员A）
- [ ] 技术方案选型（成员B、D）
- [ ] LLM API选择与测试（成员D）
- [ ] UI设计风格确定（成员E）

**产出物：**
- 需求规格说明书
- 技术方案文档
- LLM API测试报告

#### Day 3-5：数据库设计与原型设计
**分组工作**
- [ ] 数据库表结构设计（成员B）
- [ ] API接口文档编写（成员B）
- [ ] 高保真原型设计（成员E）
- [ ] 前端组件规划（成员A、C）

**产出物：**
- 数据库ER图
- API接口文档
- 高保真原型图

#### Day 6-7：环境搭建与基础架构
**全员参与**
- [ ] 开发环境配置（全员）
- [ ] Git仓库与分支管理（成员A）
- [ ] 后端基础框架搭建（成员B）
- [ ] 前端基础框架搭建（成员A、C）

**产出物：**
- 开发环境文档
- 基础代码框架

---

### 第2周：核心功能开发 - 情绪烘焙屋（Day 8-14）

#### Day 8-10：后端开发
**成员B**
- [ ] 情绪标签表设计与实现
- [ ] 帖子表添加情绪标签字段
- [ ] 互动类型表设计（拥抱/拍拍）
- [ ] 帖子发布API增强
- [ ] 互动API开发

**成员D**
- [ ] 情绪标签推荐算法
- [ ] 协助后端API开发

#### Day 11-14：前端开发
**成员A**
- [ ] 发帖页面改造
  - [ ] 情绪标签选择器组件
  - [ ] 自定义标签输入
  - [ ] 标签展示样式
- [ ] 帖子列表页改造
  - [ ] 情绪标签展示
  - [ ] 互动按钮设计（拥抱/拍拍图标）
  - [ ] 互动动画效果

**成员C**
- [ ] 互动组件开发
- [ ] 情绪标签组件开发

**成员E**
- [ ] 拥抱/拍拍图标设计
- [ ] 情绪标签图标设计
- [ ] 功能测试

**产出物：**
- 情绪烘焙屋增强版

---

### 第3周：核心功能开发 - 今日订单（Day 15-21）

#### Day 15-17：后端开发
**成员B**
- [ ] 日记表设计
  - [ ] 日记内容
  - [ ] 情绪标签
  - [ ] 隐私设置
  - [ ] 日期索引
- [ ] 日记CRUD API
- [ ] 日记列表API（按日历展示）
- [ ] 情绪统计API

**成员D**
- [ ] 日记关键词提取算法
- [ ] 情绪分析算法

#### Day 18-21：前端开发
**成员C（主力）**
- [ ] 日历视图组件开发
  - [ ] 月历展示
  - [ ] 日期标记（不同颜色/图标）
  - [ ] 日期点击事件
- [ ] 日记编辑页面
  - [ ] 富文本编辑器
  - [ ] 情绪标签选择
  - [ ] 隐私设置开关
- [ ] 日记详情页面
  - [ ] 日记内容展示
  - [ ] 编辑/删除功能

**成员A**
- [ ] 导航栏配置
- [ ] 页面路由配置
- [ ] 代码审查

**成员E**
- [ ] 日历图标设计（不同情绪）
- [ ] 页面UI优化
- [ ] 功能测试

**产出物：**
- 今日订单完整功能

---

### 第4周：核心功能开发 - 巧克力罐（Day 22-28）

#### Day 22-24：LLM集成与算法开发
**成员D（主力）**
- [ ] LLM API封装
  - [ ] 提示词工程
  - [ ] 请求/响应处理
  - [ ] 错误处理与重试
- [ ] 智能推送算法
  - [ ] 用户画像构建
  - [ ] 情绪标签分析
  - [ ] 内容关键词提取
  - [ ] 推送内容生成
- [ ] 推送记录表设计

**成员B**
- [ ] 推送API开发
- [ ] 推送历史API
- [ ] 缓存策略实现

#### Day 25-28：前端开发
**成员C（主力）**
- [ ] 巧克力罐浮动按钮
  - [ ] 固定定位
  - [ ] 动画效果
  - [ ] 点击交互
- [ ] 推送弹窗组件
  - [ ] 弹窗动画
  - [ ] 内容展示
  - [ ] 收藏功能
  - [ ] 分享功能
- [ ] 推送历史页面

**成员A**
- [ ] 集成到今日订单页面
- [ ] 代码审查

**成员E**
- [ ] 巧克力罐图标设计
- [ ] 弹窗UI设计
- [ ] 功能测试

**产出物：**
- 巧克力罐智能推送系统

---

### 第5周：核心功能开发 - 烘焙后厨（Day 29-35）

#### Day 29-31：后端开发
**成员B**
- [ ] 情绪统计API
  - [ ] 按时间段统计
  - [ ] 情绪分布统计
  - [ ] 情绪趋势分析
- [ ] 数据聚合优化

**成员D**
- [ ] 情绪波动算法
- [ ] 图表数据处理
- [ ] 情绪洞察生成

#### Day 32-35：前端开发
**成员A（主力）**
- [ ] 情绪档案模块
  - [ ] 情绪波动折线图
  - [ ] 情绪分布饼图
  - [ ] 时间范围选择器
  - [ ] 情绪洞察展示
- [ ] 个人空间页面改造
  - [ ] 模块化布局
  - [ ] 数据可视化
  - [ ] 交互优化

**成员C**
- [ ] 图表组件封装
- [ ] 动画效果

**成员E**
- [ ] 图表UI设计
- [ ] 页面整体优化
- [ ] 功能测试

**产出物：**
- 烘焙后厨情绪分析功能

---

### 第6周：测试、优化与上线（Day 36-42）

#### Day 36-38：集成测试
**全员参与**
- [ ] 功能集成测试（成员E主导）
- [ ] 性能测试与优化（成员B、D）
- [ ] 兼容性测试（成员C）
- [ ] Bug修复（全员）

**测试重点：**
- 各功能模块独立测试
- 功能间联动测试
- 边界条件测试
- 性能压力测试

#### Day 39-40：用户体验优化
**全员参与**
- [ ] UI细节优化（成员E）
- [ ] 交互流程优化（成员A、C）
- [ ] 加载速度优化（成员B）
- [ ] 错误提示优化（全员）

#### Day 41：内部验收
**全员参与**
- [ ] 功能演示
- [ ] 问题汇总
- [ ] 紧急修复

#### Day 42：上线准备
**全员参与**
- [ ] 生产环境部署（成员B）
- [ ] 小程序提交审核（成员A）
- [ ] 用户手册编写（成员E）
- [ ] 运维文档编写（成员B）

**产出物：**
- 完整可用的产品
- 用户手册
- 运维文档

---

## 🗂️ 数据库设计

### 新增/修改表结构

#### 1. 情绪标签表 (emotion_label)
```sql
CREATE TABLE emotion_label (
  id VARCHAR(32) PRIMARY KEY COMMENT '主键',
  name VARCHAR(20) NOT NULL COMMENT '标签名称',
  icon VARCHAR(256) COMMENT '标签图标',
  color VARCHAR(7) COMMENT '标签颜色',
  type ENUM('SYSTEM', 'CUSTOM') DEFAULT 'SYSTEM' COMMENT '标签类型',
  user_id VARCHAR(32) COMMENT '创建用户ID（自定义标签）',
  use_count INT DEFAULT 0 COMMENT '使用次数',
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  delete_time DATETIME,
  INDEX idx_user_id (user_id),
  INDEX idx_type (type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='情绪标签表';
```

#### 2. 帖子表修改 (topic)
```sql
ALTER TABLE topic 
ADD COLUMN emotion_label_id VARCHAR(32) COMMENT '情绪标签ID',
ADD INDEX idx_emotion_label (emotion_label_id);
```

#### 3. 互动表修改 (star)
```sql
ALTER TABLE star
ADD COLUMN interaction_type ENUM('STAR', 'HUG', 'PAT') DEFAULT 'STAR' COMMENT '互动类型';
```

#### 4. 日记表 (diary)
```sql
CREATE TABLE diary (
  id VARCHAR(32) PRIMARY KEY COMMENT '主键',
  user_id VARCHAR(32) NOT NULL COMMENT '用户ID',
  content TEXT NOT NULL COMMENT '日记内容',
  emotion_label_id VARCHAR(32) COMMENT '情绪标签ID',
  diary_date DATE NOT NULL COMMENT '日记日期',
  is_public BOOLEAN DEFAULT FALSE COMMENT '是否公开',
  weather VARCHAR(20) COMMENT '天气',
  location VARCHAR(100) COMMENT '地点',
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  update_time DATETIME,
  delete_time DATETIME,
  INDEX idx_user_date (user_id, diary_date),
  INDEX idx_emotion (emotion_label_id),
  INDEX idx_public (is_public),
  UNIQUE KEY uk_user_date (user_id, diary_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='日记表';
```

#### 5. 心灵鸡汤推送记录表 (soul_push)
```sql
CREATE TABLE soul_push (
  id VARCHAR(32) PRIMARY KEY COMMENT '主键',
  user_id VARCHAR(32) NOT NULL COMMENT '用户ID',
  content TEXT NOT NULL COMMENT '推送内容',
  source_type ENUM('DIARY', 'TOPIC', 'EMOTION') COMMENT '来源类型',
  source_id VARCHAR(32) COMMENT '来源ID',
  emotion_label_id VARCHAR(32) COMMENT '情绪标签ID',
  is_collected BOOLEAN DEFAULT FALSE COMMENT '是否收藏',
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_user (user_id),
  INDEX idx_source (source_type, source_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='心灵鸡汤推送记录表';
```

#### 6. 情绪统计表 (emotion_stat)
```sql
CREATE TABLE emotion_stat (
  id VARCHAR(32) PRIMARY KEY COMMENT '主键',
  user_id VARCHAR(32) NOT NULL COMMENT '用户ID',
  stat_date DATE NOT NULL COMMENT '统计日期',
  emotion_label_id VARCHAR(32) COMMENT '情绪标签ID',
  count INT DEFAULT 1 COMMENT '次数',
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  update_time DATETIME,
  INDEX idx_user_date (user_id, stat_date),
  INDEX idx_emotion (emotion_label_id),
  UNIQUE KEY uk_user_date_emotion (user_id, stat_date, emotion_label_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='情绪统计表';
```

---

## 🔌 API接口设计

### 功能一：情绪烘焙屋

#### 1. 获取情绪标签列表
```
GET /v2/emotion/label
Response: {
  code: 0,
  data: {
    system_labels: [...],  // 系统标签
    custom_labels: [...]   // 用户自定义标签
  }
}
```

#### 2. 创建自定义标签
```
POST /v2/emotion/label
Body: {
  name: "标签名称",
  color: "#FF5733"
}
```

#### 3. 发布帖子（增强）
```
POST /v2/topic
Body: {
  content: "帖子内容",
  images: [...],
  emotion_label_id: "标签ID"
}
```

#### 4. 互动（拥抱/拍拍）
```
POST /v2/topic/{topic_id}/interact
Body: {
  interaction_type: "HUG" | "PAT"
}
```

### 功能二：今日订单

#### 1. 创建日记
```
POST /v2/diary
Body: {
  content: "日记内容",
  emotion_label_id: "标签ID",
  diary_date: "2025-10-25",
  is_public: false
}
```

#### 2. 获取日记列表（日历视图）
```
GET /v2/diary?year=2025&month=10
Response: {
  code: 0,
  data: {
    "2025-10-25": {
      id: "...",
      emotion_label: {...},
      has_content: true
    },
    ...
  }
}
```

#### 3. 获取日记详情
```
GET /v2/diary/{diary_id}
```

#### 4. 更新日记
```
PUT /v2/diary/{diary_id}
```

#### 5. 删除日记
```
DELETE /v2/diary/{diary_id}
```

### 功能三：巧克力罐

#### 1. 获取智能推送
```
POST /v2/soul/push
Body: {
  source_type: "DIARY" | "TOPIC" | "EMOTION",
  source_id: "来源ID"
}
Response: {
  code: 0,
  data: {
    content: "温暖的句子...",
    push_id: "推送ID"
  }
}
```

#### 2. 收藏推送
```
POST /v2/soul/push/{push_id}/collect
```

#### 3. 获取推送历史
```
GET /v2/soul/push/history
```

### 功能四：烘焙后厨

#### 1. 获取情绪统计
```
GET /v2/emotion/stat?start_date=2025-10-01&end_date=2025-10-31
Response: {
  code: 0,
  data: {
    trend: [...],      // 情绪趋势数据
    distribution: [...], // 情绪分布数据
    insights: "..."    // 情绪洞察
  }
}
```

#### 2. 获取情绪波动图
```
GET /v2/emotion/wave?days=30
```

---

## 🎨 前端页面结构

### 新增/修改页面

```
july_client/pages/
├── topic/                    # 情绪烘焙屋（修改）
│   ├── index.js
│   ├── index.wxml
│   └── index.wxss
├── topic-edit/               # 发帖页面（修改）
│   ├── index.js
│   ├── index.wxml
│   └── index.wxss
├── diary/                    # 今日订单（新增）
│   ├── index.js
│   ├── index.wxml
│   └── index.wxss
├── diary-edit/               # 日记编辑（新增）
│   ├── index.js
│   ├── index.wxml
│   └── index.wxss
├── profile/                  # 烘焙后厨（修改）
│   ├── index.js
│   ├── index.wxml
│   └── index.wxss
└── soul-history/             # 推送历史（新增）
    ├── index.js
    ├── index.wxml
    └── index.wxss
```

### 新增组件

```
july_client/components/
├── emotion-label/            # 情绪标签选择器
│   ├── index.js
│   ├── index.wxml
│   └── index.wxss
├── calendar-view/            # 日历视图
│   ├── index.js
│   ├── index.wxml
│   └── index.wxss
├── soul-popup/               # 鸡汤弹窗
│   ├── index.js
│   ├── index.wxml
│   └── index.wxss
├── emotion-chart/            # 情绪图表
│   ├── index.js
│   ├── index.wxml
│   └── index.wxss
└── interaction-btn/          # 互动按钮（拥抱/拍拍）
    ├── index.js
    ├── index.wxml
    └── index.wxss
```

---

## 🤖 LLM集成方案

### 推荐方案

#### 方案一：OpenAI API（推荐）
- **模型：** GPT-3.5-turbo 或 GPT-4
- **优点：** 效果好，稳定性高
- **成本：** 约 $0.002/1K tokens

#### 方案二：国内大模型
- **选项：** 文心一言、通义千问、讯飞星火
- **优点：** 国内访问快，中文理解好
- **成本：** 相对较低

### 提示词设计

```python
PROMPT_TEMPLATE = """
你是一位温暖的心理陪伴者，请根据用户的情绪和内容，生成一句温暖、治愈的话。

用户情绪标签：{emotion_label}
用户内容：{content}

要求：
1. 语言温暖、真诚、不说教
2. 50字以内
3. 贴合用户的情绪状态
4. 给予鼓励和支持

请生成一句话：
"""
```

---

## 📊 项目里程碑

| 里程碑 | 时间节点 | 交付物 | 负责人 |
|--------|---------|--------|--------|
| M1: 需求与设计完成 | Day 7 | 需求文档、原型图、技术方案 | 成员A |
| M2: 情绪烘焙屋完成 | Day 14 | 功能一完整实现 | 成员A、B |
| M3: 今日订单完成 | Day 21 | 功能二完整实现 | 成员B、C |
| M4: 巧克力罐完成 | Day 28 | 功能三完整实现 | 成员C、D |
| M5: 烘焙后厨完成 | Day 35 | 功能四完整实现 | 成员A、D |
| M6: 测试与上线 | Day 42 | 完整产品 | 全员 |

---

## ⚠️ 风险管理

### 技术风险

| 风险 | 影响 | 应对措施 |
|------|------|---------|
| LLM API不稳定 | 高 | 准备备用方案，实现降级策略 |
| 性能问题 | 中 | 提前进行压力测试，优化查询 |
| 兼容性问题 | 中 | 多设备测试，使用兼容性好的组件 |

### 进度风险

| 风险 | 影响 | 应对措施 |
|------|------|---------|
| 开发延期 | 高 | 每周进度review，及时调整 |
| 人员变动 | 高 | 文档完善，知识共享 |
| 需求变更 | 中 | 需求冻结，变更评审 |

---

## 📝 每日站会

**时间：** 每天早上 10:00  
**时长：** 15分钟  
**内容：**
1. 昨天完成了什么
2. 今天计划做什么
3. 遇到什么问题

---

## 🔍 代码审查

**频率：** 每周两次（周三、周五）  
**审查人：** 成员A  
**内容：**
- 代码规范
- 功能实现
- 性能优化
- 安全问题

---

## 📚 文档要求

### 必须文档
1. **需求规格说明书**（成员A）
2. **技术方案文档**（成员B）
3. **API接口文档**（成员B）
4. **数据库设计文档**（成员B）
5. **用户手册**（成员E）
6. **运维文档**（成员B）

### 推荐文档
1. 开发日志
2. 问题记录
3. 测试报告

---

## 🎯 成功标准

### 功能完整性
- ✅ 所有功能按需求实现
- ✅ 无严重Bug
- ✅ 用户体验流畅

### 性能指标
- ✅ 页面加载时间 < 2秒
- ✅ API响应时间 < 500ms
- ✅ 支持100+并发用户

### 质量指标
- ✅ 代码覆盖率 > 60%
- ✅ Bug密度 < 5个/KLOC
- ✅ 用户满意度 > 4.0/5.0

---

## 📞 沟通机制

### 日常沟通
- **工具：** 微信群 + 企业微信
- **响应时间：** 工作时间内 < 1小时

### 问题升级
1. 成员间协商（30分钟）
2. 向成员A汇报（1小时）
3. 团队讨论（当天）

### 周报
- **时间：** 每周五下午
- **内容：** 本周进展、下周计划、问题与风险

---

## 🎉 项目启动

### 启动会议（Day 1）
**时间：** 2小时  
**议程：**
1. 项目背景介绍（15分钟）
2. 需求详细讲解（30分钟）
3. 技术方案讨论（30分钟）
4. 分工确认（30分钟）
5. 时间表确认（15分钟）

### 准备工作
- [ ] 创建项目仓库
- [ ] 配置开发环境
- [ ] 建立沟通群组
- [ ] 准备开发工具

---

**祝项目顺利！加油！💪**

