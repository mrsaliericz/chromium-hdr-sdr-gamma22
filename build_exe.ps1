$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $projectRoot
try {
    python -m PyInstaller `
        --noconfirm `
        --clean `
        --onefile `
        --name Gamma22Patcher `
        --add-data "recipes;recipes" `
        gamma22_patcher.py
}
finally {
    Pop-Location
}
