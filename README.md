# Pasaport Tarayıcı Kurulum

Bu uygulama, Pasaport Tarayıcı için gerekli kurulumları yapan GTK3 tabanlı bir kurulum aracıdır.

## Özellikler

- 🖥️ **Modern GTK3 Arayüzü**: Temiz ve kullanıcı dostu arayüz
- 🔧 **Otomatik Kurulum**: Tek tıkla tam kurulum
- 👥 **Kullanıcı Yönetimi**: HacPasaport grubuna kullanıcı ekleme
- 📸 **Screenshot Alma**: Ekran görüntüsü alma özelliği
- 🎨 **Özelleştirilmiş Tasarım**: Yeşil butonlar ve DIB logosu
- 🖥️ **Terminal Entegrasyonu**: Gerçek zamanlı kurulum çıktıları

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

1. **Kurulumu Başlat**: Seçilen kullanıcı için tam kurulum yapar
2. **Kullanıcı Ekle**: Mevcut kullanıcıyı HacPasaport grubuna ekler
3. **Screenshot**: Uygulama penceresinin ekran görüntüsünü alır

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

## Geliştirme

### CSS Stilleri

Butonlar için özel CSS sınıfı:
```css
.rounded-green-button {
    background-color: #00C851;
    color: white;
    border-radius: 4px;
    min-width: 60px;
    min-height: 25px;
}
```

### Yeni Özellik Ekleme

1. UI dosyasına widget ekle
2. Python kodunda event handler yaz
3. CSS ile stil ver

## Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request açın

## Lisans

Bu proje Pardus projesi altında geliştirilmiştir.

## İletişim

- **Website**: https://www.pardus.org.tr
- **GitHub**: [Proje Sayfası](https://github.com/your-username/pasaport-tarayici-kurulum)

## Ekran Görüntüleri

### Ana Pencere
- Sol panel: Kontrol butonları ve DIB logosu
- Sağ panel: Terminal çıktıları

### Hakkında Penceresi
- DIB logosu ile özelleştirilmiş
- Uygulama bilgileri ve bağlantılar

## Sürüm Geçmişi

### v1.0.0
- İlk sürüm
- GTK3 arayüzü
- Kurulum ve kullanıcı yönetimi
- Screenshot özelliği
- Özelleştirilmiş tasarım 