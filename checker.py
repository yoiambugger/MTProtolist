import re
import json
import requests
import time

SOURCES = [
    'https://raw.githubusercontent.com/Surfboardv2ray/TGProto/main/proxies.txt',
    'https://raw.githubusercontent.com/SoliSpirit/mtproto/master/all_proxies.txt',
    'https://raw.githubusercontent.com/Grim1313/mtproto-for-telegram/master/all_proxies.txt',
    'https://raw.githubusercontent.com/kort0881/telegram-proxy-collector/main/proxy_all.txt' # Твой новый источник
]

ALLOWED_COUNTRIES = ['RU', 'US', 'MD', 'DE', 'FI', 'SG', 'FR', 'SC']

def get_real_country(host):
    try:
        target = host.strip()
        response = requests.get(f"http://ip-api.com/json/{target}?fields=status,countryCode", timeout=3)
        data = response.json()
        if data.get('status') == 'success':
            return data.get('countryCode')
        return 'UNKNOWN'
    except:
        return 'UNKNOWN'

def main():
    print("--- ЗАПУСК ОБНОВЛЕННОГО ЧЕКЕРА ---")
    all_raw_links = []
    headers = {'User-Agent': 'Mozilla/5.0'}

    for url in SOURCES:
        try:
            res = requests.get(url, headers=headers, timeout=20)
            # Регулярка сама пропустит текст сверху, так как он не подходит под шаблон
            found = re.findall(r"(?:tg://proxy\?|https://t\.me/proxy\?)[^\s\"'<>]+", res.text)
            all_raw_links.extend(found)
            print(f"Источник {url}: найдено {len(found)}")
        except: continue

    unique_links = list(set(all_raw_links))
    final_data = []
    
    # Проверяем ГЕО (ограничим до 150 для баланса)
    for link in unique_links[:150]:
        try:
            clean_link = link.strip().replace('https://t.me/proxy?', 'tg://proxy?')
            srv = re.search(r"server=([^&]+)", clean_link).group(1)
            port = re.search(r"port=(\d+)", clean_link).group(1)
            secret = re.search(r"secret=([^&]+)", clean_link).group(1)

            country = get_real_country(srv)
            print(f"[{country}] {srv}")

            if country in ALLOWED_COUNTRIES:
                final_data.append({
                    "host": srv,
                    "port": port,
                    "secret": secret,
                    "link": clean_link,
                    "country": country
                })
            time.sleep(1.4) 
        except: continue

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)
    
    print(f"Готово! Сохранено {len(final_data)} проверенных прокси.")

if __name__ == "__main__":
    main()
