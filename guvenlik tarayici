#!/usr/bin/env python3
# =============================================================================
#  Guvenlik Acigi Tarama Araci  —  Terminal Surumu
#  Hazirlayan : Nida Subasi
#  Aciklama   : Kisisel merak ve ogrenme amacli yazilmis bir port tarayici.
#               Socket, subprocess, ipaddress ve concurrent.futures kullanildi.
#               Harici kutuphane gerektirmez; sadece Python 3.6+ yeterli.
#  Surumu     : 2.0  |  2026
# =============================================================================

import socket
import sys
import time
import os
import subprocess
import ipaddress
import concurrent.futures

# Windows terminalinde ANSI renk kodlarinin calismasi icin
os.system("")

# ---- Renk kodlari ----
YESIL   = "\033[92m"
KIRMIZI = "\033[91m"
SARI    = "\033[93m"
MAVI    = "\033[94m"
CYAN    = "\033[96m"
BEYAZ   = "\033[97m"
KOYU    = "\033[90m"
SIFIRLA = "\033[0m"
KALIN   = "\033[1m"

# ---- Taranacak portlar ve aciklamalari ----
PORTLAR = {
    21:   ("FTP",        "Dosya Transfer Protokolu"),
    22:   ("SSH",        "Guvenli Uzak Baglanti"),
    23:   ("Telnet",     "Sifresiz Uzak Baglanti — Tehlikeli"),
    25:   ("SMTP",       "E-posta Gonderme"),
    53:   ("DNS",        "Alan Adi Cozumleme"),
    80:   ("HTTP",       "Web Sunucusu"),
    110:  ("POP3",       "E-posta Alma"),
    135:  ("RPC",        "Windows Uzak Prosedur Cagrisi"),
    139:  ("NetBIOS",    "Windows Ag Paylasimi"),
    143:  ("IMAP",       "E-posta Yonetimi"),
    443:  ("HTTPS",      "Guvenli Web — SSL/TLS"),
    445:  ("SMB",        "Windows Dosya Paylasimi"),
    1433: ("MSSQL",      "Microsoft SQL Server"),
    3306: ("MySQL",      "MySQL Veritabani"),
    3389: ("RDP",        "Windows Uzak Masaustu"),
    5432: ("PostgreSQL", "PostgreSQL Veritabani"),
    5900: ("VNC",        "Sanal Ag Ekrani"),
    6379: ("Redis",      "Redis Veritabani"),
    8080: ("HTTP-Alt",   "Alternatif Web / Proxy"),
    8443: ("HTTPS-Alt",  "Alternatif Guvenli Web"),
}

# Canlilik tespitinde denenecek yaygin portlar
CANLILIK_PORTLARI = [80, 443, 22, 445, 135, 8080, 53, 3389]


# =============================================================================
#  YARDIMCI FONKSIYONLAR
# =============================================================================

def baslik_yazdir():
    """Ekrani temizleyip ASCII art basligini gosterir."""
    os.system("cls" if os.name == "nt" else "clear")
    print(f"""
{CYAN}{KALIN}
╔══════════════════════════════════════════════════════════════╗
║      ██████╗  ██████╗ ██████╗ ████████╗    ███████╗ ██████╗  ║
║      ██╔══██╗██╔═══██╗██╔══██╗╚══██╔══╝    ██╔════╝██╔════╝  ║
║      ██████╔╝██║   ██║██████╔╝   ██║       ███████╗██║       ║
║      ██╔═══╝ ██║   ██║██╔══██╗   ██║       ╚════██║██║       ║
║      ██║     ╚██████╔╝██║  ██║   ██║       ███████║╚██████╗  ║
║      ╚═╝      ╚═════╝ ╚═╝  ╚═╝   ╚═╝       ╚══════╝ ╚═════╝  ║
╠══════════════════════════════════════════════════════════════╣
║   Guvenlik Acigi Tarama Araci  |  Nida Subasi  |  2026       ║
╚══════════════════════════════════════════════════════════════╝
{SIFIRLA}""")


def menu_yazdir():
    """Ana menuyu yazdirir."""
    print(f"{MAVI}{'─'*64}{SIFIRLA}")
    print(f"  {SARI}[1]{SIFIRLA}  Port Tarama    {KOYU}Hedefteki portlari tara{SIFIRLA}")
    print(f"  {SARI}[2]{SIFIRLA}  Ping / Canlilik {KOYU}Host ulasimini kontrol et{SIFIRLA}")
    print(f"  {SARI}[3]{SIFIRLA}  Ag Taramasi    {KOYU}Yerel agdaki cihazlari bul{SIFIRLA}")
    print(f"  {SARI}[4]{SIFIRLA}  Hakkinda       {KOYU}Program bilgisi{SIFIRLA}")
    print(f"  {SARI}[5]{SIFIRLA}  Cikis")
    print(f"{MAVI}{'─'*64}{SIFIRLA}")


