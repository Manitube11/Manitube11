import socket
import ssl
import time
import concurrent.futures

# The user provided these working domains
COMMON_SNIS = [
    "skyroom.online", "gharar.ir", "igap.net", "shopingnet.ir",
    "www.telewebion.com", "www.aparat.com", "snapp.ir", "digikala.com"
]

def test_sni_connectivity(sni, timeout=2.0):
    # Testing against multiple IPs to ensure the SNI itself is not blocked
    test_ips = ["1.1.1.1", "172.67.13.1", "104.16.132.229", "8.8.8.8"]

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
    print(f"[+] Testing White-listed Iranian domains...")
    clean_snis = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_sni = {executor.submit(test_sni_connectivity, sni): sni for sni in COMMON_SNIS}
        for future in concurrent.futures.as_completed(future_to_sni):
            sni = future_to_sni[future]
            if future.result():
                clean_snis.append(sni)
                print(f"    [✔] {sni} is verified as OPEN.")
    return clean_snis
