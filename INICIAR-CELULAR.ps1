param(
    [Parameter(Mandatory=$true)]
    [ValidatePattern('^[A-Za-z0-9.!#$%&+_=/^{}~-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+$')]
    [string]$Email,
    [ValidateRange(5,180)][int]$Minutos=60
)
$ErrorActionPreference='Stop'
$runtimeCelular=Join-Path $PSScriptRoot 'data/runtime'
$cloudflaredCelular=Join-Path $runtimeCelular 'cloudflared.exe'
$estadoCelularArquivo=Join-Path $runtimeCelular 'celular-acesso.json'
$logCelular=Join-Path $runtimeCelular 'celular-tunnel.log'
$shaEsperadoCelular='d5c1d82031da6253dcdcff64c944cd0fe063016edeb2e4fd088075fc9bd52d0a'
if (-not (Test-Path -LiteralPath $cloudflaredCelular)) { throw 'Instale o cloudflared 2026.11.0 oficial em data/runtime/cloudflared.exe. Veja docs/teste-celular.md.' }
if ((Get-FileHash -LiteralPath $cloudflaredCelular -Algorithm SHA256).Hash.ToLowerInvariant() -ne $shaEsperadoCelular) { throw 'O executável não corresponde ao SHA-256 oficial da versão preparada.' }
if ((Invoke-RestMethod 'http://127.0.0.1:8840/api/status' -TimeoutSec 8).status -ne 'ok') { throw 'Inicie a central com INICIAR.ps1 antes do acesso móvel.' }
if (Test-Path -LiteralPath $estadoCelularArquivo) {
    $anteriorCelular=Get-Content -Raw -LiteralPath $estadoCelularArquivo | ConvertFrom-Json
    $processoAnteriorCelular=$null
    if ($anteriorCelular.processo_tunnel) { $processoAnteriorCelular=Get-Process -Id $anteriorCelular.processo_tunnel -ErrorAction SilentlyContinue }
    if ($processoAnteriorCelular -and $processoAnteriorCelular.Path -eq $cloudflaredCelular) { throw 'Já existe um acesso móvel ativo. Encerre com ENCERRAR-CELULAR.ps1 antes de iniciar outro.' }
}
$estadoCelular=@{status='iniciando';url=$null;inicio=[DateTimeOffset]::Now.ToString('o');expira_em=$null;processo_tunnel=$null;processo_controlador=$PID;protecao='codigo_por_email';destino='http://127.0.0.1:8840'}
function Salvar-EstadoCelular { $estadoCelular | ConvertTo-Json | Set-Content -LiteralPath $estadoCelularArquivo -Encoding utf8 }
$processoTunnelCelular=$null
try {
    $processoTunnelCelular=Start-Process -FilePath $cloudflaredCelular -ArgumentList @('--no-autoupdate','tunnel','--protocol','http2','--url','http://127.0.0.1:8840','--allowed-mail',$Email) -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -RedirectStandardError $logCelular -RedirectStandardOutput (Join-Path $runtimeCelular 'celular-tunnel-out.log') -PassThru
    $estadoCelular.processo_tunnel=$processoTunnelCelular.Id
    $limiteCelular=[DateTimeOffset]::Now.AddMinutes($Minutos)
    $estadoCelular.expira_em=$limiteCelular.ToString('o')
    Salvar-EstadoCelular
    while ([DateTimeOffset]::Now -lt $limiteCelular) {
        $processoTunnelCelular.Refresh()
        if ($processoTunnelCelular.HasExited) { throw 'O túnel foi encerrado. Consulte data/runtime/celular-tunnel.log.' }
        if (-not $estadoCelular.url -and (Test-Path -LiteralPath $logCelular)) {
            $conteudoCelular=Get-Content -Raw -LiteralPath $logCelular
            if (-not [string]::IsNullOrWhiteSpace($conteudoCelular)) {
                $enderecoCelular=[regex]::Match($conteudoCelular,'https://[a-z0-9-]+\.trycloudflare\.com')
                if ($enderecoCelular.Success) { $estadoCelular.url=$enderecoCelular.Value; $estadoCelular.status='ativo'; Salvar-EstadoCelular; Write-Output $estadoCelular.url }
            }
        }
        Start-Sleep -Seconds 2
    }
    $estadoCelular.status='expirado'
} catch {
    $estadoCelular.status='encerrado_ou_falhou'
    throw
} finally {
    if ($processoTunnelCelular) { $processoTunnelCelular.Refresh(); if (-not $processoTunnelCelular.HasExited) { Stop-Process -InputObject $processoTunnelCelular -Force } }
    Salvar-EstadoCelular
}
