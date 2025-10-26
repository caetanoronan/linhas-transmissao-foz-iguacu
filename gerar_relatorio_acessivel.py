"""
Gera relatório HTML acessível para pessoas com TDAH e Dislexia
Autor: Ronan Armando Caetano
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from pathlib import Path
from datetime import datetime

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

# Estatísticas principais
total_municipios = df_espec['NM_MUN'].nunique()
total_estados = df_espec['Estado'].nunique()
voltagens = sorted(df_espec['Voltagem'].unique(), key=lambda x: int(x))

# Criar visualização simples - Municípios por Estado
fig_estados = px.bar(
    df_espec.groupby('Estado')['NM_MUN'].nunique().reset_index(),
    x='Estado',
    y='NM_MUN',
    title='',
    labels={'NM_MUN': 'Quantidade', 'Estado': 'Estado'},
    color='Estado',
    color_discrete_map={'PR': '#4299e1', 'SC': '#48bb78', 'RS': '#ed8936'}
)
fig_estados.update_layout(
    showlegend=False,
    height=400,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(size=16)
)

# Top 10 municípios
df_top10 = df_mult.head(10).copy()

# Preparar dados da tabela completa
df_tabela = df_mult.copy()
df_tabela = df_tabela.sort_values('Num_Linhas', ascending=False)

# HTML com acessibilidade
now = datetime.now().strftime('%d/%m/%Y às %H:%M')

html = f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Linhas de Transmissão - Relatório Simplificado</title>
    <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
    <style>
        /* Fonte OpenDyslexic ou Comic Sans (mais legível para dislexia) */
        @import url('https://fonts.googleapis.com/css2?family=Comic+Neue:wght@400;700&display=swap');
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        :root {{
            --bg: #fef9f3;
            --text: #2d3748;
            --primary: #4299e1;
            --secondary: #48bb78;
            --warning: #ed8936;
            --card: #ffffff;
            --border: #e2e8f0;
        }}
        
        :root[data-theme='dark'] {{
            --bg: #1a202c;
            --text: #e2e8f0;
            --card: #2d3748;
            --border: #4a5568;
        }}
        
        body {{
            font-family: 'Comic Neue', 'Comic Sans MS', cursive, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 2;
            font-size: 18px;
            padding: 0;
            margin: 0;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        /* Cabeçalho com cor de fundo forte */
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
            margin-bottom: 40px;
        }}
        
        header h1 {{
            font-size: 32px;
            margin-bottom: 15px;
            font-weight: 700;
        }}
        
        header p {{
            font-size: 20px;
            opacity: 0.95;
        }}
        
        .theme-toggle {{
            margin-top: 20px;
        }}
        
        .btn {{
            background: rgba(255,255,255,0.2);
            border: 2px solid white;
            color: white;
            padding: 12px 24px;
            border-radius: 12px;
            font-size: 18px;
            cursor: pointer;
            font-weight: 700;
            transition: all 0.3s;
        }}
        
        .btn:hover {{
            background: rgba(255,255,255,0.3);
            transform: scale(1.05);
        }}
        
        /* Seções com muito espaçamento */
        .section {{
            background: var(--card);
            border: 3px solid var(--border);
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 40px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        /* Títulos grandes e claros */
        h2 {{
            font-size: 28px;
            color: var(--primary);
            margin-bottom: 25px;
            font-weight: 700;
            border-left: 6px solid var(--primary);
            padding-left: 15px;
        }}
        
        h3 {{
            font-size: 24px;
            color: var(--secondary);
            margin: 25px 0 15px 0;
            font-weight: 700;
        }}
        
        /* Parágrafos curtos com espaçamento */
        p {{
            margin-bottom: 20px;
            line-height: 2.2;
        }}
        
        /* Listas com ícones e cores */
        ul {{
            list-style: none;
            padding: 0;
            margin: 20px 0;
        }}
        
        ul li {{
            padding: 15px 15px 15px 45px;
            margin-bottom: 12px;
            background: var(--card);
            border-left: 5px solid var(--primary);
            border-radius: 8px;
            position: relative;
        }}
        
        ul li:before {{
            content: "✓";
            position: absolute;
            left: 15px;
            font-size: 22px;
            color: var(--secondary);
            font-weight: 700;
        }}
        
        /* Caixas de destaque */
        .destaque {{
            background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
            border: 3px solid var(--primary);
            border-radius: 12px;
            padding: 25px;
            margin: 25px 0;
        }}
        
        .destaque-icon {{
            font-size: 40px;
            margin-bottom: 15px;
        }}
        
        /* Números grandes */
        .numero-grande {{
            font-size: 48px;
            font-weight: 700;
            color: var(--primary);
            display: block;
            margin: 15px 0;
        }}
        
        /* Tabela simplificada */
        table {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 0 10px;
            margin: 20px 0;
        }}
        
        th {{
            background: var(--primary);
            color: white;
            padding: 15px;
            text-align: left;
            font-size: 18px;
            font-weight: 700;
        }}
        
        th:first-child {{
            border-radius: 10px 0 0 10px;
        }}
        
        th:last-child {{
            border-radius: 0 10px 10px 0;
        }}
        
        td {{
            background: var(--card);
            padding: 15px;
            border-bottom: 2px solid var(--border);
            font-size: 16px;
        }}
        
        tr:hover td {{
            background: var(--border);
        }}
        
        /* Badge para voltagens */
        .badge {{
            display: inline-block;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 700;
            margin: 3px;
        }}
        
        .badge-230 {{ background: #fef5e7; color: #d68910; }}
        .badge-500 {{ background: #ebf5fb; color: #2874a6; }}
        .badge-525 {{ background: #eafaf1; color: #1e8449; }}
        .badge-600 {{ background: #fef0f0; color: #c0392b; }}
        .badge-765 {{ background: #f4ecf7; color: #6c3483; }}
        
        /* Rodapé */
        footer {{
            text-align: center;
            padding: 40px 20px;
            color: var(--text);
            opacity: 0.7;
        }}
        
        /* Responsivo */
        @media (max-width: 600px) {{
            body {{
                font-size: 16px;
            }}
            
            header h1 {{
                font-size: 24px;
            }}
            
            h2 {{
                font-size: 22px;
            }}
            
            .numero-grande {{
                font-size: 36px;
            }}
        }}
    </style>
</head>
<body>
    <header>
        <h1>⚡ Linhas de Transmissão</h1>
        <p>Usina de Foz do Iguaçu → Região Sul</p>
        <div class="theme-toggle">
            <button id="themeBtn" class="btn">🌙 Modo Escuro / ☀️ Modo Claro</button>
        </div>
    </header>
    
    <div class="container">
        <!-- O QUE É ESTE RELATÓRIO? -->
        <div class="section">
            <h2>📋 O que é este relatório?</h2>
            
            <p><strong>Este relatório mostra:</strong></p>
            
            <p class="destaque">
                <span class="destaque-icon">🏙️</span><br>
                Quais cidades recebem energia das linhas de transmissão que saem de Foz do Iguaçu.
            </p>
            
            <p><strong>Região analisada:</strong></p>
            <ul>
                <li>Paraná (PR)</li>
                <li>Santa Catarina (SC)</li>
                <li>Rio Grande do Sul (RS)</li>
            </ul>
        </div>
        
        <!-- NÚMEROS PRINCIPAIS -->
        <div class="section">
            <h2>📊 Números Principais</h2>
            
            <div class="destaque">
                <p><strong>Total de Municípios Afetados:</strong></p>
                <span class="numero-grande">{total_municipios}</span>
                <p>cidades recebem energia dessas linhas</p>
            </div>
            
            <div class="destaque">
                <p><strong>Estados:</strong></p>
                <span class="numero-grande">{total_estados}</span>
                <p>Paraná, Santa Catarina e Rio Grande do Sul</p>
            </div>
            
            <div class="destaque">
                <p><strong>Tipos de Voltagem:</strong></p>
                <span class="numero-grande">{len(voltagens)}</span>
                <p>Diferentes voltagens: {', '.join([str(v) + ' kV' for v in voltagens])}</p>
            </div>
        </div>
        
        <!-- MUNICÍPIOS POR ESTADO -->
        <div class="section">
            <h2>🗺️ Municípios por Estado</h2>
            
            <p><strong>Veja quantas cidades em cada estado:</strong></p>
            
            {pio.to_html(fig_estados, include_plotlyjs=False, full_html=False)}
            
            <div style="margin-top: 30px;">
                <h3>Resumo:</h3>
                <p>
                    <strong>Paraná (PR):</strong> {df_espec[df_espec['Estado']=='PR']['NM_MUN'].nunique()} municípios<br>
                    <strong>Santa Catarina (SC):</strong> {df_espec[df_espec['Estado']=='SC']['NM_MUN'].nunique()} municípios<br>
                    <strong>Rio Grande do Sul (RS):</strong> {df_espec[df_espec['Estado']=='RS']['NM_MUN'].nunique()} municípios
                </p>
            </div>
        </div>
        
        <!-- TOP 10 MUNICÍPIOS -->
        <div class="section">
            <h2>🏆 Top 10 - Municípios com Mais Linhas</h2>
            
            <p><strong>Estas cidades têm várias linhas de transmissão:</strong></p>
            
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Município</th>
                        <th>Estado</th>
                        <th>Linhas</th>
                        <th>Voltagens</th>
                    </tr>
                </thead>
                <tbody>
"""

