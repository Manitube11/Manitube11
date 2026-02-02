import requests
import base64
import re
import urllib.parse
import json

def fetch_public_configs():
    """Fetches public v2ray subscriptions from reliable sources."""
    sources = [
        "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt",
        "https://raw.githubusercontent.com/yebekhe/V2Ray-Config-Collector/main/sub/base64",
        "https://raw.githubusercontent.com/LonUp/V2Ray-Config/main/Sub1.txt",
        "https://raw.githubusercontent.com/LalatinaHub/Mineral/master/result/nodes"
    ]

    configs = []
    for url in sources:
        try:
            response = requests.get(url, timeout=10)
            content = response.text
            try:
                content = base64.b64decode(content).decode('utf-8')
            except:
                pass

            vless_links = re.findall(r'vless://[^\s]+', content)
            vmess_links = re.findall(r'vmess://[^\s]+', content)
            configs.extend(vless_links)
            configs.extend(vmess_links)
        except:
            continue
    return list(set(configs))

def parse_vless(uri):
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
    except: return None

def parse_vmess(uri):
    try:
        data = uri.replace('vmess://', '')
        decoded = base64.b64decode(data).decode('utf-8')
        return json.loads(decoded)
    except: return None

def is_suitable_config(parsed):
    """Checks if the config can be patched (WS+TLS or GRPC+TLS)."""
    if not parsed: return False
    if isinstance(parsed, dict) and 'query' in parsed: # VLESS
        q = parsed['query']
        return q.get('security') == 'tls' and q.get('type') in ['ws', 'grpc']
    if isinstance(parsed, dict) and 'net' in parsed: # VMess
        return parsed.get('tls') == 'tls' and parsed.get('net') in ['ws', 'grpc']
    return False

def patch_config(uri, clean_ip):
    """Replaces address and adds Fragment."""
    if uri.startswith('vless://'):
        parsed = parse_vless(uri)
        if not is_suitable_config(parsed): return None

        sni = parsed['query'].get('sni') or parsed['address']
        host = parsed['query'].get('host') or parsed['address']

        parsed['query']['sni'] = sni
        parsed['query']['host'] = host
        parsed['query']['fragment'] = "10-20,10-100"
        parsed['address'] = clean_ip
        parsed['remark'] = f"Fixed-{parsed['remark']} [FRAG]"

        query_str = urllib.parse.urlencode(parsed['query'])
        return f"vless://{parsed['uuid']}@{clean_ip}:{parsed['port']}?{query_str}#{urllib.parse.quote(parsed['remark'])}"

    elif uri.startswith('vmess://'):
        parsed = parse_vmess(uri)
        if not is_suitable_config(parsed): return None

        sni = parsed.get('sni') or parsed.get('add')
        host = parsed.get('host') or parsed.get('add')

        parsed['sni'] = sni
        parsed['host'] = host
        parsed['add'] = clean_ip
        parsed['fragment'] = "10-20,10-100"
        parsed['ps'] = f"Fixed-{parsed.get('ps', 'Config')} [FRAG]"

        encoded = base64.b64encode(json.dumps(parsed).encode()).decode()
        return f"vmess://{encoded}"

    return None
