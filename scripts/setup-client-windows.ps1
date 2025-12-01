# setup-client-windows.ps1 - prepara entorno cliente Windows (PowerShell)
param()

$repo = Split-Path -Parent $MyInvocation.MyCommand.Path\..\
Set-Location -Path $repo

if (-Not (Test-Path .venv)) {
    python -m venv .venv
}

Write-Host "Activando entorno virtual"
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

Write-Host "Listo. Para ejecutar (PowerShell):"
Write-Host "$env:DB_HOST = '10.0.2.15'"
Write-Host "$env:PRINT_SERVER_URL = 'http://10.0.2.15:5000'"
Write-Host "python main.py"
