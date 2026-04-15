import re
import json
import requests
import time

SOURCES = [
    'https://raw.githubusercontent.com/Surfboardv2ray/TGProto/main/proxies.txt',
    'https://raw.githubusercontent.com/SoliSpirit/mtproto/master/all_proxies.txt',
    'https://raw.githubusercontent.com/Grim1313/mtproto-for-telegram/master/all_proxies.txt'
]

ALLOWED_COUNTRIES = ['RU', 'US', 'MD', 'DE', 'FI', 'SG', 'FR', 'SC']

def get_real_country(host):
    try:
        target = host.strip()
        # Используем API для проверки ГЕО
        response = requests.get(f"http://ip-api.com/json/{target}?fields=status,countryCode", timeout=3)
        data = response.json()
        if data.get('status') == 'success':
            return data.get('countryCode')
        return 'UNKNOWN'
    except:
        return 'UNKNOWN'

def main():
    print("--- ЗАПУСК БЕЗОПАСНОГО ГЕО-ЧЕКЕРА ---")
    all_raw_links = []
    headers = {'User-Agent': 'Mozilla/5.0'}

    for url in SOURCES:
        try:
            res = requests.get(url, headers=headers, timeout=20)
            found = re.findall(r"(?:tg://proxy\?|https://t\.me/proxy\?)[^\s\"'<>]+", res.text)
            all_raw_links.extend(found)
        except: continue

    unique_links = list(set(all_raw_links))
    print(f"Найдено ссылок: {len(unique_links)}")
    
    final_data = []
    # Проверяем первые 100, чтобы не затягивать процесс
    for link in unique_links[:100]:
        try:
            clean_link = link.strip().replace('https://t.me/proxy?', 'tg://proxy?')
            
            # Безопасный поиск параметров
            srv = re.search(r"server=([^&]+)", clean_link)
            prt = re.search(r"port=(\d+)", clean_link)
            sec = re.search(r"secret=([^&]+)", clean_link)

            if not srv or not prt: # Если нет сервера или порта - скипаем
                continue

            server = srv.group(1)
            port = prt.group(1)
            secret = sec.group(1) if sec else ""

            country = get_real_country(server)
            print(f"[{country}] {server}")

            if country in ALLOWED_COUNTRIES:
                final_data.append({
                    "host": server,
                    "port": port,
                    "secret": secret,
                    "link": clean_link,
                    "country": country
                })
            
            time.sleep(1.4) # Защита от бана API
        except:
            continue

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)
    
    print(f"Готово! Сохранено {len(final_data)} прокси.")

if __name__ == "__main__":
    main()
