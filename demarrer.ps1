param([switch]$RegistreSeulement)
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
$env:PATH = "$(Join-Path $PSScriptRoot '.venv\Scripts');$env:PATH"
New-Item -ItemType Directory -Force '.runtime' | Out-Null
$env:MLFLOW_TRACKING_URI = 'http://127.0.0.1:5005'
$env:MLFLOW_DISABLE_AGENT_HINT = '1'
$env:PYTHONUNBUFFERED = '1'
$env:PYTHONIOENCODING = 'utf-8'

function Start-TPService($Name, $Port, $Arguments) {
    if (Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue) {
        throw "Le port $Port est deja utilise. Verifiez le service avant de relancer."
    }
    $process = Start-Process -FilePath $python -ArgumentList $Arguments -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput ".runtime\$Name.out.log" -RedirectStandardError ".runtime\$Name.err.log"
    $process.Id | Set-Content ".runtime\$Name.pid"
    for ($i=0; $i -lt 90; $i++) {
        Start-Sleep -Seconds 1
        if ($process.HasExited) { throw "Echec de $Name : consultez .runtime\$Name.err.log" }
        try {
            $response = Invoke-WebRequest -Uri "http://127.0.0.1:$Port/health" -TimeoutSec 2
            if ($response.StatusCode -eq 200) { Write-Host "$Name pret sur 127.0.0.1:$Port (PID $($process.Id))"; return }
        } catch { }
    }
    throw "Delai de demarrage depasse pour $Name."
}

if (-not (Test-Path '.runtime\registre.pid') -or $RegistreSeulement) {
    Start-TPService 'registre' 5005 '-m mlflow server --host 127.0.0.1 --port 5005 --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlartifacts --workers 1'
}
if (-not $RegistreSeulement) {
    Start-TPService 'automl' 8100 '-m mlflow models serve -m models:/fraude-automl@production -h 127.0.0.1 -p 8100 --env-manager local'
    Start-TPService 'manuel' 8101 '-m mlflow models serve -m models:/fraude-manuel@production -h 127.0.0.1 -p 8101 --env-manager local'
}
