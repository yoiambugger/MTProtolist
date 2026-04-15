import re
import asyncio
import json
import requests

# Твои 3 источника
SOURCES = [
    'https://raw.githubusercontent.com/Surfboardv2ray/TGProto/main/proxies.txt',
    'https://raw.githubusercontent.com/SoliSpirit/mtproto/master/all_proxies.txt',
    'https://raw.githubusercontent.com/Grim1313/mtproto-for-telegram/master/all_proxies.txt'
]

async def check_proxy(host, port):
    """Проверяет, отвечает ли порт прокси"""
    try:
        conn = asyncio.open_connection(host, port)
        reader, writer = await asyncio.wait_for(conn, timeout=1.5) # 1.5 сек на ответ
        writer.close()
        await writer.wait_closed()
        return True
    except:
        return False

async def main():
    print("Начинаю сбор всех прокси...")
    all_raw_links = []
    
    # 1. Собираем всё из 3-х источников
    for url in SOURCES:
        try:
            res = requests.get(url, timeout=10)
            # Ищем все ссылки tg://proxy через регулярку
            found = re.findall(r"tg://proxy\?server=[^&]+&port=\d+&secret=[^&\s]+", res.text)
            all_raw_links.extend(found)
            print(f"Извлечено {len(found)} шт. из {url}")
        except Exception as e:
            print(f"Ошибка при чтении {url}: {e}")

    # Убираем дубликаты
    unique_links = list(set(all_raw_links))
    print(f"Всего уникальных прокси найдено: {len(unique_links)}")

    working_proxies = []
    
    # 2. Проверяем их на работоспособность
    # Проверяем пачками по 100 штук, чтобы не грузить систему
    for i in range(0, len(unique_links), 100):
        batch = unique_links[i:i+100]
        tasks = []
        proxy_data_batch = []
        
        for link in batch:
            try:
                params = dict(re.findall(r'(\w+)=([^&]+)', link.split('?')[1]))
                tasks.append(check_proxy(params['server'], int(params['port'])))
                proxy_data_batch.append({
                    "host": params['server'],
                    "port": params['port'],
                    "secret": params['secret'],
                    "link": link
                })
            except: continue
        
        results = await asyncio.gather(*tasks)
        for proxy, is_alive in zip(proxy_data_batch, results):
            if is_alive:
                working_proxies.append(proxy)

    # 3. Сохраняем результат в data.json
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(working_proxies, f, indent=2)
    
    print(f"Готово! Сохранено {len(working_proxies)} рабочих прокси в data.json")

if __name__ == "__main__":
    asyncio.run(main())
