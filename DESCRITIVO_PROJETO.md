# Descritivo Técnico do Projeto
## Análise Geoespacial de Linhas de Transmissão - Região Sul do Brasil

---

## 📋 Informações do Projeto

**Título:** Análise Geoespacial dos Municípios Afetados por Linhas de Transmissão de Energia Elétrica

**Responsável Técnico:** Ronan Armando Caetano

**Formação Acadêmica:**
- 🎓 **Ciências Biológicas** - Universidade Federal de Santa Catarina (UFSC)
- 🎓 **Técnico em Geoprocessamento** - Instituto Federal de Santa Catarina (IFSC)
- 🎓 **Técnico em Saneamento** - Instituto Federal de Santa Catarina (IFSC)

**Período de Desenvolvimento:** Outubro de 2025

**Área de Aplicação:** Geoprocessamento, Planejamento Energético e Territorial

---

## ⏱️ Tempo de Desenvolvimento Estimado

### Fase 1: Planejamento e Coleta de Dados (8-12 horas)
- Definição de escopo e objetivos
- Levantamento de fontes de dados oficiais
- Download e validação de dados geoespaciais
- Análise preliminar da qualidade dos dados
- Estruturação do projeto

### Fase 2: Processamento Geoespacial (20-30 horas)
- Reprojeção de dados para sistemas UTM apropriados
- Análise de intersecção espacial (linhas × municípios)
- Classificação por voltagem (230, 500, 525, 600, 765 kV)
- Processamento por estado (PR, SC, RS)
- Validação de geometrias
- Criação de buffers e faixas de servidão
- Consolidação de dados por município
- Geração de estatísticas descritivas

### Fase 3: Desenvolvimento de Mapas Interativos (15-20 horas)
- Configuração de mapas base com Folium
- Desenvolvimento de 9 mapas interativos personalizados
- Customização de popups e tooltips
- Definição de paletas de cores por voltagem
- Otimização de performance para web
- Testes de responsividade

### Fase 4: Relatórios e Visualizações (12-18 horas)
- Dashboard interativo com Plotly
- Relatório técnico completo
- Relatório acessível (TDAH/Dislexia)
- Gráficos estatísticos (barras, heatmaps, tabelas)
- Documentação de metodologia

### Fase 5: Documentação e Deploy (8-12 horas)
- Criação de README.md
- Documentação de processos
- Configuração de GitHub Pages
- Página índice de mapas com instruções
- Testes de deployment
- Controle de versão (Git)

### Fase 6: Refinamentos e Acessibilidade (6-10 horas)
- Implementação de tema claro/escuro
- Ajustes de contraste e legibilidade
- Otimização de acessibilidade web
- Filtros interativos na tabela
- Links para Google Maps
- Testes de usabilidade

---

## **TEMPO TOTAL ESTIMADO: 69-102 horas**
**(Média: ~85 horas de trabalho técnico especializado)**

---

## 📦 Produtos Gerados

### 1. Dados Geoespaciais Processados

#### Arquivos GeoPackage (.gpkg)
- **faixa_servidao.gpkg** - Faixas de servidão das linhas de transmissão
- **linhas_recortadas.gpkg** - Linhas de transmissão recortadas por estado (WGS 84)
- **linhas_recortadas_utm.gpkg** - Linhas em sistema UTM para análises precisas
- **municipios_afetados_por_estado.gpkg** - Municípios afetados consolidados por UF
- **municipios_afetados_por_layer.gpkg** - Municípios afetados por nível de voltagem

#### Arquivos CSV
- **dados_consolidados.csv** - Base de dados completa consolidada
- **municipios_afetados_completo.csv** - Lista completa de municípios afetados
- **municipios_multiplas_linhas.csv** - Municípios atravessados por múltiplas linhas

