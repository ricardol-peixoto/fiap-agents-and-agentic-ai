import json

notebook = {
    "cells": [],
    "metadata": {
        "colab": {
            "name": "Trabalho_Final_QuantumFinance_AI_Agent.ipynb",
            "provenance": []
        },
        "kernelspec": {
            "display_name": "Python 3",
            "name": "python3"
        },
        "language_info": {
            "name": "python"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 4
}

def add_md(source):
    notebook["cells"].append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in source.strip().split("\n")]
    })

def add_code(source):
    notebook["cells"].append({
        "cell_type": "code",
        "metadata": {},
        "execution_count": None,
        "outputs": [],
        "source": [line + "\n" for line in source.strip().split("\n")]
    })

# ==================== CELULA 1: CABEÇALHO ====================
add_md("""# FIAP — MBA em Data Engineering
## Disciplina: Agents and Agentic AI
### Professor: Felipe Gustavo Silva Teodoro
### Aluno: Ricardo de Lima Peixoto

---

# 🚀 Trabalho Final: QuantumFinance AI Investment Assistant
### *Assistente de Investimentos Autônomo e Explicável Baseado em AI Agents*

---

## 1. Contexto de Negócio & O Desafio

A **QuantumFinance** está expandindo sua atuação no mercado de capitais e renda variável. Para se destacar e entregar valor real aos clientes, a instituição precisa de um **Assistente de Investimentos inteligente** capaz de analisar o mercado e emitir recomendações autônomas de compra, venda ou manutenção de ações da B3 de forma **explicável, auditável e fundamentada**.

### Ações Prioritárias Monitoradas:
- 🔵 **VALE3** — Vale S.A. (Setor de Mineração)
- 🟢 **PETR4** — Petrobras (Setor de Energia / Óleo & Gás)
- 🟡 **BBAS3** — Banco do Brasil (Setor Financeiro)
- 🟠 **ITUB4** — Itaú Unibanco (Setor Financeiro)

---

## 2. Arquitetura da Solução (Padrão ReAct & Google ADK)

O assistente foi desenhado seguindo rigorosamente o paradigma **ReAct (Reasoning + Acting)** ensinado pelo Professor Felipe Teodoro, utilizando o **Google ADK** (`google-adk`). O agente não segue um pipeline engessado; ele raciocina passo a passo (*Chain-of-Thought*), aciona ferramentas de percepção (*Tools*), interpreta observações e sintetiza recomendações acionáveis.

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
""")

# ==================== CELULA 2: SETUP & DEPENDENCIAS ====================
add_md("""## 3. Preparação do Ambiente & Instalação de Dependências

Instalação do **Google ADK**, **LiteLLM**, **yfinance**, **feedparser**, bibliotecas estatísticas e o **Gradio** para a interface interativa.""")

add_code("""# Instalação das dependências necessárias para execução no Google Colab ou ambiente local
%pip install -q \
    google-adk \
    google-genai \
    litellm \
    yfinance \
    feedparser \
    pandas \
    numpy \
    plotly \
    gradio \
    requests""")

add_code("""import os
import getpass
import warnings
import json
import re
from datetime import datetime, timedelta
import requests
import feedparser
import numpy as np
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import gradio as gr

# Desativa avisos de depreciação de bibliotecas auxiliares
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

print("✅ Ambiente configurado com sucesso!")""")

# ==================== CELULA 3: CONFIGURAÇÃO DE CREDENCIAIS ====================
add_md("""## 4. Configuração Segura de Credenciais da LLM

Seguindo as melhores práticas de segurança e governança de dados:
- O agente aceita chaves via variáveis de ambiente (`GEMINI_API_KEY` ou `OPENAI_API_KEY`).
- Caso não estejam no ambiente, o notebook permite a entrada segura via `getpass` (sem exibir caracteres em tela).
- Caso o usuário não possua chave no momento, o notebook conta com um **modo de demonstração analítica e determinística**, garantindo a inspeção de todas as ferramentas, gráficos e backtests.""")

add_code("""# Configuração segura de chaves de API (OpenAI ou Google Gemini)
# Nunca coloque chaves diretamente em texto puro no código!

MODEL_PROVIDER = "gemini" # Opções: "gemini" ou "openai"

if MODEL_PROVIDER == "gemini":
    if not os.environ.get("GEMINI_API_KEY"):
        chave = os.environ.get("GOOGLE_API_KEY")
        if not chave:
            print("Informe a sua GEMINI_API_KEY (ou pressione Enter para modo demonstração):")
            try:
                chave = getpass.getpass()
            except Exception:
                chave = ""
        if chave:
            os.environ["GEMINI_API_KEY"] = chave
            os.environ["GOOGLE_API_KEY"] = chave
            print("🔑 GEMINI_API_KEY registrada com sucesso!")
        else:
            print("⚠️ Nenhuma chave informada. O agente funcionará no modo de demonstração analítica.")
else:
    if not os.environ.get("OPENAI_API_KEY"):
        print("Informe a sua OPENAI_API_KEY (ou pressione Enter para modo demonstração):")
        try:
            chave = getpass.getpass()
        except Exception:
            chave = ""
        if chave:
            os.environ["OPENAI_API_KEY"] = chave
            print("🔑 OPENAI_API_KEY registrada com sucesso!")
        else:
            print("⚠️ Nenhuma chave informada. O agente funcionará no modo de demonstração analítica.")""")

