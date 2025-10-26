
"""
Gera mapas interativos individuais para cada linha de transmissão por estado
Ignora combinações que não existem nos dados (ex: 230kV em RS, 500kV em RS, etc)
Saída: outputs/mapas/
"""
from pathlib import Path
import zipfile
import pandas as pd
import geopandas as gpd
import fiona
import folium
from folium import plugins
import warnings
warnings.filterwarnings('ignore')

BASE_DIR = Path(__file__).parent
OUT_DIR = BASE_DIR / 'outputs' / 'mapas'
OUT_DIR.mkdir(parents=True, exist_ok=True)
ESTADOS_DIR = BASE_DIR / 'Shapefile_Estados'

# Arquivos de entrada
CONSOLIDADO_CSV = BASE_DIR / 'dados_consolidados.csv'
MUNICIPIOS_GPKG = BASE_DIR / 'municipios_afetados_por_layer.gpkg'
LINHAS_GPKG = BASE_DIR / 'linhas_recortadas.gpkg'
FAIXA_SERVIDAO_GPKG = BASE_DIR / 'faixa_servidao.gpkg'

# Cores por voltagem
CORES_VOLTAGEM = {
    '230': '#FFA500',  # Laranja
    '500': '#FF0000',  # Vermelho
    '525': '#8B0000',  # Vermelho escuro
    '600': '#4B0082',  # Índigo
    '765': '#800080',  # Roxo
    'BASE': '#808080'  # Cinza
}

def carregar_dados():
    """Carrega dados CSV e GeoPackages"""
    print("📂 Carregando dados...")
    
    # CSV consolidado
    df = pd.read_csv(CONSOLIDADO_CSV)
    df['Voltagem'] = df['Voltagem'].astype(str)
    df['Estado'] = df['Estado'].astype(str).str.upper()
    
    # Filtra apenas linhas específicas (não BASE)
    df_espec = df[df['Tipo'] == 'especifica'].copy()
    
    # Listar camadas disponíveis (evita carregar tudo na memória)
    try:
        municipios_layers = fiona.listlayers(str(MUNICIPIOS_GPKG))
        print(f"  ✓ Camadas de municípios: {len(municipios_layers)} layers")
    except Exception as e:
        print(f"  ⚠️  Erro ao listar camadas de municípios: {e}")
        municipios_layers = []

    try:
        linhas_layers = fiona.listlayers(str(LINHAS_GPKG))
        print(f"  ✓ Camadas de linhas recortadas: {len(linhas_layers)} layers")
    except Exception as e:
        print(f"  ⚠️  Erro ao listar camadas de linhas: {e}")
        linhas_layers = []

    try:
        faixa_layers = fiona.listlayers(str(FAIXA_SERVIDAO_GPKG))
        print(f"  ✓ Camadas em faixa de servidão: {len(faixa_layers)} layers")
    except Exception as e:
        print(f"  ⚠️  Erro ao listar camadas de faixa de servidão: {e}")
        faixa_layers = []
    
    return df_espec, municipios_layers, linhas_layers, faixa_layers


def _read_municipios_layer(voltagem: str, estado: str):
    """Lê a camada de municípios para a voltagem e filtra por UF do estado."""
    layer_name = f"municipios_afetados_linha_trans_{voltagem}"
    if not MUNICIPIOS_GPKG.exists():
        return None
    try:
        gdf = gpd.read_file(MUNICIPIOS_GPKG, layer=layer_name)
    except Exception:
        # fallback para layer base
        try:
            gdf = gpd.read_file(MUNICIPIOS_GPKG, layer='municipios_afetados_linhas_de_transmissao_base')
        except Exception:
            return None
    # filtra pela UF
    uf_col = 'UF' if 'UF' in gdf.columns else ('SIGLA_UF' if 'SIGLA_UF' in gdf.columns else None)
    if uf_col:
        gdf = gdf[gdf[uf_col].astype(str).str.upper() == estado]
    # reprojeta para WGS84
    if gdf.crs and gdf.crs.to_epsg() != 4326:
        try:
            gdf = gdf.to_crs(epsg=4326)
        except Exception:
            pass
    # reduzir colunas para minimizar tamanho do GeoJSON
    cols_keep = [c for c in ['NM_MUN', 'UF'] if c in gdf.columns]
    try:
        gdf = gdf[cols_keep + ['geometry']]
    except Exception:
        gdf = gdf[['geometry']]
    return gdf