#### Dados por Camada (pasta `per_layer/`) - 12 arquivos CSV
- `municipios_linha_trans_230_PR.csv`
- `municipios_linha_trans_230_RS.csv`
- `municipios_linha_trans_230_SC.csv`
- `municipios_linha_trans_500_PR.csv`
- `municipios_linha_trans_525_PR.csv`
- `municipios_linha_trans_525_RS.csv`
- `municipios_linha_trans_525_SC.csv`
- `municipios_linha_trans_600_PR.csv`
- `municipios_linha_trans_765_PR.csv`
- `municipios_linhas_de_transmissao_base_PR.csv`
- `municipios_linhas_de_transmissao_base_RS.csv`
- `municipios_linhas_de_transmissao_base_SC.csv`

### 2. Mapas Interativos Web (9 mapas HTML)

**Paraná (5 mapas):**
- `mapa_230kV_PR.html` - Linhas de 230 kV no Paraná
- `mapa_500kV_PR.html` - Linhas de 500 kV no Paraná
- `mapa_525kV_PR.html` - Linhas de 525 kV no Paraná
- `mapa_600kV_PR.html` - Linhas de 600 kV no Paraná
- `mapa_765kV_PR.html` - Linhas de 765 kV no Paraná

**Santa Catarina (2 mapas):**
- `mapa_230kV_SC.html` - Linhas de 230 kV em SC
- `mapa_525kV_SC.html` - Linhas de 525 kV em SC

**Rio Grande do Sul (2 mapas):**
- `mapa_230kV_RS.html` - Linhas de 230 kV no RS
- `mapa_525kV_RS.html` - Linhas de 525 kV no RS

**Características dos mapas:**
- Tecnologia: Folium (Leaflet.js)
- Camadas de municípios afetados e não afetados
- Linhas de transmissão coloridas por voltagem
- Popups informativos
- Controles de zoom e camadas
- Responsivos para mobile

### 3. Relatórios e Dashboards

#### Dashboard Interativo (`outputs/dashboard.html`)
- Gráficos interativos com Plotly
- Estatísticas por voltagem, estado e município
- Matriz de calor estado × voltagem
- Top 25 municípios com mais linhas
- Tabela completa filtrável (517 municípios)
- Filtros por voltagem, estado e nome
- Tema claro/escuro
- Links para Google Maps
- Download de dados CSV

#### Relatório Técnico (`outputs/relatorio_tecnico.html`)
- Metodologia detalhada
- Análise estatística completa
- Visualizações avançadas
- Descrição de processos técnicos
- Referências bibliográficas

#### Relatório Acessível (`outputs/relatorio_acessivel.html`)
- Design otimizado para TDAH e Dislexia
- Fonte OpenDyslexic
- Cores vibrantes e alto contraste
- Layout simplificado
- Linguagem clara e objetiva

#### Página Índice de Mapas (`outputs/mapas/index.html`)
- Landing page profissional
- Introdução ao projeto e objetivos
- Instruções de uso passo a passo
- Estatísticas resumidas (517 municípios, 9 mapas, 3 estados, 5 voltagens)
- Links organizados por estado
- Créditos completos (autor, tecnologias, fontes, IA)
- Tema claro/escuro
- Totalmente responsivo

### 4. Scripts Python de Análise

- **analise_consolidada.py** - Consolidação de dados de todos os estados
- **estatisticas_detalhadas.py** - Geração de estatísticas descritivas
- **gerar_relatorio_acessivel.py** - Criação do relatório para neurodiversidade
- **gerar_relatorio_html.py** - Geração de relatórios técnicos
- **gerar_relatorio_tecnico.py** - Análise técnica aprofundada
- **dashboard.py** - Geração do dashboard interativo

### 5. Documentação

- **README.md** - Documentação principal do projeto
- **DEPLOY_GITHUB_PAGES.md** - Instruções de deployment
- **Explicacao_dados.txt** - Explicação sobre fontes de dados
- **EXPLICAÇÃO DISTRIBUIÇÃO DE LINHAS Trans.txt** - Detalhes técnicos
- **Link_de acessos.txt** - URLs de acesso aos produtos
- **DESCRITIVO_PROJETO.md** - Este documento

