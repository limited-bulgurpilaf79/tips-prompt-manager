param(
    [switch]$SkipLaunch
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$ReleaseDir = Join-Path $Root "release-assets"
$ExePath = Join-Path $ReleaseDir "tips-prompt-manager-v1.0.0-windows-x64.exe"
$ZipPath = Join-Path $ReleaseDir "tips-prompt-manager-v1.0.0-windows-x64.zip"

if (!(Test-Path -LiteralPath $ExePath)) {
    throw "Missing EXE: $ExePath"
}
if (!(Test-Path -LiteralPath $ZipPath)) {
    throw "Missing ZIP: $ZipPath"
}

$TempRoot = Join-Path $env:TEMP ("tips-smoke-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $TempRoot | Out-Null
try {
    Expand-Archive -LiteralPath $ZipPath -DestinationPath $TempRoot -Force
    $ExtractedExe = Get-ChildItem -LiteralPath $TempRoot -Recurse -Filter "tips-prompt-manager.exe" | Select-Object -First 1
    if ($null -eq $ExtractedExe) {
        throw "Portable ZIP does not contain tips-prompt-manager.exe"
    }

    if (!$SkipLaunch) {
        $OldDataDir = $env:TIPS_DATA_DIR
        $env:TIPS_DATA_DIR = Join-Path $TempRoot "data"
        $Process = Start-Process -FilePath $ExtractedExe.FullName -PassThru -WindowStyle Hidden
        Start-Sleep -Seconds 4
        if ($Process.HasExited) {
            throw "Smoke launch exited too early with code $($Process.ExitCode)"
        }
        Stop-Process -Id $Process.Id -Force
        if ($null -eq $OldDataDir) {
            Remove-Item Env:\TIPS_DATA_DIR -ErrorAction SilentlyContinue
        }
        else {
            $env:TIPS_DATA_DIR = $OldDataDir
        }
    }
}
finally {
    Remove-Item -LiteralPath $TempRoot -Recurse -Force -ErrorAction SilentlyContinue
}