def _read_lines_layer(voltagem: str, estado: str):
    """Obtém linhas para a combinação voltagem-estado.
    1) tenta linhas_recortadas.gpkg layer linha_trans_{voltagem}_{estado}
    2) fallback: faixa_servidao.gpkg layer linha_transmissao_{voltagem} e recorta pelos municípios do estado
    """
    # 1) tenta layer específica por estado
    layer_state = f"linha_trans_{voltagem}_{estado}"
    try:
        gdf = gpd.read_file(LINHAS_GPKG, layer=layer_state)
        # já está em 4326 conforme inspeção
        # manter apenas colunas necessárias para evitar problemas de serialização
        cols = [c for c in ['Nome'] if c in gdf.columns]
        gdf = gdf[cols + ['geometry']]
        return gdf
    except Exception:
        gdf = None
    # 2) fallback: camada geral por voltagem na faixa de servidão
    layer_faixa = f"linha_transmissao_{voltagem}"
    try:
        gdf = gpd.read_file(FAIXA_SERVIDAO_GPKG, layer=layer_faixa)
    except Exception:
        return None
    # garantir WGS84
    if gdf.crs and gdf.crs.to_epsg() != 4326:
        try:
            gdf = gdf.to_crs(epsg=4326)
        except Exception:
            pass
    # manter apenas colunas necessárias e converter tipos não serializáveis
    # reduz propriedades para Nome (se existir)
    cols = [c for c in ['Nome'] if c in gdf.columns]
    if cols:
        gdf = gdf[cols + ['geometry']]
    # recortar por municípios do estado
    gdf_muns = _read_municipios_layer(voltagem, estado)
    if gdf_muns is not None and not gdf_muns.empty:
        try:
            gdf = gpd.clip(gdf, gdf_muns)
        except Exception:
            pass
    return gdf


def _make_buffer(lines_gdf: gpd.GeoDataFrame, voltagem: str):
    """Cria buffer (faixa de servidão aproximada) em metros a partir das linhas."""
    if lines_gdf is None or lines_gdf.empty:
        return None
    # distâncias aproximadas por voltagem (metros)
    BUF = {'230': 60, '500': 80, '525': 80, '600': 90, '765': 100}
    dist = BUF.get(voltagem, 60)
    g = lines_gdf.copy()
    # projeta para métrica (Web Mercator) para buffer rápido
    try:
        g_m = g.to_crs(epsg=3857)
        g_buf = g_m.buffer(dist)
        gdf_buf = gpd.GeoDataFrame(geometry=g_buf, crs='EPSG:3857').to_crs(epsg=4326)
        # dissolve para reduzir quantidade de features
        gdf_buf = gdf_buf.dissolve()
        gdf_buf = gpd.GeoDataFrame(geometry=gdf_buf.geometry.explode(index_parts=False), crs='EPSG:4326')
        return gdf_buf
    except Exception:
        return None


def _unzip_state_shapefiles():
    """Garante que os shapefiles de estados em ESTADOS_DIR (zipados) estejam extraídos.
    Retorna uma lista de caminhos .shp encontrados após extração.
    """
    shps = []
    if not ESTADOS_DIR.exists():
        return shps
    # extrai todos os .zip para pastas homônimas
    for z in ESTADOS_DIR.glob('*.zip'):
        target_dir = z.with_suffix('')
        if not target_dir.exists():
            try:
                with zipfile.ZipFile(z, 'r') as zip_ref:
                    zip_ref.extractall(target_dir)
            except Exception:
                continue
        # acumula .shp dentro da pasta extraída
        shps.extend(target_dir.rglob('*.shp'))
    # também adiciona quaisquer .shp soltos dentro da pasta ESTADOS_DIR
    shps.extend(ESTADOS_DIR.glob('*.shp'))
    return shps


