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

### Gereksinimler

```bash
# Ubuntu/Debian/Pardus
sudo apt-get install python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-vte-2.91

# Fedora
sudo dnf install python3-gobject gtk3 vte291
```

### Çalıştırma

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
└── source/
    └── HacPasaport/      # Kaynak dosyalar
```

## Teknik Detaylar

- **Dil**: Python 3
- **GUI Framework**: GTK3
- **Terminal**: VTE Terminal Widget
- **Stil**: CSS ile özelleştirilmiş butonlar
- **Masaüstü Desteği**: XFCE, GNOME, KDE

## Lisans

Bu proje Diyanet Pardus projesi altında geliştirilmiştir.

## İletişim

- **Website**: https://www.pardus.org.tr
- **GitHub**: [Proje Sayfası](https://github.com/your-username/pasaport-tarayici-kurulum)