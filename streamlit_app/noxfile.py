import nox


@nox.session(python=False, name="lint")
def lint(session):
    """Black + isort + flake8"""
    # session.install("-r", "requirements.dev.txt")
    session.run("black", ".")
    session.run("isort", "--profile=black", ".")
    session.run("flake8", "--config=./.flake8", ".")


@nox.session(python=False, name="test")
def tests(session):
    """pytest"""
    # session.install("-r", "requirements.dev.txt")
    extra_args = session.posargs or [
        "--cov-report=html:coverage",
        "--cov-report=term-missing",
        "--cov=.",
        "--cov-fail-under=5",
        "-v",
        "-m",
        "not e2e",
    ]
    session.run(
        "pytest",
        "--cov-config=./pyproject.toml",
        *extra_args,
        "./tests",
    )
