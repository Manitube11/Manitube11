import scanner
import config_generator
import config_patcher
import sys
import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_input(prompt, default=None):
    if default:
        res = input(f"{prompt} [{default}]: ").strip()
        return res if res else default
    return input(f"{prompt}: ").strip()

def main():
    clear_screen()
    print("====================================================")
    print("   Cloudflare Clean IP Scanner & V2Ray Configurator")
    print("      اسکنر ایپی تمیز کلودفلر و سازنده کانفیگ")
    print("====================================================\n")

    print("نوع عملیات را انتخاب کنید:")
    print("1. ساخت کانفیگ با مشخصات سرور خودم (UUID, Host, ...)")
    print("2. حالت خودکار (پیدا کردن خودکار کانفیگ و ایپی تمیز)")

    choice = get_input("انتخاب (1 یا 2)", "2")

    print("\n--- تنظیمات اسکن ---")
    num_samples = int(get_input("تعداد نمونه در هر رنج ایپی", "5"))
    max_workers = int(get_input("تعداد تردها (سرعت اسکن)", "50"))

    user_config = {}
    if choice == "1":
        print("\n--- اطلاعات وی‌توری (V2Ray) ---")
        user_config['uuid'] = get_input("UUID", "00000000-0000-0000-0000-000000000000")
        user_config['host'] = get_input("V2Ray Host (SNI)", "your-host.com")
        user_config['path'] = get_input("V2Ray Path", "/")
        user_config['port'] = int(get_input("Port", "443"))
        user_config['protocol'] = get_input("Protocol (vless/vmess)", "vless").lower()

    print("\nدر حال دریافت رنج‌های کلودفلر...")
    ranges = scanner.fetch_cf_ranges()
    if not ranges:
        print("خطا در دریافت رنج‌های ایپی!")
        return

    public_configs = []
    if choice == "2":
        print("در حال دریافت کانفیگ‌های عمومی برای شخصی‌سازی...")
        public_configs = config_patcher.fetch_public_configs()
        print(f"تعداد {len(public_configs)} کانفیگ پیدا شد.")

    print(f"\nشروع اسکن روی {len(ranges)} رنج... لطفاً صبور باشید.\n")
    # In auto mode, we don't need host check because we'll patch multiple configs
    host_to_check = user_config.get('host') if choice == "1" else None
    results = scanner.scan_ips(ranges, samples_per_range=num_samples, max_workers=max_workers, host_to_check=host_to_check)

    if not results:
        print("\nهیچ ایپی تمیزی پیدا نشد!")
        return

    print(f"\nتعداد {len(results)} ایپی تمیز پیدا شد.")

    if choice == "1":
        print("\n--- ۳ کانفیگ برتر شما ---")
        for i, res in enumerate(results[:3]):
            ip = res['ip']
            latency = res['latency']
            remark = f"CleanIP-{ip}-{int(latency)}ms"
            if user_config['protocol'] == 'vless':
                uri = config_generator.generate_vless_uri(ip, user_config['port'], user_config['uuid'], user_config['host'], user_config['path'], user_config['host'], remark)
            else:
                uri = config_generator.generate_vmess_uri(ip, user_config['port'], user_config['uuid'], user_config['host'], user_config['path'], user_config['host'], remark)
            print(f"\n{i+1}. IP: {ip} | Latency: {latency:.2f}ms\nConfig: {uri}")
    else:
        print("\n--- کانفیگ‌های خودکار شخصی‌سازی شده (Fixed) ---")
        count = 0
        # Try to patch configs using the best clean IPs
        for ip_res in results[:3]:
            ip = ip_res['ip']
            for pub_uri in public_configs:
                patched = config_patcher.patch_config(pub_uri, ip)
                if patched:
                    print(f"\nIP: {ip} | Latency: {ip_res['latency']:.2f}ms")
                    print(f"Config: {patched}")
                    count += 1
                    break # Move to next IP after finding one working config for this IP
            if count >= 5: break

    print("\n====================================================")
    print("عملیات با موفقیت پایان یافت.")
    print("====================================================")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nبرنامه توسط کاربر متوقف شد.")
        sys.exit(0)
    except Exception as e:
        print(f"\nخطای غیرمنتظره: {e}")
