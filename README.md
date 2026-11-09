# Cotação do Dólar via API do Banco Central

Coleta automática da cotação diária do dólar na **API REST pública do Banco Central (SGS)**, com tratamento dos dados em **pandas** e um resumo mensal exportado em CSV.

## Resultado

Período coletado: **02/01/2024 a 09/11/2026**. São **718 registros diários**, só de dias úteis.

| Indicador                | Valor     | Data       |
| ------------------------ | --------- | ---------- |
| Menor cotação do período | R$ 4,8543 | 12/01/2024 |
| Maior cotação do período | R$ 6,2086 | 02/01/2025 |

**Últimos meses (média mensal):**

| Mês                 | Média  | Mínimo | Máximo | Dias úteis | Variação vs. mês anterior |
| ------------------- | ------ | ------ | ------ | ---------- | ------------------------- |
| 2026-06             | 5,1276 | 5,0160 | 5,2098 | 21         | +2,89%                    |
| 2026-07             | 5,1139 | 5,0638 | 5,1950 | 23         | -0,27%                    |
| 2026-08             | 5,1532 | 5,0723 | 5,2236 | 21         | +0,77%                    |
| 2026-09             | 5,1447 | 5,0856 | 5,2204 | 21         | -0,16%                    |
| 2026-10             | 5,1294 | 4,9698 | 5,5007 | 21         | -0,30%                    |
| 2026-11 _(parcial)_ | 5,4899 | 5,4621 | 5,5146 | 5          | +7,03%                    |

> **Atenção:** novembro/2026 é um **mês parcial**, com só 5 dias úteis até a data da coleta. A variação de +7,03% compara esses primeiros dias com o mês de outubro inteiro e vai mudar até o fim do mês. Por isso o resumo tem a coluna `mes_parcial`.

Os números acima são da coleta feita em 09/11/2026. Uma nova execução traz os dados atualizados.

## Objetivo

Praticar, num projeto pequeno e completo, o fluxo de trabalho de um analista de dados com uma fonte externa:

**pedir os dados à API → validar → limpar → analisar → salvar → documentar**

## Fonte dos dados

- **Banco Central do Brasil, SGS (Sistema Gerenciador de Séries Temporais)**
- Série **1**: taxa de câmbio, dólar americano (venda), diária
- Endpoint: `https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados?formato=json&dataInicial=DD/MM/AAAA&dataFinal=DD/MM/AAAA`
- API pública, sem cadastro e sem chave de acesso

## Tecnologias

- **Python 3**
- **requests**: consumo da API REST
- **pandas**: tratamento e agregação dos dados
- **Git e GitHub**: versionamento

## Estrutura do projeto

```
cotacao-dolar-api/
├── coletor.py                        # código principal (classe ColetorBCB)
├── requirements.txt                  # bibliotecas usadas
├── dados/
│   ├── cotacao_dolar_diaria.csv      # cotações diárias tratadas
│   └── cotacao_dolar_mensal.csv      # resumo mensal
└── README.md
```

## Como executar

```bash
# 1. Instalar as bibliotecas
pip install -r requirements.txt

# 2. Rodar a coleta
python coletor.py
```

Os arquivos CSV são gerados na pasta `dados/`, no formato brasileiro (separador `;` e decimal `,`), e abrem direto no Excel.

## Como o código funciona

O código está organizado na classe `ColetorBCB` (orientação a objetos). Cada etapa do trabalho é um método:

| Método                                      | O que faz                                                                                                     |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| `__init__(serie, data_inicial, data_final)` | Guarda a série e o período. Sem data final, usa a data de hoje                                                |
| `buscar()`                                  | Faz a requisição à API, confere se ela respondeu sem erro (`raise_for_status`) e carrega o JSON num DataFrame |
| `tratar()`                                  | Converte as colunas de **texto** para **data** e **número**, porque a API devolve tudo como texto             |
| `resumo_mensal()`                           | Calcula média, mínimo, máximo, quantidade de dias e variação % mês a mês, e marca o mês parcial               |
| `salvar(tabela, caminho)`                   | Exporta uma tabela para CSV e cria a pasta, se for preciso                                                    |

Como a série é um parâmetro, a mesma classe coleta outros indicadores do SGS, trocando só o número da série.

<details>
<summary>Trecho principal do código</summary>

```python
coletor = ColetorBCB(serie=1, data_inicial="01/01/2024")
coletor.buscar()
coletor.tratar()

mensal = coletor.resumo_mensal()
coletor.salvar(coletor.dados, "dados/cotacao_dolar_diaria.csv")
coletor.salvar(mensal, "dados/cotacao_dolar_mensal.csv")
```

</details>

## Validação dos dados

- **Tipos:** antes do tratamento, `data` e `valor` chegam como texto (`str`). Depois, viram `datetime64` e `float64`.
- **Quantidade:** 718 registros de 02/01/2024 a 09/11/2026, coerente com o número de dias úteis do período, já que a série não tem fins de semana nem feriados.
- **Maior cotação:** conferida contra os máximos mensais do resumo. Foi essa comparação que revelou um erro na primeira versão do código.

## Aprendizados

- A API devolve números e datas como **texto**. Sem converter os tipos, não dá para calcular.
- Um código pode rodar **sem erro e ainda assim estar errado**. Na primeira versão, a maior e a menor cotação apareciam iguais por causa de um `idxmin` no lugar de `idxmax`. O erro só apareceu quando comparei o resultado com o máximo mensal.
- **Mês parcial** precisa ser sinalizado para não gerar conclusões erradas.

## Próximos passos

- [ ] Gráfico da evolução da cotação (matplotlib)
- [ ] Automatizar a coleta diária (por exemplo, com n8n)
- [ ] Coletar outras séries do SGS (euro, Selic) usando a mesma classe

## Autor

**Daniel Santos**, analista de dados em formação
[GitHub](https://github.com/danielsantos343) · [LinkedIn](https://www.linkedin.com/in/daniel-santos-996576305)
