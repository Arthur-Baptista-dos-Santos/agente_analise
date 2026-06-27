from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from src.ferramentas import verificar_pipeline, analisar_dados, detectar_anomalias

LLM = ChatOllama(model="llama3.2", temperature=0)

FERRAMENTAS = [verificar_pipeline, analisar_dados, detectar_anomalias]

SYSTEM_PROMPT = """Voce e um agente de monitoramento de pipeline de dados.

REGRA ABSOLUTA: Voce NUNCA deve inventar dados ou responder com informacoes da sua memoria.
Voce TEM QUE usar as ferramentas disponiveis para obter dados reais antes de responder.

Ferramentas disponiveis:
- verificar_pipeline: verifica se os arquivos do ETL existem e quando foram gerados
- analisar_dados: le o banco DuckDB e retorna metricas reais dos dados
- detectar_anomalias: detecta valores fora do padrao estatistico

Para qualquer pergunta sobre o pipeline ou dados de vendas, chame as ferramentas primeiro.
Baseie sua resposta EXCLUSIVAMENTE nos dados retornados pelas ferramentas."""

agente = create_react_agent(LLM, FERRAMENTAS, prompt=SYSTEM_PROMPT)


def monitorar(tarefa: str) -> str:
    """Executa o agente com a tarefa recebida e retorna a resposta final."""
    resultado = agente.invoke({
        "messages": [HumanMessage(content=tarefa)]
    })
    return resultado["messages"][-1].content
