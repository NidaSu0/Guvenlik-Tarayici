#!/usr/bin/env python3
# =============================================================================
#  Guvenlik Acigi Tarama Araci  —  GUI Surumu
#  Hazirlayan : Nida Subasi
#  Aciklama   : Kisisel ogrenme amacli gelistirilmis gorsel port tarayici.
#               Tkinter tabanli; socket, subprocess, ipaddress,
#               concurrent.futures ve threading kullanildi.
#               Harici kutuphane gerektirmez; Python 3.6+ yeterli.
#  Surumu     : 2.0  |  2026
# =============================================================================

import socket
import sys
import time
import os
import subprocess
import ipaddress
import threading
import concurrent.futures
import tkinter as tk
from tkinter import ttk, messagebox

# ---- Renk paleti (GitHub Dark temasi) ----
R = {
    "bg":       "#0d1117",
    "panel":    "#161b22",
    "border":   "#30363d",
    "green":    "#3fb950",
    "red":      "#f78166",
    "blue":     "#58a6ff",
    "yellow":   "#d29922",
    "text":     "#e6edf3",
    "muted":    "#8b949e",
    "input":    "#21262d",
    "btn":      "#238636",
    "btn_h":    "#2ea043",
    "btn_stop": "#b62324",
    "cyan":     "#39c5cf",
    "select":   "#1f6feb",
}

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
#  AG / SOCKET YARDIMCILARI
# =============================================================================

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


def tcp_ping(ip, timeout=1.0):
    """Yaygin portlari deneyerek hostin canli olup olmadigini anlar."""
    for port in CANLILIK_PORTLARI:
        if tek_port_tara(ip, port, timeout):
            return True, port
    return False, None


