import platform
import socket
import psutil

def snapshot():
    try:
        local_ip = socket.gethostbyname(socket.gethostname())
    except OSError:
        local_ip = "Unavailable"
    interfaces = []
    for name, addresses in psutil.net_if_addrs().items():
        ipv4 = [a.address for a in addresses if a.family == socket.AF_INET]
        mac = [a.address for a in addresses if getattr(psutil, "AF_LINK", None) == a.family]
        if ipv4 or mac:
            interfaces.append({"name": name, "ipv4": ", ".join(ipv4) or "-", "mac": ", ".join(mac) or "-"})
    return {"hostname": socket.gethostname(), "ip": local_ip, "os": f"{platform.system()} {platform.release()}", "interfaces": interfaces}