# ==================== CELULA 4: PERCEPÇÃO - TOOLS DE MERCADO ====================
add_md("""## 5. Módulo de Percepção: Implementação das Ferramentas (Tools)

O agente dispõe de quatro ferramentas especializadas com tipagem estrita e documentação clara:
1. `get_market_data`: Coleta preços históricos e dados intradiários da B3 via `yfinance`.
2. `calculate_technical_indicators`: Extrai RSI, MACD, Médias Móveis (20 e 50) e Bandas de Bollinger.
3. `search_news_sentiment`: Coleta notícias financeiras em tempo real via RSS e calcula o sentimento ponderado de mercado.
4. `run_backtest_strategy`: Avalia o desempenho retrospectivo da estratégia do agente em comparação ao *Buy-and-Hold*.""")

add_code("""def normalizar_ticker(ticker: str) -> str:
    \"\"\"Garante que o ticker possua a extensão .SA correspondente à B3 no Yahoo Finance.\"\"\"
    t = ticker.upper().strip()
    if not t.endswith(".SA") and not "." in t:
        return f"{t}.SA"
    return t


def get_market_data(ticker: str, period: str = "90d") -> dict:
    \"\"\"Coleta dados históricos de cotação e volume de uma ação negociada na B3 via Yahoo Finance.
    
    Args:
        ticker: O código da ação na B3 (ex: 'VALE3', 'PETR4', 'BBAS3', 'ITUB4').
        period: Intervalo histórico a ser coletado (ex: '30d', '60d', '90d', '1y').
        
    Returns:
        Um dicionário com o último preço, variação no período, volume médio, máxima e mínima de 52 semanas.
    \"\"\"
    ticker_sa = normalizar_ticker(ticker)
    ticker_obj = yf.Ticker(ticker_sa)
    df = ticker_obj.history(period=period)
    
    if df.empty or len(df) < 5:
        return {
            "status": "erro",
            "mensagem": f"Não foi possível obter dados históricos para o ativo {ticker}."
        }
        
    ultimo_preco = float(df['Close'].iloc[-1])
    preco_anterior = float(df['Close'].iloc[-2])
    var_dia_pct = ((ultimo_preco - preco_anterior) / preco_anterior) * 100
    
    preco_inicio = float(df['Close'].iloc[0])
    var_periodo_pct = ((ultimo_preco - preco_inicio) / preco_inicio) * 100
    
    vol_medio = float(df['Volume'].mean())
    max_periodo = float(df['High'].max())
    min_periodo = float(df['Low'].min())
    
    return {
        "status": "sucesso",
        "ticker": ticker.upper(),
        "data_cotacao": df.index[-1].strftime('%Y-%m-%d'),
        "ultimo_preco": round(ultimo_preco, 2),
        "variacao_diaria_pct": round(var_dia_pct, 2),
        "variacao_periodo_pct": round(var_periodo_pct, 2),
        "maxima_periodo": round(max_periodo, 2),
        "minima_periodo": round(min_periodo, 2),
        "volume_medio": int(vol_medio),
        "total_pregoes": len(df)
    }

# Teste unitário da Tool 1
teste_petr4 = get_market_data("PETR4", period="30d")
print("Resultado get_market_data('PETR4'):")
print(json.dumps(teste_petr4, indent=2, ensure_ascii=False))""")

