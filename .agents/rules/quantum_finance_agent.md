# Regras do Projeto - QuantumFinance AI Investment Assistant

1. **Estratégia ReAct Rígida**: Todas as recomendações de investimento (`COMPRAR`, `VENDER`, `AGUARDAR`) emitidas pelo agente inteligente devem seguir explicitamente o padrão de raciocínio passo a passo (Chain-of-Thought). O agente deve registrar as evidências técnicas e contextuais de cada ferramenta antes de concluir.
2. **Padrão Google ADK**: Manter estrita compatibilidade com o framework `google-adk` utilizado pelo Professor Felipe Teodoro nas aulas da FIAP, garantindo o uso de:
   - `google.adk.agents.Agent`
   - `google.adk.runners.Runner`
   - `google.adk.sessions.InMemorySessionService`
   - `google.adk.models.lite_llm.LiteLlm` ou modelos Gemini diretos
   - `gradio` para interface conversacional
3. **Privacidade e Proteção de Segredos**: Nunca expor, salvar ou registrar tokens de API de professores ou usuários em arquivos de código ou documentação.
4. **Tríade de Capacidades do Agente**:
   - Percepção: APIs de mercado (`yfinance`) e feeds RSS (`feedparser`).
   - Raciocínio: Indicadores quantitativos (RSI, MACD, MM20/50, Bollinger) e sentimento NLP.
   - Ação: Recomendações estruturadas (formato JSON da aula) e chat interativo.
