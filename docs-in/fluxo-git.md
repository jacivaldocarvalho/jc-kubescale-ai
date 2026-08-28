# Guia Git — Fluxo JC-KubeScale AI

## Estrutura de branches

O projeto utiliza:

```text
main
 └── Branch principal / estável

develop
 └── Branch de desenvolvimento

feature/*
 └── Branches para novas funcionalidades
```

Fluxo recomendado:

```text
feature/* → develop → main
```

---

# 1. Verificar estado atual

Antes de qualquer operação:

```bash
git status
git branch
git branch -a
```

Verificar também o remoto:

```bash
git remote -v
```

---

# 2. Criar uma nova feature

Partindo da `develop` atualizada:

```bash
git checkout develop
git pull origin develop
```

Criar a branch:

```bash
git checkout -b feature/nome-da-feature
```

Exemplos:

```bash
git checkout -b feature/api-chat
git checkout -b feature/kserve-deployment
git checkout -b feature/autoscaling
git checkout -b feature/observability
```

---

# 3. Trabalhar na feature

Verificar alterações:

```bash
git status
```

Adicionar arquivos:

```bash
git add .
```

Criar commit:

```bash
git commit -m "feat: implement chat endpoint"
```

Exemplos de commits:

```text
feat: add chat endpoint
feat: configure kserve inference service
feat: implement llm autoscaling
fix: correct api health check
docs: update architecture documentation
test: add chat endpoint tests
chore: update project dependencies
refactor: simplify inference service
```

---

# 4. Enviar feature para o GitHub

```bash
git push -u origin feature/nome-da-feature
```

Depois abrir um Pull Request:

```text
feature/nome-da-feature
            ↓
         develop
```

---

# 5. Atualizar develop

Depois que o Pull Request for aprovado e integrado:

```bash
git checkout develop
git pull origin develop
```

A `develop` agora contém a nova funcionalidade.

---

# 6. Preparar release para main

Antes do merge:

```bash
git checkout develop
git pull origin develop

git checkout main
git pull origin main
```

Voltar para `develop` e verificar se está tudo correto:

```bash
git checkout develop
git status
```

Executar testes:

```bash
make test
```

Se a CI estiver configurada, verificar também o resultado dos workflows no GitHub.

---

# 7. Merge develop → main

## Opção A — Merge local

Ir para `main`:

```bash
git checkout main
git pull origin main
```

Fazer o merge:

```bash
git merge --no-ff develop -m "merge: integrate develop into main"
```

Verificar:

```bash
git status
```

Enviar para o GitHub:

```bash
git push origin main
```

---

# 8. Fluxo usado na criação inicial do projeto

Para a criação inicial da estrutura:

```bash
git checkout develop

git add .

git commit -m "chore: initialize project structure"

git push -u origin develop
```

Depois:

```bash
git checkout main
git pull origin main

git merge --no-ff develop -m "merge: integrate project structure"

git push origin main
```

Resultado:

```text
main
  │
  ● merge: integrate project structure
  │
  ● chore: initialize project structure
  │
develop
```

---

# 9. Sincronizar branches

Sempre que houver alterações no remoto:

### Atualizar develop

```bash
git checkout develop
git pull origin develop
```

### Atualizar main

```bash
git checkout main
git pull origin main
```

---

# 10. Criar nova feature depois de atualizar develop

Sempre começar a feature a partir da `develop` atualizada:

```bash
git checkout develop
git pull origin develop

git checkout -b feature/nova-feature
```

Isso evita criar uma feature baseada em código antigo.

---

# 11. Resolver conflitos

Se ocorrer conflito durante um merge:

```bash
git status
```

Editar os arquivos indicados pelo Git.

Depois:

```bash
git add .
git commit
```

Se quiser cancelar o merge:

```bash
git merge --abort
```

---

# 12. Ver histórico

Visualizar histórico resumido:

```bash
git log --oneline --graph --decorate --all
```

Exemplo:

```text
*   abc1234 (HEAD -> main) merge: integrate develop into main
|\
| * def5678 (develop) feat: add autoscaling
| * ghi9012 feat: add kserve deployment
|/
* jkl3456 chore: initialize project structure
```

---

# 13. Ver branches

Branches locais:

```bash
git branch
```

Branches locais + remotas:

```bash
git branch -a
```

Branches remotas:

```bash
git branch -r
```

---

# 14. Excluir feature depois do merge

Depois que a feature foi integrada à `develop`:

```bash
git branch -d feature/nome-da-feature
```

Excluir também no remoto:

```bash
git push origin --delete feature/nome-da-feature
```

---

# 15. Regra importante

Não desenvolver diretamente na `main`.

Evitar:

```text
main ← desenvolvimento direto
```

Preferir:

```text
feature/*
    ↓
develop
    ↓
main
```

A `main` deve representar uma versão estável do projeto.

---

# 16. Fluxo diário recomendado

Para começar uma nova tarefa:

```bash
git checkout develop
git pull origin develop

git checkout -b feature/minha-feature
```

Desenvolver e testar.

Depois:

```bash
git status
git add .
git commit -m "feat: minha alteração"
git push -u origin feature/minha-feature
```

Abrir PR:

```text
feature/minha-feature → develop
```

Após aprovação:

```bash
git checkout develop
git pull origin develop
```

Quando estiver pronto para uma versão estável:

```text
develop → main
```

---

# 17. Checklist antes de merge para main

```text
[ ] develop está atualizada
[ ] Testes executados
[ ] CI passou
[ ] Sem secrets no Git
[ ] .gitignore validado
[ ] README atualizado
[ ] Documentação atualizada
[ ] Helm validado
[ ] Manifests Kubernetes validados
[ ] Terraform validado, quando aplicável
[ ] Pull Request revisado
[ ] Merge realizado
[ ] main atualizada no remoto
```

---

# 18. Comandos essenciais

### Status

```bash
git status
```

### Atualizar branch

```bash
git pull origin develop
```

### Criar branch

```bash
git checkout -b feature/nome
```

### Adicionar alterações

```bash
git add .
```

### Commit

```bash
git commit -m "feat: descrição"
```

### Push

```bash
git push -u origin feature/nome
```

### Trocar branch

```bash
git checkout develop
```

### Merge

```bash
git merge --no-ff develop
```

### Push da main

```bash
git push origin main
```

### Histórico

```bash
git log --oneline --graph --decorate --all
```

---

# Fluxo resumido

```text
                    ┌──────────────┐
                    │     main     │
                    │   estável    │
                    └──────▲───────┘
                           │
                           │ merge/release
                           │
                    ┌──────┴───────┐
                    │    develop   │
                    │ integração   │
                    └──────▲───────┘
                           │
                           │ Pull Request
                           │
              ┌────────────┴────────────┐
              │                         │
       feature/api               feature/kserve
              │                         │
              └──────────┬──────────────┘
                         │
                    desenvolvimento
```

## Regra de ouro

**Feature nasce de `develop`.
Feature entra em `develop`.
`develop` entra em `main`.
`main` representa o código estável.**
