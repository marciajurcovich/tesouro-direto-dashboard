# Painel do Tesouro Direto: taxas e prazos

🔗 **App online:** https://tesouro-direto-dashboard.onrender.com

> ⏳ O app está hospedado na versão gratuita do Render e pode levar 1–2 minutos para "acordar" no primeiro acesso.

## Sobre o projeto
Aplicativo web interativo para explorar o histórico de taxas dos títulos públicos vendidos no **Tesouro Direto**, desde 2005. O app permite comparar os diferentes indexadores (Selic, Prefixado, IPCA+ e IGP-M+) e observar a relação entre o prazo dos títulos e as taxas oferecidas.

Projeto desenvolvido no MBA em Ciência de Dados e IA da TripleTen, com foco em práticas de engenharia de software: ambiente virtual, versionamento com Git/GitHub e publicação de aplicativo em nuvem.

## Funcionalidades
- **Filtros na barra lateral:** escolha dos indexadores e do período (anos).
- **Indicadores:** taxa média de cada indexador no dia mais recente e variação em 12 meses.
- **Histograma das taxas por indexador:** com que frequência cada faixa de taxa apareceu.
- **Gráfico de dispersão prazo × taxa:** se títulos mais longos pagam taxas maiores (estrutura a termo), no dia mais recente da base.
- **Evolução no tempo:** média mensal da taxa de cada indexador.
- **Simulador de investimento:** estimativa do valor bruto no vencimento de um título à venda, com premissas de Selic ou inflação definidas pelo usuário (simulação educativa, sem IR e taxas).
- Gráficos exibidos por **caixas de seleção**, interativos e com cores fixas por indexador.

## Dados
- **Fonte:** [Tesouro Transparente — Taxas dos Títulos Ofertados pelo Tesouro Direto](https://www.tesourotransparente.gov.br/ckan/dataset/taxas-dos-titulos-ofertados-pelo-tesouro-direto)
- Considerados apenas os títulos disponíveis para compra (preço de compra maior que zero).
- **Importante:** a taxa tem significado diferente em cada indexador — no Selic é o adicional sobre a Selic; no Prefixado é a taxa nominal; no IPCA+ e IGP-M+ é o ganho acima da inflação.

## Análise exploratória
A análise completa, com gráficos e conclusões, está no notebook [`notebooks/EDA.ipynb`](notebooks/EDA.ipynb).

## Tecnologias
Python · pandas · plotly-express · Streamlit · Git/GitHub · Render

## Como rodar no seu computador
```bash
git clone https://github.com/marciajurcovich/tesouro-direto-dashboard.git
cd tesouro-direto-dashboard
python -m venv tesouro_env
tesouro_env\Scripts\activate        # Windows
pip install -r requirements.txt
streamlit run app.py
```
Depois, abra `http://localhost:10000` no navegador.

## Autora
**Marcia Jurcovich Ferreira** — [LinkedIn](https://www.linkedin.com/in/marciajurcovich)
