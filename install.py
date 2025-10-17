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
import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

console = Console()
ROOT = Path(__file__).parent.resolve()

# Define packages with minimum versions for stability
VCS_PACKAGES = [
    "badges @ git+https://github.com/EntySec/Badges",
    "pex @ git+https://github.com/EntySec/Pex",
    "colorscript @ git+https://github.com/EntySec/ColorScript",
    "adb-shell>=0.1.0",
    "rich>=10.0"
]

PY_PACKAGES: List[str] = []

DEFAULT_VENV = ROOT / ".venv"


def run(cmd: List[str], env: dict | None = None, check: bool = True) -> None:
    console.log(f"[bold purple]$[/bold purple] {' '.join(cmd)}")
    res = subprocess.run(cmd, env=env, capture_output=True, text=True)
    if res.returncode != 0:
        console.print(Panel(f"[red]Error:[/red] {res.stderr.strip()}", title="Installation Error"))
        if check:
            raise SystemExit(f"Command failed: {' '.join(cmd)} (exit {res.returncode})")


def ensure_virtualenv(venv_path: Path) -> Tuple[str, str]:
    if venv_path.exists():
        console.print(Panel(f"Using existing virtualenv: [bold]{venv_path}[/bold]", title="Virtualenv"))
    else:
        console.print(Panel(f"Creating virtualenv at: [bold]{venv_path}[/bold]", title="Virtualenv"))
        run([sys.executable, "-m", "venv", str(venv_path)])
    if os.name == "nt":
        py = venv_path / "Scripts" / "python.exe"
        pip = venv_path / "Scripts" / "pip.exe"
    else:
        py = venv_path / "bin" / "python"
        pip = venv_path / "bin" / "pip"
    return str(py), str(pip)


def install_packages(py_exe: str, packages: List[str], break_system: bool = False) -> None:
    if not packages:
        return
    cmd = [py_exe, "-m", "pip", "install"] + packages
    if break_system:
        cmd.append("--break-system-packages")
    run(cmd)


def install_local_package(py_exe: str, break_system: bool = False) -> None:
    cmd = [py_exe, "-m", "pip", "install", ".", "--no-deps"]
    if break_system:
        cmd.append("--break-system-packages")
    run(cmd)


def main() -> None:
    parser = argparse.ArgumentParser(description="Ghost installer (venv or --brek/system)")
    parser.add_argument("--no-venv", action="store_true", help="Do not create/use virtualenv; install in current interpreter")
    parser.add_argument("--venv", default=".venv", help="Virtualenv path (default: .venv)")
    parser.add_argument("--brek", action="store_true", help="Install only python-tool packages (filter out VCS/URLs).")
    parser.add_argument("--yes", "-y", action="store_true", help="Automatic yes for prompts")
    args = parser.parse_args()

    console.print(Panel(Text("Ghost Installer — staged installation\n\nIndex 99 → Exit", justify="center"), style="purple"))

    use_brek = args.brek
    use_venv = not args.no_venv
    auto_yes = args.yes

    # Interactive choice if not forced
    if not (args.brek or args.no_venv) and not auto_yes:
        choice = Prompt.ask(
            "Choose install mode",
            choices=["venv", "brek", "system"],
            default="venv",
            show_choices=True,
        )
        if choice == "venv":
            use_venv = True
            use_brek = False
        elif choice == "brek":
            use_venv = False
            use_brek = True
        else:
            use_venv = False
            use_brek = False
    elif auto_yes:
        use_venv = True
        use_brek = False

    break_system_flag = not use_venv
    if break_system_flag:
        console.print(Panel("Installing into current Python interpreter (no virtualenv). --break-system-packages enabled", title="Notice", style="yellow"))

    if use_venv:
        py_exe, pip_exe = ensure_virtualenv(Path(args.venv))
    else:
        py_exe = sys.executable

    console.print("[bold]Upgrading pip in target environment...[/bold]")
    cmd_upgrade = [py_exe, "-m", "pip", "install", "--upgrade", "pip"]
    if break_system_flag:
        cmd_upgrade.append("--break-system-packages")
    run(cmd_upgrade)

    console.print(Panel(f"Installing VCS/GitHub packages ({len(VCS_PACKAGES)} items)...", title="Dependencies"))
    install_packages(py_exe, VCS_PACKAGES, break_system_flag)

    console.print(Panel("Installing Ghost main package...", style="purple"))
    install_local_package(py_exe, break_system_flag)

    console.print(Panel("[bold green]Installation completed successfully![/bold green]"))
    console.print("You can now run: ghost")


if __name__ == "__main__":
    main()
