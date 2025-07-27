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
Exec=sudo /opt/HacPasaport/source/HacPasaport/pasaport.sh
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

log "1. HacPasaport dizini kontrol ediliyor..."
if [ ! -d "/opt/HacPasaport" ]; then
    error_exit "/opt/HacPasaport dizini bulunamadı! DEB paketi düzgün kurulmamış olabilir. Lütfen önce DEB paketini kurun."
fi

# DEB paketi kurulumu sonrası gerekli dosyaların varlığını kontrol et
if [ ! -f "/opt/HacPasaport/source/HacPasaport/pasaport.sh" ]; then
    error_exit "pasaport.sh dosyası bulunamadı! DEB paketi düzgün kurulmamış olabilir. Lütfen önce DEB paketini kurun."
fi

if [ ! -f "/opt/HacPasaport/app.py" ]; then
    error_exit "app.py dosyası bulunamadı! DEB paketi düzgün kurulmamış olabilir. Lütfen önce DEB paketini kurun."
fi

log "/opt/HacPasaport dizini ve gerekli dosyalar mevcut."

log "2. Dosya izinleri ayarlanıyor..."
find /opt/HacPasaport -type f -exec chmod 644 {} +
chmod +x /opt/HacPasaport/source/HacPasaport/pasaport.sh /opt/HacPasaport/source/HacPasaport/sc.sh

# OpenCV jar dosyasının varlığını kontrol et
if [ -f "/opt/HacPasaport/source/HacPasaport/opencv-3.4.2-0.jar" ]; then
    log "OpenCV jar dosyası mevcut."
elif [ -f "/opt/HacPasaport/source/HacPasaport/opencv-3.4.2-0.jar.tar.gz" ]; then
    log "OpenCV jar arşivi bulundu, çıkarılıyor..."
    cd /opt/HacPasaport/source/HacPasaport/
    tar -xzf opencv-3.4.2-0.jar.tar.gz || error_exit "OpenCV jar arşivi çıkarılamadı!"
    if [ ! -f opencv-3.4.2-0.jar ]; then
        error_exit "OpenCV jar dosyası arşivden çıkarılamadı!"
    fi
    log "OpenCV jar arşivi başarıyla çıkarıldı."
else
    log "Uyarı: OpenCV jar dosyası bulunamadı. Pasaport tarama özelliği çalışmayabilir."
fi

# pasaport.sh ve sc.sh içeriğiyle ilgili adımlar kaldırıldı

log "3. Gerekli paketler kuruluyor..."
for pkg in pcscd tesseract-ocr tesseract-ocr-tur libacsccid1 dialog; do
    if dpkg -l | grep -qw "$pkg"; then
        log "$pkg zaten kurulu."
    else
        apt-get update && apt-get install -y "$pkg"
    fi
done

log "4. Java durumu kontrol ediliyor..."
if dpkg -l | grep -q oracle-java8-jre; then
    log "oracle-java8-jre zaten kurulu."
else
    log "oracle-java8-jre kurulu değil, kuruluyor..."
    apt-get install -y --allow-downgrades oracle-java8-jre=8u241 || log "oracle-java8-jre=8u241 kurulamadı veya bulunamadı."
fi

log "6. Java alternatifleri ayarlanıyor..."
JAVA_PATH="/usr/lib/jvm/oracle-java8-jre-amd64/bin/java"
if [ -x "$JAVA_PATH" ]; then
    update-alternatives --set java "$JAVA_PATH"
    log "Java alternatifi $JAVA_PATH olarak ayarlandı."
else
    log "Uygun java yolu bulunamadı, alternatif ayarlanamadı."
fi

log "7. Java güncellemesi engelleniyor..."
if apt-mark showhold | grep -qw oracle-java8-jre; then
    log "oracle-java8-jre zaten hold durumda."
else
    apt-mark hold oracle-java8-jre
fi

log "8. Kütüphane linkleri oluşturuluyor..."
ln -sf /usr/lib/x86_64-linux-gnu/libpcsclite.so.1 /usr/lib/x86_64-linux-gnu/libpcsclite.so
ln -sf /usr/lib/x86_64-linux-gnu/libpcsclite.so /usr/lib64/
ln -sf /usr/lib/x86_64-linux-gnu/libpcsclite.so.1 /usr/lib64/
ln -sf /usr/lib/x86_64-linux-gnu/libpcsclite.so.1.0.0 /usr/lib64/

