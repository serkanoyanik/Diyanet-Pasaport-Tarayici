#!/bin/bash
# Java uygulamasının çalışma dizininde çalışacak şekilde düzenlendi
cd /opt/HacPasaport
pkexec scanimage -d genesys:libusb:001:004 --depth 16 --mode Color --resolution 600 -x 125 -y 87 --format=tiff >/tmp/image.tiff