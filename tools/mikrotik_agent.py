#!/usr/bin/env python3
"""Hasan MikroTik Generator local execution agent.

Runs on Windows, Linux, or macOS with Python 3.10+.
Binds to 127.0.0.1 only and executes approved RouterOS CLI lines over SSH.
"""

from __future__ import annotations

import json
import os
import platform
import secrets
import socket
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from ipaddress import ip_address
from typing import Any

try:
    import paramiko
except ImportError:
    print("Missing dependency. Run: python -m pip install -r tools/requirements-agent.txt")
    raise

BIND_HOST = "127.0.0.1"
BIND_PORT = int(os.environ.get("MTG_AGENT_PORT", "8765"))
PAIRING_TOKEN = os.environ.get("MTG_AGENT_TOKEN") or secrets.token_urlsafe(24)
ALLOWED_ORIGIN = os.environ.get("MTG_ALLOWED_ORIGIN", "*")
MAX_COMMANDS = 250
MAX_BODY = 512_000


def safe_target(host: str) -> str:
    host = host.strip()
    if not host or len(host) > 253 or any(ch in host for ch in "\r\n\t /\\"):
        raise ValueError("Invalid router host")
    try:
        value = ip_address(host)
        if value.is_multicast or value.is_unspecified:
            raise ValueError("Unsupported router address")
    except ValueError as exc:
        if "Invalid router host" in str(exc) or "Unsupported" in str(exc):
            raise
        if not all(part and part.replace("-", "").isalnum() for part in host.split(".")):
            raise ValueError("Invalid router hostname")
    return host


def clean_commands(value: Any) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError("No commands supplied")
    if len(value) > MAX_COMMANDS:
        raise ValueError(f"Maximum {MAX_COMMANDS} commands per run")
    commands: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise ValueError("Every command must be text")
        command = item.strip()
        if not command or "\n" in command or "\r" in command:
            raise ValueError("Each command must contain exactly one RouterOS CLI line")
        if len(command) > 2048:
            raise ValueError("Command is too long")
        commands.append(command)
    return commands


def execute(payload: dict[str, Any]) -> dict[str, Any]:
    router = payload.get("router") or {}
    host = safe_target(str(router.get("host", "")))
    port = int(router.get("port", 22))
    if not 1 <= port <= 65535:
        raise ValueError("Invalid SSH port")
    username = str(router.get("username", "")).strip()
    password = str(router.get("password", ""))
    if not username or not password:
        raise ValueError("Router username and password are required")
    commands = clean_commands(payload.get("commands"))
    stop_on_error = bool(payload.get("stop_on_error", True))
    create_backup = bool(payload.get("create_backup", True))

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    results: list[dict[str, Any]] = []
    backup_name = "mtg-before-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")

    try:
        client.connect(
            hostname=host,
            port=port,
            username=username,
            password=password,
            timeout=10,
            banner_timeout=10,
            auth_timeout=10,
            look_for_keys=False,
            allow_agent=False,
        )
        if create_backup:
            backup_command = f'/system backup save name="{backup_name}"'
            _run(client, backup_command)
        for index, command in enumerate(commands):
            result = _run(client, command)
            result["index"] = index
            results.append(result)
            if not result["success"] and stop_on_error:
                break
        return {
            "ok": all(item["success"] for item in results) and len(results) == len(commands),
            "backup": backup_name if create_backup else None,
            "results": results,
            "executed": len(results),
            "total": len(commands),
        }
    finally:
        client.close()


def _run(client: paramiko.SSHClient, command: str) -> dict[str, Any]:
    try:
        _, stdout, stderr = client.exec_command(command, timeout=25)
        out = stdout.read().decode("utf-8", "replace").strip()
        err = stderr.read().decode("utf-8", "replace").strip()
        status = stdout.channel.recv_exit_status()
        combined = "\n".join(part for part in (out, err) if part).strip()
        lowered = combined.lower()
        failed_text = any(token in lowered for token in ("failure:", "syntax error", "expected end of command", "no such item"))
        success = status == 0 and not failed_text
        return {"command": command, "success": success, "output": combined or ("OK" if success else f"Exit status {status}")}
    except (socket.timeout, TimeoutError) as exc:
        return {"command": command, "success": False, "output": f"Timeout: {exc}"}
    except Exception as exc:
        return {"command": command, "success": False, "output": f"{type(exc).__name__}: {exc}"}


class Handler(BaseHTTPRequestHandler):
    server_version = "MTGAgent/1.0"

    def _cors(self) -> None:
        origin = self.headers.get("Origin", "")
        allowed = "*" if ALLOWED_ORIGIN == "*" else (origin if origin == ALLOWED_ORIGIN else "null")
        self.send_header("Access-Control-Allow-Origin", allowed)
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-MTG-Token")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Private-Network", "true")
        self.send_header("Vary", "Origin")

    def _json(self, status: int, data: dict[str, Any]) -> None:
        body = json.dumps(data).encode()
        self.send_response(status)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _authorized(self) -> bool:
        return secrets.compare_digest(self.headers.get("X-MTG-Token", ""), PAIRING_TOKEN)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self._cors()
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self) -> None:
        if self.path != "/health":
            self._json(404, {"error": "Not found"})
        elif not self._authorized():
            self._json(401, {"error": "Invalid pairing token"})
        else:
            self._json(200, {"ok": True, "platform": platform.system(), "agent": "MTG Agent 1.0"})

    def do_POST(self) -> None:
        if self.path != "/execute":
            self._json(404, {"error": "Not found"})
            return
        if not self._authorized():
            self._json(401, {"error": "Invalid pairing token"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > MAX_BODY:
                raise ValueError("Invalid request size")
            payload = json.loads(self.rfile.read(length))
            self._json(200, execute(payload))
        except (ValueError, json.JSONDecodeError) as exc:
            self._json(400, {"error": str(exc)})
        except paramiko.AuthenticationException:
            self._json(401, {"error": "Router authentication failed"})
        except Exception as exc:
            self._json(500, {"error": f"{type(exc).__name__}: {exc}"})

    def log_message(self, fmt: str, *args: Any) -> None:
        # Never log request bodies or router credentials.
        print(f"[agent] {self.address_string()} {fmt % args}")


if __name__ == "__main__":
    print("=" * 64)
    print("Hasan MikroTik Generator - Local Agent")
    print(f"Listening: http://{BIND_HOST}:{BIND_PORT}")
    print(f"Pairing token: {PAIRING_TOKEN}")
    print("Keep this terminal open. Press Ctrl+C to stop.")
    print("=" * 64)
    try:
        ThreadingHTTPServer((BIND_HOST, BIND_PORT), Handler).serve_forever()
    except KeyboardInterrupt:
        print("\nAgent stopped.")
