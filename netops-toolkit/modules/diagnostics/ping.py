import platform
import re
import subprocess


def ping(host, count=4, family="Auto"):
    host = host.strip()
    if not host or len(host) > 253 or re.fullmatch(r"[A-Za-z0-9._:%-]+", host) is None:
        raise ValueError("Enter a valid hostname or IP address.")
    count = max(1, min(int(count), 1000))
    family_flag = {"IPv4": "-4", "IPv6": "-6"}.get(family, "")
    if platform.system() == "Windows":
        command = ["ping"]
        if family_flag:
            command.append(family_flag)
        command.extend(["-n", str(count), "-w", "2000", host])
    else:
        command = ["ping"]
        if family_flag:
            command.append(family_flag)
        command.extend(["-c", str(count), "-W", "2", host])
    result = subprocess.run(
        command, capture_output=True, text=True, timeout=min(count * 3 + 10, 301)
    )
    return (result.stdout + result.stderr).strip() or f"Ping exited with code {result.returncode}."
