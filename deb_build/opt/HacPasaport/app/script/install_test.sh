#!/bin/bash
set -e

if [ -z "$1" ]; then
    echo "Kullanıcı adı parametre olarak verilmelidir!" >&2
    exit 1
fi
KULLANICI="$1"
ADDUSERONLY="$2"

log() {
    echo -e "\n[INFO] $1"
}
error_exit() {
    echo -e "\n[HATA] $1" >&2
    exit 1
}

add_desktop_shortcut() {
    # Pasaport-Tarayıcı.desktop dosyasını oluştur
    cat > /tmp/Pasaport-Tarayıcı.desktop <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Pasaport Tarayıcı
Comment=Diyanet Pasaport Tarayıcı Uygulaması
Exec=sudo /opt/HacPasaport/pasaport.sh
Icon=org.gnome.SimpleScan
Categories=Utility;Application;
Terminal=true
StartupNotify=false
EOF

    USER_HOME=$(eval echo "~$KULLANICI")
    USER_GROUP=$(id -gn "$KULLANICI")
    for DESKTOP_DIR in "$USER_HOME/Masaüstü" "$USER_HOME/Desktop"; do
        if [ -d "$DESKTOP_DIR" ]; then
            cp /tmp/Pasaport-Tarayıcı.desktop "$DESKTOP_DIR/Pasaport-Tarayıcı.desktop"
            chmod +x "$DESKTOP_DIR/Pasaport-Tarayıcı.desktop"
            chown "$KULLANICI:$USER_GROUP" "$DESKTOP_DIR/Pasaport-Tarayıcı.desktop"
            # GNOME için güvenlik işaretleme - daha güçlü yöntem
            sudo -u "$KULLANICI" gio set "$DESKTOP_DIR/Pasaport-Tarayıcı.desktop" "metadata::trusted" yes 2>/dev/null || true
            # Alternatif yöntemler
            sudo -u "$KULLANICI" chmod +x "$DESKTOP_DIR/Pasaport-Tarayıcı.desktop"
            # GNOME için ek güvenlik ayarı
            sudo -u "$KULLANICI" gio set "$DESKTOP_DIR/Pasaport-Tarayıcı.desktop" "metadata::trusted" true 2>/dev/null || true
            log "Masaüstü kısayolu $DESKTOP_DIR dizinine kopyalandı, sahipliği ayarlandı ve güvenli olarak işaretlendi."
        fi
    done
    
    # Kullanıcıya özel uygulama menüsü için .local/share/applications altına da ekle
    LOCAL_APP_DIR="$USER_HOME/.local/share/applications"
    mkdir -p "$LOCAL_APP_DIR"
    cp /tmp/Pasaport-Tarayıcı.desktop "$LOCAL_APP_DIR/Pasaport-Tarayıcı.desktop"
    chown "$KULLANICI:$USER_GROUP" "$LOCAL_APP_DIR/Pasaport-Tarayıcı.desktop"
    chmod +x "$LOCAL_APP_DIR/Pasaport-Tarayıcı.desktop"
    # Desktop database güncelle
    sudo -u "$KULLANICI" update-desktop-database "$LOCAL_APP_DIR" 2>/dev/null || true
    log "Kullanıcıya özel uygulama menüsü girişi $LOCAL_APP_DIR dizinine eklendi."
}

if [ "$ADDUSERONLY" = "adduseronly" ]; then
    log "Sadece kullanıcı ekleme modu."
    groupadd -f hacpasaport
    if id "$KULLANICI" &>/dev/null; then
        if id -nG "$KULLANICI" | grep -qw hacpasaport; then
            log "$KULLANICI zaten hacpasaport grubunda."
        else
            usermod -aG hacpasaport "$KULLANICI"
            log "$KULLANICI hacpasaport grubuna eklendi."
        fi
        # Masaüstü kısayolunu ekle
        add_desktop_shortcut
        echo -e "\n[UYARI] Kullanıcının oturumunu sonlandırıp tekrar giriş yapmalısınız. Grup ve yetki değişikliklerinin etkili olması için bu gereklidir."
    else
        error_exit "Kullanıcı bulunamadı: $KULLANICI"
    fi
    exit 0
