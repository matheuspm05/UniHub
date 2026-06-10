# UniHub

Aplicação Flask da plataforma universitária UniHub.

Nesta etapa o projeto combina API JSON com páginas renderizadas em Jinja, usando SQLite, SQLAlchemy, Flask-Migrate, Blueprints, Flask-Login e regras de acesso por roles.

## Estrutura

```text
app.py                  # coração da aplicação: create_app() e entrada local
tasks.py                # atalhos com invoke
unihub/
  ext/                  # configuração de extensões: db, migrate, swagger, config
  models/               # models SQLAlchemy
  views/                # blueprints de API e páginas
  services/             # seed e serviços de apoio
  utils/                # respostas JSON e helpers de autenticação/permissão
templates/              # páginas e componentes Jinja
static/                 # assets da interface
tests/                  # testes automatizados
migrations/             # Flask-Migrate/Alembic
```

## Instalar

Depois de clonar o repositório, entre na pasta do projeto:

```bash
git clone <URL_DO_REPOSITORIO>
cd Unihub
```

### Instalação recomendada

Crie e ative a `venv` primeiro. Depois rode `setup_project.py` para instalar dependências, gerar os arquivos `.env`, aplicar migrations e popular o banco.

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
python setup_project.py
```

Windows PowerShell:

```powershell
py -3 -m venv venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
python setup_project.py
```

Windows CMD:

```bat
py -3 -m venv venv
venv\Scripts\activate.bat
python setup_project.py
```

### Instalação manual

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
python make_env.py
flask --app app.py db upgrade
flask --app app.py seed
```

Windows PowerShell:

```powershell
py -3 -m venv venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
python make_env.py
flask --app app.py db upgrade
flask --app app.py seed
```

Windows CMD:

```bat
py -3 -m venv venv
venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
python make_env.py
flask --app app.py db upgrade
flask --app app.py seed
```

### PowerShell e permissão de scripts

No Windows, o erro mais comum é o PowerShell bloquear `Activate.ps1`. Para liberar somente o terminal atual, rode:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

## Configurar ambiente

O projeto usa `.env.dev`, `.env.test` e `.env.prod`. Use `.env.example` como referência.

Exemplo para desenvolvimento:

```env
FLASK_CONFIG=development
SECRET_KEY=dev-secret-key
DATABASE_URL=sqlite:///unihub.db
```

Se `DATABASE_URL` não existir, o fallback é SQLite local.

Se quiser gerar os arquivos de ambiente automaticamente:

Linux/macOS:

```bash
./venv/bin/python make_env.py
```

Windows PowerShell:

```powershell
.\venv\Scripts\python.exe make_env.py
```

## Migrations

Linux/macOS:

```bash
./venv/bin/python -m flask --app app.py db upgrade
```

Windows PowerShell:

```powershell
.\venv\Scripts\python.exe -m flask --app app.py db upgrade
```

Para criar uma migration nova:

Linux/macOS:

```bash
./venv/bin/python -m flask --app app.py db migrate -m "descricao da alteracao"
./venv/bin/python -m flask --app app.py db upgrade
```

Windows PowerShell:

```powershell
.\venv\Scripts\python.exe -m flask --app app.py db migrate -m "descricao da alteracao"
.\venv\Scripts\python.exe -m flask --app app.py db upgrade
```

Com invoke:

```bash
invoke db-upgrade
invoke db-migrate --message="descricao da alteracao"
```

## Seed

Popula o banco com usuários, fórum, eventos, moradias, notificações e mensagens iniciais.

Linux/macOS:

```bash
./venv/bin/python -m flask --app app.py seed
```

Windows PowerShell:

```powershell
.\venv\Scripts\python.exe -m flask --app app.py seed
```

Com invoke:

```bash
invoke seed
```

## Rodar

Linux/macOS:

```bash
./venv/bin/python -m flask --app app.py run --debug --port 5000
```

Windows PowerShell:

```powershell
.\venv\Scripts\python.exe -m flask --app app.py run --debug --port 5000
```

Com invoke:

```bash
invoke dev
```

O `tasks.py` foi preparado para Linux e Windows. Se o `invoke` estiver instalado no ambiente virtual, estes atalhos funcionam nos dois sistemas:

