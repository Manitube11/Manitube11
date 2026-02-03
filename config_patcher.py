import requests
import base64
import re
import urllib.parse
import json
import random

def fetch_public_configs():
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
            try: content = base64.b64decode(content).decode('utf-8')
            except: pass

            found = re.findall(r'(vless|vmess|trojan)://[^\s]+', content)
            for f in found:
                link = re.search(rf'{f}://[^\s]+', content)
                if link: configs.append(link.group(0))
        except: continue

    return list(set(configs))

def parse_vless(uri):
    try:
        # Improved regex to handle configs without ? or #
        match = re.match(r'vless://([^@]+)@([^:]+):(\d+)(\?[^#]*)?(#.*)?', uri)
        if not match: return None
        uuid, address, port, query_str, remark = match.groups()
        query = dict(urllib.parse.parse_qsl(query_str.lstrip('?'))) if query_str else {}
        return {
            'type': 'vless', 'uuid': uuid, 'address': address, 'port': port,
            'query': query, 'remark': urllib.parse.unquote(remark.lstrip('#')) if remark else ""
        }
    except: return None

def parse_vmess(uri):
    try:
        data = uri.replace('vmess://', '')
        missing_padding = len(data) % 4
        if missing_padding: data += '=' * (4 - missing_padding)
        return json.loads(base64.b64decode(data).decode('utf-8'))
    except: return None

def patch_config(uri, clean_ip, force_sni=None):
    """Advanced patcher implementing the 'Paid Config' patterns."""
    if uri.startswith('vless://'):
        parsed = parse_vless(uri)
        if not parsed: return None

        # Pattern 1: Domain Fronting (TLS + Clean SNI)
        # Pattern 2: HTTP Spoofing (No TLS + Host Header)

        old_addr = parsed['address']
        parsed['address'] = clean_ip

        query = parsed['query']
        if query.get('security') == 'tls':
            query['sni'] = force_sni if force_sni else (query.get('sni') or old_addr)
            query['host'] = force_sni if force_sni else (query.get('host') or old_addr)
        else:
            # For non-TLS, we use HTTP Header Spoofing like the user's example
            query['type'] = 'tcp'
            query['headerType'] = 'http'
            query['host'] = "skyroom.online,gharar.ir,igap.net"

        query['fragment'] = f"{random.randint(10,30)}-{random.randint(40,100)},{random.randint(5,15)}-{random.randint(20,50)}"

        query_str = urllib.parse.urlencode(query)
        remark = f"Fixed-{parsed['remark']} [IR-Pattern]"
        return f"vless://{parsed['uuid']}@{clean_ip}:{parsed['port']}?{query_str}#{urllib.parse.quote(remark)}"

    elif uri.startswith('vmess://'):
        parsed = parse_vmess(uri)
        if not parsed: return None

        old_addr = parsed.get('add')
        parsed['add'] = clean_ip

        if parsed.get('tls') == 'tls':
            parsed['sni'] = force_sni if force_sni else (parsed.get('sni') or old_addr)
            parsed['host'] = force_sni if force_sni else (parsed.get('host') or old_addr)
        else:
            parsed['net'] = 'tcp'
            parsed['type'] = 'http'
            parsed['host'] = "skyroom.online,gharar.ir,igap.net"

        parsed['ps'] = f"Fixed-{parsed.get('ps', 'Config')} [IR-Pattern]"

        encoded = base64.b64encode(json.dumps(parsed).encode()).decode()
        return f"vmess://{encoded}"

    return None
