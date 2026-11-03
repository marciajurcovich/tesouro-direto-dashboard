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

ROTULOS = {
    "Taxa Compra Manha": "Taxa de compra (% ao ano)",
    "Anos ate Vencimento": "Anos até o vencimento",
    "Data Base": "Data",
}


def br(numero, casas=2):
    """Formata um número no padrão brasileiro: 15488.22 -> 15.488,22"""
    texto = f"{numero:,.{casas}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


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
ultima_data = df["Data Base"].max()

# ----------------------------------------------------------------
# Barra lateral: filtros
# ----------------------------------------------------------------
st.sidebar.header("Filtros")

indexadores = st.sidebar.multiselect(
    "Indexadores",
    options=list(CORES.keys()),
    default=list(CORES.keys()),
)

ano_min = int(df["Data Base"].dt.year.min())
ano_max = int(df["Data Base"].dt.year.max())
anos = st.sidebar.slider(
    "Período (anos)", min_value=ano_min, max_value=ano_max, value=(ano_min, ano_max)
)

st.sidebar.caption(
    "Os filtros valem para o histograma e para a linha do tempo. "
    "O gráfico de dispersão usa sempre o dia mais recente da base."
)

# Se nenhum indexador for escolhido, avisa e para o app aqui
if not indexadores:
    st.warning("Escolha pelo menos um indexador na barra lateral.")
    st.stop()

# Tabela filtrada pelos indexadores e pelo período escolhidos
df_filtro = df[
    df["Indexador"].isin(indexadores)
    & df["Data Base"].dt.year.between(anos[0], anos[1])
]

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
# Indicadores: taxa média de cada indexador no dia mais recente,
# comparada com cerca de 1 ano antes
# ----------------------------------------------------------------
st.subheader(f"Taxas médias em {ultima_data:%d/%m/%Y}")

data_ano_antes = df.loc[
    df["Data Base"] <= ultima_data - pd.DateOffset(years=1), "Data Base"
].max()

hoje = df[df["Data Base"] == ultima_data].groupby("Indexador")["Taxa Compra Manha"].mean()
antes = df[df["Data Base"] == data_ano_antes].groupby("Indexador")["Taxa Compra Manha"].mean()

colunas = st.columns(len(indexadores))
for coluna, nome in zip(colunas, indexadores):
    if nome in hoje.index:
        variacao = None
        if nome in antes.index:
            dif = hoje[nome] - antes[nome]
            variacao = ("+" if dif >= 0 else "") + br(dif) + " p.p. em 1 ano"
        coluna.metric(nome, br(hoje[nome]) + "% a.a.", variacao, delta_color="off")
    else:
        coluna.metric(nome, "—", "sem títulos à venda", delta_color="off")

st.divider()

# ----------------------------------------------------------------
# Gráfico 1: histograma (aparece quando a caixinha é marcada)
# ----------------------------------------------------------------
if st.checkbox("Mostrar histograma das taxas", value=True):
    st.write(
        f"Com que frequência cada faixa de taxa apareceu entre {anos[0]} e {anos[1]}, por indexador."
    )
    fig_hist = px.histogram(
        df_filtro,
        x="Taxa Compra Manha",
        color="Indexador",
        color_discrete_map=CORES,
        barmode="overlay",
        nbins=80,
        labels=ROTULOS,
    )
    st.plotly_chart(fig_hist, width="stretch")

# ----------------------------------------------------------------
# Gráfico 2: dispersão prazo x taxa no dia mais recente
# ----------------------------------------------------------------
if st.checkbox("Mostrar gráfico de dispersão (prazo × taxa)"):
    df_hoje = df[(df["Data Base"] == ultima_data) & df["Indexador"].isin(indexadores)]
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
        labels=ROTULOS,
    )
    st.plotly_chart(fig_disp, width="stretch")

# ----------------------------------------------------------------
# Gráfico 3: evolução das taxas no tempo (média mensal)
# ----------------------------------------------------------------
if st.checkbox("Mostrar evolução das taxas no tempo"):
    st.write("Média mensal da taxa de compra de cada indexador.")
    media_mensal = (
        df_filtro.groupby([pd.Grouper(key="Data Base", freq="ME"), "Indexador"])[
            "Taxa Compra Manha"
        ]
        .mean()
        .reset_index()
    )
    fig_linha = px.line(
        media_mensal,
        x="Data Base",
        y="Taxa Compra Manha",
        color="Indexador",
        color_discrete_map=CORES,
        labels=ROTULOS,
    )
    st.plotly_chart(fig_linha, width="stretch")

st.divider()

# ----------------------------------------------------------------
# Simulador: quanto um investimento renderia até o vencimento
# ----------------------------------------------------------------
st.subheader("💰 Simulador de investimento")
st.write(
    "Escolha um título à venda hoje e veja uma estimativa do valor bruto no vencimento."
)

# Renda+ e Educa+ pagam em parcelas mensais, então ficam fora desta conta simples
df_sim = df[
    (df["Data Base"] == ultima_data)
    & ~df["Tipo Titulo"].str.contains("Renda\\+|Educa\\+")
].copy()
df_sim["Opcao"] = (
    df_sim["Tipo Titulo"]
    + " — vence em "
    + df_sim["Data Vencimento"].dt.strftime("%d/%m/%Y")
    + " — taxa "
    + df_sim["Taxa Compra Manha"].map(br)
    + "%"
)

opcao = st.selectbox("Título", df_sim["Opcao"].sort_values())
titulo = df_sim[df_sim["Opcao"] == opcao].iloc[0]

col1, col2 = st.columns(2)
valor = col1.number_input(
    "Valor investido (R$)", min_value=100.0, value=10000.0, step=1000.0
)

taxa = titulo["Taxa Compra Manha"] / 100
anos_ate_vencer = titulo["Anos ate Vencimento"]

# A taxa total depende do indexador
if titulo["Indexador"] == "Prefixado":
    taxa_total = taxa
    col2.info("Prefixado: a taxa já é a rentabilidade total ao ano.")
elif titulo["Indexador"] == "Selic":
    selic = col2.number_input("Selic média esperada (% ao ano)", value=10.0, step=0.25) / 100
    taxa_total = (1 + selic) * (1 + taxa) - 1
else:  # IPCA+ ou IGP-M+
    inflacao = col2.number_input("Inflação média esperada (% ao ano)", value=4.0, step=0.25) / 100
    taxa_total = (1 + inflacao) * (1 + taxa) - 1

# Juros compostos: valor x (1 + taxa) elevado ao número de anos
valor_final = valor * (1 + taxa_total) ** anos_ate_vencer

r1, r2, r3 = st.columns(3)
r1.metric("Prazo", br(anos_ate_vencer, 1) + " anos")
r2.metric("Rentabilidade estimada", br(taxa_total * 100) + "% ao ano")
r3.metric(
    "Valor bruto no vencimento",
    "R$ " + br(valor_final),
)

st.caption(
    "Simulação simplificada, apenas para fins educativos: não considera imposto de renda, "
    "taxas, marcação a mercado nem o reinvestimento dos cupons dos títulos com juros semestrais. "
    "Não é recomendação de investimento."
)
