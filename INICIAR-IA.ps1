param([string]$PastaProjeto = $env:CITIZENTECH_GENAI_PROJECT, [string]$PythonIA = $env:CITIZENTECH_GENAI_PYTHON, [switch]$Instalar)
$ErrorActionPreference = 'Stop'
if (-not $PastaProjeto) { $PastaProjeto = Join-Path $PSScriptRoot 'materiais/genai' }
$PastaProjeto = (Resolve-Path -LiteralPath $PastaProjeto).Path
if (-not $PythonIA) {
    $PythonIA = Join-Path $PastaProjeto '.venv/Scripts/python.exe'
    if (-not (Test-Path -LiteralPath $PythonIA)) {
        python -m venv (Join-Path $PastaProjeto '.venv')
        if ($LASTEXITCODE -ne 0) { throw 'Não foi possível criar o ambiente de Generative AI.' }
        $Instalar = $true
    }
}
if (-not (Test-Path -LiteralPath $PythonIA)) { throw 'O interpretador de Generative AI não existe.' }
if ($Instalar) {
    & $PythonIA -m pip install -r (Join-Path $PastaProjeto 'requirements.txt')
    if ($LASTEXITCODE -ne 0) { throw 'Falha na instalação de Generative AI.' }
}
$pathAnterior = $env:PATH
try {
    $env:PATH = (Split-Path -Parent $PythonIA) + ';' + $pathAnterior
    Write-Host 'Iniciando o projeto de Generative AI em 127.0.0.1:8765 e o modelo em 127.0.0.1:8080.'
    Write-Host 'Na primeira execução, o inicializador original baixa o modelo de aproximadamente 2,5 GB.'
    & (Join-Path $PastaProjeto 'Executar-CitizenTech.ps1')
} finally { $env:PATH = $pathAnterior }
