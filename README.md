[README.md](https://github.com/user-attachments/files/29467907/README.md)
<div align="center">

<img src="https://capsule-render.vercel.app/api?type=shark&color=0:0d1117,30:0d2b0d,60:00ff41,100:0d1117&height=200&section=header&text=PORT+SC4NNЕР&fontSize=54&fontColor=00ff41&fontAlignY=60&animation=blinking&desc=%E2%96%BA+TCP+Connect+%7C+ICMP+Ping+%7C+Ag+Kesfi+%E2%97%84&descAlignY=82&descSize=15&descColor=3fb950" width="100%"/>

</div>

<div align="center">

[![Typing SVG](https://readme-typing-svg.demolab.com?font=Share+Tech+Mono&weight=400&size=18&pause=600&color=00FF41&center=true&vCenter=true&width=700&height=45&lines=%5B%2B%5D+Hedef+taranıyor...+192.168.1.0%2F24;%5B%2B%5D+Port+80+%E2%86%92+ACIK+%28HTTP%29;%5B%2B%5D+Port+443+%E2%86%92+ACIK+%28HTTPS%29;%5B%2B%5D+Port+22+%E2%86%92+ACIK+%28SSH%29;%5B%2B%5D+14+aktif+cihaz+bulundu.;%5B%2B%5D+Tarama+tamamlandi.+2.4+sn)](https://git.io/typing-svg)

<br/>

![Python](https://img.shields.io/badge/Python-3.6%2B-00ff41?style=flat-square&logo=python&logoColor=0d1117)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-3fb950?style=flat-square&logo=python&logoColor=white)
![Terminal](https://img.shields.io/badge/CMD-Terminal_Modu-00ff41?style=flat-square&logo=gnubash&logoColor=0d1117)
![Socket](https://img.shields.io/badge/Protokol-TCP+%2F+ICMP-58a6ff?style=flat-square&logo=cloudflare&logoColor=white)
![Threads](https://img.shields.io/badge/50+Thread-Paralel_Tarama-d29922?style=flat-square&logo=speedtest&logoColor=white)
![No Deps](https://img.shields.io/badge/Sıfır_Bağımlılık-Standart_Lib-3fb950?style=flat-square&logo=checkmarx&logoColor=white)

</div>

---

<div align="center">

```
╔══════════════════════════════════════════════════════════════╗
║      ██████╗  ██████╗ ██████╗ ████████╗    ███████╗ ██████╗  ║
║      ██╔══██╗██╔═══██╗██╔══██╗╚══██╔══╝    ██╔════╝██╔════╝  ║
║      ██████╔╝██║   ██║██████╔╝   ██║       ███████╗██║       ║
║      ██╔═══╝ ██║   ██║██╔══██╗   ██║       ╚════██║██║       ║
║      ██║     ╚██████╔╝██║  ██║   ██║       ███████║╚██████╗  ║
║      ╚═╝      ╚═════╝ ╚═╝  ╚═╝   ╚═╝       ╚══════╝ ╚═════╝  ║
╠══════════════════════════════════════════════════════════════╣
║     Güvenlik Açığı Tarama Aracı  |  Nida Subaşı  |  2026    ║
╚══════════════════════════════════════════════════════════════╝
```

</div>

---

## Proje Nedir?

Hedef IP veya domain veriyorsun, program hangi portların açık olduğunu söylüyor. Ping yapıyor, hostname çözümlüyor, yerel ağdaki cihazları buluyor. Bunları yapmak için Python'un standart kütüphanesinden başka hiçbir şey kurmanı gerektirmiyor.

İki ayrı versiyonu var: terminal çıktısıyla renk kodlu bir CMD versiyonu, bir de sekme tabanlı Tkinter arayüzüyle GUI versiyonu. İkisi de aynı tarama motorunu kullanıyor, sadece sunum katmanı farklı.

---

## 🖥️ İki Versiyon

<div align="center">

| | `guvenlik_tarayici_cmd.py` | `guvenlik_tarayici_gui.py` |
|:---:|:---|:---|
| **Arayüz** | Renkli terminal çıktısı (ANSI) | Tkinter pencere — sekmeli |
| **Hız** | Biraz daha hızlı (overhead yok) | Gerçek zamanlı ilerleme çubuğu |
| **Kullanım** | `python guvenlik_tarayici_cmd.py` | Çift tıklama veya `python ...gui.py` |
| **Çıktı** | Tablo formatında stdout | DataTable + scrollbar |
| **İptal** | Ctrl+C | "DUR" butonu |

</div>

---

## ⚡ Özellikler

```
recon
  └── Port Tarama      →  20 yaygın port, TCP Connect, 50 paralel thread
      Ping / Canlılık  →  ICMP ping + TCP port ping (çift kontrol)
      Ağ Taraması      →  /24 CIDR, 100 thread, ilerleme çubuğu
      Hostname Çözüm   →  Her IP için ters DNS sorgusu
```

### 🔴 Port Tarama

20 yaygın portu paralel olarak tarıyor. Sonuçları anında gösteriyor; hangisinin açık hangisinin kapalı olduğunu, servis adını ve ne işe yaradığını söylüyor.

```
PORT     SERVİS         DURUM      AÇIKLAMA
21       FTP            KAPALI     Dosya Transfer Protokolü
22       SSH            ACIK  ◄    Güvenli Uzak Bağlantı
80       HTTP           ACIK  ◄    Web Sunucusu
443      HTTPS          ACIK  ◄    Güvenli Web (SSL/TLS)
3389     RDP            KAPALI     Windows Uzak Masaüstü
...
```

### 🟡 Ping / Canlılık Testi

İki katmanlı kontrol yapıyor. Önce ICMP ping deniyor. Güvenlik duvarı ICMP'yi engelliyorsa 8 yaygın porta TCP bağlantısı deniyor. İkisi de başarısız olursa "yanıt vermiyor" diyor. Hostname de sorguluyor.

### 🟢 Ağ Taraması

`192.168.1.0/24` gibi bir CIDR giriyorsun. 254 IP'yi 100 iş parçacığıyla aynı anda tarıyor, aktif cihazları buluyor, kendi IP'ni sarıyla işaretliyor, bulduğu cihazı TCP üzerinden tespit ettiyse hangi port üzerinden gösteriyor.

---

## 🗺️ Taranan Portlar

<div align="center">

| Port | Servis | Port | Servis |
|:----:|:------:|:----:|:------:|
| 21 | FTP | 443 | HTTPS |
| 22 | SSH | 445 | SMB |
| 23 | Telnet ⚠️ | 1433 | MSSQL |
| 25 | SMTP | 3306 | MySQL |
| 53 | DNS | 3389 | RDP |
| 80 | HTTP | 5432 | PostgreSQL |
| 110 | POP3 | 5900 | VNC |
| 135 | RPC | 6379 | Redis |
| 139 | NetBIOS | 8080 | HTTP-Alt |
| 143 | IMAP | 8443 | HTTPS-Alt |

</div>

---

## 🚀 Çalıştırma

Python 3.6+ yeterli. Pip, kurulum, sanal ortam — hiçbiri gerekmiyor.

**CMD Versiyonu:**
```bash
# Windows
python guvenlik_tarayici_cmd.py

# macOS / Linux
python3 guvenlik_tarayici_cmd.py
```

**GUI Versiyonu:**
```bash
# Windows — çift tıklama da çalışır
python guvenlik_tarayici_gui.py

# macOS / Linux
python3 guvenlik_tarayici_gui.py
```

> **Not:** macOS'ta ICMP ping `sudo` gerektirebilir.
> `sudo python3 guvenlik_tarayici_cmd.py`

---

## 📐 Teknik Detaylar

```python
# Tarama motoru — her iki versiyonda da aynı
def tek_port_tara(ip, port, timeout=1.0):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    return s.connect_ex((ip, port)) == 0

# Paralel tarama — 50 thread
with ThreadPoolExecutor(max_workers=50) as ex:
    results = {ex.submit(tek_port_tara, ip, p): p for p in PORTLAR}

# ICMP platform farkı — Windows vs macOS/Linux otomatik algılama
komut = ["ping", "-n", "1", ip]        # Windows
komut = ["ping", "-c", "1", "-W", ip]  # macOS / Linux
```

**Kullanılan modüller — hepsi standart kütüphane:**

```
socket          → TCP bağlantı ve hostname çözümü
subprocess      → ICMP ping komutu
ipaddress       → CIDR aralığı hesaplama
concurrent.futures → ThreadPoolExecutor (paralel tarama)
threading       → GUI'de arka plan iş parçacıkları
tkinter         → GUI arayüzü
```

---

## 📁 Dosya Yapısı

```
Guvenlik-Tarayici/
│
├── guvenlik_tarayici_gui.py     # Tkinter GUI — sekmeli arayüz
├── guvenlik_tarayici_cmd.py     # Terminal versiyonu — ANSI renkler
└── NASIL_CALISTIRILIR.txt       # Kurulum ve kullanım kılavuzu
```

---

## ⚠️ Sorumluluk Reddi

Bu araç yalnızca kendi ağında veya iznin olan sistemlerde kullanılmak üzere geliştirilmiştir. İzinsiz ağ taraması birçok ülkede yasaldır; etik ve yasal sınırlar içinde kullan.

---

<div align="center">

<br/>

```
[ recon → scan → analyze → report ]
```

<br/>

[![Nida Subaşı](https://img.shields.io/badge/Nida_Subaşı-00ff41?style=for-the-badge&logo=github&logoColor=0d1117)](https://github.com/NidaSu0)
![Üniversite Bitirme Projesi](https://img.shields.io/badge/Üniversite_Bitirme_Projesi-0d1117?style=for-the-badge&logo=graduation-cap&logoColor=00ff41)
![2026](https://img.shields.io/badge/2026-0d1117?style=for-the-badge&logoColor=00ff41)

<br/>

<img src="https://capsule-render.vercel.app/api?type=shark&color=0:0d1117,50:0d2b0d,100:0d1117&height=120&section=footer&reversal=true&animation=twinkling" width="100%"/>

</div>
