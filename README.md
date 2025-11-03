# bakery

项目顶层 README。下面是新增的 Mind feature 说明（由脚本和 PR 引入）。

## Mind feature 更新说明

本节说明如何在本地运行与验证“心灵配方（Mind）”功能，以及本次改动对前端/后端的影响要点。

1) 变更概览（要点）

- 后端 seed 脚本现在会使用新的内容生成器扩写或覆盖 `mind_knowledge` 表中的 `content` 字段；重复运行 seed 会覆盖已有条目的 `content`。
- API 后备数组与 `/v2/mind/knowledge/<id>` 已保证返回完整 `content`（长文本，按段落结构）。
- 前端详情页已改为使用 `<rich-text>` 渲染长正文，`detail.js` 会把 `content` 按段落拆分为 rich nodes。

2) 在本地运行 seed（开发数据库）

在 `july_server` 目录下执行下列命令（Windows PowerShell）：

```powershell
cd 'C:\Users\lyy\Desktop\bakery-Func1AndFunc2\july_server'
& .\.venv\Scripts\Activate.ps1   # 激活虚拟环境（根据你们的 venv 路径调整）
pip install -r requirements.txt
python -m scripts.seed_mind      # 将生成/覆盖 mind_knowledge 的 content
```

启动后端服务：

```powershell
python .\starter.py
```

3) 必要的环境变量（示例）

- `WEIXIN_LBS_KEY`：腾讯地图/微信定位 API Key（用于 LBS 查询）
- `AMAP_LBS_KEY`：高德地图 API Key（作为备选）
- `SQLALCHEMY_DATABASE_URI` 或其他项目中使用的 DB 连接变量（例如 `DATABASE_URL` / `MYSQL_URI`，请参照项目中 `.env` 或 `config` 配置）
- 其他常见：`FLASK_ENV`, `SECRET_KEY`（如项目运行时需要）

把这些变量放入项目根部的 `.env`（开发环境）或通过 CI/CD 的机密配置注入。

4) 在微信开发者工具中刷新缓存（确保能看到最新前端改动）

- 打开微信开发者工具 → 项目 → 选择“清缓存并编译”。
- 或者关闭开发者工具后重新打开并重新编译项目。
- 如果调试定位或 map-preview，请在开发者工具的“设置/编译”中启用位置模拟或手动指定经纬度（测试坐标示例：lat=30.518, lng=114.414，用于验证华中科技大学回退/优先展示）。

5) 简短的变更影响说明（给前端/QA）

- 后端：种子脚本将覆盖 `content` 字段；在生产数据库运行前请先审查数据备份。不要在未批准的生产环境直接运行 seed。
- API：后端后备文本由生成器扩写，`/v2/mind/knowledge/<id>` 现在会返回更长的 `content`，客户端需要能够处理长文本与段落渲染。
- 前端：详情页切换到 `rich-text` 渲染，样式（段间距、超链接、截断）可能需做微调；定位权限会在真机或体验版触发权限弹窗，请提前说明给 QA。

如需在 PR 中包含本节（供 reviewer 参考），PR body 已生成在 `PR_BODY.md`（仓库根），会在发起 PR 时作为说明一起提交。
