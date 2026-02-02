import requests
import base64
import re
import urllib.parse
import json

def fetch_public_configs():
    """Fetches public v2ray subscriptions from reliable sources."""
    # Sources that usually provide Cloudflare-based configs
    sources = [
        "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt",
        "https://raw.githubusercontent.com/yebekhe/V2Ray-Config-Collector/main/sub/base64",
        "https://raw.githubusercontent.com/LonUp/V2Ray-Config/main/Sub1.txt"
    ]

    configs = []
    for url in sources:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                content = response.text
                # Decode base64 if needed
                try:
                    decoded = base64.b64decode(content).decode('utf-8')
                    content = decoded
                except:
                    pass

                # Extract vless and vmess links
                vless_links = re.findall(r'vless://[^\s]+', content)
                vmess_links = re.findall(r'vmess://[^\s]+', content)
                configs.extend(vless_links)
                configs.extend(vmess_links)
        except:
            continue
    return list(set(configs))

def parse_vless(uri):
    """Parses a VLESS URI into a dictionary."""
    try:
        parts = re.match(r'vless://([^@]+)@([^:]+):(\d+)\?(.*)#(.*)', uri)
        if not parts: return None
        uuid, address, port, query_str, remark = parts.groups()
        query = dict(urllib.parse.parse_qsl(query_str))
        return {
            'type': 'vless',
            'uuid': uuid,
            'address': address,
            'port': port,
            'query': query,
            'remark': urllib.parse.unquote(remark)
        }
    except:
        return None

def parse_vmess(uri):
    """Parses a VMess URI into a dictionary."""
    try:
        data = uri.replace('vmess://', '')
        decoded = base64.b64decode(data).decode('utf-8')
        return json.loads(decoded)
    except:
        return None

def is_cloudflare_config(parsed):
    """Checks if the config is likely using Cloudflare (WS + TLS)."""
    if not parsed: return False

    # For VLESS
    if isinstance(parsed, dict) and 'query' in parsed:
        q = parsed['query']
        return q.get('type') == 'ws' and q.get('security') == 'tls'

    # For VMess
    if isinstance(parsed, dict) and 'net' in parsed:
        return parsed.get('net') == 'ws' and parsed.get('tls') == 'tls'

    return False

def patch_config(uri, clean_ip):
    """Replaces the address in a config with a clean IP."""
    if uri.startswith('vless://'):
        parsed = parse_vless(uri)
        if not is_cloudflare_config(parsed): return None

        # Original address becomes SNI/Host if not already set
        sni = parsed['query'].get('sni') or parsed['address']
        host = parsed['query'].get('host') or parsed['address']

        parsed['query']['sni'] = sni
        parsed['query']['host'] = host
        parsed['address'] = clean_ip
        parsed['remark'] = f"Fixed-{parsed['remark']}"

        query_str = urllib.parse.urlencode(parsed['query'])
        return f"vless://{parsed['uuid']}@{clean_ip}:{parsed['port']}?{query_str}#{urllib.parse.quote(parsed['remark'])}"

    elif uri.startswith('vmess://'):
        parsed = parse_vmess(uri)
        if not is_cloudflare_config(parsed): return None

        # Original address becomes SNI/Host
        sni = parsed.get('sni') or parsed.get('add')
        host = parsed.get('host') or parsed.get('add')

        parsed['sni'] = sni
        parsed['host'] = host
        parsed['add'] = clean_ip
        parsed['ps'] = f"Fixed-{parsed.get('ps', 'Config')}"

        encoded = base64.b64encode(json.dumps(parsed).encode()).decode()
        return f"vmess://{encoded}"

    return None