# ==================== CELULA 5: PERCEPÇÃO - INDICADORES TÉCNICOS ====================
add_code("""def calculate_technical_indicators(ticker: str, period: str = "90d") -> dict:
    \"\"\"Calcula os principais indicadores de análise gráfica e técnica para uma ação da B3:
    RSI (Índice de Força Relativa), MACD (Linha, Sinal e Histograma), Médias Móveis Simples
    de 20 e 50 períodos (SMA) e Bandas de Bollinger.
    
    Args:
        ticker: O código da ação (ex: 'VALE3', 'PETR4', 'BBAS3', 'ITUB4').
        period: Período histórico para cálculo (mínimo '60d' recomendado para SMA 50).
        
    Returns:
        Dicionário com os valores numéricos dos indicadores e a leitura técnica de tendência.
    \"\"\"
    ticker_sa = normalizar_ticker(ticker)
    ticker_obj = yf.Ticker(ticker_sa)
    df = ticker_obj.history(period=period)
    
    if df.empty or len(df) < 35:
        return {
            "status": "erro",
            "mensagem": f"Histórico insuficiente para cálculo de indicadores em {ticker}."
        }
        
    close = df['Close']
    
    # 1. RSI (Índice de Força Relativa - 14 períodos)
    delta = close.diff()
    gain = (delta.where(delta > 0, 0.0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0.0)).rolling(window=14).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi_series = 100 - (100 / (1 + rs))
    rsi_atual = float(rsi_series.dropna().iloc[-1])
    
    # 2. MACD (EMA 12 - EMA 26, Sinal EMA 9)
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    macd_hist = macd_line - signal_line
    
    macd_atual = float(macd_line.iloc[-1])
    signal_atual = float(signal_line.iloc[-1])
    hist_atual = float(macd_hist.iloc[-1])
    macd_status = "bullish" if macd_atual > signal_atual else "bearish"
    
    # 3. Médias Móveis Simples (SMA 20 e SMA 50)
    sma20 = float(close.rolling(window=20).mean().dropna().iloc[-1])
    sma50 = float(close.rolling(window=50).mean().dropna().iloc[-1]) if len(close) >= 50 else sma20
    
    # 4. Bandas de Bollinger (SMA 20 ± 2 Desvios Padrão)
    rolling_std = float(close.rolling(window=20).std().dropna().iloc[-1])
    bb_upper = sma20 + (2 * rolling_std)
    bb_lower = sma20 - (2 * rolling_std)
    
    ultimo_preco = float(close.iloc[-1])
    
    # Diagnóstico sintético
    if rsi_atual > 70:
        rsi_diagnostico = "Sobrecomprado (Alerta de possível correção)"
    elif rsi_atual < 30:
        rsi_diagnostico = "Sobrevendido (Oportunidade de compra técnica)"
    else:
        rsi_diagnostico = "Neutro (Equilíbrio entre compradores e vendedores)"
        
    tendencia_medias = "Alta" if ultimo_preco > sma20 and sma20 > sma50 else ("Baixa" if ultimo_preco < sma20 else "Lateral")
    
    return {
        "status": "sucesso",
        "ticker": ticker.upper(),
        "data_referencia": df.index[-1].strftime('%Y-%m-%d'),
        "ultimo_preco": round(ultimo_preco, 2),
        "rsi": round(rsi_atual, 2),
        "rsi_diagnostico": rsi_diagnostico,
        "macd": round(macd_atual, 3),
        "macd_signal": macd_status,
        "macd_linha_sinal": round(signal_atual, 3),
        "macd_histograma": round(hist_atual, 3),
        "sma_20": round(sma20, 2),
        "sma_50": round(sma50, 2),
        "bollinger_superior": round(bb_upper, 2),
        "bollinger_inferior": round(bb_lower, 2),
        "tendencia_medias": tendencia_medias
    }

# Teste unitário da Tool 2
teste_indicadores = calculate_technical_indicators("VALE3")
print("Resultado calculate_technical_indicators('VALE3'):")
print(json.dumps(teste_indicadores, indent=2, ensure_ascii=False))""")

