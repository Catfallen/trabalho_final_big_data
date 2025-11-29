import streamlit as st

# Importa os módulos (se estiverem na mesma pasta)
import meses
import servico
import divergencias
import tipo_equipamento
import sinonimos

import estado_global


# Configuração inicial do dashboard
st.set_page_config(page_title="Dashboard Geral", layout="wide")

st.sidebar.title("📊 Navegação")

pagina = st.sidebar.radio(
    "Escolha uma página:",
    (
        "Meses",
        "Serviço",
        "Divergências",
        "Veículos",
        "Sinônimos"
    ),
    key="menu_principal"
)


st.title("📘 Dashboard Geral")

# Chamadas de acordo com a página escolhida
if pagina == "Meses":
    st.header("📅 Análise por Meses")
    meses.main()          # <-- ALTERE caso seu arquivo não tenha função main()

elif pagina == "Serviço":
    st.header("🛠️ Análise de Serviços")
    servico.main()

elif pagina == "Divergências":
    st.header("🔍 Agrupamento de Divergências")
    divergencias.main()

elif pagina == "Veículos":
    tipo_equipamento.main()
elif pagina == "Sinônimos":
    st.header("Agrupamento de sinônimos")
    sinonimos.main()