def _find_state_shapefile(estado: str) -> Path | None:
    """Procura no workspace um shapefile do estado (PR/SC/RS) por nome do arquivo.
    Retorna o caminho do .shp se encontrado.
    """
    estado = estado.upper()
    tokens = {
        'PR': ['pr', 'parana', 'paraná'],
        'SC': ['sc', 'santa_catarina', 'santa catarina'],
        'RS': ['rs', 'rio_grande_do_sul', 'rio grande do sul']
    }.get(estado, [estado.lower()])
    # 1) prioriza shapefiles extraídos/presentes em Shapefile_Estados
    for shp in _unzip_state_shapefiles():
        name = shp.name.lower()
        if any(tok in name for tok in tokens):
            return shp
    # 2) percorre recursivamente no projeto procurando por .shp que contenha o token
    for shp in BASE_DIR.rglob('*.shp'):
        name = shp.name.lower()
        if any(tok in name for tok in tokens):
            return shp
    return None


def _find_municipios_shapefile_for_state(estado: str) -> Path | None:
    """Procura um shapefile/GeoPackage de MUNICÍPIOS para a UF.
    Heurística: nomes contendo 'munic' e tokens de UF; prioriza dentro de Shapefile_Estados.
    """
    estado = estado.upper()
    tokens_uf = {
        'PR': ['pr', 'parana', 'paraná'],
        'SC': ['sc', 'santa_catarina', 'santa catarina'],
        'RS': ['rs', 'rio_grande_do_sul', 'rio grande do sul']
    }.get(estado, [estado.lower()])
    muni_tokens = ['munic', 'municip', 'municipio', 'município', 'munis']

    # 1) procurar em ESTADOS_DIR extraído e raiz
    candidates = []
    # dentro de zip extraídos
    for shp in ESTADOS_DIR.rglob('*.shp') if ESTADOS_DIR.exists() else []:
        name = shp.name.lower()
        if any(mt in name for mt in muni_tokens) and any(ut in name for ut in tokens_uf):
            candidates.append(shp)
    # soltos em ESTADOS_DIR
    for shp in ESTADOS_DIR.glob('*.shp') if ESTADOS_DIR.exists() else []:
        name = shp.name.lower()
        if any(mt in name for mt in muni_tokens) and any(ut in name for ut in tokens_uf):
            candidates.append(shp)
    if candidates:
        return sorted(candidates, key=lambda p: len(p.name))[0]

    # 2) procurar no projeto
    for shp in BASE_DIR.rglob('*.shp'):
        name = shp.name.lower()
        if any(mt in name for mt in muni_tokens) and any(ut in name for ut in tokens_uf):
            return shp
    # 3) também considerar GeoPackage
    for gpkg in BASE_DIR.rglob('*.gpkg'):
        name = gpkg.name.lower()
        if any(mt in name for mt in muni_tokens) and any(ut in name for ut in tokens_uf):
            return gpkg
    return None


def _read_all_municipios_for_state(estado: str):
    """Tenta ler todos os municípios da UF a partir de shapefile/GeoPackage externo.
    - Se no arquivo existir coluna UF/SIGLA_UF, usa filtro; senão, infere UF pelo nome do arquivo.
    - Retorna GeoDataFrame em EPSG:4326 com colunas ['NM_MUN','UF','geometry'].
    """
    src = _find_municipios_shapefile_for_state(estado)
    if src is None:
        return None
    try:
        if src.suffix.lower() == '.gpkg':
            # tenta descobrir primeira layer poligonal
            try:
                layers = fiona.listlayers(str(src))
            except Exception:
                layers = []
            gdf = None
            for lyr in layers:
                try:
                    tmp = gpd.read_file(src, layer=lyr)
                    if not tmp.empty and tmp.geom_type.str.contains('Polygon', case=False).any():
                        gdf = tmp
                        break
                except Exception:
                    continue
            if gdf is None:
                return None
        else:
            gdf = gpd.read_file(src)
    except Exception:
        return None
    # CRS
    if gdf.crs and gdf.crs.to_epsg() != 4326:
        try:
            gdf = gdf.to_crs(epsg=4326)
        except Exception:
            pass
    # Detecta UF
    uf_col = None
    for c in ['UF', 'SIGLA_UF', 'sigla_uf', 'Sigla_UF']:
        if c in gdf.columns:
            uf_col = c
            break
    if uf_col:
        gdf = gdf[gdf[uf_col].astype(str).str.upper() == estado.upper()].copy()
        gdf = gdf.rename(columns={uf_col: 'UF'})
    else:
        gdf = gdf.copy()
        gdf['UF'] = estado.upper()
    # Detecta nome municipio
    name_col = None
    for c in ['NM_MUN', 'NM_MUNICIP', 'NM_MUNICIPIO', 'NM_MUNIC', 'NOME', 'NAME', 'nm_mun', 'nm_municip', 'nm_municipio']:
        if c in gdf.columns:
            name_col = c
            break
    if name_col and name_col != 'NM_MUN':
        gdf = gdf.rename(columns={name_col: 'NM_MUN'})
    if 'NM_MUN' not in gdf.columns:
        # último recurso: cria nomes sequenciais (não ideal, mas evita falha)
        gdf['NM_MUN'] = [f'MUN_{i}' for i in range(len(gdf))]
    try:
        gdf = gdf[['NM_MUN', 'UF', 'geometry']]
    except Exception:
        gdf = gpd.GeoDataFrame(gdf[['geometry']]).assign(UF=estado.upper(), NM_MUN=[f'MUN_{i}' for i in range(len(gdf))])
    return gdf


