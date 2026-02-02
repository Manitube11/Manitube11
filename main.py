import scanner
import config_generator
import config_patcher
import sys
import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    clear_screen()
    print("====================================================")
    print("   Cloudflare & GCore Scanner + Auto-Patch (v2.1)")
    print("      اسکنر هوشمند و اصلاح‌کننده خودکار کانفیگ")
    print("====================================================\n")

    print("--- Mode / نوع عملیات ---")
    print("1. Manual (Server Info) / دستی")
    print("2. Automatic (I have nothing) / کاملا خودکار")

    choice = input("Choice (1/2) [2]: ").strip() or "2"

    print("\n--- Scan Settings / تنظیمات اسکن ---")
    num_samples = int(input("Samples per range / تعداد نمونه [5]: ").strip() or "5")
    max_workers = int(input("Threads / تعداد ترد [50]: ").strip() or "50")

    user_config = {}
    if choice == "1":
        print("\n--- V2Ray Info ---")
        user_config['uuid'] = input("UUID: ").strip()
        user_config['host'] = input("Host/SNI: ").strip()
        user_config['path'] = input("Path [/]: ").strip() or "/"
        user_config['port'] = int(input("Port [443]: ").strip() or "443")
        user_config['protocol'] = input("Protocol (vless/vmess) [vless]: ").strip().lower() or "vless"

    print("\n[+] Fetching IP ranges (Cloudflare + GCore)...")
    ranges = scanner.fetch_cf_ranges() + scanner.fetch_gcore_ranges()

    public_configs = []
    if choice == "2":
        print("[+] Fetching public configs for patching...")
        public_configs = config_patcher.fetch_public_configs()
        print(f"[+] Found {len(public_configs)} potential nodes.")

    print(f"\n[+] Starting DEEP SCAN (TLS Handshake)...")
    sni = user_config.get('host', 'www.cloudflare.com')
    results = scanner.scan_ips(ranges, samples_per_range=num_samples, max_workers=max_workers, sni_to_check=sni)

    if not results:
        print("\n[!] No clean IPs found! Try again later or increase samples.")
        return

    print(f"\n[+] Found {len(results)} clean IPs.")

    print("\n" + "="*50)
    print("   RESULTS / نتایج (Copy the links below)")
    print("="*50)

    if choice == "1":
        for i, res in enumerate(results[:5]):
            ip = res['ip']
            remark = f"MyServer-{ip}-{int(res['latency'])}ms"
            if user_config['protocol'] == 'vless':
                uri = config_generator.generate_vless_uri(ip, user_config['port'], user_config['uuid'], user_config['host'], user_config['path'], user_config['host'], remark)
            else:
                uri = config_generator.generate_vmess_uri(ip, user_config['port'], user_config['uuid'], user_config['host'], user_config['path'], user_config['host'], remark)
            print(f"\n#{i+1} [Latency: {res['latency']:.1f}ms]")
            print(f"IP: {ip}")
            print(f"Config: {uri}")
    else:
        count = 0
        for ip_res in results[:5]:
            ip = ip_res['ip']
            for pub_uri in public_configs:
                patched = config_patcher.patch_config(pub_uri, ip)
                if patched:
                    print(f"\n#{count+1} [Latency: {ip_res['latency']:.1f}ms]")
                    print(f"IP: {ip}")
                    print(f"Config: {patched}")
                    count += 1
                    break
            if count >= 10: break

    print("\n" + "="*50)
    print("Done! If it doesn't work, enable 'Fragment' in your client.")
    print("برای جواب گرفتن، قابلیت فرگمنت را در برنامه خود فعال کنید.")
    print("="*50)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