# Adicionar linhas da tabela Top 10
for idx, row in df_top10.iterrows():
    posicao = idx + 1
    voltagens_badges = ' '.join([
        f'<span class="badge badge-{v.strip()}">{v.strip()} kV</span>' 
        for v in str(row['Voltagens']).split(',')
    ])
    
    html += f"""
                    <tr>
                        <td><strong>{posicao}º</strong></td>
                        <td><strong>{row['Municipio']}</strong></td>
                        <td>{row['Estado']}</td>
                        <td><span class="numero-grande" style="font-size:24px;">{row['Num_Linhas']}</span></td>
                        <td>{voltagens_badges}</td>
                    </tr>
"""

html += f"""
                </tbody>
            </table>
            
            <div class="destaque" style="margin-top: 30px;">
                <p><strong>🎯 Destaque:</strong></p>
                <p style="font-size: 20px;">
                    <strong>{df_top10.iloc[0]['Municipio']} ({df_top10.iloc[0]['Estado']})</strong> 
                    é o município com mais linhas de transmissão: 
                    <strong>{df_top10.iloc[0]['Num_Linhas']} linhas diferentes!</strong>
                </p>
            </div>
        </div>
        
        <!-- O QUE SIGNIFICAM AS VOLTAGENS? -->
        <div class="section">
            <h2>⚡ O que são as Voltagens?</h2>
            
            <p><strong>As linhas de transmissão têm diferentes "forças":</strong></p>
            
            <div style="margin: 25px 0;">
                <div style="padding: 20px; margin: 15px 0; background: #fef5e7; border-radius: 12px; border-left: 6px solid #d68910;">
                    <span class="badge badge-230">230 kV</span>
                    <p><strong>Voltagem Baixa</strong> - Linhas menores, para distâncias curtas</p>
                </div>
                
                <div style="padding: 20px; margin: 15px 0; background: #ebf5fb; border-radius: 12px; border-left: 6px solid #2874a6;">
                    <span class="badge badge-500">500 kV</span>
                    <p><strong>Voltagem Média</strong> - Linhas para distâncias médias</p>
                </div>
                
                <div style="padding: 20px; margin: 15px 0; background: #eafaf1; border-radius: 12px; border-left: 6px solid #1e8449;">
                    <span class="badge badge-525">525 kV</span>
                    <p><strong>Voltagem Média-Alta</strong> - Linhas para longas distâncias</p>
                </div>
                
                <div style="padding: 20px; margin: 15px 0; background: #fef0f0; border-radius: 12px; border-left: 6px solid #c0392b;">
                    <span class="badge badge-600">600 kV</span>
                    <p><strong>Voltagem Alta</strong> - Linhas grandes, para longas distâncias</p>
                </div>
                
                <div style="padding: 20px; margin: 15px 0; background: #f4ecf7; border-radius: 12px; border-left: 6px solid #6c3483;">
                    <span class="badge badge-765">765 kV</span>
                    <p><strong>Voltagem Muito Alta</strong> - As maiores linhas, para distâncias muito longas</p>
                </div>
            </div>
            
            <div class="destaque">
                <p><strong>💡 Resumindo:</strong></p>
                <p style="font-size: 20px;">
                    Quanto maior a voltagem (kV), mais longe a energia pode ir!
                </p>
            </div>
        </div>
        
        <!-- CONCLUSÃO -->
        <div class="section">
            <h2>✅ Conclusão</h2>
            
            <div class="destaque">
                <p style="font-size: 22px; line-height: 2.2;">
                    <strong>A Usina de Foz do Iguaçu distribui energia para {total_municipios} cidades</strong> 
                    nos 3 estados do Sul do Brasil.
                </p>
                
                <p style="font-size: 22px; line-height: 2.2;">
                    As linhas de transmissão usam <strong>{len(voltagens)} tipos diferentes de voltagem</strong> 
                    para levar energia a diferentes distâncias.
                </p>
                
                <p style="font-size: 22px; line-height: 2.2;">
                    Algumas cidades têm <strong>várias linhas passando por elas</strong>, 
                    como {df_top10.iloc[0]['Municipio']} que tem {df_top10.iloc[0]['Num_Linhas']} linhas!
                </p>
            </div>
        </div>
    </div>
    
    <footer>
        <p><strong>👤 Autor:</strong> Ronan Armando Caetano</p>
        <p>📅 Gerado em {now}</p>
        <p style="margin-top: 20px; font-size: 14px;">
            Relatório formatado para melhor acessibilidade<br>
            (Fonte amigável para dislexia • Espaçamento amplo • Cores para facilitar leitura)
        </p>
    </footer>
    
    <script>
        // Tema claro/escuro
        const root = document.documentElement;
        const btn = document.getElementById('themeBtn');
        let isDark = false;
        
        btn.addEventListener('click', function() {{
            isDark = !isDark;
            root.setAttribute('data-theme', isDark ? 'dark' : 'light');
            
            // Atualizar gráficos
            const plots = document.querySelectorAll('.js-plotly-plot');
            plots.forEach(function(p) {{
                const layout = {{
                    paper_bgcolor: 'rgba(0,0,0,0)',
                    plot_bgcolor: 'rgba(0,0,0,0)',
                    font: {{ color: isDark ? '#e2e8f0' : '#2d3748' }}
                }};
                Plotly.relayout(p, layout);
            }});
        }});
    </script>
</body>
</html>
"""

# Salvar arquivo
output_file = output_dir / 'relatorio_acessivel.html'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"OK Relatorio acessivel gerado: {output_file}")
print(f"  Total de municipios: {total_municipios}")
print(f"  Formatacao: Amigavel para TDAH e Dislexia")
