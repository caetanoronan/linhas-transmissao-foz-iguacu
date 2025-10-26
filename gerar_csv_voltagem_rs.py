"""
Script para gerar CSV de municípios RS com coluna de Voltagem
Cruza RS/Municipios_afetas_linhas.csv com linhas do RS/Linha_trans_RS.gpkg
e detecta quais voltagens afetam cada município via spatial join.
"""
from pathlib import Path
import pandas as pd
import geopandas as gpd
import fiona

BASE_DIR = Path(__file__).parent
RS_DIR = BASE_DIR / 'RS'
RS_MUNS_CSV = RS_DIR / 'Municipios_afetas_linhas.csv'
RS_MUNS_GPKG = RS_DIR / 'municipios_afetados_linhas_transmissao.gpkg'
RS_LINHAS_GPKG = RS_DIR / 'Linha_trans_RS.gpkg'
OUTPUT_CSV = RS_DIR / 'Municipios_afetas_linhas_por_voltagem.csv'

def main():
    print("=" * 60)
    print("GERADOR DE CSV COM VOLTAGEM POR MUNICÍPIO - RS")
    print("=" * 60)
    
    # Ler CSV original
    print("\n📂 Lendo CSV original...")
    df_muns = pd.read_csv(RS_MUNS_CSV)
    print(f"  ✓ {len(df_muns)} municípios no CSV")
    
    # Ler municípios do GPKG
    print("\n📂 Lendo municípios do GPKG...")
    try:
        layers = fiona.listlayers(str(RS_MUNS_GPKG))
    except Exception:
        layers = []
    
    gdf_muns = None
    for lyr in layers:
        try:
            tmp = gpd.read_file(RS_MUNS_GPKG, layer=lyr)
            if not tmp.empty and tmp.geom_type.astype(str).str.contains('Polygon', case=False).any():
                gdf_muns = tmp
                break
        except Exception:
            continue
    
    if gdf_muns is None:
        gdf_muns = gpd.read_file(RS_MUNS_GPKG)
    
    # Normalizar CRS
    if gdf_muns.crs and gdf_muns.crs.to_epsg() != 4326:
        gdf_muns = gdf_muns.to_crs(epsg=4326)
    
    # Padronizar nome da coluna
    if 'NM_MUN' not in gdf_muns.columns:
        for c in ['NOME_MUNI', 'MUNIC', 'NM_MUNIC', 'NM_MUNICIPIO']:
            if c in gdf_muns.columns:
                gdf_muns = gdf_muns.rename(columns={c: 'NM_MUN'})
                break
    
    print(f"  ✓ {len(gdf_muns)} municípios no GPKG")
    
    # Ler linhas do RS
    print("\n📂 Lendo linhas de transmissão...")
    try:
        layers = fiona.listlayers(str(RS_LINHAS_GPKG))
    except Exception:
        layers = []
    
    layer_to_use = None
    for lyr in layers:
        try:
            tmp = gpd.read_file(RS_LINHAS_GPKG, layer=lyr)
            if not tmp.empty and tmp.geom_type.astype(str).str.contains('Line', case=False).any():
                layer_to_use = lyr
                break
        except Exception:
            continue
    
    if layer_to_use is None and layers:
        layer_to_use = layers[0]
    
    gdf_linhas = gpd.read_file(RS_LINHAS_GPKG, layer=layer_to_use)
    
    if gdf_linhas.crs and gdf_linhas.crs.to_epsg() != 4326:
        gdf_linhas = gdf_linhas.to_crs(epsg=4326)
    
    print(f"  ✓ {len(gdf_linhas)} linhas carregadas")
    
    # Detectar coluna de tensão
    tensao_col = None
    for c in ['Tensao', 'tensao', 'Tensao_kV', 'kV', 'KV']:
        if c in gdf_linhas.columns:
            tensao_col = c
            break
    
    if tensao_col is None:
        print("  ⚠️  Nenhuma coluna de tensão encontrada nas linhas")
        print("  → Usando todas as linhas sem filtro por voltagem")
        gdf_linhas['Voltagem'] = 'TODAS'
    else:
        print(f"  ✓ Coluna de tensão: {tensao_col}")
        gdf_linhas['Voltagem'] = gdf_linhas[tensao_col].astype(str).str.replace('.0', '', regex=False)
    
    # Criar buffer nas linhas para melhor detecção
    print("\n🔧 Criando buffer nas linhas...")
    gdf_linhas_buf = gdf_linhas.copy()
    try:
        gdf_linhas_buf = gdf_linhas_buf.to_crs(epsg=3857)
        gdf_linhas_buf['geometry'] = gdf_linhas_buf.geometry.buffer(100)  # 100m
        gdf_linhas_buf = gdf_linhas_buf.to_crs(epsg=4326)
    except Exception:
        pass
    
    # Spatial join para detectar voltagens por município
    print("\n🔍 Detectando voltagens por município (spatial join)...")
    join_result = gpd.sjoin(gdf_muns, gdf_linhas_buf[['Voltagem', 'geometry']], how='inner', predicate='intersects')
    
    # Agrupar por município e coletar todas as voltagens
    mun_voltagens = {}
    for idx, row in join_result.iterrows():
        mun = row['NM_MUN']
        volt = row['Voltagem']
        if mun not in mun_voltagens:
            mun_voltagens[mun] = set()
        mun_voltagens[mun].add(volt)
    
    print(f"  ✓ {len(mun_voltagens)} municípios com voltagens detectadas")
    
    # Criar registros expandidos (um registro por município-voltagem)
    registros = []
    for _, row in df_muns.iterrows():
        mun = row['NM_MUN']
        # Normalizar nome para busca
        mun_upper = str(mun).upper() if pd.notna(mun) else ''
        
        # Buscar voltagens detectadas
        voltagens_detectadas = None
        for m, volts in mun_voltagens.items():
            if str(m).upper() == mun_upper:
                voltagens_detectadas = volts
                break
        
        if voltagens_detectadas:
            # Criar um registro para cada voltagem
            for volt in sorted(voltagens_detectadas):
                registro = row.to_dict()
                registro['Voltagem'] = volt
                registros.append(registro)
        else:
            # Município sem voltagem detectada (mantém sem voltagem específica)
            registro = row.to_dict()
            registro['Voltagem'] = 'NÃO_DETECTADA'
            registros.append(registro)
    
    # Criar DataFrame final
    df_final = pd.DataFrame(registros)
    
    # Salvar CSV
    df_final.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
    
    print("\n" + "=" * 60)
    print(f"✅ CSV gerado com sucesso!")
    print(f"📄 Arquivo: {OUTPUT_CSV}")
    print(f"📊 Total de registros: {len(df_final)}")
    print(f"📊 Municípios únicos: {df_final['NM_MUN'].nunique()}")
    print("\nDistribuição por voltagem:")
    print(df_final['Voltagem'].value_counts().to_string())
    print("=" * 60)

if __name__ == '__main__':
    main()
