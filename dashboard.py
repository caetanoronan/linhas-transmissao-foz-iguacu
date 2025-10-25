# Dashboard - Linhas de Transmissão de Foz do Iguaçu (Região Sul)
# Requer: streamlit, plotly, pandas, seaborn (opcional)

from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import subprocess
import sys

BASE_DIR = Path(__file__).parent

@st.cache_data
def load_data(cache_key: float):
    df = pd.read_csv(BASE_DIR / 'dados_consolidados.csv')
    df_mult = pd.read_csv(BASE_DIR / 'municipios_multiplas_linhas.csv')
    # Tipos e normalizações
    df['Voltagem'] = df['Voltagem'].astype(str)
    df['Estado'] = df['Estado'].astype(str)
    # Filtrar apenas específicas para algumas análises
    df_especificas = df[df['Tipo'] == 'especifica'].copy()
    # Normalização e deduplicação para evitar contagens infladas
    df_especificas['NM_MUN'] = df_especificas['NM_MUN'].astype(str).str.strip()
    df_especificas['Estado'] = df_especificas['Estado'].astype(str).str.strip().str.upper()
    df_especificas['Voltagem'] = df_especificas['Voltagem'].astype(str).str.strip()
    df_especificas = df_especificas.drop_duplicates(subset=['NM_MUN','Estado','Voltagem'])
    # Normaliza df_mult também
    if 'Municipio' in df_mult.columns:
        df_mult['Municipio'] = df_mult['Municipio'].astype(str).str.strip()
    if 'Estado' in df_mult.columns:
        df_mult['Estado'] = df_mult['Estado'].astype(str).str.strip().str.upper()
    df_mult = df_mult.drop_duplicates()
    return df, df_especificas, df_mult

st.set_page_config(
    page_title='Linhas de Transmissão - Foz do Iguaçu',
    page_icon='⚡',
    layout='wide',
)

st.title('⚡ Linhas de Transmissão de Foz do Iguaçu — Região Sul')
st.caption('Municípios afetados por linha de transmissão | Fonte: arquivos do projeto')

# Carregar dados com cache atrelado à última modificação dos CSVs
try:
    csv1 = BASE_DIR / 'dados_consolidados.csv'
    csv2 = BASE_DIR / 'municipios_multiplas_linhas.csv'
    cache_key = max(csv1.stat().st_mtime if csv1.exists() else 0,
                    csv2.stat().st_mtime if csv2.exists() else 0)
    df, df_especificas, df_mult = load_data(cache_key)
except FileNotFoundError:
    st.error('Arquivos dados_consolidados.csv e/ou municipios_multiplas_linhas.csv não encontrados. Execute primeiro o script analise_consolidada.py.')
    st.stop()

# Sidebar - filtros
with st.sidebar:
    st.header('Filtros')
    estados = sorted(df['Estado'].dropna().unique().tolist())
    estados_sel = st.multiselect('Estados', estados, default=estados)

    voltagens = sorted(df_especificas['Voltagem'].dropna().unique().tolist(), key=lambda x: int(x))
    voltagens_sel = st.multiselect('Voltagens (kV)', voltagens, default=voltagens)

    st.markdown('---')
    st.subheader('Downloads')
    st.download_button('Baixar dados consolidados (CSV)', data=df.to_csv(index=False).encode('utf-8-sig'), file_name='dados_consolidados.csv', mime='text/csv')
    st.download_button('Baixar municípios com múltiplas linhas (CSV)', data=df_mult.to_csv(index=False).encode('utf-8-sig'), file_name='municipios_multiplas_linhas.csv', mime='text/csv')

    st.markdown('---')
    st.subheader('Atualização dos dados')
    st.caption('Reprocessa os CSVs executando analise_consolidada.py')
    if st.button('🔄 Atualizar dados (reprocessar)'):
        with st.spinner('Reprocessando dados... isso pode levar alguns segundos.'):
            try:
                result = subprocess.run(
                    [sys.executable, str(BASE_DIR / 'analise_consolidada.py')],
                    cwd=str(BASE_DIR),
                    capture_output=True,
                    text=True,
                    check=True,
                )
                # Limpar cache e recarregar
                load_data.clear()
                st.success('Dados atualizados com sucesso! Recarregando dashboard...')
                st.rerun()
            except subprocess.CalledProcessError as e:
                st.error('Falha ao atualizar os dados. Veja os detalhes abaixo:')
                st.code(e.stderr or str(e), language='bash')