def ip_cozumle(hedef):
    """Domain veya hostname'i IP adresine donusturur."""
    try:
        return socket.gethostbyname(hedef)
    except socket.gaierror:
        return None


def tek_port_tara(ip, port, timeout=1.0):
    """Tek bir porta TCP baglantisi dener; True/False doner."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        sonuc = s.connect_ex((ip, port))
        s.close()
        return sonuc == 0
    except socket.error:
        return False


def paralel_tara(ip, portlar, timeout=1.0):
    """Verilen port listesini cok is parcacikliyla paralel tarar."""
    sonuclar = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        gorevler = {executor.submit(tek_port_tara, ip, p, timeout): p for p in portlar}
        for g in concurrent.futures.as_completed(gorevler):
            port = gorevler[g]
            try:
                sonuclar[port] = g.result()
            except Exception:
                sonuclar[port] = False
    return sonuclar


def icmp_ping(ip, timeout=2):
    """ICMP ping gonderir; isletim sistemine gore dogru komut secer."""
    try:
        if os.name == "nt":
            # Windows
            komut = ["ping", "-n", "1", "-w", str(timeout * 1000), ip]
        else:
            # Linux / macOS
            komut = ["ping", "-c", "1", "-W", str(timeout), ip]
        r = subprocess.run(komut, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return r.returncode == 0
    except Exception:
        return False


def tcp_ping(ip, timeout=1.0):
    """Yaygin portlari deneyerek hostin canli olup olmadigini anlamaya calisir."""
    for port in CANLILIK_PORTLARI:
        if tek_port_tara(ip, port, timeout):
            return True, port
    return False, None


def hostname_bul(ip):
    """IP adresinden hostname sorgusu yapar."""
    try:
        return socket.gethostbyaddr(ip)[0]
    except Exception:
        return "Bilinmiyor"


def yerel_ip_bul():
    """Makinenin yerel agdaki IP adresini tespit eder."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "192.168.1.1"


def tekli_host_tara(ip_str):
    """Bir IP adresinin canli olup olmadigini TCP ve ICMP ile test eder."""
    canli, port = tcp_ping(ip_str, timeout=0.5)
    if not canli:
        canli = icmp_ping(ip_str, timeout=1)
        port = None
    if canli:
        return {"ip": ip_str, "canli": True,
                "hostname": hostname_bul(ip_str), "port": port}
    return {"ip": ip_str, "canli": False}


# =============================================================================
#  ANA OZELLIKLER
# =============================================================================

def port_tarama():
    """Kullanicidan hedef alir ve secili portlari tarar."""
    print(f"\n{SARI}{'─'*64}{SIFIRLA}")
    print(f"  {CYAN}{KALIN}PORT TARAMA{SIFIRLA}")
    print(f"{SARI}{'─'*64}{SIFIRLA}")

    while True:
        hedef = input(f"\n  {CYAN}Hedef IP veya Domain: {SIFIRLA}").strip()
        if not hedef:
            print(f"  {KIRMIZI}Bos birakma.{SIFIRLA}")
            continue
        print(f"  {KOYU}Cozumleniyor...{SIFIRLA}")
        ip = ip_cozumle(hedef)
        if ip is None:
            print(f"  {KIRMIZI}'{hedef}' cozumlenemedi, tekrar dene.{SIFIRLA}")
            continue
        break

    print(f"\n  Hedef : {BEYAZ}{hedef}{SIFIRLA}")
    print(f"  IP    : {BEYAZ}{ip}{SIFIRLA}")
    print(f"\n  {SARI}Tarama basliyor...{SIFIRLA}")

    t = time.time()
    sonuclar = paralel_tara(ip, PORTLAR)
    sure = time.time() - t

    print(f"\n{MAVI}{'═'*64}{SIFIRLA}")
    print(f"  {KALIN}SONUCLAR{SIFIRLA}  ({sure:.2f} sn)")
    print(f"{MAVI}{'═'*64}{SIFIRLA}")
    print(f"  {'PORT':<8} {'SERVIS':<14} {'DURUM':<10} ACIKLAMA")
    print(f"  {KOYU}{'─'*56}{SIFIRLA}")

    acik = kapali = 0
    for port in sorted(sonuclar):
        servis, aciklama = PORTLAR[port]
        if sonuclar[port]:
            print(f"  {YESIL}{port:<8}{SIFIRLA} {servis:<14} "
                  f"{YESIL}{KALIN}ACIK{SIFIRLA}       {KOYU}{aciklama}{SIFIRLA}")
            acik += 1
        else:
            print(f"  {KOYU}{port:<8} {servis:<14} KAPALI     {aciklama}{SIFIRLA}")
            kapali += 1

    print(f"\n  {YESIL}Acik: {acik}{SIFIRLA}   {KOYU}Kapali: {kapali}{SIFIRLA}\n")


