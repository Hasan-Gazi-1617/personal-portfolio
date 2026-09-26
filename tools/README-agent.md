# MikroTik Local Agent

This optional agent gives the web generator real line-by-line RouterOS execution results.

## Supported platforms

- Windows 10/11
- Linux
- macOS
- Python 3.10 or newer
- RouterOS v6 or v7 with SSH enabled

## Start

```bash
python -m pip install -r tools/requirements-agent.txt
python tools/mikrotik_agent.py
```

Copy the printed pairing token into the generator. The agent listens only on `127.0.0.1:8765`.

Optional environment variables:

- `MTG_AGENT_TOKEN`: use a fixed pairing token
- `MTG_AGENT_PORT`: change the local port
- `MTG_ALLOWED_ORIGIN`: restrict browser access to the deployed portfolio origin

## Safety

- Review the generated commands before execution.
- Test on a lab router first.
- The agent requests a timestamped RouterOS backup before configuration.
- Router credentials are used only for the current SSH session and are not written to disk.
- The agent stops on the first failed command by default.
