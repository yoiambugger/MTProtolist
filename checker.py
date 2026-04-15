import re
import json
import requests

SOURCES = [
    'https://raw.githubusercontent.com/Surfboardv2ray/TGProto/main/proxies.txt',
    'https://raw.githubusercontent.com/SoliSpirit/mtproto/master/all_proxies.txt',
    'https://raw.githubusercontent.com/Grim1313/mtproto-for-telegram/master/all_proxies.txt'
]

def main():
    print("--- ЗАПУСК ИСПРАВЛЕННОГО СБОРА ---")
    all_proxies = []
    headers = {'User-Agent': 'Mozilla/5.0'}

    for url in SOURCES:
        try:
            print(f"Читаю: {url}")
            res = requests.get(url, headers=headers, timeout=20)
            
            # Ищем оба формата: и tg:// и https://t.me/
            # Регулярка теперь ищет всё, что содержит /proxy?server=
            links = re.findall(r"(?:tg://proxy\?|https://t\.me/proxy\?)[^\s\"'<>]+", res.text)
            print(f"Найдено: {len(links)} штук")
            
            for link in links:
                try:
                    # Превращаем всё в единый формат tg:// для сайта
                    clean_link = link.strip().replace('https://t.me/proxy?', 'tg://proxy?')
                    
                    # Вытаскиваем сервер для красоты
                    server_match = re.search(r"server=([^&]+)", clean_link)
                    host = server_match.group(1) if server_match else "MTProto"
                    
                    # Вытаскиваем порт и секрет (на всякий случай)
                    port_match = re.search(r"port=(\d+)", clean_link)
                    secret_match = re.search(r"secret=([^&]+)", clean_link)
                    
                    if server_match and port_match:
                        all_proxies.append({
                            "host": host,
                            "port": port_match.group(1),
                            "secret": secret_match.group(1) if secret_match else "",
                            "link": clean_link
                        })
                except: continue
        except Exception as e:
            print(f"Ошибка: {e}")

    # Убираем дубликаты
    unique_list = {p['link']: p for p in all_proxies}.values()
    final_list = list(unique_list)
    
    print(f"--- ИТОГО СОБРАНО: {len(final_list)} уникальных прокси ---")

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(final_list, f, indent=2, ensure_ascii=False)
    print("Файл data.json обновлен!")

if __name__ == "__main__":
    main()