def _simplify_geoms(gdf: gpd.GeoDataFrame, tol_m: float, preserve_topology: bool = True):
    """Simplifica geometrias em metros usando projecção métrica (EPSG:3857) e retorna em EPSG:4326.
    Se reprojeção falhar, aplica tolerância aproximada em graus.
    """
    if gdf is None or gdf.empty:
        return gdf
    try:
        g = gdf.copy()
        # projeta para 3857
        try:
            g_m = g.to_crs(epsg=3857)
            g_m['geometry'] = g_m.geometry.simplify(tol_m, preserve_topology=preserve_topology)
            g_s = g_m.to_crs(epsg=4326)
        except Exception:
            # fallback em graus (aprox 1 grau ~ 111.320 m)
            deg_tol = max(tol_m / 111320.0, 1e-6)
            g_s = g.copy()
            g_s['geometry'] = g_s.geometry.simplify(deg_tol, preserve_topology=preserve_topology)
        # remove vazios
        try:
            g_s = g_s[~g_s.geometry.is_empty & g_s.geometry.notna()]
        except Exception:
            pass
        return g_s
    except Exception:
        return gdf


def _read_state_boundary_from_shp(estado: str):
    """Lê o limite estadual a partir de um shapefile específico do estado, se existir.
    Caso não encontre ou não seja poligonal, retorna None.
    """
    shp = _find_state_shapefile(estado)
    if shp is None:
        return None
    try:
        gdf = gpd.read_file(shp)
    except Exception:
        return None
    # Verifica se é poligonal
    try:
        geom_types = set(gdf.geom_type.str.lower().unique())
        if not any(t in geom_types for t in ['polygon', 'multipolygon']):
            return None
    except Exception:
        return None
    # CRS para WGS84
    if gdf.crs and gdf.crs.to_epsg() != 4326:
        try:
            gdf = gdf.to_crs(epsg=4326)
        except Exception:
            pass
    # mantém apenas geometria e UF
    gdf = gdf.copy()
    if 'UF' not in gdf.columns:
        gdf['UF'] = estado.upper()
    else:
        gdf['UF'] = gdf['UF'].astype(str).str.upper().fillna(estado.upper())
    try:
        gdf = gdf[['UF', 'geometry']]
    except Exception:
        gdf = gpd.GeoDataFrame({'UF': [estado.upper()]}, geometry=gdf.geometry, crs=gdf.crs)
    # Se houver múltiplas feições, optar por dissolver por UF para uma borda única
    try:
        gdf = gdf.dissolve(by='UF').reset_index()
    except Exception:
        pass
    return gdf


