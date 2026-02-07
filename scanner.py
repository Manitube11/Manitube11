import socket
import threading
import concurrent.futures
import requests
import ipaddress
import random
import time
import urllib3
import ssl

# Suppress insecure request warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_cf_ranges():
    """Fetches Cloudflare IPv4 ranges."""
    url = "https://www.cloudflare.com/ips-v4"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.text.strip().split('\n')
    except:
        return ["173.245.48.0/20", "103.21.244.0/22", "103.22.200.0/22", "103.31.4.0/22", "141.101.64.0/18", "108.162.192.0/18", "190.93.240.0/20", "188.114.96.0/20", "197.234.240.0/22", "198.41.128.0/17", "162.158.0.0/15", "104.16.0.0/13", "104.24.0.0/14", "172.64.0.0/13", "131.0.72.0/22"]

def fetch_gcore_ranges():
    """Fetches Gcore IPv4 ranges."""
    try:
        response = requests.get("https://api.gcore.com/cdn/ips", timeout=5)
        return response.json().get('ipv4', [])
    except:
        return ["92.223.64.0/18", "95.161.192.0/20"]

def test_tls_handshake(ip, sni, port=443, timeout=2.0):
    """Performs a real TLS handshake to verify if the SNI is blocked on this IP."""
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    start_time = time.time()
    try:
        with socket.create_connection((ip, port), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=sni) as ssock:
                latency = (time.time() - start_time) * 1000
                # If we reached here, the handshake succeeded!
                return True, latency
    except Exception:
        return False, None

def scan_ips(ranges, samples_per_range=5, max_workers=50, sni_to_check="www.cloudflare.com"):
    """Scans IPs with real TLS handshake checks."""
    ips_to_scan = []
    for r in ranges:
        try:
            net = ipaddress.ip_network(r)
            num_ips = net.num_addresses
            if num_ips > samples_per_range:
                indices = random.sample(range(num_ips), samples_per_range)
                for idx in indices:
                    ips_to_scan.append(str(net[idx]))
            else:
                for ip in net:
                    ips_to_scan.append(str(ip))
        except:
            continue

    print(f"Scanning {len(ips_to_scan)} IPs with TLS handshake (SNI: {sni_to_check})...")

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_ip = {executor.submit(test_tls_handshake, ip, sni_to_check): ip for ip in ips_to_scan}
        for future in concurrent.futures.as_completed(future_to_ip):
            ip = future_to_ip[future]
            success, latency = future.result()
            if success:
                results.append({'ip': ip, 'latency': latency})
                print(f"Clean (TLS OK): {ip} - {latency:.2f}ms")

    results.sort(key=lambda x: x['latency'])
    return results

if __name__ == "__main__":
    ranges = fetch_cf_ranges()[:2]
    print(scan_ips(ranges, samples_per_range=2))
