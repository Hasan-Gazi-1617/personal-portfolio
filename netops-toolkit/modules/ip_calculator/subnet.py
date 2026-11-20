import ipaddress

def calculate(value):
    try:
        network = ipaddress.ip_network(value.strip(), strict=False)
    except ValueError as exc:
        raise ValueError(str(exc))
    result = {
        "Network": str(network), "IP version": f"IPv{network.version}",
        "Prefix": f"/{network.prefixlen}", "Total addresses": f"{network.num_addresses:,}",
        "First address": str(network.network_address), "Last address": str(network.broadcast_address)
    }
    if network.version == 4:
        result.update({"Netmask": str(network.netmask), "Wildcard": str(network.hostmask),
                       "Broadcast": str(network.broadcast_address),
                       "Usable hosts": f"{max(network.num_addresses - 2, 0):,}"})
    return result
