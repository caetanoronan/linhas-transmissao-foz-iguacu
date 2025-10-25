# 🚀 Deploy do Dashboard no GitHub Pages

## Passo a Passo para Publicação

### 1️⃣ Preparar o Repositório Git

Abra o PowerShell nesta pasta e execute:

```powershell
# Inicializar repositório Git (se ainda não tiver)
git init

# Configurar seu usuário Git (substitua pelos seus dados)
git config user.name "Ronan Armando Caetano"
git config user.email "seu-email@exemplo.com"

# Adicionar todos os arquivos
git add .

# Fazer o primeiro commit
git commit -m "Adiciona dashboard de linhas de transmissão de Foz do Iguaçu"
```

### 2️⃣ Criar Repositório no GitHub

1. Acesse https://github.com/new
2. Nome sugerido: `linhas-transmissao-foz-iguacu`
3. Descrição: `Análise de municípios afetados por linhas de transmissão da Usina de Foz do Iguaçu`
4. **Deixe PÚBLICO** (necessário para GitHub Pages gratuito)
5. **NÃO marque** "Add README" nem outras opções
6. Clique em **"Create repository"**

### 3️⃣ Conectar e Enviar para o GitHub

No PowerShell, execute (substitua `SEU-USUARIO` pelo seu nome de usuário do GitHub):

```powershell
# Adicionar o repositório remoto
git remote add origin https://github.com/SEU-USUARIO/linhas-transmissao-foz-iguacu.git

# Renomear branch para main
git branch -M main

# Enviar para o GitHub
git push -u origin main
```

Se pedir autenticação:
- **Usuário**: seu nome de usuário do GitHub
- **Senha**: use um **Personal Access Token** (não a senha da conta)
  - Criar token em: https://github.com/settings/tokens
  - Permissões necessárias: `repo` (marcar todas)

### 4️⃣ Configurar GitHub Pages

1. Vá ao repositório no GitHub
2. Clique em **Settings** (Configurações)
3. No menu lateral, clique em **Pages**
4. Em **Source** (Origem):
   - Branch: selecione **`main`**
   - Folder: selecione **`/ (root)`**
5. Clique em **Save**

### 5️⃣ Mover o Dashboard para a Raiz

O GitHub Pages procura por `index.html` na raiz do repositório. Execute:

```powershell
# Copiar o dashboard para a raiz como index.html
Copy-Item "outputs\dashboard.html" "index.html"

# Copiar o CSV também
Copy-Item "outputs\municipios_afetados_completo.csv" "municipios_afetados_completo.csv"

# Adicionar e commitar
git add index.html municipios_afetados_completo.csv
git commit -m "Adiciona dashboard como index.html para GitHub Pages"
git push
```

### 6️⃣ Acessar o Dashboard

Aguarde 1-2 minutos e acesse:

```
https://SEU-USUARIO.github.io/linhas-transmissao-foz-iguacu/
```

## ✅ Verificação

Depois de publicado, verifique se:
- ✓ Dashboard está acessível no link
- ✓ Gráficos interativos funcionam
- ✓ Tema claro/escuro funciona
- ✓ Filtros da tabela funcionam
- ✓ Download do CSV funciona
- ✓ Links do Google Maps abrem corretamente

## 🔄 Atualizações Futuras

Quando fizer mudanças no dashboard:

```powershell
# Gerar novo dashboard
& "C:/Users/caetanoronan/OneDrive - UFSC/Área de Trabalho/Afetados_ln_trans/.venv/Scripts/python.exe" gerar_relatorio_html.py

# Copiar para a raiz
Copy-Item "outputs\dashboard.html" "index.html" -Force
Copy-Item "outputs\municipios_afetados_completo.csv" "municipios_afetados_completo.csv" -Force

# Enviar para o GitHub
git add index.html municipios_afetados_completo.csv
git commit -m "Atualiza dashboard"
git push
```

## 📝 Notas Importantes

- O repositório precisa ser **PÚBLICO** para GitHub Pages gratuito
- O arquivo deve se chamar **`index.html`** na raiz
- Mudanças podem levar 1-2 minutos para aparecer online
- O CSV de download precisa estar no mesmo diretório que o index.html

## 🆘 Problemas Comuns

### Erro 404 - Página não encontrada
- Verifique se o arquivo se chama `index.html` (não `dashboard.html`)
- Confirme que está na raiz do repositório (não em `outputs/`)
- Aguarde alguns minutos após o push

### CSV Download não funciona
- Certifique-se de que `municipios_afetados_completo.csv` está na raiz
- Verifique se o commit incluiu o arquivo CSV

### Gráficos não aparecem
- Verifique se o CDN do Plotly está acessível
- Abra o console do navegador (F12) para ver erros

---

**🎉 Sucesso!** Seu dashboard estará online e acessível para qualquer pessoa com o link!
