import requests
import re
import json

# Твои три основных источника
SOURCES = [
    "https://raw.githubusercontent.com/SoliSpirit/mtproto/master/all_proxies.txt",
    "https://raw.githubusercontent.com/kort0881/telegram-proxy-collector/main/proxy_all.txt",
    "https://raw.githubusercontent.com/Argh94/Proxy-List/main/MTProto.txt"
]

def collect():
    proxies = []
    seen = set()

    for url in SOURCES:
        try:
            r = requests.get(url, timeout=15)
            # Ищем оба формата: и tg:// и https://t.me/
            found = re.findall(r"(?:tg://proxy|https://t\.me/proxy)\?server=([^&]+)&port=([0-9]+)&secret=([^& \n\r\t]+)", r.text)
            
            for srv, port, sec in found:
                if srv not in seen:
                    proxies.append({
                        "host": srv,
                        "port": port,
                        "secret": sec,
                        "country": "RU" if ".ru" in srv.lower() else "UN",
                        "link": f"tg://proxy?server={srv}&port={port}&secret={sec}"
                    })
                    seen.add(srv)
        except:
            continue

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(proxies, f, indent=4, ensure_ascii=False)
    
    print(f"Сбор завершен. Всего уникальных: {len(proxies)}")

if __name__ == "__main__":
    collect()
