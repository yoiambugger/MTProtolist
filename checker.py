import requests
import re
import json
import os

# Твои источники (обновленный список с новыми ссылками)
SOURCES = [
    "https://raw.githubusercontent.com/SoliSpirit/mtproto/master/all_proxies.txt",
    "https://raw.githubusercontent.com/kort0881/telegram-proxy-collector/main/proxy_all.txt",
    "https://raw.githubusercontent.com/Argh94/Proxy-List/main/MTProto.txt",
    "https://raw.githubusercontent.com/yebekhe/TelegramV2RayCollector/main/sub/proxies.txt",
    "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt",
    "https://raw.githubusercontent.com/NidukaAkuratiya/MTProto-Proxy-List/main/proxies.txt"
]

def get_country_code(host):
    # Базовая проверка на RU регион
    if host.lower().endswith('.ru') or '.ru.' in host.lower():
        return "RU"
    return "UN" # Остальные регионы

def collect_proxies():
    all_proxies = []
    unique_hosts = set()

    print("--- ЗАПУСК СБОРА ПРОКСИ ---")

    for url in SOURCES:
        try:
            print(f"Загружаю: {url}")
            # Увеличил таймаут, так как некоторые источники могут тупить
            response = requests.get(url, timeout=20)
            if response.status_code == 200:
                # Ищем ссылки формата tg://proxy?server=...&port=...&secret=...
                # Регулярка теперь более гибкая, чтобы ловить всё
                found = re.findall(r"tg://proxy\?server=([A-Za-z0-9\-\.]+)\&port=([0-9]+)\&secret=([A-Za-z0-9]+)", response.text)
                
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
                
                print(f"Найдено уникальных прокси в источнике: {len(found)}")
        except Exception as e:
            print(f"Пропустил источник {url} из-за ошибки: {e}")

    # Сохраняем результат в data.json для сайта
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(all_proxies, f, indent=4, ensure_ascii=False)
    
    print(f"--- СБОР ЗАВЕРШЕН ---")
    print(f"Всего сохранено в data.json: {len(all_proxies)}")

if __name__ == "__main__":
    collect_proxies()
