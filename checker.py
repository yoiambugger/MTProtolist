import requests
import re
import json

# Твои проверенные источники
SOURCES = [
    "https://raw.githubusercontent.com/SoliSpirit/mtproto/master/all_proxies.txt",
    "https://raw.githubusercontent.com/kort0881/telegram-proxy-collector/main/proxy_all.txt",
    "https://raw.githubusercontent.com/Argh94/Proxy-List/main/MTProto.txt"
]

def get_country_code(host):
    if host.lower().endswith('.ru') or '.ru.' in host.lower():
        return "RU"
    return "UN"

def collect_proxies():
    all_proxies = []
    unique_hosts = set()

    print("--- ЗАПУСК УНИВЕРСАЛЬНОГО СБОРА ---")

    for url in SOURCES:
        try:
            print(f"Загружаю: {url}")
            response = requests.get(url, timeout=20)
            if response.status_code == 200:
                # Универсальная регулярка: 
                # (?:tg://proxy|https://t\.me/proxy) — ищет оба формата начала ссылки
                # ([^& \n\r\t]+) — забирает данные до первого разделителя или пробела
                found = re.findall(r"(?:tg://proxy|https://t\.me/proxy)\?server=([^&]+)&port=([0-9]+)&secret=([^& \n\r\t]+)", response.text)
                
                count_before = len(unique_hosts)
                for host, port, secret in found:
                    if host not in unique_hosts:
                        proxy_data = {
                            "host": host,
                            "port": port,
                            "secret": secret,
                            "country": get_country_code(host),
                            # Сохраняем всегда в tg://, так как это стандарт для приложений
                            "link": f"tg://proxy?server={host}&port={port}&secret={secret}"
                        }
                        all_proxies.append(proxy_data)
                        unique_hosts.add(host)
                
                print(f"Добавлено новых уникальных прокси: {len(unique_hosts) - count_before}")
        except Exception as e:
            print(f"Ошибка источника {url}: {e}")

    # Записываем в data.json
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(all_proxies, f, indent=4, ensure_ascii=False)
    
    print(f"--- СБОР ЗАВЕРШЕН ---")
    print(f"Итого в базе: {len(all_proxies)}")

if __name__ == "__main__":
    collect_proxies()
