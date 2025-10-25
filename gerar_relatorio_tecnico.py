"""
Gera relatório técnico detalhado sobre linhas de transmissão
Autor: Ronan Armando Caetano
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
from pathlib import Path
from datetime import datetime
import numpy as np

# Diretório base
base_dir = Path(__file__).parent
output_dir = base_dir / 'outputs'
output_dir.mkdir(exist_ok=True)

# Carregar dados
df = pd.read_csv(base_dir / 'dados_consolidados.csv')
df_mult = pd.read_csv(base_dir / 'municipios_multiplas_linhas.csv')

# Filtrar apenas linhas específicas
df_espec = df[df['Tipo'] == 'especifica'].copy()

# Normalizar e deduplicate
df_espec['NM_MUN'] = df_espec['NM_MUN'].str.strip()
df_espec['Estado'] = df_espec['Estado'].str.strip().str.upper()
df_espec = df_espec.drop_duplicates(subset=['NM_MUN', 'Estado', 'Voltagem'])

# ====================
# ANÁLISES ESTATÍSTICAS
# ====================

# Estatísticas básicas
total_municipios = df_espec['NM_MUN'].nunique()
total_registros = len(df_espec)
voltagens = sorted(df_espec['Voltagem'].unique(), key=lambda x: int(x))

# Análise por estado
stats_estado = df_espec.groupby('Estado').agg({
    'NM_MUN': 'nunique',
    'Voltagem': lambda x: x.nunique()
}).reset_index()
stats_estado.columns = ['Estado', 'Municipios', 'Tipos_Voltagem']

# Análise por voltagem
stats_voltagem = df_espec.groupby('Voltagem').agg({
    'NM_MUN': 'nunique',
    'Estado': lambda x: x.nunique()
}).reset_index()
stats_voltagem.columns = ['Voltagem', 'Municipios', 'Estados']
stats_voltagem = stats_voltagem.sort_values('Voltagem', key=lambda x: x.astype(int))

# Análise de concentração (municípios com múltiplas linhas)
linhas_por_municipio = df_espec.groupby('NM_MUN')['Linha'].nunique()
dist_linhas = linhas_por_municipio.value_counts().sort_index()

# Estatísticas descritivas
media_linhas = linhas_por_municipio.mean()
mediana_linhas = linhas_por_municipio.median()
max_linhas = linhas_por_municipio.max()
municipio_max = linhas_por_municipio.idxmax()

# Análise de cobertura por estado e voltagem
matriz_cobertura = df_espec.groupby(['Estado', 'Voltagem'])['NM_MUN'].nunique().unstack(fill_value=0)

# ====================
# VISUALIZAÇÕES TÉCNICAS
# ====================

# 1. Distribuição de municípios por voltagem
fig1 = go.Figure()
fig1.add_trace(go.Bar(
    x=stats_voltagem['Voltagem'].astype(str) + ' kV',
    y=stats_voltagem['Municipios'],
    marker_color=['#3182ce', '#38a169', '#d69e2e', '#e53e3e', '#805ad5'],
    text=stats_voltagem['Municipios'],
    textposition='auto',
))
fig1.update_layout(
    title='Distribuição de Municípios por Classe de Voltagem',
    xaxis_title='Voltagem (kV)',
    yaxis_title='Número de Municípios',
    showlegend=False,
    height=400,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
)

# 2. Heatmap de cobertura estado x voltagem
fig2 = px.imshow(
    matriz_cobertura,
    text_auto=True,
    aspect='auto',
    color_continuous_scale='Blues',
    title='Matriz de Cobertura: Municípios por Estado e Voltagem'
)
fig2.update_xaxes(title='Voltagem (kV)')
fig2.update_yaxes(title='Estado')
fig2.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

# 3. Distribuição de concentração de linhas
fig3 = go.Figure()
fig3.add_trace(go.Bar(
    x=dist_linhas.index.astype(str),
    y=dist_linhas.values,
    marker_color='#4299e1',
    text=dist_linhas.values,
    textposition='auto',
))
fig3.update_layout(
    title='Distribuição de Concentração de Linhas por Município',
    xaxis_title='Número de Linhas de Transmissão',
    yaxis_title='Quantidade de Municípios',
    showlegend=False,
    height=400,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
)

# 4. Comparativo por estado
fig4 = go.Figure()
for estado in ['PR', 'SC', 'RS']:
    df_estado = df_espec[df_espec['Estado'] == estado]
    counts = df_estado.groupby('Voltagem')['NM_MUN'].nunique().reindex(voltagens, fill_value=0)
    fig4.add_trace(go.Bar(
        name=estado,
        x=[str(v) + ' kV' for v in voltagens],
        y=counts.values
    ))
fig4.update_layout(
    title='Municípios por Voltagem em Cada Estado',
    xaxis_title='Voltagem (kV)',
    yaxis_title='Número de Municípios',
    barmode='group',
    height=400,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
)

# 5. Box plot - distribuição de linhas por estado
fig5 = go.Figure()
for estado in ['PR', 'SC', 'RS']:
    municipios_estado = df_espec[df_espec['Estado'] == estado]['NM_MUN'].unique()
    linhas_estado = [linhas_por_municipio.get(m, 0) for m in municipios_estado]
    fig5.add_trace(go.Box(
        name=estado,
        y=linhas_estado,
        boxmean='sd'
    ))
fig5.update_layout(
    title='Distribuição de Linhas por Município (por Estado)',
    yaxis_title='Número de Linhas',
    height=400,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
)

# ====================
# GERAR HTML
# ====================

now = datetime.now().strftime('%d/%m/%Y às %H:%M')

html = f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Relatório Técnico - Linhas de Transmissão de Foz do Iguaçu</title>
    <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
    <style>
        :root {{
            --bg: #ffffff;
            --text: #1a202c;
            --primary: #2b6cb0;
            --secondary: #4a5568;
            --border: #e2e8f0;
            --card: #f7fafc;
            --code-bg: #2d3748;
            --code-text: #e2e8f0;
        }}
        
        :root[data-theme='dark'] {{
            --bg: #1a202c;
            --text: #e2e8f0;
            --primary: #4299e1;
            --secondary: #a0aec0;
            --border: #2d3748;
            --card: #2d3748;
            --code-bg: #1a202c;
            --code-text: #e2e8f0;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.7;
            font-size: 16px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        header {{
            background: linear-gradient(135deg, #2b6cb0 0%, #2c5282 100%);
            color: white;
            padding: 60px 20px;
            text-align: center;
            margin-bottom: 40px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        header h1 {{
            font-size: 36px;
            margin-bottom: 12px;
            font-weight: 700;
        }}
        
        header p {{
            font-size: 18px;
            opacity: 0.95;
            margin: 8px 0;
        }}
        
        .metadata {{
            font-size: 14px;
            opacity: 0.85;
            margin-top: 16px;
        }}
        
        .theme-toggle {{
            margin-top: 20px;
        }}
        
        .btn {{
            background: rgba(255,255,255,0.2);
            border: 2px solid white;
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s;
        }}
        
        .btn:hover {{
            background: rgba(255,255,255,0.3);
        }}
        
        .section {{
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 32px;
            margin-bottom: 32px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        
        h2 {{
            font-size: 28px;
            color: var(--primary);
            margin-bottom: 20px;
            border-left: 5px solid var(--primary);
            padding-left: 16px;
        }}
        
        h3 {{
            font-size: 22px;
            color: var(--secondary);
            margin: 24px 0 12px 0;
        }}
        
        h4 {{
            font-size: 18px;
            color: var(--secondary);
            margin: 16px 0 8px 0;
        }}
        
        p {{
            margin-bottom: 16px;
            text-align: justify;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 24px 0;
        }}
        
        .stat-card {{
            background: var(--card);
            border: 2px solid var(--border);
            border-radius: 10px;
            padding: 20px;
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 36px;
            font-weight: 700;
            color: var(--primary);
            margin: 8px 0;
        }}
        
        .stat-label {{
            font-size: 14px;
            color: var(--secondary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }}
        
        th {{
            background: var(--primary);
            color: white;
            font-weight: 600;
        }}
        
        tr:hover td {{
            background: var(--border);
        }}
        
        .code-block {{
            background: var(--code-bg);
            color: var(--code-text);
            padding: 16px;
            border-radius: 8px;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            margin: 16px 0;
        }}
        
        .highlight {{
            background: linear-gradient(135deg, rgba(66, 153, 225, 0.1) 0%, rgba(49, 130, 206, 0.1) 100%);
            border-left: 4px solid var(--primary);
            padding: 16px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        
        .methodology {{
            background: rgba(237, 137, 54, 0.1);
            border-left: 4px solid #ed8936;
            padding: 16px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        
        ul, ol {{
            margin: 16px 0;
            padding-left: 24px;
        }}
        
        li {{
            margin: 8px 0;
        }}
        
        .chart-container {{
            margin: 24px 0;
        }}
        
        footer {{
            text-align: center;
            padding: 40px 20px;
            color: var(--secondary);
            border-top: 1px solid var(--border);
            margin-top: 40px;
        }}
    </style>
</head>
<body>
    <header>
        <h1>📊 Relatório Técnico</h1>
        <p>Análise Geoespacial de Linhas de Transmissão</p>
        <p>Usina Hidrelétrica de Foz do Iguaçu → Região Sul do Brasil</p>
        <div class="metadata">
            <strong>Autor:</strong> Ronan Armando Caetano | 
            <strong>Gerado em:</strong> {now}
        </div>
        <div class="theme-toggle">
            <button id="themeBtn" class="btn">Alternar Tema</button>
        </div>
    </header>
    
    <div class="container">
        <!-- RESUMO EXECUTIVO -->
        <div class="section">
            <h2>1. Resumo Executivo</h2>
            
            <p>
                Este relatório apresenta uma análise técnica abrangente das linhas de transmissão de energia elétrica 
                originárias da Usina Hidrelétrica de Foz do Iguaçu, contemplando sua distribuição geoespacial e impacto 
                nos municípios da região Sul do Brasil.
            </p>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">Total de Municípios</div>
                    <div class="stat-value">{total_municipios}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Registros Únicos</div>
                    <div class="stat-value">{total_registros}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Classes de Voltagem</div>
                    <div class="stat-value">{len(voltagens)}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Estados Cobertos</div>
                    <div class="stat-value">3</div>
                </div>
            </div>
            
            <div class="highlight">
                <strong>Principais Achados:</strong>
                <ul>
                    <li>Foram identificados <strong>{total_municipios} municípios únicos</strong> afetados por linhas de transmissão</li>
                    <li>A voltagem varia de <strong>{min(voltagens)} kV a {max(voltagens)} kV</strong></li>
                    <li>Em média, cada município é atravessado por <strong>{media_linhas:.2f} linhas</strong> de transmissão</li>
                    <li>O município de <strong>{municipio_max}</strong> concentra o maior número de linhas ({max_linhas})</li>
                    <li>A maioria dos municípios ({dist_linhas.iloc[0]}) possui apenas 1 linha de transmissão</li>
                </ul>
            </div>
        </div>
        
        <!-- METODOLOGIA -->
        <div class="section">
            <h2>2. Metodologia</h2>
            
            <h3>2.1 Fonte de Dados</h3>
            <p>
                Os dados foram obtidos através de análise geoespacial utilizando GeoPackage (.gpkg) contendo 
                as geometrias das linhas de transmissão e limites municipais. A intersecção espacial foi realizada 
                para identificar quais municípios são atravessados por cada linha.
            </p>
            
            <div class="methodology">
                <strong>Arquivos de Entrada:</strong>
                <ul>
                    <li><code>linhas_recortadas_utm.gpkg</code> - Geometrias das linhas de transmissão</li>
                    <li><code>municipios_afetados_por_layer.gpkg</code> - Resultados da análise espacial</li>
                    <li><code>faixa_servidao.gpkg</code> - Faixas de servidão das linhas</li>
                </ul>
            </div>
            
            <h3>2.2 Processamento de Dados</h3>
            <p>O pipeline de processamento seguiu as seguintes etapas:</p>
            <ol>
                <li><strong>Extração:</strong> Leitura dos arquivos GeoPackage contendo dados geoespaciais</li>
                <li><strong>Normalização:</strong> Padronização de nomes (remoção de espaços, uppercase em estados)</li>
                <li><strong>Deduplicação:</strong> Remoção de registros duplicados baseado em município, estado e voltagem</li>
                <li><strong>Classificação:</strong> Separação entre linhas "base" e "específicas" por voltagem</li>
                <li><strong>Agregação:</strong> Cálculo de estatísticas por município, estado e voltagem</li>
            </ol>
            
            <div class="code-block">
# Exemplo de normalização aplicada<br>
df['NM_MUN'] = df['NM_MUN'].str.strip()<br>
df['Estado'] = df['Estado'].str.strip().str.upper()<br>
df = df.drop_duplicates(subset=['NM_MUN', 'Estado', 'Voltagem'])
            </div>
            
            <h3>2.3 Ferramentas Utilizadas</h3>
            <ul>
                <li><strong>Python 3.13:</strong> Linguagem de programação principal</li>
                <li><strong>Pandas 2.3.3:</strong> Manipulação e análise de dados tabulares</li>
                <li><strong>GeoPandas:</strong> Operações geoespaciais e intersecções</li>
                <li><strong>QGIS:</strong> Visualização e validação de dados geoespaciais</li>
                <li><strong>Plotly 6.3.1:</strong> Visualizações interativas</li>
            </ul>
        </div>
        
        <!-- ANÁLISE ESTATÍSTICA -->
        <div class="section">
            <h2>3. Análise Estatística Descritiva</h2>
            
            <h3>3.1 Distribuição por Estado</h3>
            <table>
                <thead>
                    <tr>
                        <th>Estado</th>
                        <th>Municípios</th>
                        <th>Tipos de Voltagem</th>
                        <th>% do Total</th>
                    </tr>
                </thead>
                <tbody>
"""