def ping_testi():
    """Hedef hostin ulasimini ICMP ve TCP ile test eder."""
    print(f"\n{SARI}{'─'*64}{SIFIRLA}")
    print(f"  {CYAN}{KALIN}PING / HOST CANLILIK TESTI{SIFIRLA}")
    print(f"{SARI}{'─'*64}{SIFIRLA}")

    while True:
        hedef = input(f"\n  {CYAN}Hedef IP veya Domain: {SIFIRLA}").strip()
        if not hedef:
            print(f"  {KIRMIZI}Bos birakma.{SIFIRLA}")
            continue
        ip = ip_cozumle(hedef)
        if ip is None:
            print(f"  {KIRMIZI}'{hedef}' cozumlenemedi.{SIFIRLA}")
            continue
        break

    print(f"\n  {KOYU}{hedef}  ({ip}){SIFIRLA}")
    print(f"  {KOYU}{'─'*50}{SIFIRLA}")

    # --- ICMP ---
    print(f"\n  {SARI}[1/3]{SIFIRLA} ICMP Ping...")
    t = time.time()
    icmp_ok = icmp_ping(ip)
    ms = (time.time() - t) * 1000
    if icmp_ok:
        print(f"        {YESIL}Basarili ({ms:.0f} ms){SIFIRLA}")
    else:
        print(f"        {KOYU}Cevap alinamadi (guvenlik duvari engelliyor olabilir){SIFIRLA}")

    # --- TCP ---
    print(f"\n  {SARI}[2/3]{SIFIRLA} TCP port kontrolu...")
    t = time.time()
    tcp_ok, acik_port = tcp_ping(ip)
    ms = (time.time() - t) * 1000
    if tcp_ok:
        servis = PORTLAR.get(acik_port, ("?", ""))[0]
        print(f"        {YESIL}Basarili - Port {acik_port}/{servis} ({ms:.0f} ms){SIFIRLA}")
    else:
        print(f"        {KOYU}Hicbir yaygin portta yanit yok{SIFIRLA}")

    # --- Hostname ---
    print(f"\n  {SARI}[3/3]{SIFIRLA} Hostname sorgusu...")
    hostname = hostname_bul(ip)
    print(f"        {CYAN}{hostname}{SIFIRLA}")

    # --- Sonuc ---
    print(f"\n{MAVI}{'═'*64}{SIFIRLA}")
    if icmp_ok or tcp_ok:
        print(f"  {YESIL}{KALIN}SONUC: HOST ERISEBILIR{SIFIRLA}")
    else:
        print(f"  {KIRMIZI}{KALIN}SONUC: HOST YANIT VERMIYOR{SIFIRLA}")
        print(f"  {KOYU}Cihaz kapali veya trafigi engelliyor olabilir.{SIFIRLA}")
    print(f"{MAVI}{'═'*64}{SIFIRLA}\n")


