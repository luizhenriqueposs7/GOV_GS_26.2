$ErrorActionPreference='Stop'
$scriptAcessoCelular=Join-Path (Split-Path $PSScriptRoot) 'INICIAR-CELULAR.ps1'
$casosAcessoCelular=@(
    @{Email='*@example.com';Minutos=60},
    @{Email='um@example.com,dois@example.com';Minutos=60},
    @{Email='um@example.com --url';Minutos=60},
    @{Email='um@example.com';Minutos=0}
)
foreach ($casoAcessoCelular in $casosAcessoCelular) {
    $rejeitadoCelular=$false
    try { & $scriptAcessoCelular @casoAcessoCelular }
    catch { if ($_.FullyQualifiedErrorId -notmatch '^ParameterArgumentValidationError') { throw }; $rejeitadoCelular=$true }
    if (-not $rejeitadoCelular) { throw 'Uma configuração não autorizada passou pela validação.' }
}
Write-Output '4/4: wildcard, múltiplos e-mails, argumentos extras e tempo inválido rejeitados antes da publicação.'