for _, row in stats_estado.iterrows():
    percentual = (row['Municipios'] / total_municipios) * 100
    html += f"""
                    <tr>
                        <td><strong>{row['Estado']}</strong></td>
                        <td>{row['Municipios']}</td>
                        <td>{row['Tipos_Voltagem']}</td>
                        <td>{percentual:.1f}%</td>
                    </tr>
"""

html += f"""
                </tbody>
            </table>
            
            <h3>3.2 Distribuição por Voltagem</h3>
            <table>
                <thead>
                    <tr>
                        <th>Voltagem (kV)</th>
                        <th>Municípios Afetados</th>
                        <th>Estados</th>
                        <th>Alcance</th>
                    </tr>
                </thead>
                <tbody>
"""

alcance_descricao = {
    '230': 'Regional',
    '500': 'Interestadual',
    '525': 'Longa Distância',
    '600': 'Transmissão Pesada',
    '765': 'Ultra Alta Tensão'
}

for _, row in stats_voltagem.iterrows():
    html += f"""
                    <tr>
                        <td><strong>{row['Voltagem']} kV</strong></td>
                        <td>{row['Municipios']}</td>
                        <td>{row['Estados']}</td>
                        <td>{alcance_descricao.get(str(int(row['Voltagem'])), 'N/A')}</td>
                    </tr>
"""

