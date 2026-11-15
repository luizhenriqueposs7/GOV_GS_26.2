# Teste no celular

O acesso temporário usa Cloudflare Quick Tunnel com `--allowed-mail`. Apenas o e-mail explicitamente autorizado pode entrar com o código recebido. O túnel aponta para a central local em 127.0.0.1:8840 e não exige abrir portas no roteador. Fotos, relatos e GPS atravessam a Cloudflare até o computador; a área do mapa também é recebida pelo OpenStreetMap. As permissões de câmera e localização são concedidas pela pessoa no telefone.

## Preparação

O executável oficial cloudflared 2026.11.0 foi baixado em `data/runtime/cloudflared.exe`, fora do Git. O SHA-256 foi conferido com a publicação da Cloudflare no GitHub: `d5c1d82031da6253dcdcff64c944cd0fe063016edeb2e4fd088075fc9bd52d0a`. O inicializador confere esse hash novamente e não inicia sem a opção de proteção por e-mail.

- [Publicação oficial e hash](https://github.com/cloudflare/cloudflared/releases/tag/2026.11.0)
- [Proteção por e-mail](https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/#restrict-access-by-email)

Com a central aberta, execute em PowerShell: `./INICIAR-CELULAR.ps1 -Email SEU_EMAIL -Minutos 60`. O e-mail real fica apenas no processo local e na configuração temporária do provedor, sem ser versionado. O endereço e o horário limite ficam em `data/runtime/celular-acesso.json`. O link muda a cada inicialização. Ao terminar o tempo, o processo encerra o túnel. Para encerrar antes, use `./ENCERRAR-CELULAR.ps1`; a central local continua aberta.

Para preparar tudo em um comando, use `./PREPARAR.ps1 -Celular -Email SEU_EMAIL -Minutos 60`. Ele inicia ou reutiliza a central e a IA, confere as sete integrações técnicas e só depois abre o acesso protegido. Sem `-Celular`, a preparação é apenas local. A leitura de câmera e GPS pode ser cancelada: uma resposta atrasada não deve substituir o ponto escolhido manualmente. A confirmação final declara o teste, sem exigir que uma foto ou coordenada reais sejam chamadas de fictícias.

O computador precisa permanecer ligado, conectado e sem suspensão durante o teste. A disponibilidade do serviço temporário depende da Cloudflare. O acesso não é uma publicação de produção.

## Percurso

O teste físico e a gravação foram planejados pelo integrante para 15/11/2026. O link temporário de 14/11 não será reutilizado: iniciar a central e gerar outro link protegido no momento do teste. O e-mail já autorizado pode ser mantido. Isso não significa que o teste físico tenha passado antecipadamente.

Para a gravação, escolha uma situação urbana simples que possa fotografar sem risco, como um trecho de calçada. Capture a foto pelo aplicativo, confira o GPS e envie o pedido na hora. Continue o mesmo identificador no computador: verifique o anexo e o ponto, registre a revisão e a justificativa, confirme no ZelaBairro e faça a contestação. O histórico deve conservar cada etapa. Grave a operação completa; selecione depois o trecho que cabe no vídeo final de 5 a 7 minutos, que também precisa apresentar as outras disciplinas.

1. Abra o link HTTPS no Safari do iPhone ou Chrome do Android. Informe o e-mail autorizado e o código enviado à caixa de entrada. Não use o navegador interno de um mensageiro.
2. Entre em Registrar. Toque no botão da câmera e permita o acesso. Fotografe um objeto ou superfície de demonstração, sem pessoas, placas ou documentos. Se a câmera ao vivo não abrir, use Câmera do aparelho ou Escolher imagem.
3. Escreva um relato claramente identificado como teste. Avance para localização e toque em Usar posição do aparelho. Permita a localização; confira o ponto, a precisão informada e a referência. O GPS não preenche endereço ou bairro automaticamente.
4. Para não guardar a posição real no pedido, após conferir o GPS use Limpar coordenadas e escolha um ponto de demonstração. Se mantiver a posição real, ela ficará no banco e no histórico locais, fora do Git.
5. Confirme o ponto, avance, confira a foto e o relato e registre o pedido de demonstração. Anote o identificador recebido. Ele aparecerá na mesma central aberta no computador.
6. Abra Meus pedidos para conferir a foto e o histórico. Revisão e confirmação no ZelaBairro continuam exigindo a chave local do responsável. O registro não abre chamado municipal.

O que a demonstração pode provar: captura/anexo, localização do aparelho, confirmação do ponto, persistência e revisão do pedido. A foto de uma calçada não comprova detecção automática de buraco; o GPS não comprova o endereço. Se alguma etapa falhar, registre a condição e o resultado observado, sem substituir silenciosamente por uma execução anterior.

Registre separadamente o aparelho, navegador, permissões concedidas, resultado da câmera, precisão do GPS e identificador do pedido. A preparação do link não comprova funcionamento físico: esse resultado depende do teste feito pela pessoa no celular. Não envie códigos de acesso, chave de gestão ou foto pessoal para o GitHub.

## Conferência da preparação em 14/11/2026

Sintaxe dos dois scripts aprovada e quatro configurações inválidas rejeitadas antes de iniciar o túnel: wildcard de domínio, múltiplos e-mails, tentativa de argumentos extras e duração fora do limite. A conexão HTTP/2 com a Cloudflare foi estabelecida. No navegador sem autenticação, o endereço abriu a tela de login da Cloudflare Access; nenhum código foi solicitado pelo assistente.

Requisições sem cookie à página inicial, à lista de pedidos e à foto de um pedido fictício retornaram 302 para a autenticação, sem liberar o conteúdo. Evidência sem e-mail, cookies ou códigos em [verificação do acesso](evidencias/acesso-celular-2026-11-14.json). O endereço temporário e seus parâmetros de autenticação não são versionados.