log "9. pcscd servisi yeniden başlatılıyor..."
/etc/init.d/pcscd restart || true

log "10. hacpasaport grubu oluşturuluyor..."
groupadd -f hacpasaport

log "11. Kullanıcı gruba ekleniyor..."
if id "$KULLANICI" &>/dev/null; then
    if id -nG "$KULLANICI" | grep -qw hacpasaport; then
        log "$KULLANICI zaten hacpasaport grubunda."
    else
        usermod -aG hacpasaport "$KULLANICI"
        log "$KULLANICI hacpasaport grubuna eklendi."
    fi
else
    error_exit "Kullanıcı bulunamadı: $KULLANICI"
fi

# Sudoers yetkisi ekleniyor
cat > /etc/sudoers.d/diyanet <<EOF
%hacpasaport ALL=(ALL) NOPASSWD: /opt/HacPasaport/source/HacPasaport/pasaport.sh, /opt/HacPasaport/source/HacPasaport/sc.sh
EOF
chmod 440 /etc/sudoers.d/diyanet

# Masaüstü kısayolu için ayrı bir .desktop dosyası oluştur
cat > /tmp/Pasaport-Tarayıcı.desktop <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Pasaport Tarayıcı
Comment=Diyanet Pasaport Tarayıcı Uygulaması
Exec=sudo /opt/HacPasaport/source/HacPasaport/pasaport.sh
Icon=org.gnome.SimpleScan
Categories=Utility;Application;
Terminal=true
StartupNotify=false
EOF

USER_HOME=$(eval echo "~$KULLANICI")
USER_GROUP=$(id -gn "$KULLANICI")

# Kullanıcıya özel uygulama menüsü için .local/share/applications altına ekle
LOCAL_APP_DIR="$USER_HOME/.local/share/applications"
mkdir -p "$LOCAL_APP_DIR"
cp /tmp/Pasaport-Tarayıcı.desktop "$LOCAL_APP_DIR/Pasaport-Tarayıcı.desktop"
chown "$KULLANICI:$USER_GROUP" "$LOCAL_APP_DIR/Pasaport-Tarayıcı.desktop"
chmod +x "$LOCAL_APP_DIR/Pasaport-Tarayıcı.desktop"
log "Kullanıcıya özel uygulama menüsü girişi $LOCAL_APP_DIR dizinine eklendi."

# Masaüstü kısayollarını oluştur ve güvenlik ayarlarını yap
for DESKTOP_DIR in "$USER_HOME/Masaüstü" "$USER_HOME/Desktop"; do
    if [ -d "$DESKTOP_DIR" ]; then
        cp /tmp/Pasaport-Tarayıcı.desktop "$DESKTOP_DIR/Pasaport-Tarayıcı.desktop"
        chown "$KULLANICI:$USER_GROUP" "$DESKTOP_DIR/Pasaport-Tarayıcı.desktop"
        chmod +x "$DESKTOP_DIR/Pasaport-Tarayıcı.desktop"
        
        # GNOME için güvenlik işaretleme - basit ve güvenli yöntem
        sudo -u "$KULLANICI" gio set "$DESKTOP_DIR/Pasaport-Tarayıcı.desktop" "metadata::trusted" yes 2>/dev/null || true
        sudo -u "$KULLANICI" chmod +x "$DESKTOP_DIR/Pasaport-Tarayıcı.desktop"
        sudo -u "$KULLANICI" update-desktop-database "$LOCAL_APP_DIR" 2>/dev/null || true
        
        log "Masaüstü kısayolu $DESKTOP_DIR dizinine kopyalandı, sahipliği ayarlandı ve güvenli olarak işaretlendi."
    fi
done

log "12. Polkit yetkisi ekleniyor..."
cat <<EOF | tee /etc/polkit-1/localauthority/50-local.d/99-scan.pkla > /dev/null
[Allow scanimage for hacpasaport]
Identity=unix-group:hacpasaport
Action=org.freedesktop.policykit.exec
ResultActive=yes
ResultAny=yes
ResultInactive=yes
EOF
if [ ! -f /etc/polkit-1/localauthority/50-local.d/99-scan.pkla ]; then
    error_exit "/etc/polkit-1/localauthority/50-local.d/99-scan.pkla dosyası oluşturulamadı!"
