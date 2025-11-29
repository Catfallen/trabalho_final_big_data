import pandas as pd
import streamlit as st
from pathlib import Path
import matplotlib.pyplot as plt
from io import BytesIO

def main():
    st.set_page_config(page_title="Análise de Veículos", layout="wide")
    st.title("🚚 Análise de Veículos - Top Tipos com Mais Registros")

    # ------------------------------
    # Carregar CSV
    # ------------------------------
    caminho = Path("saida.csv")
    arquivo = st.file_uploader("Envie o CSV (opcional)", type=["csv"])
    
    if arquivo:
        df = pd.read_csv(arquivo, sep=";")
    elif caminho.exists():
        df = pd.read_csv(caminho, sep=";")
    else:
        st.error("Nenhum CSV encontrado e nenhum arquivo enviado.")
        st.stop()

    # ------------------------------
    # Processar coluna tag_equipamento
    # ------------------------------
    if "tag_equipamento" not in df.columns:
        st.error("A coluna 'tag_equipamento' não existe no CSV.")
        st.stop()

    df['tipo'] = df['tag_equipamento'].astype(str).str.split('-').str[0]
    df['veiculo'] = df['tag_equipamento'].astype(str).str.split('-').str[1]
    df_validos = df[df['tipo'].str.match(r'^[A-Za-z]+$')]

    if df_validos.empty:
        st.warning("Nenhum tipo válido encontrado após a filtragem.")
        st.stop()

    # ------------------------------
    # Dicionário de descrições
    # ------------------------------
    descricao_veiculos = {
        "CA": "Caminhão Aspirador", "CB": "Caminhão Basculante", "CC": "Caminhão Comboio",
        "CG": "Caminhão Guincho", "CM": "Caminhão Munck", "CP": "Caminhão Pipa",
        "CR": "Caminhão Rolo", "EH": "Escavadeira Hidráulica", "GA": "Guindaste Articulado",
        "GG": "Guindaste Giratório", "MB": "Motoniveladora", "MN": "Mini Carregadeira",
        "PC": "Pá Carregadeira", "PR": "Perfuratriz", "RC": "Rolo Compactador",
        "RE": "Retroescavadeira", "TE": "Trator Esteira", "TI": "Trator Industrial",
        "TP": "Trator de Pneus", "TS": "Trator Scraper", "VA": "Vibro Acabadora",
        "VTR": "Viatura"
    }

    # ------------------------------
    # Contagem de tipos
    # ------------------------------
    contagem_tipo = df_validos['tipo'].value_counts()
    tipo_mais_comum = contagem_tipo.idxmax()
    qtd_tipo = contagem_tipo.max()

    # Exibir tipo mais comum com chave e descrição
    st.subheader("🏆 Tipo de Veículo com Mais Registros")
    st.write(f"**{tipo_mais_comum}: {descricao_veiculos.get(tipo_mais_comum, tipo_mais_comum)}** "
             f"com **{qtd_tipo}** registros")

    # ------------------------------
    # Configuração de gráfico
    # ------------------------------
    grafico_tipo = st.selectbox("Selecione o tipo de gráfico", ["Barra", "Linha", "Pizza"])
    top_n = 5
    contagem_top = contagem_tipo.head(top_n)
    if grafico_tipo == "Barra":
        st.bar_chart(contagem_top)
    elif grafico_tipo == "Linha":
        st.line_chart(contagem_top)
    elif grafico_tipo == "Pizza":
        fig, ax = plt.subplots(figsize=(4, 4))
        wedges, texts, autotexts = ax.pie(
            contagem_top.values,
            labels=None,
            autopct='%1.1f%%',
            startangle=90
        )
        # Legenda com chave + descrição
        descricoes = [f"{k}: {descricao_veiculos.get(k, k)}" for k in contagem_top.index]
        ax.set_title(f"Top {top_n} Tipos de Veículos")
        ax.legend(descricoes, title="Tipos", loc="center left", bbox_to_anchor=(1, 0.5))
        buf = BytesIO()
        fig.savefig(buf, format="png", bbox_inches='tight')
        buf.seek(0)
        st.image(buf, width=500)
        plt.close(fig)

    # ------------------------------
    # Tabela detalhada de veículos
    # ------------------------------
    st.subheader("🚚 Veículos Detalhados")
    df_codigos = df_validos[df_validos['veiculo'].notna() & df_validos['veiculo'].astype(str).str.match(r'^[0-9]+$')]
    
    if df_codigos.empty:
        st.warning("Nenhum código de veículo válido encontrado.")
        return

    df_codigos["veiculo_full"] = df_codigos["tipo"] + "-" + df_codigos["veiculo"]
    contagem_veiculo = df_codigos["veiculo_full"].value_counts().reset_index()
    contagem_veiculo.columns = ["Veículo", "Quantidade"]
    contagem_veiculo["Tipo"] = contagem_veiculo["Veículo"].str.split("-").str[0]
    contagem_veiculo["Código"] = contagem_veiculo["Veículo"].str.split("-").str[1]
    contagem_veiculo["Descrição"] = contagem_veiculo["Tipo"].map(descricao_veiculos)
    contagem_veiculo = contagem_veiculo[["Veículo", "Tipo", "Descrição", "Código", "Quantidade"]]

    st.write("Clique nos cabeçalhos para ordenar por nome, tipo ou quantidade:")
    st.dataframe(contagem_veiculo, use_container_width=True)

if __name__ == "__main__":
    main()
