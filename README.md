# Linhas de Transmissão – Foz do Iguaçu (Região Sul)

**Autor:** Ronan Armando Caetano

Dashboard interativo e análise completa dos municípios afetados por linhas de transmissão que partem da Usina Hidrelétrica de Foz do Iguaçu e distribuem energia para a região Sul do Brasil (Paraná, Santa Catarina e Rio Grande do Sul).

## 🌐 Dashboard Online

**Acesse o dashboard publicado:** [https://SEU-USUARIO.github.io/linhas-transmissao-foz-iguacu/](https://SEU-USUARIO.github.io/linhas-transmissao-foz-iguacu/)

> ⚠️ **Substitua `SEU-USUARIO`** pelo seu nome de usuário do GitHub após publicar

## 📊 Sobre o Projeto

Este projeto analisa **517 municípios únicos** afetados por linhas de transmissão de diferentes voltagens:
- 230 kV
- 500 kV
- 525 kV
- 600 kV
- 765 kV

### Funcionalidades
- ✅ Visualizações interativas com Plotly
- ✅ Filtros por estado, voltagem e município
- ✅ Links diretos para Google Maps
- ✅ Download de dados em CSV
- ✅ Tema claro/escuro
- ✅ Análise de municípios com múltiplas linhas

## 📁 Estrutura do Projeto

```
📁 Afetados_ln_trans/
├── 📄 index.html                          # Dashboard HTML (GitHub Pages)
├── 📄 municipios_afetados_completo.csv    # Dados completos para download
├── 📄 gerar_relatorio_html.py             # Script para gerar dashboard HTML
├── 📄 analise_consolidada.py              # Consolida dados dos CSVs
├── 📄 dashboard.py                        # Dashboard Streamlit (local)
├── 📄 estatisticas_detalhadas.py          # Análises detalhadas no console
├── 📄 dados_consolidados.csv              # Dados consolidados
├── 📄 municipios_multiplas_linhas.csv     # Municípios com múltiplas linhas
├── 📁 per_layer/                          # CSVs por voltagem e estado
├── 📁 outputs/                            # Arquivos gerados
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
git remote add origin https://github.com/SEU-USUARIO/linhas-transmissao-foz-iguacu.git
git push -u origin main
```

3. **Configurar GitHub Pages:**
   - Vá em `Settings` > `Pages`
   - Source: `main` branch, `/ (root)` folder
   - Clique em `Save`

4. **Aguarde 1-2 minutos** e acesse:
   ```
   https://SEU-USUARIO.github.io/linhas-transmissao-foz-iguacu/
   ```

### Atualizar Dashboard Publicado

Após fazer mudanças nos dados ou no código:

```powershell
# Gerar novo dashboard
& ".venv\Scripts\python.exe" gerar_relatorio_html.py

# Copiar para a raiz
Copy-Item "outputs\dashboard.html" "index.html" -Force
Copy-Item "outputs\municipios_afetados_completo.csv" "municipios_afetados_completo.csv" -Force

# Enviar para GitHub
git add index.html municipios_afetados_completo.csv
git commit -m "Atualiza dashboard"
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
**Assistência Técnica:** GitHub Copilot

## ❓ Troubleshooting

- **Porta ocupada:** altere `--server.port 8502`
- **Dados ausentes:** rode `analise_consolidada.py` ou use o botão no dashboard
- **Erro ao abrir gráficos:** use `--server.headless true`
- **404 no GitHub Pages:** verifique se `index.html` está na raiz do repositório

---

📊 **Dashboard Online:** [https://SEU-USUARIO.github.io/linhas-transmissao-foz-iguacu/](https://SEU-USUARIO.github.io/linhas-transmissao-foz-iguacu/)