fi
if ! grep -q 'hacpasaport' /etc/polkit-1/localauthority/50-local.d/99-scan.pkla; then
    error_exit "/etc/polkit-1/localauthority/50-local.d/99-scan.pkla içeriği hatalı!"
fi

# GNOME masaüstü için özel iyileştirmeler
log "13. Masaüstü ortamı kontrolü ve GNOME iyileştirmeleri..."
DESKTOP_ENV=""

# Güvenilir masaüstü ortamı tespiti - pkexec ile çalıştırıldığında da çalışır
# 1. Environment değişkenlerini kontrol et
if [ -n "$XDG_CURRENT_DESKTOP" ]; then
    DESKTOP_ENV=$(echo "$XDG_CURRENT_DESKTOP" | tr '[:upper:]' '[:lower:]')
    log "XDG_CURRENT_DESKTOP tespit edildi: $DESKTOP_ENV"
elif [ -n "$DESKTOP_SESSION" ]; then
    DESKTOP_ENV=$(echo "$DESKTOP_SESSION" | tr '[:upper:]' '[:lower:]')
    log "DESKTOP_SESSION tespit edildi: $DESKTOP_ENV"
else
    # 2. Alternatif yöntem: Kullanıcının home dizinindeki config dosyalarını kontrol et
    USER_HOME=$(eval echo "~$KULLANICI")
    
    if [ -f "$USER_HOME/.config/gnome-session/sessions" ] || [ -d "$USER_HOME/.config/gnome-session" ]; then
        DESKTOP_ENV="gnome"
        log "GNOME session config dosyaları tespit edildi"
    elif [ -f "$USER_HOME/.config/xfce4" ]; then
        DESKTOP_ENV="xfce"
        log "XFCE config dosyaları tespit edildi"
    elif [ -f "$USER_HOME/.config/kdeglobals" ]; then
        DESKTOP_ENV="kde"
        log "KDE config dosyaları tespit edildi"
    else
        # 3. Son çare: Çalışan process'leri kontrol et
        if pgrep gnome-session >/dev/null 2>&1; then
            DESKTOP_ENV="gnome"
            log "GNOME session process tespit edildi"
        elif pgrep xfce4-session >/dev/null 2>&1; then
            DESKTOP_ENV="xfce"
            log "XFCE session process tespit edildi"
        elif pgrep plasma-session >/dev/null 2>&1; then
            DESKTOP_ENV="kde"
            log "KDE session process tespit edildi"
        else
            DESKTOP_ENV="unknown"
            log "Masaüstü ortamı tespit edilemedi"
        fi
    fi
fi

log "Tespit edilen masaüstü ortamı: $DESKTOP_ENV"

if echo "$DESKTOP_ENV" | grep -q gnome; then
    log "GNOME masaüstü tespit edildi. Özel iyileştirmeler uygulanıyor..."
    
    # GNOME için grup üyeliğinin daha hızlı aktif olması için iyileştirmeler
    USER_HOME=$(eval echo "~$KULLANICI")
    
    # GNOME session'ı yenilemek için gerekli dosyaları oluştur
    GNOME_SESSION_DIR="$USER_HOME/.config/gnome-session"
    mkdir -p "$GNOME_SESSION_DIR"
    
    # GNOME için grup üyeliğini aktif hale getiren script oluştur
    cat > "$USER_HOME/.hacpasaport_group_check.sh" <<'EOF'
#!/bin/bash
# HacPasaport grup üyeliği kontrol ve aktif hale getirme scripti

# Grup üyeliğini kontrol et
if groups | grep -q hacpasaport; then
    echo "✅ HacPasaport grubu zaten aktif!"
    notify-send "HacPasaport" "Grup üyeliği zaten aktif!" -i info
    exit 0
fi

echo "🔄 HacPasaport grubu aktif hale getiriliyor..."

# GNOME için grup üyeliğini aktif hale getirme yöntemleri
# 1. PAM session'ı yenile
pkill -HUP -u $USER 2>/dev/null || true

# 2. GNOME session'ı yenile (güvenli yöntem)
if pgrep gnome-session >/dev/null; then
    # GNOME session'ı yenilemek için güvenli yöntem
    dbus-send --session --type=method_call --dest=org.gnome.SessionManager /org/gnome/SessionManager org.gnome.SessionManager.Reload 2>/dev/null || true
fi

