# Configuration
$Repo = "nullvoider07/macos_actuation_control"
$BinaryName = "macos-actuation.exe"

Write-Host "Checking for latest version..." -ForegroundColor Cyan

# 1. Get Latest Tag from GitHub API
try {
    $ReleaseUrl = "https://api.github.com/repos/$Repo/releases/latest"
    $LatestRelease = Invoke-RestMethod -Uri $ReleaseUrl
    $TagName = $LatestRelease.tag_name
}
catch {
    Write-Error "Failed to fetch release info. Check your internet connection."
    exit 1
}

if ([string]::IsNullOrWhiteSpace($TagName)) {
    Write-Error "Could not find latest release."
    exit 1
}

# Extract Version (Remove 'mac-v' prefix)
$Version = $TagName -replace "mac-v", ""
Write-Host "Latest Version: $Version" -ForegroundColor Green

# 2. Construct Download URL
# Pattern: macos-actuation-{VERSION}-win-x64.zip
$ZipName = "macos-actuation-$Version-win-x64.zip"
$DownloadUrl = "https://github.com/$Repo/releases/download/$TagName/$ZipName"

# 3. Download
$TempZip = "$env:TEMP\$ZipName"
Write-Host "Downloading $DownloadUrl..." -ForegroundColor Cyan
try {
    Invoke-WebRequest -Uri $DownloadUrl -OutFile $TempZip
}
catch {
    Write-Error "Download failed. Check if the asset $ZipName exists in the release."
    exit 1
}

# 4. Install
# We will install to a local folder in AppData and add to PATH
$InstallDir = "$env:LOCALAPPDATA\Programs\macos-actuation"
if (!(Test-Path -Path $InstallDir)) {
    New-Item -ItemType Directory -Path $InstallDir | Out-Null
}

Write-Host "Extracting to $InstallDir..." -ForegroundColor Cyan
Expand-Archive -Path $TempZip -DestinationPath $InstallDir -Force

# 5. Verify Binary Exists (Using the previously unused variable)
$BinaryPath = Join-Path -Path $InstallDir -ChildPath $BinaryName
if (!(Test-Path -Path $BinaryPath)) {
    Write-Warning "Installation finished, but could not find '$BinaryName' in the extraction folder."
    Write-Warning "Please check the contents of: $InstallDir"
}

# 6. Add to PATH (User Scope)
$UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($UserPath -notlike "*$InstallDir*") {
    Write-Host "Adding to PATH..." -ForegroundColor Yellow
    [Environment]::SetEnvironmentVariable("Path", "$UserPath;$InstallDir", "User")
    $env:Path += ";$InstallDir"
    Write-Host "✅ Path updated. You may need to restart your terminal." -ForegroundColor Green
} else {
    Write-Host "✅ Path already configured." -ForegroundColor Green
}

# Cleanup
Remove-Item $TempZip -Force

# Final Success Message
$CommandName = $BinaryName -replace ".exe", ""
Write-Host ""
Write-Host "🎉 Installation Complete!" -ForegroundColor Green
Write-Host "Run '$CommandName --help' to get started." -ForegroundColor Cyan