"""
Análise Consolidada - Municípios Afetados por Linhas de Transmissão
Origem: Usina de Foz do Iguaçu - Região Sul do Brasil
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import os

# Configurações de estilo
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Diretório base
base_dir = Path(__file__).parent
per_layer_dir = base_dir / 'per_layer'

# Dicionário para armazenar todos os dados
dados_consolidados = []

# Ler todos os arquivos CSV da pasta per_layer
print("=" * 80)
print("ANÁLISE CONSOLIDADA - LINHAS DE TRANSMISSÃO FOZ DO IGUAÇU")
print("=" * 80)
print()

# Listar todos os arquivos CSV
csv_files = list(per_layer_dir.glob('*.csv'))
print(f"📁 Arquivos encontrados: {len(csv_files)}\n")

# Processar cada arquivo
for csv_file in csv_files:
    filename = csv_file.stem
    
    # Extrair informações do nome do arquivo
    if 'base' in filename.lower():
        # Arquivo base (todas as linhas)
        estado = filename.split('_')[-1]
        voltagem = 'BASE'
        tipo = 'base'
    else:
        # Arquivo específico de voltagem
        parts = filename.split('_')
        voltagem = parts[3]  # ex: 230, 525, etc
        estado = parts[4].replace('.csv', '')  # PR, RS, SC
        tipo = 'especifica'
    
    # Ler o CSV
    df = pd.read_csv(csv_file)
    # Assegurar nomes limpos e únicos por arquivo
    if 'NM_MUN' in df.columns:
        df['NM_MUN'] = df['NM_MUN'].astype(str).str.strip()
        df = df.drop_duplicates(subset=['NM_MUN'])
    
    # Adicionar informações extras
    df['Voltagem'] = voltagem
    df['Estado'] = estado
    df['Tipo'] = tipo
    df['Linha'] = f"{voltagem} kV" if voltagem != 'BASE' else 'BASE'
    
    dados_consolidados.append(df)
    
    print(f"✓ {filename}")
    print(f"  └─ {voltagem} kV - {estado} - {len(df)} municípios")

# Consolidar tudo em um único DataFrame
df_completo = pd.concat(dados_consolidados, ignore_index=True)
df_completo['NM_MUN'] = df_completo['NM_MUN'].astype(str).str.strip()
df_completo['Estado'] = df_completo['Estado'].astype(str).str.strip().str.upper()
df_completo['Voltagem'] = df_completo['Voltagem'].astype(str).str.strip()
df_completo = df_completo.drop_duplicates()

print("\n" + "=" * 80)
print("RESUMO GERAL")
print("=" * 80)

# Estatísticas gerais
total_municipios_unicos = df_completo['NM_MUN'].nunique()
total_registros = len(df_completo)

print(f"\n📊 Total de registros: {total_registros}")
print(f"🏘️  Municípios únicos afetados: {total_municipios_unicos}")
print(f"⚡ Linhas de transmissão diferentes: {df_completo['Linha'].nunique()}")
print(f"🗺️  Estados cobertos: {', '.join(sorted(df_completo['Estado'].unique()))}")

# Análise por voltagem
print("\n" + "-" * 80)
print("MUNICÍPIOS POR VOLTAGEM")
print("-" * 80)

df_especificas = df_completo[df_completo['Tipo'] == 'especifica']
municipios_por_voltagem = df_especificas.groupby('Voltagem')['NM_MUN'].nunique().sort_values(ascending=False)

for voltagem, count in municipios_por_voltagem.items():
    print(f"  {voltagem} kV: {count} municípios")

# Análise por estado
print("\n" + "-" * 80)
print("MUNICÍPIOS POR ESTADO")
print("-" * 80)

municipios_por_estado = df_completo.groupby('Estado')['NM_MUN'].nunique().sort_values(ascending=False)

for estado, count in municipios_por_estado.items():
    print(f"  {estado}: {count} municípios")

# Municípios com múltiplas linhas
print("\n" + "-" * 80)
print("MUNICÍPIOS ATRAVESSADOS POR MÚLTIPLAS LINHAS")
print("-" * 80)

municipios_multiplas = df_especificas.groupby('NM_MUN')['Linha'].nunique().sort_values(ascending=False)
municipios_com_multiplas = municipios_multiplas[municipios_multiplas > 1]

print(f"\n🔄 {len(municipios_com_multiplas)} municípios são atravessados por mais de uma linha\n")
print("Top 10 municípios com mais linhas:")
for municipio, num_linhas in municipios_com_multiplas.head(10).items():
    linhas = df_especificas[df_especificas['NM_MUN'] == municipio]['Linha'].unique()
    print(f"  {municipio}: {int(num_linhas)} linhas - {', '.join(sorted(linhas))}")

# ============================================================================
# VISUALIZAÇÕES
# ============================================================================

print("\n" + "=" * 80)
print("GERANDO VISUALIZAÇÕES...")
print("=" * 80)

# Criar figura com múltiplos subplots
fig = plt.figure(figsize=(16, 12))

# 1. Municípios por Voltagem
ax1 = plt.subplot(2, 2, 1)
municipios_por_voltagem.plot(kind='barh', ax=ax1, color='steelblue')
ax1.set_xlabel('Número de Municípios')
ax1.set_ylabel('Voltagem (kV)')
ax1.set_title('Municípios Afetados por Voltagem da Linha', fontsize=12, fontweight='bold')
ax1.grid(axis='x', alpha=0.3)

# Adicionar valores nas barras
for i, v in enumerate(municipios_por_voltagem.values):
    ax1.text(v + 0.5, i, str(v), va='center')

# 2. Municípios por Estado
ax2 = plt.subplot(2, 2, 2)
cores_estados = {'PR': '#1f77b4', 'SC': '#ff7f0e', 'RS': '#2ca02c'}
colors = [cores_estados.get(estado, 'gray') for estado in municipios_por_estado.index]
municipios_por_estado.plot(kind='bar', ax=ax2, color=colors)
ax2.set_xlabel('Estado')
ax2.set_ylabel('Número de Municípios')
ax2.set_title('Municípios Afetados por Estado', fontsize=12, fontweight='bold')
ax2.tick_params(axis='x', rotation=0)
ax2.grid(axis='y', alpha=0.3)

# Adicionar valores nas barras
for i, v in enumerate(municipios_por_estado.values):
    ax2.text(i, v + 1, str(v), ha='center', va='bottom')

# 3. Distribuição de linhas por município
ax3 = plt.subplot(2, 2, 3)
dist_linhas = municipios_multiplas.value_counts().sort_index()
dist_linhas.plot(kind='bar', ax=ax3, color='coral')
ax3.set_xlabel('Número de Linhas')
ax3.set_ylabel('Quantidade de Municípios')
ax3.set_title('Distribuição: Quantas Linhas Atravessam Cada Município', fontsize=12, fontweight='bold')
ax3.tick_params(axis='x', rotation=0)
ax3.grid(axis='y', alpha=0.3)

# Adicionar valores nas barras
for i, v in enumerate(dist_linhas.values):
    ax3.text(i, v + 0.5, str(v), ha='center', va='bottom')

# 4. Matriz de linhas por estado
ax4 = plt.subplot(2, 2, 4)
matriz_estado_voltagem = df_especificas.groupby(['Estado', 'Voltagem'])['NM_MUN'].nunique().unstack(fill_value=0)
sns.heatmap(matriz_estado_voltagem, annot=True, fmt='d', cmap='YlOrRd', ax=ax4, cbar_kws={'label': 'Municípios'})
ax4.set_xlabel('Voltagem (kV)')
ax4.set_ylabel('Estado')
ax4.set_title('Matriz: Municípios por Estado e Voltagem', fontsize=12, fontweight='bold')

plt.suptitle('Análise Consolidada - Linhas de Transmissão de Foz do Iguaçu', 
             fontsize=16, fontweight='bold', y=0.995)

plt.tight_layout()

# Salvar figura
output_path = base_dir / 'analise_consolidada_visualizacao.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"\n✓ Visualização salva em: {output_path}")

# Salvar DataFrame consolidado
csv_output_path = base_dir / 'dados_consolidados.csv'
df_completo.to_csv(csv_output_path, index=False, encoding='utf-8-sig')
print(f"✓ Dados consolidados salvos em: {csv_output_path}")

# Salvar relatório de municípios com múltiplas linhas
if len(municipios_com_multiplas) > 0:
    relatorio_multiplas = []
    for municipio in municipios_com_multiplas.index:
        linhas = df_especificas[df_especificas['NM_MUN'] == municipio]
        estado = linhas['Estado'].iloc[0]
        voltagens = ', '.join(sorted(linhas['Voltagem'].unique()))
        num_linhas = len(linhas['Linha'].unique())
        
        relatorio_multiplas.append({
            'Municipio': municipio,
            'Estado': estado,
            'Num_Linhas': num_linhas,
            'Voltagens': voltagens
        })
    
    df_multiplas = pd.DataFrame(relatorio_multiplas).sort_values('Num_Linhas', ascending=False)
    multiplas_output_path = base_dir / 'municipios_multiplas_linhas.csv'
    df_multiplas.to_csv(multiplas_output_path, index=False, encoding='utf-8-sig')
    print(f"✓ Relatório de múltiplas linhas salvo em: {multiplas_output_path}")

print("\n" + "=" * 80)
print("✅ ANÁLISE CONCLUÍDA COM SUCESSO!")
print("=" * 80)

plt.show()