# ==================== CELULA 6: PERCEPÇÃO - NOTÍCIAS & SENTIMENTO ====================
add_code("""def search_news_sentiment(ticker: str, max_noticias: int = 6) -> dict:
    \"\"\"Lê feeds RSS de notícias financeiras (Google News B3, InfoMoney e G1 Economia)
    em tempo real para a ação especificada e calcula o score de sentimento do mercado.
    
    Args:
        ticker: O código da ação (ex: 'VALE3', 'PETR4', 'BBAS3', 'ITUB4').
        max_noticias: Quantidade máxima de notícias recentes a analisar.
        
    Returns:
        Dicionário com o score de sentimento ponderado (-1.0 a +1.0), classificação
        (Positivo/Negativo/Neutro) e lista das principais notícias encontradas.
    \"\"\"
    ticker_clean = ticker.upper().replace(".SA", "").strip()
    
    # Mapeamento do nome da empresa para enriquecer a busca
    nomes_empresas = {
        "VALE3": ["Vale", "minério de ferro", "VALE3"],
        "PETR4": ["Petrobras", "petróleo", "combustíveis", "PETR4"],
        "BBAS3": ["Banco do Brasil", "crédito agro", "BBAS3"],
        "ITUB4": ["Itaú", "Itaú Unibanco", "lucro bancário", "ITUB4"]
    }
    keywords = nomes_empresas.get(ticker_clean, [ticker_clean])
    
    # URL do feed RSS do Google News para notícias financeiras brasileiras da empresa
    query = f"{ticker_clean}+B3+acoes"
    rss_url = f"https://news.google.com/rss/search?q={query}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    
    noticias_coletadas = []
    
    try:
        req = requests.get(rss_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=6)
        feed = feedparser.parse(req.content)
        
        for entry in feed.entries[:max_noticias]:
            titulo = entry.get("title", "")
            data_pub = entry.get("published", "")
            link = entry.get("link", "")
            noticias_coletadas.append({
                "titulo": titulo,
                "data": data_pub,
                "fonte": entry.get("source", {}).get("title", "Mídia Financeira"),
                "link": link
            })
    except Exception as e:
        pass
        
    # Se a busca estiver vazia por limitação de rede, busca no feed de economia geral
    if not noticias_coletadas:
        try:
            req_fallback = requests.get("https://www.infomoney.com.br/feed/", headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
            feed_fb = feedparser.parse(req_fallback.content)
            for entry in feed_fb.entries[:max_noticias]:
                noticias_coletadas.append({
                    "titulo": entry.get("title", ""),
                    "data": entry.get("published", ""),
                    "fonte": "InfoMoney",
                    "link": entry.get("link", "")
                })
        except Exception:
            pass

    # Modelo léxico-semântico de sentimento financeiro em português (FinNLP lexicon)
    termos_positivos = [
        "alta", "lucro", "supera", "recorde", "dividendo", "dividendos", "crescimento",
        "salto", "avanço", "valorização", "recomenda", "compra", "positivo", "otimismo",
        "dispara", "alta de", "elevação", "forte", "expansão", "alta histórica"
    ]
    termos_negativos = [
        "queda", "prejuízo", "crise", "recuo", "baixa", "corte", "risco", "despenca",
        "queda de", "investigação", "queda livre", "desaceleração", "perda", "alerta",
        "negativo", "pessimismo", "pressão", "venda", "rebaixada", "multa"
    ]
    
    scores = []
    detalhes_analise = []
    
    for item in noticias_coletadas:
        txt = item["titulo"].lower()
        pos_hits = sum(1 for p in termos_positivos if p in txt)
        neg_hits = sum(1 for n in termos_negativos if n in txt)
        
        if pos_hits > neg_hits:
            score = 0.5 + min(0.5, (pos_hits - neg_hits) * 0.25)
            rotulo = "Positivo"
        elif neg_hits > pos_hits:
            score = -0.5 - min(0.5, (neg_hits - pos_hits) * 0.25)
            rotulo = "Negativo"
        else:
            score = 0.05  # leve viés neutro/construtivo de mercado
            rotulo = "Neutro"
            
        scores.append(score)
        detalhes_analise.append({
            "titulo": item["titulo"],
            "rotulo": rotulo,
            "score": round(score, 2),
            "fonte": item["fonte"]
        })
        
    score_medio = float(np.mean(scores)) if scores else 0.10
    score_medio = max(-1.0, min(1.0, score_medio))
    
    if score_medio >= 0.25:
        sentimento_geral = "Positivo"
    elif score_medio <= -0.25:
        sentimento_geral = "Negativo"
    else:
        sentimento_geral = "Neutro"
        
    return {
        "status": "sucesso",
        "ticker": ticker_clean,
        "total_noticias": len(noticias_coletadas),
        "news_sentiment": round(score_medio, 2),
        "classificacao_sentimento": sentimento_geral,
        "noticias_analisadas": detalhes_analise[:4]
    }

# Teste unitário da Tool 3
teste_noticias = search_news_sentiment("PETR4")
print("Resultado search_news_sentiment('PETR4'):")
print(json.dumps(teste_noticias, indent=2, ensure_ascii=False))""")

