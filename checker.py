import requests
import re
import json
import time

# Твои актуальные источники (с refs/heads/)
SOURCES = [
    "https://raw.githubusercontent.com/SoliSpirit/mtproto/refs/heads/master/all_proxies.txt",
    "https://raw.githubusercontent.com/kort0881/telegram-proxy-collector/refs/heads/main/proxy_all.txt",
    "https://raw.githubusercontent.com/Argh94/Proxy-List/refs/heads/main/MTProto.txt"
]

def get_country_code(host):
    if host.lower().endswith('.ru') or '.ru.' in host.lower():
        return "RU"
    return "UN"

def collect_proxies():
    all_proxies = []
    unique_hosts = set()

    # Берем текущее время, чтобы создать "хвост"
    current_time = int(time.time())
    print(f"--- ЗАПУСК СБОРА (Метка времени: {current_time}) ---")

    for url in SOURCES:
        try:
            # Вот тот самый "хвост", который заставляет GitHub отдать свежак
            fresh_url = f"{url}?t={current_time}"
            print(f"Запрашиваю свежую версию: {url}")
            
            response = requests.get(fresh_url, timeout=20)
            if response.status_code == 200:
                # Ищем оба формата ссылок
                found = re.findall(r"(?:tg://proxy|https://t\.me/proxy)\?server=([^&]+)&port=([0-9]+)&secret=([^& \n\r\t]+)", response.text)
                
                count_before = len(unique_hosts)
                for host, port, secret in found:
                    if host not in unique_hosts:
                        proxy_data = {
                            "host": host,
                            "port": port,
                            "secret": secret,
                            "country": get_country_code(host),
                            "link": f"tg://proxy?server={host}&port={port}&secret={secret}"
                        }
                        all_proxies.append(proxy_data)
                        unique_hosts.add(host)
                
                print(f"Добавлено новых уникальных прокси: {len(unique_hosts) - count_before}")
            else:
                print(f"Ошибка: Сервер ответил кодом {response.status_code}")
        except Exception as e:
            print(f"Ошибка при обработке {url}: {e}")

    # Сохраняем в JSON для сайта
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(all_proxies, f, indent=4, ensure_ascii=False)
    
    print(f"--- СБОР ЗАВЕРШЕН ---")
    print(f"Всего актуальных прокси в базе: {len(all_proxies)}")

if __name__ == "__main__":
    collect_proxies()
