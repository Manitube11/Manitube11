import base64
import json
import urllib.parse

def generate_vless_uri(ip, port, uuid, host, path, sni, remark):
    """Generates a VLESS over WebSocket + TLS URI."""
    params = {
        "encryption": "none",
        "security": "tls",
        "sni": sni,
        "type": "ws",
        "host": host,
        "path": path
    }
    query = urllib.parse.urlencode(params)
    uri = f"vless://{uuid}@{ip}:{port}?{query}#{urllib.parse.quote(remark)}"
    return uri

def generate_vmess_uri(ip, port, uuid, host, path, sni, remark):
    """Generates a VMess over WebSocket + TLS URI."""
    config = {
        "v": "2",
        "ps": remark,
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
        "alpn": ""
    }
    json_config = json.dumps(config)
    encoded_config = base64.b64encode(json_config.encode()).decode()
    return f"vmess://{encoded_config}"

if __name__ == "__main__":
    # Test generation
    ip = "1.1.1.1"
    port = 443
    uuid = "00000000-0000-0000-0000-000000000000"
    host = "example.com"
    path = "/graphql"
    sni = "example.com"
    remark = "Test Config"

    vless = generate_vless_uri(ip, port, uuid, host, path, sni, remark)
    vmess = generate_vmess_uri(ip, port, uuid, host, path, sni, remark)

    print(f"VLESS: {vless}")
    print(f"VMess: {vmess}")

    if vless.startswith("vless://") and vmess.startswith("vmess://"):
        print("\nVerification: Success - Correct prefixes found.")
    else:
        print("\nVerification: Failed - Incorrect prefixes.")
