#!/usr/bin/env python3
"""
deploy_secrets.py — Securely upload a production .env to the UniMap EC2 instance.

Reads your local .env file, injects the Elastic IP from Terraform output into
ALLOWED_HOSTS, writes a temp file, SCPs it to the server, and locks permissions.

Usage
-----
    # Auto-detect IP from `terraform output`
    python deploy_secrets.py

    # Or supply the Elastic IP manually
    python deploy_secrets.py --ip 54.72.100.200

    # Custom paths
    python deploy_secrets.py --env ../.env --key ~/.ssh/my_key.pem

Requirements
------------
    pip install python-dotenv   (only standard-lib + dotenv)
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# ── Defaults ──────────────────────────────────────────────────────────────────

REMOTE_USER = "ubuntu"
REMOTE_ENV_PATH = "/opt/unimap/.env"
SSH_KEY_DEFAULT = "~/.ssh/id_ed25519"
TERRAFORM_DIR = Path(__file__).resolve().parent.parent  # terraform/
PROJECT_ROOT = TERRAFORM_DIR.parent                     # repo root
LOCAL_ENV_DEFAULT = str(PROJECT_ROOT / ".env")

# Production domains that should always be in ALLOWED_HOSTS
PRODUCTION_HOSTS = [
    "api-unimap.birukkasahun.com",
    "jigjigaunimap.birukkasahun.com",
    "localhost",
    "127.0.0.1",
]

PRODUCTION_CORS = [
    "https://jigjigaunimap.birukkasahun.com",
    "http://localhost:5173",
]

PRODUCTION_CSRF = [
    "https://api-unimap.birukkasahun.com",
    "https://jigjigaunimap.birukkasahun.com",
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def log(msg: str) -> None:
    print(f"  → {msg}")


def error(msg: str) -> None:
    print(f"  ✗ {msg}", file=sys.stderr)
    sys.exit(1)


def get_terraform_ip() -> str | None:
    """Run `terraform output -json` and extract the public_ip value."""
    try:
        result = subprocess.run(
            ["terraform", "output", "-json"],
            cwd=str(TERRAFORM_DIR),
            capture_output=True,
            text=True,
            check=True,
        )
        outputs = json.loads(result.stdout)
        return outputs.get("public_ip", {}).get("value")
    except FileNotFoundError:
        log("terraform CLI not found — provide --ip manually.")
        return None
    except (subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        log(f"Could not read terraform output: {exc}")
        return None


def parse_env_file(path: str) -> dict[str, str]:
    """Parse a .env file into a dict, preserving comments as metadata."""
    values: dict[str, str] = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if "=" not in stripped:
                continue
            key, _, val = stripped.partition("=")
            values[key.strip()] = val.strip()
    return values


def build_production_env(local_values: dict[str, str], elastic_ip: str) -> str:
    """
    Build the production .env content using local secrets merged with
    production-specific overrides (ALLOWED_HOSTS, CORS, CSRF, DEBUG).
    """
    # Merge the Elastic IP into ALLOWED_HOSTS
    hosts = list(PRODUCTION_HOSTS)
    if elastic_ip not in hosts:
        hosts.append(elastic_ip)
    allowed_hosts = ",".join(hosts)

    # Use values from the local .env, with production overrides
    secret_key = local_values.get("SECRET_KEY", "CHANGE-ME-IMMEDIATELY")
    db_name = local_values.get("POSTGRES_DB", "unimap_db")
    db_user = local_values.get("POSTGRES_USER", "unimap_user")
    db_pass = local_values.get("POSTGRES_PASSWORD", "unimap_pass")
    workers = local_values.get("GUNICORN_WORKERS", "2")
    timeout = local_values.get("GUNICORN_TIMEOUT", "120")
    topo_path = local_values.get(
        "TOPOLOGY_GEOJSON_PATH", "/opt/unimap/data/topology_paths.geojson"
    )

    return f"""\
# ─── Django ──────────────────────────────────────────────────────────────
SECRET_KEY={secret_key}
DEBUG=False
ALLOWED_HOSTS={allowed_hosts}

# ─── PostgreSQL / PostGIS ────────────────────────────────────────────────
POSTGRES_DB={db_name}
POSTGRES_USER={db_user}
POSTGRES_PASSWORD={db_pass}
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# ─── CORS ────────────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS={",".join(PRODUCTION_CORS)}

# ─── CSRF ────────────────────────────────────────────────────────────────
CSRF_TRUSTED_ORIGINS={",".join(PRODUCTION_CSRF)}

