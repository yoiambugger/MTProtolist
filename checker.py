import re
import asyncio
import json
import requests

# Твои источники
SOURCES = [
    'https://raw.githubusercontent.com/Surfboardv2ray/TGProto/main/proxies.txt',
    'https://raw.githubusercontent.com/SoliSpirit/mtproto/master/all_proxies.txt',
    'https://raw.githubusercontent.com/Grim1313/mtproto-for-telegram/master/all_proxies.txt'
]

async def check_proxy(host, port):
    """Проверяет, отвечает ли порт прокси"""
    try:
        # Увеличили таймаут до 3 секунд, чтобы дать шанс медленным прокси
        conn = asyncio.open_connection(host, port)
        reader, writer = await asyncio.wait_for(conn, timeout=3.0) 
        writer.close()
        await writer.wait_closed()
        return True
    except:
        return False

async def main():
    print("Запуск глубокого сканирования...")
    all_raw_links = []
    
    for url in SOURCES:
        try:
            res = requests.get(url, timeout=15)
            # Улучшенный поиск: ищем всё, что похоже на tg://proxy, не глядя на хвосты
            found = re.findall(r"tg://proxy\?[^\s\"']+", res.text)
            all_raw_links.extend(found)
            print(f"Найдено {len(found)} потенциальных ссылок в {url}")
        except Exception as e:
            print(f"Ошибка источника {url}: {e}")

    unique_links = list(set(all_raw_links))
    print(f"Всего уникальных кандидатов: {len(unique_links)}")

    working_proxies = []
    
    # Проверяем пачками
    for i in range(0, len(unique_links), 50):
        batch = unique_links[i:i+50]
        tasks = []
        proxy_info_list = []
        
        for link in batch:
            try:
                # Разбираем ссылку по запчастям
                raw_params = link.split('?')[1]
                params = {k: v for k, v in [p.split('=') for p in raw_params.split('&') if '=' in p]}
                
                if 'server' in params and 'port' in params:
                    tasks.append(check_proxy(params['server'], int(params['port'])))
                    proxy_info_list.append({
                        "host": params['server'],
                        "port": params['port'],
                        "secret": params.get('secret', ''),
                        "link": link
                    })
            except: continue
        
        if tasks:
            results = await asyncio.gather(*tasks)
            for info, is_alive in zip(proxy_info_list, results):
                if is_alive:
                    working_proxies.append(info)

    # Сохраняем результат
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(working_proxies, f, indent=2)
    
    print(f"Проверка завершена! Живых прокси: {len(working_proxies)}")

if __name__ == "__main__":
    asyncio.run(main())
