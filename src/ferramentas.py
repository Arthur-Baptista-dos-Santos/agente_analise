from langchain_core.tools import tool
from pathlib import Path
from datetime import datetime
import duckdb
import pandas as pd

CAMINHO_ETL = Path("C:/PORTIFÓLIO/etl_airflow")
CAMINHO_DB = CAMINHO_ETL / "saida" / "vendas.db"
CAMINHO_RELATORIO = CAMINHO_ETL / "saida" / "relatorio.txt"
CAMINHO_CSV_BRUTO = CAMINHO_ETL / "dados" / "vendas_brutas.csv"
CAMINHO_CSV_TRANSFORMADO = CAMINHO_ETL / "dados" / "vendas_transformadas.csv"


@tool
def verificar_pipeline(dummy: str = "") -> str:
    """Verifica se o pipeline ETL rodou e quais arquivos foram gerados."""
    arquivos = {
        "CSV bruto": CAMINHO_CSV_BRUTO,
        "CSV transformado": CAMINHO_CSV_TRANSFORMADO,
        "Banco DuckDB": CAMINHO_DB,
        "Relatorio": CAMINHO_RELATORIO,
    }

    linhas = []
    for nome, caminho in arquivos.items():
        if caminho.exists():
            modificado = datetime.fromtimestamp(caminho.stat().st_mtime)
            linhas.append(f"[OK] {nome}: {modificado.strftime('%d/%m/%Y %H:%M')}")
        else:
            linhas.append(f"[AUSENTE] {nome}: arquivo nao encontrado")

    return "\n".join(linhas)


@tool
def analisar_dados(dummy: str = "") -> str:
    """Analisa a qualidade dos dados no banco DuckDB gerado pelo pipeline."""
    if not CAMINHO_DB.exists():
        return "Banco DuckDB nao encontrado. Execute o pipeline primeiro."

    con = duckdb.connect(str(CAMINHO_DB), read_only=True)

    total = con.execute("SELECT COUNT(*) FROM vendas").fetchone()[0]
    nulos = con.execute("""
        SELECT COUNT(*) FROM vendas
        WHERE vendedor IS NULL OR regiao IS NULL OR produto IS NULL
    """).fetchone()[0]

    receita_total = con.execute("SELECT ROUND(SUM(receita), 2) FROM vendas").fetchone()[0]
    lucro_total = con.execute("SELECT ROUND(SUM(lucro), 2) FROM vendas").fetchone()[0]
    margem_media = con.execute("SELECT ROUND(AVG(margem_pct), 2) FROM vendas").fetchone()[0]

    por_performance = con.execute("""
        SELECT performance, COUNT(*) as total
        FROM vendas GROUP BY performance ORDER BY total DESC
    """).fetchdf()

    con.close()

    linhas = [
        f"Total de registros: {total}",
        f"Registros com nulos: {nulos}",
        f"Receita total: R$ {receita_total:,.2f}",
        f"Lucro total: R$ {lucro_total:,.2f}",
        f"Margem media: {margem_media}%",
        "",
        "Distribuicao de performance:",
    ]
    for _, row in por_performance.iterrows():
        linhas.append(f"  {row['performance']}: {row['total']} vendas")

    return "\n".join(linhas)


@tool
def detectar_anomalias(dummy: str = "") -> str:
    """Detecta anomalias estatisticas nos dados de vendas."""
    if not CAMINHO_DB.exists():
        return "Banco DuckDB nao encontrado. Execute o pipeline primeiro."

    con = duckdb.connect(str(CAMINHO_DB), read_only=True)
    df = con.execute("SELECT * FROM vendas").fetchdf()
    con.close()

    anomalias = []

    for coluna in ["receita", "lucro", "margem_pct"]:
        media = df[coluna].mean()
        std = df[coluna].std()
        outliers = df[(df[coluna] > media + 2 * std) | (df[coluna] < media - 2 * std)]
        if not outliers.empty:
            for _, row in outliers.iterrows():
                anomalias.append(
                    f"[ANOMALIA] {coluna} fora do padrao: "
                    f"{row['vendedor']} / {row['produto']} = {row[coluna]:.2f} "
                    f"(media: {media:.2f}, desvio: {std:.2f})"
                )

    bruto = pd.read_csv(CAMINHO_CSV_BRUTO)
    nulos_bruto = bruto.isnull().sum().sum()
    if nulos_bruto > 0:
        anomalias.append(f"[QUALIDADE] {nulos_bruto} valores nulos no CSV bruto foram removidos no transform")

    if not anomalias:
        return "Nenhuma anomalia detectada. Dados dentro do padrao esperado."

    return "\n".join(anomalias)