# ─── Gunicorn ────────────────────────────────────────────────────────────
GUNICORN_WORKERS={workers}
GUNICORN_TIMEOUT={timeout}

# ─── Topology Data ──────────────────────────────────────────────────────
TOPOLOGY_GEOJSON_PATH={topo_path}
"""


def scp_upload(
    local_path: str,
    remote_ip: str,
    remote_path: str,
    ssh_key: str,
    user: str,
) -> None:
    """SCP a file to the remote host and lock permissions to 600."""
    key = os.path.expanduser(ssh_key)

    if not os.path.isfile(key):
        error(f"SSH key not found: {key}")

    remote_target = f"{user}@{remote_ip}:{remote_path}"

    # Ensure the remote directory exists
    mkdir_cmd = [
        "ssh", "-i", key,
        "-o", "StrictHostKeyChecking=accept-new",
        f"{user}@{remote_ip}",
        f"sudo mkdir -p {os.path.dirname(remote_path)} && sudo chown {user}:{user} {os.path.dirname(remote_path)}",
    ]
    log(f"Ensuring remote directory exists...")
    subprocess.run(mkdir_cmd, check=True)

    # Upload via SCP
    scp_cmd = [
        "scp", "-i", key,
        "-o", "StrictHostKeyChecking=accept-new",
        local_path,
        remote_target,
    ]
    log(f"Uploading to {remote_target}...")
    subprocess.run(scp_cmd, check=True)

    # Lock permissions: chmod 600 + chown to www-data for Gunicorn
    chmod_cmd = [
        "ssh", "-i", key,
        "-o", "StrictHostKeyChecking=accept-new",
        f"{user}@{remote_ip}",
        f"chmod 600 {remote_path} && echo 'Permissions set to 600 on {remote_path}'",
    ]
    log("Setting remote file permissions to 600...")
    subprocess.run(chmod_cmd, check=True)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Deploy production .env to the UniMap EC2 instance.",
    )
    parser.add_argument(
        "--ip",
        default=None,
        help="Elastic IP of the EC2 instance (auto-detected from Terraform if omitted).",
    )
    parser.add_argument(
        "--env",
        default=LOCAL_ENV_DEFAULT,
        help=f"Path to the local .env file (default: {LOCAL_ENV_DEFAULT}).",
    )
    parser.add_argument(
        "--key",
        default=SSH_KEY_DEFAULT,
        help=f"Path to the SSH private key (default: {SSH_KEY_DEFAULT}).",
    )
    parser.add_argument(
        "--remote-path",
        default=REMOTE_ENV_PATH,
        help=f"Remote .env destination (default: {REMOTE_ENV_PATH}).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the generated .env to stdout without uploading.",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("  UniMap — Deploy Secrets to EC2")
    print("=" * 60)

    # 1. Resolve Elastic IP
    elastic_ip = args.ip or get_terraform_ip()
    if not elastic_ip:
        error(
            "Could not determine Elastic IP.\n"
            "  Run from the terraform/ directory, or pass --ip <ADDRESS>."
        )
    log(f"Target server: {elastic_ip}")

    # 2. Read local .env
    env_path = args.env
    if not os.path.isfile(env_path):
        error(f"Local .env file not found: {env_path}")
    local_values = parse_env_file(env_path)
    log(f"Read {len(local_values)} variables from {env_path}")

    # 3. Build production .env
    production_env = build_production_env(local_values, elastic_ip)

    if args.dry_run:
        print("\n--- Generated .env (dry run) ---")
        print(production_env)
        print("--- End ---")
        return

    # 4. Write to temp file and upload
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".env",
        prefix="unimap_prod_",
        delete=False,
        encoding="utf-8",
    ) as tmp:
        tmp.write(production_env)
        tmp_path = tmp.name

    try:
        scp_upload(
            local_path=tmp_path,
            remote_ip=elastic_ip,
            remote_path=args.remote_path,
            ssh_key=args.key,
            user=REMOTE_USER,
        )
    finally:
        os.unlink(tmp_path)
        log(f"Cleaned up temp file.")

    print()
    print("=" * 60)
    print("  ✓ Secrets deployed successfully!")
    print("=" * 60)
    print(f"  Remote file : {args.remote_path} (chmod 600)")
    print(f"  ALLOWED_HOSTS includes: {elastic_ip}")
    print()
    print("  Next: restart Gunicorn to pick up the new config:")
    print(f"    ssh -i {args.key} ubuntu@{elastic_ip} \\")
    print(f'      "sudo systemctl restart unimap-gunicorn"')
    print()


if __name__ == "__main__":
    main()
