import geopandas as gpd
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

print("Carregando dados...")

# Carregar as linhas de transmissão
linhas = gpd.read_file('Linha_trans_RS.gpkg')
print(f"✓ Linhas carregadas: {len(linhas)} registros")

# Carregar os municípios do RS
municipios = gpd.read_file('Rs.gpkg')
print(f"✓ Municípios carregados: {len(municipios)} registros")

# Garantir que ambos estejam no mesmo CRS
if linhas.crs != municipios.crs:
    print(f"Convertendo CRS das linhas para {municipios.crs}...")
    linhas = linhas.to_crs(municipios.crs)

print("\nIdentificando municípios afetados...")

# Criar conjunto com códigos dos municípios afetados
municipios_afetados_codigos = set()
municipios_afetados_nomes = set()

for idx, linha in linhas.iterrows():
    for idx_mun, municipio in municipios.iterrows():
        if linha.geometry.intersects(municipio.geometry):
            municipios_afetados_codigos.add(municipio['CD_MUN'])
            municipios_afetados_nomes.add(municipio['NM_MUN'])

print(f"✓ Identificados {len(municipios_afetados_codigos)} municípios afetados")

# Filtrar apenas os municípios afetados
municipios_filtrados = municipios[municipios['CD_MUN'].isin(municipios_afetados_codigos)].copy()

# Adicionar informação sobre quantidade de linhas por município
print("\nCalculando quantidade de linhas por município...")
linhas_por_municipio = {}

for idx, municipio in municipios_filtrados.iterrows():
    cd_mun = municipio['CD_MUN']
    nm_mun = municipio['NM_MUN']
    count = 0
    
    for idx_linha, linha in linhas.iterrows():
        if linha.geometry.intersects(municipio.geometry):
            count += 1
    
    linhas_por_municipio[cd_mun] = count

# Adicionar coluna com quantidade de linhas
municipios_filtrados['N_LINHAS'] = municipios_filtrados['CD_MUN'].map(linhas_por_municipio)

print(f"\n{'='*70}")
print(f"EXPORTANDO SHAPEFILE")
print(f"{'='*70}")

# Exportar para shapefile
output_shp = 'municipios_afetados_linhas_transmissao.shp'
municipios_filtrados.to_file(output_shp, driver='ESRI Shapefile', encoding='utf-8')

print(f"\n✓ Shapefile criado com sucesso!")
print(f"  Arquivo: {output_shp}")
print(f"  Municípios: {len(municipios_filtrados)}")
print(f"  CRS: {municipios_filtrados.crs}")
print(f"\nColunas incluídas:")
for col in municipios_filtrados.columns:
    if col != 'geometry':
        print(f"  - {col}")

# Também salvar em GeoPackage (formato mais moderno)
output_gpkg = 'municipios_afetados_linhas_transmissao.gpkg'
municipios_filtrados.to_file(output_gpkg, driver='GPKG')
print(f"\n✓ GeoPackage também criado: {output_gpkg}")

# Estatísticas
print(f"\n{'='*70}")
print(f"ESTATÍSTICAS")
print(f"{'='*70}")
print(f"Total de municípios afetados: {len(municipios_filtrados)}")
print(f"Município com mais linhas: {municipios_filtrados.loc[municipios_filtrados['N_LINHAS'].idxmax(), 'NM_MUN']} ({municipios_filtrados['N_LINHAS'].max()} linhas)")
print(f"Município com menos linhas: {municipios_filtrados.loc[municipios_filtrados['N_LINHAS'].idxmin(), 'NM_MUN']} ({municipios_filtrados['N_LINHAS'].min()} linhas)")
print(f"Média de linhas por município: {municipios_filtrados['N_LINHAS'].mean():.2f}")

print(f"\n✓ Processo concluído!")