def icmp_ping(ip, timeout=2):
    """ICMP ping gonderir; isletim sistemine gore dogru komut secer."""
    try:
        if os.name == "nt":
            # Windows
            komut = ["ping", "-n", "1", "-w", str(timeout * 1000), ip]
        else:
            # macOS / Linux
            komut = ["ping", "-c", "1", "-W", str(timeout), ip]
        r = subprocess.run(
            komut, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return r.returncode == 0
    except Exception:
        return False


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
        return {
            "ip": ip_str, "canli": True,
            "hostname": hostname_bul(ip_str), "port": port
        }
    return {"ip": ip_str, "canli": False}


# =============================================================================
#  WIDGET YARDIMCILARI
# =============================================================================

def tablo_yap(ust, sutunlar, genislikler):
    """Dark temali, kaydirma cubuklu bir Treeview tablosu olusturur."""
    stil = ttk.Style()
    stil.theme_use("default")
    ad = f"T{id(ust)}.Treeview"
    stil.configure(
        ad,
        background=R["panel"], foreground=R["text"],
        fieldbackground=R["panel"], rowheight=28,
        font=("Consolas", 10),
    )
    stil.configure(
        f"{ad}.Heading",
        background=R["input"], foreground=R["blue"],
        font=("Consolas", 9, "bold"), relief="flat",
    )
    stil.map(ad, background=[("selected", R["select"])])

    cerceve = tk.Frame(ust, bg=R["border"], bd=1)
    cerceve.pack(fill="both", expand=True)

    tablo = ttk.Treeview(cerceve, columns=sutunlar, show="headings", style=ad)
    for i, (s, g) in enumerate(zip(sutunlar, genislikler)):
        tablo.column(s, width=g, anchor="w", stretch=(i == len(sutunlar) - 1))

    sb = ttk.Scrollbar(cerceve, orient="vertical", command=tablo.yview)
    tablo.configure(yscrollcommand=sb.set)
    tablo.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")

    tablo.tag_configure("acik",   foreground=R["green"])
    tablo.tag_configure("kapali", foreground=R["muted"])
    tablo.tag_configure("canli",  foreground=R["green"])
    tablo.tag_configure("ben",    foreground=R["yellow"])
    return tablo


def etiket(ust, metin, renk=None, font=None, **kw):
    """Standart dark tema etiketi olusturur."""
    return tk.Label(
        ust, text=metin,
        fg=renk or R["text"],
        bg=kw.pop("bg", R["bg"]),
        font=font or ("Consolas", 10),
        **kw
    )


def dugme(ust, metin, komut, bg=None, **kw):
    """Stilize buton olusturur."""
    return tk.Button(
        ust, text=metin, command=komut,
        bg=bg or R["btn"], fg="white",
        font=("Consolas", 11, "bold"),
        relief="flat", cursor="hand2",
        activebackground=R["btn_h"],
        activeforeground="white",
        padx=12, pady=6,
        **kw
    )


def giris(ust, genislik=40, **kw):
    """Dark temali metin giris alani olusturur."""
    return tk.Entry(
        ust,
        font=("Consolas", 13),
        bg=R["input"], fg=R["text"],
        insertbackground=R["blue"],
        relief="flat", bd=6,
        width=genislik,
        **kw
    )


def placeholder(w, metin):
    """Giris alanina placeholder (ipucu metni) ekler."""
    w.insert(0, metin)
    w.config(fg=R["muted"])

    def temizle(e):
        if w.cget("fg") == R["muted"]:
            w.delete(0, "end")
            w.config(fg=R["text"])

    def geri(e):
        if not w.get().strip():
            w.insert(0, metin)
            w.config(fg=R["muted"])

    w.bind("<FocusIn>",  temizle)
    w.bind("<FocusOut>", geri)


def ilerleme(ust):
    """Ince, yesil renkli bir ilerleme cubugu olusturur."""
    stil = ttk.Style()
    stil.configure(
        "P.Horizontal.TProgressbar",
        troughcolor=R["input"], background=R["green"], thickness=5
    )
    pb = ttk.Progressbar(
        ust, orient="horizontal",
        mode="determinate",
        style="P.Horizontal.TProgressbar"
    )
    pb.pack(fill="x", pady=(8, 0))
    return pb


# =============================================================================
#  ANA UYGULAMA SINIFI
# =============================================================================

class Uygulama:

    def __init__(self, pencere):
        self.pencere = pencere
        self._pencereyi_hazirla()
        self._baslik()
        self._sekmeler()
        self._durum_cubugu()

    # ---- PENCERE AYARLARI ----

    def _pencereyi_hazirla(self):
        self.pencere.title(
            "Port Tarayici  |  Nida Subasi  |  2026"
        )
        self.pencere.geometry("960x700")
        self.pencere.minsize(800, 580)
        self.pencere.configure(bg=R["bg"])

        # Ekrana ortala
        self.pencere.update_idletasks()
        w = self.pencere.winfo_width()
        h = self.pencere.winfo_height()
        x = (self.pencere.winfo_screenwidth()  - w) // 2
        y = (self.pencere.winfo_screenheight() - h) // 2
        self.pencere.geometry(f"+{x}+{y}")

    # ---- BASLIK ALANI ----

    def _baslik(self):
        f = tk.Frame(self.pencere, bg=R["panel"])
        f.pack(fill="x")
        tk.Frame(f, bg=R["blue"], height=2).pack(fill="x", side="bottom")

        ic = tk.Frame(f, bg=R["panel"])
        ic.pack(padx=24, pady=14, fill="x")

        etiket(
            ic, "PORT TARAYICI",
            renk=R["blue"], font=("Consolas", 20, "bold"),
            bg=R["panel"]
        ).pack(side="left")

        etiket(
            ic, "Guvenlik Acigi Tarama Araci  |  Nida Subasi  |  2026",
            renk=R["muted"], bg=R["panel"],
            font=("Consolas", 9)
        ).pack(side="right")

    # ---- SEKMELER ----

    def _sekmeler(self):
        stil = ttk.Style()
        stil.theme_use("default")
        stil.configure("S.TNotebook", background=R["bg"], borderwidth=0)
        stil.configure(
            "S.TNotebook.Tab",
            background=R["input"], foreground=R["muted"],
            font=("Consolas", 10, "bold"), padding=[18, 8]
        )
        stil.map(
            "S.TNotebook.Tab",
            background=[("selected", R["panel"])],
            foreground=[("selected", R["blue"])]
        )

        nb = ttk.Notebook(self.pencere, style="S.TNotebook")
        nb.pack(fill="both", expand=True, padx=16, pady=(10, 0))

        s1 = tk.Frame(nb, bg=R["bg"])
        s2 = tk.Frame(nb, bg=R["bg"])
        s3 = tk.Frame(nb, bg=R["bg"])
        s4 = tk.Frame(nb, bg=R["bg"])

        nb.add(s1, text="  PORT TARAMA  ")
        nb.add(s2, text="  PING / CANLILIK  ")
        nb.add(s3, text="  AG TARAMASI  ")
        nb.add(s4, text="  HAKKINDA  ")

        self._sekme1(s1)
        self._sekme2(s2)
        self._sekme3(s3)
        self._sekme4(s4)

    # ---- SEKME 1: PORT TARAMA ----

    def _sekme1(self, ust):
        self._port_aktif = False

        gf = tk.Frame(ust, bg=R["bg"])
        gf.pack(fill="x", padx=20, pady=(18, 6))
        etiket(
            gf, "HEDEF IP VEYA DOMAIN",
            renk=R["muted"], font=("Consolas", 8, "bold")
        ).pack(anchor="w")

        sf = tk.Frame(gf, bg=R["bg"])
        sf.pack(fill="x", pady=(4, 0))

        self.p_giris = giris(sf)
        placeholder(self.p_giris, "192.168.1.1  veya  google.com")
        self.p_giris.pack(side="left", fill="x", expand=True, ipady=8)
        self.p_giris.bind("<Return>", lambda e: self._port_baslat())

        self.p_btn = dugme(sf, "  TARA  ", self._port_baslat)
        self.p_btn.pack(side="left", padx=(10, 0))
        self.p_dur = dugme(
            sf, "  DUR  ", self._port_durdur,
            bg=R["btn_stop"], state="disabled"
        )
        self.p_dur.pack(side="left", padx=(6, 0))

        self.p_pb = ilerleme(gf)

        of = tk.Frame(ust, bg=R["bg"])
        of.pack(fill="x", padx=20, pady=(4, 4))
        etiket(
            of, "SONUCLAR",
            renk=R["muted"], font=("Consolas", 8, "bold")
        ).pack(side="left")
        self.p_ozet = etiket(of, "", renk=R["green"])
        self.p_ozet.pack(side="right")

        self.p_tablo = tablo_yap(
            ust,
            ("port", "servis", "durum", "aciklama"),
            (70, 120, 110, 500)
        )
        for s, b in [
            ("port",     "PORT"),
            ("servis",   "SERVIS"),
            ("durum",    "DURUM"),
            ("aciklama", "ACIKLAMA"),
        ]:
            self.p_tablo.heading(s, text=b)

    def _port_baslat(self):
        if self._port_aktif:
            return
        hedef = self.p_giris.get().strip()
        if not hedef or self.p_giris.cget("fg") == R["muted"]:
            messagebox.showwarning("Eksik", "Hedef adres gir.")
            return
        for r in self.p_tablo.get_children():
            self.p_tablo.delete(r)
        self.p_ozet.config(text="")
        self.p_btn.config(state="disabled")
        self.p_dur.config(state="normal")
        self._port_aktif = True
        threading.Thread(
            target=self._port_is, args=(hedef,), daemon=True
        ).start()

    def _port_durdur(self):
        self._port_aktif = False
        self._durum("Durduruldu.", R["yellow"])
        self.p_btn.config(state="normal")
        self.p_dur.config(state="disabled")

    def _port_is(self, hedef):
        self._durum("Cozumleniyor...", R["yellow"])
        ip = ip_cozumle(hedef)
        if not ip:
            self.pencere.after(0, lambda: messagebox.showerror(
                "Hata", f"'{hedef}' cozumlenemedi."
            ))
            self._port_durdur()
            return

        self._durum(f"Taranıyor: {hedef} ({ip})", R["blue"])
        portlar = sorted(PORTLAR.keys())
        acik = kapali = tamamlanan = 0

        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as ex:
            fmap = {ex.submit(tek_port_tara, ip, p): p for p in portlar}
            for future in concurrent.futures.as_completed(fmap):
                if not self._port_aktif:
                    break
                p = fmap[future]
                ok = future.result() if not future.exception() else False
                servis, aciklama = PORTLAR[p]
                if ok:
                    acik   += 1
                else:
                    kapali += 1
                tamamlanan += 1
                yuzde = int(tamamlanan / len(portlar) * 100)
                a, k = acik, kapali

                self.pencere.after(0, lambda pp=p, ss=servis, oo=ok,
                                          aa=aciklama, yy=yuzde, av=a, kv=k: (
                    self.p_tablo.insert(
                        "", "end",
                        values=(pp, ss, "ACIK" if oo else "KAPALI", aa),
                        tags=("acik" if oo else "kapali",)
                    ),
                    self.p_pb.config(value=yy),
                    self.p_ozet.config(text=f"Acik: {av}   Kapali: {kv}")
                ))

        if self._port_aktif:
            self._durum(
                f"Tamamlandi — {acik} acik, {kapali} kapali", R["green"]
            )
        self._port_aktif = False
        self.pencere.after(0, lambda: (
            self.p_btn.config(state="normal"),
            self.p_dur.config(state="disabled")
        ))

    # ---- SEKME 2: PING / CANLILIK ----

    def _sekme2(self, ust):
        self._ping_aktif = False

        gf = tk.Frame(ust, bg=R["bg"])
        gf.pack(fill="x", padx=20, pady=(18, 6))
        etiket(
            gf, "HEDEF IP VEYA DOMAIN",
            renk=R["muted"], font=("Consolas", 8, "bold")
        ).pack(anchor="w")

        sf = tk.Frame(gf, bg=R["bg"])
        sf.pack(fill="x", pady=(4, 0))

        self.pi_giris = giris(sf)
        placeholder(self.pi_giris, "8.8.8.8  veya  google.com")
        self.pi_giris.pack(side="left", fill="x", expand=True, ipady=8)
        self.pi_giris.bind("<Return>", lambda e: self._ping_baslat())

        self.pi_btn = dugme(sf, "  TEST ET  ", self._ping_baslat)
        self.pi_btn.pack(side="left", padx=(10, 0))

        self.pi_pb = ilerleme(gf)

        kf = tk.Frame(ust, bg=R["bg"])
        kf.pack(fill="x", padx=20, pady=12)

        self.k_icmp  = self._kart(kf, "ICMP PING",     "—")
        self.k_tcp   = self._kart(kf, "TCP PORT PING", "—")
        self.k_host  = self._kart(kf, "HOSTNAME",      "—")
        self.k_genel = self._kart(kf, "GENEL SONUC",   "—", buyuk=True)

    def _kart(self, ust, baslik, deger, buyuk=False):
        f = tk.Frame(
            ust, bg=R["panel"],
            highlightbackground=R["border"],
            highlightthickness=1
        )
        f.pack(fill="x", pady=4, ipady=6)

        ic = tk.Frame(f, bg=R["panel"])
        ic.pack(padx=14, pady=4, fill="x")

        etiket(
            ic, baslik, renk=R["muted"],
            font=("Consolas", 8, "bold"), bg=R["panel"]
        ).pack(anchor="w")

        font = ("Consolas", 14, "bold") if buyuk else ("Consolas", 11)
        lb   = etiket(ic, deger, renk=R["text"], font=font, bg=R["panel"])
        lb.pack(anchor="w", pady=(2, 0))
        return lb

    def _ping_baslat(self):
        if self._ping_aktif:
            return
        hedef = self.pi_giris.get().strip()
        if not hedef or self.pi_giris.cget("fg") == R["muted"]:
            messagebox.showwarning("Eksik", "Hedef adres gir.")
            return
        for k in (self.k_icmp, self.k_tcp, self.k_host, self.k_genel):
            k.config(text="Bekleniyor...", fg=R["muted"])
        self.pi_pb.config(value=0)
        self.pi_btn.config(state="disabled")
        self._ping_aktif = True
        threading.Thread(
            target=self._ping_is, args=(hedef,), daemon=True
        ).start()

    def _ping_is(self, hedef):
        ip = ip_cozumle(hedef)
        if not ip:
            self.pencere.after(0, lambda: messagebox.showerror(
                "Hata", f"'{hedef}' cozumlenemedi."
            ))
            self._ping_bitis()
            return

        self._durum(f"Test ediliyor: {hedef} ({ip})", R["blue"])

        # ICMP
        self.pencere.after(0, lambda: (
            self.k_icmp.config(text="ICMP gonderiliyor...", fg=R["muted"]),
            self.pi_pb.config(value=10)
        ))
        t0     = time.time()
        icmp_ok = icmp_ping(ip)
        ms      = (time.time() - t0) * 1000
        txt_icmp = (f"Basarili ({ms:.0f} ms)"
                    if icmp_ok else "Cevap alinamadi")
        self.pencere.after(0, lambda t=txt_icmp, c=R["green"] if icmp_ok else R["muted"]: (
            self.k_icmp.config(text=t, fg=c),
            self.pi_pb.config(value=35)
        ))

        # TCP
        self.pencere.after(0, lambda: self.k_tcp.config(
            text="TCP port kontrolu...", fg=R["muted"]
        ))
        t0     = time.time()
        tcp_ok, port = tcp_ping(ip)
        ms     = (time.time() - t0) * 1000
        if tcp_ok:
            servis   = PORTLAR.get(port, ("?",))[0]
            txt_tcp  = f"Basarili — Port {port}/{servis} ({ms:.0f} ms)"
        else:
            txt_tcp  = "Hicbir yaygin portta yanit yok"
        self.pencere.after(0, lambda t=txt_tcp, c=R["green"] if tcp_ok else R["muted"]: (
            self.k_tcp.config(text=t, fg=c),
            self.pi_pb.config(value=65)
        ))

        # Hostname
        self.pencere.after(0, lambda: self.k_host.config(
            text="Hostname aranıyor...", fg=R["muted"]
        ))
        hostname = hostname_bul(ip)
        self.pencere.after(0, lambda h=hostname: (
            self.k_host.config(text=h, fg=R["cyan"]),
            self.pi_pb.config(value=90)
        ))

        # Genel sonuc
        canli = icmp_ok or tcp_ok
        if canli:
            gm = f"HOST ERISEBILIR\n{ip}  —  {hostname}"
            gc = R["green"]
            self._durum(f"{hedef} erisebilir.", R["green"])
        else:
            gm = f"HOST YANIT VERMIYOR\n{ip}  —  {hostname}"
            gc = R["red"]
            self._durum(f"{hedef} yanit vermedi.", R["muted"])

        self.pencere.after(0, lambda t=gm, c=gc: (
            self.k_genel.config(text=t, fg=c),
            self.pi_pb.config(value=100)
        ))
        self._ping_bitis()

    def _ping_bitis(self):
        self._ping_aktif = False
        self.pencere.after(0, lambda: self.pi_btn.config(state="normal"))

    # ---- SEKME 3: AG TARAMASI ----

    def _sekme3(self, ust):
        self._ag_aktif  = False
        self._kendi_ip  = yerel_ip_bul()
        parca           = self._kendi_ip.rsplit(".", 1)[0]
        self._onerilen  = f"{parca}.0/24"

        bf = tk.Frame(ust, bg=R["panel"])
        bf.pack(fill="x", padx=20, pady=(16, 0))
        ic = tk.Frame(bf, bg=R["panel"])
        ic.pack(padx=14, pady=8, fill="x")

        etiket(
            ic, "Kendi IP Adresin:",
            renk=R["muted"], font=("Consolas", 9), bg=R["panel"]
        ).pack(side="left")
        etiket(
            ic, self._kendi_ip,
            renk=R["yellow"], font=("Consolas", 12, "bold"), bg=R["panel"]
        ).pack(side="left", padx=(8, 0))

        gf = tk.Frame(ust, bg=R["bg"])
        gf.pack(fill="x", padx=20, pady=(10, 4))
        etiket(
            gf, "AG ARALIGI (CIDR)",
            renk=R["muted"], font=("Consolas", 8, "bold")
        ).pack(anchor="w")

        sf = tk.Frame(gf, bg=R["bg"])
        sf.pack(fill="x", pady=(4, 0))

        self.ag_giris = giris(sf, genislik=30)
        self.ag_giris.insert(0, self._onerilen)
        self.ag_giris.pack(side="left", fill="x", expand=True, ipady=8)
        self.ag_giris.bind("<Return>", lambda e: self._ag_baslat())

        self.ag_btn = dugme(sf, "  TARA  ", self._ag_baslat)
        self.ag_btn.pack(side="left", padx=(10, 0))
        self.ag_dur = dugme(
            sf, "  DUR  ", self._ag_durdur,
            bg=R["btn_stop"], state="disabled"
        )
        self.ag_dur.pack(side="left", padx=(6, 0))

        self.ag_pb = ilerleme(gf)

        of = tk.Frame(ust, bg=R["bg"])
        of.pack(fill="x", padx=20, pady=(4, 4))
        etiket(
            of, "BULUNAN CIHAZLAR",
            renk=R["muted"], font=("Consolas", 8, "bold")
        ).pack(side="left")
        self.ag_ozet = etiket(of, "", renk=R["green"])
        self.ag_ozet.pack(side="right")

        self.ag_tablo = tablo_yap(
            ust,
            ("no", "ip", "hostname", "durum"),
            (40, 150, 280, 300)
        )
        for s, b in [
            ("no",       "#"),
            ("ip",       "IP"),
            ("hostname", "HOSTNAME"),
            ("durum",    "DURUM"),
        ]:
            self.ag_tablo.heading(s, text=b)
        self.ag_tablo.column("no", anchor="center", width=40, stretch=False)

    def _ag_baslat(self):
        if self._ag_aktif:
            return
        ag_str = self.ag_giris.get().strip()
        if not ag_str:
            messagebox.showwarning("Eksik", "Ag araligi gir.")
            return
        try:
            ag = ipaddress.ip_network(ag_str, strict=False)
        except ValueError:
            messagebox.showerror(
                "Hata", f"Gecersiz CIDR: {ag_str}\nOrnek: 192.168.1.0/24"
            )
            return
        for r in self.ag_tablo.get_children():
            self.ag_tablo.delete(r)
        self.ag_ozet.config(text="")
        self.ag_btn.config(state="disabled")
        self.ag_dur.config(state="normal")
        self.ag_pb.config(value=0)
        self._ag_aktif = True
        threading.Thread(
            target=self._ag_is, args=(ag,), daemon=True
        ).start()

    def _ag_durdur(self):
        self._ag_aktif = False
        self._durum("Durduruldu.", R["yellow"])
        self.ag_btn.config(state="normal")
        self.ag_dur.config(state="disabled")

    def _ag_is(self, ag):
        ip_listesi = [str(ip) for ip in ag.hosts()]
        toplam     = len(ip_listesi)
        self._durum(f"{ag} — {toplam} IP taranıyor", R["blue"])

        tamamlanan = 0
        sayac      = [0]

        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as ex:
            fmap = {ex.submit(tekli_host_tara, ip): ip for ip in ip_listesi}
            for future in concurrent.futures.as_completed(fmap):
                if not self._ag_aktif:
                    break
                tamamlanan += 1
                try:
                    s = future.result()
                    if s["canli"]:
                        sayac[0] += 1
                        no       = sayac[0]
                        ip_str   = s["ip"]
                        hostname = s.get("hostname", "Bilinmiyor")
                        port     = s.get("port")

                        if ip_str == self._kendi_ip:
                            durum = "Sen"
                            tag   = "ben"
                        elif port:
                            servis = PORTLAR.get(port, ("?",))[0]
                            durum  = f"Canli (TCP:{port}/{servis})"
                            tag    = "canli"
                        else:
                            durum = "Canli"
                            tag   = "canli"

                        y  = int(tamamlanan / toplam * 100)
                        cv = sayac[0]
                        self.pencere.after(
                            0,
                            lambda n=no, i=ip_str, h=hostname,
                                   d=durum, t=tag, yy=y, c=cv: (
                                self.ag_tablo.insert(
                                    "", "end",
                                    values=(n, i, h, d), tags=(t,)
                                ),
                                self.ag_pb.config(value=yy),
                                self.ag_ozet.config(text=f"{c} cihaz")
                            )
                        )
                    else:
                        y = int(tamamlanan / toplam * 100)
                        self.pencere.after(
                            0, lambda yy=y: self.ag_pb.config(value=yy)
                        )
                except Exception:
                    pass

        if self._ag_aktif:
            n = sayac[0]
            self._durum(
                f"Tamamlandi — {n} cihaz / {toplam} IP", R["green"]
            )
        self._ag_aktif = False
        self.pencere.after(0, lambda: (
            self.ag_btn.config(state="normal"),
            self.ag_dur.config(state="disabled")
        ))

    # ---- SEKME 4: HAKKINDA ----

    def _sekme4(self, ust):
        f = tk.Frame(ust, bg=R["bg"])
        f.pack(expand=True)

        bilgiler = [
            ("PORT TARAYICI", ("Consolas", 22, "bold"), R["blue"]),
            ("Guvenlik Acigi Tarama Araci  —  GUI Surumu",
             ("Consolas", 11), R["muted"]),
            ("", None, None),
            ("Hazirlayan  :  Nida Subasi", ("Consolas", 13, "bold"), R["green"]),
            ("Surumu      :  2.0  |  2026", ("Consolas", 11), R["text"]),
            ("Dil         :  Python 3  (sadece standart kutuphane)",
             ("Consolas", 11), R["text"]),
            ("Platform    :  Windows · macOS · Linux",
             ("Consolas", 11), R["text"]),
            ("", None, None),
            ("Ozellikler:", ("Consolas", 11, "bold"), R["yellow"]),
            ("  •  Paralel port tarama  (TCP Connect, 50 is parcacigi)",
             ("Consolas", 10), R["text"]),
            ("  •  ICMP + TCP canlilik testi",
             ("Consolas", 10), R["text"]),
            ("  •  Yerel ag kesfetme  (/24 CIDR destegi)",
             ("Consolas", 10), R["text"]),
            ("  •  Dark tema arayuz  (GitHub Dark palet)",
             ("Consolas", 10), R["text"]),
            ("  •  Gercek zamanli ilerleme gostergesi",
             ("Consolas", 10), R["text"]),
        ]

        for metin, font, renk in bilgiler:
            if metin == "":
                tk.Frame(f, bg=R["bg"], height=10).pack()
                continue
            tk.Label(
                f, text=metin, fg=renk, bg=R["bg"],
                font=font or ("Consolas", 10)
            ).pack(anchor="w", padx=60, pady=1)

    # ---- DURUM CUBUGU ----

    def _durum_cubugu(self):
        f = tk.Frame(self.pencere, bg=R["panel"], height=32)
        f.pack(fill="x", side="bottom")
        f.pack_propagate(False)

        tk.Frame(f, bg=R["border"], height=1).pack(fill="x")

        ic = tk.Frame(f, bg=R["panel"])
        ic.pack(fill="both", expand=True, padx=16)

        self._d_lbl = etiket(ic, "Hazir", renk=R["muted"], bg=R["panel"])
        self._d_lbl.pack(side="left", pady=4)

        # Imza — sag alt kose
        etiket(
            ic, "Nida Subasi  |  2026",
            renk=R["border"], font=("Consolas", 8), bg=R["panel"]
        ).pack(side="right", pady=4)

    def _durum(self, metin, renk=None):
        self.pencere.after(0, lambda: self._d_lbl.config(
            text=metin, fg=renk or R["muted"]
        ))


# =============================================================================
#  GIRIS NOKTASI
# =============================================================================

def main():
    pencere = tk.Tk()

    # Uygulama ikonu — varsa yukle, yoksa sessizce atla
    try:
        pencere.iconbitmap(default="icon.ico")
    except Exception:
        pass

    Uygulama(pencere)
    pencere.protocol("WM_DELETE_WINDOW", pencere.destroy)
    pencere.mainloop()


if __name__ == "__main__":
    main()
