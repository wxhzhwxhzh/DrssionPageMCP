$chromePath = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$userDataDir = "D:\chrome-mcp-dp"
$debugPort = "9223"

if (-not (Test-Path $chromePath)) {
    throw "Chrome not found: $chromePath"
}

if (-not (Test-Path $userDataDir)) {
    New-Item -ItemType Directory -Path $userDataDir -Force | Out-Null
}

$args = @(
    "--remote-debugging-port=$debugPort"
    "--user-data-dir=$userDataDir"
)

Start-Process -FilePath $chromePath -ArgumentList $args | Out-Null
Write-Output "Started Chrome with remote debugging on port $debugPort and user-data-dir $userDataDir"
