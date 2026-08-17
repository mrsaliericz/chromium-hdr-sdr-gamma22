$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $projectRoot
try {
    & "$projectRoot\make_icon.ps1"
    python -m PyInstaller `
        --noconfirm `
        --clean `
        --onefile `
        --noconsole `
        --icon "$projectRoot\assets\gamma22.ico" `
        --add-data "$projectRoot\assets\gamma22.ico;assets" `
        --add-data "$projectRoot\assets\gamma22-disabled.ico;assets" `
        --name Gamma22Tray `
        tray_gamma22.py
}
finally {
    Pop-Location
}