### 6. Website Público (GitHub Pages)

**URL:** https://caetanoronan.github.io/linhas-transmissao-foz-iguacu/

**Páginas disponíveis:**
- Dashboard principal (`/outputs/dashboard.html`)
- Relatório técnico (`/outputs/relatorio_tecnico.html`)
- Relatório acessível (`/outputs/relatorio_acessivel.html`)
- Índice de mapas (`/outputs/mapas/`)
- 9 mapas interativos individuais

---

## 🔧 Responsabilidades Técnicas

### 1. Geoprocessamento e Análise Espacial
**Competências aplicadas: Técnico em Geoprocessamento (IFSC)**

- **Processamento de dados vetoriais:** Manipulação de shapefiles e GeoPackages
- **Sistemas de coordenadas:** Conversão entre WGS 84 (EPSG:4326) e UTM (EPSG:31982, 31983)
- **Análise espacial:** Operações de intersecção, buffer e overlay
- **Topologia:** Validação e correção de geometrias
- **Cartografia digital:** Criação de mapas temáticos interativos
- **Metadados geoespaciais:** Documentação de fontes e processos
- **Controle de qualidade:** Validação de precisão e exatidão posicional

**Ferramentas utilizadas:**
- GeoPandas 1.0.1
- Shapely 2.0.6
- Fiona 1.10.1
- QGIS 3.x (pré-processamento)

### 2. Análise Ambiental e Territorial
**Competências aplicadas: Ciências Biológicas (UFSC) + Técnico em Saneamento (IFSC)**

- **Análise de impacto territorial:** Identificação de municípios afetados por infraestrutura energética
- **Planejamento territorial:** Mapeamento de faixas de servidão administrativa
- **Gestão de recursos naturais:** Compreensão do contexto ambiental das linhas de transmissão
- **Licenciamento ambiental:** Conhecimento de normas aplicáveis a empreendimentos lineares
- **Saneamento e infraestrutura:** Visão integrada de serviços públicos essenciais
- **Desenvolvimento regional:** Análise de distribuição espacial de infraestrutura crítica

**Conhecimentos aplicados:**
- Legislação ambiental brasileira
- Normas técnicas de transmissão de energia (ANEEL, ONS)
- Planejamento urbano e regional
- Análise socioambiental

### 3. Programação e Desenvolvimento Web
**Competências técnicas adquiridas e aplicadas**

- **Python 3.13:** Desenvolvimento de scripts de automação
- **Bibliotecas científicas:** Pandas, NumPy para análise de dados
- **Visualização de dados:** Plotly para gráficos interativos
- **Web mapping:** Folium para mapas web
- **HTML/CSS/JavaScript:** Desenvolvimento de interfaces responsivas
- **Controle de versão:** Git e GitHub
- **Deploy web:** GitHub Pages, CI/CD
- **Acessibilidade web:** WCAG 2.1, design inclusivo

### 4. Gestão de Dados e Documentação

- **Modelagem de dados:** Estruturação de bancos de dados geoespaciais
- **Padronização:** Nomenclatura consistente e organização de arquivos
- **Documentação técnica:** Criação de README, manuais e guias
- **Metadados:** Registro de fontes, datas e metodologias
- **Controle de qualidade:** Validação cruzada de dados
- **Arquivamento digital:** Organização para preservação a longo prazo

---

## 📊 Estatísticas do Projeto

### Dados Processados
- **517 municípios únicos** analisados
- **3 estados** da região Sul (PR, SC, RS)
- **5 níveis de voltagem** (230, 500, 525, 600, 765 kV)
- **9 mapas interativos** gerados
- **12 camadas de dados** por voltagem/estado
- **3 relatórios HTML** com propósitos diferentes

