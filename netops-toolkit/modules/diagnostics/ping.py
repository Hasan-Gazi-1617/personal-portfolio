import platform
import re
import subprocess

def ping(host, count=4):
    host = host.strip()
    if not host or len(host) > 253 or re.fullmatch(r"[A-Za-z0-9._:%-]+", host) is None:
        raise ValueError("Enter a valid hostname or IP address.")
    count = max(1, min(int(count), 20))
    command = (["ping", "-n", str(count), "-w", "2000", host] if platform.system() == "Windows"
               else ["ping", "-c", str(count), "-W", "2", host])
    result = subprocess.run(command, capture_output=True, text=True, timeout=count * 4 + 5)
    return (result.stdout + result.stderr).strip() or f"Ping exited with code {result.returncode}."
