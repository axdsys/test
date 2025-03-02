import requests
import time
import os
import urllib3
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
from colorama import Fore, Style, init
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

# Initialize colorama for colored output
init(autoreset=True)

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Global settings
MAX_THREADS = 10  # Number of threads for faster crawling

# Social media domains to search for
SOCIAL_MEDIA_SITES = ["facebook.com", "twitter.com", "instagram.com", "linkedin.com", "youtube.com", "t.me"]

# ASCII Banner
BANNER = f"""{Fore.MAGENTA}
██╗     ██╗███╗   ██╗██╗  ██╗██╗  ██╗██████╗ ██████╗ ███████╗████████╗
██║     ██║████╗  ██║██║ ██╔╝██║ ██╔╝██╔══██╗██╔══██╗██╔════╝╚══██╔══╝
██║     ██║██╔██╗ ██║█████╔╝ █████╔╝ ██████╔╝██████╔╝███████╗   ██║   
██║     ██║██║╚██╗██║██╔═██╗ ██╔═██╗ ██╔═══╝ ██╔═══╝ ╚════██║   ██║   
███████╗██║██║ ╚████║██║  ██╗██║  ██╗██║     ██║     ███████║   ██║   
╚══════╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═╝     ╚═╝     ╚══════╝   ╚═╝   
{Style.RESET_ALL}
{Fore.CYAN}Author: Arshad | Version: v1{Style.RESET_ALL}
"""

# Entry message
print(BANNER)
print(Fore.GREEN + Style.BRIGHT + "[+] Welcome to LinkXtract v7.0 - The Ultimate Version!")
print(Fore.CYAN + "----------------------------------------------------------------------\n")

def loading_animation(message="Processing..."):
    """Colored Animated Progress Bar."""
    print(Fore.YELLOW + message)
    for _ in tqdm(range(20), desc=Fore.CYAN + "🔍 Scanning", bar_format="{l_bar}{bar} {n_fmt}/{total_fmt}"):
        time.sleep(0.1)
    print(Fore.GREEN + "✔ Extraction Completed!\n")

def extract_links(url):
    """Extracts all links from the website."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        links = set()

        for tag in soup.find_all(['a', 'script', 'iframe']):
            href = tag.get('href') or tag.get('src')
            if href:
                links.add(urljoin(url, href))

        return links

    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"[-] Error: {e}\n")
        return set()

def find_social_media_links(url):
    """Extracts social media links and Gmail links from a website."""
    print(Fore.YELLOW + "\n[+] Searching for Social Media & Gmail Links...\n")
    
    all_links = extract_links(url)
    social_links = {link for link in all_links if any(site in link for site in SOCIAL_MEDIA_SITES)}
    gmail_links = {link for link in all_links if "mailto:" in link and "gmail.com" in link}

    if social_links:
        print(Fore.GREEN + "\n[+] Found Social Media Links:\n")
        for link in social_links:
            print(Fore.LIGHTBLUE_EX + "  ➤ " + link)

    if gmail_links:
        print(Fore.GREEN + "\n[+] Found Gmail Links:\n")
        for link in gmail_links:
            print(Fore.LIGHTRED_EX + "  ➤ " + link)

    if not social_links and not gmail_links:
        print(Fore.RED + "[-] No Social Media or Gmail Links Found.")

def extract_deep_links(url, depth=2):
    """Extracts parameterized links recursively up to 'depth' levels."""
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
        print(Fore.YELLOW + "\n[1] Find Social Media & Gmail Links")
        print(Fore.CYAN + "[2] Run Full LinkXtract Script")
        
        choice = input(Fore.BLUE + "\n[?] Select an option (1/2): ").strip()

        if choice == "1":
            website_url = input(Fore.BLUE + "[?] Enter the website URL: ").strip()
            loading_animation()
            find_social_media_links(website_url)

        elif choice == "2":
            website_url = input(Fore.BLUE + "[?] Enter the website URL: ").strip()
            aggressive_mode = input(Fore.MAGENTA + "[?] Enable aggressive deep crawling? (yes/no): ").strip().lower() == 'yes'
            query_search = input(Fore.CYAN + "[?] Enter specific query parameter to find (e.g., 'id=123'): ").strip()
            save_results = input(Fore.YELLOW + "[?] Do you want to save the extracted links? (yes/no): ").strip().lower() == 'yes'

            loading_animation()

            if aggressive_mode:
                print(Fore.RED + "\n[+] Aggressive Mode Activated! Fetching ONLY parameterized links...\n")
                links = extract_deep_links(website_url, depth=3)
            else:
                links = extract_links(website_url)

            matched_links = {link for link in links if query_search in link}

            if matched_links:
                print(Fore.CYAN + f"\n[+] Found {len(matched_links)} links matching `{query_search}`:\n")

                if save_results:
                    filename = f"extracted_links_{int(time.time())}.txt"
                    with open(filename, "w") as file:
                        for link in matched_links:
                            print(Fore.LIGHTRED_EX + Style.BRIGHT + "  ➤ " + link)
                            file.write("[MATCHED] " + link + "\n")

                    print(Fore.GREEN + f"\n✔ Matching links saved to '{filename}'")

            else:
                print(Fore.RED + f"[-] No links found matching `{query_search}`!\n")

        else:
            print(Fore.RED + "[-] Invalid option. Please choose 1 or 2.")

    except KeyboardInterrupt:
        print(Fore.RED + "\n[!] User interrupted. Exiting...")

    print(Fore.CYAN + "\n[+] Thank you for using LinkXtract v7.0! Stay aggressive! 🚀🔥")