def _read_state_boundaries_from_base(estado: str):
    """Fallback: cria limite estadual a partir da camada base de municípios (filtra apenas a UF pedida)."""
    try:
        gdf = gpd.read_file(MUNICIPIOS_GPKG, layer='municipios_afetados_linhas_de_transmissao_base')
    except Exception:
        return None
    uf_col = 'UF' if 'UF' in gdf.columns else ('SIGLA_UF' if 'SIGLA_UF' in gdf.columns else None)
    if not uf_col:
        return None
    gdf = gdf[gdf[uf_col].astype(str).str.upper() == estado.upper()].copy()
    if gdf.empty:
        return None
    if gdf.crs and gdf.crs.to_epsg() != 4326:
        try:
            gdf = gdf.to_crs(epsg=4326)
        except Exception:
            pass
    gdf = gdf.rename(columns={uf_col: 'UF'})
    try:
        gdf = gdf[['UF', 'geometry']]
    except Exception:
        gdf = gpd.GeoDataFrame({'UF': [estado.upper()]}, geometry=gdf.geometry, crs=gdf.crs)
    # não fazer dissolve pesado; limites municipais já dão o contorno do estado
    return gdf


def identificar_combinacoes(df):
    """Identifica quais combinações de voltagem x estado existem nos dados"""
    combinacoes = df.groupby(['Voltagem', 'Estado']).size().reset_index(name='count')
    combinacoes = combinacoes[combinacoes['Voltagem'] != 'BASE']  # Ignora BASE
    
    print(f"\n📊 Combinações encontradas: {len(combinacoes)}")
    for _, row in combinacoes.iterrows():
        print(f"  • {row['Voltagem']} kV - {row['Estado']}: {row['count']} municípios")
    
    return combinacoes


def criar_mapa_base(titulo, subtitulo="", min_zoom: int = 5, max_zoom: int = 12):
    """Cria mapa base Folium centrado na região Sul, com limites de zoom."""
    mapa = folium.Map(
        location=[-26.0, -51.0],  # Centro aproximado do Sul do Brasil
        zoom_start=7,
        tiles='OpenStreetMap',
        control_scale=True,
        min_zoom=min_zoom,
        max_zoom=max_zoom
    )
    
    # Título
    titulo_html = f'''
    <div style="position: fixed; 
                top: 10px; 
                left: 50px; 
                width: auto;
                max-width: 500px;
                background-color: white; 
                border: 2px solid #0f4c81;
                border-radius: 8px;
                padding: 10px 15px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                z-index: 9999;
                font-family: Arial, sans-serif;">
        <h3 style="margin: 0 0 5px 0; color: #0f4c81; font-size: 16px;">{titulo}</h3>
        <p style="margin: 0; color: #666; font-size: 12px;">{subtitulo}</p>
    </div>
    '''
    mapa.get_root().html.add_child(folium.Element(titulo_html))
    
    return mapa


