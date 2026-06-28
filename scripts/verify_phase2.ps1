$ErrorActionPreference = "Stop"

Set-Location "G:\VSC projects\gameplay-automation-retroarch"

python -m pip install -r requirements.txt
python "G:\VSC projects\gameplay-automation-retroarch\src\scenarios\scripted_playback.py"

$newestLog = Get-ChildItem ".\logs" -Filter "*.jsonl" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $newestLog) {
    throw "No JSONL playback log was created."
}

Write-Host "Newest log:" $newestLog.FullName
Get-Content $newestLog.FullName
