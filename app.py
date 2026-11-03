import pandas as pd
import plotly.express as px
import streamlit as st

# ----------------------------------------------------------------
# Configuração da página (título na aba do navegador e layout largo)
# ----------------------------------------------------------------
st.set_page_config(page_title="Painel do Tesouro Direto", layout="wide")

# Cada indexador terá sempre a mesma cor em todos os gráficos
CORES = {
    "Selic": "#1f77b4",
    "Prefixado": "#d62728",
    "IPCA+": "#2ca02c",
    "IGP-M+": "#9467bd",
}


def indexador(nome):
    """Classifica o título pelo indexador (mesma regra do notebook)."""
    if "Selic" in nome:
        return "Selic"
    if "Prefixado" in nome:
        return "Prefixado"
    if "IGPM" in nome:
        return "IGP-M+"
    return "IPCA+"  # IPCA+, Renda+ e Educa+


# ----------------------------------------------------------------
# Leitura e preparação dos dados
# @st.cache_data guarda o resultado na memória: o arquivo é lido
# uma vez só, e o app fica rápido quando o usuário clica em algo.
# ----------------------------------------------------------------
@st.cache_data
def carregar_dados():
    df = pd.read_csv(
        "precotaxatesourodireto.csv", sep=";", decimal=",", encoding="latin-1"
    )
    df["Data Base"] = pd.to_datetime(df["Data Base"], format="%d/%m/%Y")
    df["Data Vencimento"] = pd.to_datetime(df["Data Vencimento"], format="%d/%m/%Y")
    df["Anos ate Vencimento"] = (
        (df["Data Vencimento"] - df["Data Base"]).dt.days / 365.25
    ).round(1)
    df["Indexador"] = df["Tipo Titulo"].apply(indexador)
    # Só os títulos que estavam à venda (preço de compra maior que zero)
    return df[df["PU Compra Manha"] > 0]


df = carregar_dados()

# ----------------------------------------------------------------
# Cabeçalho
# ----------------------------------------------------------------
st.header("Painel do Tesouro Direto: taxas e prazos")
st.write(
    "Explore as taxas dos títulos públicos vendidos no Tesouro Direto. "
    "Fonte: Tesouro Transparente (Taxas dos Títulos Ofertados pelo Tesouro Direto)."
)
st.caption(
    "Atenção: a taxa tem significado diferente em cada indexador. "
    "Selic = adicional sobre a Selic; Prefixado = taxa nominal; "
    "IPCA+ e IGP-M+ = ganho acima da inflação."
)

# ----------------------------------------------------------------
# Gráfico 1: histograma (aparece quando a caixinha é marcada)
# ----------------------------------------------------------------
if st.checkbox("Mostrar histograma das taxas"):
    st.write("Com que frequência cada faixa de taxa apareceu, por indexador.")
    fig_hist = px.histogram(
        df,
        x="Taxa Compra Manha",
        color="Indexador",
        color_discrete_map=CORES,
        barmode="overlay",
        nbins=80,
        labels={"Taxa Compra Manha": "Taxa de compra (% ao ano)"},
    )
    st.plotly_chart(fig_hist, width="stretch")

# ----------------------------------------------------------------
# Gráfico 2: dispersão prazo x taxa no dia mais recente
# ----------------------------------------------------------------
if st.checkbox("Mostrar gráfico de dispersão (prazo × taxa)"):
    ultima_data = df["Data Base"].max()
    df_hoje = df[df["Data Base"] == ultima_data]
    st.write(
        f"Cada ponto é um título à venda em {ultima_data:%d/%m/%Y}. "
        "Títulos mais longos pagam mais?"
    )
    fig_disp = px.scatter(
        df_hoje,
        x="Anos ate Vencimento",
        y="Taxa Compra Manha",
        color="Indexador",
        color_discrete_map=CORES,
        hover_name="Tipo Titulo",
        labels={
            "Anos ate Vencimento": "Anos até o vencimento",
            "Taxa Compra Manha": "Taxa de compra (% ao ano)",
        },
    )
    st.plotly_chart(fig_disp, width="stretch")