def adicionar_camadas(mapa, gdf_municipios, gdf_linhas, gdf_buffer, voltagem, estado):
    """Adiciona camadas de municípios, linhas e buffer ao mapa.
    Observação: os parâmetros gdf_* não são mais utilizados; os dados são lidos por camada sob demanda.
    """
    cor_voltagem = CORES_VOLTAGEM.get(voltagem, '#808080')

    # Municípios afetados (por layer e UF)
    gdf_mun_filtrado = _read_municipios_layer(voltagem, estado)

    # Municípios não afetados (fundo), se camada completa existir
    gdf_all_muns = _read_all_municipios_for_state(estado)
    if (gdf_all_muns is not None) and (not gdf_all_muns.empty):
        try:
            # alinhar nomes
            if (gdf_mun_filtrado is not None) and (not gdf_mun_filtrado.empty) and ('NM_MUN' in gdf_mun_filtrado.columns):
                afetados = set(gdf_mun_filtrado['NM_MUN'].astype(str).str.upper().unique())
                gdf_all_muns['NM_MUN_UP'] = gdf_all_muns['NM_MUN'].astype(str).str.upper()
                gdf_nao = gdf_all_muns[~gdf_all_muns['NM_MUN_UP'].isin(afetados)][['NM_MUN', 'UF', 'geometry']]
            else:
                gdf_nao = gdf_all_muns[['NM_MUN', 'UF', 'geometry']]
            # simplificação mais forte no fundo
            gdf_nao = _simplify_geoms(gdf_nao, tol_m=100)
            if not gdf_nao.empty:
                fg_nao = folium.FeatureGroup(name=f'Municípios não afetados ({estado})', show=False)
                folium.GeoJson(
                    gdf_nao,
                    style_function=lambda f: {
                        'fillColor': '#e2e8f0',
                        'color': '#b8c2cc',
                        'weight': 1,
                        'fillOpacity': 0.35
                    }
                ).add_to(fg_nao)
                fg_nao.add_to(mapa)
        except Exception:
            pass
    if gdf_mun_filtrado is not None and not gdf_mun_filtrado.empty:
        # simplificação moderada para afetados
        gdf_mun_filtrado = _simplify_geoms(gdf_mun_filtrado, tol_m=60)
        fg_municipios = folium.FeatureGroup(name=f'Municípios ({voltagem} kV - {estado})', show=True)
        folium.GeoJson(
            gdf_mun_filtrado,
            style_function=lambda f: {
                'fillColor': cor_voltagem,
                'color': '#000000',
                'weight': 1,
                'fillOpacity': 0.25
            },
            tooltip=folium.GeoJsonTooltip(fields=['NM_MUN'], aliases=['Município:'], sticky=False)
        ).add_to(fg_municipios)
        fg_municipios.add_to(mapa)

    # Linhas (preferencial por linhas_recortadas; fallback faixa_serv.)
    gdf_lin = _read_lines_layer(voltagem, estado)
    if gdf_lin is not None and not gdf_lin.empty:
        # linhas com simplificação leve
        gdf_lin = _simplify_geoms(gdf_lin, tol_m=8)
        fg_linhas = folium.FeatureGroup(name=f'Linha de Transmissão ({voltagem} kV)', show=True)
        folium.GeoJson(
            gdf_lin,
            style_function=lambda f: {
                'color': cor_voltagem,
                'weight': 3,
                'opacity': 0.9
            },
            tooltip=folium.GeoJsonTooltip(fields=['Nome'], aliases=['Linha:'], sticky=False)
        ).add_to(fg_linhas)
        fg_linhas.add_to(mapa)

        # Buffer (faixa de servidão) calculado a partir das linhas
        gdf_buf = _make_buffer(gdf_lin, voltagem)
        if gdf_buf is not None and not gdf_buf.empty:
            # simplificação leve no buffer
            gdf_buf = _simplify_geoms(gdf_buf, tol_m=40)
            fg_buffer = folium.FeatureGroup(name=f'Faixa de Servidão ({voltagem} kV)', show=True)
            folium.GeoJson(
                gdf_buf,
                style_function=lambda f: {
                    'fillColor': cor_voltagem,
                    'color': cor_voltagem,
                    'weight': 1,
                    'fillOpacity': 0.15,
                    'opacity': 0.4
                }
            ).add_to(fg_buffer)
            fg_buffer.add_to(mapa)

    # Limite estadual (por UF via shapefile, com fallback)
    gdf_estado = _read_state_boundary_from_shp(estado)
    if (gdf_estado is None) or gdf_estado.empty:
        gdf_estado = _read_state_boundaries_from_base(estado)
    if gdf_estado is not None and not gdf_estado.empty:
        # simplificação mais forte no contorno estadual
        gdf_estado = _simplify_geoms(gdf_estado, tol_m=150)
        nome_fg = f"Limite Estadual ({estado})"
        fg_estados = folium.FeatureGroup(name=nome_fg, show=True)
        folium.GeoJson(
            gdf_estado,
            style_function=lambda f: {
                'color': '#222222',
                'weight': 2,
                'fillOpacity': 0
            },
            tooltip=folium.GeoJsonTooltip(fields=['UF'], aliases=['UF:'], sticky=False)
        ).add_to(fg_estados)
        fg_estados.add_to(mapa)


