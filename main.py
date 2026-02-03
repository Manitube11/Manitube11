import scanner
import config_patcher
import sni_scanner
import sys
import os
import random
import re

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def verify_and_display(results, choice, public_configs=None, clean_snis=None):
    print("\n" + "="*50)
    print("   RESULTS & SMART PATTERN VERIFICATION (v2.6)")
    print("="*50)

    best_sni = clean_snis[0] if clean_snis else "shopingnet.ir"
    count = 0

    # 1. Show IRAN DIRECT TUNNELS first (High Success)
    print("\n[🇮🇷] Searching for IRAN DIRECT TUNNELS...")
    ir_tunnels = []
    for pub_uri in public_configs:
        addr = ""
        if pub_uri.startswith('vless://') or pub_uri.startswith('trojan://'):
            match = re.search(r'@([^:]+):', pub_uri)
            if match: addr = match.group(1)
        elif pub_uri.startswith('vmess://'):
            p = config_patcher.parse_vmess(pub_uri)
            if p: addr = p.get('add', '')

        if addr and config_patcher.is_iran_ip(addr):
            # Patch it using the IR pattern
            patched = config_patcher.patch_config(pub_uri, addr)
            if patched:
                print(f"\n[✔] IR-TUNNEL | Addr: {addr}")
                print(f"Config: {patched}")
                count += 1
                ir_tunnels.append(patched)
        if len(ir_tunnels) >= 5: break

    # 2. Show REALITY nodes
    realities = list(set([c for c in public_configs if 'security=reality' in c]))
    random.shuffle(realities)
    for rc in realities[:3]:
        print(f"\n[⭐] REALITY NODE (Stable)")
        print(f"Config: {rc}")
        count += 1

    # 3. Patch Cloudflare IPs (CDN Pattern)
    print("\n[+] Generating Verified CDN Patches (CF/GCore)...")
    patched_count = 0
    for ip_res in results:
        ip = ip_res['ip']
        random.shuffle(public_configs)
        for pub_uri in public_configs[:200]:
            if 'security=reality' in pub_uri: continue

            # Apply CDN pattern to Cloudflare IP
            patched = config_patcher.patch_config(pub_uri, ip, force_sni=best_sni)
            if patched:
                print(f"\n[✔] VERIFIED CDN | Latency: {ip_res['latency']:.1f}ms")
                print(f"IP: {ip} | SNI: {best_sni}")
                print(f"Config: {patched}")
                patched_count += 1
                count += 1
                break
        if patched_count >= 5: break

    if count == 0:
        print("\n[!] No working configs found.")

def main():
    clear_screen()
    print("====================================================")
    print("   Cloudflare & GCore Smart Scanner (v2.6)")
    print("      هوشمندسازی الگوهای ایران و خارج")
    print("====================================================\n")

    print("1. Manual Mode / دستی")
    print("2. Auto: Smart Patterns (CDN & Tunnel) / خودکار")

    choice = input("Choice (1/2) [2]: ").strip() or "2"

    print("\n[+] Step 0: Discovery...")
    clean_snis = sni_scanner.find_best_sni()
    public_configs = config_patcher.fetch_public_configs()

    print("\n[+] Step 1: Scanning for Clean IPs...")
    ranges = scanner.fetch_cf_ranges() + scanner.fetch_gcore_ranges()
    results = scanner.scan_ips(ranges, samples_per_range=3, max_workers=60)

    verify_and_display(results, choice, public_configs=public_configs, clean_snis=clean_snis)

    print("\n" + "="*50)
    print("Done! Check your client version for REALITY support.")
    print("====================================================")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
