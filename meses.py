import pandas as pd
import streamlit as st
from io import StringIO

def carregar_dados(caminho_arquivo, separador):
    """Carrega o CSV e trata erros básicos."""
    try:
        df = pd.read_csv(caminho_arquivo, sep=separador, encoding="utf-8")
        if df.empty:
            st.error("O arquivo CSV está vazio.")
            return None
        return df
    except FileNotFoundError:
        st.error(f"Arquivo '{caminho_arquivo}' não encontrado.")
        return None
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo: {e}")
        return None

def processar_datas(df, col_data):
    """Converte a coluna de data e extrai mês e ano."""
    if col_data not in df.columns:
        st.error(f"Coluna '{col_data}' não encontrada no CSV.")
        return None
    
    df[col_data] = pd.to_datetime(df[col_data], errors="coerce")
    df = df.dropna(subset=[col_data])
    if df.empty:
        st.warning("Nenhum registro válido após processar datas.")
        return None
    
    df["mes"] = df[col_data].dt.month
    df["ano"] = df[col_data].dt.year
    return df

def gerar_resumo(df, filtro_ano=None):
    """Agrupa por mês e calcula total e média."""
    if filtro_ano:
        df = df[df["ano"] == filtro_ano]
        if df.empty:
            st.warning(f"Nenhum registro encontrado para o ano {filtro_ano}.")
            return None
    
    resumo_anual = df.groupby(["ano", "mes"]).size().reset_index(name="registros")
    resumo = resumo_anual.groupby("mes").agg(
        total=("registros", "sum"),
        media=("registros", "mean")
    ).reset_index()
    
    meses_nome = {1:"Jan",2:"Fev",3:"Mar",4:"Abr",5:"Mai",6:"Jun",
                  7:"Jul",8:"Ago",9:"Set",10:"Out",11:"Nov",12:"Dez"}
    resumo["mes_nome"] = resumo["mes"].map(meses_nome)
    resumo = resumo.sort_values("mes")
    return resumo

def exibir_metrica_topo(resumo):
    """Exibe métricas compactas no topo."""
    if resumo is not None and not resumo.empty:
        total = resumo["total"].sum()
        media = resumo["total"].mean()
        max_mes = resumo.loc[resumo["total"].idxmax()]
        min_mes = resumo.loc[resumo["total"].idxmin()]
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total de registros", f"{total}")
        col2.metric("Média mensal", f"{media:.2f}")
        col3.metric("Mês mais ativo", f"{max_mes['mes_nome']}", f"{max_mes['total']} regs")
        col4.metric("Mês menos ativo", f"{min_mes['mes_nome']}", f"{min_mes['total']} regs")

def main():
    st.set_page_config(page_title="Análise por Mês", layout="wide")

    st.sidebar.header("Configurações")
    caminho_arquivo = st.sidebar.text_input("Caminho CSV", "saida.csv")
    separador = st.sidebar.selectbox("Separador", [";", ",", "\t"])
    filtro_ano = st.sidebar.number_input("Filtrar por ano (0 = todos)", 0, 9999, 0)
    filtro_ano = filtro_ano if filtro_ano > 0 else None

    df = carregar_dados(caminho_arquivo, separador)
    if df is None:
        return

    colunas_data = [c for c in df.columns if "data" in c.lower() or "date" in c.lower()]
    if colunas_data:
        col_data = st.sidebar.selectbox("Coluna de data", colunas_data)
    else:
        col_data = st.sidebar.text_input("Coluna de data", "DataEntrada")

    df = processar_datas(df, col_data)
    if df is None:
        return

    resumo = gerar_resumo(df, filtro_ano)
    if resumo is None:
        return

    # Métricas no topo
    exibir_metrica_topo(resumo)

    # Tabela resumida
    st.dataframe(resumo[["mes_nome","total","media"]].rename(columns={"mes_nome":"Mês","total":"Total","media":"Média"}), use_container_width=True)

    # Gráficos lado a lado com títulos
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Total de Registros por Mês")
        st.bar_chart(resumo.set_index("mes_nome")["total"], use_container_width=True)
    with col2:
        st.markdown("#### Média de Registros por Mês")
        st.bar_chart(resumo.set_index("mes_nome")["media"], use_container_width=True)

    # Download CSV
    csv_buffer = StringIO()
    resumo.to_csv(csv_buffer, index=False, sep=";")
    st.download_button("📥 Baixar Resumo", csv_buffer.getvalue(), "resumo_meses.csv", "text/csv")

if __name__ == "__main__":
    main()