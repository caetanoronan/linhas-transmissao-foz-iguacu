import geopandas as gpd
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

print("Carregando dados das linhas de transmissão...")

# Carregar as linhas de transmissão do GeoPackage
try:
    linhas = gpd.read_file('Linha_trans_RS.gpkg')
    print(f"✓ Linhas carregadas: {len(linhas)} registros")
    print(f"  CRS: {linhas.crs}")
    print(f"  Colunas: {list(linhas.columns)}")
except Exception as e:
    print(f"✗ Erro ao carregar Linha_trans_RS.gpkg: {e}")
    linhas = None

# Carregar os municípios do RS
print("\nCarregando municípios do RS...")
try:
    municipios = gpd.read_file('Rs.gpkg')
    print(f"✓ Municípios carregados: {len(municipios)} registros")
    print(f"  CRS: {municipios.crs}")
    print(f"  Colunas: {list(municipios.columns)}")
except Exception as e:
    print(f"✗ Erro ao carregar Rs.gpkg: {e}")
    municipios = None

if linhas is not None and municipios is not None:
    # Garantir que ambos estejam no mesmo CRS
    if linhas.crs != municipios.crs:
        print(f"\nConvertendo CRS das linhas de {linhas.crs} para {municipios.crs}...")
        linhas = linhas.to_crs(municipios.crs)
    
    print("\n" + "="*70)
    print("ANÁLISE DE MUNICÍPIOS AFETADOS PELAS LINHAS DE TRANSMISSÃO")
    print("="*70)
    
    # Identificar municípios que intersectam com as linhas
    print("\nIdentificando municípios afetados...")
    municipios_afetados = set()
    detalhes = []
    
    for idx, linha in linhas.iterrows():
        # Identificar qual nome de coluna usar para a linha
        nome_linha = None
        for col in ['linha_transmissao', 'nome', 'name', 'NOME']:
            if col in linha.index and pd.notna(linha[col]):
                nome_linha = linha[col]
                break
        
        if nome_linha is None:
            nome_linha = f"Linha {idx+1}"
        
        # Encontrar municípios que intersectam com esta linha
        for idx_mun, municipio in municipios.iterrows():
            if linha.geometry.intersects(municipio.geometry):
                # Identificar nome do município
                nome_mun = None
                for col in ['NM_MUN', 'nome', 'NOME', 'municipio', 'name']:
                    if col in municipio.index and pd.notna(municipio[col]):
                        nome_mun = municipio[col]
                        break
                
                if nome_mun:
                    municipios_afetados.add(nome_mun)
                    detalhes.append({
                        'Linha': nome_linha,
                        'Município': nome_mun
                    })
    
    print(f"\n✓ Análise concluída!")
    print(f"\nTOTAL DE MUNICÍPIOS AFETADOS: {len(municipios_afetados)}")
    print("\nLista de municípios:")
    print("-" * 70)
    for municipio in sorted(municipios_afetados):
        print(f"  • {municipio}")
    
    # Criar DataFrame com detalhes
    df_detalhes = pd.DataFrame(detalhes)
    
    # Salvar resultados
    print("\nSalvando resultados...")
    
    # Lista de municípios
    with open('municipios_afetados.txt', 'w', encoding='utf-8') as f:
        f.write("MUNICÍPIOS DO RS AFETADOS POR LINHAS DE TRANSMISSÃO\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Total: {len(municipios_afetados)} municípios\n\n")
        for municipio in sorted(municipios_afetados):
            f.write(f"  • {municipio}\n")
    
    # Detalhes em CSV
    df_detalhes.to_csv('linhas_por_municipio.csv', index=False, encoding='utf-8-sig')
    
    # Resumo por município
    resumo_municipio = df_detalhes.groupby('Município').size().reset_index(name='Quantidade_Linhas')
    resumo_municipio = resumo_municipio.sort_values('Quantidade_Linhas', ascending=False)
    resumo_municipio.to_csv('resumo_por_municipio.csv', index=False, encoding='utf-8-sig')
    
    print("✓ Arquivos salvos:")
    print("  - municipios_afetados.txt")
    print("  - linhas_por_municipio.csv (detalhes de cada linha por município)")
    print("  - resumo_por_municipio.csv (quantidade de linhas por município)")
    
    # Mostrar top 10 municípios com mais linhas
    print("\n" + "="*70)
    print("TOP 10 MUNICÍPIOS COM MAIS LINHAS DE TRANSMISSÃO")
    print("="*70)
    print(resumo_municipio.head(10).to_string(index=False))

else:
    print("\n✗ Não foi possível realizar a análise. Verifique os arquivos.")