html += f"""
                </tbody>
            </table>
            
            <div class="chart-container">
                {pio.to_html(fig1, include_plotlyjs=False, full_html=False)}
            </div>
            
            <h3>3.3 Concentração de Linhas por Município</h3>
            <p>
                A análise de concentração revela que a distribuição de linhas por município segue um padrão 
                típico de infraestrutura de transmissão, com a maioria dos municípios possuindo poucas linhas 
                e alguns poucos concentrando múltiplas linhas devido à sua posição estratégica.
            </p>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">Média de Linhas</div>
                    <div class="stat-value">{media_linhas:.2f}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Mediana</div>
                    <div class="stat-value">{int(mediana_linhas)}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Máximo</div>
                    <div class="stat-value">{max_linhas}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Moda</div>
                    <div class="stat-value">{dist_linhas.index[0]}</div>
                </div>
            </div>
            
            <div class="chart-container">
                {pio.to_html(fig3, include_plotlyjs=False, full_html=False)}
            </div>
            
            <div class="highlight">
                <strong>Interpretação Estatística:</strong>
                <ul>
                    <li>A <strong>média ({media_linhas:.2f})</strong> é superior à <strong>mediana ({int(mediana_linhas)})</strong>, 
                        indicando assimetria positiva (cauda à direita)</li>
                    <li>Isso significa que poucos municípios concentram muitas linhas, elevando a média</li>
                    <li><strong>{dist_linhas.iloc[0]} municípios ({(dist_linhas.iloc[0]/total_municipios*100):.1f}%)</strong> 
                        possuem apenas 1 linha</li>
                    <li><strong>{dist_linhas[dist_linhas.index >= 3].sum()} municípios ({(dist_linhas[dist_linhas.index >= 3].sum()/total_municipios*100):.1f}%)</strong> 
                        possuem 3 ou mais linhas</li>
                </ul>
            </div>
        </div>
        
        <!-- ANÁLISE GEOESPACIAL -->
        <div class="section">
            <h2>4. Análise Geoespacial</h2>
            
            <h3>4.1 Matriz de Cobertura Estado x Voltagem</h3>
            <p>
                A matriz de cobertura ilustra a distribuição espacial das diferentes classes de voltagem 
                nos três estados da região Sul. Cada célula representa o número de municípios afetados 
                por uma determinada voltagem em cada estado.
            </p>
            
            <div class="chart-container">
                {pio.to_html(fig2, include_plotlyjs=False, full_html=False)}
            </div>
            
            <h3>4.2 Análise Comparativa por Estado</h3>
            <div class="chart-container">
                {pio.to_html(fig4, include_plotlyjs=False, full_html=False)}
            </div>
            
            <h3>4.3 Variabilidade Regional</h3>
            <p>
                O box plot abaixo demonstra a distribuição de linhas por município em cada estado, 
                permitindo identificar padrões de concentração e dispersão.
            </p>
            
            <div class="chart-container">
                {pio.to_html(fig5, include_plotlyjs=False, full_html=False)}
            </div>
            
            <div class="highlight">
                <strong>Insights Geoespaciais:</strong>
                <ul>
                    <li>Paraná concentra a maior parte das linhas de alta voltagem (600 e 765 kV)</li>
                    <li>Santa Catarina apresenta distribuição mais uniforme entre as voltagens</li>
                    <li>Rio Grande do Sul possui maior número de municípios com linhas de 525 kV</li>
                    <li>A linha de 765 kV é exclusiva do Paraná, refletindo sua conexão direta com Foz do Iguaçu</li>
                </ul>
            </div>
        </div>
        
        <!-- MUNICÍPIOS CRÍTICOS -->
        <div class="section">
            <h2>5. Municípios Críticos</h2>
            
            <p>
                Municípios atravessados por múltiplas linhas de transmissão são considerados críticos 
                do ponto de vista de planejamento territorial e gestão ambiental. A tabela abaixo 
                lista os 15 municípios com maior concentração de linhas.
            </p>
            
            <table>
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Município</th>
                        <th>Estado</th>
                        <th>Nº Linhas</th>
                        <th>Voltagens (kV)</th>
                    </tr>
                </thead>
                <tbody>
"""

