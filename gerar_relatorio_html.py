"""
Gera um relatório HTML único (interativo) com Plotly
Saída: outputs/dashboard.html
"""
from pathlib import Path
import sys
import subprocess
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

BASE_DIR = Path(__file__).parent
OUT_DIR = BASE_DIR / 'outputs'
OUT_DIR.mkdir(exist_ok=True)

CONSOLIDADO_CSV = BASE_DIR / 'dados_consolidados.csv'
MULTIPLAS_CSV = BASE_DIR / 'municipios_multiplas_linhas.csv'


def ensure_data():
    if CONSOLIDADO_CSV.exists() and MULTIPLAS_CSV.exists():
        return
    # Se não existir, executa o consolidado
    print('Dados não encontrados. Executando analise_consolidada.py...')
    subprocess.run([sys.executable, str(BASE_DIR / 'analise_consolidada.py')], check=True)


def load():
    df = pd.read_csv(CONSOLIDADO_CSV)
    df_mult = pd.read_csv(MULTIPLAS_CSV)
    df['Voltagem'] = df['Voltagem'].astype(str)
    df['Estado'] = df['Estado'].astype(str)
    df_espec = df[df['Tipo'] == 'especifica'].copy()
    # Normalização e deduplicação para evitar linhas repetidas
    df_espec['NM_MUN'] = df_espec['NM_MUN'].astype(str).str.strip()
    df_espec['Estado'] = df_espec['Estado'].astype(str).str.strip().str.upper()
    df_espec['Voltagem'] = df_espec['Voltagem'].astype(str).str.strip()
    df_espec = df_espec.drop_duplicates(subset=['NM_MUN', 'Estado', 'Voltagem'])

    # Normaliza e deduplica a tabela de múltiplas linhas também
    if 'Municipio' in df_mult.columns:
        df_mult['Municipio'] = df_mult['Municipio'].astype(str).str.strip()
    if 'Estado' in df_mult.columns:
        df_mult['Estado'] = df_mult['Estado'].astype(str).str.strip().str.upper()
    if 'Voltagens' in df_mult.columns:
        # normaliza espaços e ordem (já vem ordenado do gerador, mas por garantia)
        df_mult['Voltagens'] = (
            df_mult['Voltagens']
            .astype(str)
            .str.split(',')
            .apply(lambda xs: ', '.join(sorted(v.strip() for v in xs)))
        )
    if 'Num_Linhas' in df_mult.columns:
        df_mult['Num_Linhas'] = pd.to_numeric(df_mult['Num_Linhas'], errors='coerce').fillna(0).astype(int)
    df_mult = df_mult.drop_duplicates(subset=['Municipio', 'Estado', 'Num_Linhas', 'Voltagens'])
    return df, df_espec, df_mult


