[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'Medium')]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('Chrome', 'Edge')]
    [string]$Browser,

    [string]$ExecutablePath,

    [string]$ProfileDirectory,

    [switch]$Unregister,

    [switch]$NoOpenSettings
)

$ErrorActionPreference = 'Stop'

if ($Browser -eq 'Edge') {
    $applicationName = 'Edge Gamma 2.2'
    $applicationKey = 'EdgeGamma22'
    $urlProgId = 'EdgeGamma22URL'
    $htmlProgId = 'EdgeGamma22HTML'
} else {
    $applicationName = 'Chrome Gamma 2.2'
    $applicationKey = 'ChromeGamma22'
    $urlProgId = 'ChromeGamma22URL'
    $htmlProgId = 'ChromeGamma22HTML'
}

$classesRoot = 'HKCU:\Software\Classes'
$applicationRoot = "HKCU:\Software\$applicationKey"
$capabilitiesRoot = "$applicationRoot\Capabilities"
$registeredApplications = 'HKCU:\Software\RegisteredApplications'

function Ensure-RegistryKey {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        New-Item -Path $Path | Out-Null
    }
}

function Set-RegistryString {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [string]$Name,
        [AllowEmptyString()][string]$Value
    )

    Ensure-RegistryKey -Path $Path
    if ([string]::IsNullOrEmpty($Name)) {
        Set-Item -LiteralPath $Path -Value $Value
    } else {
        New-ItemProperty -LiteralPath $Path -Name $Name -Value $Value `
            -PropertyType String -Force | Out-Null
    }
}

if ($Unregister) {
    $userChoicePaths = @(
        'HKCU:\Software\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice',
        'HKCU:\Software\Microsoft\Windows\Shell\Associations\UrlAssociations\https\UserChoice',
        'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\.htm\UserChoice',
        'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\.html\UserChoice',
        'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\.shtml\UserChoice'
    )

    $activeProgIds = foreach ($path in $userChoicePaths) {
        if (Test-Path -LiteralPath $path) {
            (Get-ItemProperty -LiteralPath $path -ErrorAction SilentlyContinue).ProgId
        }
    }

    if (($activeProgIds -contains $urlProgId) -or
        ($activeProgIds -contains $htmlProgId)) {
        throw "$applicationName is still selected as a default app. Select another browser in Windows Settings first, then run -Unregister again."
    }

    if ($PSCmdlet.ShouldProcess($applicationName, 'Remove per-user browser registration')) {
        foreach ($path in @(
            "$classesRoot\$urlProgId",
            "$classesRoot\$htmlProgId",
            $applicationRoot
        )) {
            if (Test-Path -LiteralPath $path) {
                Remove-Item -LiteralPath $path -Recurse -Force
            }
        }

        if (Test-Path -LiteralPath $registeredApplications) {
            Remove-ItemProperty -LiteralPath $registeredApplications `
                -Name $applicationName -ErrorAction SilentlyContinue
        }

        Write-Host "$applicationName registration removed."
    }
    return
}

if ([string]::IsNullOrWhiteSpace($ExecutablePath)) {
    throw '-ExecutablePath is required unless -Unregister is used.'
}
if (-not (Test-Path -LiteralPath $ExecutablePath -PathType Leaf)) {
    throw "Browser executable not found: $ExecutablePath"
}

$resolvedExecutable = (Resolve-Path -LiteralPath $ExecutablePath).Path
if ([System.IO.Path]::GetExtension($resolvedExecutable) -ne '.exe') {
    throw "Browser executable must be an .exe file: $resolvedExecutable"
}

$launchCommand = '"' + $resolvedExecutable + '"'
if (-not [string]::IsNullOrWhiteSpace($ProfileDirectory)) {
    $resolvedProfile = [System.IO.Path]::GetFullPath($ProfileDirectory)
    $launchCommand += ' --user-data-dir="' + $resolvedProfile + '"'
    $launchCommand += ' --no-first-run --no-default-browser-check'
}
$launchCommand += ' "%1"'
$icon = "$resolvedExecutable,0"

if ($PSCmdlet.ShouldProcess($applicationName, 'Register as a per-user default-browser candidate')) {
    Set-RegistryString -Path "$classesRoot\$urlProgId" `
        -Value "$applicationName URL"
    Set-RegistryString -Path "$classesRoot\$urlProgId" `
        -Name 'URL Protocol' -Value ''
    Set-RegistryString -Path "$classesRoot\$urlProgId\DefaultIcon" `
        -Value $icon
    Set-RegistryString -Path "$classesRoot\$urlProgId\shell\open\command" `
        -Value $launchCommand

    Set-RegistryString -Path "$classesRoot\$htmlProgId" `
        -Value "$applicationName HTML Document"
    Set-RegistryString -Path "$classesRoot\$htmlProgId\DefaultIcon" `
        -Value $icon
    Set-RegistryString -Path "$classesRoot\$htmlProgId\shell\open\command" `
        -Value $launchCommand

    Set-RegistryString -Path $capabilitiesRoot `
        -Name 'ApplicationName' -Value $applicationName
    Set-RegistryString -Path $capabilitiesRoot `
        -Name 'ApplicationDescription' `
        -Value 'Patched portable Chromium browser with SDR gamma 2.2 and native HDR/WCG support'
    Set-RegistryString -Path $capabilitiesRoot `
        -Name 'ApplicationIcon' -Value $icon
    Set-RegistryString -Path "$capabilitiesRoot\URLAssociations" `
        -Name 'http' -Value $urlProgId
    Set-RegistryString -Path "$capabilitiesRoot\URLAssociations" `
        -Name 'https' -Value $urlProgId
    Set-RegistryString -Path "$capabilitiesRoot\FileAssociations" `
        -Name '.htm' -Value $htmlProgId
    Set-RegistryString -Path "$capabilitiesRoot\FileAssociations" `
        -Name '.html' -Value $htmlProgId
    Set-RegistryString -Path "$capabilitiesRoot\FileAssociations" `
        -Name '.shtml' -Value $htmlProgId
    Set-RegistryString -Path $registeredApplications `
        -Name $applicationName -Value "Software\$applicationKey\Capabilities"

    Write-Host "$applicationName registered for the current Windows user."
    Write-Host "Launch command: $launchCommand"
    Write-Host 'Windows requires you to confirm the final choice in Default apps.'

    if (-not $NoOpenSettings) {
        $encodedName = [System.Uri]::EscapeDataString($applicationName)
        Start-Process "ms-settings:defaultapps?registeredAppUser=$encodedName"
    }
}
