param([switch]$Instalar, [switch]$Visao)
$ErrorActionPreference = 'Stop'
$pythonCentral = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $pythonCentral)) {
    python -m venv (Join-Path $PSScriptRoot '.venv')
    if ($LASTEXITCODE -ne 0) { throw 'Não foi possível criar o ambiente. Instale Python 3.13.' }
    $Instalar = $true
}
Push-Location -LiteralPath $PSScriptRoot
try {
    if ($Instalar) {
        & $pythonCentral -m pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) { throw 'Falha na instalação das dependências da central.' }
    }
    if ($Visao) {
        & $pythonCentral -m pip install -r requirements-visao.txt
        if ($LASTEXITCODE -ne 0) { throw 'Falha na instalação do ambiente de Visão.' }
    }
    Write-Host 'Central: http://127.0.0.1:8840'
    Write-Host 'Use dados fictícios. A chave de revisão fica em data/chave-gestao.txt, salvo configuração por ambiente.'
    Write-Host 'Para encerrar, pressione Ctrl+C. Generative AI é iniciado separadamente com INICIAR-IA.ps1.'
    & $pythonCentral -X utf8 -m uvicorn central.app:app --host 127.0.0.1 --port 8840 --workers 1
    if ($LASTEXITCODE -ne 0) { throw 'A central foi encerrada com erro. Confira a mensagem acima.' }
} finally { Pop-Location }