def build_figures(df, df_espec, df_mult):
    figs = []

    # 1. Municípios por voltagem
    s_volt = (
        df_espec.groupby('Voltagem')['NM_MUN']
        .nunique()
        .sort_index(key=lambda x: x.astype(int))
    )
    fig1 = px.bar(
        s_volt,
        orientation='h',
        labels={'value': 'Municípios', 'Voltagem': 'kV'},
        text_auto=True,
        title='Municípios afetados por voltagem (kV)'
    )
    fig1.update_layout(yaxis_title='Voltagem (kV)', xaxis_title='Número de Municípios')
    figs.append(('Municípios por voltagem', fig1))

    # 2. Municípios por estado
    s_estado = df.groupby('Estado')['NM_MUN'].nunique().sort_values(ascending=False)
    fig2 = px.bar(
        s_estado,
        text_auto=True,
        labels={'value': 'Municípios', 'Estado': 'Estado'},
        title='Municípios afetados por estado'
    )
    fig2.update_layout(xaxis_title='Estado', yaxis_title='Número de Municípios')
    figs.append(('Municípios por estado', fig2))

    # 3. Distribuição: nº de linhas por município
    mun_lin = df_espec.groupby('NM_MUN')['Linha'].nunique()
    dist = mun_lin.value_counts().sort_index()
    fig3 = px.bar(
        dist,
        labels={'index': 'Nº de Linhas', 'value': 'Qtd de Municípios'},
        text_auto=True,
        title='Distribuição: quantas linhas atravessam cada município'
    )
    fig3.update_layout(xaxis=dict(type='category'))
    figs.append(('Distribuição por município', fig3))

    # 4. Matriz estado x voltagem
    mat = df_espec.groupby(['Estado', 'Voltagem'])['NM_MUN'].nunique().unstack(fill_value=0)
    fig4 = px.imshow(
        mat,
        text_auto=True,
        color_continuous_scale='YlOrRd',
        aspect='auto',
        title='Matriz: municípios por estado e voltagem'
    )
    fig4.update_layout(xaxis_title='Voltagem (kV)', yaxis_title='Estado')
    figs.append(('Matriz estado x voltagem', fig4))

    # 5. Tabela: municípios com múltiplas linhas
    # Dedup por segurança antes de ordenar
    df_top = df_mult.drop_duplicates(subset=['Municipio','Estado','Num_Linhas','Voltagens']).sort_values('Num_Linhas', ascending=False)
    head = df_top.head(25)
    table = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=list(head.columns), 
                    fill_color='#4a5568',  # Cor que funciona em ambos os temas
                    align='left',
                    font=dict(color='white', size=12)
                ),
                cells=dict(
                    values=[head[c] for c in head.columns], 
                    align='left',
                    fill_color='rgba(255,255,255,0.05)',  # Fundo translúcido
                    font=dict(size=11),
                    line=dict(color='rgba(128,128,128,0.3)', width=1)
                )
            )
        ]
    )
    table.update_layout(
        title='Top municípios com mais linhas (Top 25)',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    figs.append(('Top municípios', table))

    return figs

def build_full_table_html(df_all):
    # Gera uma tabela HTML com busca (client-side), filtros por voltagem/estado e links Google Maps
    # Coleta valores únicos para os filtros
    voltagens_unicas = sorted(set(v.strip() for row in df_all['Voltagens'] for v in str(row).split(',')), key=lambda x: int(x) if x.isdigit() else 999)
    estados_unicos = sorted(df_all['Estado'].unique())
    
    # Gera as linhas da tabela com atributos data-* para filtragem e link Google Maps
    rows_html = []
    for _, r in df_all.iterrows():
        municipio = r['Municipio']
        estado = r['Estado']
        num_linhas = r['Num_Linhas']
        voltagens = r['Voltagens']
        # Link Google Maps usando query
        maps_link = f"https://www.google.com/maps/search/?api=1&query={municipio}+{estado}+Brasil"
        rows_html.append(
            f"<tr data-voltagens='{voltagens}' data-estado='{estado}'>"
            f"<td><a href='{maps_link}' target='_blank' style='color:var(--primary);text-decoration:none;'>{municipio}</a></td>"
            f"<td>{estado}</td>"
            f"<td style='text-align:center'>{num_linhas}</td>"
            f"<td>{voltagens}</td>"
            f"</tr>"
        )
    
    # Monta os options dos filtros
    voltagem_options = ''.join(f"<option value='{v}'>{v} kV</option>" for v in voltagens_unicas)
    estado_options = ''.join(f"<option value='{e}'>{e}</option>" for e in estados_unicos)
    
    table_html = f"""
    <section>
        <h2>Todos os municípios afetados</h2>
        <p>Lista completa de municípios afetados por linhas de transmissão. Ao clicar em um município, você pode abrir sua localização no Google Maps para inspeção rápida.</p>
        
        <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(200px,1fr));gap:12px;margin:12px 0;">
            <div>
                <label style="display:block;margin-bottom:4px;font-weight:600;font-size:13px;">Layer (Voltagem)</label>
                <select id="filterVoltagem" style="width:100%;padding:8px;border:1px solid var(--border);border-radius:8px;background:var(--card-bg);color:var(--fg);">
                    <option value="">Todas as voltagens</option>
                    {voltagem_options}
                </select>
            </div>
            <div>
                <label style="display:block;margin-bottom:4px;font-weight:600;font-size:13px;">Estado (UF)</label>
                <select id="filterEstado" style="width:100%;padding:8px;border:1px solid var(--border);border-radius:8px;background:var(--card-bg);color:var(--fg);">
                    <option value="">Todos</option>
                    {estado_options}
                </select>
            </div>
            <div>
                <label style="display:block;margin-bottom:4px;font-weight:600;font-size:13px;">Buscar município</label>
                <input id="filterMunicipio" type="text" placeholder="Digite nome do município (ex.: Florianópolis)" style="width:100%;padding:8px;border:1px solid var(--border);border-radius:8px;background:var(--card-bg);color:var(--fg);" />
            </div>
        </div>
        
        <div style="margin:12px 0;padding:10px;background:rgba(0,0,0,0.02);border:1px solid var(--border);border-radius:8px;">
            <strong style="font-size:14px;">Downloads</strong>
            <div style="margin-top:8px;display:flex;flex-wrap:wrap;gap:8px;">
                <a href="municipios_afetados_completo.csv" download style="padding:6px 12px;background:var(--primary);color:#fff;border-radius:6px;text-decoration:none;font-size:13px;">📥 municipios_afetados_completo.csv</a>
            </div>
        </div>
        
        <div style="overflow:auto;">
            <table id="fullTable" style="border-collapse:collapse;width:100%;">
                <thead>
                    <tr style="background:rgba(0,0,0,0.03);">
                        <th style="text-align:left;border-bottom:1px solid var(--border);padding:8px;">Município</th>
                        <th style="text-align:left;border-bottom:1px solid var(--border);padding:8px;">Estado</th>
                        <th style="text-align:center;border-bottom:1px solid var(--border);padding:8px;">Nº Linhas</th>
                        <th style="text-align:left;border-bottom:1px solid var(--border);padding:8px;">Voltagens (kV)</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(rows_html)}
                </tbody>
            </table>
        </div>
    </section>
    <script>
        (function(){{
            const filterVoltagem = document.getElementById('filterVoltagem');
            const filterEstado = document.getElementById('filterEstado');
            const filterMunicipio = document.getElementById('filterMunicipio');
            const table = document.getElementById('fullTable');
            
            function applyFilters() {{
                const voltagemSel = (filterVoltagem.value || '').trim();
                const estadoSel = (filterEstado.value || '').trim();
                const municipioQ = (filterMunicipio.value || '').toLowerCase();
                
                const rows = table.querySelectorAll('tbody tr');
                rows.forEach(function(tr) {{
                    const voltagens = tr.getAttribute('data-voltagens') || '';
                    const estado = tr.getAttribute('data-estado') || '';
                    const texto = tr.innerText.toLowerCase();
                    
                    let show = true;
                    if (voltagemSel && !voltagens.includes(voltagemSel)) show = false;
                    if (estadoSel && estado !== estadoSel) show = false;
                    if (municipioQ && !texto.includes(municipioQ)) show = false;
                    
                    tr.style.display = show ? '' : 'none';
                }});
            }}
            
            filterVoltagem && filterVoltagem.addEventListener('change', applyFilters);
            filterEstado && filterEstado.addEventListener('change', applyFilters);
            filterMunicipio && filterMunicipio.addEventListener('keyup', applyFilters);
        }})();
    </script>
    """
    return table_html


def build_html(figs, df_all):
    # Compor um HTML único com todas as figuras inline
    parts = []
    for title, fig in figs:
        html = pio.to_html(fig, include_plotlyjs=False, full_html=False)
        section = f"""
        <section>
            <h2>{title}</h2>
            {html}
        </section>
        """
        parts.append(section)

    # Adiciona a tabela completa uma única vez ao final
    parts.append(build_full_table_html(df_all))

    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    template = f"""
<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Dashboard – Linhas de Transmissão (Foz do Iguaçu)</title>
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
        :root {{
            --bg: #fafafa;
            --fg: #222222;
            --card-bg: #ffffff;
            --border: #eeeeee;
            --primary: #0f4c81;
            --muted: #666666;
        }}
        :root[data-theme='dark'] {{
            --bg: #0f172a;
            --fg: #e5e7eb;
            --card-bg: #111827;
            --border: #1f2937;
            --primary: #60a5fa;
            --muted: #9ca3af;
        }}
        body {{ font-family: -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; margin: 0; padding: 0; background: var(--bg); color: var(--fg); transition: background .2s ease, color .2s ease; }}
        .js-plotly-plot .table text {{ fill: var(--fg) !important; }}
        header {{ background: var(--primary); color: #fff; padding: 24px; }}
    header h1 {{ margin: 0; font-size: 22px; }}
        header p {{ margin: 6px 0 0; opacity: 0.95; }}
        .header-actions {{ display:flex; gap:8px; align-items:center; margin-top:8px; }}
        .btn {{ cursor:pointer; border:1px solid rgba(255,255,255,.5); background: transparent; color:#fff; padding:6px 10px; border-radius:8px; font-size: 13px; }}
        .btn:hover {{ background: rgba(255,255,255,.1); }}
    main {{ max-width: 1120px; margin: 24px auto; padding: 0 16px; }}
        section {{ background: var(--card-bg); border: 1px solid var(--border); border-radius: 10px; padding: 16px; margin-bottom: 16px; box-shadow: 0 1px 2px rgba(0,0,0,0.04); }}
        h2 {{ font-size: 18px; margin: 4px 0 12px; color: var(--primary); }}
        h3 {{ font-size: 16px; margin-top: 20px; margin-bottom: 8px; color: var(--primary); }}
        ul {{ line-height: 1.8; color: var(--fg); }}
        ul ul {{ margin-top: 6px; }}
        .intro-section {{ background: linear-gradient(135deg, var(--card-bg) 0%, var(--card-bg) 100%); border-left: 4px solid var(--primary); }}
        footer {{ max-width: 1120px; margin: 24px auto; padding: 0 16px 24px; color: var(--muted); line-height: 1.6; }}
        footer ul {{ margin: 8px 0 12px 0; padding-left: 20px; }}
        footer ul li {{ margin: 4px 0; }}
    .kpi {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 16px; }}
        .card {{ background:var(--card-bg); border:1px solid var(--border); border-radius:10px; padding:12px; text-align:center; }}
    .card .big {{ font-size:24px; font-weight:700; }}
    @media (max-width: 800px) {{ .kpi {{ grid-template-columns: repeat(2, 1fr); }} }}
  </style>
</head>
<body>
  <header>
    <h1>Dashboard – Linhas de Transmissão (Foz do Iguaçu)</h1>
    <p>Municípios afetados por linha de transmissão — Atualizado em {now}</p>
        <div class=\"header-actions\">
            <button id=\"themeToggle\" class=\"btn\">Alternar tema (Claro/Escuro)</button>
        </div>
  </header>
  <main>
    <section class="intro-section">
      <h2>📊 Sobre este Dashboard</h2>
      <p style="line-height:1.6; margin-bottom:12px;">
        Este dashboard apresenta uma análise detalhada dos <strong>municípios afetados pelas linhas de transmissão</strong> 
        que partem da <strong>Usina Hidrelétrica de Foz do Iguaçu</strong> e distribuem energia para a região Sul do Brasil 
        (Paraná, Santa Catarina e Rio Grande do Sul).
      </p>
      <p style="line-height:1.6; margin-bottom:12px;">
        Os dados incluem linhas de transmissão de diferentes voltagens: <strong>230 kV, 500 kV, 525 kV, 600 kV e 765 kV</strong>, 
        totalizando <strong>517 municípios únicos</strong> afetados em toda a região Sul.
      </p>
      
      <h3 style="font-size:16px; margin-top:20px; margin-bottom:8px; color:var(--primary);">💡 Como Utilizar</h3>
      <ul style="line-height:1.8;">
        <li><strong>Visualizações Interativas:</strong> Passe o mouse sobre os gráficos para ver detalhes. Clique nas legendas para mostrar/ocultar séries.</li>
        <li><strong>Tema Claro/Escuro:</strong> Use o botão no topo da página para alternar entre os modos claro e escuro.</li>
        <li><strong>Filtros na Tabela Completa:</strong> Na seção "Todos os municípios afetados", você pode:
          <ul>
            <li>Filtrar por <strong>Voltagem</strong> (Layer): selecione uma voltagem específica no menu suspenso</li>
            <li>Filtrar por <strong>Estado</strong>: escolha PR, RS ou SC</li>
            <li>Buscar por <strong>Município</strong>: digite o nome para localizar rapidamente</li>
          </ul>
        </li>
        <li><strong>Google Maps:</strong> Clique no nome de qualquer município para visualizar sua localização no Google Maps.</li>
        <li><strong>Download de Dados:</strong> Baixe a tabela completa em formato CSV usando o botão de download.</li>
      </ul>
    </section>
    {''.join(parts)}
  </main>
  <footer>
    <div style="border-top: 1px solid var(--border); padding-top: 16px; margin-bottom: 12px;">
      <p style="margin: 0 0 8px 0; font-size: 14px;"><strong>👤 Autor:</strong> Ronan Armando Caetano</p>
      <p style="margin: 0 0 8px 0; font-size: 13px;"><strong>🛠️ Softwares Utilizados:</strong></p>
      <ul style="margin: 0 0 12px 0; padding-left: 20px; font-size: 13px; line-height: 1.6;">
        <li><strong>Python 3.13</strong> - Linguagem de programação</li>
        <li><strong>Pandas</strong> - Manipulação e análise de dados</li>
        <li><strong>Plotly</strong> - Visualizações interativas</li>
        <li><strong>GeoPandas/QGIS</strong> - Processamento de dados geoespaciais</li>
        <li><strong>Streamlit</strong> - Dashboard interativo</li>
      </ul>
      <p style="margin: 0; font-size: 12px; opacity: 0.8;">
        <strong>🤖 Assistência Técnica:</strong> GitHub Copilot - Auxílio no desenvolvimento, análise de dados e criação do dashboard
      </p>
    </div>
    <p style="margin: 0; font-size: 12px; opacity: 0.7;">Gerado automaticamente por gerar_relatorio_html.py</p>
  </footer>
    <script>
        (function() {{
            const root = document.documentElement;
            const saved = localStorage.getItem('theme');
            const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
            function applyTheme(theme) {{
                root.setAttribute('data-theme', theme);
                try {{
                    const isDark = theme === 'dark';
                    const plots = document.querySelectorAll('.js-plotly-plot');
                    plots.forEach(function(p) {{
                        // Tenta alternar template; se não suportado, ajusta cores básicas
                        const layout = {{
                            template: isDark ? 'plotly_dark' : 'plotly_white',
                            paper_bgcolor: 'rgba(0,0,0,0)',
                            plot_bgcolor: 'rgba(0,0,0,0)',
                            font: {{ color: getComputedStyle(root).getPropertyValue('--fg').trim() }}
                        }};
                        Plotly.relayout(p, layout);
                    }});
                }} catch (e) {{ /* ignora erros de reestilização */ }}
            }}
            const initial = saved || (prefersDark ? 'dark' : 'light');
            applyTheme(initial);
            localStorage.setItem('theme', initial);
            const btn = document.getElementById('themeToggle');
            if (btn) {{
                btn.addEventListener('click', function() {{
                    const current = root.getAttribute('data-theme') || 'light';
                    const next = current === 'light' ? 'dark' : 'light';
                    localStorage.setItem('theme', next);
                    applyTheme(next);
                }});
            }}
        }})();
    </script>
</body>
</html>
"""
    return template


def main():
    ensure_data()
    df, df_espec, df_mult = load()
    # Monta tabela completa por município+estado com voltagens agregadas
    agg = (
        df_espec.groupby(['NM_MUN', 'Estado'])['Voltagem']
        .apply(lambda s: sorted(set(s), key=lambda x: int(x)))
        .reset_index(name='VoltagensList')
    )
    agg['Num_Linhas'] = agg['VoltagensList'].apply(len)
    agg['Voltagens'] = agg['VoltagensList'].apply(lambda vs: ', '.join(vs))
    df_all = agg.rename(columns={'NM_MUN': 'Municipio'})[['Municipio', 'Estado', 'Num_Linhas', 'Voltagens']]
    # Salva CSV completo para publicação
    out_csv = OUT_DIR / 'municipios_afetados_completo.csv'
    df_all.to_csv(out_csv, index=False, encoding='utf-8-sig')
    figs = build_figures(df, df_espec, df_mult)
    html = build_html(figs, df_all)
    out_path = OUT_DIR / 'dashboard.html'
    out_path.write_text(html, encoding='utf-8')
    print(f'✓ Relatório gerado: {out_path}')


if __name__ == '__main__':
    main()
