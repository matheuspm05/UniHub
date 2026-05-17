import sys
from pathlib import Path

from invoke.tasks import task


ROOT = Path(__file__).resolve().parent
PYTHON = f'"{sys.executable}"'
FLASK = f"{PYTHON} -m flask --app app.py"
PIP = f"{PYTHON} -m pip"


@task
def install(ctx):
    with ctx.cd(str(ROOT)):
        ctx.run(f"{PIP} install -r requirements.txt")
        ctx.run(f"{PIP} install -e .")


@task
def run(ctx, port=5000):
    with ctx.cd(str(ROOT)):
        ctx.run(f"{FLASK} --debug run --port {port}", pty=(sys.platform != "win32"))


@task
def routes(ctx):
    with ctx.cd(str(ROOT)):
        ctx.run(f"{FLASK} routes")


@task
def shell(ctx):
    with ctx.cd(str(ROOT)):
        ctx.run(f"{FLASK} shell", pty=(sys.platform != "win32"))


@task(name="db-upgrade")
def db_upgrade(ctx):
    with ctx.cd(str(ROOT)):
        ctx.run(f"{FLASK} db upgrade")


@task(name="db-migrate")
def db_migrate(ctx, message="auto migration"):
    with ctx.cd(str(ROOT)):
        ctx.run(f'{FLASK} db migrate -m "{message}"')


@task
def seed(ctx):
    with ctx.cd(str(ROOT)):
        ctx.run(f"{FLASK} seed")


@task
def test(ctx):
    with ctx.cd(str(ROOT)):
        ctx.run(f"{PYTHON} -m unittest")


@task
def dev(ctx, port=5000):
    db_upgrade(ctx)
    seed(ctx)
    run(ctx, port=port)
