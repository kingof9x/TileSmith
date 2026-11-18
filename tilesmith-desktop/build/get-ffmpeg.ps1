# Run by the TileSmith Windows installer when the user says Yes to "Download ffmpeg now?".
# Downloads ffmpeg (free software by the FFmpeg developers, GPL) from gyan.dev and puts ffmpeg.exe in TileSmith's own
# add-ons folder (the same place as Info > Add-ons > Download ffmpeg in the app). Nothing is shipped inside TileSmith.
# Tries the "full" build first (has the HAP encoder), then "essentials". Exit code 0 = ffmpeg is ready.
param([Parameter(Mandatory = $true)][string]$Dest)
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'   # Invoke-WebRequest is much faster without the progress bar
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$tar = Join-Path $env:SystemRoot 'System32\tar.exe'
$sources = @('https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-full.7z', 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip')
New-Item -ItemType Directory -Force -Path $Dest | Out-Null
foreach ($url in $sources) {
  $tmp = Join-Path ([IO.Path]::GetTempPath()) ('tilesmith-ff-' + [guid]::NewGuid())
  New-Item -ItemType Directory -Force -Path $tmp | Out-Null
  try {
    $arc = Join-Path $tmp ([IO.Path]::GetFileName($url))
    Write-Output "Downloading $url"
    Invoke-WebRequest -Uri $url -OutFile $arc -UseBasicParsing -UserAgent 'TileSmith'
    $un = Join-Path $tmp 'x'; New-Item -ItemType Directory -Force -Path $un | Out-Null
    Write-Output 'Unpacking'
    $ok = $false
    if (Test-Path $tar) { & $tar -xf $arc -C $un 2>$null; $ok = ($LASTEXITCODE -eq 0) }
    if (-not $ok -and $arc -like '*.zip') { Expand-Archive -LiteralPath $arc -DestinationPath $un -Force; $ok = $true }
    if (-not $ok) { throw "could not unpack $arc" }
    $exe = Get-ChildItem -Path $un -Recurse -Filter 'ffmpeg.exe' | Select-Object -First 1
    if (-not $exe) { throw 'no ffmpeg.exe in the download' }
    $out = Join-Path $Dest 'ffmpeg.exe'
    Copy-Item -Force $exe.FullName $out
    & $out -hide_banner -version | Out-Null
    if ($LASTEXITCODE -ne 0) { Remove-Item -Force $out; throw 'the downloaded ffmpeg does not run' }
    Write-Output "ffmpeg is ready: $out"
    exit 0
  } catch {
    Write-Output ("Failed: " + $_.Exception.Message)
  } finally {
    Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
  }
}
exit 1
