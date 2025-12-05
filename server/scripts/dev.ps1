<#
One-click local dev helper for server (Windows PowerShell)

Usage examples:
  # 仅启动（无 SocketIO）
  .\scripts\dev.ps1

  # 启动并启用 SocketIO
  .\scripts\dev.ps1 -WithSocket

  # 先尝试导入数据库（需要 mysql.exe 可用）再启动（无 SocketIO）
  .\scripts\dev.ps1 -ImportDb

  # 指定 mysql.exe 路径导入
  .\scripts\dev.ps1 -ImportDb -MysqlPath "C:\\Program Files\\MySQL\\MySQL Server 8.0\\bin\\mysql.exe"

Notes:
- 读取 .env（根目录）中的 APP_HOST/APP_PORT/APP_RELOAD 与 DB_* 配置。
- 如未安装 mysql CLI，脚本会给出 Workbench 导入提示，不会中断。
#>

param(
  [switch]$WithSocket = $false,
  [switch]$ImportDb   = $false,
  [string]$MysqlPath  = "",
  [string]$SqlFile    = "sql\\july_complete_final.sql"
)

$ErrorActionPreference = 'Stop'

function Resolve-RepoRoot {
  $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
  return (Resolve-Path (Join-Path $scriptDir '..')).Path
}

function Read-DotEnv([string]$envPath) {
  $map = @{}
  if (Test-Path $envPath) {
    Get-Content $envPath | ForEach-Object {
      $line = $_.Trim()
      if ($line -eq '' -or $line.StartsWith('#')) { return }
      $kv = $line -split '=', 2
      if ($kv.Count -eq 2) { $map[$kv[0]] = $kv[1] }
    }
  }
  return $map
}

function New-Venv([string]$root) {
  $venvAct = Join-Path $root '.venv\\Scripts\\Activate.ps1'
  if (-not (Test-Path $venvAct)) {
    Write-Host '[+] Creating virtual environment (.venv)'
    python -m venv (Join-Path $root '.venv')
  }
  Write-Host '[+] Activating virtual environment'
  . $venvAct
}

function Install-Dependencies([string]$root) {
  Write-Host '[+] Installing dependencies via pip'
  pip install -r (Join-Path $root 'requirements.txt')
}

function Import-Database([hashtable]$envMap, [string]$root, [string]$sqlFile, [string]$mysqlPath) {
  $dbHost = $envMap['DB_HOST']; if (-not $dbHost) { $dbHost = '127.0.0.1' }
  $dbPort = $envMap['DB_PORT']; if (-not $dbPort) { $dbPort = '3306' }
  $dbUser = $envMap['DB_USER']; if (-not $dbUser) { $dbUser = 'root' }
  $dbPass = $envMap['DB_PASSWORD']; if (-not $dbPass) { $dbPass = '' }
  $dbName = $envMap['DB_NAME']; if (-not $dbName) { $dbName = 'july' }

  $sqlAbs = Resolve-Path (Join-Path $root $sqlFile)
  if (-not (Test-Path $sqlAbs)) {
    Write-Warning "[!] SQL file not found: $sqlAbs"
    return
  }

  $mysqlExe = $null
  if ($mysqlPath -and (Test-Path $mysqlPath)) { $mysqlExe = $mysqlPath }
  else {
    try { $cmd = Get-Command mysql -ErrorAction Stop; $mysqlExe = $cmd.Source } catch { $mysqlExe = $null }
  }

  if (-not $mysqlExe) {
    Write-Warning '[!] mysql.exe not found in PATH. Skipping automatic import.'
    Write-Host '    提示：'
    Write-Host '    1) 可使用 MySQL Workbench -> Server -> Data Import -> Import from Self-Contained File 选择 SQL 并导入数据库 "july"。'
    Write-Host '    2) 或提供 mysql.exe 路径重新执行：'
    Write-Host '       .\\scripts\\dev.ps1 -ImportDb -MysqlPath "C:\\Program Files\\MySQL\\MySQL Server 8.0\\bin\\mysql.exe"'
    return
  }

  Write-Host "[+] Importing database via: $mysqlExe"
  # 使用 cmd /c 以便处理输入重定向 <
  $importCmd = '"' + $mysqlExe + '" -u ' + $dbUser + ' -p' + $dbPass + ' -h ' + $dbHost + ' -P ' + $dbPort + ' ' + $dbName + ' < ' + '"' + $sqlAbs + '"'
  cmd /c $importCmd
  Write-Host '[+] Database import completed.'
}

function Start-Server([switch]$withSocket, [hashtable]$envMap, [string]$root) {
  $appHost = if ($envMap['APP_HOST']) { $envMap['APP_HOST'] } else { '0.0.0.0' }
  $appPort = if ($envMap['APP_PORT']) { [int]$envMap['APP_PORT'] } else { 5000 }
  $debug = if ($envMap['APP_RELOAD']) { $envMap['APP_RELOAD'].ToLower() -in @('1','true','yes','on') } else { $true }

  $py = if ($withSocket) { 'starter.py' } else { 'starter_no_socketio.py' }
  Write-Host ("[+] Starting server ({0}) on http://{1}:{2}  (debug={3})" -f $py, $appHost, $appPort, $debug)
  python (Join-Path $root $py)
}

# --- Main ---
$root = Resolve-RepoRoot
Set-Location $root

$envMap = Read-DotEnv (Join-Path $root '.env')

New-Venv -root $root
Install-Dependencies -root $root

if ($ImportDb) {
  Import-Database -envMap $envMap -root $root -sqlFile $SqlFile -mysqlPath $MysqlPath
}

Start-Server -withSocket:$WithSocket -envMap $envMap -root $root
