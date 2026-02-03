import socket
import ssl
import time
import concurrent.futures

# List of SNIs that are often unblocked in Iran
COMMON_SNIS = [
    "www.google.com", "www.microsoft.com", "www.samsung.com",
    "www.skype.com", "www.wikipedia.org", "www.bing.com",
    "www.digikala.com", "www.snapp.ir", "www.telewebion.com",
    "www.aparat.com", "www.shatelland.com", "www.soft98.ir"
]

def test_sni_connectivity(sni, timeout=2.0):
    """Tests if a specific SNI is blocked on the current network."""
    # We use a known stable IP (Cloudflare 1.1.1.1 or Google 8.8.8.8)
    # just to see if the SNI handshake passes through the ISP's DPI.
    test_ips = ["1.1.1.1", "1.0.0.1", "172.67.13.1", "104.16.132.229"]

    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    for ip in test_ips:
        try:
            with socket.create_connection((ip, 443), timeout=timeout) as sock:
                with context.wrap_socket(sock, server_hostname=sni) as ssock:
                    return True
        except Exception:
            continue
    return False

def find_best_sni(max_workers=10):
    """Scans a list of SNIs to find which ones are open on the user's ISP."""
    print(f"[+] Scanning {len(COMMON_SNIS)} common domains to find an unblocked SNI...")
    clean_snis = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_sni = {executor.submit(test_sni_connectivity, sni): sni for sni in COMMON_SNIS}
        for future in concurrent.futures.as_completed(future_to_sni):
            sni = future_to_sni[future]
            if future.result():
                clean_snis.append(sni)
                print(f"    [OK] {sni} is open.")
    return clean_snis
