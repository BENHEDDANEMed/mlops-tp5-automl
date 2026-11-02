$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
foreach ($name in @('automl', 'manuel', 'registre')) {
    $pidFile = ".runtime\$name.pid"
    if (Test-Path $pidFile) {
        $servicePid = [int](Get-Content $pidFile)
        $process = Get-CimInstance Win32_Process -Filter "ProcessId=$servicePid"
        if ($process -and $process.CommandLine -like '*mlflow*' -and $process.ExecutablePath -like "$PSScriptRoot\*") {
            # taskkill /T termine aussi les travailleurs HTTP crees par MLflow.
            taskkill /PID $servicePid /T /F | Out-Null
        }
        Remove-Item -LiteralPath $pidFile
    }
}
Write-Host 'Services du TP5 arretes.'
