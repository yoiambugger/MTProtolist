import re
import json
import requests
import time
import socket

# Источники прокси
SOURCES = [
    'https://raw.githubusercontent.com/SoliSpirit/mtproto/master/all_proxies.txt',
    'https://raw.githubusercontent.com/kort0881/telegram-proxy-collector/main/proxy_all.txt',
    'https://raw.githubusercontent.com/Argh94/Proxy-List/main/MTProto.txt',
    'СЮДА_ВСТАВЬ_ССЫЛКУ_НА_ТВОЙ_НОВЫЙ_ПАРСЕР' # <--- Вот сюда вставь ссылку на свой новый источник
]

def measure_ping(host, port):
    """Замеряет время TCP-соединения в мс"""
    start = time.perf_counter()
    try:
        # Уменьшил таймаут до 2.0 сек для ускорения массовой проверки
        with socket.create_connection((host, int(port)), timeout=2.0):
            end = time.perf_counter()
            return int((end - start) * 1000)
    except:
        return None 

def get_real_country(host):
    """Проверка ГЕО по IP/хосту"""
    try:
        target = host.strip()
        response = requests.get(f"http://ip-api.com/json/{target}?fields=status,countryCode", timeout=3)
        data = response.json()
        if data.get('status') == 'success':
            return data.get('countryCode')
        return 'UN'
    except:
        return 'UN'

def main():
    print("--- ЗАПУСК ГЛОБАЛЬНОГО СБОРЩИКА (БЕЗ ФИЛЬТРОВ ГЕО) ---")
    all_raw_links = []
    headers = {'User-Agent': 'Mozilla/5.0'}

    # 1. Сбор ссылок
    for url in SOURCES:
        try:
            print(f"Сканирую: {url}")
            res = requests.get(url, headers=headers, timeout=20)
            found = re.findall(r"(?:tg://proxy\?|https://t\.me/proxy\?)[^\s\"'<>]+", res.text)
            all_raw_links.extend(found)
        except Exception as e:
            print(f"Ошибка источника {url}: {e}")
            continue

    # Вот эта строчка автоматически удаляет все дубликаты со всех источников
    unique_links = list(set(all_raw_links))
    print(f"Уникальных кандидатов: {len(unique_links)}")
    
    final_data = []
    
    # 3. Проверка ПИНГА и ГЕО (проверяем кандидатов, пока не наберем 100 живых или не кончатся ссылки)
    # Увеличил выборку до 200, так как мы теперь не фильтруем по странам
    for link in unique_links[:200]:
        if len(final_data) >= 100: # Ограничим до 100 рабочих для стабильности сайта
            break
            
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

            # 1. Проверяем пинг (живой/мертвый)
            ping_ms = measure_ping(server, port)
            
            if ping_ms is not None:
                # 2. Если живой — сразу забираем ГЕО
                country = get_real_country(server)
                print(f"[ALIVE] {server} | {ping_ms}ms | {country}")

                # ТЕПЕРЬ ДОБАВЛЯЕМ ВСЁ БЕЗ ПРОВЕРКИ ALLOWED_COUNTRIES
                final_data.append({
                    "host": server,
                    "port": port,
                    "secret": secret,
                    "link": clean_link,
                    "country": country,
                    "ping": ping_ms
                })
                
                # Пауза для API геолокации
                time.sleep(1.3)
            else:
                # Мертвые серверы просто скипаем без вывода в консоль (чтобы не спамить)
                pass
            
        except:
            continue

    # 4. Сохранение в data.json
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)
    
    print(f"--- ПРОВЕРКА ЗАВЕРШЕНА ---")
    print(f"Итого в списке: {len(final_data)} рабочих прокси со всего мира.")

if __name__ == "__main__":
    main()
