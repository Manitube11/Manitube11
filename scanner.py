import socket
import threading
import concurrent.futures
import requests
import ipaddress
import random
import time
import urllib3

# Suppress insecure request warnings for Host check
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_cf_ranges():
    """Fetches Cloudflare IPv4 ranges from the official source."""
    url = "https://www.cloudflare.com/ips-v4"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text.strip().split('\n')
    except Exception as e:
        print(f"Error fetching ranges: {e}")
        # Fallback to a hardcoded list if fetch fails
        return [
            "173.245.48.0/20", "103.21.244.0/22", "103.22.200.0/22",
            "103.31.4.0/22", "141.101.64.0/18", "108.162.192.0/18",
            "190.93.240.0/20", "188.114.96.0/20", "197.234.240.0/22",
            "198.41.128.0/17", "162.158.0.0/15", "104.16.0.0/13",
            "104.24.0.0/14", "172.64.0.0/13", "131.0.72.0/22"
        ]

def test_tcp_latency(ip, port=443, timeout=1.0):
    """Tests TCP connectivity and measures latency."""
    start_time = time.time()
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((str(ip), port))
        sock.close()
        latency = (time.time() - start_time) * 1000
        return True, latency
    except Exception:
        return False, None

def check_host(ip, host, timeout=2.0):
    """Checks if the IP can reach a specific host via HTTPS."""
    url = f"https://{ip}/"
    headers = {'Host': host}
    try:
        # verify=False is needed because we connect to IP, not the hostname in the cert
        response = requests.get(url, headers=headers, timeout=timeout, verify=False)
        # Usually any response from Cloudflare (even 403/404) means the IP is reachable
        return True, response.status_code
    except Exception:
        return False, None

def scan_ips(ranges, samples_per_range=5, max_workers=50, host_to_check=None):
    """Scans a subset of IPs from each range."""
    ips_to_scan = []
    for r in ranges:
        try:
            net = ipaddress.ip_network(r)
            # Pick random IPs from the range
            num_ips = net.num_addresses
            if num_ips > samples_per_range:
                # Random sample
                indices = random.sample(range(num_ips), samples_per_range)
                for idx in indices:
                    ips_to_scan.append(str(net[idx]))
            else:
                for ip in net:
                    ips_to_scan.append(str(ip))
        except Exception:
            continue

    print(f"Scanning {len(ips_to_scan)} IPs...")

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_ip = {executor.submit(test_tcp_latency, ip): ip for ip in ips_to_scan}
        for future in concurrent.futures.as_completed(future_to_ip):
            ip = future_to_ip[future]
            success, latency = future.result()
            if success:
                h_ok = True
                h_status = None
                if host_to_check:
                    h_ok, h_status = check_host(ip, host_to_check)

                if h_ok:
                    results.append({'ip': ip, 'latency': latency, 'status': h_status})
                    print(f"Found clean IP: {ip} - Latency: {latency:.2f}ms")

    # Sort by latency
    results.sort(key=lambda x: x['latency'])
    return results

if __name__ == "__main__":
    ranges = fetch_cf_ranges()
    # Test run with small sample from more ranges
    top_ips = scan_ips(ranges[:5], samples_per_range=3, max_workers=20)
    print("\nTop IPs:")
    for res in top_ips[:5]:
        print(res)