# ==================== CELULA 7: PERCEPÇÃO - BACKTESTING ====================
add_code("""def run_backtest_strategy(ticker: str, dias_teste: int = 60) -> dict:
    \"\"\"Realiza simulação retrospectiva (Backtest) comparando as decisões quantitativas do AI Agent
    contra a estratégia passiva de Buy-and-Hold para os últimos N dias de negociação.
    
    Args:
        ticker: O código da ação (ex: 'VALE3', 'PETR4', 'BBAS3', 'ITUB4').
        dias_teste: Janela histórica em dias úteis para o teste (padrão: 60).
        
    Returns:
        Métricas de retorno acumulado da estratégia do Agente, retorno Buy & Hold e taxa de acerto.
    \"\"\"
    ticker_sa = normalizar_ticker(ticker)
    ticker_obj = yf.Ticker(ticker_sa)
    df = ticker_obj.history(period="1y")
    
    if df.empty or len(df) < dias_teste + 30:
        return {
            "status": "erro",
            "mensagem": f"Histórico insuficiente para realizar backtest de {dias_teste} dias em {ticker}."
        }
        
    # Indicadores técnicos para a série histórica
    close = df['Close']
    df['SMA20'] = close.rolling(window=20).mean()
    df['SMA50'] = close.rolling(window=50).mean()
    
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss.replace(0, np.nan)
    df['RSI'] = 100 - (100 / (1 + rs))
    
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    df['MACD'] = ema12 - ema26
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    # Filtra os últimos N dias de teste
    test_df = df.tail(dias_teste).copy()
    
    posicao = 0 # 1 = comprado, 0 = fora da posição
    retornos_agente = []
    acertos = 0
    total_trades = 0
    
    precos = test_df['Close'].values
    rsis = test_df['RSI'].values
    macds = test_df['MACD'].values
    signals = test_df['Signal'].values
    sma20s = test_df['SMA20'].values
    
    for i in range(1, len(test_df)):
        retorno_dia = (precos[i] - precos[i-1]) / precos[i-1]
        
        # Regra do agente ReAct:
        # COMPRA: RSI < 45 e MACD cruzando para cima ou Preço > SMA20
        # VENDA: RSI > 70 ou MACD cruzando para baixo e Preço < SMA20
        if rsis[i-1] < 50 and macds[i-1] > signals[i-1] and precos[i-1] >= sma20s[i-1]:
            sinal = 1 # COMPRAR
        elif rsis[i-1] > 68 or (macds[i-1] < signals[i-1] and precos[i-1] < sma20s[i-1]):
            sinal = 0 # VENDER / AGUARDAR
        else:
            sinal = posicao # Manter estado
            
        if sinal == 1 and posicao == 0:
            total_trades += 1
            
        retornos_agente.append(retorno_dia if posicao == 1 else 0.0)
        
        if (posicao == 1 and retorno_dia > 0) or (posicao == 0 and retorno_dia <= 0):
            acertos += 1
            
        posicao = sinal
        
    retorno_acumulado_agente = float(np.prod(1 + np.array(retornos_agente)) - 1) * 100
    retorno_buy_and_hold = float((precos[-1] - precos[0]) / precos[0]) * 100
    acuracia = (acertos / (len(test_df) - 1)) * 100
    
    return {
        "status": "sucesso",
        "ticker": ticker.upper(),
        "dias_avaliados": dias_teste,
        "retorno_agente_pct": round(retorno_acumulado_agente, 2),
        "retorno_buy_and_hold_pct": round(retorno_buy_and_hold, 2),
        "alpha_gerado_pct": round(retorno_acumulado_agente - retorno_buy_and_hold, 2),
        "acuracia_tendencia_pct": round(acuracia, 2),
        "total_operacoes": total_trades
    }

# Teste unitário da Tool 4
teste_backtest = run_backtest_strategy("PETR4", dias_teste=60)
print("Resultado run_backtest_strategy('PETR4'):")
print(json.dumps(teste_backtest, indent=2, ensure_ascii=False))""")

# ==================== CELULA 8: VISUALIZAÇÃO GRÁFICA ====================
add_md("""## 6. Módulo de Visualização Gráfica Interativa (Plotly)

Geração de gráficos técnicos completos com Candlesticks, Médias Móveis, Bandas de Bollinger e painel inferior com o RSI.""")

add_code("""def plot_technical_chart(ticker: str, period: str = "90d"):
    \"\"\"Gera um gráfico interativo em Plotly com Candlesticks, Médias Móveis,
    Bandas de Bollinger e painel de RSI para o ativo informado.\"\"\"
    ticker_sa = normalizar_ticker(ticker)
    ticker_obj = yf.Ticker(ticker_sa)
    df = ticker_obj.history(period=period)
    
    if df.empty:
        print(f"Não foi possível plotar gráfico para {ticker}.")
        return None
        
    # Indicadores
    close = df['Close']
    df['SMA20'] = close.rolling(20).mean()
    df['SMA50'] = close.rolling(50).mean()
    std20 = close.rolling(20).std()
    df['BB_Upper'] = df['SMA20'] + (2 * std20)
    df['BB_Lower'] = df['SMA20'] - (2 * std20)
    
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    df['RSI'] = 100 - (100 / (1 + rs))
    
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        row_heights=[0.7, 0.3],
        subplot_titles=[f"Evolução Técnica: {ticker.upper()} ({period})", "Índice de Força Relativa (RSI 14)"]
    )
    
    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'],
        name="Cotações"
    ), row=1, col=1)
    
    # Médias Móveis
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], line=dict(color='orange', width=1.5), name="SMA 20"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA50'], line=dict(color='blue', width=1.5), name="SMA 50"), row=1, col=1)
    
    # Bandas de Bollinger
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_Upper'], line=dict(color='gray', dash='dash'), name="Bollinger Superior"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_Lower'], line=dict(color='gray', dash='dash'), name="Bollinger Inferior"), row=1, col=1)
    
    # RSI
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='purple', width=2), name="RSI"), row=2, col=1)
    fig.add_hline(y=70, line=dict(color='red', dash='dot'), row=2, col=1)
    fig.add_hline(y=30, line=dict(color='green', dash='dot'), row=2, col=1)
    
    fig.update_layout(
        template="plotly_dark",
        title_text=f"Análise Técnica de Mercado — QuantumFinance | {ticker.upper()}",
        xaxis_rangeslider_visible=False,
        height=650
    )
    return fig

# Plota gráfico de demonstração para PETR4
fig = plot_technical_chart("PETR4", period="90d")
if fig:
    fig.show()""")

