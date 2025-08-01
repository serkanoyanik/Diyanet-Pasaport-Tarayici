# Diyanet Pasaport Kurulum Uygulaması - Detaylı İnceleme

## 📋 Genel Bakış

**Diyanet Pasaport Kurulum** uygulaması, Diyanet İşleri Başkanlığı için geliştirilmiş, pasaport tarayıcı sisteminin kurulumunu ve yönetimini sağlayan GTK3 tabanlı bir masaüstü uygulamasıdır.

## 🎯 Ana Amaç

Bu uygulama, Canon LiDE200 tarayıcı ile pasaport tarama işlemleri için gerekli olan Java tabanlı pasaport tarayıcı yazılımının sistem kurulumunu otomatikleştirir.

## 🏗️ Uygulama Yapısı

### 📁 Geliştirme Dizin Yapısı

```
diyanet_pasaport_kurulum/
├── app.py                          # Ana uygulama dosyası
├── __main__.py                     # Giriş noktası
├── ui/                             # UI dosyaları
├── icons/                          # Uygulama ikonları
├── script/                         # Kurulum betikleri
├── source/                         # Java kaynak dosyaları
└── deb_build/                     # DEB paketi yapısı
```

## 🔧 Teknik Özellikler

### 🐍 Programlama Dili ve Framework
- **Ana Dil**: Python 3
- **GUI Framework**: GTK3 (PyGObject)
- **Terminal Widget**: VTE Terminal
- **Stil**: CSS ile özelleştirilmiş arayüz

### 💻 Sistem Gereksinimleri
- **Python**: python3, python3-gi
- **GTK**: gir1.2-gtk-3.0, gir1.2-vte-2.91
- **Java**: oracle-java8-jre
- **OCR**: tesseract-ocr, tesseract-ocr-tur
- **Donanım**: pcscd, libacsccid1
- **Diğer**: dialog

## 🎨 Kullanıcı Arayüzü

### 📱 Ana Pencere Özellikleri
- **Boyut**: 800x600 piksel
- **Layout**: Yatay düzen (sol panel + terminal)
- **Sol Panel**: Butonlar ve DIB logosu
- **Sağ Panel**: Terminal widget (kurulum çıktıları için)

### 🔘 Butonlar
1. **"Kurulumu Başlat"**: Tam kurulum işlemi
2. **"Hakkında"**: Dropdown menü (Uygulama Hakkında, Uygulamayı Kaldır)
3. **"Screenshot"**: Ekran görüntüsü alma

### 🎨 Görsel Tasarım
- **CSS Stilleri**: Yeşil renkli, yuvarlak köşeli butonlar
- **Renk Şeması**: 
  - Ana butonlar: #00C851 (yeşil)
  - Hover: #00A843
  - Active: #007E33
