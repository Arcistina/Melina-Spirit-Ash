param([string]$Zig = 'zig')
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$taskVendor = Join-Path $PSScriptRoot 'third_party\minhook'
$taskOutput = Join-Path $PSScriptRoot 'out'
New-Item -ItemType Directory -Path $taskOutput -Force | Out-Null
& $Zig cc -target x86_64-windows-gnu -O2 -s route_test.c -o (Join-Path $taskOutput 'route_test.exe')
if ($LASTEXITCODE -ne 0) { throw 'Contract test compilation failed' }
& (Join-Path $taskOutput 'route_test.exe')
if ($LASTEXITCODE -ne 0) { throw 'Contract test failed' }
& $Zig cc -target x86_64-windows-gnu -O2 -s -shared -DUNICODE -D_UNICODE -I (Join-Path $taskVendor 'include') -I (Join-Path $taskVendor 'src') loader.c (Join-Path $taskVendor 'src\buffer.c') (Join-Path $taskVendor 'src\hook.c') (Join-Path $taskVendor 'src\trampoline.c') (Join-Path $taskVendor 'src\hde\hde64.c') -o (Join-Path $taskOutput 'MelinaIcons.dll') -lbcrypt
if ($LASTEXITCODE -ne 0) { throw 'Icon helper compilation failed' }
