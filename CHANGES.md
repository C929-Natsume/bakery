# CHANGES.md

此文件列出本次会话中需要关注/已修改或建议检查的文件与产物，便于回退或分发给他人。

注意：如果你使用版本控制（git），请用 `git status` / `git diff` 来查看具体更改；如果没有，请手动审查下列路径。

主要受影响或应检查的文件/目录：
- `july_server/app/api/v2/mind.py`  —— 列表/详情 API（summary/origin 清洗逻辑）
- `july_server/app_2/api/v2/mind.py` —— 同上（备用分支）
- `july_server/sql/mind_seed.generated.sql` —— 原始生成的种子 SQL（可能已转码为 `mind_seed.utf8.sql`）
- `july_server/sql/mind_seed.utf8.sql` —— 转码后的 SQL（建议保留以便重现导入步骤）
- `july_server/backup_mind_records_*.json` —— 更新前的备份数据（如果存在）
- `july_server/rollback_mind_records_*.sql` —— 自动生成的回滚 SQL（如果存在）
- `july_client/config/api.js` —— 前端 API 根路径（确认为本地开发时指向 `http://127.0.0.1:5000/v2`）
- `july_client/utils/paging.js` 与 `july_client/pages/mind-recipes/*` —— 前端分页与模板，可能需调整 `size` 或初始 `page`

我已在仓库中添加：
- `july_server/.env_template`（占位，复制为 `.env` 后替换密码）
- `README_SEED_IMPORT.md`（本指南）
- `CHANGES.md`（本文件）

回滚建议：
1. 如果要回退数据库改动，优先使用 `rollback_mind_records_*.sql`（如存在），并在执行前备份当前表：
   - `mysqldump -u root -p july mind_knowledge > mind_knowledge_backup.sql`
   - 然后执行回滚 SQL。
2. 要回退代码修改（若使用 git）：
   - `git checkout -- <file>` 或使用 `git revert` 回退提交。

如果需要我把这些变更整理为一个 zip 包或创建一个带占位符的 `.env` 并自动启动示例（在安全前提下），告诉我你偏好的密码处理方式（占位 OR 我写入真实密码 — 注意安全）。

## 最近变更（2025-12-01）

- **受影响文件（主要）**:
   - `july_server/app/api/v2/mind.py`
   - `july_server/app_2/api/v2/mind.py`
   - `july_server/app/service/lbs_service.py`
   - `july_server/app_2/service/lbs_service.py`
   - `july_server/sql/mind_seed.generated.sql`（可能转为 `mind_seed.utf8.sql`）
   - `july_client/pages/mind-recipes/*` 与 `july_client/utils/paging.js`

- **操作摘要**: 生成并建议导入种子 SQL（UTF-8 编码），在后端为文章生成 `summary` 并保存原始来源到 `origin`；删除多数静态 LBS 推荐并确保在缺失时把“华中科技大学心理健康教育中心”置于首位；前端模板改为优先显示 `summary`。
- **备份与回滚**: 若更新脚本修改了数据库，会在 `july_server` 目录下生成 `backup_mind_records_*.json` 与 `rollback_mind_records_*.sql`（如已生成，请先审查回滚文件再执行）。
- **验证要点**: 启动后端并使用 `GET /v2/mind/knowledge?page=1&size=50` 验证数据；在小程序端请清缓存并检查 `baseAPI` 是否指向本地后端。

如需我把这些文件打包或切出专门的回滚脚本/commit，告诉我你希望我接下来的操作（例如：生成 zip / 提交到 git / 还原某些文件）。
