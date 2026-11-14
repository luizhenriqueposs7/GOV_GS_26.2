$ErrorActionPreference='Stop'
$runtimeCelular=Join-Path $PSScriptRoot 'data/runtime'
$estadoCelularArquivo=Join-Path $runtimeCelular 'celular-acesso.json'
if (-not (Test-Path -LiteralPath $estadoCelularArquivo)) { Write-Output 'Nenhum acesso móvel preparado.'; return }
$estadoCelular=Get-Content -Raw -LiteralPath $estadoCelularArquivo | ConvertFrom-Json
$processoTunnelCelular=$null
if ($estadoCelular.processo_tunnel) { $processoTunnelCelular=Get-Process -Id $estadoCelular.processo_tunnel -ErrorAction SilentlyContinue }
$executavelCelular=Join-Path $runtimeCelular 'cloudflared.exe'
if ($processoTunnelCelular -and $processoTunnelCelular.Path -eq $executavelCelular) { Stop-Process -InputObject $processoTunnelCelular -Force }
Write-Output 'Acesso externo encerrado. A central local continua disponível em 127.0.0.1:8840.'
