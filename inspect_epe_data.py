"""Script temporário para inspecionar dados EPE e comparar com dados atuais do RS"""
import geopandas as gpd
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parent

# Carregar shapefile EPE
epe_shp = BASE_DIR / '_ags_Download Dados Webmap EPE' / 'zipfolder' / 'Linhas_de_Transmissão_-_Base_Existente.shp'
gdf_epe = gpd.read_file(epe_shp)

print("="*60)
print("DADOS EPE - Linhas de Transmissão Base Existente")
print("="*60)
print(f"Total de features: {len(gdf_epe)}")
print(f"\nColunas: {list(gdf_epe.columns)}")
print(f"\nPrimeiras 5 linhas:")
print(gdf_epe.head())

# Verificar voltagens únicas
if 'Tensao' in gdf_epe.columns:
    print(f"\n\nVoltagens únicas: {sorted(gdf_epe['Tensao'].dropna().unique())}")
    print(f"\nDistribuição por voltagem:")
    print(gdf_epe['Tensao'].value_counts().sort_index())

# Verificar nomes
if 'Nome' in gdf_epe.columns:
    print(f"\n\nExemplos de nomes de linhas:")
    print(gdf_epe['Nome'].dropna().unique()[:10])

# Carregar dados consolidados atuais
csv_atual = BASE_DIR / 'dados_consolidados.csv'
df_atual = pd.read_csv(csv_atual)

print("\n" + "="*60)
print("DADOS ATUAIS - RS")
print("="*60)
df_rs = df_atual[df_atual['Estado'] == 'RS']
print(f"Total municípios RS: {len(df_rs)}")
print(f"\nDistribuição por voltagem:")
print(df_rs.groupby(['Voltagem', 'Tipo']).size())

print("\n" + "="*60)
print("ANÁLISE")
print("="*60)
print("Por favor, verifique:")
print("1. Quais voltagens aparecem no RS nos dados EPE?")
print("2. Nos dados atuais, temos principalmente BASE (linhas genéricas)")
print("3. Identifique se há linhas específicas 230kV ou 525kV no RS que não foram capturadas")
