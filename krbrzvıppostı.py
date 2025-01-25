"""
KRBZ VIEW BOT V3.0
Gelişmiş Telegram View Gönderme Botu
Developer: @KRBRZZ063
"""

import os
import sys
import requests
import threading
from threading import active_count
import time
import random
from colorama import Fore, Style
import warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
from threading import Thread

warnings.filterwarnings('ignore', category=InsecureRequestWarning)

class ViewBot:
    def __init__(self):
        self.n_threads = 1000
        self.threads = []
        self.successful_views = 0
        self.failed_views = 0
        self.session = requests.Session()
        self.session.verify = False
        self.session.timeout = 3
        
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]

        self.channel_id = None
        self.current_post_id = 0
        self.running = True

    def send_view(self, channel: str, msgid: str, proxy: str) -> bool:
        s = requests.Session()
        proxies = {
            'http': proxy,
            'https': proxy
        }
        try:
            # İlk istek
            a = s.get("https://t.me/"+channel+"/"+msgid,
                    timeout=10, proxies=proxies)
            cookie = a.headers['set-cookie'].split(';')[0]
        except:
            return False

        h1 = {
            "Accept": "*/*", 
            "Accept-Encoding": "gzip, deflate, br", 
            "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7", 
            "Connection": "keep-alive", 
            "Content-Length": "5", 
            "Content-type": "application/x-www-form-urlencoded",
            "Cookie": cookie, 
            "Host": "t.me", 
            "Origin": "https://t.me", 
            "Referer": "https://t.me/"+channel+"/"+msgid+"?embed=1", 
            "Sec-Fetch-Dest": "empty", 
            "Sec-Fetch-Mode": "cors", 
            "Sec-Fetch-Site": "same-origin", 
            "User-Agent": random.choice(self.user_agents),
            "X-Requested-With": "XMLHttpRequest"
        }
        
        d1 = {"_rl": "1"}
        
        try:
            r = s.post('https://t.me/'+channel+'/'+msgid+'?embed=1',
                    json=d1, headers=h1, proxies=proxies)
            key = r.text.split('data-view="')[1].split('"')[0]
            now_view = r.text.split('<span class="tgme_widget_message_views">')[1].split('</span>')[0]
            if now_view.find("K") != -1:
                now_view = now_view.replace("K","00").replace(".", "")
        except:
            return False

        h2 = {
            "Accept": "*/*", 
            "Accept-Encoding": "gzip, deflate, br", 
            "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7", 
            "Connection": "keep-alive", 
            "Cookie": cookie, 
            "Host": "t.me",
            "Referer": "https://t.me/"+channel+"/"+msgid+"?embed=1", 
            "Sec-Fetch-Dest": "empty", 
            "Sec-Fetch-Mode": "cors", 
            "Sec-Fetch-Site": "same-origin", 
            "User-Agent": random.choice(self.user_agents), 
            "X-Requested-With": "XMLHttpRequest"
        }
        
        try:
            i = s.get('https://t.me/v/?views='+key, timeout=10,
                    headers=h2, proxies=proxies)
            if(i.text == "true"):
                self.successful_views += 1
                print(f'{Fore.GREEN}✅✅ View Başarılı ✅✅ | Görüntüleme: {now_view}{Style.RESET_ALL}')
                return True
        except:
            return False

        return False

    def view_worker(self, links: list, proxy: str):
        success_count = 0
        fail_count = 0
        
        for link in links:
            try:
                if not link:
                    continue
                    
                channel = link.split('/')[3]
                msgid = link.split('/')[4]
                
                if self.send_view(channel, msgid, proxy):
                    success_count += 1
                    if success_count >= 3:  # Her proxy ile 3 başarılı view
                        time.sleep(0.5)
                        continue
                else:
                    fail_count += 1
                    if fail_count >= 2:  # 2 başarısız denemeden sonra proxy değiştir
                        break
                        
                time.sleep(0.5)
                
            except:
                continue

    def get_proxies(self) -> list:
        proxies = []
        try:
            # HTTP/HTTPS Proxies
            proxy_sources = [
                "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=5000&country=all&ssl=yes&anonymity=all",
                "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
                "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
                "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
                "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt",
                "https://api.proxyscrape.com/?request=displayproxies&proxytype=http",
                "https://www.proxy-list.download/api/v1/get?type=http&anon=elite"
            ]
            
            for source in proxy_sources:
                try:
                    response = requests.get(source, timeout=10)
                    if response.status_code == 200:
                        new_proxies = [line.strip() for line in response.text.splitlines() if line.strip()]
                        proxies.extend(new_proxies)
                except:
                    continue
                
        except:
            pass
            
        return list(set(proxies))  # Tekrar eden proxy'leri temizle

    def start(self, links: list):
        while True:
            try:
                print(f"\n{Fore.YELLOW}Proxy'ler alınıyor...{Style.RESET_ALL}")
                proxies = self.get_proxies()
                
                if not proxies:
                    print(f"{Fore.RED}Proxy bulunamadı! Tekrar deneniyor...{Style.RESET_ALL}")
                    time.sleep(5)
                    continue
                    
                print(f"{Fore.GREEN}{len(proxies)} proxy bulundu!{Style.RESET_ALL}")
                
                with ThreadPoolExecutor(max_workers=self.n_threads) as executor:
                    futures = []
                    for proxy in proxies:
                        futures.append(
                            executor.submit(self.view_worker, links, proxy)
                        )
                    
                    for future in as_completed(futures):
                        try:
                            future.result()
                        except:
                            continue
                
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Program durduruluyor...{Style.RESET_ALL}")
                break
            except Exception as e:
                print(f"\n{Fore.RED}Hata: {str(e)}{Style.RESET_ALL}")
                time.sleep(5)
                continue

    def check_new_posts(self):
        """Yeni postları kontrol et"""
        try:
            url = f"https://t.me/s/{self.channel_id}"
            response = requests.get(url)
            if response.status_code == 200:
                # Son post ID'sini bul
                matches = re.findall(r'/(\d+)"', response.text)
                if matches:
                    latest_id = max(map(int, matches))
                    if latest_id > self.current_post_id:
                        # Yeni post bulundu
                        success_animation(f"✅ Yeni post bulundu! ID: {latest_id}")
                        self.current_post_id = latest_id
                    return self.current_post_id
        except Exception as e:
            error_animation(f"❌ Post kontrol hatası: {str(e)}")
        return self.current_post_id

    def auto_view_worker(self):
        """Otomatik izleme işlemini başlat"""
        while self.running:
            try:
                # Proxy'leri al
                proxies = self.get_proxies()
                if not proxies:
                    print(f"{Fore.RED}Proxy bulunamadı! Tekrar deneniyor...{Style.RESET_ALL}")
                    time.sleep(5)
                    continue
                
                print(f"{Fore.GREEN}{len(proxies)} proxy bulundu!{Style.RESET_ALL}")
                
                # Mevcut postu sürekli izle
                while self.running:
                    # Yeni post kontrolü
                    latest_id = self.check_new_posts()
                    
                    # View gönder
                    with ThreadPoolExecutor(max_workers=self.n_threads) as executor:
                        futures = []
                        for proxy in proxies:
                            futures.append(
                                executor.submit(self.send_view, self.channel_id, str(latest_id), proxy)
                            )
                        
                        for future in as_completed(futures):
                            try:
                                future.result()
                            except:
                                continue
                    
                    time.sleep(1)  # Her döngü arası 1 saniye bekle
                    
            except Exception as e:
                print(f"{Fore.RED}Hata: {str(e)}{Style.RESET_ALL}")
                time.sleep(5)
                continue

