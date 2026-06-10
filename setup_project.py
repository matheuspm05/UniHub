import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def run(command):
    print(f"\n> {' '.join(str(part) for part in command)}")
    subprocess.run(command, cwd=ROOT, check=True)


def ensure_active_venv():
    if sys.prefix == sys.base_prefix:
        raise SystemExit(
            "Ative a venv antes de rodar este script.\n"
            "Linux/macOS: source venv/bin/activate\n"
            r"Windows PowerShell: .\venv\Scripts\Activate.ps1"
        )


def main():
    ensure_active_venv()
    python = Path(sys.executable)

    run([python, "-m", "pip", "install", "--upgrade", "pip"])
    run([python, "-m", "pip", "install", "-r", "requirements.txt"])
    run([python, "-m", "pip", "install", "-e", "."])
    run([python, "make_env.py"])
    run([python, "-m", "flask", "--app", "app.py", "db", "upgrade"])
    run([python, "-m", "flask", "--app", "app.py", "seed"])

    print("\nProjeto pronto.")
    print("Para rodar: flask --app app.py run --debug --port 5000")


if __name__ == "__main__":
    main()
