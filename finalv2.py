import requests
import time
import os
import urllib3
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from colorama import Fore, Style, init
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import re
import socket

# Initialize colorama for colored output
init(autoreset=True)

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Global settings
MAX_THREADS = 20  # Increased number of threads for faster crawling
USER_AGENT = {"User-Agent": "Mozilla/5.0"}
DEPTH_LIMIT = 5

# Social media domains to search for
SOCIAL_MEDIA_SITES = ["facebook.com", "twitter.com", "instagram.com", "linkedin.com", "youtube.com", "t.me"]

# Enhanced regular expression for email extraction
EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

# ASCII Banner
BANNER = f"""{Fore.MAGENTA}
███████╗██╗     ██╗███╗   ██╗██╗  ██╗██╗  ██╗██████╗ ██████╗ ███████╗████████╗
██╔════╝██║     ██║████╗  ██║██║ ██╔╝██║ ██╔╝██╔══██╗██╔══██╗██╔════╝╚══██╔══╝
███████╗██║     ██║██╔██╗ ██║█████╔╝ █████╔╝ ██████╔╝██████╔╝███████╗   ██║   
╚════██║██║     ██║██║╚██╗██║██╔═██╗ ██╔═██╗ ██╔═══╝ ██╔═══╝ ╚════██║   ██║   
███████║███████╗██║██║ ╚████║██║  ██╗██║  ██╗██║     ██║     ███████║   ██║   
╚══════╝╚══════╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝     ╚══════╝   ╚═╝   
{Style.RESET_ALL}{Fore.CYAN}Author: Advanced Version | Version: v3.0{Style.RESET_ALL}
"""

print(BANNER)

def loading_animation(message="Processing..."):
    print(Fore.YELLOW + message)
    for _ in tqdm(range(20), desc=Fore.CYAN + "🔍 Scanning", bar_format="{l_bar}{bar} {n_fmt}/{total_fmt}"):
        time.sleep(0.1)
    print(Fore.GREEN + "✔ Extraction Completed!\n")

def extract_links(url):
    try:
        response = requests.get(url, headers=USER_AGENT, timeout=10, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = set(urljoin(url, tag.get('href', '')) for tag in soup.find_all('a') if tag.get('href'))
        return links
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"[-] Error: {e}\n")
        return set()

def extract_emails(url):
    try:
        response = requests.get(url, headers=USER_AGENT, timeout=10, verify=False)
        emails = set(re.findall(EMAIL_REGEX, response.text))
        return emails
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"[-] Error: {e}\n")
        return set()

def extract_ip_and_dns(url):
    try:
        parsed_url = urlparse(url)
        ip = socket.gethostbyname(parsed_url.netloc)
        return ip
    except socket.gaierror:
        return "Unable to resolve"

def find_social_media_links(url):
    print(Fore.YELLOW + "\n[+] Searching for Social Media & Email Links...\n")
    all_links = extract_links(url)
    social_links = {link for link in all_links if any(site in link for site in SOCIAL_MEDIA_SITES)}
    emails = extract_emails(url)
    
    if social_links:
        print(Fore.GREEN + "\n[+] Found Social Media Links:\n")
        for link in social_links:
            print(Fore.LIGHTBLUE_EX + "  ➤ " + link)
    
    if emails:
        print(Fore.GREEN + "\n[+] Found Email Addresses:\n")
        for email in emails:
            print(Fore.LIGHTRED_EX + "  ➤ " + email)

def extract_deep_links(url, depth=3):
    visited = set()
    all_links = set()
    
    def crawl(current_url, current_depth):
        if current_url in visited or current_depth > depth:
            return
        visited.add(current_url)
        links = extract_links(current_url)
        all_links.update(links)
        with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            futures = [executor.submit(crawl, link, current_depth + 1) for link in links]
            for future in futures:
                future.result()
    
    crawl(url, 1)
    return all_links

if __name__ == "__main__":
    try:
        print(Fore.YELLOW + "\n[1] Find Social Media, Emails & IP Info")
        print(Fore.CYAN + "[2] Run Full Advanced Link Extraction")
        choice = input(Fore.BLUE + "\n[?] Select an option (1/2): ").strip()
        
        if choice == "1":
            website_url = input(Fore.BLUE + "[?] Enter the website URL: ").strip()
            loading_animation()
            find_social_media_links(website_url)
            ip_info = extract_ip_and_dns(website_url)
            print(Fore.GREEN + f"\n[+] Website IP Address: {ip_info}\n")
        
        elif choice == "2":
            website_url = input(Fore.BLUE + "[?] Enter the website URL: ").strip()
            loading_animation()
            links = extract_deep_links(website_url, depth=DEPTH_LIMIT)
            print(Fore.CYAN + f"\n[+] Extracted {len(links)} links from {website_url}\n")
        else:
            print(Fore.RED + "[-] Invalid option. Please choose 1 or 2.")
    
    except KeyboardInterrupt:
        print(Fore.RED + "\n[!] User interrupted. Exiting...")
    
    print(Fore.CYAN + "\n[+] Thank you for using Advanced LinkXtract v3.0! 🚀🔥")
