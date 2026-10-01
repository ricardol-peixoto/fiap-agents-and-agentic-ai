# Diretrizes do Projeto: QuantumFinance AI Investment Assistant

## 1. Visão Geral do Projeto
Este repositório contém a implementação do Trabalho Final da disciplina **Agents and Agentic AI** do curso de **MBA em Data Engineering** (FIAP), ministrado pelo **Professor Felipe Gustavo Silva Teodoro**.

O objetivo é desenvolver um Assistente de Investimentos autônomo e explicável baseado em **AI Agents** para a empresa fictícia **QuantumFinance**, focando em quatro ações prioritárias da B3:
- `VALE3` (Vale S.A. - Mineração)
- `PETR4` (Petrobras - Energia)
- `BBAS3` (Banco do Brasil - Setor Financeiro)
- `ITUB4` (Itaú Unibanco - Setor Financeiro)

## 2. Princípios de Arquitetura e Decisões Críticas
- **Padrão Obrigatório (ReAct - Reasoning + Acting)**: O agente não pode ser um mero pipeline sequencial de LLM. Ele deve refletir (*Thought*), acionar ferramentas especializadas (*Action / Tool Call*), analisar os retornos técnicos (*Observation*) e sintetizar uma recomendação fundamentada (*Final Answer*).
- **Framework Padrão**: **Google ADK** (`google-adk`), conforme praticado pelo professor nos notebooks de aula (`Agent`, `Runner`, `InMemorySessionService`, `LiteLlm` ou `gemini-2.5-flash`), com interface conversacional em **Gradio** (`import gradio as gr`).
- **Fontes de Dados Abertas e Robustas**:
  - Dados de Mercado: `yfinance` para histórico OHLCV (usando sufixo `.SA` para B3).
  - Análise Técnica: Cálculos nativos de RSI (14), MACD (12, 26, 9), Médias Móveis (SMA 20, SMA 50), Bandas de Bollinger e Volume.
  - Feeds de Notícias: `feedparser` lendo RSS direcionado (Google News Brasil para B3, InfoMoney e G1 Economia).
  - Sentimento NLP: FinBERT / VADER ou extração via LLM com prompt de finanças estruturado (-1.0 a +1.0).
- **Segurança de Credenciais**: Nenhuma chave de API deve ser versionada ou exposta. O agente utiliza `os.environ.get()` e inputs mascarados via `getpass`.

## 3. Estrutura dos Arquivos
- `Trabalho_Final_QuantumFinance_AI_Agent.ipynb`: Notebook principal de entrega, executável em Google Colab, Databricks Community Edition e ambiente local.
- `ARCHITECTURE.md`: Especificação técnica detalhada e diagramas Mermaid.
- `README.md`: Guia de execução, apresentação executiva e mapeamento da rubrica acadêmica.
- `resources/`: Transcrições das aulas e enunciados em PDF/DOCX (ignorado no git).
- `resources/notebooks_aula/`: Notebooks de referência das aulas ministradas pelo professor (ignorado no git).

## 4. Evolução Futura & Databricks Apps
- **Databricks Community Edition (Free)**: Garantir que qualquer pessoa consiga importar e executar o notebook gratuitamente sem fricção ou dependência de cloud paga.
- **Databricks Apps**: Estruturar a aplicação para possibilitar a publicação como um Databricks App (Gradio/Streamlit) servido nativamente no ecossistema Databricks.

