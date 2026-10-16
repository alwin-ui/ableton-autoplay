# Installs the AutoPlay control surface script into every Ableton Live
# User Library found on this PC. Run via "Install AutoPlay (Windows).bat".
$ErrorActionPreference = 'Stop'

$RepoZip = 'https://github.com/alwin-ui/ableton-autoplay/archive/refs/heads/main.zip'
$Here = $PSScriptRoot

# ---- find the script files ----------------------------------------------------
if (Test-Path (Join-Path $Here 'AutoPlay\__init__.py')) {
    $Src = Join-Path $Here 'AutoPlay'                     # release zip
} elseif (Test-Path (Join-Path $Here '..\__init__.py')) {
    $Src = (Resolve-Path (Join-Path $Here '..')).Path      # repo clone
} else {
    $Tmp = Join-Path $env:TEMP ('autoplay-' + [guid]::NewGuid())
    New-Item -ItemType Directory -Path $Tmp | Out-Null
    Write-Host 'Downloading AutoPlay...'
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Invoke-WebRequest -Uri $RepoZip -OutFile (Join-Path $Tmp 'src.zip') -UseBasicParsing
    Expand-Archive (Join-Path $Tmp 'src.zip') -DestinationPath $Tmp
    $Src = (Get-ChildItem $Tmp -Directory | Select-Object -First 1).FullName
}

# ---- find Live's User Library (it can be moved in Settings > Library) --------
$Libs = @()
$PrefsRoot = Join-Path $env:APPDATA 'Ableton'
if (Test-Path $PrefsRoot) {
    Get-ChildItem $PrefsRoot -Directory -Filter 'Live *' | ForEach-Object {
        $cfg = Join-Path $_.FullName 'Preferences\Library.cfg'
        if (Test-Path $cfg) {
            try {
                [xml]$x = Get-Content $cfg -Raw
                $p = @($x.Ableton.ContentLibrary.UserLibrary.LibraryProject)[0]
                $path = $p.ProjectPath.Value
                $name = $p.ProjectName.Value
                if (-not $name) { $name = 'User Library' }
                if ($path) { $Libs += (Join-Path $path $name) }
            } catch { }
        }
    }
}
if ($Libs.Count -eq 0) {
    $Libs += Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'Ableton\User Library'
}

# ---- install -------------------------------------------------------------------
$installed = $false
foreach ($lib in ($Libs | Select-Object -Unique)) {
    $dest = Join-Path $lib 'Remote Scripts\AutoPlay'
    try {
        New-Item -ItemType Directory -Force -Path $dest | Out-Null
        Copy-Item (Join-Path $Src '__init__.py'), (Join-Path $Src 'AutoPlay.py') $dest -Force
        Remove-Item (Join-Path $dest '__pycache__') -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "Installed to: $dest"
        $installed = $true
    } catch {
        Write-Host "Could not write to: $dest"
    }
}

Write-Host ''
if ($installed) {
    Write-Host 'Done! Now:'
    Write-Host '  1. Restart Ableton Live.'
    Write-Host "  2. Settings > Link, Tempo & MIDI > pick 'AutoPlay' in an empty Control Surface slot."
    Write-Host '  3. Launch a scene - the rest plays automatically.'
} else {
    Write-Host 'Install failed - see messages above.'
    exit 1
}
