#!/usr/bin/env python3
"""
MIT License

Copyright (c) 2020-2024 EntySec

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import List

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

console = Console()
ROOT = Path(__file__).parent.resolve()

# List of Python packages installed by Ghost installer
PYTHON_PACKAGES = [
    "ghost",
    "adb-shell",
    "pex",
    "badges",
    "colorscript",
]

# Default virtualenv path
DEFAULT_VENV = ROOT / ".venv"


def run(cmd: List[str], check: bool = True) -> None:
    """Run a shell command and print it."""
    console.log(f"[bold purple]$[/bold purple] {' '.join(cmd)}")
    res = subprocess.run(cmd)
    if check and res.returncode != 0:
        console.print(Panel(f"[red]Command failed: {' '.join(cmd)}[/red]"))


def uninstall_packages(python_exe: str, break_system: bool = False) -> None:
    """Uninstall all Ghost-related packages."""
    for pkg in PYTHON_PACKAGES:
        console.print(Panel(f"Uninstalling package: [bold]{pkg}[/bold]"))
        cmd = [python_exe, "-m", "pip", "uninstall", "-y", pkg]
        if break_system:
            cmd.append("--break-system-packages")
        run(cmd)


def remove_virtualenv(venv_path: Path) -> None:
    """Remove virtualenv folder if exists."""
    if venv_path.exists():
        console.print(Panel(f"Removing virtualenv: [bold]{venv_path}[/bold]"))
        import shutil
        shutil.rmtree(venv_path)
        console.print(Panel(f"[green]Virtualenv removed.[/green]"))
    else:
        console.print(Panel("[yellow]No virtualenv found.[/yellow]"))


def main() -> None:
    console.print(Panel("[bold purple]Ghost Uninstaller[/bold purple]\nIndex 99 → Return to Menu / Exit"))

    use_venv = False
    if DEFAULT_VENV.exists():
        use_venv = Confirm.ask(f"Detected virtualenv at {DEFAULT_VENV}. Remove it?", default=True)
        if use_venv:
            remove_virtualenv(DEFAULT_VENV)

    # Ask if want to uninstall packages from system Python
    uninstall_system = Confirm.ask("Do you want to uninstall Ghost Python packages from system interpreter?", default=False)
    if uninstall_system:
        python_exe = sys.executable
        uninstall_packages(python_exe, break_system=True)

    console.print(Panel("[bold green]Uninstall process completed.[/bold green]"))


if __name__ == "__main__":
    main()