def print_banner():
    """Animasyonlu banner yazdır"""
    banner_lines = f"""{Fore.CYAN}
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
╔═══════════════════════════════════════════════════════════════╗
║                     ⚡ KRBRZ VIEW BOT V3.0 ⚡                  ║
║                      Professional Edition                      ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║        ██╗  ██╗██████╗ ██████╗ ██████╗ ███████╗              ║
║        ██║ ██╔╝██╔══██╗██╔══██╗██╔══██╗╚══███╔╝              ║
║        █████╔╝ ██████╔╝██████╔╝██████╔╝  ███╔╝               ║
║        ██╔═██╗ ██╔══██╗██╔══██╗██╔══██╗ ███╔╝                ║
║        ██║  ██╗██║  ██║██████╔╝██║  ██║███████╗              ║
║        ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝╚══════╝              ║
║                                                               ║
║                    🚀 KRBRZ TEAM 🚀                          ║
║                                                               ║
╠═══════════════════════════════════════════════════════════════╣
║              Developer: @KRBRZ063 | @KRBZ_VIP_TR              ║
╚═══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
""".split('\n')

    # Matrix efekti karakterleri
    matrix_chars = "░▒▓█"
    
    # Her satır için matrix efekti
    for line in banner_lines:
        if line.strip():  # Boş satırları atla
            # Önce matrix efekti
            scrambled = ''
            for char in line:
                if char not in ['║', '╔', '╗', '╚', '╝', '╠', '╣', '═', ' ']:
                    scrambled += random.choice(matrix_chars)
                else:
                    scrambled += char
            print(scrambled)
            time.sleep(0.05)
            # Sonra gerçek satır
            print(f"\033[F{line}")  # Bir satır yukarı çık ve gerçek satırı yazdır
            time.sleep(0.05)
        else:
            print(line)  # Boş satırları direkt yazdır

