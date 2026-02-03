import requests
import base64
import re
import urllib.parse
import json
import random

def fetch_public_configs():
    """Fetches configs, with a strong focus on REALITY and IRAN RELAYS."""
    sources = [
        "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge.txt",
        "https://raw.githubusercontent.com/yebekhe/V2Ray-Config-Collector/main/sub/base64",
        "https://raw.githubusercontent.com/LonUp/V2Ray-Config/main/Sub1.txt",
        "https://raw.githubusercontent.com/LalatinaHub/Mineral/master/result/nodes",
        "https://raw.githubusercontent.com/IranianStuff/FreeV2rayConfig/main/Sub1.txt",
        "https://raw.githubusercontent.com/SreN-98/V2ray-Configs/main/All_Configs_Sub.txt"
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

            # Support VLESS, VMess, and TROJAN
            found = re.findall(r'(vless|vmess|trojan)://[^\s]+', content)
            for f in found:
                # Reconstruct the link correctly
                link = re.search(rf'{f}://[^\s]+', content)
                if link: configs.append(link.group(0))
        except:
            continue

    # PRIORITY 1: Iran Relays / Bridges (Addrs that look like Iran IPs or have IR in PS)
    # PRIORITY 2: Reality configs
    # PRIORITY 3: Cloudflare Workers

    prioritized = []
    others = []

    ir_keywords = ['IR', 'Iran', 'Bridge', 'Tunnel', 'Relay', 'MCI', 'Irancell', 'Asiatech', 'Arvan']

    for c in configs:
        is_prio = False
        if 'security=reality' in c:
            is_prio = True
        elif any(kw.lower() in c.lower() for kw in ir_keywords):
            is_prio = True

        if is_prio:
            prioritized.append(c)
        else:
            others.append(c)

    return prioritized + others

def parse_vmess(uri):
    try:
        data = uri.replace('vmess://', '')
        missing_padding = len(data) % 4
        if missing_padding:
            data += '=' * (4 - missing_padding)
        decoded = base64.b64decode(data).decode('utf-8')
        return json.loads(decoded)
    except: return None

def patch_config(uri, clean_ip, force_sni=None):
    """Refined patcher for v2.4."""
    if uri.startswith('vless://') or uri.startswith('trojan://'):
        # For Reality configs, we DO NOT replace the address with Cloudflare IPs
        # Reality needs to connect to the specific destination server
        if 'security=reality' in uri:
            return uri # Reality is usually good as is

        # For others (WS/GRPC), use Cloudflare clean IP
        parts = re.split(r'[?#]', uri)
        base = parts[0]
        query_str = parts[1] if len(parts) > 1 else ""
        remark = parts[2] if len(parts) > 2 else "Config"

        # Replace address
        match = re.match(r'(.*)@([^:]+):(\d+)', base)
        if match:
            proto_uuid, old_addr, port = match.groups()
            new_base = f"{proto_uuid}@{clean_ip}:{port}"

            query = dict(urllib.parse.parse_qsl(query_str))
            # Important: Keep old address as SNI/Host
            if not query.get('sni'): query['sni'] = old_addr
            if not query.get('host'): query['host'] = old_addr
            if force_sni: query['sni'] = force_sni

            query['fragment'] = f"{random.randint(10,30)}-{random.randint(40,100)},{random.randint(5,15)}-{random.randint(20,50)}"

            new_query = urllib.parse.urlencode(query)
            return f"{new_base}?{new_query}#{remark}"

    elif uri.startswith('vmess://'):
        parsed = parse_vmess(uri)
        if not parsed: return None

        # Don't touch Reality or non-WS/GRPC if possible, but VMess is usually WS
        old_addr = parsed.get('add')
        parsed['add'] = clean_ip
        if not parsed.get('sni'): parsed['sni'] = old_addr
        if not parsed.get('host'): parsed['host'] = old_addr
        if force_sni: parsed['sni'] = force_sni

        # FIX: type should be 'none' for WS, not 'auto'
        if parsed.get('net') == 'ws':
            parsed['type'] = 'none'

        parsed['fragment'] = f"{random.randint(10,30)}-{random.randint(40,100)},{random.randint(5,15)}-{random.randint(20,50)}"

        encoded = base64.b64encode(json.dumps(parsed).encode()).decode()
        return f"vmess://{encoded}"

    return None
