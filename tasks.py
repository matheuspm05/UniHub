from invoke import task


FLASK = "venv/bin/flask --app app.py"
PIP = "venv/bin/pip"


@task
def install(ctx):
    ctx.run(f"{PIP} install -r requirements.txt")
    ctx.run(f"{PIP} install -e .")


@task
def run(ctx, port=5000):
    ctx.run(f"{FLASK} --debug run --port {port}", pty=True)


@task
def routes(ctx):
    ctx.run(f"{FLASK} routes")


@task
def shell(ctx):
    ctx.run(f"{FLASK} shell", pty=True)


@task(name="db-upgrade")
def db_upgrade(ctx):
    ctx.run(f"{FLASK} db upgrade")


@task(name="db-migrate")
def db_migrate(ctx, message="auto migration"):
    ctx.run(f'{FLASK} db migrate -m "{message}"')


@task
def seed(ctx):
    ctx.run(f"{FLASK} seed")


@task
def dev(ctx, port=5000):
    db_upgrade(ctx)
    seed(ctx)
    run(ctx, port=port)