for idx, row in df_mult.head(15).iterrows():
    html += f"""
                    <tr>
                        <td><strong>{idx + 1}º</strong></td>
                        <td>{row['Municipio']}</td>
                        <td>{row['Estado']}</td>
                        <td>{row['Num_Linhas']}</td>
                        <td>{row['Voltagens']}</td>
                    </tr>
"""

html += f"""
                </tbody>
            </table>
            
            <div class="highlight">
                <strong>Implicações:</strong>
                <ul>
                    <li><strong>Faixas de Servidão:</strong> Municípios com múltiplas linhas têm maior área 
                        de restrição de uso do solo</li>
                    <li><strong>Redundância:</strong> Maior segurança energética, mas também maior impacto ambiental</li>
                    <li><strong>Planejamento Urbano:</strong> Necessidade de zoneamento específico para acomodar 
                        corredores de transmissão</li>
                </ul>
            </div>
        </div>
        
        <!-- CONCLUSÕES -->
        <div class="section">
            <h2>6. Conclusões e Recomendações</h2>
            
            <h3>6.1 Principais Conclusões</h3>
            <ol>
                <li>
                    <strong>Abrangência Significativa:</strong> O sistema de transmissão de Foz do Iguaçu 
                    alcança {total_municipios} municípios, demonstrando a importância estratégica da usina 
                    para a região Sul.
                </li>
                <li>
                    <strong>Diversificação de Voltagens:</strong> A utilização de 5 classes diferentes de voltagem 
                    (230 a 765 kV) reflete a necessidade de atender diferentes distâncias e demandas de carga.
                </li>
                <li>
                    <strong>Concentração Estratégica:</strong> Municípios próximos a Foz do Iguaçu apresentam 
                    maior concentração de linhas, indicando o padrão radial de distribuição.
                </li>
                <li>
                    <strong>Assimetria Regional:</strong> Paraná concentra linhas de maior voltagem, enquanto 
                    SC e RS dependem mais de linhas de média voltagem.
                </li>
            </ol>
            
            <h3>6.2 Recomendações Técnicas</h3>
            <ul>
                <li>
                    <strong>Monitoramento Ambiental:</strong> Implementar sistema de monitoramento específico 
                    nos 15 municípios críticos identificados
                </li>
                <li>
                    <strong>Planejamento Territorial:</strong> Desenvolver planos diretores que considerem 
                    as faixas de servidão das linhas de transmissão
                </li>
                <li>
                    <strong>Redundância:</strong> Avaliar a necessidade de linhas alternativas em municípios 
                    com apenas 1 linha de transmissão
                </li>
                <li>
                    <strong>Expansão:</strong> Considerar a construção de novas linhas de 525-600 kV para 
                    Santa Catarina e Rio Grande do Sul
                </li>
            </ul>
            
            <h3>6.3 Limitações do Estudo</h3>
            <ul>
                <li>Análise baseada apenas em dados de intersecção geográfica, sem considerar capacidade de transmissão</li>
                <li>Não foram analisados aspectos de demanda energética por município</li>
                <li>Dados de faixa de servidão não foram incluídos nas métricas quantitativas</li>
            </ul>
        </div>
        
        <!-- REFERÊNCIAS -->
        <div class="section">
            <h2>7. Referências Técnicas</h2>
            
            <h3>7.1 Ferramentas e Bibliotecas</h3>
            <ul>
                <li>Python Software Foundation. (2024). Python 3.13. https://www.python.org/</li>
                <li>McKinney, W. (2024). pandas: Python Data Analysis Library. https://pandas.pydata.org/</li>
                <li>GeoPandas developers. (2024). GeoPandas. https://geopandas.org/</li>
                <li>Plotly Technologies Inc. (2024). Plotly Python Graphing Library. https://plotly.com/python/</li>
                <li>QGIS Development Team. (2024). QGIS Geographic Information System. https://qgis.org/</li>
            </ul>
            
            <h3>7.2 Dados</h3>
            <ul>
                <li>Linhas de Transmissão: Base de dados geoespacial em formato GeoPackage (.gpkg)</li>
                <li>Limites Municipais: IBGE - Instituto Brasileiro de Geografia e Estatística</li>
                <li>Período de Análise: {now}</li>
            </ul>
        </div>
    </div>
    
    <footer>
        <p><strong>Autor:</strong> Ronan Armando Caetano</p>
        <p><strong>Assistência Técnica:</strong> GitHub Copilot</p>
        <p style="margin-top: 16px; font-size: 14px; opacity: 0.8;">
            Este relatório foi gerado automaticamente a partir de dados geoespaciais processados com Python.<br>
            Para mais informações, consulte o repositório: 
            <a href="https://github.com/caetanoronan/linhas-transmissao-foz-iguacu" style="color: var(--primary);">
                github.com/caetanoronan/linhas-transmissao-foz-iguacu
            </a>
        </p>
    </footer>
    
    <script>
        // Tema claro/escuro
        const root = document.documentElement;
        const btn = document.getElementById('themeBtn');
        const saved = localStorage.getItem('theme-tech');
        let isDark = saved === 'dark';
        
        if (isDark) {{
            root.setAttribute('data-theme', 'dark');
        }}
        
        btn.addEventListener('click', function() {{
            isDark = !isDark;
            root.setAttribute('data-theme', isDark ? 'dark' : 'light');
            localStorage.setItem('theme-tech', isDark ? 'dark' : 'light');
            
            // Atualizar gráficos
            const plots = document.querySelectorAll('.js-plotly-plot');
            plots.forEach(function(p) {{
                const layout = {{
                    template: isDark ? 'plotly_dark' : 'plotly_white',
                    paper_bgcolor: 'rgba(0,0,0,0)',
                    plot_bgcolor: 'rgba(0,0,0,0)',
                    font: {{ color: isDark ? '#e2e8f0' : '#1a202c' }}
                }};
                Plotly.relayout(p, layout);
            }});
        }});
    </script>
</body>
</html>
"""

# Salvar arquivo
output_file = output_dir / 'relatorio_tecnico.html'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"✓ Relatório técnico gerado: {output_file}")
print(f"  Total de municípios analisados: {total_municipios}")
print(f"  Visualizações incluídas: 5 gráficos")
print(f"  Análises: Estatística descritiva, geoespacial e concentração")