def gerar_mapa(voltagem, estado, gdf_municipios, gdf_linhas, gdf_buffer, df_filtrado):
    """Gera um mapa individual para uma combinação voltagem-estado"""
    
    titulo = f"Linha de Transmissão {voltagem} kV - {estado}"
    num_municipios = len(df_filtrado['NM_MUN'].unique())
    subtitulo = f"{num_municipios} municípios afetados"
    
    print(f"  🗺️  Gerando mapa: {titulo}")
    
    # Cria mapa base
    mapa = criar_mapa_base(titulo, subtitulo)
    
    # Adiciona camadas (dados são carregados on-demand por layer)
    adicionar_camadas(mapa, None, None, None, voltagem, estado)
    
    # Adiciona controle de camadas
    folium.LayerControl(position='topright', collapsed=False).add_to(mapa)
    
    # Adiciona plugin de tela cheia
    plugins.Fullscreen(
        position='topleft',
        title='Tela cheia',
        title_cancel='Sair da tela cheia'
    ).add_to(mapa)
    
    # Adiciona medidor de escala
    plugins.MeasureControl(position='bottomleft', primary_length_unit='kilometers').add_to(mapa)
    
    # Ajusta a extensão do mapa para cobrir os municípios/linhas do estado
    try:
        # prioriza bounds das linhas; fallback municípios
        gdf_lin = _read_lines_layer(voltagem, estado)
        bounds_gdf = gdf_lin
        if (bounds_gdf is None) or bounds_gdf.empty:
            bounds_gdf = _read_municipios_layer(voltagem, estado)
        if (bounds_gdf is not None) and (not bounds_gdf.empty):
            minx, miny, maxx, maxy = bounds_gdf.total_bounds
            mapa.fit_bounds([[miny, minx], [maxy, maxx]])
    except Exception:
        pass

    # Salva mapa
    nome_arquivo = f"mapa_{voltagem}kV_{estado}.html"
    caminho_saida = OUT_DIR / nome_arquivo
    mapa.save(str(caminho_saida))
    
    print(f"    ✓ Salvo: {caminho_saida}")
    return caminho_saida


def gerar_indice_html(mapas_gerados):
    """Gera página índice com links para todos os mapas"""
    
    # Agrupa por estado
    por_estado = {}
    for voltagem, estado, caminho in mapas_gerados:
        if estado not in por_estado:
            por_estado[estado] = []
        por_estado[estado].append((voltagem, caminho))
    
    # Ordena voltagens
    for estado in por_estado:
        por_estado[estado].sort(key=lambda x: int(x[0]))
    
    html = f"""
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Mapas - Linhas de Transmissão por Estado</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        header {{
            background: linear-gradient(135deg, #0f4c81 0%, #1a5fa0 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        header h1 {{
            font-size: 28px;
            margin-bottom: 8px;
        }}
        header p {{
            opacity: 0.9;
            font-size: 14px;
        }}
        .content {{
            padding: 30px;
        }}
        .estado-section {{
            margin-bottom: 30px;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            overflow: hidden;
        }}
        .estado-header {{
            background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
            padding: 15px 20px;
            border-bottom: 2px solid #cbd5e0;
        }}
        .estado-header h2 {{
            color: #2d3748;
            font-size: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .estado-nome {{
            background: #0f4c81;
            color: white;
            padding: 4px 12px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: bold;
        }}
        .mapas-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 15px;
            padding: 20px;
        }}
        .mapa-card {{
            background: white;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            transition: all 0.3s ease;
            cursor: pointer;
        }}
        .mapa-card:hover {{
            border-color: #0f4c81;
            box-shadow: 0 4px 12px rgba(15, 76, 129, 0.15);
            transform: translateY(-2px);
        }}
        .voltagem-badge {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 18px;
            font-weight: bold;
            color: white;
            margin-bottom: 12px;
        }}
        .v230 {{ background: #FFA500; }}
        .v500 {{ background: #FF0000; }}
        .v525 {{ background: #8B0000; }}
        .v600 {{ background: #4B0082; }}
        .v765 {{ background: #800080; }}
        .mapa-card a {{
            display: inline-block;
            margin-top: 8px;
            padding: 8px 20px;
            background: #0f4c81;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 500;
            transition: background 0.2s;
        }}
        .mapa-card a:hover {{
            background: #1a5fa0;
        }}
        .info-box {{
            background: #edf2f7;
            border-left: 4px solid #0f4c81;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 4px;
        }}
        .info-box p {{
            margin: 5px 0;
            color: #2d3748;
            line-height: 1.6;
        }}
        footer {{
            background: #f7fafc;
            padding: 20px;
            text-align: center;
            color: #718096;
            font-size: 13px;
            border-top: 1px solid #e2e8f0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🗺️ Mapas Interativos - Linhas de Transmissão</h1>
            <p>Foz do Iguaçu • Região Sul do Brasil</p>
        </header>
        
        <div class="content">
            <div class="info-box">
                <p><strong>📍 Sobre os mapas:</strong> Cada mapa mostra os municípios afetados por uma linha de transmissão específica em cada estado.</p>
                <p><strong>🎨 Interatividade:</strong> Clique nos municípios, linhas e faixa de servidão para ver detalhes. Use os controles no canto superior direito para alternar camadas.</p>
                <p><strong>🛡️ Faixa de Servidão:</strong> Área de segurança (buffer) ao redor das linhas de transmissão que identifica os municípios afetados.</p>
                <p><strong>📊 Total de mapas gerados:</strong> {len(mapas_gerados)}</p>
            </div>
"""
    
    # Gera seções por estado
    estados_ordem = ['PR', 'SC', 'RS']
    nomes_estados = {'PR': 'Paraná', 'SC': 'Santa Catarina', 'RS': 'Rio Grande do Sul'}
    
    for estado in estados_ordem:
        if estado in por_estado:
            html += f"""
            <div class="estado-section">
                <div class="estado-header">
                    <h2>
                        <span class="estado-nome">{estado}</span>
                        {nomes_estados[estado]}
                    </h2>
                </div>
                <div class="mapas-grid">
"""
            for voltagem, caminho in por_estado[estado]:
                nome_arquivo = caminho.name
                html += f"""
                    <div class="mapa-card">
                        <div class="voltagem-badge v{voltagem}">{voltagem} kV</div>
                        <p style="color: #4a5568; font-size: 14px; margin-bottom: 8px;">Linha de Transmissão</p>
                        <a href="{nome_arquivo}" target="_blank">Ver Mapa ➜</a>
                    </div>
"""
            html += """
                </div>
            </div>
"""
    
    html += """
        </div>
        
        <footer>
            <p><strong>Gerado automaticamente por:</strong> gerar_mapas_por_linha.py</p>
            <p>Projeto: Linhas de Transmissão de Foz do Iguaçu</p>
        </footer>
    </div>
</body>
</html>
"""
    
    # Salva índice
    indice_path = OUT_DIR / 'index.html'
    indice_path.write_text(html, encoding='utf-8')
    print(f"\n✓ Índice gerado: {indice_path}")
    return indice_path


