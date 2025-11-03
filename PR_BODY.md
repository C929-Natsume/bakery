PR 标题（建议）：

feat(mind): 扩充“心灵配方”正文（600–800 字），种子脚本/API 后备使用生成器，前端用 rich-text 渲染

PR 描述（可直接复制到 GitHub PR body）：

改动概览

本次提交将“心灵配方”功能从原先的占位文本扩展为详尽、分段、可操作性的心理科普条目（目标 600–800 字），并对前后端做了配套改造：

修改/新增文件（主要影响项）
- `july_server/app/lib/mind_content_generator.py` — 新增：内容生成器模块，用于基于 title/tags/source 合成结构化正文（含参考链接映射），仅用于开发/种子场景。
- `july_server/scripts/seed_mind.py` — 修改：种子脚本在写入 DB 前调用生成器并改为 update-on-exist（会覆盖已存在条目的 content 字段），使得运行一次 seed 即可批量把数据库内容扩充为详尽正文。
- `july_server/sql/mind_seed.sql` — 修改：加入说明（建议使用脚本生成扩写内容）；并把首批 INSERT 的 content 字段更新为扩写文本（历史备份用途）。
- `july_server/app/api/v2/mind.py` — 修改：引入生成器并在静态回退 `_KNOWLEDGE` 上扩写 content，保证 DB 不可用时 API 的回退也有详尽正文；并确保 detail 接口显式返回 `content` 字段。
- `july_client/pages/mind-recipes/detail.wxml` — 修改：正文渲染由 plain text 改为 `<rich-text nodes="{{richNodes}}">`，以稳定地按段落展示。
- `july_client/pages/mind-recipes/detail.js` — 修改：加载详情时把 `item.content` 按双换行/单换行拆成段落，生成 `richNodes`；目前不在文本中插入缩进，缩进建议用 CSS 控制。

必要的运行步骤（给开发/运维的人）

1) 拉取并检出分支（假设分支名为 `Func3`）：

```powershell
git fetch origin
git checkout -b Func3 origin/Func3
```

2) 进入后端并激活虚拟环境（项目采用 `.venv` 的情况）：

```powershell
cd 'C:\Users\lyy\Desktop\bakery-Func1AndFunc2\july_server'
& .\.venv\Scripts\Activate.ps1
# 若仓库没有 .venv，可用 python -m venv .venv 创建后激活
```

3) 安装依赖（仅首次或当依赖变更时）：

```powershell
pip install -r requirements.txt
# 如缺少 dotenv： pip install python-dotenv
```

4) 配置环境变量（若使用真实 LBS 或非本地 DB）：
- `WEIXIN_LBS_KEY` / `AMAP_LBS_KEY`（可选，若需要真实附近检索）
- 数据库连接（比如 `DATABASE_URL` 或项目里实际读取的 env 名称）

PowerShell 临时示例：

```powershell
$env:WEIXIN_LBS_KEY = "<your_tencent_key>"
$env:AMAP_LBS_KEY = "<your_amap_key>"
$env:DATABASE_URL = "mysql://user:pass@127.0.0.1:3306/july_db"
```

5) 运行种子脚本（会覆盖已有条目的 content 字段为扩写内容）：

```powershell
python -m scripts.seed_mind
# 预期输出：mind_knowledge seeded. inserted=0  （inserted=0 表示更新覆盖已有条目）
```

6) 启动后端服务并验证 API：

```powershell
python .\starter.py
# 验证示例：
Invoke-RestMethod -Uri "http://127.0.0.1:8000/v2/mind/knowledge?page=1&size=6" -Method GET | ConvertTo-Json -Depth 6
Invoke-RestMethod -Uri "http://127.0.0.1:8000/v2/mind/knowledge/<ID>" -Method GET | ConvertTo-Json -Depth 6
```

检查点：detail 接口返回的 JSON 应包含 `content` 字段，且文本已按段落分段并在结尾包含“参考与延伸阅读：”的链接或说明。

