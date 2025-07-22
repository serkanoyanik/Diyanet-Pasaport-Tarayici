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
    USER_HOME=$(eval echo "~$KULLANICI")
    USER_GROUP=$(id -gn "$KULLANICI")
    for DESKTOP_DIR in "$USER_HOME/Masaüstü" "$USER_HOME/Desktop"; do
        if [ -d "$DESKTOP_DIR" ]; then
            cp /usr/share/applications/Pasaport-Tarayıcı.desktop "$DESKTOP_DIR/Pasaport-Tarayıcı.desktop"
            chmod +x "$DESKTOP_DIR/Pasaport-Tarayıcı.desktop"
            chown "$KULLANICI:$USER_GROUP" "$DESKTOP_DIR/Pasaport-Tarayıcı.desktop"
            sudo -u "$KULLANICI" gio set "$DESKTOP_DIR/Pasaport-Tarayıcı.desktop" "metadata::trusted" yes 2>/dev/null || true
            log "Masaüstü kısayolu $DESKTOP_DIR dizinine kopyalandı, sahipliği ayarlandı ve güvenli olarak işaretlendi."
        fi
    done
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

log "1. HacPasaport dizini /opt altına kopyalanıyor..."
if [ ! -d "/opt/HacPasaport" ]; then
    if [ ! -d "$(dirname "$0")/../source/HacPasaport" ]; then
        error_exit "Kaynak HacPasaport dizini bulunamadı!"
    fi
    cp -r "$(dirname "$0")/../source/HacPasaport" /opt/ || error_exit "/opt dizinine kopyalama başarısız. Root yetkisi gerekli."
else
    log "/opt/HacPasaport zaten mevcut, kopyalama atlandı."
fi

log "2. Dosya izinleri ayarlanıyor..."
find /opt/HacPasaport -type f -exec chmod 644 {} +
chmod +x /opt/HacPasaport/pasaport.sh /opt/HacPasaport/sc.sh

# pasaport.sh ve sc.sh içeriğiyle ilgili adımlar kaldırıldı

log "3. Gerekli paketler kuruluyor..."
for pkg in pcscd tesseract-ocr tesseract-ocr-tur libacsccid1 dialog; do
    if dpkg -l | grep -qw "$pkg"; then
        log "$pkg zaten kurulu."
    else
        apt-get update && apt-get install -y "$pkg"
    fi
done

log "4. Eski oracle-java8-jre kaldırılıyor..."
if dpkg -l | grep -q oracle-java8-jre; then
    apt-get remove --purge -y oracle-java8-jre || true
    apt-get autoremove -y || true
else
    log "oracle-java8-jre zaten kurulu değil."
fi

log "5. Uyumlu oracle-java8-jre kuruluyor..."
if dpkg -l | grep -qw oracle-java8-jre; then
    log "oracle-java8-jre zaten kurulu."
else
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

log "12. Sudoers yetkisi ekleniyor..."
echo "%hacpasaport ALL=(ALL) NOPASSWD: /opt/HacPasaport/pasaport.sh, /opt/HacPasaport/sc.sh" | tee /etc/sudoers.d/diyanet > /dev/null
chmod 440 /etc/sudoers.d/diyanet
if [ ! -f /etc/sudoers.d/diyanet ]; then
    error_exit "/etc/sudoers.d/diyanet dosyası oluşturulamadı!"
fi
if ! grep -q 'hacpasaport' /etc/sudoers.d/diyanet; then
    error_exit "/etc/sudoers.d/diyanet içeriği hatalı!"
fi

log "13. Polkit yetkisi ekleniyor..."
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

log "14. Donanım kontrolü: scanimage -L"
if scanimage -L | grep -i "canon.*lide200" > /dev/null; then
    log "✅ Canon LiDE200 tarayıcı bulundu!"
else
    log "❌ Canon LiDE200 tarayıcı bulunamadı!"
    log "Lütfen tarayıcının bağlı olduğundan ve açık olduğundan emin olun."
fi

log "15. Masaüstü kısayolu oluşturuluyor..."
cat > /usr/share/applications/Pasaport-Tarayıcı.desktop <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Pasaport Tarayıcı
Comment=
Exec=sudo /opt/HacPasaport/pasaport.sh
Icon=org.gnome.SimpleScan
Path=/opt/HacPasaport
Terminal=true
StartupNotify=false
EOF
chmod 644 /usr/share/applications/Pasaport-Tarayıcı.desktop
add_desktop_shortcut

log "Kurulum tamamlandı!"
echo -e "\n[UYARI] Kullanıcının oturumunu sonlandırıp tekrar giriş yapmalısınız. Grup ve yetki değişikliklerinin etkili olması için bu gereklidir."
