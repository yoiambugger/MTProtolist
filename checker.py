import requests
import re
import json
import time

# Список источников (добавил еще один надежный источник)
SOURCES = [
    "https://raw.githubusercontent.com/SoliSpirit/mtproto/refs/heads/master/all_proxies.txt",
    "https://raw.githubusercontent.com/kort0881/telegram-proxy-collector/refs/heads/main/proxy_all.txt",
    "https://raw.githubusercontent.com/Argh94/Proxy-List/refs/heads/main/MTProto.txt",
    "https://raw.githubusercontent.com/FediS-m/Telegram-Proxy-Collector/refs/heads/main/MTProto_all.txt"
]

def get_source_name(url):
    # Вытаскиваем "Автор/Репозиторий" из ссылки
    parts = url.split('/')
    try:
        return f"{parts[3]}/{parts[4]}"
    except:
        return "Unknown Source"

def get_country_code(host):
    if host.lower().endswith('.ru') or '.ru.' in host.lower():
        return "RU"
    return "UN"

def collect_proxies():
    all_proxies = []
    unique_hosts = set()
    total_found_in_files = 0

    print(f"--- ЗАПУСК СИСТЕМЫ ({time.strftime('%H:%M:%S')}) ---")

    for url in SOURCES:
        try:
            # Обход кэша через timestamp
            fresh_url = f"{url}?t={int(time.time())}"
            response = requests.get(fresh_url, timeout=25)
            
            if response.status_code == 200:
                # Ищем все форматы ссылок
                links = re.findall(r"((?:tg://proxy|https://t\.me/proxy)\?[^ \n\r\t]+)", response.text)
                
                source_name = get_source_name(url)
                in_file = len(links)
                new_here = 0
                
                for link in links:
                    srv = re.search(r"server=([^&]+)", link)
                    prt = re.search(r"port=([0-9]+)", link)
                    sec = re.search(r"secret=([^& \n\r\t]+)", link)
                    
                    if srv and prt and sec:
                        host = srv.group(1)
                        if host not in unique_hosts:
                            proxy_data = {
                                "host": host,
                                "port": prt.group(1),
                                "secret": sec.group(1),
                                "country": get_country_code(host),
                                "link": f"tg://proxy?server={host}&port={prt.group(1)}&secret={sec.group(1)}"
                            }
                            all_proxies.append(proxy_data)
                            unique_hosts.add(host)
                            new_here += 1
                
                total_found_in_files += in_file
                print(f"Источник: {source_name}")
                print(f"  > Найдено ссылок: {in_file}")
                print(f"  > Новых уникальных: {new_here}")
                
        except Exception as e:
            print(f"Ошибка источника {url}: {e}")

    # Сохранение в data.json для фронтенда
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(all_proxies, f, indent=4, ensure_ascii=False)
    
    print(f"--- ИТОГ СБОРКИ ---")
    print(f"Всего просмотрено: {total_found_in_files}")
    print(f"Итого уникальных в базе: {len(all_proxies)}")

if __name__ == "__main__":
    collect_proxies()
