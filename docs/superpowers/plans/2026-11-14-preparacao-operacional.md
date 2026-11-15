# Preparação operacional do ZelaBairro

Objetivo autorizado: deixar a plataforma pronta para o teste físico e a gravação de 15/11, mantendo as funções e a identidade aprovadas.

1. Corrigir a espera por permissões de câmera/GPS: cancelar sem bloquear todo o formulário e descartar respostas atrasadas ao trocar de etapa ou ajustar o ponto. Arquivos: web/mobile.mjs, web/app.js, tests/mobile.test.mjs.
2. Ajustar o texto de confirmação para um teste técnico com foto e posição reais, sem afirmar envio municipal. Arquivos: web/index.html, web/sw.js, README.md.
3. Unificar a preparação local, reutilizando INICIAR.ps1 e INICIAR-IA.ps1; verificar central, modelo local, RPA, PLN, Visão e materiais com execução atual. Não iniciar acesso externo automaticamente. Arquivos: PREPARAR.ps1, verificar_prontidao.py, testes relacionados e guia.
4. Testar permissões canceladas/negadas, GPS atrasado, diagnósticos e fluxo completo. Executar verificações apropriadas e registrar resultado; preservar bancos atuais. O teste físico continua pendente até o integrante usar o telefone.

Decisões: usar AbortController para controlar a intenção da leitura, sem presumir que o navegador cancela a API física. A inicialização mantém bibliotecas e serviços existentes. Caminhos específicos desta máquina ficam em data, fora do Git. IoT segue externo, Cluster simulação e Quântica estudo conceitual. Não acrescentar detector de buracos ou integração municipal.
