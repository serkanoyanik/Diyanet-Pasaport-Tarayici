#!/usr/bin/env python3

import subprocess
import sys

commands = [
    "curl -s https://secure.globalsign.com/cacert/gsrsaovsslca2018.crt -o /tmp/gs-int.der",
    "openssl x509 -inform der -in /tmp/gs-int.der -out /tmp/gs-int.pem",
    "keytool -importcert -trustcacerts -noprompt "
    "-alias globalsign-rsa-ov-ssl-ca-2018 "
    "-file /tmp/gs-int.pem "
    "-keystore /usr/lib/jvm/oracle-java8-jre-amd64/lib/security/cacerts "
    "-storepass changeit",
    "keytool -delete "
    "-alias globalsign-rsa-ov-ssl-ca-2018 "
    "-keystore /usr/lib/jvm/oracle-java8-jre-amd64/lib/security/cacerts "
    "-storepass changeit",
    "keytool -importcert -trustcacerts -noprompt "
    "-alias globalsign-rsa-ov-ssl-ca-2018 "
    "-file /tmp/gs-int.pem "
    "-keystore /usr/lib/jvm/oracle-java8-jre-amd64/lib/security/cacerts "
    "-storepass changeit",
    "keytool -list "
    "-keystore /usr/lib/jvm/oracle-java8-jre-amd64/lib/security/cacerts "
    "-storepass changeit | grep -i globalsign-rsa-ov-ssl-ca-2018"
]

def run_command(cmd):
    print(f"\n➡️ Çalıştırılıyor:\n{cmd}")
    result = subprocess.run(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:
        print("❌ Hata oluştu:")
        print(result.stderr)
        sys.exit(result.returncode)
    else:
        print("✅ Başarılı:")
        print(result.stdout)

def main():
    for cmd in commands:
        run_command(cmd)

    print("\n🎉 Tüm komutlar başarıyla çalıştırıldı.")

if __name__ == "__main__":
    main()
