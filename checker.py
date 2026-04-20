import requests
import re
import json
import time

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
    total_raw_found = 0

    print(f"--- ЗАПУСК ПРОВЕРКИ ({time.strftime('%H:%M:%S')}) ---")

    for url in SOURCES:
        try:
            cache_buster = f"{url}?t={int(time.time())}"
            response = requests.get(cache_buster, timeout=20)
            if response.status_code == 200:
                # Находим вообще все упоминания прокси ссылок
                links = re.findall(r"((?:tg://proxy|https://t\.me/proxy)\?[^ \n\r\t]+)", response.text)
                
                source_total = len(links)
                source_unique = 0
                
                for link in links:
                    # Вытаскиваем параметры из каждой конкретной ссылки
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
                            source_unique += 1
                
                total_raw_found += source_total
                print(f"Источник: {url.split('/')[-2]}") # Короткое имя
                print(f"  > Всего ссылок в файле: {source_total}")
                print(f"  > Из них новых для нас: {source_unique}")
                
        except Exception as e:
            print(f"Ошибка источника {url}: {e}")

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(all_proxies, f, indent=4, ensure_ascii=False)
    
    print(f"--- ИТОГ ---")
    print(f"Просмотрено ссылок всего: {total_raw_found}")
    print(f"Уникальных прокси сохранено: {len(all_proxies)}")

if __name__ == "__main__":
    collect_proxies()