# 3. Yeni grup üyeliğini kontrol et
sleep 2
if groups | grep -q hacpasaport; then
    echo "✅ HacPasaport grubu başarıyla aktif hale getirildi!"
    notify-send "HacPasaport" "Grup üyeliği başarıyla aktif hale getirildi!" -i info
else
    echo "⚠️ Grup üyeliği henüz aktif değil. Yeni terminal açmanız önerilir."
    notify-send "HacPasaport" "Grup üyeliği henüz aktif değil. Yeni terminal açın." -i warning
fi

# 4. Grup üyeliğini göster
echo "📋 Mevcut gruplar: $(groups)"
EOF
    
    chmod +x "$USER_HOME/.hacpasaport_group_check.sh"
    chown "$KULLANICI:$USER_GROUP" "$USER_HOME/.hacpasaport_group_check.sh"
    
    # GNOME için grup üyeliğini otomatik aktif hale getiren script oluştur
    cat > "$USER_HOME/.hacpasaport_activate_group.sh" <<'EOF'
#!/bin/bash
# GNOME için grup üyeliğini otomatik aktif hale getirme scripti

# Sadece GNOME ortamında çalış
if [ -z "$XDG_CURRENT_DESKTOP" ] || ! echo "$XDG_CURRENT_DESKTOP" | grep -q -i gnome; then
    exit 0
fi

# Grup üyeliğini kontrol et
if ! groups | grep -q hacpasaport; then
    echo "🔄 GNOME ortamında grup üyeliği aktif hale getiriliyor..."
    
    # Güvenli yöntemlerle grup üyeliğini aktif hale getir
    # 1. PAM session yenileme (güvenli)
    pkill -HUP -u $USER 2>/dev/null || true
    
    # 2. GNOME session yenileme (güvenli yöntem)
    if pgrep gnome-session >/dev/null; then
        # Sadece session'ı yenile, desktop ayarlarını sıfırlama
        dbus-send --session --type=method_call --dest=org.gnome.SessionManager /org/gnome/SessionManager org.gnome.SessionManager.Reload 2>/dev/null || true
    fi
    
    # 3. GNOME için özel grup aktivasyon yöntemleri
    # 3.1. Yeni bir shell session'ı başlat ve grup üyeliğini kontrol et
    if command -v newgrp >/dev/null 2>&1; then
        # newgrp ile yeni grup session'ı başlat
        echo "hacpasaport" | newgrp hacpasaport 2>/dev/null || true
    fi
    
    # 3.2. GNOME environment'ını yenile
    if command -v gdbus >/dev/null 2>&1; then
        gdbus call --session --dest=org.gnome.SessionManager --object-path=/org/gnome/SessionManager --method=org.gnome.SessionManager.Reload 2>/dev/null || true
    fi
    
    # 3.3. PAM session'ı manuel olarak yenile
    if command -v pamtester >/dev/null 2>&1; then
        pamtester open_session $USER 2>/dev/null || true
    fi
    
    # 4. Kısa bekleme
    sleep 2
    
    # 5. Son kontrol
    if groups | grep -q hacpasaport; then
        echo "✅ Grup üyeliği aktif hale getirildi!"
        notify-send "HacPasaport" "Grup üyeliği aktif hale getirildi!" -i info
    else
        echo "⚠️ Grup üyeliği henüz aktif değil, manuel kontrol gerekebilir"
        notify-send "HacPasaport" "Grup üyeliği henüz aktif değil. Yeni terminal açın." -i warning
    fi
fi
EOF
    
    chmod +x "$USER_HOME/.hacpasaport_activate_group.sh"
    chown "$KULLANICI:$USER_GROUP" "$USER_HOME/.hacpasaport_activate_group.sh"
    
    # GNOME oturum başlangıcında çalışacak script oluştur
    cat > "$USER_HOME/.hacpasaport_session_start.sh" <<'EOF'
#!/bin/bash
# GNOME oturum başlangıcında grup üyeliğini aktif hale getirme scripti

# Sadece GNOME ortamında çalış
if [ -z "$XDG_CURRENT_DESKTOP" ] || ! echo "$XDG_CURRENT_DESKTOP" | grep -q -i gnome; then
    exit 0
fi

# Oturum başlangıcında biraz bekle
sleep 3