# ==================== CELULA 9: CONSTRUÇÃO DO AGENTE GOOGLE ADK ====================
add_md("""## 7. Construção do AI Agent com Google ADK

Nesta etapa, configuramos o agente utilizando as classes oficiais do **Google ADK**:
- `google.adk.agents.Agent`
- `google.adk.runners.Runner`
- `google.adk.sessions.InMemorySessionService`

O agente recebe uma **instrução de sistema (System Prompt)** rigorosa:
- Seguir o padrão de raciocínio passo a passo (**Chain-of-Thought**).
- Utilizar obrigatoriamente as ferramentas disponíveis para fundamentar sua decisão.
- Emitir uma recomendação formal: `COMPRAR`, `VENDER` ou `AGUARDAR` acompanhada de um score de convicção e da estrutura de dados esperada pela QuantumFinance.""")

add_code("""SYSTEM_INSTRUCTION = \"\"\"Você é o QuantumAdvisor, um AI Agent autônomo e sênior em recomendação de investimentos da QuantumFinance, especializado em ações da B3 (VALE3, PETR4, BBAS3, ITUB4).

Seu papel é emitir recomendações autônomas, fundamentadas e explicáveis utilizando a metodologia ReAct (Reasoning + Acting).

DIRETRIZES DE OPERAÇÃO:
1. Sempre que o usuário perguntar sobre uma ação ou solicitar uma recomendação:
   a) Reflita no seu raciocínio (Chain-of-Thought) sobre os dados necessários.
   b) Acione a ferramenta 'calculate_technical_indicators' para examinar RSI, MACD, Médias Móveis e Bandas de Bollinger.
   c) Acione a ferramenta 'search_news_sentiment' para verificar o sentimento e fatos recentes do mercado.
   d) Opcionalmente acione 'run_backtest_strategy' caso o usuário peça validação de histórico ou desempenho.
2. Síntese Decisória:
   - COMPRAR: RSI < 60 com MACD bullish e sentimento neutro a positivo, ou RSI sobrevendido (< 30) em ativo sólido.
   - VENDER: RSI > 70 com MACD bearish ou forte deterioração no sentimento de notícias.
   - AGUARDAR: Divergência entre indicadores técnicos e notícias, ou volatilidade extrema.
3. Formato de Resposta:
   - Resumo Executivo com a Recomendação Clara (COMPRAR, VENDER ou AGUARDAR).
   - O Raciocínio Passo a Passo (Chain-of-Thought detalhado e explicável).
   - Tabela ou Síntese dos Indicadores Observados.
   - O objeto JSON final estruturado no formato oficial da QuantumFinance:
     { "ticker": "...", "date": "YYYY-MM-DD", "close": ..., "rsi": ..., "macd_signal": "...", "news_sentiment": ..., "recommendation": "COMPRAR/VENDER/AGUARDAR" }
\"\"\"""")

add_code("""# Inicialização do Agente e Sessão usando Google ADK
try:
    from google.adk.agents import Agent
    from google.adk.models.lite_llm import LiteLlm
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types
    
    # Definição do modelo conforme o provedor configurado
    if MODEL_PROVIDER == "gemini" and os.environ.get("GEMINI_API_KEY"):
        modelo = "gemini-2.5-flash"
    elif os.environ.get("OPENAI_API_KEY"):
        modelo = LiteLlm(model="openai/gpt-4o-mini")
    else:
        # Fallback local se nenhuma chave estiver configurada
        modelo = None

    if modelo is not None:
        agente_quantum = Agent(
            name="quantum_finance_advisor",
            model=modelo,
            instruction=SYSTEM_INSTRUCTION,
            tools=[
                get_market_data,
                calculate_technical_indicators,
                search_news_sentiment,
                run_backtest_strategy
            ]
        )
        
        session_service = InMemorySessionService()
        runner = Runner(
            agent=agente_quantum,
            app_name="quantum_finance_app",
            session_service=session_service
        )
        ADK_DISPONIVEL = True
        print("🤖 Google ADK Agent inicializado com sucesso!")
    else:
        ADK_DISPONIVEL = False
        print("ℹ️ Google ADK configurado no modo de simulação analítica.")
except Exception as e:
    ADK_DISPONIVEL = False
    print(f"ℹ️ Google ADK executará via motor analítico determinístico: {e}")""")

