#!/usr/bin/env python3

import os
import sys
import subprocess
import shutil
import importlib.util
from pathlib import Path
from typing import List, Optional


def run(cmd: List[str], cwd: Optional[str] = None) -> None:
    print(f"→ {' '.join(cmd)}")
    subprocess.run(cmd, check=True, cwd=cwd)


def ensure_pip() -> None:
    try:
        import pip  # noqa: F401
    except ImportError:
        print("[+] Bootstrapping pip using ensurepip")
        run([sys.executable, "-m", "ensurepip", "--upgrade", "--default-pip"])


def install_virtualenv() -> None:
    print("[+] Installing virtualenv via pip (user install)")
    run([sys.executable, "-m", "pip", "install", "--user", "--no-warn-script-location", "virtualenv"])


def create_bootstrap_venv(target: Path) -> None:
    print(f"[+] Creating bootstrap venv at {target}")

    if importlib.util.find_spec("venv") is not None:
        run([sys.executable, "-m", "venv", str(target)])
    else:
        print("[!] 'venv' module not available, using virtualenv fallback")
        ensure_pip()
        install_virtualenv()
        virtualenv_bin = Path.home() / ".local" / "bin" / "virtualenv"
        if not virtualenv_bin.exists():
            print("[-] virtualenv not found in ~/.local/bin", file=sys.stderr)
            sys.exit(1)
        run([str(virtualenv_bin), str(target)])


def main() -> None:
    if sys.version_info < (3, 6):
        print("[-] Python 3.6+ is required", file=sys.stderr)
        sys.exit(1)

    bootstrap_dir = Path.home() / ".local" / "pipx-bootstrap"
    pipx_target_bin = Path.home() / ".local" / "bin" / "pipx"

    create_bootstrap_venv(bootstrap_dir)

    venv_pip = bootstrap_dir / "bin" / "pip"
    venv_pipx = bootstrap_dir / "bin" / "pipx"

    print("[+] Installing pipx into bootstrap venv")
    run([str(venv_pip), "install", "pipx"])

    print("[+] Using bootstrap pipx to install user pipx")
    run([str(venv_pipx), "install", "pipx", "--force", "--include-deps"])

    if not pipx_target_bin.exists():
        print("[-] pipx installation failed", file=sys.stderr)
        sys.exit(1)

    print("[✓] pipx installed successfully at ~/.local/bin/pipx")

    print("[+] Cleaning up bootstrap venv")
    shutil.rmtree(bootstrap_dir, ignore_errors=True)

    print("→ Add ~/.local/bin to your PATH if not already there")
    print("→ Then restart your shell or run: exec $SHELL")


if __name__ == "__main__":
    main()
