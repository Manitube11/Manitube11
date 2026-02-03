import scanner
import config_generator
import config_patcher
import sni_scanner
import sys
import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def verify_and_display(results, choice, user_config=None, public_configs=None, clean_snis=None):
    print("\n" + "="*50)
    print("   RESULTS & CONNECTIVITY TEST (v2.3)")
    print("="*50)

    count = 0
    # Use the best SNI found by sni_scanner if available
    best_sni = clean_snis[0] if clean_snis else None

    if choice == "1":
        for res in results:
            ip = res['ip']
            port = user_config['port']
            # Try user's SNI first, then fallback to clean SNI
            sni_to_test = [user_config['host']]
            if best_sni: sni_to_test.append(best_sni)

            for sni in sni_to_test:
                success, _ = scanner.test_tls_handshake(ip, sni, port, timeout=3.0)
                if success:
                    remark = f"Verified-{ip}"
                    if user_config['protocol'] == 'vless':
                        uri = config_generator.generate_vless_uri(ip, port, user_config['uuid'], user_config['host'], user_config['path'], sni, remark)
                    else:
                        uri = config_generator.generate_vmess_uri(ip, port, user_config['uuid'], user_config['host'], user_config['path'], sni, remark)

                    print(f"\n[✔] VERIFIED | Latency: {res['latency']:.1f}ms | SNI: {sni}")
                    print(f"Config: {uri}")
                    count += 1
                    break
            if count >= 5: break
    else:
        # Auto mode: Try to find working combinations
        print("[+] Testing potential IR Relays and SNI combinations...")
        for ip_res in results:
            ip = ip_res['ip']
            # Limit configs to test per IP to save time
            for pub_uri in public_configs[:100]:
                # 1. Extract info
                target_sni = ""
                port = 443
                if pub_uri.startswith('vless://'):
                    p = config_patcher.parse_vless(pub_uri)
                    if p:
                        target_sni = p['query'].get('sni') or p['address']
                        port = int(p['port'])
                else:
                    p = config_patcher.parse_vmess(pub_uri)
                    if p:
                        target_sni = p.get('sni') or p.get('add')
                        port = int(p.get('port', 443))

                if not target_sni: continue

                # 2. Test original SNI
                success, _ = scanner.test_tls_handshake(ip, target_sni, port, timeout=2.5)

                # 3. If original fails, try forcing a "Clean SNI" (Domain Fronting trick)
                if not success and best_sni:
                    success, _ = scanner.test_tls_handshake(ip, best_sni, port, timeout=2.5)
                    if success: target_sni = best_sni # Use the clean one

                if success:
                    patched = config_patcher.patch_config(pub_uri, ip, force_sni=target_sni)
                    if patched:
                        print(f"\n[✔] VERIFIED | Latency: {ip_res['latency']:.1f}ms")
                        print(f"IP: {ip} | SNI: {target_sni}")
                        print(f"Config: {patched}")
                        count += 1
                        break
            if count >= 5: break

    if count == 0:
        print("\n[!] متاسفانه هیچ تانل یا دامنه‌ای روی اینترنت شما جواب نداد.")
        print("احتمالاً تمام رنج‌های کلودفلر/جیکور روی اپراتور شما مسدود شده است.")
    else:
        print(f"\n[+] تعداد {count} کانفیگ با موفقیت تست شد.")

def main():
    clear_screen()
    print("====================================================")
    print("   Cloudflare & GCore Smart Scanner (v2.3)")
    print("      اسکنر هوشمند با قابلیت تانل‌ یاب و SNI یاب")
    print("====================================================\n")

    print("1. Manual Mode / دستی")
    print("2. Automatic (Search IR Bridges/Relays) / تانل یاب خودکار")

    choice = input("Choice (1/2) [2]: ").strip() or "2"

    print("\n[+] Starting Phase 0: SNI Discovery...")
    clean_snis = sni_scanner.find_best_sni()

    num_samples = 3
    max_workers = 50

    user_config = {}
    if choice == "1":
        print("\n--- V2Ray Info ---")
        user_config['uuid'] = input("UUID: ").strip()
        user_config['host'] = input("Host/SNI: ").strip()
        user_config['path'] = input("Path [/]: ").strip() or "/"
        user_config['port'] = int(input("Port [443]: ").strip() or "443")
        user_config['protocol'] = input("Protocol (vless/vmess) [vless]: ").strip().lower() or "vless"

    print("\n[+] Fetching IP ranges...")
    ranges = scanner.fetch_cf_ranges() + scanner.fetch_gcore_ranges()

    public_configs = []
    if choice == "2":
        print("[+] Fetching public configs (prioritizing IR Bridges)...")
        public_configs = config_patcher.fetch_public_configs()

    print(f"\n[+] Starting Phase 1: Fast IP Scan...")
    results = scanner.scan_ips(ranges, samples_per_range=num_samples, max_workers=max_workers)

    if not results:
        print("\n[!] No clean IPs found.")
        return

    print(f"\n[+] Starting Phase 2: Live Tunnel Verification...")
    verify_and_display(results, choice, user_config, public_configs, clean_snis)

    print("\n" + "="*50)
    print("Done! Use VERIFIED links. Try different ISPs if none work.")
    print("====================================================")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
