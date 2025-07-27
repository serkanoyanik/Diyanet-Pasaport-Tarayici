# Pasaport Tarayıcı Kurulum

Bu uygulama, Pasaport Tarayıcı için gerekli kurulumları yapan GTK3 tabanlı bir kurulum aracıdır.

## Özellikler

- 🖥️ **Modern GTK3 Arayüzü**
- 🔧 **Otomatik Kurulum**
- 👥 **Kullanıcı Yönetimi** (Yerel ve Domain kullanıcıları)
- 📸 **Screenshot Alma**
- 🎨 **Özelleştirilmiş Tasarım**
- 🖥️ **Terminal Entegrasyonu**
- 🔍 **Tarayıcı Kontrolü** (Canon LiDE200)
- ℹ️ **Akıllı Bilgilendirme**

## Ekran Görüntüleri

![Ana Ekran](screenshots/main_window.png)

## Kurulum

### DEB Paketi ile Kurulum (Önerilen)

```bash
# DEB paketini indirin ve kurun
sudo dpkg -i hac-pasaport-kurulum_1.0.0.deb

# Bağımlılıkları kontrol edin
sudo apt-get install -f

# Uygulamalar menüsünden "Pasaport Tarayıcı Kurulum" uygulamasını çalıştırın
```

### Manuel Kurulum

#### Gereksinimler

```bash
# Ubuntu/Debian/Pardus
sudo apt-get install python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-vte-2.91

# Fedora
sudo dnf install python3-gobject gtk3 vte291
```

#### OpenCV JAR Dosyası Hakkında

- `source/HacPasaport/opencv-3.4.2-0.jar` dosyası boyut sınırı nedeniyle repoda **sıkıştırılmış olarak** (`opencv-3.4.2-0.jar.tar.gz`) tutulmaktadır.
- Kurulum sırasında `scripts/install.sh` bu arşivi otomatik olarak açar ve gerekli `.jar` dosyasını doğru dizine yerleştirir.
- **Ekstra bir işlem yapmanıza gerek yoktur.**

#### Çalıştırma

```bash
python3 app.py
```

## Kullanım

1. **Kurulumu Başlat**: 
   - Canon LiDE200 tarayıcısını kontrol eder
   - Seçilen kullanıcı için tam kurulum yapar
   - Kurulum sonrası grup üyeliği hakkında bilgi verir

2. **Kullanıcı Ekle**: 
   - Mevcut kullanıcıyı HacPasaport grubuna ekler
   - Domain kullanıcılarını destekler (/home/DIB/ formatında)
   - Grup üyeliği hakkında bilgi verir

3. **Screenshot**: Uygulama penceresinin ekran görüntüsünü alır

### Önemli Notlar

- **Tarayıcı Gereksinimi**: Canon LiDE200 tarayıcı gerekli
- **Grup Üyeliği**: Kullanıcı eklendikten sonra oturum kapatıp tekrar giriş yapın
- **GNOME Masaüstü**: Bazı durumlarda yeniden başlatma gerekebilir
- **Domain Kullanıcıları**: Active Directory kullanıcıları otomatik algılanır
- **Masaüstü Kısayolu**: Sadece seçili kullanıcının masaüstüne eklenir

## Proje Yapısı

```
hac_pasaport_kurulum/
├── app.py                 # Ana uygulama dosyası
├── __main__.py           # Giriş noktası
├── ui/
│   ├── window.ui         # GTK UI tanımları
│   └── styles.css        # CSS stilleri
├── icons/
│   ├── dib_logo.png      # DIB logosu
│   ├── camera.png        # Kamera ikonu
│   └── open-menu.png     # Menü ikonu
├── scripts/
│   └── install.sh        # Kurulum betiği
├── source/
│   └── HacPasaport/      # Kaynak dosyalar
└── deb_build/            # DEB paketi yapısı
    └── hac-pasaport-kurulum_1.0.0/
        ├── DEBIAN/       # Paket kontrol dosyaları
        ├── opt/HacPasaport/  # Uygulama dosyaları
        └── usr/share/    # Sistem dosyaları
```

## DEB Paketi Özellikleri

- **Sistem Entegrasyonu**: Uygulamalar menüsüne otomatik eklenir
- **İkon Desteği**: Canon LiDE210 ikonu ile görsel entegrasyon
- **Kullanıcı Yönetimi**: Sadece seçili kullanıcı için masaüstü kısayolu
- **Otomatik Kurulum**: Postinst betiği ile gerekli ayarlar
- **Bağımlılık Yönetimi**: Gerekli paketler otomatik kurulur

## Teknik Detaylar

- **Dil**: Python 3
- **GUI Framework**: GTK3
- **Terminal**: VTE Terminal Widget
- **Stil**: CSS ile özelleştirilmiş butonlar
- **Masaüstü Desteği**: XFCE, GNOME, KDE
- **Paket Formatı**: DEB (Debian/Ubuntu/Pardus)

## Lisans

Bu proje Diyanet Pardus projesi altında geliştirilmiştir.

## İletişim

- **Website**: https://www.pardus.org.tr
- **GitHub**: [Proje Sayfası](https://github.com/serkanoyanik/Diyanet-Pasaport-Tarayici)