- **Terminal**: Koyu tema (#2E2E2E arka plan)
- **Dropdown Menü**: Yuvarlak köşeli, gölgeli menü tasarımı
- **İkonlar**: SVG ikonlar ile modern görünüm

## ⚙️ Ana Fonksiyonlar

### 🔍 Tarayıcı Kontrolü
```python
def check_scanner(self):
    # Canon LiDE200 tarayıcısının varlığını kontrol eder
    # scanimage -L komutu ile tarayıcı listesi alınır
    # Canon LiDE200 veya benzer Canon tarayıcıları aranır
```

### 👥 Kullanıcı Yönetimi
```python
def get_all_users(self):
    # Yerel kullanıcıları /etc/passwd'den alır
    # Domain kullanıcılarını /home/DIB/ altından alır
    # getent passwd ile domain kullanıcılarını kontrol eder
```

### 🛠️ Kurulum İşlemleri
1. **Grup Oluşturma**: `hacpasaport` grubu oluşturulur
2. **Kullanıcı Ekleme**: Seçilen kullanıcı gruba eklenir
3. **Dosya İzinleri**: Gerekli dosyalara çalıştırma izni verilir
4. **Masaüstü Kısayolu**: Kullanıcının masaüstüne kısayol eklenir
5. **Java Kontrolü**: oracle-java8-jre=8u241 sürümü kontrol edilir ve kurulur
6. **USB Tespiti**: Canon LiDE tarayıcısı otomatik tespit edilir
7. **sc.sh Güncelleme**: USB bağlantı noktası otomatik güncellenir

### 📸 Screenshot Özelliği
- **Masaüstü Desteği**: XFCE, GNOME, KDE
- **Araçlar**: gnome-screenshot, xfce4-screenshooter, spectacle
- **Alternatif**: GTK API ile pencere görüntüsü alma

## 🔄 Kurulum Süreci

### 📋 Kurulum Adımları (install.sh)
1. **Dizin Kontrolü**: `/opt/HacPasaport` varlığı kontrol edilir
2. **Dosya İzinleri**: Gerekli dosyalara çalıştırma izni verilir
3. **Grup Yönetimi**: `hacpasaport` grubu oluşturulur
4. **Kullanıcı Ekleme**: Seçilen kullanıcı gruba eklenir
5. **Masaüstü Kısayolu**: Kullanıcının masaüstüne kısayol eklenir
6. **Güvenlik Ayarları**: GNOME için güvenlik işaretleme

### 🎯 Kullanıcı Ekleme Modu
- **Parametre**: `adduseronly` ile sadece kullanıcı ekleme
- **Grup Kontrolü**: Kullanıcının zaten grupta olup olmadığı kontrol edilir
- **Bilgilendirme**: Grup üyeliği hakkında kullanıcıya bilgi verilir

## 🖥️ Masaüstü Ortamı Desteği

### 🔍 Otomatik Tespit
```python
def detect_desktop_environment(self):
    # XDG_CURRENT_DESKTOP değişkenini kontrol eder
    # DESKTOP_SESSION değişkenini kontrol eder
    # ps komutu ile çalışan process'leri kontrol eder
    # Config dosyalarını kontrol eder
```

### 📱 Desteklenen Ortamlar
- **XFCE**: xfce4-screenshooter ile screenshot
- **GNOME**: gnome-screenshot ile screenshot
- **KDE**: spectacle ile screenshot
- **Diğer**: Genel araçlarla fallback

## 📦 DEB Paketi Özellikleri

### 📋 Paket Bilgileri
- **Paket Adı**: diyanet-pasaport-kurulum
- **Versiyon**: 1.1.0
- **Mimari**: amd64
- **Bölüm**: utils
- **Öncelik**: optional

### 🔗 Bağımlılıklar
- python3, python3-gi
- gir1.2-gtk-3.0, gir1.2-vte-2.91
- pcscd, tesseract-ocr, tesseract-ocr-tur
- libacsccid1, dialog, oracle-java8-jre





### 📁 Yeni DEB Paketi Yapısı
```
/opt/HacPasaport/
├── app/                          # GUI uygulama dosyaları
│   ├── app.py                    # Ana uygulama
│   ├── __main__.py               # Giriş noktası
│   ├── ui/                       # UI dosyaları
│   │   ├── window.ui
│   │   └── styles.css
│   ├── icons/                    # İkon dosyaları
│   │   ├── dib_logo.png
│   │   ├── camera.png
│   │   └── [diğer ikonlar]
│   └── script/                   # Kurulum betikleri
│       └── install.sh
├── pasaport.sh                   # Java uygulaması başlatıcı
├── sc.sh                         # Tarayıcı kontrol betiği
├── swingUI.jar                   # Java dosyaları (düz konumlandırma)
├── tess4j-4.5.5.jar
├── opencv-3.4.2-0.jar
├── tessdata/                     # OCR dil dosyaları
└── [diğer Java dosyaları]
```

### 🚀 Çalıştırma
```bash
#!/bin/bash
cd /opt/HacPasaport
exec /usr/bin/java -jar /opt/HacPasaport/swingUI.jar
```

## 🔧 Özel Özellikler

### 🎨 CSS Özelleştirme
- **Buton Stilleri**: Yeşil renkli, yuvarlak köşeli
- **Hover Efektleri**: Gölge ve renk değişimi
- **Focus Stilleri**: Erişilebilirlik için özel focus

### 📱 Responsive Tasarım
- **Sol Panel**: 180px genişlik
- **Terminal**: Dinamik boyutlandırma
- **Header Bar**: Modern GTK3 header bar

### 🔒 Güvenlik Özellikleri
- **pkexec**: Kurulum için sudo yetkisi
- **Grup Yönetimi**: hacpasaport grubu ile yetki kontrolü
- **Dosya İzinleri**: Güvenli dosya izinleri
- **Standart Kaldırma**: `dpkg -r diyanet-pasaport-kurulum` ile güvenli kaldırma
- **Yetki Kontrolü**: GUI'den kaldırma için `pkexec` ile yetki kontrolü

### 🔧 Java Uygulaması Düzeltmeleri (v1.1.0)
- **Çalışma Dizini**: Java uygulaması `/opt/HacPasaport` dizininde çalışıyor
- **sc.sh Erişimi**: `./sc.sh` artık doğru dosyayı buluyor
- **Canon LiDE 210**: Tarayıcı sorunsuz çalışıyor
- **USB Tespiti**: Otomatik USB bağlantı noktası tespiti
- **sc.sh Güncelleme**: USB bağlantı noktası otomatik güncelleniyor

## 📊 Performans ve Optimizasyon

### ⚡ Hızlı Başlatma
- **Lazy Loading**: Kaynaklar gerektiğinde yüklenir
- **Threading**: Arka plan işlemleri için threading
- **GLib.idle_add**: UI güncellemeleri için asenkron

### 🎯 Bellek Yönetimi
- **VTE Terminal**: Scrollback limiti (-1 = sınırsız)
- **Pixbuf**: Logo yükleme için optimize edilmiş boyutlar
- **Dialog Yönetimi**: Modal dialog'lar için proper cleanup

## 🔍 Hata Yönetimi

### ⚠️ Hata Kontrolü
- **Dosya Varlığı**: Kritik dosyaların varlığı kontrol edilir
- **Komut Başarısı**: Subprocess çıktıları kontrol edilir
- **Kullanıcı Varlığı**: Kullanıcının sistemde var olup olmadığı kontrol edilir

### 📝 Logging
- **Terminal Çıktısı**: Tüm işlemler terminal'de gösterilir
- **Hata Mesajları**: Kullanıcı dostu hata mesajları
- **Başarı Mesajları**: İşlem sonuçları hakkında bilgilendirme

## 🎯 Kullanım Senaryoları

### 🏢 Kurumsal Ortam
- **Domain Kullanıcıları**: Active Directory entegrasyonu
- **Toplu Kurulum**: Birden fazla kullanıcı için kurulum
- **Güvenlik**: Grup tabanlı yetki yönetimi

### 🏠 Bireysel Kullanım
- **Basit Kurulum**: Tek kullanıcı için hızlı kurulum
- **Screenshot**: Sorun giderme için ekran görüntüsü
- **Bilgilendirme**: Kullanıcı dostu mesajlar

## 🔮 Gelecek Geliştirmeler

### 📈 Potansiyel İyileştirmeler
- **Çoklu Dil Desteği**: Uluslararasılaştırma
- **Otomatik Güncelleme**: Yeni versiyon kontrolü
- **Gelişmiş Raporlama**: Kurulum raporları
- **Uzaktan Yönetim**: Ağ üzerinden kurulum
- **Gelişmiş USB Tespiti**: Daha fazla tarayıcı modeli desteği

### 🛠️ Teknik İyileştirmeler
- **GTK4 Desteği**: Modern GTK framework
- **Flatpak Paketi**: Sandboxed kurulum
- **Snap Paketi**: Ubuntu Snap Store desteği
- **Java 11+ Desteği**: Modern Java runtime desteği

## ⚠️ GELİŞTİRME VE TASARLAMA UYARILARI

### 🚨 KRİTİK UYARILAR

#### 📁 `/opt/HacPasaport` Dizini
- **KESİNLİKLE SİLMEYİN**: Bu dizin uygulamanın çalışması için kritik öneme sahiptir
- **Yanlışlıkla Silme**: Dizinin silinmesi uygulamanın tamamen çalışmamasına neden olur
- **Kontrol Mekanizması**: `app.py` dosyasında `/opt/HacPasaport/app/app.py` varlığı kontrol edilir
- **Hata Mesajı**: Dizin yoksa "DEB paketi düzgün kurulmamış olabilir" hatası verir

#### 🔧 Geliştirme Aşamasında Dikkat Edilecekler
1. **Dizin Yapısını Koruyun**: 
   - `/opt/HacPasaport/` ana dizini
   - `/opt/HacPasaport/app/` GUI uygulama dosyaları
   - `/opt/HacPasaport/` Java dosyaları (düz konumlandırma)
   - `/opt/HacPasaport/app/script/install.sh` kurulum betiği

2. **Dosya İzinleri**:
   - `pasaport.sh` ve `sc.sh` dosyalarına çalıştırma izni verilmeli
   - `chmod +x` komutu ile izinler ayarlanmalı

3. **Kritik Dosyalar**:
   - `swingUI.jar`: Ana Java uygulaması
   - `pasaport.sh`: Java uygulaması başlatıcı
   - `app.py`: GUI uygulaması
   - `install.sh`: Kurulum betiği

#### 🛡️ Güvenlik Önlemleri
- **Yedekleme**: Geliştirme öncesi `/opt/HacPasaport` dizininin yedeğini alın
- **Test Ortamı**: Değişiklikleri test ortamında deneyin
- **Geri Alma Planı**: Sorun çıkarsa yedekten geri yükleme planı hazırlayın

#### 🔍 Hata Kontrolü
```python
# app.py'de kontrol edilen kritik dosyalar
if not os.path.exists("/opt/HacPasaport/app/app.py"):
    error_exit("app.py dosyası bulunamadı!")

if not os.path.exists("/opt/HacPasaport/pasaport.sh"):
    error_exit("pasaport.sh dosyası bulunamadı!")
```

#### 📋 Geliştirme Checklist
- [ ] `/opt/HacPasaport` dizini mevcut mu?
- [ ] `/opt/HacPasaport/app` dizini mevcut mu?
- [ ] `pasaport.sh` dosyası çalıştırılabilir mi?
- [ ] `swingUI.jar` dosyası mevcut mu?
- [ ] `app.py` dosyası `/opt/HacPasaport/app/` altında mı?
- [ ] Dosya izinleri doğru mu?
- [ ] Test ortamında çalışıyor mu?

## 📚 Teknik Dokümantasyon

### 🔗 API Referansı
- **GTK3**: https://developer.gnome.org/gtk3/
- **VTE Terminal**: https://developer.gnome.org/vte/
- **PyGObject**: https://pygobject.readthedocs.io/

### 📖 Geliştirici Kaynakları
- **Proje GitHub**: https://github.com/serkanoyanik/Diyanet-Pasaport-Tarayici
- **Pardus**: https://www.pardus.org.tr
- **Diyanet**: https://www.diyanet.gov.tr

---

**Son Güncelleme**: 2025
**Versiyon**: 1.1.0
**Geliştirici**: Serkan Oyanık
**Lisans**: Diyanet Pardus Projesi 