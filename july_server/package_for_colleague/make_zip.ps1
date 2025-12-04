# make_zip.ps1
# 在项目根（july_server）目录下运行：
# powershell -ExecutionPolicy Bypass -File .\package_for_colleague\make_zip.ps1
# 该脚本会把若干必要文件压缩为 jully_seed_package.zip（不包含 rollback/backup 文件）

$ErrorActionPreference = 'Stop'

# 让输出使用 UTF-8，避免在控制台出现乱码
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$cwd = (Get-Location).ProviderPath.TrimEnd('\')
$dest = Join-Path $cwd "july_seed_package.zip"

# 要包含的相对路径（相对于当前工作目录，即你应在 juli_server 下运行此脚本）
$filesToInclude = @(
    ".\sql\mind_seed.generated.sql",
    ".\sql\update_selected_mind.sql",
    ".\sql\update_mind_suggestions.sql",
    ".\scripts\apply_update_suggestions.py",
    ".\scripts\convert_sql_to_utf8.py",
    ".\scripts\test_mysql_connect.py"
)

# .env.example 可能在项目根或 package_for_colleague 目录中，尝试容错查找
$envCandidates = @('.\.env.example', '.\package_for_colleague\.env.example')
foreach ($e in $envCandidates) { if (Test-Path $e) { $filesToInclude += $e; break } }

$existing = @()
$missing = @()
foreach ($f in $filesToInclude) {
    if (Test-Path $f) { $existing += (Resolve-Path $f).ProviderPath }
    else { $missing += $f }
}

Write-Host "目标 zip: $dest"
if ($missing.Count -gt 0) {
    Write-Warning "下面列出的文件未找到，将不会被包含："
    $missing | ForEach-Object { Write-Host "  - $_" }
    Write-Host "如果这些文件应当存在，请先将它们放回对应位置，或手工复制文件到 zip。"
}

if ($existing.Count -eq 0) {
    Write-Error "没有可用于打包的文件，脚本退出。"
    exit 2
}

# 生成临时目录以保证 zip 结构清晰
$tmp = Join-Path $env:TEMP ("july_seed_pkg_" + (Get-Date -Format yyyyMMddHHmmss))
New-Item -Path $tmp -ItemType Directory -Force | Out-Null

foreach ($abs in $existing) {
    # 计算相对于 cwd 的相对路径（保留子目录结构）
    $rel = $abs.Substring($cwd.Length).TrimStart('\')
    $target = Join-Path $tmp $rel
    $tdir = Split-Path $target -Parent
    if (-not (Test-Path $tdir)) { New-Item -Path $tdir -ItemType Directory -Force | Out-Null }
    Copy-Item -Path $abs -Destination $target -Force
}

# 生成 zip
if (Test-Path $dest) { Remove-Item $dest -Force }
Compress-Archive -Path (Join-Path $tmp '*') -DestinationPath $dest -Force

# 清理临时目录
Remove-Item -Recurse -Force $tmp

Write-Host "已生成: $dest"
Write-Host "包含的文件:" 
$existing | ForEach-Object { Write-Host "  - $_" }

exit 0
