import re
import json
import requests
import time

SOURCES = [
    'https://raw.githubusercontent.com/Surfboardv2ray/TGProto/main/proxies.txt',
    'https://raw.githubusercontent.com/SoliSpirit/mtproto/master/all_proxies.txt',
    'https://raw.githubusercontent.com/Grim1313/mtproto-for-telegram/master/all_proxies.txt'
]

# Твой список разрешенных регионов
ALLOWED_COUNTRIES = ['RU', 'US', 'MD', 'DE', 'FI', 'SG', 'FR', 'SC']

def get_real_country(host):
    """
    Проверяет реальную геолокацию IP/Хоста через внешний API.
    Лимит бесплатного API: 45 запросов в минуту.
    """
    try:
        # Убираем лишние пробелы
        target = host.strip()
        # Запрос к профессиональной базе IP-геолокации
        response = requests.get(f"http://ip-api.com/json/{target}?fields=status,countryCode", timeout=3)
        data = response.json()
        
        if data.get('status') == 'success':
            return data.get('countryCode')
        return 'UNKNOWN'
    except Exception as e:
        print(f"Ошибка гео-проверки {host}: {e}")
        return 'ERROR'

def main():
    print("--- ЗАПУСК СТРОГОЙ ГЕО-ПРОВЕРКИ ПО IP ---")
    all_raw_links = []
    headers = {'User-Agent': 'Mozilla/5.0'}

    # 1. Собираем все ссылки из источников
    for url in SOURCES:
        try:
            res = requests.get(url, headers=headers, timeout=20)
            found = re.findall(r"(?:tg://proxy\?|https://t\.me/proxy\?)[^\s\"'<>]+", res.text)
            all_raw_links.extend(found)
        except: continue

    unique_links = list(set(all_raw_links))
    print(f"Найдено уникальных кандидатов: {len(unique_links)}")
    
    final_data = []
    processed_count = 0

    # 2. Проверяем ГЕО каждого сервера
    # Ограничиваем выборку первыми 130 штуками, чтобы не ждать вечность и не получить бан от API
    for link in unique_links[:130]:
        try:
            clean_link = link.strip().replace('https://t.me/proxy?', 'tg://proxy?')
            server = re.search(r"server=([^&]+)", clean_link).group(1)
            port = re.search(r"port=(\d+)", clean_link).group(1)
            secret = re.search(r"secret=([^&]+)", clean_link).group(1)

            # Самый важный момент: запрос реальной страны по IP/хосту
            country = get_real_country(server)
            print(f"Сервер {server} -> Определен регион: {country}")

            # Фильтруем только по твоему списку
            if country in ALLOWED_COUNTRIES:
                final_data.append({
                    "host": server,
                    "port": port,
                    "secret": secret,
                    "link": clean_link,
                    "country": country
                })
            
            processed_count += 1
            # Пауза 1.5 сек, чтобы API не заблокировал нас (45 запросов в минуту)
            time.sleep(1.5)
            
        except: continue

    # 3. Сохраняем результат
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)
    
    print(f"--- ПРОВЕРКА ЗАВЕРШЕНА ---")
    print(f"Обработано: {processed_count}. Прошло фильтр: {len(final_data)}")

if __name__ == "__main__":
    main()