fi

log "=== GELİŞTİRME TEST MODU ==="
log "Yeni dizin yapılandırması: /opt/HacPasaport/ (Java dosyaları + app/ dizini)"

log "1. HacPasaport dizini kontrol ediliyor..."
if [ ! -d "/opt/HacPasaport" ]; then
    log "⚠️ /opt/HacPasaport dizini bulunamadı (geliştirme aşaması - normal)"
    log "Bu geliştirme test modunda normal bir durumdur."
    log "DEB paketi kurulduğunda: /opt/HacPasaport/ altında Java dosyaları + app/ dizini olacak"
else
    log "✅ /opt/HacPasaport dizini mevcut."
    log "Yapılandırma: Java dosyaları doğrudan /opt/HacPasaport/ altında"
    log "GUI dosyaları: /opt/HacPasaport/app/ altında"
fi

log "2. Gerekli paketler kontrol ediliyor..."
for pkg in pcscd tesseract-ocr tesseract-ocr-tur libacsccid1 dialog; do
    if dpkg -l | grep -qw "$pkg"; then
        log "✅ $pkg zaten kurulu."
    else
        log "⚠️ $pkg kurulu değil (geliştirme aşaması - normal)"
    fi
done

log "3. Java durumu kontrol ediliyor..."
if dpkg -l | grep -q oracle-java8-jre; then
    log "✅ oracle-java8-jre zaten kurulu."
else
    log "⚠️ oracle-java8-jre kurulu değil (geliştirme aşaması - normal)"
fi

log "4. hacpasaport grubu oluşturuluyor..."
groupadd -f hacpasaport
log "✅ hacpasaport grubu oluşturuldu."

log "5. Kullanıcı gruba ekleniyor..."
if id "$KULLANICI" &>/dev/null; then
    if id -nG "$KULLANICI" | grep -qw hacpasaport; then
        log "✅ $KULLANICI zaten hacpasaport grubunda."
    else
        usermod -aG hacpasaport "$KULLANICI"
        log "✅ $KULLANICI hacpasaport grubuna eklendi."
    fi
else
    error_exit "Kullanıcı bulunamadı: $KULLANICI"
fi

log "6. Sudoers yetkisi ekleniyor..."
cat > /etc/sudoers.d/diyanet <<EOF
%hacpasaport ALL=(ALL) NOPASSWD: /opt/HacPasaport/pasaport.sh, /opt/HacPasaport/sc.sh
EOF
chmod 440 /etc/sudoers.d/diyanet
log "✅ Sudoers yetkisi eklendi."

log "7. Polkit yetkisi ekleniyor..."
cat <<EOF | tee /etc/polkit-1/localauthority/50-local.d/99-scan.pkla > /dev/null
[Allow scanimage for hacpasaport]
Identity=unix-group:hacpasaport
Action=org.freedesktop.policykit.exec
ResultActive=yes
ResultAny=yes
ResultInactive=yes
EOF
log "✅ Polkit yetkisi eklendi."

log "8. Donanım kontrolü: scanimage -L"
if scanimage -L | grep -i "canon.*lide" > /dev/null; then
    log "✅ Canon LiDE tarayıcı bulundu!"
    scanimage -L | grep -i "canon.*lide"
else
    log "❌ Canon LiDE tarayıcı bulunamadı!"
    log "Lütfen tarayıcının bağlı olduğundan ve açık olduğundan emin olun."
fi

log "9. Test kurulumu tamamlandı!"
log "=== GELİŞTİRME TEST MODU TAMAMLANDI ==="

log "Kurulum tamamlandı!"
echo -e "\n[UYARI] Kullanıcının oturumunu sonlandırıp tekrar giriş yapmalısınız. Grup ve yetki değişikliklerinin etkili olması için bu gereklidir." 