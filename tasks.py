import sys
from pathlib import Path

from invoke.tasks import task


ROOT = Path(__file__).resolve().parent
VENV = ROOT / "venv"


def _quote(path):
    return f'"{path}"'


def _venv_python():
    if sys.platform == "win32":
        return VENV / "Scripts" / "python.exe"
    return VENV / "bin" / "python"


def _python():
    python = _venv_python()
    if python.exists():
        return _quote(python)
    return _quote(Path(sys.executable))


def _flask():
    return f"{_python()} -m flask --app app.py"


def _pip():
    return f"{_python()} -m pip"


@task
def venv(ctx):
    if _venv_python().exists():
        print("Ambiente virtual ja existe: venv")
        return
    with ctx.cd(str(ROOT)):
        ctx.run(f"{_quote(Path(sys.executable))} -m venv venv")


@task
def install(ctx):
    venv(ctx)
    with ctx.cd(str(ROOT)):
        ctx.run(f"{_pip()} install --upgrade pip")
        ctx.run(f"{_pip()} install -r requirements.txt")
        ctx.run(f"{_pip()} install -e .")


@task
def setup(ctx):
    install(ctx)
    with ctx.cd(str(ROOT)):
        ctx.run(f"{_python()} make_env.py")
    db_upgrade(ctx)
    seed(ctx)


@task
def run(ctx, port=5000):
    with ctx.cd(str(ROOT)):
        ctx.run(f"{_flask()} --debug run --port {port}", pty=(sys.platform != "win32"))


@task
def routes(ctx):
    with ctx.cd(str(ROOT)):
        ctx.run(f"{_flask()} routes")


@task
def shell(ctx):
    with ctx.cd(str(ROOT)):
        ctx.run(f"{_flask()} shell", pty=(sys.platform != "win32"))


@task(name="db-upgrade")
def db_upgrade(ctx):
    with ctx.cd(str(ROOT)):
        ctx.run(f"{_flask()} db upgrade")


@task(name="db-migrate")
def db_migrate(ctx, message="auto migration"):
    with ctx.cd(str(ROOT)):
        ctx.run(f'{_flask()} db migrate -m "{message}"')


@task
def seed(ctx):
    with ctx.cd(str(ROOT)):
        ctx.run(f"{_flask()} seed")


@task
def test(ctx):
    with ctx.cd(str(ROOT)):
        ctx.run(f"{_python()} -m unittest")


@task
def dev(ctx, port=5000):
    venv(ctx)
    db_upgrade(ctx)
    seed(ctx)
    run(ctx, port=port)
