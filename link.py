import requests
import time
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
from colorama import Fore, Style, init
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

# Initialize colorama for colored output
init(autoreset=True)

# Global settings
MAX_THREADS = 10  # Number of threads for faster crawling

# Status code colors
def status_color(status):
    if 200 <= status < 300:
        return Fore.GREEN  # ✅ Green for 200s
    elif 300 <= status < 400:
        return Fore.YELLOW  # ⚠️ Yellow for 3xx
    elif 400 <= status < 600:
        return Fore.RED  # ❌ Red for 4xx/5xx
    return Fore.WHITE

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

def get_next_filename():
    """Generates an incrementing filename for saved results."""
    base_name = "extracted_links"
    ext = ".txt"
    count = 1

    while os.path.exists(f"{base_name}_{count}{ext}"):
        count += 1

    return f"{base_name}_{count}{ext}"

def loading_animation(message="Processing..."):
    """Colored Animated Progress Bar."""
    print(Fore.YELLOW + message)
    for _ in tqdm(range(20), desc=Fore.CYAN + "🔍 Scanning", bar_format="{l_bar}{bar} {n_fmt}/{total_fmt}"):
        time.sleep(0.1)
    print(Fore.GREEN + "✔ Extraction Completed!\n")

def extract_links(url):
    """Extracts only links that contain query parameters (`?key=value`)."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        status_code = response.status_code
        print(f"{Fore.CYAN}[+] Fetching URL:{Fore.WHITE} {url} {status_color(status_code)}[Status: {status_code}]\n")

        if response.status_code >= 400:
            print(Fore.RED + f"[-] Skipping {url} due to error status: {status_code}\n")
            return set()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract only links containing query parameters
        links = set()
        for tag in soup.find_all(['a', 'script', 'iframe']):
            href = tag.get('href') or tag.get('src')
            if href:
                full_link = urljoin(url, href)
                if "?" in full_link and "=" in urlparse(full_link).query:
                    links.add(full_link)

        return links

    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"[-] Error: {e}\n")
        return set()

def match_query_parameter(url, query_param):
    """Checks if a URL contains a specific query parameter"""
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    return query_param in query_params

def extract_deep_links(url, depth=2):
    """Aggressive mode: Extracts only links with query parameters recursively up to 'depth' levels"""
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

        matched_links = {link for link in links if match_query_parameter(link, query_search)}

        if matched_links:
            print(Fore.CYAN + f"\n[+] Found {len(matched_links)} links matching `{query_search}`:\n")

            if save_results:
                filename = get_next_filename()
                with open(filename, "w") as file:
                    file.write(f"=== Extracted Links Matching `{query_search}` ===\n")

                    for link in matched_links:
                        print(Fore.LIGHTRED_EX + Style.BRIGHT + "  ➤ " + link + "\n")
                        file.write("[MATCHED] " + link + "\n")

                print(Fore.GREEN + f"\n✔ Matching links saved to '{filename}'")

        else:
            print(Fore.RED + f"[-] No links found matching `{query_search}`!\n")

    except KeyboardInterrupt:
        print(Fore.RED + "\n[!] User interrupted. Exiting...")

    # Exit message
    print(Fore.CYAN + "\n[+] Thank you for using LinkXtract v7.0! Stay aggressive! 🚀🔥")