# Aplicar filtros
mask_estado = df['Estado'].isin(estados_sel)
mask_estado_espec = df_especificas['Estado'].isin(estados_sel)
mask_volt = df_especificas['Voltagem'].isin(voltagens_sel)

_df = df[mask_estado].copy()
_df_espec = df_especificas[mask_estado_espec & mask_volt].copy()
_df_mult = df_mult[df_mult['Estado'].isin(estados_sel)].copy()

# KPIs principais
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric('Municípios únicos (filtrado)', _df['NM_MUN'].nunique())
with col2:
    st.metric('Linhas distintas (filtrado)', _df_espec['Linha'].nunique())
with col3:
    st.metric('Estados selecionados', len(estados_sel))
with col4:
    st.metric('Municípios com múltiplas linhas', int((_df_espec.groupby('NM_MUN')['Linha'].nunique() > 1).sum()))

st.markdown('---')

# Row 1: Municípios por voltagem | Municípios por estado
c1, c2 = st.columns(2)

with c1:
    st.subheader('Municípios afetados por voltagem (kV)')
    if len(_df_espec):
        s = _df_espec.groupby('Voltagem')['NM_MUN'].nunique().sort_index(key=lambda x: x.astype(int))
        fig = px.bar(s, orientation='h', labels={'value':'Municípios','Voltagem':'kV'}, text_auto=True, height=420)
        fig.update_layout(yaxis_title='Voltagem (kV)', xaxis_title='Número de Municípios')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info('Sem dados para os filtros atuais.')

with c2:
    st.subheader('Municípios afetados por estado')
    s = _df.groupby('Estado')['NM_MUN'].nunique().sort_values(ascending=False)
    fig = px.bar(s, text_auto=True, labels={'value':'Municípios','Estado':'Estado'}, height=420)
    fig.update_layout(xaxis_title='Estado', yaxis_title='Número de Municípios')
    st.plotly_chart(fig, use_container_width=True)

# Row 2: Distribuição de linhas por município | Matriz estado x voltagem
c3, c4 = st.columns(2)

with c3:
    st.subheader('Distribuição: quantas linhas atravessam cada município')
    if len(_df_espec):
        municipios_multiplas = _df_espec.groupby('NM_MUN')['Linha'].nunique()
        dist = municipios_multiplas.value_counts().sort_index()
        fig = px.bar(dist, labels={'index':'Nº de Linhas', 'value':'Qtd de Municípios'}, text_auto=True, height=420)
        fig.update_layout(xaxis=dict(type='category'))
        st.plotly_chart(fig, use_container_width=True)
        with st.expander('Como ler este gráfico?'):
            st.write('Cada barra mostra quantos municípios são atravessados por 1, 2, 3, 4, ... linhas. Ex.: barra em 3 = quantidade de municípios com 3 linhas diferentes.')
    else:
        st.info('Sem dados para os filtros atuais.')

with c4:
    st.subheader('Matriz: municípios por estado x voltagem')
    if len(_df_espec):
        mat = _df_espec.groupby(['Estado', 'Voltagem'])['NM_MUN'].nunique().unstack(fill_value=0)
        fig = px.imshow(mat, text_auto=True, color_continuous_scale='YlOrRd', aspect='auto', height=420)
        fig.update_layout(xaxis_title='Voltagem (kV)', yaxis_title='Estado')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info('Sem dados para os filtros atuais.')

# Row 3: Top municípios e tabela
st.subheader('Municípios com mais linhas')
if len(_df_mult):
    df_top = _df_mult.sort_values('Num_Linhas', ascending=False)
    st.dataframe(df_top, use_container_width=True, hide_index=True)
else:
    st.info('Sem municípios com múltiplas linhas para os filtros atuais.')

# Se existir imagem consolidada, exibir
img_path = BASE_DIR / 'analise_consolidada_visualizacao.png'
if img_path.exists():
    st.markdown('---')
    st.subheader('Figura da Análise Consolidada')
    st.image(str(img_path), caption='Gráficos gerados pelo script analise_consolidada.py', use_column_width=True)

st.markdown('---')
st.caption('Dashboard interativo desenvolvido com Streamlit + Plotly | Utilize os filtros na barra lateral para explorar os dados.')