7) 前端（微信小程序）验证：
- 在微信开发者工具打开 `july_client`，执行“清缓存并重新编译”。
- 打开“心灵配方”详情页，检查正文是否按段落显示（rich-text）。

简短的变更影响

- 后端：`scripts/seed_mind.py` 会在运行时覆盖 `mind_knowledge.content` 字段（以生成器输出为准）。这意味着开发环境运行一次 seed 即可同步全部详尽正文。请在生产环境谨慎运行此脚本（建议仅在 dev/test 环境自动运行）。
- API 后备：当 DB 不可用或回退使用静态数据时，`app/api/v2/mind.py` 会用生成器扩写 `_KNOWLEDGE` 中的 content，保证回退文本详尽。
- 前端：详情页改为使用 `rich-text` 渲染段落（兼容、显示更好），并在客户端把 `content` 按空行分段生成 `richNodes`。

关于「把我之前提交的直接改了还是不改另外提交」与合并策略

- 合并行为说明：将本分支（Func3）合并到 `main` 时，Git 会把本分支的提交（你当前的修改）按时间顺序合并到目标分支；不会“改写”你之前已推到远端的历史提交（除非你使用了 rebase/force-push 改写历史）。
- 具体情况：
  - 若你的改动已经以提交的形式存在于 `Func3`，合并该分支会把这些提交一并合并到 `main`（这是标准、安全的做法）。
  - 如果你想把这些改动“替换”为另一套提交（例如合并前想清理 commit、压缩、改写提交信息），可以在本地做一个交互式 rebase 并强推（force push），但这会改写远端分支历史，可能会影响正在基于该分支开发的同事。
- 推荐做法（团队安全）：
  1. 保持当前提交历史不变，向 `main` 发起 PR，由 reviewer 审核并合并（合并方式可选：Merge commit / Squash and merge / Rebase and merge）。
  2. 若想要更清晰的 commit 历史，先在本地用 `git rebase -i` 整理提交，然后在 push 前通知相关同事（会需要 force push，并可能导致同事需要 reset/重新基于新分支工作）。

团队是否可以“直接把这个分支合并到他们那儿”？

- 是的，如果同事从远端检出 `Func3`（或你把分支推到 origin 并发 PR），他们可以直接合并该分支到目标分支（`main` 或其它开发分支），前提是：
  - 没有冲突（或冲突已解决）
  - 团队的合并/审批流程允许（例如需要通过 CI / 审核）
- 合并后，目标分支就会包含你所有修改；不会额外删除别人的改动，除非存在冲突并在合并时被误解决。

PR Body（建议直接粘贴到 GitHub）：

---

（用上面“PR 描述（可直接复制）”部分内容）

---

如何我可以进一步帮忙

- 我可以把上面 PR 描述写入仓库根的 `PR_BODY.md`（已完成），也可以：
  - 帮你在远端创建 PR（需要你在本地 push `Func3` 到远端，或授权我远端操作权限）
  - 帮你把 README 增加一小节说明（包含上面运行步骤）并提交为一个小 PR

如果你希望我直接创建远端 PR，请先执行：

```powershell
# 确保本地分支已 commit
git push -u origin Func3
```

然后你可以在浏览器到 GitHub 页面创建 PR，或使用 gh CLI：

```powershell
# 使用 GitHub CLI 创建 PR（会打开交互或直接创建）
gh pr create --base main --head Func3 --title "feat(mind): 扩充心灵配方正文" --body-file PR_BODY.md
```

（前提：本机已安装并登录 gh CLI）

---

我已经把这份 PR 描述写入仓库：`PR_BODY.md`，你可以直接在 GitHub 创建 PR 并将该文件内容粘贴为 PR body，或用 `gh pr create --body-file PR_BODY.md` 直接创建。

需要我现在替你把远端 PR 创建好，还是你先 push 分支并在 GitHub 上点击创建（我可以在 PR 文案上再帮你润色）？
