import gradio as gr
from src.agente import monitorar

SUGESTOES = [
    "Monitore o pipeline de vendas e gere um relatorio de saude completo",
    "Verifique se o pipeline ETL rodou corretamente hoje",
    "Analise a qualidade dos dados e detecte anomalias",
    "Qual vendedor tem a melhor performance? Analise os dados.",
]


def responder(mensagem: str, historico: list) -> str:
    return monitorar(mensagem)


with gr.Blocks(title="Agente de Monitoramento ETL") as interface:
    gr.Markdown("""
    # Agente de Monitoramento de Pipeline ETL
    Agente autonomo com LangGraph que monitora o pipeline de vendas, analisa qualidade dos dados e detecta anomalias.
    """)

    gr.ChatInterface(
        fn=responder,
        chatbot=gr.Chatbot(height=500),
        textbox=gr.Textbox(
            placeholder="Digite uma tarefa para o agente...",
            container=False,
        ),
        examples=SUGESTOES,
        title="",
    )

if __name__ == "__main__":
    interface.launch(share=False, theme=gr.themes.Soft())
