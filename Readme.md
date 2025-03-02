🔗 LinkXtract - Advanced Link Extractor
🚀 Version: v1 | 👤 Author: Arshad | 🎭 Nickname: ???

LinkXtract is a fast and efficient link extractor that focuses on extracting only parameterized links (?key=value). It supports deep crawling, multi-threading, and auto-saving results

✨ Features
✅ Extracts only links with query parameters (?key=value)
🔍 Aggressive Mode: Recursively extracts links up to multiple levels
⚡ Multi-threaded for faster extraction
📊 Displays status codes for each fetched URL
💾 Auto-incrementing file saving for extracted links
🔑 User-defined query parameter search (e.g., ?id=123)
📝 Organized and tidy output


📦 Installation
Ensure you have Python installed, then install dependencies:

sh
Copy code
pip install requests beautifulsoup4 colorama tqdm concurrent.futures

⚡ Usage
Run the script with:

sh
Copy code
python linkxtract.py
It will prompt for:
1️⃣ Website URL to scan
2️⃣ Enable Aggressive Mode? (Yes/No)
3️⃣ Query Parameter to Search (e.g., ?id=123)
4️⃣ Save Results? (Yes/No)

📜 Example Output
pgsql
Copy code
[?] Enter the website URL: https://example.com
[?] Enable aggressive deep crawling? (yes/no): yes
[?] Enter specific query parameter to find (e.g., 'id=123'): session
[?] Do you want to save the extracted links? (yes/no): yes

⏳ Processing: 100% | 20/20  
✅ Extraction Completed!

🔗 [+] Fetching URL: https://example.com/page?session=abc123 [Status: 200]  
🔗 [+] Fetching URL: https://example.com/user?session=xyz456 [Status: 200]  

💾 ✔ Matching links saved to 'extracted_links_1.txt'


