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
        "https://raw.githubusercontent.com/IranianStuff/FreeV2rayConfig/main/Sub1.txt",
        "https://raw.githubusercontent.com/SreN-98/V2ray-Configs/main/All_Configs_Sub.txt",
        "https://raw.githubusercontent.com/vfarid/v2ray-worker-sub/master/sub/base64"
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

def is_iran_ip(ip):
    iran_prefixes = ('2.144', '2.176', '2.180', '2.184', '2.188', '5.1', '31.2', '31.5', '37.2', '37.3', '46.1', '46.2', '78.3', '78.1', '79.1', '80.1', '85.1', '87.1', '89.1', '91.9', '94.1', '151.2', '158.5', '176.1', '178.2', '185.8', '185.1', '188.1', '217.2')
    return ip.startswith(iran_prefixes)

def patch_config(uri, clean_ip, force_sni=None):
    is_ir = is_iran_ip(clean_ip)

    if uri.startswith('vless://') or uri.startswith('trojan://'):
        if 'security=reality' in uri: return uri

        parts = re.split(r'[?#]', uri)
        base = parts[0]
        query_str = parts[1] if len(parts) > 1 else ""
        remark = parts[2] if len(parts) > 2 else "Node"

        match = re.match(r'(.*)@([^:]+):(\d+)', base)
        if not match: return None
        proto_uuid, old_addr, port = match.groups()
        query = dict(urllib.parse.parse_qsl(query_str))

        # Identify original domain
        original_domain = query.get('host') or query.get('sni') or (old_addr if not re.match(r'^\d', old_addr) else None)

        if is_ir:
            query['security'] = 'none'
            query['type'] = 'tcp'
            query['headerType'] = 'http'
            query['host'] = "skyroom.online,gharar.ir,igap.net"
            query.pop('sni', None)
        else:
            query['security'] = 'tls'
            query['sni'] = force_sni if force_sni else (original_domain or old_addr)
            query['host'] = original_domain if original_domain else old_addr
            query['fp'] = 'chrome'
            query['alpn'] = 'h2,http/1.1'
            query['allowInsecure'] = '1' # CRITICAL for SNI spoofing
            query['insecure'] = '1'
            query['fragment'] = f"{random.randint(10,30)}-{random.randint(40,100)},{random.randint(5,15)}-{random.randint(20,50)}"
            if port in ['80', '8080', '8880', '2052', '2082', '2086', '2095']: port = '443'

        new_base = f"{proto_uuid}@{clean_ip}:{port}"
        new_query = urllib.parse.urlencode(query)
        return f"{new_base}?{new_query}#{urllib.parse.quote(f'Fixed-{remark}')}"

    elif uri.startswith('vmess://'):
        try:
            data = uri.replace('vmess://', '')
            missing_padding = len(data) % 4
            if missing_padding: data += '=' * (4 - missing_padding)
            parsed = json.loads(base64.b64decode(data).decode('utf-8'))
        except: return None

        old_addr = parsed.get('add')
        parsed['add'] = clean_ip

        # Identify original domain
        original_domain = parsed.get('host') or parsed.get('sni') or (old_addr if not re.match(r'^\d', old_addr) else None)

        if is_ir:
            parsed['tls'] = ""
            parsed['net'] = 'tcp'
            parsed['type'] = 'http'
            parsed['host'] = "skyroom.online,gharar.ir,igap.net"
        else:
            parsed['tls'] = "tls"
            parsed['sni'] = force_sni if force_sni else (original_domain or old_addr)
            parsed['host'] = original_domain if original_domain else (parsed.get('host') or old_addr)
            parsed['fp'] = 'chrome'
            parsed['skip-cert-verify'] = True # CRITICAL for SNI spoofing
            if parsed.get('net') == 'ws': parsed['type'] = 'none'
            parsed['fragment'] = f"{random.randint(10,30)}-{random.randint(40,100)},{random.randint(5,15)}-{random.randint(20,50)}"
            if str(parsed.get('port')) in ['80', '8080', '2086']: parsed['port'] = 443

        encoded = base64.b64encode(json.dumps(parsed).encode()).decode()
        return f"vmess://{encoded}"

    return None

def parse_vmess(uri):
    try:
        data = uri.replace('vmess://', '')
        missing_padding = len(data) % 4
        if missing_padding: data += '=' * (4 - missing_padding)
        return json.loads(base64.b64decode(data).decode('utf-8'))
    except: return None
