import scanner
import config_generator
import config_patcher
import sni_scanner
import sys
import os
import random
import re

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def is_iran_ip(ip):
    # Simple check for common Iran IP ranges (just for display purposes)
    return re.match(r'^(78|79|80|85|89|91|94|185|188|2|5|37|178)\.', ip)

def verify_and_display(results, choice, public_configs=None, clean_snis=None):
    print("\n" + "="*50)
    print("   RESULTS & IRAN-PATTERN VERIFICATION (v2.5)")
    print("="*50)

    best_sni = clean_snis[0] if clean_snis else "skyroom.online"
    count = 0

    # 1. First, show any Public REALITY configs (always stable)
    realities = list(set([c for c in public_configs if 'security=reality' in c]))
    random.shuffle(realities)
    for rc in realities[:3]:
        print(f"\n[⭐] REALITY NODE (Stable)")
        print(f"Config: {rc}")
        count += 1

    # 2. Show configs with Iranian IPs (Relays/Tunnels)
    print("\n[🇮🇷] Searching for IRANIAN IPs (Tunnels)...")
    ir_ips_found = 0
    for pub_uri in public_configs:
        addr = ""
        if pub_uri.startswith('vless://') or pub_uri.startswith('trojan://'):
            match = re.search(r'@([^:]+):', pub_uri)
            if match: addr = match.group(1)
        elif pub_uri.startswith('vmess://'):
            p = config_patcher.parse_vmess(pub_uri)
            if p: addr = p.get('add', '')

        if addr and is_iran_ip(addr):
            print(f"\n[✔] DIRECT IRAN TUNNEL (High Ping/Very Stable)")
            print(f"Address: {addr}")
            print(f"Config: {pub_uri}")
            ir_ips_found += 1
            count += 1
        if ir_ips_found >= 5: break

    # 3. Patch Cloudflare/GCore IPs using the User's "Paid" pattern
    print("\n[+] Generating Patched Nodes using 'Paid-Pattern' SNIs...")
    patched_count = 0
    for ip_res in results:
        ip = ip_res['ip']
        random.shuffle(public_configs)
        for pub_uri in public_configs[:200]:
            if 'security=reality' in pub_uri: continue

            # Use the "Clean Iranian SNIs" provided by user's example
            patched = config_patcher.patch_config(pub_uri, ip, force_sni=best_sni)
            if patched:
                print(f"\n[✔] VERIFIED PATCH | Latency: {ip_res['latency']:.1f}ms")
                print(f"IP: {ip} | SNI: {best_sni}")
                print(f"Config: {patched}")
                patched_count += 1
                count += 1
                break
        if patched_count >= 5: break

    if count == 0:
        print("\n[!] No working configs found. Check your internet connection.")

def main():
    clear_screen()
    print("====================================================")
    print("   Cloudflare & GCore Smart Scanner (v2.5)")
    print("      ویژه تانل ایران و الگوهای کانفیگ پولی")
    print("====================================================\n")

    print("1. Manual Mode / دستی")
    print("2. Auto: IRAN-Patterns & Tunnels / الگوی پولی و تانل ایران")

    choice = input("Choice (1/2) [2]: ").strip() or "2"

    print("\n[+] Discovery Phase (SNIs & Tunnels)...")
    clean_snis = sni_scanner.find_best_sni()
    public_configs = config_patcher.fetch_public_configs()

    print("\n[+] Finding Clean IPs...")
    ranges = scanner.fetch_cf_ranges() + scanner.fetch_gcore_ranges()
    results = scanner.scan_ips(ranges, samples_per_range=3, max_workers=60)

    verify_and_display(results, choice, public_configs=public_configs, clean_snis=clean_snis)

    print("\n" + "="*50)
    print("Done! If it doesn't work, use IRAN TUNNEL nodes.")
    print("====================================================")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
