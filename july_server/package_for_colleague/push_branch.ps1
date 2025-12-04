<#
push_branch.ps1

作用：
- 在当前仓库（应为 juli_server 根目录）检查并移除 `.env` 的索引（不删除本地文件），把 `.env` 加入 `.gitignore`（如尚未），
- 创建一个新分支（交互式输入分支名），把指定文件/目录添加、提交并推送到远程（origin 或指定的 remote URL），
- 默认要提交的文件为 `package_for_colleague` 目录与 `README.md`；可传入额外路径作为参数。

使用方法（在 PowerShell 中，位于项目根）：
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
    .\package_for_colleague\push_branch.ps1

或传入其它要提交的文件：
    .\package_for_colleague\push_branch.ps1 .\other\path README.md

注意：
- 脚本不会读写或显示 `.env` 内容；如果 `.env` 已被提交到历史中，需另外清理历史（脚本不会自动清理历史）。
- 如果远程仓库需要凭证，HTTPS 会提示输入用户名/Token，SSH 则使用 SSH key。
#>

Param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$PathsToAdd
)

function ExecGit([string[]]$args) {
    # 使用参数数组调用 git，避免复杂字符串内的引号/转义问题
    $p = & git @args 2>&1
    $code = $LASTEXITCODE
    return @{Out=$p; Code=$code}
}

# 确认在 git repo
$inside = ExecGit(@('rev-parse', '--is-inside-work-tree'))
if ($inside.Code -ne 0 -or $inside.Out -notmatch 'true') {
    Write-Error "当前目录不是 git 仓库（请在项目根运行）。"
    exit 2
}

# 确保 .env 不会被提交
if (Test-Path .\.env) {
    # 检查是否已被 git 跟踪
    $ls = ExecGit(@('ls-files', '--error-unmatch', '.env'))
    if ($ls.Code -eq 0) {
        Write-Host ".env 当前已被 git 跟踪，将从索引移除（不会删除本地文件）..."
        ExecGit(@('rm', '--cached', '.env')) | Out-Null
        Write-Host "已从索引移除 .env"
    }
    # 确保 .gitignore 包含 .env
    $gi = Get-Content .gitignore -ErrorAction SilentlyContinue
    if ($gi -eq $null -or ($gi -notcontains '.env')) {
        Write-Host "将 .env 加入 .gitignore"
        Add-Content -Path .gitignore -Value "`n.env"
        ExecGit(@('add', '.gitignore')) | Out-Null
        ExecGit(@('commit', '-m', 'chore: add .env to .gitignore and remove from index')) | Out-Null
        Write-Host ".gitignore 更新并提交"
    }
} else {
    Write-Host ".env 文件未在项目根找到，跳过 .env 处理。"
}

# 询问远程 URL 或使用 origin
    $remote = ExecGit(@('remote', 'get-url', 'origin'))
$remoteURL = $null
if ($remote.Code -eq 0 -and $remote.Out.Trim() -ne '') {
    $remoteURL = $remote.Out.Trim()
    Write-Host "检测到 remote 'origin': $remoteURL"
    $useOrigin = Read-Host "使用现有 remote 'origin' 吗？(Y/n)"
    if ($useOrigin -eq 'n' -or $useOrigin -eq 'N') { $remoteURL = $null }
}
if (-not $remoteURL) {
    $inputUrl = Read-Host "请输入要推送的远程仓库 URL（例如 https://github.com/你的账号/仓库.git），或直接回车使用 origin（如果已配置）"
    if ($inputUrl -ne '') { $remoteURL = $inputUrl }
}

if (-not $remoteURL) {
    Write-Host "未指定远程，假设已配置名为 origin 的远程。"
} else {
    # 若 origin 未配置或被用户输入不同 URL，确保 origin 指向这个 URL
    $current = ExecGit(@('remote', 'get-url', 'origin'))
    if ($current.Code -ne 0 -or $current.Out.Trim() -ne $remoteURL) {
        Write-Host "设置 origin 为 $remoteURL"
        # 如果 origin 存在则 set-url，否则 add
        $check = ExecGit(@('remote'))
        if ($check.Out -match 'origin') {
            ExecGit(@('remote', 'set-url', 'origin', $remoteURL)) | Out-Null
        } else {
            ExecGit(@('remote', 'add', 'origin', $remoteURL)) | Out-Null
        }
    }
}

# 分支名
$defaultBranch = "feature/package-for-colleague"
$branch = Read-Host "请输入要创建并推送的新分支名（回车使用 $defaultBranch)"
if ($branch -eq '') { $branch = $defaultBranch }

# 创建并切换分支
Write-Host "创建并切换到分支 $branch"
$co = ExecGit(@('checkout', '-b', $branch))
if ($co.Code -ne 0) {
    Write-Error "无法创建或切换分支： $($co.Out)"
    exit 3
}

# 决定要 add 的路径
if (-not $PathsToAdd -or $PathsToAdd.Count -eq 0) {
    $PathsToAdd = @('.\package_for_colleague', '.\README.md')
}

# 过滤存在的路径
$toAdd = @()
foreach ($p in $PathsToAdd) {
    if (Test-Path $p) { $toAdd += $p }
}
if ($toAdd.Count -eq 0) {
    Write-Error "没有要添加的文件或目录（传入的路径不存在）。请检查后重试。"
    exit 4
}

Write-Host "将添加并提交以下路径："
$toAdd | ForEach-Object { Write-Host "  - $_" }
$confirm = Read-Host "确认要添加并提交这些文件吗？(y/N)"
if ($confirm -ne 'y' -and $confirm -ne 'Y') {
    Write-Host "取消操作"
    exit 0
}

# git add
foreach ($p in $toAdd) { ExecGit(@('add', $p)) | Out-Null }

# 查看是否有变更
$st = ExecGit(@('status', '--porcelain'))
if ($st.Out.Trim() -eq '') {
    Write-Host "没有新的变更可提交。"
} else {
    # 提交
    $commitMsg = Read-Host "输入此次提交信息（回车使用默认: 'chore(package): add package_for_colleague')"
    if ($commitMsg -eq '') { $commitMsg = 'chore(package): add package_for_colleague' }
    $cm = ExecGit(@('commit', '-m', $commitMsg))
    if ($cm.Code -ne 0) {
        Write-Error "提交失败： $($cm.Out)"
        exit 5
    } else {
        Write-Host "已提交： $commitMsg"
    }
}

# 推送到远程
if (-not $remoteURL) { $remoteURL = 'origin' }
Write-Host "开始推送到远程 $remoteURL 分支 $branch ..."
$push = ExecGit(@('push', '-u', 'origin', $branch))
if ($push.Code -ne 0) {
    Write-Error "推送失败： $($push.Out)"
    exit 6
} else {
    Write-Host "推送成功： 分支 $branch 已推到 $remoteURL"
}

Write-Host "操作完成。你可以在 GitHub 上打开 Pull Request。"
