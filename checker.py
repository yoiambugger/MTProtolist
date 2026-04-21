import re
import json
import requests
import time

# Твои новые источники (обновлено)
SOURCES = [
    'https://raw.githubusercontent.com/SoliSpirit/mtproto/master/all_proxies.txt',
    'https://raw.githubusercontent.com/kort0881/telegram-proxy-collector/main/proxy_all.txt',
    'https://raw.githubusercontent.com/Argh94/Proxy-List/main/MTProto.txt'
]

# Твой список разрешенных регионов
ALLOWED_COUNTRIES = ['RU', 'US', 'MD', 'DE', 'FI', 'SG', 'FR', 'SC']

def get_real_country(host):
    """Проверка реального ГЕО по IP/хосту"""
    try:
        target = host.strip()
        # Используем API для проверки геолокации
        response = requests.get(f"http://ip-api.com/json/{target}?fields=status,countryCode", timeout=3)
        data = response.json()
        if data.get('status') == 'success':
            return data.get('countryCode')
        return 'UNKNOWN'
    except:
        return 'UNKNOWN'

def main():
    print("--- ЗАПУСК ОБНОВЛЕННОГО СБОРЩИКА ---")
    all_raw_links = []
    headers = {'User-Agent': 'Mozilla/5.0'}

    # 1. Сбор ссылок из всех новых источников
    for url in SOURCES:
        try:
            print(f"Сканирую: {url}")
            res = requests.get(url, headers=headers, timeout=20)
            # Ищем и tg:// и https://t.me/ ссылки
            found = re.findall(r"(?:tg://proxy\?|https://t\.me/proxy\?)[^\s\"'<>]+", res.text)
            all_raw_links.extend(found)
            print(f"Найдено в источнике: {len(found)}")
        except Exception as e:
            print(f"Ошибка при чтении {url}: {e}")
            continue

    # 2. Очистка от дубликатов
    unique_links = list(set(all_raw_links))
    print(f"Всего уникальных кандидатов: {len(unique_links)}")
    
    final_data = []
    
    # 3. Проверка ГЕО (проверяем первые 130 штук для баланса скорости и лимитов API)
    for link in unique_links[:130]:
        try:
            # Приводим к единому формату
            clean_link = link.strip().replace('https://t.me/proxy?', 'tg://proxy?')
            
            srv_match = re.search(r"server=([^&]+)", clean_link)
            prt_match = re.search(r"port=(\d+)", clean_link)
            sec_match = re.search(r"secret=([^&]+)", clean_link)

            if not srv_match or not prt_match:
                continue

            server = srv_match.group(1)
            port = prt_match.group(1)
            secret = sec_match.group(1) if sec_match else ""

            # Определяем реальную страну
            country = get_real_country(server)
            print(f"[{country}] {server}")

            # Фильтруем только нужные страны
            if country in ALLOWED_COUNTRIES:
                final_data.append({
                    "host": server,
                    "port": port,
                    "secret": secret,
                    "link": clean_link,
                    "country": country
                })
            
            # Пауза, чтобы ip-api нас не забанил (лимит 45 запросов в минуту)
            time.sleep(1.4)
            
        except:
            continue

    # 4. Сохранение в data.json
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)
    
    print(f"--- ПРОВЕРКА ЗАВЕРШЕНА ---")
    print(f"В итоговый список попало: {len(final_data)}")

if __name__ == "__main__":
    main()
