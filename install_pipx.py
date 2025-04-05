#!/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path
import importlib.util
import shutil


def run(cmd: list[str], cwd: str | None = None):
    print(f"→ {' '.join(cmd)}")
    subprocess.run(cmd, check=True, cwd=cwd)


def ensure_pip():
    try:
        import pip  # noqa: F401
    except ImportError:
        print("[+] Bootstrapping pip with ensurepip")
        run([sys.executable, "-m", "ensurepip", "--upgrade", "--default-pip"])


def install_virtualenv():
    print("[+] Installing virtualenv into user site-packages")
    run([sys.executable, "-m", "pip", "install", "--user", "--no-warn-script-location", "virtualenv"])


def create_bootstrap_venv(target: Path):
    print(f"[+] Creating bootstrap venv at {target}")

    if importlib.util.find_spec("venv") is not None:
        run([sys.executable, "-m", "venv", str(target)])
    else:
        ensure_pip()
        install_virtualenv()
        virtualenv_bin = Path.home() / ".local" / "bin" / "virtualenv"
        run([str(virtualenv_bin), str(target)])


def main():
    if sys.version_info < (3, 9):
        print("[-] Python 3.9+ required.", file=sys.stderr)
        sys.exit(1)

    bootstrap_dir = Path.home() / ".local" / "pipx-bootstrap"
    pipx_target_bin = Path.home() / ".local" / "bin" / "pipx"

    create_bootstrap_venv(bootstrap_dir)

    venv_pip = bootstrap_dir / "bin" / "pip"
    venv_pipx = bootstrap_dir / "bin" / "pipx"

    print("[+] Installing pipx into bootstrap venv")
    run([str(venv_pip), "install", "pipx"])

    print("[+] Using bootstrap pipx to install user pipx")
    run([str(venv_pipx), "install", "pipx"])

    print("[+] Verifying ~/.local/bin/pipx exists")
    if not pipx_target_bin.exists():
        print("[-] pipx was not installed correctly", file=sys.stderr)
        sys.exit(1)

    print("[✓] pipx installed successfully at ~/.local/bin/pipx")

    print("[+] Cleaning up bootstrap environment")
    shutil.rmtree(bootstrap_dir, ignore_errors=True)

    print("→ Add ~/.local/bin to your PATH if not already there")
    print("→ Then restart your shell or run: exec $SHELL")


if __name__ == "__main__":
    main()
