# 🚀 QuantumFinance — AI Investment Assistant
> **Trabalho Final da Disciplina:** *Agents and Agentic AI*  
> **Curso:** MBA em Data Engineering — **FIAP**  
> **Professor:** Felipe Gustavo Silva Teodoro  
> **Integrantes do Grupo:**
> - Fátima Beatriz Rodrigues
> - Jean Felipe Ertzogue
> - Luiz Soldatelli Neto
> - Ricardo Peixoto


## 📌 1. Visão Geral do Desafio

A **QuantumFinance** é uma instituição financeira em expansão no mercado de capitais que deseja oferecer aos seus clientes um **Assistente de Investimentos autônomo e explicável** baseado em **AI Agents**.

O assistente foi projetado para monitorar continuamente o mercado brasileiro (B3), coletar dados fundamentalistas, cotações e notícias financeiras em tempo real, raciocinar criticamente e emitir recomendações diárias fundamentadas de **COMPRA**, **VENDA** ou **MANUTENÇÃO (AGUARDAR)** para as 4 ações prioritárias do desafio:

| Ticker | Empresa | Setor de Atuação | Fonte de Cotações |
| :---: | :---: | :---: | :---: |
| **VALE3** | Vale S.A. | Mineração & Siderurgia | B3 (`yfinance`) |
| **PETR4** | Petrobras | Energia / Óleo & Gás | B3 (`yfinance`) |
| **BBAS3** | Banco do Brasil | Serviços Financeiros / Bancário | B3 (`yfinance`) |
| **ITUB4** | Itaú Unibanco | Serviços Financeiros / Bancário | B3 (`yfinance`) |

---

## 🏛️ 2. Arquitetura da Solução & Fluxo Mermaid

O assistente adota estritamente a metodologia **ReAct (Reasoning + Acting)** implementada com o framework oficial ensinado nas aulas, o **Google ADK** (`google-adk`), integrando ferramentas modulares e interface conversacional com **Gradio**.

```mermaid
flowchart TD
    User([Investidor / Usuário Final]) --> UI[Interface Conversacional\nGradio Chat / Jupyter]
    
    subgraph Core [Núcleo do AI Agent - Google ADK]
        Runner[Runner & Session Manager\nInMemorySessionService]
        Agent[Orquestrador ReAct Agent\nGoogle ADK + LiteLLM / Gemini]
        Memory[(Histórico de Sessão\nMulti-Turn Memory)]
    end
    
    UI <-->|Pergunta / Resposta| Runner
    Runner <--> Agent
    Agent <--> Memory
    
    subgraph Perception [Módulo de Percepção & Dados de Mercado]
        T1["Tool 1: get_market_data(ticker, period)\nColeta Histórica OHLCV (yfinance)"]
        T2["Tool 2: calculate_indicators(ticker, period)\nRSI, MACD, SMA 20/50, Bandas de Bollinger"]
        T3["Tool 3: search_news_sentiment(ticker)\nRSS Feeds (feedparser) + NLP Sentiment"]
        T4["Tool 4: run_backtest_strategy(ticker, days)\nSimulação Quantitativa vs Buy & Hold"]
    end
    
    Agent -->|1. Thought & Tool Selection| Perception
    Perception -->|2. Structured Observation| Agent
    
    subgraph ExternalSources [Fontes Externas de Dados]
        YF[(Yahoo Finance API\nCotações B3 .SA)]
        RSS[(Feeds RSS\nGoogle News B3, InfoMoney, G1)]
    end
    
    T1 <--> YF
    T2 --> T1
    T3 <--> RSS
    T4 --> T1
    T4 --> T2
```

---

## 🛡️ 2.1. Diferencial de Engenharia: Modo Resiliente com Fallback Offline (Graceful Degradation)
> [!TIP]
> **Alta Disponibilidade e Execução Sem Barreiras:**
> Em arquiteturas de dados de missão crítica, agentes de IA não podem falhar se a API de um provedor de LLM sofrer oscilações, atinja limites de requisições (*rate limits*) ou se o usuário não possuir créditos cadastrados.
> 
> O **QuantumAdvisor** incorpora o padrão de engenharia **Graceful Degradation**:
> 1. **Modo Conectado (LLM via Google ADK)**: Utiliza `gemini-2.5-flash`, `gpt-4o-mini` ou `Llama 3` orquestrado pelo Google ADK.
> 2. **Modo Resiliente (Fallback Offline Determinístico)**: Caso nenhuma chave seja detectada, o agente aciona automaticamente um motor analítico fundamentado. Ele consome dados reais da B3 via `yfinance`, calcula matematicamente todos os indicadores técnicos, lê as notícias reais via RSS (`feedparser`), executa o backtest e sintetiza o parecer com **Chain-of-Thought** e o **JSON estruturado do Slide 7**.
> 
> Isso garante **100% de reprodutibilidade** no **Google Colab**, **Databricks Community Edition (Free)** ou em qualquer terminal local sem custo e sem atrito.

---

## 🧠 3. As Três Dimensões do AI Agent

