# Arranca MySQL (Docker), espera al puerto 3308 y ejecuta migraciones + Flask en el host.
# Uso (desde esta carpeta):  .\run-local.ps1
# Requisitos: Docker Desktop, Python con dependencias del map, RabbitMQ en 5672 si pruebas RPC.

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "Levantando MySQL (docker compose)..." -ForegroundColor Cyan
docker compose up -d mysql
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Esperando a que 127.0.0.1:3308 acepte conexiones..." -ForegroundColor Cyan
$deadline = (Get-Date).AddSeconds(90)
$ready = $false
while ((Get-Date) -lt $deadline) {
    try {
        $c = New-Object System.Net.Sockets.TcpClient
        $iar = $c.BeginConnect("127.0.0.1", 3308, $null, $null)
        if ($iar.AsyncWaitHandle.WaitOne(500) -and $c.Connected) {
            $c.EndConnect($iar)
            $c.Close()
            $ready = $true
            break
        }
        $c.Close()
    } catch {}
    Start-Sleep -Milliseconds 400
}
if (-not $ready) {
    Write-Host "MySQL no respondio a tiempo. Revisa: docker compose ps / docker compose logs mysql" -ForegroundColor Red
    exit 1
}

$env:FLASK_APP = "main.py"
$env:PYTHONPATH = $PSScriptRoot
$env:DATABASE_URL = "mysql+pymysql://map_user:map_pass@127.0.0.1:3308/geo_db"
$env:RABBITMQ_URL = "amqp://guest:guest@127.0.0.1:5672/"
$env:ENABLE_RABBIT_CONSUMERS = "1"
if (-not $env:FLASK_SECRET_KEY) { $env:FLASK_SECRET_KEY = "dev-local" }

Write-Host "Ejecutando migraciones..." -ForegroundColor Cyan
python -m flask db upgrade
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Iniciando API en http://127.0.0.1:8081 (Ctrl+C para salir)" -ForegroundColor Green
python -m flask run --host=0.0.0.0 --port=8081
