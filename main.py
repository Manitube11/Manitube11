import scanner
import config_generator
import config_patcher
import sys
import os
import re

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def verify_and_display(results, choice, user_config=None, public_configs=None):
    print("\n" + "="*50)
    print("   RESULTS & CONNECTIVITY TEST / نتایج و تست اتصال")
    print("="*50)

    count = 0
    if choice == "1":
        for res in results:
            ip = res['ip']
            port = user_config['port']
            sni = user_config['host']

            # Real test with user's specific SNI
            success, _ = scanner.test_tls_handshake(ip, sni, port, timeout=3.0)

            if success:
                remark = f"Verified-{ip}"
                if user_config['protocol'] == 'vless':
                    uri = config_generator.generate_vless_uri(ip, port, user_config['uuid'], user_config['host'], user_config['path'], user_config['host'], remark)
                else:
                    uri = config_generator.generate_vmess_uri(ip, port, user_config['uuid'], user_config['host'], user_config['path'], user_config['host'], remark)

                print(f"\n[✔] VERIFIED | Latency: {res['latency']:.1f}ms")
                print(f"IP: {ip}")
                print(f"Config: {uri}")
                count += 1
            if count >= 5: break
    else:
        # Auto mode patching
        for ip_res in results:
            ip = ip_res['ip']
            for pub_uri in public_configs:
                # Basic check for IP/SNI connectivity before patching
                # We need to extract SNI from the config first to test it
                sni = ""
                port = 443
                if pub_uri.startswith('vless://'):
                    p = config_patcher.parse_vless(pub_uri)
                    if p:
                        sni = p['query'].get('sni') or p['address']
                        port = int(p['port'])
                else:
                    p = config_patcher.parse_vmess(pub_uri)
                    if p:
                        sni = p.get('sni') or p.get('add')
                        port = int(p.get('port', 443))

                if not sni: continue

                # Test if THIS specific config's SNI works with THIS clean IP on user's net
                success, _ = scanner.test_tls_handshake(ip, sni, port, timeout=3.0)

                if success:
                    patched = config_patcher.patch_config(pub_uri, ip)
                    if patched:
                        print(f"\n[✔] VERIFIED | Latency: {ip_res['latency']:.1f}ms")
                        print(f"IP: {ip} | SNI: {sni}")
                        print(f"Config: {patched}")
                        count += 1
                        break # Found a working config for this IP, move to next IP
            if count >= 5: break

    if count == 0:
        print("\n[!] هیچ کانفیگی در تست نهایی با اینترنت شما موفق نبود.")
        print("احتمالا SNI های موجود در کانفیگ‌های عمومی همگی مسدود هستند.")
    else:
        print(f"\n[+] تعداد {count} کانفیگ با موفقیت تست شد و آماده استفاده است.")

def main():
    clear_screen()
    print("====================================================")
    print("   Cloudflare & GCore Smart Scanner (v2.2)")
    print("      اسکنر هوشمند با قابلیت تست زنده اتصال")
    print("====================================================\n")

    print("--- Mode / نوع عملیات ---")
    print("1. Manual (Server Info) / دستی")
    print("2. Automatic (Full Auto) / کاملا خودکار")

    choice = input("Choice (1/2) [2]: ").strip() or "2"

    print("\n--- Scan Settings / تنظیمات اسکن ---")
    num_samples = int(input("Samples per range / تعداد نمونه [3]: ").strip() or "3")
    max_workers = int(input("Threads / تعداد ترد [50]: ").strip() or "50")

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
        print("[+] Fetching public configs...")
        public_configs = config_patcher.fetch_public_configs()
        print(f"[+] Found {len(public_configs)} potential nodes.")

    print(f"\n[+] Starting Phase 1: Fast IP Scan...")
    # Fast scan with default SNI to find potentially clean IPs
    results = scanner.scan_ips(ranges, samples_per_range=num_samples, max_workers=max_workers)

    if not results:
        print("\n[!] No clean IPs found in Phase 1.")
        return

    print(f"\n[+] Starting Phase 2: Live Connectivity Test...")
    print("در حال تست نهایی روی اینترنت شما...")
    verify_and_display(results, choice, user_config, public_configs)

    print("\n" + "="*50)
    print("Done! Use the [✔] VERIFIED configs for best performance.")
    print("کانفیگ‌هایی که علامت تیک دارند مستقیماً با نت شما تست شده‌اند.")
    print("="*50)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
