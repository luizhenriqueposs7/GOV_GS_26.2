# CitizenTech · Triagem de solicitações de zeladoria urbana

Global Solution 2026.2 · AI for Robotic Process Automation

## Integrantes

- Luiz Henrique Poss · RM562177
- Luis Filipe Chaves Amorim · RM564706
- Felipe Stefani Honorato · RM563380

## Problema

A equipe de zeladoria recebe descrições livres de problemas urbanos, como buracos, postes apagados, descarte irregular e barreiras de acessibilidade. O protótipo organiza um lote de relatos e sinaliza quais precisam de revisão. A triagem usa regras de texto e grava os casos em SQLite para consulta.

## Como executar

1. Abra [Global_Solution_CitizenTech_RPA_IA.ipynb](Global_Solution_CitizenTech_RPA_IA.ipynb) no Google Colab ou no Jupyter, com Python 3. No Jupyter local, instale o Pandas com `python -m pip install pandas`.
2. Mantenha `CSV_PROPRIO = None` na seção **Entrada de dados** e use **Executar tudo** para rodar a demonstração. O notebook gera o CSV sintético, mostra os relatórios, roda os testes e consulta o banco.
3. Para usar um CSV próprio, envie o arquivo a uma pasta separada de `outputs/` e informe seu caminho em `CSV_PROPRIO`. O arquivo deve usar UTF-8, vírgula como separador e as colunas `case_id`, `description` e `neighborhood`. Execute todas as células. Use somente dados sintéticos ou públicos sem dados pessoais.

O processamento roda no ambiente do notebook e dispensa chaves de API.

## Arquivos gerados

| Arquivo | Conteúdo |
|---|---|
| `data/solicitacoes_demo.csv` | Entrada fictícia criada em modo de demonstração. |
| `data/requests.sqlite` | Solicitações válidas, com um registro por `case_id`. |
| `outputs/solicitacoes_processadas.csv` | Classificação, prioridade e indicação de revisão do lote atual. |
| `outputs/registros_rejeitados.csv` | Linhas do lote que têm campos obrigatórios vazios. |
| `outputs/execucao.log` | Contagens de processamento e registro de falhas. |

O banco acumula solicitações entre execuções na mesma pasta. Repetir o mesmo lote não duplica registros. Se um ID reaparecer com dados diferentes em outro lote, o registro é atualizado. Os relatórios exibidos no notebook correspondem ao lote executado com sucesso.

## Validação

A seção **Validação** contém a amostra rotulada e os resultados de categoria, prioridade e revisão. Em uma pasta temporária, o notebook também demonstra o tratamento de arquivo ausente, registro incompleto, repetição de ID e atualização consistente no SQLite e no CSV.
