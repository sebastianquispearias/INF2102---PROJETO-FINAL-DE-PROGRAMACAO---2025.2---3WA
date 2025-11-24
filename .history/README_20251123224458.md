# Fleet NOx EDA

Pequena aplicação em Python/Streamlit para explorar dados de emissões de NOx em frotas de veículos.

A ideia é simples: o usuário sobe um ou mais CSVs de telemetria, escolhe um período e um conjunto de veículos, e a ferramenta mostra gráficos básicos e um ranking simples por veículo. O foco é apoiar a análise exploratória de dados (EDA) para o projeto da disciplina INF2102.

---

## Objetivo

- Visualizar a distribuição de NOx da frota.
- Comparar veículos entre si.
- Ver como o NOx varia ao longo do tempo e por horário do dia.
- Calcular um ranking simples de veículos com base em NOx.

Não é um sistema em tempo real. É uma ferramenta de análise offline, focada em leitura de CSVs e geração de gráficos e métricas básicas.

---

## Tecnologias usadas

- Python 3.12
- Streamlit
- pandas
- plotly
- pytest (para alguns testes unitários simples)

---

## Estrutura do projeto

```text
fleet-nox-eda/
  app.py                # aplicação Streamlit
  requirements.txt      # dependências
  README.md

  src/
    __init__.py
    data_loader.py      # leitura e preparação do CSV
    filters.py          # filtros por data e por veículo
    metrics.py          # métricas globais e ranking
    plots.py            # funções de gráficos (plotly)

  sample_data/
    demo_fleet.csv      # conjunto de exemplo (dados fictícios)

  tests/
    test_data_loader.py # teste da função de carga de CSV
    test_metrics.py     # testes das funções de métricas
```

---

## Como rodar o projeto

### 1. Clonar ou copiar a pasta

No Windows, por exemplo:

```bash
cd C:\Users\User\Desktop
# se usar git:
# git clone <URL-DO-REPO> fleet-nox-eda
cd fleet-nox-eda
```

Se não estiver usando git, basta copiar a pasta do projeto para algum diretório.

### 2. Criar ambiente virtual (recomendado)

```bash
python -m venv .venv
.\.venv\Scriptsctivate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Rodar a aplicação Streamlit

```bash
streamlit run app.py
```

Depois é só abrir o navegador em `http://localhost:8501` (normalmente o próprio Streamlit já abre).

---

## Como usar a aplicação

1. Na barra lateral, em **"Configuração de dados"**, enviar um ou mais arquivos CSV.
2. Ajustar o intervalo de datas (baseado na coluna `timestamp`).
3. Selecionar os veículos que quer analisar.
4. Ajustar o threshold de NOx (por exemplo, 50 ppm).
5. Navegar pelas abas:

   - **Histograma**: distribuição geral de NOx.
   - **Boxplot**: NOx por veículo (comparação entre veículos).
   - **Série temporal**: NOx ao longo do tempo, separado por veículo.
   - **Média por veículo**: NOx médio por veículo (gráfico de barras).
   - **Média por hora**: NOx médio por hora do dia (0–23).
   - **Ranking**: tabela com estatísticas por veículo e fração do tempo acima do threshold.

6. Na aba **Ranking** é possível baixar:
   - o ranking em CSV (`vehicle_ranking.csv`);
   - as métricas globais em CSV (`global_metrics.csv`).

---

## Formato esperado do CSV

O código de carga (`data_loader.py`) foi pensado para um formato parecido com dados reais de frota. As colunas mínimas esperadas são:

- `vehicle_number` ou `vehicle_name` (ou já `vehicle_id`);
- `timestamp`;
- `NOx`;
- `O2`;
- `position` (quando não há `latitude` e `longitude` separados).

Regras principais:

- **timestamp**:
  - pode ser numérico em milissegundos desde epoch (ex.: `1735689600000`), ou
  - string de data/hora que o pandas consiga interpretar.

- **vehicle_id interno**:
  - se existir `vehicle_name`, vira o `vehicle_id`;
  - senão usa `vehicle_number`;
  - se já existir `vehicle_id`, usa direto.

- **NOx e O2**:
  - convertidos para `float` (linhas com valores inválidos podem ser descartadas).

- **Localização**:
  - se existirem `latitude` e `longitude`, o código usa essas colunas;
  - se existir apenas `position` no formato `POINT(lon lat)`, o código extrai `latitude` e `longitude`;
  - se não houver nenhuma informação de posição, os gráficos funcionam mesmo assim (sem mapa).

Exemplo (arquivo de demo):

```csv
vehicle_number,vehicle_name,timestamp,order,Sensor_Hours,NOx,NOx_max,NOx_min,NOx_dp,samples,O2,position,label_parado_nox
101,TRUCK_01,1735689600000,1000,10,30,60,10,5,1200,20.0,POINT(-43.2786 -22.8701),True
...
```

---

## Métricas e ranking

Para os dados depois dos filtros (datas + veículos), são calculadas:

- **Métricas globais**:
  - média de NOx (`global_mean_nox`);
  - mediana de NOx (`global_median_nox`);
  - número de veículos distintos (`n_vehicles`);
  - número de registros (`n_records`);
  - valor de `threshold_nox` usado no momento.

- **Ranking por veículo**:
  - `mean_nox`: média de NOx do veículo;
  - `median_nox`: mediana de NOx do veículo;
  - `fraction_time_above_threshold`: fração de registros em que `NOx > threshold`.

O ranking é ordenado pela fração acima do limiar (veículos com maior fração aparecem primeiro).

---

## Testes

Há alguns testes unitários básicos usando `pytest`:

- `tests/test_data_loader.py`:
  - testa a carga do CSV de exemplo (`demo_fleet.csv`);
  - verifica se as colunas principais existem e têm tipo adequado.

- `tests/test_metrics.py`:
  - testa `compute_basic_stats` com um DataFrame pequeno construído em memória;
  - testa `compute_vehicle_ranking` com dados artificiais, checando as colunas e o cálculo da fração acima do threshold.

Para rodar os testes, com o ambiente virtual ativado:

```bash
python -m pytest
```

---

## Limitações e ideias futuras

Limitações atuais:

- Focado apenas em NOx; outras variáveis do CSV não são exploradas em detalhe.
- Não há detecção de eventos específicos (por exemplo, marcha lenta prolongada).
- Não há interface de mapa nem filtros espaciais.
- A aplicação trabalha sempre em memória (não salva resultados em banco de dados).

Possíveis extensões:

- Adicionar métricas diárias ou semanais por veículo.
- Incluir outras variáveis (velocidade, carga, etc.) nos gráficos.
- Salvar configurações de filtro ou relatórios prontos.
- Integrar com outros sistemas de telemetria ou APIs.