```bash
invoke setup
invoke install
invoke db-upgrade
invoke seed
invoke test
invoke dev
```

O `invoke setup` faz o fluxo completo: cria `venv`, instala dependências, gera `.env`, roda migrations e executa o seed.

No Windows, se o comando `invoke` não estiver disponível no terminal atual, use:

```powershell
.\venv\Scripts\python.exe -m invoke dev
```

Se a porta 5000 estiver ocupada:

```bash
invoke dev --port=5001
```

Fluxos principais no navegador:

- Landing page: `http://127.0.0.1:5000/`
- Login: `http://127.0.0.1:5000/auth/login`
- Dashboard: `http://127.0.0.1:5000/dashboard`
- Perfil: `http://127.0.0.1:5000/perfil`
- Notificações: `http://127.0.0.1:5000/notificacoes`

## Swagger

Interface:

```text
http://127.0.0.1:5000/swagger/
```

JSON:

```text
http://127.0.0.1:5000/swagger.json
```

## Testes

Os testes usam SQLite em memória e fazem seed automaticamente.

Linux/macOS:

```bash
./venv/bin/python -m unittest
```

Windows PowerShell:

```powershell
.\venv\Scripts\python.exe -m unittest
```

Com invoke:

```bash
invoke test
```

## Autenticação

O projeto usa Flask-Login com sessão do Flask. Primeiro faça login:

```bash
curl -X POST http://127.0.0.1:5000/auth/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"email":"lucas.almeida@uvv.br","senha":"senha123"}'
```

Usuários principais do seed:

```text
1 Lucas Almeida     usuario
3 Mariana Costa     moderador
5 Rafael Souza      admin
```

A senha padrão dos usuários do seed é:

```text
senha123
```

Para chamar uma rota protegida via cURL, envie o cookie salvo no login:

```bash
curl -b cookies.txt http://127.0.0.1:5000/auth/me
```

Regras atuais:

- `usuario`: cria tópicos, responde fórum, salva eventos e anuncia moradias.
- `moderador`: pode criar eventos, criar avisos e moderar fórum/moradias.
- `admin`: acessa `/admin/*`, gerencia usuários e pode desativar conteúdos.

## Rotas Principais

```text
GET    /
GET    /dashboard
GET    /perfil
GET    /perfil/editar
GET    /health
POST   /auth/cadastro
GET    /auth/cadastro
POST   /auth/login
GET    /auth/login
POST   /auth/logout
GET    /auth/me
GET    /usuarios
GET    /usuarios/me
PATCH  /usuarios/me
GET    /forum/topicos
POST   /forum/topicos
POST   /forum/topicos/<id>/respostas
GET    /eventos
POST   /eventos
POST   /eventos/<id>/salvar
GET    /agenda
GET    /moradias
POST   /moradias
GET    /notificacoes
GET    /mensagens
GET    /admin/dashboard
GET    /admin/usuarios
PATCH  /admin/usuarios/<id>/role
PATCH  /admin/usuarios/<id>/desativar
```

## Exemplos cURL

```bash
curl http://127.0.0.1:5000/health
curl http://127.0.0.1:5000/forum/topicos
curl http://127.0.0.1:5000/eventos
curl http://127.0.0.1:5000/moradias
```

Criar tópico:

```bash
curl -X POST http://127.0.0.1:5000/auth/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"email":"lucas.almeida@uvv.br","senha":"senha123"}'

curl -X POST http://127.0.0.1:5000/forum/topicos \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"titulo":"Duvida Flask","descricao":"Como usar Blueprints?","curso":"Ciencia da Computacao","disciplina":"Web","categoria":"Duvida"}'
```

Criar evento como moderador:

```bash
curl -X POST http://127.0.0.1:5000/auth/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"email":"mariana.costa@uvv.br","senha":"senha123"}'

curl -X POST http://127.0.0.1:5000/eventos \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"titulo":"Workshop Flask","descricao":"API com Flask","categoria":"Workshop","data_evento":"2026-05-20","horario":"19:00","local":"UVV"}'
```

Alterar role como admin:

```bash
curl -X POST http://127.0.0.1:5000/auth/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"email":"rafael.souza@uvv.br","senha":"senha123"}'

curl -X PATCH http://127.0.0.1:5000/admin/usuarios/2/role \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"role":"moderador"}'
```
