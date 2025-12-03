# July 项目 — 心理知识文章导入与本地运行指南

本文档旨在把我们会话中完成的步骤整理成可复现的说明，方便你或其他人再次执行相同流程。

注意：不要把包含真实密码的 `.env` 提交到代码托管服务。

前置条件
- 操作系统：Windows
- Python 3.8+（项目使用虚拟环境 `.venv3` 推荐启用）
- MySQL Server 可访问（本例使用 `127.0.0.1:3306`）
- 如果需要：WeChat DevTools 用于小程序调试

关键文件（本次工作涉及，建议检查）
- 后端 API: `july_server/app/api/v2/mind.py` 与 `july_server/app_2/api/v2/mind.py`
- 前端配置: `july_client/config/api.js`
- 前端分页/模板: `july_client/utils/paging.js`, `july_client/pages/mind-recipes/*`
- SQL: `july_server/sql/mind_seed.generated.sql` (以及转换后的 `mind_seed.utf8.sql`)
- 辅助脚本: `july_server/scripts/convert_sql_to_utf8.py`, `july_server/scripts/test_mysql_connect.py`

一、把 SQL 转为 UTF-8（如需要）
1. 如果 SQL 文件编码不对，使用仓库中的脚本转换：

PowerShell / cmd:
```
cd "C:\Users\lyy\Desktop\july_client (2) (1)\july_server\sql"
python ..\scripts\convert_sql_to_utf8.py mind_seed.generated.sql mind_seed.utf8.sql
```

二、在 Windows 下导入 SQL（推荐使用 `cmd.exe` 而非 PowerShell 重定向以避免编码问题）
1. 直接在 `cmd.exe` 运行：
```
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" --default-character-set=utf8mb4 -u root -p -h127.0.0.1 -P3306 july < mind_seed.utf8.sql
```
2. 或者使用交互式 `mysql` 输入并运行 `SOURCE`：
```
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" --default-character-set=utf8mb4 -u root -p -h127.0.0.1 -P3306 july
mysql> SOURCE C:/path/to/mind_seed.utf8.sql;
```

三、验证数据已写入
```
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" --default-character-set=utf8mb4 -u root -p -h127.0.0.1 -P3306 -e "SELECT id,title,create_time FROM july.mind_knowledge ORDER BY create_time DESC LIMIT 20;"
```

四、设置后端环境并启动
1. 复制 `.env_template` 为 `.env`（位于 `july_server` 根），把 `YOURPASSWORD` 替换为本机 MySQL 密码：
```
cd "C:\Users\lyy\Desktop\july_client (2) (1)\july_server"
copy .env_template .env
:: 编辑 .env，将 SQLALCHEMY_DATABASE_URI 中的 YOURPASSWORD 替换
```
2. 推荐激活项目虚拟环境并安装依赖：
```
cd "C:\Users\lyy\Desktop\july_client (2) (1)\july_server"
.\.venv3\Scripts\Activate.ps1   # PowerShell
python -m pip install --upgrade pip
pip install -r requirements.txt
```
3. 启动后端：
```
python .\starter.py
```
4. 启动成功后应能看到类似：
```
[config] ENV=production, SQLALCHEMY_DATABASE_URI=mysql+cymysql://root:YOURPASSWORD@127.0.0.1:3306/july?charset=utf8mb4
* wsgi starting up on http://127.0.0.1:5000
```

五、测试 API（PowerShell 推荐用于中文可读）
```
Invoke-RestMethod -Uri 'http://127.0.0.1:5000/v2/mind/knowledge?page=1&size=50' -Method GET | ConvertTo-Json -Depth 6
```
检查 `code` 为 0、`data.items` 包含前面插入的文章（按 title 校验）。

六、若小程序端看不到数据的排查（常见）
- 确认 `july_client/config/api.js` 中 `baseAPI` 指向 `http://127.0.0.1:5000/v2`。
- 在 WeChat DevTools 清缓存并重启（`编译 -> 清缓存并重启`）。
- 在 DevTools Network 观察实际请求（page、size 参数），若前端默认请求 `page=2` 或 `size` 太小可能导致数据不在当前页。
- 临时测试：在 DevTools 中把请求的 `size` 改为 50 以确认数据可见。

七、如何回滚
- 仔细检查 `july_server/sql/` 下是否存在 `rollback_*.sql`。若存在，可在目标 DB 中执行回滚 SQL（小心：请先备份）。

八、备份与共享
- 为便于共享给他人，打包时包含：
  - `july_server/.env_template`（占位）
  - `july_server/sql/mind_seed.utf8.sql`（已转码的 SQL）
  - `README_SEED_IMPORT.md`（本文件）

如果在任一步遇到错误，请把完整命令输出或后端日志中的相关堆栈粘回。本指南会持续更新。

**最近变更（2025-12-01）**
- **后端**: 更新了 `july_server/app/api/v2/mind.py` 与 `july_server/app_2/api/v2/mind.py`，为条目构建 `summary` 字段，清理 `content` 中的“来源/原文链接”，并把原始来源保存在 `origin` 字段，前端可通过 `summary` 与 `origin` 显示简短摘要与来源。
- **数据库**: 已生成并建议导入 `july_server/sql/mind_seed.generated.sql`（建议先用 `convert_sql_to_utf8.py` 转为 `mind_seed.utf8.sql` 再导入）。运行更新脚本时会备份被修改的记录（如存在，会产生 `july_server/backup_mind_records_*.json`）并生成回滚 SQL（`july_server/rollback_mind_records_*.sql`）。
- **LBS（附近机构）**: 删除了大部分静态推荐条目，并在缺失时将“华中科技大学心理健康教育中心”作为首位推荐（修改文件：`july_server/app/service/lbs_service.py` 与 `july_server/app_2/service/lbs_service.py`）。
- **前端**: 列表页与详情页已调整优先使用 `summary` 显示简短文本，详情页显示 `origin`；检查 `july_client/pages/mind-recipes/*` 和 `july_client/utils/paging.js` 以确认分页参数（`page`/`size`）不会把数据隐藏在其他页。
- **验证**: 启动后端后（`python starter.py`），调用 `GET /v2/mind/knowledge?page=1&size=50`，确认响应中的 `data.items` 包含期望的标题和 `summary` 字段；若小程序未显示，清除微信开发者工具缓存并重新编译。
- **回滚提示**: 若需要回退数据库改动，优先使用 `july_server/rollback_mind_records_*.sql`（如果存在），并在执行前用 `mysqldump` 做一次备份；回退代码请使用 `git` 或手动恢复上文列出的受影响文件。
- **安全提醒**: 请勿把含真实凭据的 `.env` 提交到仓库；已在仓库保留 `.env_template` 作为占位符。

已保存当前修改到工作区。
