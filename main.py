import scanner
import config_generator
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

    print("--- مرحله ۱: تنظیمات اسکن ---")
    num_samples = int(get_input("تعداد نمونه در هر رنج ایپی", "5"))
    max_workers = int(get_input("تعداد تردها (سرعت اسکن)", "50"))

    check_host_option = get_input("آیا میخواهید هاست خاصی را چک کنید؟ (y/n)", "n").lower()
    host_to_check = None
    if check_host_option == 'y':
        host_to_check = get_input("نام هاست (مثلا example.workers.dev)")

    print("\n--- مرحله ۲: اطلاعات وی‌توری (V2Ray) ---")
    uuid = get_input("UUID", "00000000-0000-0000-0000-000000000000")
    v_host = get_input("V2Ray Host (SNI)", "your-host.com")
    v_path = get_input("V2Ray Path", "/")
    v_port = int(get_input("Port", "443"))
    protocol = get_input("Protocol (vless/vmess)", "vless").lower()

    print("\nدر حال دریافت رنج‌های کلودفلر...")
    ranges = scanner.fetch_cf_ranges()
    if not ranges:
        print("خطا در دریافت رنج‌های ایپی!")
        return

    print(f"تعداد {len(ranges)} رنج ایپی یافت شد.")
    print("شروع اسکن... لطفاً صبور باشید.\n")

    results = scanner.scan_ips(ranges, samples_per_range=num_samples, max_workers=max_workers, host_to_check=host_to_check)

    if not results:
        print("\nهیچ ایپی تمیزی پیدا نشد! شاید محدودیت اینترنت شما زیاد است.")
        return

    print(f"\nتعداد {len(results)} ایپی تمیز پیدا شد.")
    print("\n--- ۳ ایپی برتر با کمترین تاخیر ---")

    for i, res in enumerate(results[:3]):
        ip = res['ip']
        latency = res['latency']
        remark = f"CleanIP-{ip}-{int(latency)}ms"

        if protocol == 'vless':
            uri = config_generator.generate_vless_uri(ip, v_port, uuid, v_host, v_path, v_host, remark)
        else:
            uri = config_generator.generate_vmess_uri(ip, v_port, uuid, v_host, v_path, v_host, remark)

        print(f"\n{i+1}. IP: {ip} | Latency: {latency:.2f}ms")
        print(f"Config: {uri}")

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
