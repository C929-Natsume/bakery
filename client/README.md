心情烘焙坊小程序客户端（bakery_client）

> 微信小程序前端代码，用于展示心情烘焙坊商品、用户资料、下单与互动等功能。

## 功能概览
- 情绪烘焙屋：发帖、评论与互动社区。
- 心灵配方：心理知识科普与结构化内容浏览。
- 今日订单：个人日记记录与管理。
- 烘焙后厨：个人中心，展示头像/资料与设置入口。
- 巧克力罐：智能心灵鸡汤推送与个性化推荐。
- 配置化：通过 `config/` 与 `utils/` 管理常量与工具方法。
- 组件化：在 `components/` 下复用 UI 组件（如头像、卡片等）。

## 运行环境
- 微信开发者工具（推荐最新版）。
- 微信小程序基础库版本：与项目 `project.config.json` 保持兼容（建议使用工具自动选择）。
- Node.js（可选）：用于安装/管理 `miniprogram_npm` 依赖。

## 快速开始
1. 安装微信开发者工具，并登录。
2. 在工具中导入项目：
   - 选择目录：`项目源码/bakery_client/bakery`
   - AppID：使用你自己的测试 AppID（或测试号）。
3. 根据需要配置本地或远端服务端地址：
   - 查看并调整 `config/` 下的接口地址配置（如有）。
4. 预览与调试：
   - 在开发者工具中点击“预览/编译”，观察页面效果与控制台日志。

## 项目结构
```
bakery_client/
  README.md                # 当前文件
  bakery/
    app.js                 # 小程序全局逻辑
    app.json               # 路由页面、窗口、分包等全局配置
    app.wxss               # 全局样式
    components/            # 业务与通用组件
    config/                # 常量/环境/接口配置
    images/                # 图片资源
    LICENSE                # 开源许可文件
    miniprogram_npm/       # 小程序 npm 依赖（需在构建中引入）
    models/                # 数据模型与类型
    package.json           # 前端依赖定义（如使用 npm）
    pages/                 # 业务页面（列表、详情、用户中心等）
    project.config.json    # 微信项目配置（工具识别）
    project.private.config.json # 私有配置（本地工具偏好）
    sitemap.json           # 小程序索引配置
    utils/                 # 工具函数（请求、格式化、校验等）
```

## 开发与构建
- 依赖安装（如使用 npm 组件）：
  - 在终端（PowerShell）进入 `项目源码/bakery_client/bakery`：
    ```powershell
    cd "c:\Users\lyy\Desktop\第10组(连晓仪-郝依凝-李语嫣-王茜-陈琦晗)\项目源码\bakery_client\bakery"
    npm install
    ```
  - 在微信开发者工具中：工具栏选择“构建 npm”，确保 `miniprogram_npm` 正确生成。
- 接口联调：
  - 保持服务端（`bakery_server`）运行，前端配置指向正确地址（如 `http://localhost:8000`）。
  - 使用工具的“网络”面板查看请求与响应。

## 常见问题
- 构建 npm 报错：确认 Node.js 安装、`npm install` 成功，并在工具中使用“构建 npm”而非手动复制依赖。
- 预览白屏或页面不显示：检查 `app.json` 中页面路径是否存在于 `pages/`，以及对应 `wxml/wxss/js/json` 文件是否完整。
- 跨域或请求失败：微信小程序不使用浏览器跨域策略，但需保证服务端可访问、域名/端口已在微信后台或本地开发设置允许范围。

## 截图与演示
- 可将运行时截图放在 `image/log/` 或 `images/`，并在此处粘贴示例。

## 许可证
- 参见 `bakery/LICENSE`。如需二次分发或修改，请遵循该许可证条款。

## 参考
- 微信官方文档：https://developers.weixin.qq.com/miniprogram/dev/
- 小程序 npm 使用：https://developers.weixin.qq.com/miniprogram/dev/devtools/npm.html
