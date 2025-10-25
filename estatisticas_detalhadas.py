"""
Estatísticas Detalhadas - Linhas de Transmissão
Explicação do gráfico "Distribuição de linhas por município"
"""

import pandas as pd
from pathlib import Path

# Diretório base
base_dir = Path(__file__).parent

# Carregar dados
df_consolidado = pd.read_csv(base_dir / 'dados_consolidados.csv')
df_multiplas = pd.read_csv(base_dir / 'municipios_multiplas_linhas.csv')

print("=" * 80)
print("EXPLICAÇÃO: DISTRIBUIÇÃO DE LINHAS POR MUNICÍPIO")
print("=" * 80)
print()
print("Este gráfico mostra QUANTOS municípios têm 1 linha, 2 linhas, 3 linhas, etc.")
print()
print("Exemplo de interpretação:")
print("  - Se há uma barra em '1' com valor 50, significa que 50 municípios")
print("    são atravessados por apenas 1 linha de transmissão")
print("  - Se há uma barra em '3' com valor 10, significa que 10 municípios")
print("    são atravessados por 3 linhas diferentes")
print()

# Contar quantas linhas cada município tem
df_especificas = df_consolidado[df_consolidado['Tipo'] == 'especifica']
municipios_linhas = df_especificas.groupby('NM_MUN')['Linha'].nunique()

distribuicao = municipios_linhas.value_counts().sort_index()

print("-" * 80)
print("DISTRIBUIÇÃO COMPLETA:")
print("-" * 80)
for num_linhas, qtd_municipios in distribuicao.items():
    print(f"  {qtd_municipios} municípios têm {int(num_linhas)} linha(s) de transmissão")

print()
print("=" * 80)
print("ESTATÍSTICAS DETALHADAS POR ESTADO")
print("=" * 80)

for estado in sorted(df_especificas['Estado'].unique()):
    print()
    print(f"{'=' * 80}")
    print(f"ESTADO: {estado}")
    print(f"{'=' * 80}")
    
    df_estado = df_especificas[df_especificas['Estado'] == estado]
    
    # Total de municípios
    total_municipios = df_estado['NM_MUN'].nunique()
    print(f"\n📍 Total de municípios afetados: {total_municipios}")
    
    # Por voltagem
    print(f"\n⚡ Municípios por voltagem:")
    voltagem_estado = df_estado.groupby('Voltagem')['NM_MUN'].nunique().sort_values(ascending=False)
    for voltagem, count in voltagem_estado.items():
        print(f"   • {voltagem} kV: {count} municípios")
    
    # Municípios com múltiplas linhas neste estado
    df_multiplas_estado = df_multiplas[df_multiplas['Estado'] == estado]
    if len(df_multiplas_estado) > 0:
        print(f"\n🔄 Municípios com múltiplas linhas: {len(df_multiplas_estado)}")
        print(f"\n   Top 5 municípios com mais linhas em {estado}:")
        for idx, row in df_multiplas_estado.head(5).iterrows():
            print(f"   {row['Num_Linhas']}x - {row['Municipio']}: {row['Voltagens']} kV")
    
    # Municípios únicos (apenas 1 linha)
    municipios_1_linha = df_estado.groupby('NM_MUN')['Linha'].nunique()
    municipios_1_linha = municipios_1_linha[municipios_1_linha == 1]
    print(f"\n   Municípios com apenas 1 linha: {len(municipios_1_linha)}")

print()
print("=" * 80)
print("ESTATÍSTICAS DETALHADAS POR VOLTAGEM")
print("=" * 80)

for voltagem in sorted(df_especificas['Voltagem'].unique(), key=lambda x: int(x)):
    print()
    print(f"{'=' * 80}")
    print(f"VOLTAGEM: {voltagem} kV")
    print(f"{'=' * 80}")
    
    df_voltagem = df_especificas[df_especificas['Voltagem'] == voltagem]
    
    # Total de municípios
    total_municipios = df_voltagem['NM_MUN'].nunique()
    print(f"\n⚡ Total de municípios afetados: {total_municipios}")
    
    # Por estado
    print(f"\n🗺️  Distribuição por estado:")
    estado_voltagem = df_voltagem.groupby('Estado')['NM_MUN'].nunique().sort_values(ascending=False)
    for estado, count in estado_voltagem.items():
        print(f"   • {estado}: {count} municípios")
    
    # Quantos municípios têm SOMENTE esta voltagem
    todos_municipios_voltagem = df_voltagem['NM_MUN'].unique()
    municipios_exclusivos = []
    
    for municipio in todos_municipios_voltagem:
        linhas_municipio = df_especificas[df_especificas['NM_MUN'] == municipio]['Voltagem'].unique()
        if len(linhas_municipio) == 1:
            municipios_exclusivos.append(municipio)
    
    print(f"\n   Municípios afetados APENAS por {voltagem} kV: {len(municipios_exclusivos)}")
    
    # Alguns exemplos
    if len(municipios_exclusivos) > 0:
        print(f"   Exemplos: {', '.join(municipios_exclusivos[:5])}")

print()
print("=" * 80)
print("RESUMO GERAL - CRUZAMENTO DE INFORMAÇÕES")
print("=" * 80)

print("\n📊 MUNICÍPIOS MAIS IMPACTADOS (Top 10):")
print("   (Municípios atravessados por mais linhas diferentes)\n")
for idx, row in df_multiplas.head(10).iterrows():
    print(f"   {row['Num_Linhas']}x - {row['Municipio']} ({row['Estado']})")
    print(f"        Voltagens: {row['Voltagens']} kV")

print("\n" + "=" * 80)

# Análise especial: Foz do Iguaçu
print("\n🔍 DESTAQUE: FOZ DO IGUAÇU")
print("-" * 80)
foz = df_especificas[df_especificas['NM_MUN'] == 'Foz do Iguaçu']
if len(foz) > 0:
    print(f"Foz do Iguaçu é atravessada por {len(foz)} linhas diferentes:")
    for idx, row in foz.iterrows():
        print(f"  • {row['Linha']}")
    print("\nIsso faz sentido, pois Foz do Iguaçu é o ponto de origem!")

print("\n" + "=" * 80)
print("✅ ANÁLISE COMPLETA!")
print("=" * 80)
