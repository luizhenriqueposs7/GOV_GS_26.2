param(
    [switch]$Celular,
    [ValidatePattern('^[A-Za-z0-9.!#$%&+_=/^{}~-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+$')][string]$Email,
    [ValidateRange(5,180)][int]$Minutos=60
)
$ErrorActionPreference='Stop'
if ($Celular -and -not $Email) { throw 'Para abrir o acesso protegido, use -Celular -Email seu-email.' }
$runtimePreparacao=Join-Path $PSScriptRoot 'data/runtime'
New-Item -ItemType Directory -Path $runtimePreparacao -Force | Out-Null
$pythonPreparacao=Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $pythonPreparacao)) { throw 'Prepare o ambiente antes com INICIAR.ps1 -Instalar -Visao.' }
$hostPreparacao=(Get-Command pwsh -ErrorAction Stop).Source
@{ok=$false;status='preparando';data=[DateTimeOffset]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $runtimePreparacao 'prontidao.json') -Encoding utf8

function Testar-RespostaPreparacao([string]$Url) {
    try { return (Invoke-WebRequest -Uri $Url -TimeoutSec 3).StatusCode -eq 200 } catch { return $false }
}
function Iniciar-ServicoPreparacao([string]$Script,[string[]]$Parametros,[string]$Nome) {
    $comandoPreparacao=@('-NoProfile','-File',('"'+(Join-Path $PSScriptRoot $Script)+'"'))+$Parametros
    return Start-Process -FilePath $hostPreparacao -ArgumentList $comandoPreparacao -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $runtimePreparacao ($Nome+'-out.log')) -RedirectStandardError (Join-Path $runtimePreparacao ($Nome+'-err.log')) -PassThru
}
function Aguardar-ServicoPreparacao([string]$Url,$Processo,[int]$Segundos) {
    $limitePreparacao=[DateTimeOffset]::UtcNow.AddSeconds($Segundos)
    while ([DateTimeOffset]::UtcNow -lt $limitePreparacao) {
        if (Testar-RespostaPreparacao $Url) { return }
        $Processo.Refresh()
        if ($Processo.HasExited) { throw "O serviço foi encerrado durante a preparação. Consulte os logs em data/runtime. Endereço: $Url" }
        Start-Sleep -Seconds 2
    }
    throw "O serviço não ficou pronto no tempo esperado. Consulte data/runtime. Endereço: $Url"
}

try {
    if (-not (Testar-RespostaPreparacao 'http://127.0.0.1:8840/api/status')) {
        Write-Output 'Iniciando a central…'
        $processoPreparacaoCentral=Iniciar-ServicoPreparacao 'INICIAR.ps1' @() 'preparacao-central'
        @{url='http://127.0.0.1:8840';processo=$processoPreparacaoCentral.Id;origem='PREPARAR.ps1'} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $runtimePreparacao 'central-processo.json') -Encoding utf8
        Aguardar-ServicoPreparacao 'http://127.0.0.1:8840/api/status' $processoPreparacaoCentral 40
    } else { Write-Output 'Central já está respondendo.' }

    $iaPreparacaoAtiva=Testar-RespostaPreparacao 'http://127.0.0.1:8765/'
    $modeloPreparacaoAtivo=Testar-RespostaPreparacao 'http://127.0.0.1:8080/health'
    if (-not $iaPreparacaoAtiva -or -not $modeloPreparacaoAtivo) {
        if ($iaPreparacaoAtiva -or $modeloPreparacaoAtivo) { throw 'Generative AI está parcialmente iniciado. Encerre a inicialização anterior de IA e execute PREPARAR.ps1 novamente; nenhum processo desconhecido foi encerrado.' }
        $pastaPreparacaoIA=$env:CITIZENTECH_GENAI_PROJECT
        $pythonPreparacaoIA=$env:CITIZENTECH_GENAI_PYTHON
        $arquivoPreparacaoConfig=Join-Path $PSScriptRoot 'data/preparacao-local.json'
        if (Test-Path -LiteralPath $arquivoPreparacaoConfig) {
            $configPreparacao=Get-Content -Raw -LiteralPath $arquivoPreparacaoConfig | ConvertFrom-Json
            if (-not $pastaPreparacaoIA) { $pastaPreparacaoIA=$configPreparacao.PastaProjetoIA }
            if (-not $pythonPreparacaoIA) { $pythonPreparacaoIA=$configPreparacao.PythonIA }
        }
        if (-not $pastaPreparacaoIA) { $pastaPreparacaoIA=Join-Path $PSScriptRoot 'materiais/genai' }
        if (-not $pythonPreparacaoIA) { $pythonPreparacaoIA=Join-Path $pastaPreparacaoIA '.venv/Scripts/python.exe' }
        foreach ($arquivoPreparacao in @($pythonPreparacaoIA,(Join-Path $pastaPreparacaoIA '.runtime/Qwen3-4B-Instruct-2507-Q4_K_M.gguf'),(Join-Path $pastaPreparacaoIA '.runtime/llama/llama-server.exe'))) {
            if (-not (Test-Path -LiteralPath $arquivoPreparacao)) { throw 'O ambiente de IA ainda não está preparado. Execute INICIAR-IA.ps1 com os caminhos corretos antes da gravação. Consulte README.md.' }
        }
        Write-Output 'Iniciando Generative AI com o modelo já instalado…'
        $parametrosPreparacaoIA=@('-PastaProjeto',('"'+$pastaPreparacaoIA+'"'),'-PythonIA',('"'+$pythonPreparacaoIA+'"'))
        $processoPreparacaoIA=Iniciar-ServicoPreparacao 'INICIAR-IA.ps1' $parametrosPreparacaoIA 'preparacao-ia'
        @{url='http://127.0.0.1:8765';pid=$processoPreparacaoIA.Id;host=$hostPreparacao;origem='PREPARAR.ps1'} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $runtimePreparacao 'genai-processo.json') -Encoding utf8
        Aguardar-ServicoPreparacao 'http://127.0.0.1:8765/' $processoPreparacaoIA 180
        if (-not (Testar-RespostaPreparacao 'http://127.0.0.1:8080/health')) { throw 'O aplicativo de IA abriu, mas o modelo não respondeu à verificação.' }
    } else { Write-Output 'Generative AI e modelo já estão respondendo.' }

    Write-Output 'Conferindo as integrações com execução atual…'
    & $pythonPreparacao -X utf8 (Join-Path $PSScriptRoot 'verificar_prontidao.py')
    if ($LASTEXITCODE -ne 0) { throw 'Uma integração falhou. Confira data/runtime/prontidao.json antes de gravar.' }
    Write-Output 'Preparação técnica concluída: http://127.0.0.1:8840'
    if ($Celular) { & (Join-Path $PSScriptRoot 'INICIAR-CELULAR.ps1') -Email $Email -Minutos $Minutos }
} catch {
    $arquivoDiagnosticoPreparacao=Join-Path $runtimePreparacao 'prontidao.json'
    $diagnosticoPreparacao=Get-Content -Raw -LiteralPath $arquivoDiagnosticoPreparacao | ConvertFrom-Json
    if ($diagnosticoPreparacao.status -eq 'preparando') { @{ok=$false;status='falha_na_inicializacao';erro=$_.Exception.Message;data=[DateTimeOffset]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath $arquivoDiagnosticoPreparacao -Encoding utf8 }
    throw
}
