import requests
import base64
import re
import urllib.parse
import json
import random

def fetch_public_configs():
    """Fetches public v2ray subscriptions, prioritizing potential Iran bridges/relays."""
    sources = [
        "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt",
        "https://raw.githubusercontent.com/yebekhe/V2Ray-Config-Collector/main/sub/base64",
        "https://raw.githubusercontent.com/LonUp/V2Ray-Config/main/Sub1.txt",
        "https://raw.githubusercontent.com/LalatinaHub/Mineral/master/result/nodes",
        "https://raw.githubusercontent.com/IranianStuff/FreeV2rayConfig/main/Sub1.txt"
    ]

    configs = []
    for url in sources:
        try:
            response = requests.get(url, timeout=10)
            content = response.text
            try:
                # Some sources are base64 encoded
                content = base64.b64decode(content).decode('utf-8')
            except:
                pass

            # Extract links
            vless_links = re.findall(r'vless://[^\s]+', content)
            vmess_links = re.findall(r'vmess://[^\s]+', content)
            configs.extend(vless_links)
            configs.extend(vmess_links)
        except:
            continue

    # Prioritize configs that might be Iran Relays (contain IR, Iran, Bridge, Tunnel)
    prioritized = []
    others = []
    keywords = ['IR', 'Iran', 'Bridge', 'Tunnel', 'Relay', 'MCI', 'Irancell']

    for c in configs:
        if any(kw.lower() in c.lower() for kw in keywords):
            prioritized.append(c)
        else:
            others.append(c)

    return prioritized + others

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
        # Handle padded base64
        missing_padding = len(data) % 4
        if missing_padding:
            data += '=' * (4 - missing_padding)
        decoded = base64.b64decode(data).decode('utf-8')
        return json.loads(decoded)
    except: return None

def generate_random_fragment():
    """Generates a random fragment string for DPI bypass."""
    # Format: packets_count-packets_count,length-length
    return f"{random.randint(10,30)}-{random.randint(40,100)},{random.randint(5,15)}-{random.randint(20,50)}"

def patch_config(uri, clean_ip, force_sni=None):
    """Replaces address, adds random Fragment and optionally forces a clean SNI."""
    if uri.startswith('vless://'):
        parsed = parse_vless(uri)
        if not parsed: return None

        # Determine SNI and Host
        sni = force_sni if force_sni else (parsed['query'].get('sni') or parsed['address'])
        host = parsed['query'].get('host') or parsed['address']

        parsed['query']['sni'] = sni
        parsed['query']['host'] = host
        parsed['query']['fragment'] = generate_random_fragment()
        parsed['address'] = clean_ip
        parsed['remark'] = f"Fixed-{parsed['remark']} [TUNNEL]"

        query_str = urllib.parse.urlencode(parsed['query'])
        return f"vless://{parsed['uuid']}@{clean_ip}:{parsed['port']}?{query_str}#{urllib.parse.quote(parsed['remark'])}"

    elif uri.startswith('vmess://'):
        parsed = parse_vmess(uri)
        if not parsed: return None

        sni = force_sni if force_sni else (parsed.get('sni') or parsed.get('add'))
        host = parsed.get('host') or parsed.get('add')

        parsed['sni'] = sni
        parsed['host'] = host
        parsed['add'] = clean_ip
        parsed['fragment'] = generate_random_fragment()
        parsed['ps'] = f"Fixed-{parsed.get('ps', 'Config')} [TUNNEL]"

        encoded = base64.b64encode(json.dumps(parsed).encode()).decode()
        return f"vmess://{encoded}"

    return None
