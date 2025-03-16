import subprocess

from rich import print as rprint

# Update as needed.
SRC_PATHS = ["src", "tests", "devtools"]
DOC_PATHS = ["README.md"]


def main():
    rprint()

    errcount = 0
    errcount += _run(["codespell", "--write-changes", *SRC_PATHS, *DOC_PATHS])
    errcount += _run(["ruff", "check", "--fix", *SRC_PATHS])
    errcount += _run(["ruff", "format", *SRC_PATHS])
    errcount += _run(["mypy", *SRC_PATHS])

    rprint()

    if errcount != 0:
        rprint(f"[bold red]✗ Lint failed with {errcount} errors.[/bold red]")
    else:
        rprint("[bold green]✔️ Lint passed![/bold green]")
    rprint()

    return errcount


def _run(cmd: list[str]) -> int:
    rprint(f"[bold green]❯ {' '.join(cmd)}[/bold green]")
    errcount = 0
    try:
        subprocess.run(cmd, text=True, check=True)
    except subprocess.CalledProcessError as e:
        rprint(f"[bold red]Error: {e}[/bold red]")
        errcount = 1
    rprint()

    return errcount


if __name__ == "__main__":
    exit(main())
