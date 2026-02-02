import base64
import json
import urllib.parse

def generate_vless_uri(ip, port, uuid, host, path, sni, remark):
    """Generates a VLESS URI with Fragment hint."""
    params = {
        "encryption": "none",
        "security": "tls",
        "sni": sni,
        "type": "ws",
        "host": host,
        "path": path,
        "fragment": "10-20,10-100" # Adding fragment hint
    }
    query = urllib.parse.urlencode(params)
    uri = f"vless://{uuid}@{ip}:{port}?{query}#{urllib.parse.quote(remark + ' [FRAG]')}"
    return uri

def generate_vmess_uri(ip, port, uuid, host, path, sni, remark):
    """Generates a VMess URI with Fragment support."""
    config = {
        "v": "2",
        "ps": remark + " [FRAG]",
        "add": ip,
        "port": str(port),
        "id": uuid,
        "aid": "0",
        "scy": "auto",
        "net": "ws",
        "type": "none",
        "host": host,
        "path": path,
        "tls": "tls",
        "sni": sni,
        "fragment": "10-20,10-100" # Common fragment setting for Iran
    }
    json_config = json.dumps(config)
    encoded_config = base64.b64encode(json_config.encode()).decode()
    return f"vmess://{encoded_config}"