def ag_taramasi():
    """Yerel agdaki aktif cihazlari tespit eder."""
    print(f"\n{SARI}{'─'*64}{SIFIRLA}")
    print(f"  {CYAN}{KALIN}AG TARAMASI{SIFIRLA}")
    print(f"{SARI}{'─'*64}{SIFIRLA}")

    kendi_ip = yerel_ip_bul()
    parca = kendi_ip.rsplit(".", 1)[0]
    onerilen = f"{parca}.0/24"

    print(f"\n  Kendi IP: {BEYAZ}{kendi_ip}{SIFIRLA}")

    while True:
        girdi = input(
            f"\n  {CYAN}Ag araligi [{SARI}{onerilen}{CYAN}]: {SIFIRLA}"
        ).strip()
        if not girdi:
            girdi = onerilen
        try:
            ag = ipaddress.ip_network(girdi, strict=False)
            break
        except ValueError:
            print(f"  {KIRMIZI}Gecersiz CIDR. Ornek: 192.168.1.0/24{SIFIRLA}")

    ip_listesi = [str(ip) for ip in ag.hosts()]
    toplam = len(ip_listesi)

    print(f"\n  Ag: {BEYAZ}{ag}{SIFIRLA}  ({toplam} adres)")
    print(f"  {SARI}Taranıyor, lutfen bekle...{SIFIRLA}\n")

    t = time.time()
    canlilar = []
    tamamlanan = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        gorevler = {executor.submit(tekli_host_tara, ip): ip for ip in ip_listesi}
        for g in concurrent.futures.as_completed(gorevler):
            tamamlanan += 1
            try:
                sonuc = g.result()
                if sonuc["canli"]:
                    canlilar.append(sonuc)
            except Exception:
                pass

            # Ilerleme cubugu
            if tamamlanan % 5 == 0 or tamamlanan == toplam:
                yuzde = int((tamamlanan / toplam) * 100)
                dolu  = yuzde // 2
                bar   = (f"{YESIL}{'█' * dolu}"
                         f"{KOYU}{'░' * (50 - dolu)}{SIFIRLA}")
                print(f"\r  [{bar}] {BEYAZ}{yuzde}%{SIFIRLA}"
                      f"  {YESIL}{len(canlilar)} cihaz{SIFIRLA}",
                      end="", flush=True)

    sure = time.time() - t
    print()  # ilerleme cubugundan sonra yeni satir

    print(f"\n{MAVI}{'═'*64}{SIFIRLA}")
    print(f"  {KALIN}AG TARAMA SONUCLARI{SIFIRLA}  ({sure:.1f} sn)")
    print(f"{MAVI}{'═'*64}{SIFIRLA}")

    if not canlilar:
        print(f"\n  {SARI}Aktif cihaz bulunamadi.{SIFIRLA}")
        print(f"  {KOYU}Guvenlik duvari engelliyor olabilir.{SIFIRLA}\n")
        return

    canlilar.sort(key=lambda x: socket.inet_aton(x["ip"]))
    print(f"\n  {'#':<4} {'IP':<18} {'HOSTNAME':<28} DURUM")
    print(f"  {KOYU}{'─'*58}{SIFIRLA}")

    for i, c in enumerate(canlilar, 1):
        ip_str   = c["ip"]
        hostname = c.get("hostname", "Bilinmiyor")
        port     = c.get("port")

        if ip_str == kendi_ip:
            durum = f"{SARI}Sen{SIFIRLA}"
        elif port:
            servis = PORTLAR.get(port, ("?",))[0]
            durum  = f"{YESIL}Canli (port {port}/{servis}){SIFIRLA}"
        else:
            durum = f"{YESIL}Canli{SIFIRLA}"

        print(f"  {KOYU}{i:<4}{SIFIRLA} {BEYAZ}{ip_str:<18}{SIFIRLA} "
              f"{CYAN}{hostname:<28}{SIFIRLA} {durum}")

    print(f"\n  {YESIL}{len(canlilar)} cihaz bulundu{SIFIRLA}"
          f"  {KOYU}({toplam} IP, {sure:.1f} sn){SIFIRLA}\n")


def hakkinda():
    """Program ve gelistirici bilgisini gosterir."""
    print(f"""
{CYAN}{'─'*64}{SIFIRLA}
  {KALIN}Guvenlik Acigi Tarama Araci  —  Terminal Surumu{SIFIRLA}

  Hazirlayan : {YESIL}Nida Subasi{SIFIRLA}
  Surumu     : 2.0  |  2026
  Dil        : Python 3  (sadece standart kutuphane)
  Isletim S. : Windows, macOS, Linux

  Ozellikler :
    - Paralel port tarama (TCP Connect, 50 is parcacigi)
    - ICMP + TCP canlilik testi
    - Yerel ag kesfetme (/24 CIDR destegi)
    - Renk kodlu terminal ciktisi
{CYAN}{'─'*64}{SIFIRLA}
""")


# =============================================================================
#  GIRIS NOKTASI
# =============================================================================

def main():
    baslik_yazdir()
    while True:
        menu_yazdir()
        try:
            secim = input(f"\n  {CYAN}Secim [1-5]: {SIFIRLA}").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n\n  {SARI}Cikis yapiliyor...{SIFIRLA}\n")
            sys.exit(0)

        try:
            if   secim == "1":
                port_tarama()
            elif secim == "2":
                ping_testi()
            elif secim == "3":
                ag_taramasi()
            elif secim == "4":
                hakkinda()
            elif secim == "5":
                print(f"\n  {SARI}Gule gule!{SIFIRLA}\n")
                sys.exit(0)
            else:
                print(f"\n  {KIRMIZI}Lutfen 1 ile 5 arasinda bir sayi gir.{SIFIRLA}\n")
        except KeyboardInterrupt:
            print(f"\n\n  {SARI}Iptal edildi, menüye donuluyor...{SIFIRLA}\n")

        try:
            input(f"  {KOYU}Devam etmek icin Enter'a bas...{SIFIRLA}")
        except (KeyboardInterrupt, EOFError):
            sys.exit(0)

        baslik_yazdir()


if __name__ == "__main__":
    main()
