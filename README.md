markdown
# BANU Hacking Tool 🛠️

**BANU** is a powerful all-in-one hacking and penetration testing tool with **200+ functions**, including DDoS attacks, backdoors, rootkits, Wi-Fi cracking, phishing, encryption, and more.

> ⚠️ **Disclaimer:** This tool is for **educational purposes only**. Use it only on systems you own or have explicit permission to test. Misuse is illegal and punishable by law.

---

## 📥 Installation

### 1. Clone the repository
```bash
git clone https://github.com/omarionstar67-source/banu-hacking-tool.git
cd banu-hacking-tool
2. Install dependencies
bash
apt update && apt install -y python3 hping3 hydra nmap aircrack-ng
3. Run the tool
bash
python3 banu.py
🚀 Quick Start
Run the script:

bash
python3 banu.py
Choose a function by entering a number (1-200).

Follow the prompts.

📋 Features (200+ Functions)
Category	Functions
DDoS	SYN, UDP, ICMP, HTTP, Slowloris, Amplification (NTP, DNS, SSDP, Memcached)
Backdoors	Reverse Shell, Bind Shell, SSH Tunnel, Persistence
Rootkits	Hide processes, files, network, users
Bruteforce	SSH, FTP, RDP, HTTP, ZIP, Wi-Fi, Instagram, Facebook
Exploits	EternalBlue, BlueKeep, Shellshock, Heartbleed, DirtyPipe, Log4Shell
Scanning	Ports, network, web, vulnerabilities, DNS, SMB, LDAP
Spoofing	ARP, DNS, IP, MAC, Email, SMS, Call
Keyloggers	Linux, Windows, Web, Android, Network
Anonymity	Tor, VPN, Proxy, MAC spoofing, DNS, Hostname
Wi-Fi	Deauth, cracking, scanning, handshake, PMKID, WPS
Phishing	Web, Email, SMS, Call, QR, DNS
Encryption	AES, RSA, PGP, Disk, Email, Cloud
Steganography	Hide data in images, audio, video, text
Utilities	Base64, Hex, ROT13, Hash, QR, Barcode
Games	Guess the number, Snake, Tic-tac-toe
Social Engineering	Phishing, Pretexting, Baiting, Tailgating
Cryptography	AES, RSA, DES, 3DES, Blowfish, Twofish, RC4
Analysis	Traffic, logs, memory, disk, network, processes
Misc	QR, Barcode, Random, Sort, Filter, Calculator, Clock, Weather
📂 File Structure
text
banu-hacking-tool/
├── banu.py       # Main script (200+ functions)
└── README.md     # This file
🔧 Requirements
Python 3.x

Kali Linux or any Debian-based system

Root privileges (sudo)

📌 Example Usage
DDoS SYN Flood:

bash
python3 banu.py
[>] Введи номер: 1
[+] IP: 1.2.3.4
[+] Порт: 80
[+] Время (сек): 60
Reverse Shell:

bash
python3 banu.py
[>] Введи номер: 11
[+] Ваш IP: 192.168.1.100
[+] Порт: 4444
Wi-Fi Deauth:

bash
python3 banu.py
[>] Введи номер: 101
[+] Интерфейс: wlan0
[+] BSSID: AA:BB:CC:DD:EE:FF
[+] Канал: 6
⚠️ Legal Disclaimer
This tool is provided for educational and research purposes only. The author is not responsible for any misuse or damage caused by this tool. Always obtain proper authorization before testing any system.

📧 Contact
GitHub: omarionstar67-source

Repository: banu-hacking-tool

⭐ Support
If you like this project, give it a star ⭐ on GitHub!

text

---

## КАК ДОБАВИТЬ README В РЕПОЗИТОРИЙ

### Через браузер:
1. Открой `https://github.com/omarionstar67-source/banu-hacking-tool`
2. Нажми **"Add file"** → **"Create new file"**
3. Назови файл: `README.md`
4. Вставь текст сверху
5. Нажми **"Commit changes"**

### Через терминал:
```bash
cd /root
nano README.md
# Вставь текст сверху
git add README.md
git commit -m "Add README"
git push
