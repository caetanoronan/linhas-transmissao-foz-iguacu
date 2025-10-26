# Linhas de Transmissão – Foz do Iguaçu (Região Sul)

[![Validate Root Redirect](https://github.com/caetanoronan/linhas-transmissao-foz-iguacu/actions/workflows/validate-root-redirect.yml/badge.svg?branch=main)](https://github.com/caetanoronan/linhas-transmissao-foz-iguacu/actions/workflows/validate-root-redirect.yml)

**Autor:** Ronan Armando Caetano

Análise geoespacial completa e dashboards interativos dos municípios afetados por linhas de transmissão de energia elétrica na região Sul do Brasil (Paraná, Santa Catarina e Rio Grande do Sul).

## 🌐 Acesso Online

**🗺️ Mapas Interativos:** [https://caetanoronan.github.io/linhas-transmissao-foz-iguacu/outputs/mapas/](https://caetanoronan.github.io/linhas-transmissao-foz-iguacu/outputs/mapas/)

**📊 Dashboard Completo:** [https://caetanoronan.github.io/linhas-transmissao-foz-iguacu/outputs/dashboard.html](https://caetanoronan.github.io/linhas-transmissao-foz-iguacu/outputs/dashboard.html)

Links diretos para os mapas do RS por voltagem:
- RS – 230 kV: https://caetanoronan.github.io/linhas-transmissao-foz-iguacu/outputs/mapas/mapa_230kV_RS.html
- RS – 525 kV: https://caetanoronan.github.io/linhas-transmissao-foz-iguacu/outputs/mapas/mapa_525kV_RS.html

## 📊 Sobre o Projeto

Este projeto analisa **600+ municípios** afetados por linhas de transmissão de energia elétrica de diferentes voltagens:
- 230 kV
- 500 kV
- 525 kV
- 600 kV
- 765 kV

### Funcionalidades
- ✅ **9 mapas interativos** individuais por voltagem e estado (Folium)
- ✅ Visualizações interativas com Plotly
- ✅ Filtros por estado, voltagem e município
- ✅ Camadas sobrepostas: municípios afetados, linhas, faixa de servidão, limites estaduais
- ✅ Links diretos para Google Maps
- ✅ Download de dados em CSV
- ✅ Tema claro/escuro
- ✅ Análise de municípios com múltiplas linhas

## 📁 Estrutura do Projeto

```
📁 Afetados_ln_trans/
├── � outputs/
│   ├── 📁 mapas/
│   │   ├── �📄 index.html                  # Landing page dos mapas interativos
│   │   ├── 📄 mapa_230kV_PR.html          # Mapa interativo 230kV PR
│   │   ├── 📄 mapa_525kV_SC.html          # Mapa interativo 525kV SC
│   │   └── ... (9 mapas no total)
│   ├── 📄 dashboard.html                  # Dashboard Plotly completo
│   └── 📄 municipios_afetados_completo.csv
├── 📄 gerar_mapas_por_linha.py            # Gera mapas interativos Folium
├── 📄 municipios_afetados_completo.csv    # Dados completos para download
├── 📄 gerar_relatorio_html.py             # Script para gerar dashboard HTML
├── 📄 analise_consolidada.py              # Consolida dados dos CSVs
├── 📄 dashboard.py                        # Dashboard Streamlit (local)
├── 📄 estatisticas_detalhadas.py          # Análises detalhadas no console
├── 📄 dados_consolidados.csv              # Dados consolidados
├── 📄 municipios_multiplas_linhas.csv     # Municípios com múltiplas linhas
├── 📁 per_layer/                          # CSVs por voltagem e estado
├── 📁 Shapefile_Estados/                  # Shapefiles PR, SC, RS
├── 📁 per_layer/                          # CSVs por voltagem e estado
├── 📄 *.gpkg                              # GeoPackages (municípios, linhas, faixa de servidão)
└── 📁 .venv/                              # Ambiente virtual Python
```

## 🚀 Deploy no GitHub Pages

### Publicação Inicial

1. **Criar repositório no GitHub:**
   - Nome sugerido: `linhas-transmissao-foz-iguacu`
   - Deixar como **PÚBLICO**

2. **Enviar para o GitHub:**
```powershell
git init
git add .
git commit -m "Adiciona dashboard de linhas de transmissão"
git branch -M main
git remote add origin https://github.com/caetanoronan/linhas-transmissao-foz-iguacu.git
git push -u origin main
```

3. **Configurar GitHub Pages:**
   - Vá em `Settings` > `Pages`
   - Source: `main` branch, `/ (root)` folder
   - Clique em `Save`

4. **Aguarde 1-2 minutos** e acesse:
   ```
   https://caetanoronan.github.io/linhas-transmissao-foz-iguacu/outputs/mapas/
   ```

### Atualizar Mapas e Dashboard Publicados

Após fazer mudanças nos dados ou no código, regenere os mapas e dashboard:

```powershell
# Gerar mapas interativos
& ".venv\Scripts\python.exe" gerar_mapas_por_linha.py

# Gerar dashboard Plotly
& ".venv\Scripts\python.exe" gerar_relatorio_html.py

# Enviar tudo para GitHub
git add outputs/mapas/* outputs/dashboard.html outputs/municipios_afetados_completo.csv
git commit -m "Atualiza mapas e dashboard"
git push
```

📖 **Guia completo:** Veja `DEPLOY_GITHUB_PAGES.md` para instruções detalhadas.

## 💻 Rodar Dashboard Streamlit Localmente

Para rodar a versão interativa com Streamlit (opcional, já que o HTML está publicado):

1. **Instalar dependências:**
```powershell
cd "c:\Users\caetanoronan\OneDrive - UFSC\Área de Trabalho\Afetados_ln_trans"
".venv\Scripts\python.exe" -m pip install -r requirements.txt
```

2. **Gerar/atualizar dados (opcional):**
```powershell
".venv\Scripts\python.exe" analise_consolidada.py
```

3. **Iniciar dashboard:**
```powershell
".venv\Scripts\python.exe" -m streamlit run dashboard.py
```

Acesse: http://localhost:8501

## 🛠️ Tecnologias Utilizadas

- **Python 3.13** - Linguagem de programação
- **Pandas** - Manipulação e análise de dados
- **Plotly** - Visualizações interativas
- **GeoPandas/QGIS** - Processamento de dados geoespaciais
- **Streamlit** - Dashboard interativo local
- **GitHub Pages** - Hospedagem do dashboard HTML

## 📝 Créditos

**Autor:** Ronan Armando Caetano  
## 🗺️ Mapas Interativos

Foram gerados **9 mapas interativos** individualizados por voltagem e estado:

### Paraná (PR)
- 230 kV, 500 kV, 525 kV, 600 kV, 765 kV

### Santa Catarina (SC)
- 230 kV, 525 kV

### Rio Grande do Sul (RS)
- 230 kV, 525 kV

Cada mapa inclui:
- **Municípios afetados** (coloridos por voltagem)
- **Linha de transmissão** (traçado exato)
- **Faixa de servidão** (buffer de segurança)
- **Municípios não afetados** (fundo opcional)
- **Limite estadual** (contorno do estado)

**Tecnologia:** Folium + GeoPandas + Shapely

## 📝 Créditos

**Autor:** Ronan Armando Caetano  
**Fonte de Dados:** EPE (Empresa de Pesquisa Energética) - Webmap de Linhas de Transmissão  
**Assistência Técnica:** GitHub Copilot

## ❓ Troubleshooting

- **Porta ocupada:** altere `--server.port 8502`
- **Dados ausentes:** rode `analise_consolidada.py` ou use o botão no dashboard
- **Mapas não carregando:** verifique se os arquivos HTML estão em `outputs/mapas/`
- **Dados ausentes:** rode `analise_consolidada.py` e `gerar_mapas_por_linha.py`
- **Erro ao abrir gráficos:** use `--server.headless true`
- **404 no GitHub Pages:** verifique se `index.html` está na raiz do repositório

---

🗺️ **Mapas Interativos:** [https://caetanoronan.github.io/linhas-transmissao-foz-iguacu/outputs/mapas/](https://caetanoronan.github.io/linhas-transmissao-foz-iguacu/outputs/mapas/)  
📊 **Dashboard Completo:** [https://caetanoronan.github.io/linhas-transmissao-foz-iguacu/outputs/dashboard.html](https://caetanoronan.github.io/linhas-transmissao-foz-iguacu/outputs/dashboard.html)
