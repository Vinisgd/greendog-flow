# 🚀 Deploy do GreenDog Flow no Railway

Tempo estimado: **10–15 minutos**

---

## Pré-requisitos

- Conta no [GitHub](https://github.com) (gratuita)
- Conta no [Railway](https://railway.app) (gratuita para começar)

---

## Passo 1 — Subir o código no GitHub

1. Acesse [github.com](https://github.com) e faça login
2. Clique em **"New repository"** (botão verde)
3. Nome sugerido: `greendog-flow`
4. Marque como **Private** (recomendado)
5. Clique em **"Create repository"**
6. Siga as instruções para fazer upload da pasta `kanbanflow-v2/`:
   - Na sua máquina, abra o terminal dentro da pasta
   - Execute:
     ```bash
     git init
     git add .
     git commit -m "GreenDog Flow v2"
     git branch -M main
     git remote add origin https://github.com/SEU-USUARIO/greendog-flow.git
     git push -u origin main
     ```

> 💡 **Alternativa sem terminal:** use o [GitHub Desktop](https://desktop.github.com/) com interface visual.

---

## Passo 2 — Criar projeto no Railway

1. Acesse [railway.app](https://railway.app) e faça login (pode usar a conta GitHub)
2. Clique em **"New Project"**
3. Escolha **"Deploy from GitHub repo"**
4. Autorize o Railway a acessar seu GitHub
5. Selecione o repositório `greendog-flow`
6. Railway detectará automaticamente que é um app Python ✅

---

## Passo 3 — Adicionar banco de dados PostgreSQL

1. Dentro do projeto no Railway, clique em **"+ New"**
2. Escolha **"Database" → "Add PostgreSQL"**
3. O Railway criará o banco e definirá `DATABASE_URL` automaticamente ✅

---

## Passo 4 — Configurar variáveis de ambiente

1. Clique no serviço do app (não no banco)
2. Vá em **"Variables"**
3. Adicione:

| Variável | Valor |
|----------|-------|
| `SECRET_KEY` | Uma string longa e aleatória — gere em [generate-secret.vercel.app/64](https://generate-secret.vercel.app/64) |

> ⚠️ `DATABASE_URL` é preenchido automaticamente pelo Railway — não precisa adicionar manualmente.

---

## Passo 5 — Fazer o deploy

1. Railway já deve estar fazendo o deploy automaticamente
2. Aguarde o build finalizar (1–3 minutos)
3. Quando aparecer ✅ **"Active"**, clique em **"View Logs"** para confirmar:
   ```
   Uvicorn running on http://0.0.0.0:...
   Seeding database... Done!
   ```

---

## Passo 6 — Acessar o app

1. Clique em **"Settings"** do serviço
2. Em **"Domains"**, clique em **"Generate Domain"**
3. Railway gera uma URL pública, ex: `https://greendog-flow-production.up.railway.app`
4. Acesse essa URL no navegador — o GreenDog Flow estará online! 🌭

---

## Usuários iniciais (seed automático)

| Email | Senha | Cargo |
|-------|-------|-------|
| admin@acme.com | admin123 | Administrador |
| manager@acme.com | admin123 | Gerente |
| dev1@acme.com | admin123 | Membro |
| viewer@acme.com | admin123 | Visualizador |

> 🔐 **Importante:** troque as senhas após o primeiro acesso em **Equipe → Editar**.

---

## Custos estimados

| Plano | Custo | Adequado para |
|-------|-------|---------------|
| **Hobby** (pago) | ~US$ 5/mês (~R$ 28) | Uso diário, sem pausas |
| **Free trial** | US$ 5 de crédito | Testar antes de pagar |

O banco PostgreSQL custa ~US$ 1–2/mês adicionais para uso leve.

---

## Domínio personalizado (opcional)

Se quiser usar `app.greendog.com.br` em vez da URL gerada:

1. No Railway → **Settings → Domains → Custom Domain**
2. Digite o domínio desejado
3. Configure o DNS no seu provedor de domínio conforme instruído
4. Aguarde propagação (até 24h)

---

## Suporte

Em caso de dúvidas, compartilhe esta pasta com seu técnico de confiança.
Toda a configuração necessária já está incluída nessa pasta.
