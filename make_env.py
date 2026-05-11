from pathlib import Path


ENV_FILES = {
    ".env.dev": """SECRET_KEY=dev-unihub-secret-key
DATABASE_URL=sqlite:///unihub.db
FLASK_ENV=development
FLASK_CONFIG=development
""",
    ".env.test": """SECRET_KEY=test-unihub-secret-key
TEST_DATABASE_URL=sqlite:///:memory:
FLASK_ENV=testing
FLASK_CONFIG=testing
""",
    ".env.prod": """SECRET_KEY=change-me-in-production
DATABASE_URL=sqlite:///unihub.db
FLASK_ENV=production
FLASK_CONFIG=production
""",
}


def main():
    base_dir = Path(__file__).resolve().parent
    for filename, content in ENV_FILES.items():
        path = base_dir / filename
        if not path.exists():
            path.write_text(content, encoding="utf-8")
            print(f"Criado: {filename}")
        else:
            print(f"Ja existe: {filename}")


if __name__ == "__main__":
    main()
