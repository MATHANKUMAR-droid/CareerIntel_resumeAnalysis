$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
if (!(Test-Path 'requirements.txt') -or !(Test-Path 'app/main.py')) {
    throw 'Run this script from the extracted CareerIntel project root.'
}
if (!(Test-Path '.venv/Scripts/python.exe')) { python -m venv .venv }
$python = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
& $python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw 'pip upgrade failed.' }
& $python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
if (!(Test-Path '.env')) { Copy-Item '.env.example' '.env' }
Start-Process 'http://127.0.0.1:8000'
& $python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
