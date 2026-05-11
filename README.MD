# UniHub

Backend Flask da plataforma universitária UniHub.

Nesta etapa o projeto está focado em API JSON, SQLite, SQLAlchemy, Flask-Migrate, Blueprints e regras mockadas de usuário/roles. Ainda não existe login real, JWT, Flask-Login ou frontend Jinja/Tailwind.

## Estrutura

```text
app.py                  # coração da aplicação: create_app() e entrada local
tasks.py                # atalhos com invoke
unihub/
  ext/                  # configuração de extensões: db, migrate, swagger, config
  models/               # models SQLAlchemy
  views/                # blueprints e rotas JSON
  services/             # seed e serviços de apoio
  utils/                # respostas JSON e autenticação mockada
templates/              # reservado para Jinja no frontend futuro
static/                 # reservado para assets futuros
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
python -m unittest
```

## Roles Mockadas

Ainda não existe login real. Para simular usuário logado, o backend usa:

```python
USUARIO_MOCK_ID = 1
```

Usuários principais do seed:

```text
1 Lucas Almeida     usuario
3 Mariana Costa     moderador
5 Rafael Souza      admin
```

Para testar outra role, envie o header:

```bash
curl -H "X-Mock-User-Id: 5" http://127.0.0.1:5000/admin/dashboard
```

Regras atuais:

- `usuario`: cria tópicos, responde fórum, salva eventos e anuncia moradias.
- `moderador`: pode criar/gerenciar eventos e moderar fórum/moradias.
- `admin`: acessa `/admin/*`, gerencia usuários e pode desativar conteúdos.

## Endpoints Principais

```text
GET    /
GET    /health
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
curl -X POST http://127.0.0.1:5000/forum/topicos \
  -H "Content-Type: application/json" \
  -d '{"titulo":"Duvida Flask","descricao":"Como usar Blueprints?","curso":"Ciencia da Computacao","disciplina":"Web","categoria":"Duvida"}'
```

Criar evento como moderador:

```bash
curl -X POST http://127.0.0.1:5000/eventos \
  -H "Content-Type: application/json" \
  -H "X-Mock-User-Id: 3" \
  -d '{"titulo":"Workshop Flask","descricao":"API com Flask","categoria":"Workshop","data_evento":"2026-05-20","horario":"19:00","local":"UVV"}'
```

Alterar role como admin:

```bash
curl -X PATCH http://127.0.0.1:5000/admin/usuarios/2/role \
  -H "Content-Type: application/json" \
  -H "X-Mock-User-Id: 5" \
  -d '{"role":"moderador"}'
```
