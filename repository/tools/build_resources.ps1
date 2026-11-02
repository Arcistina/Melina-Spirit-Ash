param(
    [string]$Python = 'python',
    [Parameter(Mandatory = $true)][string]$Witchy,
    [string]$IconDll = '',
    [string]$Zig = 'zig'
)
$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $PSScriptRoot
$taskWitchy = (Resolve-Path -LiteralPath $Witchy).Path
$taskAcceptedDll = if ($IconDll) { (Resolve-Path -LiteralPath $IconDll).Path } else { '' }
for ($taskAncestor = Get-Item -LiteralPath $taskRoot; $null -ne $taskAncestor; $taskAncestor = $taskAncestor.Parent) {
    if (Test-Path -LiteralPath (Join-Path $taskAncestor.FullName 'eldenring.exe')) {
        throw 'Use a development checkout outside the original game directory.'
    }
}
Push-Location -LiteralPath $taskRoot
try {
    & $Python (Join-Path $PSScriptRoot 'build_melina_params.py')
    if ($LASTEXITCODE -ne 0) { throw 'Parameter preparation failed' }
    $taskNames = @('NpcParam','NpcThinkParam','BuddyParam','EquipParamGoods','SpEffectParam','ShopLineupParam')
    $taskParamXml = $taskNames | ForEach-Object { Join-Path $taskRoot "work\melina-build\regulation-bin\$_.param.xml" }
    & $taskWitchy -p -r @taskParamXml
    if ($LASTEXITCODE -ne 0) { throw 'Parameter repack failed' }
    & $Python (Join-Path $PSScriptRoot 'check_param_row_bytes.py')
    if ($LASTEXITCODE -ne 0) { throw 'Original parameter rows changed' }
    $taskBinder = Join-Path $taskRoot 'work\melina-build\regulation-bin\_witchy-bnd4.xml'
    [xml]$taskManifest = Get-Content -LiteralPath $taskBinder -Raw
    if ($taskManifest.bnd4.version -ne '11730034') { throw 'Unsupported parameter binder version' }
    $taskManifest.bnd4.filename = 'melina_param.bnd.dcx'
    if ($taskManifest.bnd4.game) { [void]$taskManifest.bnd4.RemoveChild($taskManifest.bnd4.SelectSingleNode('game')) }
    $taskManifest.Save($taskBinder)
    & $taskWitchy -p -r -b (Join-Path $taskRoot 'work\melina-build\regulation-bin')
    if ($LASTEXITCODE -ne 0) { throw 'Parameter binder repack failed' }
    & $Python (Join-Path $PSScriptRoot 'finalize_regulation.py')
    if ($LASTEXITCODE -ne 0) { throw 'Regulation encryption failed' }

    & $Python (Join-Path $PSScriptRoot 'build_item_text.py')
    if ($LASTEXITCODE -ne 0) { throw 'Text preparation failed' }
    $taskStems = @('item','item_dlc01','item_dlc02')
    $taskFmgXml = foreach ($taskStem in $taskStems) {
        foreach ($taskName in @('GoodsName','GoodsInfo','GoodsInfo2','GoodsCaption')) {
            Join-Path $taskRoot "work\melina-msg\$taskStem-msgbnd-dcx\$taskName.fmg.xml"
        }
    }
    & $taskWitchy -p -r @taskFmgXml
    if ($LASTEXITCODE -ne 0) { throw 'FMG repack failed' }
    $taskTextDirs = $taskStems | ForEach-Object { Join-Path $taskRoot "work\melina-msg\$_-msgbnd-dcx" }
    & $taskWitchy -p -r @taskTextDirs
    if ($LASTEXITCODE -ne 0) { throw 'Message binder repack failed' }
    $taskOutput = Join-Path $taskRoot 'build\melina_ashes\mod'
    $taskMsgOutput = Join-Path $taskOutput 'msg\zhocn'
    New-Item -ItemType Directory -Path $taskMsgOutput -Force | Out-Null
    foreach ($taskStem in $taskStems) {
        Copy-Item -LiteralPath (Join-Path $taskRoot "work\melina-msg\$taskStem.msgbnd.dcx") -Destination $taskMsgOutput
    }

    if (-not $taskAcceptedDll) {
        Push-Location -LiteralPath $taskRoot
        try { & (Join-Path $taskRoot 'src\melina_icons\build_windows.ps1') -Zig $Zig }
        finally { Pop-Location }
        $taskAcceptedDll = Join-Path $taskRoot 'src\melina_icons\out\MelinaIcons.dll'
        if (-not (Test-Path -LiteralPath $taskAcceptedDll -PathType Leaf)) { throw 'Icon helper build failed' }
    }
    & $Python (Join-Path $PSScriptRoot 'publish_ui.py') --dll $taskAcceptedDll
    if ($LASTEXITCODE -ne 0) { throw 'Custom UI publication failed' }
    Write-Output "Built local resources under $taskOutput. No installation or game launch was performed."
}
finally { Pop-Location }
