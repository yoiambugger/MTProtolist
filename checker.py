import re
import json
import requests
import time
import socket # Добавили для пинга

# Твои источники
SOURCES = [
    'https://raw.githubusercontent.com/SoliSpirit/mtproto/master/all_proxies.txt',
    'https://raw.githubusercontent.com/kort0881/telegram-proxy-collector/main/proxy_all.txt',
    'https://raw.githubusercontent.com/Argh94/Proxy-List/main/MTProto.txt'
]

# Список разрешенных регионов
ALLOWED_COUNTRIES = ['RU', 'US', 'MD', 'DE', 'FI', 'SG', 'FR', 'SC']

def measure_ping(host, port):
    """Замеряет время TCP-соединения в мс"""
    start = time.perf_counter()
    try:
        # Пробуем подключиться к порту прокси
        with socket.create_connection((host, int(port)), timeout=2.5):
            end = time.perf_counter()
            return int((end - start) * 1000)
    except:
        return None # Если не достучались — прокси мертв

def get_real_country(host):
    """Проверка реального ГЕО по IP/хосту"""
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
    print("--- ЗАПУСК ОБНОВЛЕННОГО СБОРЩИКА С ПИНГОМ ---")
    all_raw_links = []
    headers = {'User-Agent': 'Mozilla/5.0'}

    # 1. Сбор ссылок
    for url in SOURCES:
        try:
            print(f"Сканирую: {url}")
            res = requests.get(url, headers=headers, timeout=20)
            found = re.findall(r"(?:tg://proxy\?|https://t\.me/proxy\?)[^\s\"'<>]+", res.text)
            all_raw_links.extend(found)
            print(f"Найдено: {len(found)}")
        except Exception as e:
            print(f"Ошибка источника {url}: {e}")
            continue

    unique_links = list(set(all_raw_links))
    print(f"Уникальных кандидатов: {len(unique_links)}")
    
    final_data = []
    
    # 3. Проверка ГЕО и ПИНГА
    for link in unique_links[:130]:
        try:
            clean_link = link.strip().replace('https://t.me/proxy?', 'tg://proxy?')
            
            srv_match = re.search(r"server=([^&]+)", clean_link)
            prt_match = re.search(r"port=(\d+)", clean_link)
            sec_match = re.search(r"secret=([^&]+)", clean_link)

            if not srv_match or not prt_match:
                continue

            server = srv_match.group(1)
            port = prt_match.group(1)
            secret = sec_match.group(1) if sec_match else ""

            # Сначала проверяем, живой ли прокси
            ping_ms = measure_ping(server, port)
            
            if ping_ms is not None:
                # Если живой, определяем страну
                country = get_real_country(server)
                print(f"[OK] {server} | Ping: {ping_ms}ms | Country: {country}")

                # Фильтруем по списку стран
                if country in ALLOWED_COUNTRIES:
                    final_data.append({
                        "host": server,
                        "port": port,
                        "secret": secret,
                        "link": clean_link,
                        "country": country,
                        "ping": ping_ms # Новое поле для твоего сайта
                    })
                
                # Пауза для API
                time.sleep(1.4)
            else:
                print(f"[DEAD] {server}")
            
        except:
            continue

    # 4. Сохранение в data.json
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)
    
    print(f"--- ПРОВЕРКА ЗАВЕРШЕНА ---")
    print(f"В итоговый список (живые + нужные страны) попало: {len(final_data)}")

if __name__ == "__main__":
    main()
