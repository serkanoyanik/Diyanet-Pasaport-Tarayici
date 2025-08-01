import gi
import os
import subprocess
import datetime
import pwd
import grp
import threading

gi.require_version("Gtk", "3.0")
gi.require_version("Vte", "2.91")
from gi.repository import Gtk, Vte, GLib, Gdk, GdkPixbuf

def get_app_base_path():
    """Uygulamanın temel dizinini belirle - geliştirme veya kurulum moduna göre"""
    # Eğer /opt/HacPasaport/app altında çalışıyorsa (DEB paketi kurulumu)
    if os.path.exists("/opt/HacPasaport/app/app.py"):
        return "/opt/HacPasaport/app"
    # Geliştirme modunda
    else:
        return os.path.dirname(__file__)

def get_resource_path(resource_type, filename):
    """Kaynak dosyaların yolunu belirle"""
    base_path = get_app_base_path()
    
    if resource_type == "ui":
        # UI dosyaları /usr/share/hac-pasaport-kurulum/ui altında
        if os.path.exists(f"/usr/share/hac-pasaport-kurulum/ui/{filename}"):
            return f"/usr/share/hac-pasaport-kurulum/ui/{filename}"
        else:
            return os.path.join(base_path, "ui", filename)
    elif resource_type == "icons":
        # İkon dosyaları /usr/share/hac-pasaport-kurulum/icons altında
        if os.path.exists(f"/usr/share/hac-pasaport-kurulum/icons/{filename}"):
            return f"/usr/share/hac-pasaport-kurulum/icons/{filename}"
        else:
            return os.path.join(base_path, "icons", filename)
    elif resource_type == "scripts":
        # Script dosyaları için öncelik sırası:
        # 1. /opt/HacPasaport/app/script/install.sh (DEB paketi kurulumu sonrası)
        # 2. script/install.sh (geliştirme modu)
        if os.path.exists(f"/opt/HacPasaport/app/script/{filename}"):
            return f"/opt/HacPasaport/app/script/{filename}"
        else:
            return os.path.join(base_path, "script", filename)
    else:
        return os.path.join(base_path, resource_type, filename)

class ScannerCheckDialog(Gtk.Dialog):
    def __init__(self, parent, scanner_found):
        super().__init__(title="Tarayıcı Durumu", transient_for=parent, modal=True)
        self.set_default_size(400, 200)
        
        box = self.get_content_area()
        
        if scanner_found:
            label = Gtk.Label(label="✅ Canon LiDE200 tarayıcı bulundu!\n\nTarayıcı hazır durumda.")
            label.set_line_wrap(True)
        else:
            label = Gtk.Label(label="❌ Canon LiDE200 tarayıcı bulunamadı!\n\nLütfen tarayıcının bağlı olduğundan ve açık olduğundan emin olun.\n\nDesteklenen tarayıcı: Canon LiDE200")
            label.set_line_wrap(True)
        
        box.add(label)
        self.add_button("Tamam", Gtk.ResponseType.OK)
        self.show_all()

class GroupInfoDialog(Gtk.Dialog):
    def __init__(self, parent):
        super().__init__(title="Grup Üyeliği Bilgisi", transient_for=parent, modal=True)
        self.set_default_size(450, 250)
        
        box = self.get_content_area()
        
        info_text = """ℹ️ Önemli Bilgi

Kullanıcı HacPasaport grubuna eklendikten sonra:

1. Oturumu kapatıp tekrar giriş yapın
2. Eğer grup üyeliği aktif olmazsa, sistemi yeniden başlatın

Bu, Linux sistemlerinde grup üyeliklerinin aktif olması için gereklidir.

Not: Bazı masaüstü ortamlarında (özellikle GNOME) grup üyeliğinin aktif olması için yeniden başlatma gerekebilir."""
        
        label = Gtk.Label(label=info_text)
        label.set_line_wrap(True)
        label.set_justify(Gtk.Justification.LEFT)
        
        box.add(label)
        self.add_button("Anladım", Gtk.ResponseType.OK)
        self.show_all()

class UserSelectDialog(Gtk.Dialog):
    def __init__(self, parent, user_list):
        super().__init__(title="Kullanıcı Seç", transient_for=parent, modal=True)
        self.set_default_size(350, 200)
        self.user_combo = Gtk.ComboBoxText()
        for user in user_list:
            self.user_combo.append_text(user)
        self.user_combo.set_active(0)
        box = self.get_content_area()
        box.add(Gtk.Label(label="HacPasaport grubuna eklenecek kullanıcıyı seçin:"))
        box.add(self.user_combo)
        self.add_button("İptal", Gtk.ResponseType.CANCEL)
        self.add_button("Seç", Gtk.ResponseType.OK)
        self.show_all()
    def get_selected_user(self):
        return self.user_combo.get_active_text()