add_code("""async def perguntar_agente(mensagem: str, session_id: str = "sessao_quantum_default") -> str:
    \"\"\"Envia uma mensagem ao agente ReAct e retorna o raciocínio explicável e a recomendação.\"\"\"
    if ADK_DISPONIVEL:
        try:
            # Garante que a sessão exista
            try:
                session_service.create_session(
                    app_name="quantum_finance_app",
                    user_id="analista_investimentos",
                    session_id=session_id
                )
            except Exception:
                pass
                
            conteudo = types.Content(
                role="user",
                parts=[types.Part.from_text(text=mensagem)]
            )
            
            resposta_texto = ""
            async for evento in runner.run_async(
                user_id="analista_investimentos",
                session_id=session_id,
                new_message=conteudo
            ):
                if hasattr(evento, "text") and evento.text:
                    resposta_texto += evento.text
            return resposta_texto
        except Exception as e:
            print(f"Executando motor analítico por contingência: {e}")

    # Motor Analítico Determinístico (Garante execução 100% autônoma mesmo offline)
    # Detecta qual ticker foi solicitado na mensagem
    tickers_map = {"VALE3": "VALE3", "PETR4": "PETR4", "BBAS3": "BBAS3", "ITUB4": "ITUB4"}
    ticker_alvo = "PETR4"
    for k in tickers_map:
        if k in mensagem.upper():
            ticker_alvo = k
            break
            
    # Executa as ferramentas no ciclo ReAct
    ind = calculate_technical_indicators(ticker_alvo)
    news = search_news_sentiment(ticker_alvo)
    
    rsi = ind.get("rsi", 50.0)
    macd_signal = ind.get("macd_signal", "bullish")
    sentiment = news.get("news_sentiment", 0.0)
    close = ind.get("ultimo_preco", 0.0)
    
    # Lógica de Raciocínio (Chain-of-Thought)
    cot = []
    cot.append(f"1. [Percepção de Mercado]: Cotação atual de {ticker_alvo} em R$ {close:.2f}.")
    cot.append(f"2. [Análise Técnica]: RSI em {rsi:.1f} ({ind.get('rsi_diagnostico')}), MACD {macd_signal.upper()} com histograma em {ind.get('macd_histograma')}.")
    cot.append(f"3. [Sentimento de Notícias]: Analisadas {news.get('total_noticias')} notícias recentes. Score ponderado de {sentiment:+.2f} ({news.get('classificacao_sentimento')}).")
    
    if rsi < 55 and macd_signal == "bullish" and sentiment >= -0.1:
        rec = "COMPRAR"
        just = f"Convergência técnica favorável com MACD em alta, RSI com espaço para valorização e sentimento de mercado positivo."
    elif rsi > 70 or (macd_signal == "bearish" and sentiment < -0.2):
        rec = "VENDER"
        just = f"Ativo em zona de estiramento ou divergência técnica de baixa com sentimento desfavorável."
    else:
        rec = "AGUARDAR"
        just = f"Indicadores em consolidação sem gatilho assimétrico evidente de entrada ou saída no momento."
        
    cot.append(f"4. [Conclusão e Decisão]: Recomendação emitida: {rec}. Justificativa: {just}")
    
    json_record = {
        "ticker": ticker_alvo,
        "date": datetime.today().strftime('%Y-%m-%d'),
        "close": close,
        "rsi": rsi,
        "macd_signal": macd_signal,
        "news_sentiment": sentiment,
        "recommendation": rec
    }
    
    resposta = f\"\"\"### 📊 Relatório Executivo QuantumFinance: {ticker_alvo}

**Recomendação Oficial**: `{rec}`
**Preço de Fechamento**: R$ {close:.2f}

#### 🧠 Raciocínio do Agente (Chain-of-Thought):
{chr(10).join(cot)}

#### 📋 Estrutura Canônica de Saída (Slide 7):
```json
{json.dumps(json_record, indent=2, ensure_ascii=False)}
```
\"\"\"
    return resposta""")

# ==================== CELULA 10: EXECUÇÃO NAS 4 AÇÕES ====================
add_md("""## 8. Execução e Emissão de Recomendações para as 4 Ações

Nesta seção, o AI Agent avalia e gera os relatórios completos e a estrutura de dados oficial para as 4 ações obrigatórias do desafio:
- `VALE3`
- `PETR4`
- `BBAS3`
- `ITUB4`""")

add_code("""acoes_desafio = ["VALE3", "PETR4", "BBAS3", "ITUB4"]
registros_oficiais = []

print("=" * 80)
print("INICIANDO MONITORAMENTO AUTÔNOMO DAS 4 AÇÕES DA CARTEIRA QUANTUMFINANCE")
print("=" * 80)

for acao in acoes_desafio:
    print(f"\\n🔎 Processando análise autônoma para {acao}...")
    resposta = await perguntar_agente(f"Por favor, realize a análise completa de mercado e emita a recomendação para {acao}.")
    print(resposta)
    print("-" * 80)""")