### Distribuição Estadual
- **Paraná:** 161 municípios analisados
- **Santa Catarina:** 154 municípios analisados
- **Rio Grande do Sul:** 205 municípios analisados

### Município com Maior Impacto
**Foz do Iguaçu/PR:** 5 linhas diferentes (230, 500, 525, 600, 765 kV)

---

## 🛠️ Stack Tecnológico Completo

### Software de Geoprocessamento
- **QGIS 3.x** - Processamento inicial e validação
- **GeoPandas 1.0.1** - Manipulação de dados geoespaciais
- **Shapely 2.0.6** - Operações geométricas
- **Fiona 1.10.1** - I/O de formatos geoespaciais

### Análise e Visualização de Dados
- **Python 3.13** - Linguagem principal
- **Pandas 2.2.3** - Análise de dados tabulares
- **NumPy** - Computação numérica
- **Plotly 5.24.1** - Gráficos interativos

### Desenvolvimento Web
- **Folium 0.18.0** - Mapas web interativos (Leaflet.js)
- **HTML5 + CSS3** - Estrutura e estilização
- **JavaScript** - Interatividade (filtros, tema)

### Controle de Versão e Deploy
- **Git** - Versionamento
- **GitHub** - Hospedagem de código
- **GitHub Pages** - Publicação web

### Ferramentas de Suporte
- **VS Code** - IDE principal
- **GitHub Copilot** - Assistência com IA para desenvolvimento
- **PowerShell** - Automação de tarefas

---

## 📚 Fontes de Dados Oficiais

1. **Empresa de Pesquisa Energética (EPE)** - Linhas de transmissão PR/SC
2. **Instituto Brasileiro de Geografia e Estatística (IBGE)** - Malhas municipais PR/SC
3. **Dados estaduais do Rio Grande do Sul** - Linhas e municípios RS
4. **Agência Nacional de Energia Elétrica (ANEEL)** - Normas técnicas

---

## 🎯 Aplicações Práticas

Este projeto pode ser utilizado para:

1. **Planejamento Energético:** Identificação de áreas de influência de linhas de transmissão
2. **Gestão Territorial:** Apoio a planos diretores municipais
3. **Licenciamento Ambiental:** Mapeamento de áreas afetadas
4. **Estudos Acadêmicos:** Base de dados para pesquisas em energia e território
5. **Transparência Pública:** Visualização acessível de infraestrutura energética
6. **Gestão Municipal:** Consulta rápida de linhas que atravessam cada município
7. **Análise de Impacto:** Avaliação de exposição a campos eletromagnéticos
8. **Planejamento de Expansão:** Base para futuros estudos de novas linhas

---

## 🏆 Diferenciais do Projeto

✅ **Multidisciplinaridade:** Integração de conhecimentos em biologia, saneamento e geoprocessamento

✅ **Acessibilidade:** Relatório específico para pessoas com TDAH e dislexia

✅ **Interatividade:** Mapas e dashboards totalmente interativos

✅ **Código Aberto:** Disponível no GitHub para reprodutibilidade

✅ **Documentação Completa:** Metodologia transparente e replicável

✅ **Responsividade:** Funciona em desktop, tablet e mobile

✅ **Padrões Web:** Seguindo boas práticas de desenvolvimento

✅ **Design Inclusivo:** Tema claro/escuro, alto contraste

---

## 📞 Contato

**Autor:** Ronan Armando Caetano

**Repositório:** https://github.com/caetanoronan/linhas-transmissao-foz-iguacu

**Website do Projeto:** https://caetanoronan.github.io/linhas-transmissao-foz-iguacu/

---

## 📄 Licença e Uso

Este projeto foi desenvolvido com finalidade técnica e educacional. Os dados são derivados de fontes públicas oficiais. Para uso comercial ou acadêmico, consultar o autor.

---

**Documento gerado em:** 26 de outubro de 2025

**Versão:** 1.0