def main():
    print("=" * 60)
    print("🗺️  GERADOR DE MAPAS POR LINHA DE TRANSMISSÃO")
    print("=" * 60)
    
    # Carrega dados (camadas disponíveis)
    df_espec, municipios_layers, linhas_layers, faixa_layers = carregar_dados()
    
    if df_espec.empty:
        print("❌ Erro: Nenhum dado encontrado em dados_consolidados.csv")
        return
    
    # Identifica combinações existentes
    combinacoes = identificar_combinacoes(df_espec)
    
    if combinacoes.empty:
        print("❌ Erro: Nenhuma combinação voltagem-estado encontrada")
        return
    
    # Gera mapas
    print(f"\n📍 Gerando {len(combinacoes)} mapas...\n")
    mapas_gerados = []
    
    for idx, row in combinacoes.iterrows():
        voltagem = row['Voltagem']
        estado = row['Estado']
        
        # Filtra dados para esta combinação
        df_filtrado = df_espec[
            (df_espec['Voltagem'] == voltagem) & 
            (df_espec['Estado'] == estado)
        ]
        
        try:
            caminho = gerar_mapa(voltagem, estado, None, None, None, df_filtrado)
            mapas_gerados.append((voltagem, estado, caminho))
        except Exception as e:
            print(f"    ⚠️  Erro ao gerar mapa {voltagem}kV-{estado}: {e}")
    
    # Gera página índice
    if mapas_gerados:
        gerar_indice_html(mapas_gerados)
        
        print("\n" + "=" * 60)
        print(f"✅ CONCLUÍDO! {len(mapas_gerados)} mapas gerados com sucesso")
        print(f"📂 Diretório de saída: {OUT_DIR}")
        print(f"🌐 Abra o arquivo index.html para navegar pelos mapas")
        print("=" * 60)
    else:
        print("\n❌ Nenhum mapa foi gerado com sucesso")


if __name__ == '__main__':
    main()