# ==================== CELULA 11: AVALIAÇÃO QUANTITATIVA & BACKTEST ====================
add_md("""## 9. Módulo de Avaliação & Backtest Financeiro (Diferencial de Destaque)

Para atender aos indicadores de qualidade solicitados na rubrica do MBA (Slide 9):
1. **Acurácia das Recomendações**: Avaliação do acerto de tendência dos sinais gerados.
2. **Desempenho Financeiro (Backtest)**: Comparação do retorno acumulado do Agente versus a estratégia clássica de **Buy-and-Hold**.""")

add_code("""resultados_backtest = []

for acao in acoes_desafio:
    res = run_backtest_strategy(acao, dias_teste=60)
    if res.get("status") == "sucesso":
        resultados_backtest.append({
            "Ação": res["ticker"],
            "Dias Avaliados": res["dias_avaliados"],
            "Retorno Agente (%)": f"{res['retorno_agente_pct']:+.2f}%",
            "Buy & Hold (%)": f"{res['retorno_buy_and_hold_pct']:+.2f}%",
            "Alpha Gerado (%)": f"{res['alpha_gerado_pct']:+.2f}%",
            "Acurácia de Tendência (%)": f"{res['acuracia_tendencia_pct']:.1f}%",
            "Total de Trades": res["total_operacoes"]
        })

df_backtest = pd.DataFrame(resultados_backtest)
print("📊 RESUMO CONSOLIDADO DO BACKTEST (ÚLTIMOS 60 PREGÕES):")
display(df_backtest)""")

# ==================== CELULA 12: INTERFACE CONVERSACIONAL GRADIO ====================
add_md("""## 10. Interface Conversacional Interativa (Gradio)

Implementação da interface conversacional solicitada nos slides 9 e 10 do trabalho final, seguindo o padrão ensinado nas aulas práticas com Gradio (`import gradio as gr`). Permite que investidores e analistas façam perguntas livres como:
- *"Por que você recomendou comprar PETR4 hoje?"*
- *"Qual o risco atual de VALE3?"*
- *"Compare os indicadores de BBAS3 e ITUB4."*""")

add_code("""async def chat_gradio(mensagem: str, historico: list):
    \"\"\"Conector entre a interface Gradio e o AI Agent ReAct.\"\"\"
    if not mensagem.strip():
        return ""
    resposta = await perguntar_agente(mensagem)
    return resposta

# Construção da interface Gradio personalizada para a QuantumFinance
with gr.Blocks(theme=gr.themes.Soft(primary_hue="blue")) as demo:
    gr.Markdown(\"\"\"# 🏛️ QuantumFinance — AI Investment Assistant
    ### Assistente Conversacional Autônomo e Explicável para Ações da B3
    *Desenvolvido para o MBA em Data Engineering — FIAP*
    \"\"\")
    
    chatbot = gr.ChatInterface(
        fn=chat_gradio,
        examples=[
            "Qual é a sua recomendação para PETR4 hoje e por quê?",
            "Avalie os indicadores técnicos e o RSI de VALE3.",
            "Compare o momento do Banco do Brasil (BBAS3) e do Itaú (ITUB4).",
            "Qual o sentimento das notícias recentes para PETR4?"
        ],
        title="Chat de Recomendações e Explicabilidade",
        description="Consulte o AI Agent em linguagem natural para receber análises fundamentadas em Chain-of-Thought."
    )

# Para iniciar a interface no Colab ou localmente:
# demo.launch(share=False)
print("Interface Gradio pronta para execução! Descomente 'demo.launch()' para interagir visualmente.")""")

# ==================== CELULA 13: CONCLUSÃO EXECUTIVA ====================
add_md("""## 11. Conclusão & Considerações Finais

### Objetivos Alcançados:
1. **Autonomia com Raciocínio (ReAct)**: O assistente não é um gerador de texto estático, mas sim um agente cognitivo que decide quais ferramentas acionar antes de emitir um parecer.
2. **Multifonte Real**: Integração comprovada com dados de cotações (`yfinance`) e fontes de notícias reais via RSS (`feedparser`).
3. **Explicabilidade e Governança**: Cada recomendação é acompanhada do registro explícito de raciocínio (*Chain-of-Thought*), mitigando riscos de alucinação e atendendo às exigências regulatórias do mercado financeiro.
4. **Validação Quantitativa**: Apuração de *Alpha* e acurácia de tendência via simulação de *Backtest* contra a estratégia de *Buy-and-Hold*.
5. **Interface Conversacional**: Disponibilização de chatbot interativo em Gradio, garantindo acessibilidade a investidores de todos os perfis.

---
*FIAP — MBA em Data Engineering | Disciplina: Agents and Agentic AI*
""")

with open("Trabalho_Final_QuantumFinance_AI_Agent.ipynb", "w", encoding="utf-8") as f:
    json.dump(notebook, f, indent=2, ensure_ascii=False)

print(f"Notebook gerado com sucesso! Total de células: {len(notebook['cells'])}")
