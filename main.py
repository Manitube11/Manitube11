import scanner
import config_generator
import config_patcher
import sni_scanner
import sys
import os
import random

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def verify_and_display(results, choice, public_configs=None, clean_snis=None):
    print("\n" + "="*50)
    print("   RESULTS & DEEP VERIFICATION (v2.4)")
    print("="*50)

    best_sni = clean_snis[0] if clean_snis else None
    count = 0

    if choice == "2":
        # 1. REALITY NODES
        realities = list(set([c for c in public_configs if 'security=reality' in c]))
        random.shuffle(realities)
        for rc in realities[:4]:
            print(f"\n[⭐] REALITY NODE (Stable/بدون فیلتر)")
            print(f"Config: {rc}")
            count += 1

        # 2. IRAN RELAYS
        ir_relays = list(set([c for c in public_configs if any(kw.lower() in c.lower() for kw in ['IR', 'Iran', 'Bridge', 'Tunnel', 'Relay'])]))
        random.shuffle(ir_relays)
        for ic in ir_relays[:4]:
            print(f"\n[🇮🇷] IRAN TUNNEL (Relay/تانل شده)")
            print(f"Config: {ic}")
            count += 1

    # 3. PATCHED NODES (Only if we have clean IPs)
    print("\n[+] Generating Verified Patched Nodes...")
    patched_count = 0
    for ip_res in results:
        ip = ip_res['ip']
        random.shuffle(public_configs)
        for pub_uri in public_configs[:300]:
            if 'security=reality' in pub_uri: continue

            sni = ""
            port = 443
            if pub_uri.startswith('vless://'):
                p = config_patcher.parse_vless(pub_uri)
                if p:
                    sni = p['query'].get('sni') or p['address']
                    port = int(p['port'])
            elif pub_uri.startswith('vmess://'):
                p = config_patcher.parse_vmess(pub_uri)
                if p:
                    sni = p.get('sni') or p.get('add')
                    port = int(p.get('port', 443))

            if not sni: continue

            # Use the most robust SNI we found earlier
            test_sni = sni if random.random() > 0.3 else best_sni
            if not test_sni: test_sni = sni

            success, _ = scanner.test_tls_handshake(ip, test_sni, port, timeout=2.0)
            if success:
                patched = config_patcher.patch_config(pub_uri, ip, force_sni=test_sni)
                if patched:
                    print(f"\n[✔] VERIFIED PATCH | Latency: {ip_res['latency']:.1f}ms")
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
    print("   Cloudflare & GCore Smart Scanner (v2.4)")
    print("      ویژه تانل ایران و پروتکل ریالیتی")
    print("====================================================\n")

    print("1. Manual Mode / دستی")
    print("2. Auto: IR-Tunnels & Reality / تانل یاب و ریالیتی")

    choice = input("Choice (1/2) [2]: ").strip() or "2"

    print("\n[+] Phase 0: Discovery (SNI & Configs)...")
    clean_snis = sni_scanner.find_best_sni()
    public_configs = config_patcher.fetch_public_configs()

    print("\n[+] Phase 1: Finding Clean IPs...")
    ranges = scanner.fetch_cf_ranges() + scanner.fetch_gcore_ranges()
    results = scanner.scan_ips(ranges, samples_per_range=3, max_workers=60)

    print("\n[+] Phase 2: Live Verification...")
    verify_and_display(results, choice, public_configs=public_configs, clean_snis=clean_snis)

    print("\n" + "="*50)
    print("نکته: برای ریالیتی (Reality) حتما از کلاینت بروز استفاده کنید.")
    print("====================================================")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
