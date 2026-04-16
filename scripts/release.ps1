param(
    [string]$Added = "",
    [string]$Fixed = "",
    [string]$Optimized = "",
    [string]$Files = "main.py"
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$changelogPath = Join-Path $projectRoot "CHANGELOG.md"
$dateText = Get-Date -Format "yyyy-MM-dd"

function Split-Items([string]$text) {
    if ([string]::IsNullOrWhiteSpace($text)) {
        return @()
    }
    return $text.Split("|") | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" }
}

function Build-Section([string]$title, [string[]]$items) {
    if ($items.Count -eq 0) {
        return ""
    }

    $lines = @("### $title", "")
    foreach ($item in $items) {
        $lines += "- $item"
    }
    $lines += ""
    return ($lines -join "`n")
}

if (-not (Test-Path $changelogPath)) {
    throw "CHANGELOG.md not found: $changelogPath"
}

$addedItems = Split-Items $Added
$fixedItems = Split-Items $Fixed
$optimizedItems = Split-Items $Optimized
$fileItems = Split-Items $Files

if ($addedItems.Count -eq 0 -and $fixedItems.Count -eq 0 -and $optimizedItems.Count -eq 0) {
    $optimizedItems = @("执行自动化打包，无功能变更")
}

if ($fileItems.Count -eq 0) {
    $fileItems = @("main.py")
}

$entryParts = @("## $dateText", "")
$entryParts += (Build-Section "新增" $addedItems)
$entryParts += (Build-Section "修复" $fixedItems)
$entryParts += (Build-Section "优化" $optimizedItems)
$entryParts += "### 影响文件"
$entryParts += ""
foreach ($file in $fileItems) {
    $entryParts += "- $file"
}
$entryParts += ""

$entryText = ($entryParts -join "`n").TrimEnd()

Add-Content -Path $changelogPath -Value "`n`n$entryText"
Write-Host "CHANGELOG updated for $dateText"

Push-Location $projectRoot
try {
    pyinstaller --onefile --windowed --name "MortarAid" --icon=img/icon.ico .\main.py
}
finally {
    Pop-Location
}