# Grup üyeliğini kontrol et
if ! groups | grep -q hacpasaport; then
    echo "🔄 GNOME oturum başlangıcında grup üyeliği aktif hale getiriliyor..."
    
    # 1. PAM session'ı yenile
    pkill -HUP -u $USER 2>/dev/null || true
    
    # 2. Yeni grup session'ı başlat
    if command -v newgrp >/dev/null 2>&1; then
        echo "hacpasaport" | newgrp hacpasaport 2>/dev/null || true
    fi
    
    # 3. GNOME session'ı yenile
    if pgrep gnome-session >/dev/null; then
        dbus-send --session --type=method_call --dest=org.gnome.SessionManager /org/gnome/SessionManager org.gnome.SessionManager.Reload 2>/dev/null || true
    fi
    
    # 4. Son kontrol
    sleep 2
    if groups | grep -q hacpasaport; then
        echo "✅ Oturum başlangıcında grup üyeliği aktif hale getirildi!"
        notify-send "HacPasaport" "Grup üyeliği aktif hale getirildi!" -i info
    fi
fi
EOF
    
    chmod +x "$USER_HOME/.hacpasaport_session_start.sh"
    chown "$KULLANICI:$USER_GROUP" "$USER_HOME/.hacpasaport_session_start.sh"
    
    # GNOME otomatik başlatma için desktop dosyası oluştur (güvenli)
    AUTOSTART_DIR="$USER_HOME/.config/autostart"
    mkdir -p "$AUTOSTART_DIR"
    
    # Ana aktivasyon scripti için autostart
    cat > "$AUTOSTART_DIR/hacpasaport-group-activate.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=HacPasaport Grup Aktivasyonu
Comment=GNOME ortamında HacPasaport grup üyeliğini aktif hale getirir
Exec=$USER_HOME/.hacpasaport_activate_group.sh
Hidden=true
NoDisplay=true
X-GNOME-Autostart-enabled=true
X-GNOME-Autostart-Delay=10
EOF
    
    chmod +x "$AUTOSTART_DIR/hacpasaport-group-activate.desktop"
    chown "$KULLANICI:$USER_GROUP" "$AUTOSTART_DIR/hacpasaport-group-activate.desktop"
    
    # Oturum başlangıcı için ayrı autostart
    cat > "$AUTOSTART_DIR/hacpasaport-session-start.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=HacPasaport Oturum Başlangıcı
Comment=GNOME oturum başlangıcında grup üyeliğini aktif hale getirir
Exec=$USER_HOME/.hacpasaport_session_start.sh
Hidden=true
NoDisplay=true
X-GNOME-Autostart-enabled=true
X-GNOME-Autostart-Delay=5
EOF
    
    chmod +x "$AUTOSTART_DIR/hacpasaport-session-start.desktop"
    chown "$KULLANICI:$USER_GROUP" "$AUTOSTART_DIR/hacpasaport-session-start.desktop"
    
    # GNOME için grup üyeliğini hemen aktif hale getirmeyi dene (güvenli)
    log "GNOME ortamında grup üyeliği aktif hale getiriliyor..."
    if sudo -u "$KULLANICI" bash "$USER_HOME/.hacpasaport_activate_group.sh" 2>/dev/null; then
        log "✅ GNOME grup aktivasyonu başarıyla uygulandı."
    else
        log "⚠️ GNOME grup aktivasyonu uygulanamadı, manuel kontrol gerekebilir."
    fi
    
    log "GNOME iyileştirmeleri tamamlandı."
    log "Kullanıcı için grup aktivasyon scripti oluşturuldu: $USER_HOME/.hacpasaport_activate_group.sh"
    log "Otomatik başlatma dosyası oluşturuldu: $AUTOSTART_DIR/hacpasaport-group-activate.desktop"
else
    log "GNOME masaüstü tespit edilmedi. Standart kurulum devam ediyor..."
fi

log "14. Donanım kontrolü: scanimage -L"
if scanimage -L | grep -i "canon.*lide200" > /dev/null; then
    log "✅ Canon LiDE200 tarayıcı bulundu!"
else
    log "❌ Canon LiDE200 tarayıcı bulunamadı!"
    log "Lütfen tarayıcının bağlı olduğundan ve açık olduğundan emin olun."
fi

log "15. Kurulum tamamlandı!"

log "Kurulum tamamlandı!"
echo -e "\n[UYARI] Kullanıcının oturumunu sonlandırıp tekrar giriş yapmalısınız. Grup ve yetki değişikliklerinin etkili olması için bu gereklidir."