def loading_animation(duration: int = 3):
    """Yükleme animasyonu göster"""
    animation = [
        "[■□□□□□□□□□]",
        "[■■□□□□□□□□]",
        "[■■■□□□□□□□]",
        "[■■■■□□□□□□]",
        "[■■■■■□□□□□]",
        "[■■■■■■□□□□]",
        "[■■■■■■■□□□]",
        "[■■■■■■■■□□]",
        "[■■■■■■■■■□]",
        "[■■■■■■■■■■]"
    ]
    
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        print(f"\r{Fore.CYAN}Yükleniyor {animation[i % len(animation)]}{Style.RESET_ALL}", end='')
        time.sleep(0.1)
        i += 1
    print("\r" + " " * 50 + "\r", end='')

def success_animation(message: str):
    """Başarı animasyonu göster"""
    print(f"\r{Fore.GREEN}", end='')
    for char in message:
        print(char, end='', flush=True)
        time.sleep(0.02)
    print(f"{Style.RESET_ALL}")

def error_animation(message: str):
    """Hata animasyonu göster"""
    print(f"\r{Fore.RED}", end='')
    for char in message:
        print(char, end='', flush=True)
        time.sleep(0.02)
    print(f"{Style.RESET_ALL}")

def main():
    """Ana program"""
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print_banner()
    loading_animation()
    
    bot = ViewBot()
    
    try:
        # Kanal ID'sini otomatik ayarla
        bot.channel_id = "KRBZ_VIP_TR"
        
        success_animation(f"✅ Kanal bağlantısı kuruldu: @{bot.channel_id}")
        print(f"\n{Fore.CYAN}Bot çalışıyor... Son postu sürekli izliyor ve yeni post kontrolü yapıyor.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Durdurmak için Ctrl+C tuşlarına basın.{Style.RESET_ALL}\n")
        
        # Otomatik izleme thread'ini başlat
        view_thread = Thread(target=bot.auto_view_worker)
        view_thread.daemon = True
        view_thread.start()
        
        # Ana döngü
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        bot.running = False
        print(f"\n{Fore.YELLOW}Program durduruluyor...{Style.RESET_ALL}")
        return
    except Exception as e:
        error_animation(f"\n❌ Hata: {str(e)}")

if __name__ == "__main__":
    main()
