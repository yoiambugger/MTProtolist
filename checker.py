import re
import json
import requests
import time

SOURCES = [
    'https://raw.githubusercontent.com/Surfboardv2ray/TGProto/main/proxies.txt',
    'https://raw.githubusercontent.com/SoliSpirit/mtproto/master/all_proxies.txt',
    'https://raw.githubusercontent.com/Grim1313/mtproto-for-telegram/master/all_proxies.txt'
]

# Твои регионы
ALLOWED = ['RU', 'US', 'MD', 'DE', 'FI', 'SG', 'FR', 'SC']

def get_country(host):
    try:
        # Простой пробив по API
        r = requests.get(f"http://ip-api.com/json/{host.strip()}?fields=status,countryCode", timeout=3).json()
        if r.get('status') == 'success':
            return r.get('countryCode')
    except:
        pass
    return 'UN'

def main():
    print("--- ЗАПУСК ---")
    raw_links = []
    headers = {'User-Agent': 'Mozilla/5.0'}

    for url in SOURCES:
        try:
            res = requests.get(url, headers=headers, timeout=15)
            found = re.findall(r"(?:tg://proxy\?|https://t\.me/proxy\?)[^\s\"'<>]+", res.text)
            raw_links.extend(found)
        except: continue

    unique = list(set(raw_links))
    final = []

    # Берем первые 100 для проверки, чтобы не ждать долго
    for link in unique[:100]:
        try:
            clean = link.strip().replace('https://t.me/proxy?', 'tg://proxy?')
            srv = re.search(r"server=([^&]+)", clean).group(1)
            
            # Определяем ГЕО
            code = get_country(srv)
            print(f"[{code}] {srv}")

            if code in ALLOWED:
                final.append({
                    "host": srv,
                    "link": clean,
                    "country": code
                })
            time.sleep(1.4) # Лимит API
        except: continue

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(final, f, indent=2, ensure_ascii=False)
    print(f"Сохранено: {len(final)}")

if __name__ == "__main__":
    main()