class AppWindow:
    def __init__(self, application):
        builder = Gtk.Builder()
        ui_path = get_resource_path("ui", "window.ui")
        builder.add_from_file(ui_path)

        self.window = builder.get_object("main_window")
        self.window.set_application(application)

        self.install_button = builder.get_object("install_button")
        self.about_button = builder.get_object("about_button")
        self.screenshot_button = builder.get_object("screenshot_button")
        
        # Header bar ikonları için dinamik yol ayarla
        about_image = self.about_button.get_child()
        if about_image and isinstance(about_image, Gtk.Image):
            about_icon_path = get_resource_path("icons", "open-menu.png")
            if os.path.exists(about_icon_path):
                about_image.set_from_file(about_icon_path)
                print(f"About ikonu yüklendi: {about_icon_path}")
            else:
                print(f"About ikonu bulunamadı: {about_icon_path}")
        
        screenshot_image = self.screenshot_button.get_child()
        if screenshot_image and isinstance(screenshot_image, Gtk.Image):
            screenshot_icon_path = get_resource_path("icons", "camera.png")
            if os.path.exists(screenshot_icon_path):
                screenshot_image.set_from_file(screenshot_icon_path)
                print(f"Screenshot ikonu yüklendi: {screenshot_icon_path}")
            else:
                print(f"Screenshot ikonu bulunamadı: {screenshot_icon_path}")
        
        # DIB logosu için dinamik yol ayarla
        self.dib_logo = builder.get_object("dib_logo")
        logo_path = get_resource_path("icons", "dib_logo.png")
        if os.path.exists(logo_path):
            # Logo dosyasını boyutlandırarak yükle
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(logo_path, 200, 200, True)
                self.dib_logo.set_from_pixbuf(pixbuf)
                print(f"DIB logosu boyutlandırılarak yüklendi: {logo_path}")
            except Exception as e:
                print(f"Logo boyutlandırma hatası: {e}")
                self.dib_logo.set_from_file(logo_path)
                print(f"DIB logosu normal yüklendi: {logo_path}")
        else:
            print(f"DIB logosu bulunamadı: {logo_path}")
        self.terminal_placeholder = builder.get_object("terminal_placeholder")

        self.vte_terminal = Vte.Terminal()
        self.vte_terminal.set_font_scale(1.0)
        self.vte_terminal.set_cursor_blink_mode(Vte.CursorBlinkMode.OFF)
        self.vte_terminal.set_allow_bold(True)
        self.vte_terminal.set_scrollback_lines(-1)
        self.vte_terminal.set_input_enabled(False)
        self.vte_terminal.set_scroll_on_output(True)
        self.vte_terminal.set_scroll_on_keystroke(True)
        self.vte_terminal.set_mouse_autohide(True)
        self.terminal_placeholder.pack_start(self.vte_terminal, True, True, 0)
        self.vte_terminal.show()

        self.install_button.connect("clicked", self.on_install_button_clicked)
        self.about_button.connect("clicked", self.on_menu_button_clicked)
        self.screenshot_button.connect("clicked", self.on_screenshot_button_clicked)

        # CSS stillerini uygula
        self.apply_css_styles()
        
        # Butonları özelleştirilmiş widget'larla değiştir
        self._replace_buttons_with_custom_widgets()
        
        # Pencereyi ortala
        self.center_window()

        self.window.show_all()

    def check_scanner(self):
        """Canon LiDE200 tarayıcısının varlığını kontrol et"""
        try:
            result = subprocess.run(['scanimage', '-L'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                scanner_output = result.stdout.lower()
                # Canon LiDE200 veya benzer Canon tarayıcıları ara
                if 'canon' in scanner_output and ('lide200' in scanner_output or 'lide' in scanner_output):
                    return True
                else:
                    print("Tarayıcı bulunamadı. Çıktı:", result.stdout)
                    return False
            else:
                print("scanimage komutu başarısız:", result.stderr)
                return False
        except subprocess.TimeoutExpired:
            print("scanimage komutu zaman aşımına uğradı")
            return False
        except FileNotFoundError:
            print("scanimage komutu bulunamadı")
            return False
        except Exception as e:
            print(f"Tarayıcı kontrolü hatası: {e}")
            return False

    def get_all_users(self):
        """Tüm kullanıcıları al (yerel ve domain kullanıcıları dahil)"""
        users = []
        try:
            # /etc/passwd'den kullanıcıları al
            for p in pwd.getpwall():
                if p.pw_uid >= 1000 and p.pw_name != "nobody":
                    users.append(p.pw_name)
            
            # Domain kullanıcılarını kontrol et (Active Directory)
            # /home/DIB/ altındaki kullanıcıları ara
            dib_home = "/home/DIB"
            if os.path.exists(dib_home):
                for item in os.listdir(dib_home):
                    item_path = os.path.join(dib_home, item)
                    if os.path.isdir(item_path) and item not in users:
                        users.append(item)
            
            # getent passwd ile domain kullanıcılarını da al
            try:
                result = subprocess.run(['getent', 'passwd'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    for line in result.stdout.splitlines():
                        parts = line.split(':')
                        if len(parts) >= 3:
                            username = parts[0]
                            uid = int(parts[2])
                            if uid >= 1000 and username not in users and username != "nobody":
                                users.append(username)
            except Exception as e:
                print(f"Domain kullanıcıları alınırken hata: {e}")
                
        except Exception as e:
            print(f"Kullanıcı listesi alınırken hata: {e}")
        
        return sorted(set(users))

    def show_scanner_check(self):
        """Tarayıcı durumunu kontrol et ve bilgi ver"""
        scanner_found = self.check_scanner()
        dialog = ScannerCheckDialog(self.window, scanner_found)
        dialog.run()
        dialog.destroy()
        return scanner_found

    def show_group_info(self):
        """Grup üyeliği hakkında bilgi ver"""
        # Masaüstü ortamını tespit et
        desktop_env = self.detect_desktop_environment()
        
        if desktop_env == 'gnome':
            # GNOME için özel mesaj
            dialog = self._create_gnome_group_info_dialog()
        else:
            # Diğer masaüstü ortamları için genel mesaj
            dialog = self._create_general_group_info_dialog()
        
        dialog.run()
        dialog.destroy()
    
    def _create_gnome_group_info_dialog(self):
        """GNOME masaüstü için özel grup bilgi dialog'u"""
        dialog = Gtk.Dialog(title="Grup Üyeliği Bilgisi - GNOME", transient_for=self.window, modal=True)
        dialog.set_default_size(500, 300)
        
        box = dialog.get_content_area()
        
        info_text = """ℹ️ GNOME Masaüstü - Grup Üyeliği Bilgisi

Kullanıcı HacPasaport grubuna eklendikten sonra:

✅ Otomatik Aktivasyon:
GNOME ortamında grup üyeliği otomatik olarak aktif hale getirilmeye çalışıldı.

🔄 Oturum Yenileme (Önerilen):
1. Oturumu kapatın (Çıkış Yap)
2. Tekrar giriş yapın
3. Terminal'de 'groups' komutu ile kontrol edin

✅ Gelişmiş GNOME Aktivasyonu:
Artık GNOME'da oturum kapatıp açtıktan sonra grup üyeliği otomatik olarak aktif hale gelecek.

⚠️ GNOME Özel Durumu:
GNOME masaüstü ortamında grup üyelikleri bazen oturum kapatıp açma ile aktif olmayabilir. Bu durumda:

🔄 Alternatif Yöntemler:
• Yeni bir terminal penceresi açın (Ctrl+Alt+T)
• 'groups' komutu ile kontrol edin
• Otomatik aktivasyon scripti çalıştırın: ~/.hacpasaport_activate_group.sh

⚠️ ÖNEMLİ UYARI:
Eğer masaüstü erişimi kaybolursa veya grup üyeliği aktif olmazsa:
• Bilgisayarı yeniden başlatın
• Veya yeni bir oturum açın (Ctrl+Alt+F2)

🔍 Grup Üyeliğini Kontrol Etmek İçin:
Terminal'de şu komutu çalıştırın:
groups

✅ Başarılı grup üyeliği şöyle görünür:
pardus-adm adm dialout cdrom floppy sudo audio dip video plugdev netdev hacpasaport

💡 İpucu: GNOME'da grup üyeliklerinin aktif olması için bazen yeni terminal pencereleri açmak gerekebilir.

🛠️ Otomatik Aktivasyon Araçları:
• ~/.hacpasaport_activate_group.sh - Grup üyeliğini aktif hale getirir
• ~/.hacpasaport_session_start.sh - Oturum başlangıcında grup üyeliğini aktif hale getirir
• ~/.hacpasaport_group_check.sh - Grup üyeliğini kontrol eder

🔧 Sorun Giderme:
Eğer masaüstü erişimi kaybolursa, terminal'de şu komutu çalıştırın:
sudo systemctl restart gdm

✅ Yeni Özellik:
GNOME'da oturum kapatıp açtıktan sonra grup üyeliği otomatik olarak aktif hale gelecek."""
        
        label = Gtk.Label(label=info_text)
        label.set_line_wrap(True)
        label.set_justify(Gtk.Justification.LEFT)
        
        # Scroll view ekle
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.add(label)
        
        box.add(scrolled_window)
        dialog.add_button("Anladım", Gtk.ResponseType.OK)
        dialog.show_all()
        
        return dialog
    
    def _create_general_group_info_dialog(self):
        """Genel masaüstü ortamları için grup bilgi dialog'u"""
        dialog = Gtk.Dialog(title="Grup Üyeliği Bilgisi", transient_for=self.window, modal=True)
        dialog.set_default_size(450, 250)
        
        box = dialog.get_content_area()
        
        info_text = """ℹ️ Önemli Bilgi

Kullanıcı HacPasaport grubuna eklendikten sonra:

1. Oturumu kapatıp tekrar giriş yapın
2. Eğer grup üyeliği aktif olmazsa, sistemi yeniden başlatın

Bu, Linux sistemlerinde grup üyeliklerinin aktif olması için gereklidir.

⚠️ Masaüstü Ortamı Uyarısı:
Bazı masaüstü ortamlarında grup üyeliğinin aktif olması için yeniden başlatma gerekebilir. Eğer oturum kapatıp açma yeterli olmazsa, bilgisayarı yeniden başlatın.

🔍 Grup Üyeliğini Kontrol Etmek İçin:
Terminal'de 'groups' komutunu çalıştırarak hacpasaport grubunun listede olup olmadığını kontrol edebilirsiniz."""
        
        label = Gtk.Label(label=info_text)
        label.set_line_wrap(True)
        label.set_justify(Gtk.Justification.LEFT)
        
        box.add(label)
        dialog.add_button("Anladım", Gtk.ResponseType.OK)
        dialog.show_all()
        
        return dialog

    def on_install_button_clicked(self, widget):
        # Tarayıcı kontrolünü arka planda başlat
        threading.Thread(target=self._background_scanner_check, daemon=True).start()
        
        users = self.get_all_users()
        dialog = UserSelectDialog(self.window, users)
        response = dialog.run()
        selected_user = dialog.get_selected_user() if response == Gtk.ResponseType.OK else None
        dialog.destroy()
        if not selected_user:
            return
        self.install_button.set_sensitive(False)
        self.vte_terminal.reset(True, True)
        # Gerçek kurulum scriptini kullan
        script_path = get_resource_path("scripts", "install.sh")
        if not os.path.exists(script_path):
            self.vte_terminal.feed_child("Hata: Kurulum betiği bulunamadı!\n".encode('utf-8'))
            self.install_button.set_sensitive(True)
            return
        
        self.vte_terminal.feed_child(f"Gerçek kurulum başlatılıyor... Script: {script_path}\n".encode('utf-8'))
        self.vte_terminal.feed_child("⚠️ Bu gerçek kurulum scriptidir. /opt/HacPasaport dizini gerekli!\n".encode('utf-8'))
        self.vte_terminal.spawn_async(
            Vte.PtyFlags.DEFAULT, None, ["pkexec", "/bin/bash", script_path, selected_user], [],
            GLib.SpawnFlags.DO_NOT_REAP_CHILD, None, None, -1, None, self.on_child_exited, None)

    def _background_scanner_check(self):
        found = self.check_scanner()
        if found:
            GLib.idle_add(self.vte_terminal.feed_child, "Canon LiDE200 tarayıcı bulundu.\n".encode('utf-8'))
        else:
            GLib.idle_add(self.vte_terminal.feed_child, "Uyarı: Canon LiDE200 tarayıcı bulunamadı! Kuruluma devam ediliyor...\n".encode('utf-8'))



    def on_child_exited(self, terminal, pid, status, user_data):
        self.install_button.set_sensitive(True)
        if status == 0:
            self.vte_terminal.feed_child("\n--- Kurulum başarıyla tamamlandı! ---\n".encode('utf-8'))
            # Grup üyeliği hakkında bilgi ver
            GLib.idle_add(self.show_group_info)
        else:
            self.vte_terminal.feed_child("\n--- Kurulumda bir hata oluştu veya iptal edildi! ---\n".encode('utf-8'))

    def on_menu_button_clicked(self, widget):
        """Menü butonuna tıklandığında dropdown menü göster"""
        # Popup menü oluştur
        menu = Gtk.Menu()
        
        # Uygulama Hakkında menü öğesi
        about_item = Gtk.MenuItem()
        about_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        
        # Information ikonu
        info_icon_path = get_resource_path("icons", "info.svg")
        if os.path.exists(info_icon_path):
            try:
                # SVG dosyasını boyutlandırarak yükle
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(info_icon_path, 16, 16, True)
                info_image = Gtk.Image.new_from_pixbuf(pixbuf)
            except Exception as e:
                print(f"Info ikonu yükleme hatası: {e}")
                # Fallback ikon
                info_image = Gtk.Image.new_from_icon_name("dialog-information", Gtk.IconSize.MENU)
        else:
            # Fallback ikon
            info_image = Gtk.Image.new_from_icon_name("dialog-information", Gtk.IconSize.MENU)
        about_box.pack_start(info_image, False, False, 0)
        
        about_label = Gtk.Label(label="Uygulama Hakkında")
        about_box.pack_start(about_label, True, True, 0)
        about_item.add(about_box)
        about_item.connect("activate", self.on_about_menu_clicked)
        menu.append(about_item)
        
        # Ayırıcı
        separator = Gtk.SeparatorMenuItem()
        menu.append(separator)
        
        # Uygulamayı Kaldır menü öğesi
        uninstall_item = Gtk.MenuItem()
        uninstall_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        
        # Uninstall ikonu
        uninstall_icon_path = get_resource_path("icons", "uninstall.svg")
        if os.path.exists(uninstall_icon_path):
            try:
                # SVG dosyasını boyutlandırarak yükle
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(uninstall_icon_path, 16, 16, True)
                uninstall_image = Gtk.Image.new_from_pixbuf(pixbuf)
            except Exception as e:
                print(f"Uninstall ikonu yükleme hatası: {e}")
                # Fallback ikon
                uninstall_image = Gtk.Image.new_from_icon_name("edit-delete", Gtk.IconSize.MENU)
        else:
            # Fallback ikon
            uninstall_image = Gtk.Image.new_from_icon_name("edit-delete", Gtk.IconSize.MENU)
        uninstall_box.pack_start(uninstall_image, False, False, 0)
        
        uninstall_label = Gtk.Label(label="Uygulamayı Kaldır")
        uninstall_box.pack_start(uninstall_label, True, True, 0)
        uninstall_item.add(uninstall_box)
        uninstall_item.connect("activate", self.on_uninstall_menu_clicked)
        menu.append(uninstall_item)
        
        # Menü stillerini programatik olarak ayarla
        menu.get_style_context().add_class("custom-menu")
        
        # Menüye çıkıntı ekle
        self.add_menu_arrow(menu)
        
        menu.show_all()
        
        # Menüyü butonun tam altında göster
        menu.popup_at_widget(widget, Gdk.Gravity.SOUTH_WEST, Gdk.Gravity.NORTH_WEST, None)
    
    def on_about_menu_clicked(self, widget):
        """Uygulama Hakkında menü öğesine tıklandığında"""
        about_dialog = Gtk.AboutDialog(
            transient_for=self.window, modal=True, authors=["Serkan Oyanık"],
            comments="Bu uygulama, Pasaport Tarayıcı için gerekli kurulumları yapar.",
            program_name="Diyanet Pasaport Tarayıcı Kurulum", version="1.0.0",
            website="https://github.com/serkanoyanik/Diyanet-Pasaport-Tarayici", website_label="Proje Github Reposu"
        )
        
        # DIB logosunu yükle ve ekle
        try:
            logo_path = get_resource_path("icons", "dib_logo.png")
            if os.path.exists(logo_path):
                # Logo boyutunu ayarla (AboutDialog için uygun boyut)
                logo_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                    logo_path, 128, 128, True)  # 128x128 piksel boyutunda
                about_dialog.set_logo(logo_pixbuf)
                print(f"DIB logosu başarıyla yüklendi: {logo_path}")
            else:
                print(f"Logo dosyası bulunamadı: {logo_path}")
        except Exception as e:
            print(f"Logo yükleme hatası: {str(e)}")
        
        # Kapat butonunu düzelt
        about_dialog.connect("response", self.on_about_dialog_response)
        about_dialog.present()
    
    def add_menu_arrow(self, menu):
        """Menüye çıkıntı (arrow) ekle"""
        try:
            # Menü penceresini al
            menu_window = menu.get_window()
            if menu_window:
                # Çıkıntı için bir overlay widget oluştur
                arrow_overlay = Gtk.Overlay()
                arrow_overlay.add(menu)
                
                # Çıkıntı için bir drawing area oluştur
                arrow_drawing = Gtk.DrawingArea()
                arrow_drawing.set_size_request(16, 8)
                arrow_drawing.connect("draw", self.draw_menu_arrow)
                
                arrow_overlay.add_overlay(arrow_drawing)
                arrow_overlay.show_all()
                
        except Exception as e:
            print(f"Menü çıkıntısı eklenirken hata: {e}")
    
    def draw_menu_arrow(self, widget, cr):
        """Menü çıkıntısını çiz"""
        try:
            # Beyaz üçgen çiz
            cr.set_source_rgb(1, 1, 1)  # Beyaz
            cr.move_to(8, 0)
            cr.line_to(0, 8)
            cr.line_to(16, 8)
            cr.close_path()
            cr.fill()
            
            # Kenarlık için gri üçgen çiz
            cr.set_source_rgb(0.88, 0.88, 0.88)  # Açık gri
            cr.move_to(8, 0)
            cr.line_to(0, 8)
            cr.line_to(16, 8)
            cr.close_path()
            cr.stroke()
            
        except Exception as e:
            print(f"Çıkıntı çizilirken hata: {e}")
    
    def on_uninstall_menu_clicked(self, widget):
        """Uygulamayı Kaldır menü öğesine tıklandığında"""
        # Onay dialog'u göster
        dialog = Gtk.MessageDialog(
            transient_for=self.window,
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Uygulamayı Kaldır",
            secondary_text="Diyanet Pasaport Kurulum uygulamasını kaldırmak istediğinizden emin misiniz?\n\nBu işlem:\n• Tüm kısayolları kaldıracak\n• Kullanıcı gruplarını temizleyecek\n• Sistem dosyalarını silecek\n• Uygulama dizinini kaldıracak\n\nNot: Bu işlem için yönetici yetkisi gereklidir."
        )
        
        response = dialog.run()
        dialog.destroy()
        
        if response == Gtk.ResponseType.YES:
            # Kaldırma işlemini başlat
            self.vte_terminal.feed_child("Uygulama kaldırma işlemi başlatılıyor...\n".encode('utf-8'))
            
            # dpkg ile standart DEB paketi kaldırma işlemi
            self.vte_terminal.feed_child("dpkg ile standart kaldırma işlemi başlatılıyor...\n".encode('utf-8'))
            self.vte_terminal.spawn_async(
                Vte.PtyFlags.DEFAULT, None, ["pkexec", "dpkg", "-r", "diyanet-pasaport-kurulum"], [],
                GLib.SpawnFlags.DO_NOT_REAP_CHILD, None, None, -1, None, self.on_uninstall_exited, None)
        else:
            self.vte_terminal.feed_child("Uygulama kaldırma işlemi iptal edildi.\n".encode('utf-8'))
    
    def on_uninstall_exited(self, terminal, pid, status, user_data):
        """Kaldırma işlemi tamamlandığında"""
        if status == 0:
            self.vte_terminal.feed_child("✅ Uygulama başarıyla kaldırıldı!\n".encode('utf-8'))
            self.vte_terminal.feed_child("dpkg ile standart kaldırma işlemi tamamlandı.\n".encode('utf-8'))
            # Uygulamayı kapat
            GLib.timeout_add(2000, self.close_application)
        else:
            self.vte_terminal.feed_child("❌ Uygulama kaldırma işleminde hata oluştu!\n".encode('utf-8'))
            self.vte_terminal.feed_child("Hata kodu: {}\n".format(status).encode('utf-8'))
            # Hata durumunda manuel kaldırma seçeneği sun
            self.vte_terminal.feed_child("Manuel kaldırma seçeneği denenebilir.\n".encode('utf-8'))
    
    def manual_uninstall(self):
        """Manuel kaldırma işlemi"""
        try:
            # Temel kaldırma işlemleri
            commands = [
                "rm -rf /opt/HacPasaport",
                "rm -f /usr/share/applications/Pasaport-Tarayıcı-Kurulum.desktop",
                "rm -f /etc/sudoers.d/diyanet",
                "rm -f /etc/polkit-1/localauthority/50-local.d/99-scan.pkla",
                "groupdel hacpasaport 2>/dev/null || true"
            ]
            
            for cmd in commands:
                self.vte_terminal.feed_child(f"Komut çalıştırılıyor: {cmd}\n".encode('utf-8'))
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    self.vte_terminal.feed_child("✅ Başarılı\n".encode('utf-8'))
                else:
                    self.vte_terminal.feed_child(f"⚠️ Uyarı: {result.stderr}\n".encode('utf-8'))
            
            self.vte_terminal.feed_child("✅ Manuel kaldırma işlemi tamamlandı!\n".encode('utf-8'))
            # Uygulamayı kapat
            GLib.timeout_add(2000, self.close_application)
            
        except Exception as e:
            self.vte_terminal.feed_child(f"❌ Manuel kaldırma hatası: {str(e)}\n".encode('utf-8'))
    
    def close_application(self):
        """Uygulamayı kapat"""
        self.window.close()
        return False
    
    def on_about_dialog_response(self, dialog, response):
        dialog.destroy()
    
    def apply_css_styles(self):
        """CSS stillerini harici dosyadan yükle"""
        try:
            css_path = get_resource_path("ui", "styles.css")
            print(f"CSS dosya yolu: {css_path}")
            print(f"CSS dosyası var mı: {os.path.exists(css_path)}")
            
            if os.path.exists(css_path):
                css_provider = Gtk.CssProvider()
                css_provider.load_from_path(css_path)
                screen = Gdk.Screen.get_default()
                style_context = Gtk.StyleContext()
                style_context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
                print("CSS stilleri başarıyla yüklendi.")
                self.vte_terminal.feed_child("CSS stilleri başarıyla yüklendi.\n".encode('utf-8'))
            else:
                print("Uyarı: CSS dosyası bulunamadı!")
                self.vte_terminal.feed_child("Uyarı: CSS dosyası bulunamadı, varsayılan stiller kullanılıyor.\n".encode('utf-8'))
        except Exception as e:
            print(f"CSS yükleme hatası: {str(e)}")
            self.vte_terminal.feed_child(f"CSS yükleme hatası: {str(e)}\n".encode('utf-8'))
    
    def center_window(self):
        """Pencereyi ekranın ortasına yerleştir"""
        self.window.set_position(Gtk.WindowPosition.CENTER)
    
    def _replace_buttons_with_custom_widgets(self):
        """Butonları CSS ile özelleştir"""
        try:
            print("Buton özelleştirme başlıyor...")
            
            # Butonlara CSS sınıfını ekle
            self.install_button.get_style_context().add_class("rounded-green-button")
            print("CSS sınıfları eklendi.")
            
            # Buton boyutlarını zorla
            self.install_button.set_size_request(20, 25)
            print("Buton boyutları ayarlandı.")
            
            # Buton genişliğini zorla
            self.install_button.set_property("width-request", 20)
            print("Buton genişliği zorlandı.")
            
            # Butonları yeniden çiz
            self.install_button.queue_resize()
            print("Butonlar yeniden çizildi.")
            
            self.vte_terminal.feed_child("Butonlar CSS ile özelleştirildi.\n".encode('utf-8'))
            print("Buton özelleştirme tamamlandı.")
            
        except Exception as e:
            print(f"Buton özelleştirme hatası: {str(e)}")
            self.vte_terminal.feed_child(f"Buton özelleştirme hatası: {str(e)}\n".encode('utf-8'))
    

    
    def on_screenshot_button_clicked(self, widget):
        """Screenshot butonuna tıklandığında çalışır"""
        try:
            # Doğrudan screenshot al
            self.take_screenshot()
        except Exception as e:
            self.vte_terminal.feed_child(f"Hata: Screenshot alınamadı - {str(e)}\n".encode('utf-8'))
    
    def take_screenshot(self):
        """Screenshot al ve kaydet"""
        try:
            # Pencereyi öne getir
            self.window.present()
            self.window.set_keep_above(True)
            
            # Kısa bir bekleme süresi
            GLib.timeout_add(500, self._take_screenshot_delayed)
            
        except Exception as e:
            self.vte_terminal.feed_child(f"Hata: Screenshot alınamadı - {str(e)}\n".encode('utf-8'))
    
    def _take_screenshot_delayed(self):
        """Gecikmeli screenshot alma"""
        try:
            # Pencereyi normal konuma getir
            self.window.set_keep_above(False)
            
            # Masaüstü ortamını tespit et
            desktop_env = self.detect_desktop_environment()
            self.vte_terminal.feed_child(f"Screenshot alınıyor... Masaüstü: {desktop_env}\n".encode('utf-8'))
            
            # Geçici dosya adı oluştur
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_filename = f"/tmp/pasaport_tarayici_{timestamp}.png"
            
            # Önce screenshot al
            success = self._take_screenshot_with_desktop_tool(temp_filename, desktop_env)
            
            if success and os.path.exists(temp_filename):
                # Screenshot başarılı, şimdi kaydetme dialog'u göster
                self._show_save_dialog(temp_filename)
            else:
                # Masaüstü aracı başarısızsa alternatif yöntem
                self.vte_terminal.feed_child("Masaüstü aracı başarısız, alternatif yöntem deneniyor...\n".encode('utf-8'))
                self._take_screenshot_alternative(temp_filename)
                
        except Exception as e:
            self.vte_terminal.feed_child(f"Hata: Screenshot alınamadı - {str(e)}\n".encode('utf-8'))
        
        return False  # timeout'u durdur
    
    def _show_save_dialog(self, temp_filename):
        """Kaydetme dialog'unu göster"""
        try:
            # Dosya adı oluştur
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"pasaport_tarayici_{timestamp}.png"
            
            # Kaydetme dialog'u göster
            dialog = Gtk.FileChooserDialog(
                title="Screenshot Kaydet",
                transient_for=self.window,
                action=Gtk.FileChooserAction.SAVE
            )
            dialog.add_button("İptal", Gtk.ResponseType.CANCEL)
            dialog.add_button("Kaydet", Gtk.ResponseType.OK)
            dialog.set_current_name(default_filename)
            
            # PNG filtresi ekle
            png_filter = Gtk.FileFilter()
            png_filter.set_name("PNG Dosyaları")
            png_filter.add_pattern("*.png")
            dialog.add_filter(png_filter)
            
            response = dialog.run()
            
            if response == Gtk.ResponseType.OK:
                filename = dialog.get_filename()
                if not filename.endswith('.png'):
                    filename += '.png'
                
                # Geçici dosyayı hedef konuma kopyala
                import shutil
                shutil.copy2(temp_filename, filename)
                
                # Geçici dosyayı sil
                try:
                    os.remove(temp_filename)
                except:
                    pass
                
                self.vte_terminal.feed_child(f"Screenshot başarıyla kaydedildi: {filename}\n".encode('utf-8'))
            else:
                self.vte_terminal.feed_child("Screenshot iptal edildi.\n".encode('utf-8'))
                # Geçici dosyayı sil
                try:
                    os.remove(temp_filename)
                except:
                    pass
            
            dialog.destroy()
            
        except Exception as e:
            self.vte_terminal.feed_child(f"Hata: Dosya kaydetme hatası - {str(e)}\n".encode('utf-8'))
    
    def detect_desktop_environment(self):
        """Masaüstü ortamını tespit et"""
        try:
            # 1. XDG_CURRENT_DESKTOP değişkenini kontrol et
            desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
            if desktop:
                print(f"XDG_CURRENT_DESKTOP tespit edildi: {desktop}")
                if 'xfce' in desktop:
                    return 'xfce'
                elif 'gnome' in desktop:
                    return 'gnome'
                elif 'kde' in desktop:
                    return 'kde'
                elif 'mate' in desktop:
                    return 'mate'
                elif 'cinnamon' in desktop:
                    return 'cinnamon'
            
            # 2. DESKTOP_SESSION değişkenini kontrol et
            desktop_session = os.environ.get('DESKTOP_SESSION', '').lower()
            if desktop_session:
                print(f"DESKTOP_SESSION tespit edildi: {desktop_session}")
                if 'xfce' in desktop_session:
                    return 'xfce'
                elif 'gnome' in desktop_session:
                    return 'gnome'
                elif 'kde' in desktop_session:
                    return 'kde'
                elif 'mate' in desktop_session:
                    return 'mate'
                elif 'cinnamon' in desktop_session:
                    return 'cinnamon'
            
            # 3. Alternatif yöntem: ps komutu ile kontrol
            result = subprocess.run(['ps', '-e'], capture_output=True, text=True)
            if result.returncode == 0:
                ps_output = result.stdout.lower()
                if 'xfce4-session' in ps_output:
                    print("XFCE session process tespit edildi")
                    return 'xfce'
                elif 'gnome-session' in ps_output:
                    print("GNOME session process tespit edildi")
                    return 'gnome'
                elif 'plasma-session' in ps_output or 'kde' in ps_output:
                    print("KDE session process tespit edildi")
                    return 'kde'
                elif 'mate-session' in ps_output:
                    print("MATE session process tespit edildi")
                    return 'mate'
                elif 'cinnamon-session' in ps_output:
                    print("Cinnamon session process tespit edildi")
                    return 'cinnamon'
            
            # 4. Son çare: Kullanıcının home dizinindeki config dosyalarını kontrol et
            home_dir = os.path.expanduser("~")
            if os.path.exists(os.path.join(home_dir, ".config", "gnome-session")):
                print("GNOME config dosyaları tespit edildi")
                return 'gnome'
            elif os.path.exists(os.path.join(home_dir, ".config", "xfce4")):
                print("XFCE config dosyaları tespit edildi")
                return 'xfce'
            elif os.path.exists(os.path.join(home_dir, ".config", "kdeglobals")):
                print("KDE config dosyaları tespit edildi")
                return 'kde'
            
            print("Masaüstü ortamı tespit edilemedi")
            return 'unknown'
            
        except Exception as e:
            print(f"Masaüstü ortamı tespit hatası: {e}")
            return 'unknown'
    
    def _take_screenshot_with_desktop_tool(self, filename, desktop_env):
        """Masaüstü ortamına göre screenshot aracını kullan"""
        try:
            if desktop_env == 'xfce':
                # XFCE için xfce4-screenshooter -w parametresi ile pencere görüntüsü
                cmd = f"xfce4-screenshooter -w --save={filename}"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    self.vte_terminal.feed_child(f"XFCE pencere screenshot başarıyla kaydedildi: {filename}\n".encode('utf-8'))
                    return True
                else:
                    self.vte_terminal.feed_child(f"XFCE screenshot hatası: {result.stderr}\n".encode('utf-8'))
                    return False
                    
            elif desktop_env == 'gnome':
                # GNOME için gnome-screenshot -w parametresi ile pencere görüntüsü
                cmd = f"gnome-screenshot -w --file={filename}"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    self.vte_terminal.feed_child(f"GNOME pencere screenshot başarıyla kaydedildi: {filename}\n".encode('utf-8'))
                    return True
                else:
                    self.vte_terminal.feed_child(f"GNOME screenshot hatası: {result.stderr}\n".encode('utf-8'))
                    return False
                    
            elif desktop_env == 'kde':
                # KDE için spectacle -w parametresi ile pencere görüntüsü
                cmd = f"spectacle -w --output={filename}"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    self.vte_terminal.feed_child(f"KDE pencere screenshot başarıyla kaydedildi: {filename}\n".encode('utf-8'))
                    return True
                else:
                    self.vte_terminal.feed_child(f"KDE screenshot hatası: {result.stderr}\n".encode('utf-8'))
                    return False
                    
            else:
                # Bilinmeyen masaüstü ortamı için genel araçları dene
                tools = ['gnome-screenshot', 'xfce4-screenshooter', 'spectacle']
                
                for tool in tools:
                    try:
                        if tool == 'gnome-screenshot':
                            cmd = f"gnome-screenshot -w --file={filename}"
                        elif tool == 'xfce4-screenshooter':
                            cmd = f"xfce4-screenshooter -w --save={filename}"
                        elif tool == 'spectacle':
                            cmd = f"spectacle -w --output={filename}"
                        
                        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
                        
                        if result.returncode == 0:
                            self.vte_terminal.feed_child(f"{tool} ile pencere screenshot başarıyla kaydedildi: {filename}\n".encode('utf-8'))
                            return True
                    except:
                        continue
                
                return False
                
        except Exception as e:
            self.vte_terminal.feed_child(f"Screenshot aracı hatası: {str(e)}\n".encode('utf-8'))
            return False
    
    def _take_screenshot_alternative(self, filename):
        """Alternatif screenshot yöntemi"""
        try:
            # Pencere boyutlarını al
            width, height = self.window.get_size()
            
            # Uygulama penceresinin screenshot'ını al
            window = self.window.get_window()
            if window:
                # Screenshot al
                pixbuf = Gdk.pixbuf_get_from_window(window, 0, 0, width, height)
                
                if pixbuf:
                    # Dosyayı kaydet
                    pixbuf.savev(filename, "png", [], [])
                    self.vte_terminal.feed_child(f"GTK API ile screenshot başarıyla kaydedildi: {filename}\n".encode('utf-8'))
                    
                    # Kaydetme dialog'unu göster
                    self._show_save_dialog(filename)
                else:
                    self.vte_terminal.feed_child("Hata: Screenshot alınamadı.\n".encode('utf-8'))
            else:
                self.vte_terminal.feed_child("Hata: Pencere bulunamadı.\n".encode('utf-8'))
                
        except Exception as e:
            self.vte_terminal.feed_child(f"Hata: Alternatif screenshot yöntemi başarısız - {str(e)}\n".encode('utf-8'))

class Application(Gtk.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id="tr.org.diyanet.pasaport-kurulum", **kwargs)
        self.appwindow = None

    def do_activate(self):
        if not self.appwindow:
            self.appwindow = AppWindow(self)
        self.appwindow.window.present()

    def do_startup(self):
        Gtk.Application.do_startup(self)

if __name__ == "__main__":
    import sys
    app = Application()
    sys.exit(app.run(sys.argv))