### 👁️ A. Percepção (Perception)
* **Preços e Volumes em Tempo Real**: Coleta de dados OHLCV da B3 via `yfinance` com cálculo de variações diárias e volume médio.
* **Indicadores Gráficos Quantitativos**: Extração matemática de:
  * **RSI (14 períodos)**: Detecção de zonas de sobrecompra (>70) ou sobrevenda (<30).
  * **MACD (12, 26, 9)**: Cruzamento de médias exponenciais e histograma de aceleração (*bullish* / *bearish*).
  * **Médias Móveis Simples (SMA 20 e SMA 50)**: Tendência de curto e médio prazo.
  * **Bandas de Bollinger (20, ±2σ)**: Níveis de volatilidade e envelopes de suporte/resistência.
* **Leitura de Notícias em Tempo Real**: Parser de feeds RSS direcionados para cada ticker (Google News Brasil para B3, InfoMoney e G1 Economia) via `feedparser`.

### 🧩 B. Raciocínio (Reasoning & Chain-of-Thought)
* **Análise de Sentimento (NLP Financeiro)**: Processamento e pontuação ponderada das manchetes mais recentes em uma escala contínua de **-1.0** (forte aversão) a **+1.0** (forte otimismo).
* **Raciocínio Transparente**: O agente explicita cada etapa do pensamento antes de tomar uma decisão, garantindo total conformidade com as exigências de explicabilidade do mercado regulado.

### ⚡ C. Ação (Action & Decision)
* **Recomendação Oficial**: Emissão de parecer formal (**COMPRAR**, **VENDER** ou **AGUARDAR**).
* **Estrutura de Saída Canônica** (conforme solicitado no Slide 7 do enunciado):
  ```json
  {
    "ticker": "VALE3",
    "date": "2026-10-01",
    "close": 61.42,
    "rsi": 45.2,
    "macd_signal": "bullish",
    "news_sentiment": 0.72,
    "recommendation": "COMPRAR"
  }
  ```
* **Simulação de Backtest**: Comparação de retorno financeiro e acurácia de tendência em relação ao benchmark de *Buy-and-Hold*.
* **Interface Conversacional**: Suporte a consultas em linguagem natural via **Gradio Chat** (ex.: *"Por que você recomendou comprar PETR4 hoje?"*).

---

## 📊 4. Matriz de Atendimento à Rubrica da Disciplina

| Item do Enunciado | Requisito Solicitado | Implementação no Projeto | Status |
| :---: | :--- | :--- | :---: |
| **01** | **Coleta e Pré-processamento** | Integração aberta de dados OHLCV via `yfinance` e RSS via `feedparser`. | ✅ Concluído |
| **02** | **Análise de Sentimento** | Classificação léxico-semântica de notícias financeiras com cálculo de score contínuo. | ✅ Concluído |
| **03** | **AI Agent com Tools** | Agente construído com **Google ADK** contendo 4 ferramentas ativas e ciclo ReAct explícito. | ✅ Concluído |
| **04** | **Recomendações e Backtest** | Emissão de recomendações com Chain-of-Thought, cálculo de acurácia de tendência e simulação vs Buy & Hold. | ✅ Concluído |
| **Bônus** | **Interface Conversacional** | Chat interativo implementado com `gradio` permitindo perguntas multi-turno. | ✅ Concluído |
| **Bônus** | **Visualização Gráfica** | Gráficos interativos em `plotly` combinando Candlesticks, Médias, Bollinger e RSI. | ✅ Concluído |

---

## 💻 5. Como Executar o Projeto

### Opção A: Executar no Google Colab (Recomendado)
1. Acesse o [Google Colab](https://colab.research.google.com/).
2. Faça o upload do arquivo [`Trabalho_Final_QuantumFinance_AI_Agent.ipynb`](file:///c:/Users/Ricardo/Projetos/agents-and-agentic-ai/Trabalho_Final_QuantumFinance_AI_Agent.ipynb).
3. Execute as células sequencialmente. O notebook possui suporte tanto para chaves da **API do Google Gemini** quanto da **OpenAI**, além de um modo de execução determinística local caso nenhuma chave seja informada.

### Opção B: Executar Localmente
```bash
# Clone ou acesse o repositório
cd c:/Users/Ricardo/Projetos/agents-and-agentic-ai

# Instale as dependências (usando uv ou pip)
uv run --python 3.12 --with jupyter jupyter notebook Trabalho_Final_QuantumFinance_AI_Agent.ipynb
# Ou alternativamente:
# pip install google-adk google-genai litellm yfinance feedparser pandas numpy plotly gradio requests
# jupyter notebook Trabalho_Final_QuantumFinance_AI_Agent.ipynb
```

---

## 📁 6. Estrutura do Repositório

```
agents-and-agentic-ai/
├── AGENTS.md                                   # Diretrizes operacionais e memória do projeto
├── ARCHITECTURE.md                             # Especificação técnica completa e diagrama de sequência
├── README.md                                   # Documentação geral e guia do trabalho
├── Trabalho_Final_QuantumFinance_AI_Agent.ipynb # Notebook executável principal da entrega
├── generate_final_notebook.py                  # Script automatizado de compilação do notebook
└── resources/
    ├── Trabalho_Final_AI_Agents_v2.pdf         # Enunciado original do trabalho final
    ├── Reunião em _Agents and Agentic AI_...   # Transcrições das 4 aulas da disciplina
    └── notebooks_aula/                         # Notebooks de referência das aulas práticas (Google ADK)
```

---
*FIAP — MBA em Data Engineering | Disciplina: Agents and Agentic AI*
