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

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
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

## Migrations

```bash
flask --app app.py db upgrade
```

Para criar uma migration nova:

```bash
flask --app app.py db migrate -m "descricao da alteracao"
flask --app app.py db upgrade
```

Com invoke:

```bash
invoke db-upgrade
invoke db-migrate --message="descricao da alteracao"
```

## Seed

Popula o banco com usuários, fórum, eventos, moradias, notificações e mensagens iniciais.

```bash
flask --app app.py seed
```

Com invoke:

```bash
invoke seed
```

## Rodar

```bash
flask --app app.py run --debug --port 5000
```

Com invoke:

```bash
invoke dev
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

```bash
./venv/bin/python -m unittest
```

Alternativa sem ativar o ambiente virtual:

```bash
python3 -m unittest
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
